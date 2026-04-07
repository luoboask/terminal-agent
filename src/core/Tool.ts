import { z } from 'zod';

/**
 * 工具输入参数 Schema 类型
 */
export type ToolInputSchema = z.ZodObject<Record<string, z.ZodType>>;

/**
 * 工具执行结果
 */
export interface ToolResult {
  success: boolean;
  content: string;
  error?: string;
}

/**
 * 工具定义接口
 */
export interface ToolDefinition<T extends ToolInputSchema = ToolInputSchema> {
  name: string;
  description: string;
  inputSchema: T;
  execute: (input: z.infer<T>) => Promise<ToolResult>;
}

/**
 * 工具抽象基类
 * 
 * 参考自 source/src/Tool.ts (30KB) 的简化版本
 * 原始实现包含复杂的权限检查、进度追踪等功能
 * 这里保留核心接口定义
 */
export abstract class BaseTool<T extends ToolInputSchema = ToolInputSchema> {
  abstract readonly name: string;
  abstract readonly description: string;
  abstract readonly inputSchema: T;

  /**
   * 执行工具
   * @param input - 工具输入参数
   * @returns 工具执行结果
   */
  abstract execute(input: z.infer<T>): Promise<ToolResult>;

  /**
   * 获取工具定义（用于 MCP 协议）
   */
  getDefinition(): ToolDefinition<T> {
    return {
      name: this.name,
      description: this.description,
      inputSchema: this.inputSchema,
      execute: this.execute.bind(this),
    };
  }

  /**
   * 验证输入
   */
  validateInput(input: unknown): z.infer<T> | null {
    try {
      return this.inputSchema.parse(input);
    } catch {
      return null;
    }
  }
}

/**
 * 工具注册表
 */
export class ToolRegistry {
  private tools: Map<string, BaseTool<any>> = new Map();

  /**
   * 注册工具
   */
  register(tool: BaseTool<any>): void {
    this.tools.set(tool.name, tool);
  }

  /**
   * 获取工具
   */
  get(name: string): BaseTool<any> | undefined {
    return this.tools.get(name);
  }

  /**
   * 列出所有工具
   */
  list(): BaseTool<any>[] {
    return Array.from(this.tools.values());
  }

  /**
   * 获取所有工具定义（用于 MCP）
   */
  getMcpTools(): Array<{ name: string; description: string; input_schema: Record<string, unknown> }> {
    return this.list().map(tool => ({
      name: tool.name,
      description: tool.description,
      input_schema: tool.inputSchema.schema as unknown as Record<string, unknown>,
    }));
  }
}
