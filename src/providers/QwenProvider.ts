/**
 * Qwen Provider - 通义千问 API 适配器
 * 
 * 支持阿里云百炼平台的 Qwen3.5-plus 模型
 * ✅ Function Call 支持
 * ✅ 大文件内容优化处理
 */

import { z } from 'zod';

// Qwen API 配置
export const QWEN_CONFIG = {
  baseUrl: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
  apiKey: process.env.DASHSCOPE_API_KEY || '',
  models: [{
    id: 'qwen3.5-plus',
    name: 'qwen3.5-plus',
    reasoning: true,
    contextWindow: 1000000,
    maxTokens: 65536,
  }]
};

// 类型定义
export interface ToolDefinition {
  type: 'function';
  function: {
    name: string;
    description: string;
    parameters: {
      type: 'object';
      properties: Record<string, { type: string; description?: string }>;
      required?: string[];
    };
  };
}

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export interface ToolResultMessage {
  role: 'tool';
  tool_call_id: string;
  content: string;
}

export interface ChatOptions {
  model?: string;
  temperature?: number;
  maxTokens?: number;
  tools?: ToolDefinition[];
}

export interface ToolCall {
  id: string;
  name: string;
  arguments: Record<string, unknown>;
}

export interface ChatResponse {
  id: string;
  model: string;
  content: string;
  toolCalls?: ToolCall[];
  usage: { promptTokens: number; completionTokens: number; totalTokens: number; };
}

// Schema
const ToolCallSchema = z.object({
  id: z.string(),
  type: z.literal('function'),
  function: z.object({ name: z.string(), arguments: z.string() }),
});

const ChoiceSchema = z.object({
  index: z.number(),
  message: z.object({
    role: z.enum(['assistant']),
    content: z.string().nullable(),
    tool_calls: z.array(ToolCallSchema).optional(),
  }),
  finish_reason: z.string(),
});

const QwenResponseSchema = z.object({
  id: z.string(),
  choices: z.array(ChoiceSchema),
  usage: z.object({
    prompt_tokens: z.number(),
    completion_tokens: z.number(),
    total_tokens: z.number(),
  }),
});

/**
 * Qwen API 客户端
 */
export class QwenProvider {
  private baseUrl: string;
  private apiKey: string;

  constructor(config?: { baseUrl?: string; apiKey?: string }) {
    this.baseUrl = config?.baseUrl || QWEN_CONFIG.baseUrl;
    this.apiKey = config?.apiKey || QWEN_CONFIG.apiKey;
    if (!this.apiKey) throw new Error('Qwen API Key 未设置');
  }

  async chat(messages: (ChatMessage | ToolResultMessage)[], options: ChatOptions = {}): Promise<ChatResponse> {
    const { model = 'qwen3.5-plus', temperature = 0.7, maxTokens = 4096, tools } = options;

    const response = await fetch(`${this.baseUrl}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${this.apiKey}`,
      },
      body: JSON.stringify({
        model,
        messages,
        temperature,
        max_tokens: maxTokens,
        ...(tools && tools.length > 0 ? { tools, tool_choice: 'auto' } : {}),
      }),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Qwen API 请求失败：${response.status} ${error}`);
    }

    const data = QwenResponseSchema.parse(await response.json());
    const message = data.choices[0].message;

    // 解析工具调用（优化：直接提取关键参数）
    const toolCalls: ToolCall[] = [];
    if (message.tool_calls?.length) {
      for (const tc of message.tool_calls) {
        try {
          toolCalls.push({
            id: tc.id,
            name: tc.function.name,
            arguments: JSON.parse(tc.function.arguments),
          });
        } catch {
          // 大文件内容解析失败时，直接提取关键参数
          const raw = tc.function.arguments;
          const args: any = {};
          
          // 提取常见参数
          const pathMatch = raw.match(/"file_path"\s*:\s*"([^"]+)"/);
          const dirPathMatch = raw.match(/"directory_path"\s*:\s*"([^"]+)"/);
          const contentMatch = raw.match(/"content"\s*:\s*"((?:[^"\\]|\\.)*)"/);
          
          if (pathMatch) args.file_path = pathMatch[1];
          if (dirPathMatch) args.directory_path = dirPathMatch[1];
          
          // 大文件处理：自动持久化 + 分块提示
          if (contentMatch) {
            const content = contentMatch[1].replace(/\\"/g, '"').replace(/\\n/g, '\n');
            const MAX_CONTENT_LENGTH = 25000; // 25KB 阈值
            
            if (content.length > MAX_CONTENT_LENGTH) {
              // 内容过大，自动持久化到临时文件
              const fs = await import('fs/promises');
              const path = await import('path');
              const tempDir = path.join(process.cwd(), '.source-deploy-temp');
              await fs.mkdir(tempDir, { recursive: true });
              
              const tempFile = path.join(tempDir, `large_content_${Date.now()}.txt`);
              await fs.writeFile(tempFile, content, 'utf-8');
              
              // 添加智能提示，告诉模型使用分块写入
              args.content = `[内容过大，已保存到临时文件]
文件大小：${content.length} 字符
临时文件：${tempFile}

💡 请使用分块写入方式：
1. 将内容分成多个块（每块约 20000 字符）
2. 使用 file_write 工具，设置：
   - is_chunk: true
   - total_chunks: <总块数>
   - chunk_index: <当前块索引，从 0 开始>
   - file_path: <目标文件路径>
   - content: <当前块内容>

示例：
file_write({
  file_path: "target.txt",
  content: "...第一块内容...",
  is_chunk: true,
  chunk_index: 0,
  total_chunks: 5
})`;
              
              console.log(`[QwenProvider] 大文件内容已持久化：${tempFile} (${content.length} 字符)`);
            } else {
              args.content = content;
            }
          }
          
          if (Object.keys(args).length > 0) {
            toolCalls.push({ id: tc.id, name: tc.function.name, arguments: args });
          } else {
            // 参数提取失败，跳过此工具调用
            console.warn(`[QwenProvider] 无法解析工具参数：${tc.function.name}`);
            // 不添加工具调用，让模型重新生成
          }
        }
      }
    }

    return {
      id: data.id,
      model: data.model,
      content: message.content || '',
      toolCalls: toolCalls.length > 0 ? toolCalls : undefined,
      usage: data.usage,
    };
  }

  static buildTools(toolRegistry: any): ToolDefinition[] {
    return toolRegistry.list().map(tool => {
      const schema = (tool as any).schema || {};
      const properties: Record<string, any> = {};
      const required: string[] = [];

      if (schema.shape) {
        for (const [key, value] of Object.entries(schema.shape as Record<string, any>)) {
          properties[key] = {
            type: this.inferJsonType(value),
            description: (value as any)?.description || key,
          };
          required.push(key);
        }
      }

      return {
        type: 'function' as const,
        function: {
          name: tool.name,
          description: tool.description || `Execute ${tool.name}`,
          parameters: { type: 'object', properties, required },
        },
      };
    });
  }

  private static inferJsonType(zodType: any): string {
    if (!zodType?._def?.typeName) return 'string';
    const typeName = zodType._def.typeName;
    switch (typeName) {
      case 'ZodString': return 'string';
      case 'ZodNumber': return 'number';
      case 'ZodBoolean': return 'boolean';
      case 'ZodArray': return 'array';
      case 'ZodObject': return 'object';
      default: return 'string';
    }
  }

  async testConnection(): Promise<boolean> {
    try {
      await this.chat([{ role: 'user', content: '你好' }], { maxTokens: 10 });
      return true;
    } catch {
      return false;
    }
  }
}

export default QwenProvider;
