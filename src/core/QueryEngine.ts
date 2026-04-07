import { ToolRegistry, BaseTool, ToolResult } from './Tool.js';
import { info, debug, error, warn } from '../utils/logger.js';
import { QwenProvider, ChatMessage, ToolResultMessage, ToolCall } from '../providers/QwenProvider.js';
import { writeFileSync, mkdirSync, existsSync } from 'fs';
import { join } from 'path';

/**
 * 消息类型
 */
export interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

/**
 * 查询引擎配置
 */
export interface QueryEngineConfig {
  apiKey: string;
  model?: string;
  maxTokens?: number;
  systemPrompt?: string;
  cwd?: string;
  toolRegistry: ToolRegistry;
}

/**
 * 流式消息块
 */
export interface StreamMessage {
  type: 'text' | 'tool_use' | 'tool_result' | 'error';
  content: string;
  toolName?: string;
  toolInput?: Record<string, unknown>;
}

/**
 * 查询引擎类（完整工具调用支持）
 */
export class QueryEngine {
  private client: QwenProvider;
  private config: QueryEngineConfig;
  private messages: (Message | ToolResultMessage)[] = [];
  private abortController: AbortController | null = null;
  
  // 重复调用检测
  private recentToolCalls: Array<{name: string; argsHash: string}> = [];
  private readonly MAX_RECENT_CALLS = 10;
  
  // 文件读取历史记录（防止重复读取同一文件）
  private readFilePaths: Set<string> = new Set();
  private readonly MAX_FILE_READS = 2; // 同一文件最多读取 2 次

  constructor(config: QueryEngineConfig) {
    this.config = {
      ...config,
      model: config.model || 'qwen3.5-plus',
      maxTokens: config.maxTokens || 4096,
      cwd: config.cwd || process.cwd(),
    };

    this.client = new QwenProvider({
      apiKey: config.apiKey,
      baseUrl: process.env.QWEN_BASE_URL || undefined,
    });

    this.messages = [];
    
    if (config.systemPrompt) {
      this.messages.push({
        role: 'system',
        content: config.systemPrompt,
      });
    }
  }

