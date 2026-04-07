/**
 * TaskUpdate Tool - 更新任务
 * 
 * 基于原始源码改进，支持智能字段更新
 */

import { z } from 'zod';
import { BaseTool, ToolResult } from '../core/Tool.js';
import { loadTasks, saveTasks } from '../utils/taskStorage.js';

const TaskUpdateInputSchema = z.object({
  taskId: z.string().describe('任务 ID'),
  task_id: z.string().optional().describe('任务 ID（下划线命名，兼容 AI）'),
  title: z.string().optional().describe('新标题'),
  subject: z.string().optional().describe('新主题（兼容，同 title）'),
  description: z.string().optional().describe('新描述'),
  status: z.enum(['pending', 'in_progress', 'completed', 'stopped']).optional().describe('新状态'),
  priority: z.enum(['low', 'medium', 'high']).optional().describe('新优先级'),
  dueDate: z.string().optional().describe('新截止日期'),
  metadata: z.record(z.unknown()).optional().describe('新元数据'),
});

type Input = z.infer<typeof TaskUpdateInputSchema>;

export class TaskUpdateTool extends BaseTool<typeof TaskUpdateInputSchema> {
  readonly name = 'task_update';
  readonly description = '更新任务的状态、优先级、描述等信息';
  readonly inputSchema = TaskUpdateInputSchema;

  async execute(input: Input): Promise<ToolResult> {
    // 支持两种命名方式
    const taskId = input.taskId || input.task_id;
    const { title, subject, description, status, priority, dueDate, metadata } = input;

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
      const appliedUpdates: string[] = [];

      // 智能更新字段（只有值不同时才更新）
      if (title !== undefined && title !== task.title) {
        task.title = title;
        task.subject = title;
        appliedUpdates.push(`标题：→ ${title}`);
      } else if (subject !== undefined && subject !== task.subject) {
        task.subject = subject;
        task.title = subject;
        appliedUpdates.push(`标题：→ ${subject}`);
      }

      if (description !== undefined && description !== task.description) {
        task.description = description;
        appliedUpdates.push(`描述：→ ${description}`);
      }

      if (status !== undefined && status !== task.status) {
        const oldStatus = task.status;
        task.status = status;
        appliedUpdates.push(`状态：${oldStatus} → ${status}`);

        // 自动设置完成时间
        if (status === 'completed' && !task.completedAt) {
          task.completedAt = new Date().toISOString();
          appliedUpdates.push(`完成时间：→ ${task.completedAt}`);
        }
      }

      if (priority !== undefined && priority !== task.priority) {
        task.priority = priority;
        appliedUpdates.push(`优先级：→ ${priority}`);
      }

      if (dueDate !== undefined && dueDate !== task.dueDate) {
        task.dueDate = dueDate;
        appliedUpdates.push(`截止日期：→ ${dueDate}`);
      }

      if (metadata !== undefined) {
        task.metadata = { ...task.metadata, ...metadata };
        appliedUpdates.push(`元数据：已更新`);
      }

      // 保存到文件存储
      tasks[taskIndex] = task;
      saveTasks(tasks);

      return {
        success: true,
        content: `✅ **任务已更新**

📋 **任务 ID**: ${taskId}

**更新内容**:
${appliedUpdates.map(u => `- ${u}`).join('\n')}

🕐 **更新时间**: ${new Date().toLocaleString('zh-CN')}`,
        data: { taskId, appliedUpdates },
      };
    } catch (error) {
      const err = error as Error;
      return {
        success: false,
        content: `❌ **任务更新失败**\n\n❌ 错误：${err.message}`,
        error: err.message,
      };
    }
  }
}
