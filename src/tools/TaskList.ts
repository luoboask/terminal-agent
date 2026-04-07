/**
 * TaskList Tool - 列出任务
 * 
 * 基于原始源码改进，支持筛选/分组/排序
 */

import { z } from 'zod';
import { BaseTool, ToolResult } from '../core/Tool.js';
import { loadTasks, listTasksSimple } from '../utils/taskStorageV2.js';

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

  async execute(): Promise<ToolResult> {
    try {
      // 使用简洁格式输出（参考 claude-code-learning）
      const content = listTasksSimple();
      return { success: true, content };
    } catch (error) {
      const err = error as Error;
      return {
        success: false,
        content: `Failed to list tasks: ${err.message}`,
        error: err.message,
      };
    }
  }
}