  /**
   * 提交消息并获取响应（完整工具调用循环）
   */
  async *submitMessage(prompt: string): AsyncGenerator<StreamMessage> {
    // 添加用户消息
    this.messages.push({
      role: 'user',
      content: prompt,
    });
    
    // 自动保存会话
    this.autoSaveSession();

    debug('Submitting message:', prompt.slice(0, 100));

    try {
      // 构建工具定义
      const tools = QwenProvider.buildTools(this.config.toolRegistry);

      // 最大工具调用轮数（防止无限循环）
      const MAX_TURNS = 1000;  // 增加到 1000 轮，支持复杂多步骤任务
      
      for (let turn = 0; turn < MAX_TURNS; turn++) {
        debug(`Turn ${turn + 1}/${MAX_TURNS}`);

        // 调用 LLM
        const response = await this.client.chat(
          this.messages as ChatMessage[],
          {
            model: this.config.model!,
            maxTokens: this.config.maxTokens!,
            tools: tools.length > 0 ? tools : undefined,
          }
        );

        debug(`LLM response: content=${response.content.length}, toolCalls=${response.toolCalls?.length || 0}`);

        // 如果有文本内容，返回给用户
        if (response.content) {
          yield { type: 'text', content: response.content };
          
          // 添加助手消息到历史
          this.messages.push({
            role: 'assistant',
            content: response.content,
          });
        }

        // 如果没有工具调用，对话结束
        if (!response.toolCalls || response.toolCalls.length === 0) {
          debug('No tool calls, conversation complete');
          return;
        }

        // 执行工具调用
        for (const toolCall of response.toolCalls) {
          debug(`Checking tool call: ${toolCall.name}`, toolCall.arguments);

          // 检测文件重复读取（即使路径格式不同）
          if (toolCall.name === 'file_read' && toolCall.arguments.file_path) {
            const filePath = toolCall.arguments.file_path as string;
            // 标准化路径（移除 ./ 等前缀，提取文件名）
            const fileName = filePath.split('/').pop() || filePath;
            
            // 检查是否已读取过该文件
            const previousReads = Array.from(this.readFilePaths).filter(p => p.endsWith(fileName));
            if (previousReads.length >= this.MAX_FILE_READS) {
              warn(`⚠️ 文件 ${fileName} 已读取 ${previousReads.length} 次`);
              // 使用 assistant 角色而不是 tool 角色，避免 Qwen API 验证错误
              this.messages.push({
                role: 'assistant',
                content: `✅ 文件 ${fileName} 已读取过，请开始总结分析`,
              });
              yield {
                type: 'tool_result',
                content: `✅ 已读取`,
                toolName: toolCall.name,
              };
              continue; // 跳过这次工具调用
            }
            this.readFilePaths.add(filePath);
          }
          
          // 检测重复调用
          if (this.isRepeatedToolCall(toolCall.name, toolCall.arguments)) {
            warn(`⚠️ 重复工具调用：${toolCall.name}`);
            // 如果是连续第 2 次相同调用，警告；第 5 次阻止并返回错误（针对 file_read 等读取操作）
            const consecutiveCount = this.getConsecutiveCallCount(toolCall.name, toolCall.arguments);
            if (consecutiveCount >= 2) {
              warn(`⚠️ 重复工具调用警告：连续 ${consecutiveCount} 次调用 "${toolCall.name}"`);
            }
            // 对于 file_read 等读取操作，2 次就警告，3 次阻止；其他操作 50 次才阻止
            const isReadOperation = toolCall.name === 'file_read' || toolCall.name === 'glob';
            const threshold = isReadOperation ? 3 : 50;
            if (consecutiveCount >= 2 && isReadOperation) {
              warn(`⚠️ 已读取 ${consecutiveCount} 次文件，请开始总结分析，不要继续读取`);
            }
            if (consecutiveCount >= threshold) {
              // 使用 assistant 角色而不是 tool 角色，避免 Qwen API 验证错误
              this.messages.push({
                role: 'assistant',
                content: `错误：检测到重复工具调用循环。连续 ${consecutiveCount} 次调用相同的工具 "${toolCall.name}" 且参数相同。请尝试其他方法或修改参数。`,
              });
              yield {
                type: 'tool_result',
                content: `❌ 阻止重复调用：连续 ${consecutiveCount} 次相同调用\n\n💡 提示：读取文件 1-2 次就够了，请继续处理文件或进行下一步操作`,
                toolName: toolCall.name,
              };
              continue;
            }
          }

          debug(`Executing tool: ${toolCall.name}`, toolCall.arguments);

          // 记录这次调用
          this.recordToolCall(toolCall.name, toolCall.arguments);

          // 通知用户正在使用工具（即使参数为空也要显示工具名）
          yield {
            type: 'tool_use',
            content: JSON.stringify(toolCall.arguments || {}),
            toolName: toolCall.name,
            toolInput: toolCall.arguments || {},
          };

          // 确保动画至少显示 200ms（让用户能看到）
          await new Promise(r => setTimeout(r, 200));

          // 查找并执行工具
          const tool = this.config.toolRegistry.get(toolCall.name);
          if (!tool) {
            error(`Tool not found: ${toolCall.name}`);
            
            // 添加工具错误结果
            this.messages.push({
              role: 'tool',
              tool_call_id: toolCall.id,
              content: `Error: Tool "${toolCall.name}" not found`,
            });
            
            yield {
              type: 'error',
              content: `Tool not found: ${toolCall.name}`,
              toolName: toolCall.name,
            };
            continue;
          }

          // 执行工具
          try {
            const result = await tool.execute(toolCall.arguments);
            
            // 添加工具结果到历史
            this.messages.push({
              role: 'tool',
              tool_call_id: toolCall.id,
              content: result.success 
                ? result.content 
                : `Error: ${result.error || result.content}`,
            });

            // 返回工具结果（简洁版）
            const resultMessage = result.success
              ? result.content
              : `❌ 失败：${result.error || result.content}`;
            
            yield {
              type: 'tool_result',
              content: resultMessage,
              toolName: toolCall.name,
            };

            if (!result.success) {
              error(`Tool execution failed: ${toolCall.name}`, result.error);
            }
          } catch (err) {
            error(`Tool execution error: ${toolCall.name}`, err);
            
            this.messages.push({
              role: 'tool',
              tool_call_id: toolCall.id,
              content: `Error: ${err instanceof Error ? err.message : String(err)}`,
            });
            
            yield {
              type: 'error',
              content: `Tool ${toolCall.name} failed: ${err}`,
              toolName: toolCall.name,
            };
          }
        }

        // 继续下一轮对话（LLM 基于工具结果继续）
        debug('Continuing to next turn...');
      }

      // 达到最大轮数
      warn('Reached maximum conversation turns');
      yield {
        type: 'error',
        content: '达到最大对话轮数，请重新描述你的需求',
      };

    } catch (err) {
      error('Query failed:', err);
      yield {
        type: 'error',
        content: err instanceof Error ? err.message : String(err),
      };
    }
  }

