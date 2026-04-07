/**
 * TaskGet Tool - 获取任务详情
 * 
 * 基于原始源码改进，支持完整任务信息
 */

import { z } from 'zod';
import { BaseTool, ToolResult } from '../core/Tool.js';
import { loadTasks } from '../utils/taskStorageV2.js';

const TaskGetInputSchema = z.object({
  taskId: z.string().describe('任务 ID'),
  task_id: z.string().optional().describe('任务 ID（下划线命名，兼容 AI）'),
});

type Input = z.infer<typeof TaskGetInputSchema>;

export class TaskGetTool extends BaseTool<typeof TaskGetInputSchema> {
  readonly name = 'task_get';
  readonly description = '获取任务的详细信息';
  readonly inputSchema = TaskGetInputSchema;

  async execute(input: Input): Promise<ToolResult> {
    const taskId = input.taskId || input.task_id;

    try {
      const tasks = loadTasks();
      const task = tasks.find((t: any) => t.id === taskId);

      if (!task) {
        return {
          success: false,
          content: `❌ 未找到任务\n\n任务 ID: ${taskId}\n\n请使用 \`task_list\` 查看所有任务。`,
          error: 'Task not found',
        };
      }

      // 获取阻塞关系
      const blocks = tasks.filter((t: any) => t.blockedBy?.includes(taskId)).map((t: any) => t.id);
      const blockedBy = tasks.filter((t: any) => t.blocks?.includes(taskId)).map((t: any) => t.id);

      return {
        success: true,
        content: `📋 **任务详情**

📋 **任务 ID**: ${task.id}
📝 **标题**: ${task.subject}
📄 **描述**: ${task.description}
🚩 **优先级**: ${this.getPriorityEmoji(task.priority)} ${task.priority}
📊 **状态**: ${this.getStatusEmoji(task.status)} ${task.status}
${task.owner ? `👤 **负责人**: ${task.owner}` : ''}
${task.dueDate ? `📅 **截止日期**: ${task.dueDate}` : ''}
🔗 **阻塞**: ${blocks.length > 0 ? blocks.join(', ') : '无'}
🔗 **被阻塞**: ${blockedBy.length > 0 ? blockedBy.join(', ') : '无'}
🕐 **创建时间**: ${new Date(task.createdAt).toLocaleString('zh-CN')}
${task.completedAt ? `✅ **完成时间**: ${new Date(task.completedAt).toLocaleString('zh-CN')}` : ''}`,
        data: {
          task: {
            id: task.id,
            subject: task.subject,
            description: task.description,
            status: task.status,
            priority: task.priority,
            blocks,
            blockedBy,
          },
        },
      };
    } catch (error) {
      const err = error as Error;
      return {
        success: false,
        content: `❌ **获取任务失败**\n\n❌ 错误：${err.message}`,
        error: err.message,
      };
    }
  }

  private getPriorityEmoji(priority: string): string {
    const emojis: Record<string, string> = {
      low: '🟢',
      medium: '🟡',
      high: '🔴',
    };
    return emojis[priority] || '⚪';
  }

  private getStatusEmoji(status: string): string {
    const emojis: Record<string, string> = {
      pending: '⏳',
      in_progress: '🔄',
      completed: '✅',
      stopped: '⏹️',
    };
    return emojis[status] || '⚪';
  }
}
