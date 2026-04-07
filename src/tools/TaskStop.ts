/**
 * TaskStop Tool - 停止任务
 * 
 * 基于原始源码改进，支持停止原因记录
 */

import { z } from 'zod';
import { BaseTool, ToolResult } from '../core/Tool.js';
import { loadTasks, saveTasks } from '../utils/taskStorageV2.js';

const TaskStopInputSchema = z.object({
  taskId: z.string().describe('任务 ID'),
  task_id: z.string().optional().describe('任务 ID（下划线命名，兼容 AI）'),
  reason: z.string().optional().describe('停止原因'),
});

type Input = z.infer<typeof TaskStopInputSchema>;

export class TaskStopTool extends BaseTool<typeof TaskStopInputSchema> {
  readonly name = 'task_stop';
  readonly description = '停止运行中的任务，支持记录停止原因';
  readonly inputSchema = TaskStopInputSchema;

  async execute(input: Input): Promise<ToolResult> {
    const taskId = input.taskId || input.task_id;
    const { reason = '用户手动停止' } = input;

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
      if (task.status !== 'in_progress' && task.status !== 'pending') {
        return {
          success: false,
          content: `⚠️ 任务未运行中，无法停止\n\n任务 ID: ${taskId}\n当前状态：${task.status}`,
          error: 'Task not running',
        };
      }

      // 更新任务状态
      const oldStatus = task.status;
      task.status = 'stopped';
      task.stoppedAt = new Date().toISOString();
      task.stopReason = reason;

      // 保存到文件存储
      tasks[taskIndex] = task;
      saveTasks(tasks);

      return {
        success: true,
        content: `✅ **任务已停止**

📋 **任务 ID**: ${taskId}
📝 **标题**: ${task.subject}
📊 **状态**: ${oldStatus} → ⏹️ stopped
❌ **停止原因**: ${reason}
🕐 **停止时间**: ${new Date(task.stoppedAt).toLocaleString('zh-CN')}`,
        data: { taskId, task_type: 'user_task', reason },
      };
    } catch (error) {
      const err = error as Error;
      return {
        success: false,
        content: `❌ **任务停止失败**\n\n❌ 错误：${err.message}`,
        error: err.message,
      };
    }
  }
}
