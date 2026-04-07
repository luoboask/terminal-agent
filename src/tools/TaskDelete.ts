/**
 * TaskDelete Tool - 删除任务
 * 
 * 基于原始源码改进，支持确认机制和归档选项
 */

import { z } from 'zod';
import { BaseTool, ToolResult } from '../core/Tool.js';
import { loadTasks, saveTasks } from '../utils/taskStorage.js';

const TaskDeleteInputSchema = z.object({
  taskId: z.string().describe('任务 ID'),
  task_id: z.string().optional().describe('任务 ID（下划线命名，兼容 AI）'),
  confirm: z.boolean().optional().describe('是否确认删除（默认 false）'),
  archive: z.boolean().optional().describe('是否先归档再删除（默认 true）'),
});

type Input = z.infer<typeof TaskDeleteInputSchema>;

export class TaskDeleteTool extends BaseTool<typeof TaskDeleteInputSchema> {
  readonly name = 'task_delete';
  readonly description = '删除任务，支持确认机制和归档选项';
  readonly inputSchema = TaskDeleteInputSchema;

  async execute(input: Input): Promise<ToolResult> {
    const taskId = input.taskId || input.task_id;
    const { confirm = false, archive = true } = input;

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

      // 如果没有确认，返回确认提示
      if (!confirm) {
        return {
          success: true,
          content: `⚠️ **确认删除**

📋 **任务 ID**: ${taskId}
📝 **标题**: ${task.subject}
📄 **描述**: ${task.description}

⚠️ 此操作将永久删除任务，是否继续？

请使用 \`confirm=true\` 参数确认删除。`,
          data: { taskId, requiresConfirmation: true },
        };
      }

      // 归档（如果启用）
      if (archive) {
        task.archived = true;
        task.archivedAt = new Date().toISOString();
      }

      // 删除任务
      tasks.splice(taskIndex, 1);
      saveTasks(tasks);

      return {
        success: true,
        content: `✅ **任务已删除**

📋 **任务 ID**: ${taskId}
📝 **标题**: ${task.subject}
🗄️ **归档**: ${archive ? '是' : '否'}
🕐 **删除时间**: ${new Date().toLocaleString('zh-CN')}`,
        data: { taskId, deleted: true, archived: archive },
      };
    } catch (error) {
      const err = error as Error;
      return {
        success: false,
        content: `❌ **任务删除失败**\n\n❌ 错误：${err.message}`,
        error: err.message,
      };
    }
  }
}
