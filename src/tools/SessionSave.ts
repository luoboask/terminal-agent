/**
 * SessionSave Tool - 保存当前会话到文件
 */

import { z } from 'zod';
import { BaseTool, ToolResult } from '../core/Tool.js';
import { writeFileSync, existsSync, mkdirSync, readFileSync } from 'fs';
import { join } from 'path';

const SessionSaveInputSchema = z.object({
  filename: z.string().optional().describe('保存文件名（默认 session-history.json）'),
});

type Input = z.infer<typeof SessionSaveInputSchema>;

export class SessionSaveTool extends BaseTool<Input> {
  readonly name = 'session_save';
  readonly description = '保存当前会话历史到文件。用于持久化会话记录，方便后续查看或加载。';
  readonly inputSchema = SessionSaveInputSchema;

  async execute(input: Input): Promise<ToolResult> {
    const { filename = 'session-history.json' } = input;

    try {
      // 从自动保存文件读取会话历史
      const saveDir = join(process.cwd(), '.source-deploy');
      const currentSessionFile = join(saveDir, 'current-session.json');
      
      if (!existsSync(currentSessionFile)) {
        return {
          success: false,
          content: `❌ 会话文件未找到

📁 文件路径：${currentSessionFile}

💡 提示：当前没有自动保存的会话，请先进行一些对话`,
          error: 'Session file not found',
        };
      }
      
      const currentData = JSON.parse(readFileSync(currentSessionFile, 'utf-8'));
      const history = currentData.messages || [];
      
      if (history.length === 0) {
        return {
          success: false,
          content: `❌ 会话为空

💡 提示：当前会话没有任何消息，无法保存`,
          error: 'Session is empty',
        };
      }

      // 确保目录存在
      if (!existsSync(saveDir)) {
        mkdirSync(saveDir, { recursive: true });
      }

      // 保存文件
      const filePath = join(saveDir, filename);
      const saveData = {
        timestamp: new Date().toISOString(),
        messageCount: history.length,
        messages: history,
        source: currentSessionFile,
      };
      
      writeFileSync(filePath, JSON.stringify(saveData, null, 2), 'utf-8');

      return {
        success: true,
        content: `✅ 会话已保存

📁 保存路径：${filePath}
📊 消息数量：${history.length} 条
🕐 保存时间：${saveData.timestamp}`,
      };
    } catch (error) {
      const err = error as Error;
      return {
        success: false,
        content: `❌ 保存失败

❌ 错误：${err.message}`,
        error: err.message,
      };
    }
  }
}
