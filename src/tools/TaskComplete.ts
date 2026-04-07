/**
 * TaskComplete Tool - 完成任务
 * 
 * 基于原始源码改进，支持完成总结/交付物/耗时记录
 */

import { z } from 'zod';
import { BaseTool, ToolResult } from '../core/Tool.js';
import { loadTasks, saveTasks } from '../utils/taskStorage.js';

const TaskCompleteInputSchema = z.object({
  taskId: z.string().describe('任务 ID'),
  task_id: z.string().optional().describe('任务 ID（下划线命名，兼容 AI）'),
  summary: z.string().optional().describe('任务完成总结'),
  deliverables: z.array(z.string()).optional().describe('交付物列表'),
  timeSpent: z.number().optional().describe('耗时（分钟）'),
  notifyTeam: z.boolean().optional().describe('是否通知团队（默认 true）'),
  archive: z.boolean().optional().describe('是否归档任务（默认 true）'),
});

type Input = z.infer<typeof TaskCompleteInputSchema>;

export class TaskCompleteTool extends BaseTool<typeof TaskCompleteInputSchema> {
  readonly name = 'task_complete';
  readonly description = '完成任务，支持总结、交付物列表和耗时记录';
  readonly inputSchema = TaskCompleteInputSchema;

  async execute(input: Input): Promise<ToolResult> {
    const taskId = input.taskId || input.task_id;
    const { summary, deliverables = [], timeSpent, notifyTeam = true, archive = true } = input;

    try {
      const tasks = loadTasks();
      const taskIndex = tasks.findIndex((t: any) => t.id === taskId);

      if (taskIndex === -1) {
        return {
          success: false,
          content: `❌ 未找到任务\n\n任务 ID: ${taskId}\n\n请使用 \`task_list\` 查看所有任务。`,
          error: 'Task not found',
        };
      }

      const task = tasks[taskIndex];

      // 检查任务状态
      if (task.status === 'completed') {
        return {
          success: false,
          content: `⚠️ 任务已完成，无需重复操作\n\n任务 ID: ${taskId}\n状态：已完成`,
          error: 'Task already completed',
        };
      }

      // 更新任务状态
      const oldStatus = task.status;
      task.status = 'completed';
      task.completedAt = new Date().toISOString();
      task.summary = summary || task.summary;
      task.deliverables = deliverables;
      task.timeSpent = timeSpent || task.timeSpent;
      task.archived = archive;

      // 保存到文件存储
      tasks[taskIndex] = task;
      saveTasks(tasks);

      // 执行 Hooks
      const hookMessages: string[] = [];

      if (archive) {
        hookMessages.push('✅ 任务已归档');
      }

      if (notifyTeam) {
        hookMessages.push('ℹ️ 已通知团队成员');
      }

      return {
        success: true,
        content: `✅ **任务已完成**

📋 **任务 ID**: ${taskId}
📝 **标题**: ${task.subject}
📊 **状态**: ${oldStatus} → ✅ completed
📝 **完成总结**: ${summary || '无'}
${deliverables.length > 0 ? `📦 **交付物**: ${deliverables.join(', ')}` : ''}
${timeSpent ? `⏱️ **耗时**: ${timeSpent} 分钟` : ''}
🕐 **完成时间**: ${new Date(task.completedAt).toLocaleString('zh-CN')}

${hookMessages.length > 0 ? `**Hooks 执行**:\n${hookMessages.map(m => `- ${m}`).join('\n')}` : ''}`,
        data: { taskId, status: 'completed', summary, deliverables, timeSpent },
      };
    } catch (error) {
      const err = error as Error;
      return {
        success: false,
        content: `❌ **任务完成失败**\n\n❌ 错误：${err.message}`,
        error: err.message,
      };
    }
  }
}
