import { z } from 'zod';
import { BaseTool, ToolResult } from '../core/Tool.js';
import { info, debug, error } from '../utils/logger.js';

/**
 * TodoWrite 工具 - 任务列表管理
 * 
 * 参考自 source/src/tools/TodoWriteTool/TodoWriteTool.ts
 * 简化版本，保留核心功能：
 * - 创建、更新、删除待办事项
 * - 支持任务状态追踪
 */

interface TodoItem {
  id: string;
  content: string;
  status: 'pending' | 'in_progress' | 'completed';
  priority?: 'low' | 'medium' | 'high';
}

interface TodoWriteInput {
  todos: Array<{
    id?: string;
    content: string;
    status?: 'pending' | 'in_progress' | 'completed';
    priority?: 'low' | 'medium' | 'high';
  }>;
  operation?: 'set' | 'add' | 'update' | 'delete';
}

// 简单的内存存储（实际应该持久化）
let todoStore: Map<string, TodoItem> = new Map();
let todoIdCounter = 1;

export class TodoWriteTool extends BaseTool {
  readonly name = 'todo_write';
  readonly description = 'Create, update, or delete todo items. Helps track progress on multi-step tasks.';
  readonly inputSchema = z.object({
    todos: z.array(z.object({
      id: z.string().optional(),
      content: z.string().describe('The task description'),
      status: z.enum(['pending', 'in_progress', 'completed']).optional(),
      priority: z.enum(['low', 'medium', 'high']).optional(),
    })).describe('List of todo items to add/update'),
    operation: z.enum(['set', 'add', 'update', 'delete']).optional().describe('Operation type (default: add)'),
  });

  validateInput(input: unknown): TodoWriteInput | null {
    try {
      return this.inputSchema.parse(input);
    } catch (err) {
      if (err instanceof z.ZodError) {
        error('TodoWrite validation failed:', err.errors.map(e => e.message).join(', '));
      }
      return null;
    }
  }

  async execute(input: TodoWriteInput): Promise<ToolResult> {
    const { todos, operation = 'add' } = input;

    try {
      const results: Array<{ id: string; content: string; status: string }> = [];

      switch (operation) {
        case 'set':
          // 替换所有任务
          todoStore.clear();
          for (const todo of todos) {
            const id = todo.id || `todo_${todoIdCounter++}`;
            const item: TodoItem = {
              id,
              content: todo.content,
              status: todo.status || 'pending',
              priority: todo.priority,
            };
            todoStore.set(id, item);
            results.push({ id, content: item.content, status: item.status });
          }
          break;

        case 'add':
          // 添加新任务
          for (const todo of todos) {
            const id = todo.id || `todo_${todoIdCounter++}`;
            const item: TodoItem = {
              id,
              content: todo.content,
              status: todo.status || 'pending',
              priority: todo.priority,
            };
            todoStore.set(id, item);
            results.push({ id, content: item.content, status: item.status });
          }
          break;

        case 'update':
          // 更新现有任务
          for (const todo of todos) {
            if (!todo.id) {
              continue;
            }
            const existing = todoStore.get(todo.id);
            if (existing) {
              const updated: TodoItem = {
                ...existing,
                content: todo.content !== undefined ? todo.content : existing.content,
                status: todo.status || existing.status,
                priority: todo.priority !== undefined ? todo.priority : existing.priority,
              };
              todoStore.set(todo.id, updated);
              results.push({ id: todo.id, content: updated.content, status: updated.status });
            }
          }
          break;

        case 'delete':
          // 删除任务
          for (const todo of todos) {
            if (todo.id && todoStore.has(todo.id)) {
              todoStore.delete(todo.id);
              results.push({ id: todo.id, content: 'deleted', status: 'deleted' });
            }
          }
          break;
      }

      debug(`TodoWrite completed: ${results.length} items affected`);

      // 返回当前所有任务
      const allTodos = Array.from(todoStore.values());
      
      return {
        success: true,
        content: JSON.stringify({
          affected: results,
          todos: allTodos.sort((a, b) => {
            // 按状态和优先级排序
            const statusOrder = { pending: 0, in_progress: 1, completed: 2 };
            const priorityOrder = { high: 0, medium: 1, low: 2 };
            const statusDiff = statusOrder[a.status] - statusOrder[b.status];
            if (statusDiff !== 0) return statusDiff;
            return priorityOrder[a.priority || 'medium'] - priorityOrder[b.priority || 'medium'];
          }),
        }, null, 2),
      };
    } catch (err) {
      error('TodoWrite execution failed:', err);
      return {
        success: false,
        content: `Todo write failed: ${err instanceof Error ? err.message : String(err)}`,
        error: 'TODO_WRITE_FAILED',
      };
    }
  }
}
