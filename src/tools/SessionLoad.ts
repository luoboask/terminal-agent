/**
 * SessionLoad Tool - 从文件加载历史会话
 */

import { z } from 'zod';
import { BaseTool, ToolResult } from '../core/Tool.js';
import { readFileSync, existsSync } from 'fs';
import { join } from 'path';

const SessionLoadInputSchema = z.object({
  filename: z.string().describe('要加载的会话文件名'),
});

type Input = z.infer<typeof SessionLoadInputSchema>;

export class SessionLoadTool extends BaseTool<Input> {
  readonly name = 'session_load';
  readonly description = '从文件加载历史会话。用于恢复之前的会话记录。';
  readonly inputSchema = SessionLoadInputSchema;

  async execute(input: Input): Promise<ToolResult> {
    const { filename } = input;

    try {
      // 读取文件（支持完整路径或文件名）
      let filePath: string;
      
      if (filename.startsWith('/')) {
        // 完整路径
        filePath = filename;
      } else {
        // 文件名，在 .source-deploy 目录中查找
        filePath = join(process.cwd(), '.source-deploy', filename);
      }
      
      if (!existsSync(filePath)) {
        return {
          success: false,
          content: `❌ 文件未找到

📁 请求路径：${filePath}

💡 提示：请检查文件名是否正确，或使用 session_save 先保存会话`,
          error: 'File not found',
        };
      }

      const content = readFileSync(filePath, 'utf-8');
      const saveData = JSON.parse(content);

      // 设置到全局变量
      (global as any).__sessionHistory = saveData.messages || [];

      return {
        success: true,
        content: `✅ 会话已加载

📁 文件路径：${filePath}
📊 消息数量：${saveData.messages?.length || 0} 条
🕐 保存时间：${saveData.timestamp || '未知'}`,
        data: {
          messages: saveData.messages,
        },
      };
    } catch (error) {
      const err = error as Error;
      return {
        success: false,
        content: `❌ 加载失败

❌ 错误：${err.message}`,
        error: err.message,
      };
    }
  }
}
