/**
 * SendMessage Tool - 发送消息
 */

import { z } from 'zod';
import { BaseTool, ToolResult } from '../core/Tool.js';

const SendMessageInputSchema = z.object({
  to: z.string().describe('接收者（用户 ID 或频道）'),
  message: z.string().describe('消息内容'),
  type: z.enum(['info', 'warning', 'error', 'success']).optional().describe('消息类型'),
});

type Input = z.infer<typeof SendMessageInputSchema>;

export class SendMessageTool extends BaseTool<typeof SendMessageInputSchema> {
  readonly name = 'send_message';
  readonly description = '发送消息给用户或其他接收者';
  readonly inputSchema = SendMessageInputSchema;

  async execute(input: Input): Promise<ToolResult> {
    const { to, message, type = 'info' } = input;

    const typeEmojis: Record<string, string> = {
      info: 'ℹ️',
      warning: '⚠️',
      error: '❌',
      success: '✅',
    };

    try {
      // 存储消息（简化实现）
      const globalMessages = (global as any).__messages__ || [];
      
      const messageObj = {
        id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`,
        to,
        message,
        type,
        sentAt: new Date().toISOString(),
        read: false,
      };

      globalMessages.push(messageObj);
      (global as any).__messages__ = globalMessages;

      return {
        success: true,
        content: `${typeEmojis[type]} **消息已发送**

📤 **接收者**: ${to}
📝 **内容**: ${message}
🏷️ **类型**: ${type}
🕐 **发送时间**: ${new Date().toLocaleString('zh-CN')}
📊 **状态**: 已发送`,
        data: messageObj,
      };
    } catch (err) {
      const error = err as Error;
      return {
        success: false,
        content: `❌ 发送消息失败\n\n接收者：${to}\n❌ 错误：${error.message}`,
        error: error.message,
      };
    }
  }
}
