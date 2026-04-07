/**
 * TaskCreate Tool - 创建任务
 * 
 * 基于原始源码改进，支持优先级/截止日期/元数据
 */

import { z } from 'zod';
import { BaseTool, ToolResult } from '../core/Tool.js';
import { createTask, loadTasks } from '../utils/taskStorageV2.js';

const TaskCreateInputSchema = z.object({
  title: z.string().describe('任务标题'),
  subject: z.string().optional().describe('任务主题（兼容，同 title）'),
  description: z.string().describe('任务描述'),
  priority: z.enum(['low', 'medium', 'high']).optional().describe('优先级（默认 medium）'),
  dueDate: z.string().optional().describe('截止日期'),
  metadata: z.record(z.unknown()).optional().describe('元数据'),
});

type Input = z.infer<typeof TaskCreateInputSchema>;

export class TaskCreateTool extends BaseTool<typeof TaskCreateInputSchema> {
  readonly name = 'task_create';
  readonly description = '创建新任务，支持优先级、截止日期和元数据';
  readonly inputSchema = TaskCreateInputSchema;

  async execute(input: Input): Promise<ToolResult> {
    const { title, subject, description, priority = 'medium', dueDate, metadata } = input;

    try {
      // 检查是否有重复任务（相同标题且未完成）
      const tasks = loadTasks();
      const similarTask = tasks.find(t => 
        t.title === title && 
        !['completed', 'failed'].includes(t.status)
      );
      
      if (similarTask) {
        return {
          success: false,
          content: `⚠️ 任务已存在

相似任务：
📋 ID: ${similarTask.id}
📝 标题：${similarTask.title}
📊 状态：${similarTask.status}
🕐 创建：${similarTask.createdAt}

该任务已在进行中，无需重复创建。`,
          error: 'Duplicate task',
        };
      }

      // 创建任务对象
      const taskId = `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      const createdAt = new Date().toISOString();

      const task = {
        id: taskId,
        subject: title || subject,
        title: title || subject,
        description,
        priority,
        dueDate: dueDate || null,
        status: 'pending' as const,
        owner: undefined,
        blocks: [],
        blockedBy: [],
        metadata: metadata || {},
        createdAt,
        completedAt: null,
      };

      // 保存到文件存储
      createTask(task);

      return {
        success: true,
        content: `✅ **任务已创建**

📋 **任务 ID**: ${taskId}
📝 **标题**: ${task.subject}
📄 **描述**: ${task.description}
🚩 **优先级**: ${this.getPriorityEmoji(priority)} ${priority}
${dueDate ? `📅 **截止日期**: ${dueDate}` : ''}
📊 **状态**: 待处理
🕐 **创建时间**: ${createdAt}

任务已添加到待处理列表，随时可以开始执行。`,
        data: {
          task: {
            id: taskId,
            subject: task.subject,
            priority: task.priority,
          },
        },
      };
    } catch (error) {
      const err = error as Error;
      return {
        success: false,
        content: `❌ **任务创建失败**\n\n❌ 错误：${err.message}`,
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
}
