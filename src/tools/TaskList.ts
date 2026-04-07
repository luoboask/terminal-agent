/**
 * TaskList Tool - 列出任务
 * 
 * 基于原始源码改进，支持筛选/分组/排序
 */

import { z } from 'zod';
import { BaseTool, ToolResult } from '../core/Tool.js';
import { loadTasks } from '../utils/taskStorage.js';

const TaskListInputSchema = z.object({
  status: z.enum(['all', 'pending', 'in_progress', 'completed', 'stopped']).optional().describe('按状态筛选（默认 all）'),
  priority: z.enum(['all', 'low', 'medium', 'high']).optional().describe('按优先级筛选'),
  groupBy: z.enum(['none', 'status', 'priority']).optional().describe('分组显示（默认 none）'),
  limit: z.number().optional().describe('最大返回数量（默认 20）'),
});

type Input = z.infer<typeof TaskListInputSchema>;

export class TaskListTool extends BaseTool<typeof TaskListInputSchema> {
  readonly name = 'task_list';
  readonly description = '列出任务，支持状态/优先级筛选和分组显示';
  readonly inputSchema = TaskListInputSchema;

  async execute(input: Input): Promise<ToolResult> {
    const { status = 'all', priority = 'all', groupBy = 'none', limit = 20 } = input;

    try {
      let tasks = loadTasks();

      // 筛选
      if (status !== 'all') {
        tasks = tasks.filter((task: any) => task.status === status);
      }
      if (priority !== 'all') {
        tasks = tasks.filter((task: any) => task.priority === priority);
      }

      // 按创建时间排序（最新的在前）
      tasks = tasks.sort((a: any, b: any) =>
        new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
      );

      // 限制数量
      const truncated = tasks.length > limit;
      tasks = tasks.slice(0, limit);

      // 分组显示
      if (groupBy !== 'none') {
        const groups: Record<string, any[]> = {};
        tasks.forEach((task: any) => {
          const key = groupBy === 'status' ? task.status : (task.priority || 'all');
          if (!groups[key]) groups[key] = [];
          groups[key].push(task);
        });

        let output = `📋 **任务列表**\n\n`;
        Object.entries(groups).forEach(([key, groupTasks]) => {
          const emoji = this.getStatusEmoji(key) || this.getPriorityEmoji(key);
          output += `${emoji} **${key}** (${groupTasks.length}个)\n\n`;
          groupTasks.forEach((task: any) => {
            output += `- #${task.id}: ${task.subject}\n`;
          });
          output += '\n';
        });

        if (truncated) {
          output += `\n… 还有更多任务（已显示前${limit}个）`;
        }

        return { success: true, content: output, data: { groups, total: tasks.length } };
      }

      // 简洁输出：类似 claude-code-learning 格式
      if (tasks.length === 0) {
        return { success: true, content: 'No tasks found', data: { tasks: [], total: 0 } };
      }
      
      const lines = tasks.map((task: any) => {
        const statusIcon = this.getStatusEmoji(task.status);
        const priorityIcon = this.getPriorityEmoji(task.priority);
        return `${statusIcon} ${priorityIcon} #${task.id}: ${task.subject}`;
      });
      
      let content = lines.join('\n');
      
      if (truncated) {
        content += `\n… (+${tasks.length - limit} more)`;
      }
      
      return { success: true, content, data: { tasks, total: tasks.length } };
    } catch (error) {
      const err = error as Error;
      return {
        success: false,
        content: `❌ **获取任务列表失败**\n\n❌ 错误：${err.message}`,
        error: err.message,
      };
    }
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

  private getPriorityEmoji(priority: string): string {
    const emojis: Record<string, string> = {
      low: '🟢',
      medium: '🟡',
      high: '🔴',
    };
    return emojis[priority] || '⚪';
  }
}
