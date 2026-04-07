/**
 * TaskOutput Tool - 获取任务输出
 * 
 * 基于原始源码改进，支持阻塞等待和超时控制
 */

import { z } from 'zod';
import { BaseTool, ToolResult } from '../core/Tool.js';
import { loadTasks } from '../utils/taskStorageV2.js';

const TaskOutputInputSchema = z.object({
  taskId: z.string().describe('任务 ID'),
  task_id: z.string().optional().describe('任务 ID（下划线命名，兼容 AI）'),
  block: z.boolean().optional().describe('是否等待完成（默认 true）'),
  timeout: z.number().optional().describe('超时时间（毫秒，默认 30000）'),
});

type Input = z.infer<typeof TaskOutputInputSchema>;

const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export class TaskOutputTool extends BaseTool<typeof TaskOutputInputSchema> {
  readonly name = 'task_output';
  readonly description = '获取任务输出/日志，支持阻塞等待和超时控制';
  readonly inputSchema = TaskOutputInputSchema;

  async execute(input: Input): Promise<ToolResult> {
    const taskId = input.taskId || input.task_id;
    const { block = true, timeout = 30000 } = input;

    try {
      let tasks = loadTasks();
      let task = tasks.find((t: any) => t.id === taskId);

      if (!task) {
        return {
          success: false,
          content: `❌ 未找到任务\n\n任务 ID: ${taskId}\n\n请使用 \`task_list\` 查看所有任务。`,
          error: 'Task not found',
        };
      }

      // 如果阻塞且任务未完成，等待
      if (block && (task.status === 'pending' || task.status === 'in_progress')) {
        const startTime = Date.now();
        while (Date.now() - startTime < timeout) {
          tasks = loadTasks();
          task = tasks.find((t: any) => t.id === taskId);

          if (task && task.status === 'completed') {
            break;
          }

          await sleep(100);
        }
      }

      // 检查是否超时
      const retrievalStatus = task.status === 'completed' ? 'success' : 
                             (task.status === 'pending' || task.status === 'in_progress') ? 'timeout' : 'success';

      return {
        success: true,
        content: `📋 **任务输出**

📋 **任务 ID**: ${taskId}
📝 **描述**: ${task.description}
📊 **状态**: ${task.status}
${task.summary ? `📝 **总结**: ${task.summary}` : ''}
${task.deliverables && task.deliverables.length > 0 ? `📦 **交付物**: ${task.deliverables.join(', ')}` : ''}
${task.timeSpent ? `⏱️ **耗时**: ${task.timeSpent} 分钟` : ''}
🕐 **创建时间**: ${new Date(task.createdAt).toLocaleString('zh-CN')}
${task.completedAt ? `✅ **完成时间**: ${new Date(task.completedAt).toLocaleString('zh-CN')}` : ''}

${retrievalStatus === 'timeout' ? '⚠️ **提示**: 任务尚未完成，已等待超时' : ''}`,
        data: {
          task_id: taskId,
          task_type: 'user_task',
          status: task.status,
          description: task.description,
          output: task.summary || '',
          retrieval_status: retrievalStatus,
        },
      };
    } catch (error) {
      const err = error as Error;
      return {
        success: false,
        content: `❌ **获取任务输出失败**\n\n❌ 错误：${err.message}`,
        error: err.message,
      };
    }
  }
}