  /**
   * 简单对话（非流式，包装 submitMessage）
   */
  async chat(prompt: string): Promise<string> {
    let response = '';
    
    for await (const chunk of this.submitMessage(prompt)) {
      if (chunk.type === 'text') {
        response += chunk.content;
      }
    }

    return response;
  }

  /**
   * 获取消息历史
   */
  getHistory(): (Message | ToolResultMessage)[] {
    return [...this.messages];
  }

  /**
   * 清空历史
   */
  clearHistory(): void {
    this.messages = [];
    this.recentToolCalls = [];
    if (this.config.systemPrompt) {
      this.messages.push({
        role: 'system',
        content: this.config.systemPrompt,
      });
    }
  }

  /**
   * 生成参数哈希（用于检测重复）
   */
  private hashArgs(args: Record<string, unknown>): string {
    return JSON.stringify(args, Object.keys(args).sort());
  }

  /**
   * 检查是否是重复的工具调用
   */
  private isRepeatedToolCall(name: string, args: Record<string, unknown>): boolean {
    const argsHash = this.hashArgs(args);
    return this.recentToolCalls.some(
      call => call.name === name && call.argsHash === argsHash
    );
  }

  /**
   * 记录工具调用
   */
  private recordToolCall(name: string, args: Record<string, unknown>): void {
    const argsHash = this.hashArgs(args);
    this.recentToolCalls.push({ name, argsHash });
    
    // 保持最近 N 次记录
    if (this.recentToolCalls.length > this.MAX_RECENT_CALLS) {
      this.recentToolCalls.shift();
    }
  }

  /**
   * 获取连续相同调用的次数
   */
  private getConsecutiveCallCount(name: string, args: Record<string, unknown>): number {
    const argsHash = this.hashArgs(args);
    let count = 0;
    
    // 从后往前数连续相同的调用
    for (let i = this.recentToolCalls.length - 1; i >= 0; i--) {
      const call = this.recentToolCalls[i];
      if (call.name === name && call.argsHash === argsHash) {
        count++;
      } else {
        break;
      }
    }
    
    return count;
  }

  /**
   * 自动保存会话到文件
   */
  private autoSaveSession(): void {
    try {
      // 保存到 .source-deploy 目录
      const saveDir = join(process.cwd(), '.source-deploy');
      if (!existsSync(saveDir)) {
        mkdirSync(saveDir, { recursive: true });
      }

      const filePath = join(saveDir, 'current-session.json');
      const saveData = {
        timestamp: new Date().toISOString(),
        messageCount: this.messages.length,
        messages: this.messages,
      };

      writeFileSync(filePath, JSON.stringify(saveData, null, 2), 'utf-8');
      debug(`Session auto-saved to ${filePath}`);
    } catch (error) {
      warn(`Failed to auto-save session: ${error}`);
    }
  }
}
