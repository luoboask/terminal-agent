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
        ...(tools && tools.length > 0 ? { tools } : {}),
        // Qwen API 不支持 tool_choice: 'required'，使用 auto 或不设置
      }),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Qwen API 请求失败：${response.status} ${error}`);
    }

    const data = QwenResponseSchema.parse(await response.json());
    const message = data.choices[0].message;

    // console.log(`[DEBUG] API 响应：tool_calls=${message.tool_calls?.length || 0}, content=${message.content?.substring(0, 100)}...`);

    // AI 执行模式：从文本响应中解析工具调用
    const toolCalls: ToolCall[] = [];
    
    // 1. 尝试从 tool_calls 字段获取
    if (message.tool_calls?.length) {
      // console.log(`[DEBUG] tool_calls 数量：${message.tool_calls.length}`);
      for (const tc of message.tool_calls) {
        // console.log(`[DEBUG] tool_call: id=${tc.id}, name=${tc.function.name}, args=${tc.function.arguments.substring(0, 200)}...`);
        try {
          toolCalls.push({ id: tc.id, name: tc.function.name, arguments: JSON.parse(tc.function.arguments) });
          // console.log(`[DEBUG] 解析成功`);
        } catch (e) {
          // console.log(`[DEBUG] 解析失败：${e}`);
        }
      }
    }
    
    // 2. 如果 tool_calls 为空，从文本响应中提取（AI 执行模式）
    if (toolCalls.length === 0 && message.content) {
      const extractedCalls = this.extractToolCallsFromText(message.content);
      if (extractedCalls.length > 0) {
        toolCalls.push(...extractedCalls);
        // 不移除工具调用标记，让 UI 显示
        // message.content = this.removeToolCallsFromText(message.content);
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

  /**
   * 从文本响应中提取工具调用（AI 执行模式）
   */
  extractToolCallsFromText(text: string): ToolCall[] {
    const toolCalls: ToolCall[] = [];
    // 支持多种工具调用格式：⏺ 或 ⏺ 或 ▶
    const toolCallRegex = /[⏺▶]\s*(\w+)\(([\s\S]*?)\)(?=\s*(?:[⏺▶]|$|\n))/g;
    let match;
    
    // console.log(`[DEBUG] 开始解析工具调用，文本长度：${text.length}`);
    // console.log(`[DEBUG] 原始文本前 500 字符：${text.substring(0, 500)}...`);
    
    while ((match = toolCallRegex.exec(text)) !== null) {
      const toolName = match[1];
      const paramsStr = match[2];
      const args: Record<string, any> = {};
      
      // console.log(`[DEBUG] === 匹配到工具调用 ===`);
      // console.log(`[DEBUG] 工具名：${toolName}`);
      // console.log(`[DEBUG] 完整匹配：${match[0].substring(0, 200)}...`);
      // console.log(`[DEBUG] 原始参数：${paramsStr.substring(0, 200)}...`);
      
      // 智能分割参数：考虑数组中的逗号
      const pairs = this.smartSplitParams(paramsStr);
      // console.log(`[DEBUG] 分割后的参数对：${JSON.stringify(pairs)}`);
      
      for (const pair of pairs) {
        const [key, ...valueParts] = pair.split('=');
        if (key && valueParts.length > 0) {
          let value = valueParts.join('=').trim();
          // console.log(`[DEBUG]   参数 ${key} = ${value.substring(0, 100)}...`);
          
          // 处理数组格式：["a", "b", "c"] 或 [a, b, c]
          if (value.startsWith('[') && value.endsWith(']')) {
            const arrayContent = value.slice(1, -1);
            const items = arrayContent.split(/,\s*/).map(item => item.trim().replace(/^["']|["']$/g, ''));
            value = items;
            // console.log(`[DEBUG]   解析为数组：${JSON.stringify(value)}`);
          } else {
            // 普通值
            value = value.replace(/^["']|["']$/g, '');
            value = value === 'true' ? true : value === 'false' ? false : /^\d+$/.test(value) ? parseInt(value) : value;
            // console.log(`[DEBUG]   解析为值：${value}`);
          }
          
          args[key.trim()] = value;
        }
      }
      
      // console.log(`[DEBUG] 最终参数对象：${JSON.stringify(args)}`);
      toolCalls.push({ id: `text_${Date.now()}_${toolCalls.length}`, name: toolName, arguments: args });
    }
    
    // console.log(`[DEBUG] 提取完成，共 ${toolCalls.length} 个工具调用`);
    return toolCalls;
  }

  /**
   * 智能分割参数（考虑数组中的逗号）
   */
  private smartSplitParams(paramsStr: string): string[] {
    const pairs: string[] = [];
    let current = '';
    let inArray = false;
    let inString = false;
    let escapeNext = false;
    
    for (let i = 0; i < paramsStr.length; i++) {
      const char = paramsStr[i];
      
      // 处理转义字符
      if (escapeNext) {
        current += char;
        escapeNext = false;
        continue;
      }
      if (char === '\\') {
        escapeNext = true;
        current += char;
        continue;
      }
      
      // 处理字符串引号
      if ((char === '"' || char === "'") && !inArray) {
        inString = !inString;
      }
      
      // 处理数组
      if (char === '[' && !inString) {
        inArray = true;
      } else if (char === ']' && !inString) {
        inArray = false;
      }
      
      // 分割参数（逗号不在数组或字符串内）
      if (char === ',' && !inArray && !inString) {
        pairs.push(current.trim());
        current = '';
      } else {
        current += char;
      }
    }
    
    if (current.trim()) {
      pairs.push(current.trim());
    }
    
    return pairs;
  }

  /**
   * 从文本中移除工具调用标记
   */
  removeToolCallsFromText(text: string): string {
    return text.replace(/⏺\s*\w+\([^)]*\)\s*\n/g, '').trim();
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
