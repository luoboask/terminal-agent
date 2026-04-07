import { writeFileSync, readFileSync, existsSync } from 'fs';
import { join } from 'path';
import { debug, info, error } from '../utils/logger.js';

/**
 * 任务计划 (Task Plans)
 * 
 * 参考自 source/src/tasks/ 和 source/src/Task.ts
 * 
 * 特点：
 * - 待办事项和进度追踪
 * - 任务依赖关系
 * - 任务状态管理
 */

export interface Task {
  id: string;
  title: string;
  description?: string;
  status: 'pending' | 'in_progress' | 'blocked' | 'completed' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  parentTaskId?: string;
  subTasks: string[]; // Task IDs
  dependencies: string[]; // Task IDs that must be completed first
  createdAt: number;
  updatedAt: number;
  completedAt?: number;
  tags: string[];
  metadata?: Record<string, unknown>;
}

export interface TaskPlan {
  id: string;
  name: string;
  description?: string;
  tasks: Map<string, Task>;
  createdAt: number;
  updatedAt: number;
}

export interface TaskPlannerConfig {
  filePath?: string; // 默认为 .source-deploy-tasks.json
}

/**
 * 任务计划管理器
 * 
 * 管理待办事项和进度追踪，包括：
 * - 创建和更新任务
 * - 任务依赖管理
 * - 进度追踪
 * - 任务层次结构（父子任务）
 */
export class TaskPlanner {
  private config: TaskPlannerConfig;
  private plans: Map<string, TaskPlan> = new Map();
  private currentPlanId?: string;
  private initialized = false;

  constructor(config: TaskPlannerConfig = {}) {
    this.config = config;
  }

  async initialize(): Promise<void> {
    if (this.initialized) return;

    const filePath = this.config.filePath || '.source-deploy-tasks.json';

    if (existsSync(filePath)) {
      try {
        const content = readFileSync(filePath, 'utf-8');
        const data = JSON.parse(content);
        
        // 恢复 plans
        for (const planData of data.plans || []) {
          const plan: TaskPlan = {
            ...planData,
            tasks: new Map(Object.entries(planData.tasks || {})),
          };
          this.plans.set(plan.id, plan);
        }

        this.currentPlanId = data.currentPlanId;
        info(`Loaded task planner with ${this.plans.size} plans`);
      } catch (err) {
        error('Failed to load task planner:', err);
      }
    } else {
      // 创建默认计划
      this.createPlan('Default', 'Default task plan');
    }

    this.initialized = true;
  }

  private save(): void {
    const filePath = this.config.filePath || '.source-deploy-tasks.json';

    try {
      const data = {
        plans: Array.from(this.plans.values()).map(plan => ({
          ...plan,
          tasks: Object.fromEntries(plan.tasks),
        })),
        currentPlanId: this.currentPlanId,
        updatedAt: Date.now(),
      };

      writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf-8');
    } catch (err) {
      error('Failed to save task planner:', err);
    }
  }

  /**
   * 创建新计划
   */
  createPlan(name: string, description?: string): TaskPlan {
    const plan: TaskPlan = {
      id: `plan_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
      name,
      description,
      tasks: new Map(),
      createdAt: Date.now(),
      updatedAt: Date.now(),
    };

    this.plans.set(plan.id, plan);
    
    if (!this.currentPlanId) {
      this.currentPlanId = plan.id;
    }

    this.save();
    info(`Created task plan: ${plan.id} (${name})`);
    return plan;
  }

  /**
   * 获取当前计划
   */
  getCurrentPlan(): TaskPlan | undefined {
    if (!this.currentPlanId) return undefined;
    return this.plans.get(this.currentPlanId);
  }

  /**
   * 切换计划
   */
  switchPlan(planId: string): boolean {
    if (!this.plans.has(planId)) {
      return false;
    }
    this.currentPlanId = planId;
    this.save();
    return true;
  }

  /**
   * 创建任务
   */
  createTask(title: string, options?: Partial<Task>): Task {
    const plan = this.getCurrentPlan();
    if (!plan) {
      throw new Error('No active task plan');
    }

    const task: Task = {
      id: `task_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
      title,
      description: options?.description,
      status: options?.status || 'pending',
      priority: options?.priority || 'medium',
      parentTaskId: options?.parentTaskId,
      subTasks: [],
      dependencies: options?.dependencies || [],
      createdAt: Date.now(),
      updatedAt: Date.now(),
      tags: options?.tags || [],
      metadata: options?.metadata,
    };

    plan.tasks.set(task.id, task);

    // 如果有父任务，添加到父任务的 subTasks
    if (task.parentTaskId) {
      const parent = plan.tasks.get(task.parentTaskId);
      if (parent) {
        parent.subTasks.push(task.id);
        parent.updatedAt = Date.now();
      }
    }

    plan.updatedAt = Date.now();
    this.save();
    info(`Created task: ${task.id} (${title})`);

    return task;
  }

  /**
   * 更新任务状态
   */
  updateTaskStatus(taskId: string, status: Task['status']): boolean {
    const plan = this.getCurrentPlan();
    if (!plan) return false;

    const task = plan.tasks.get(taskId);
    if (!task) return false;

    task.status = status;
    task.updatedAt = Date.now();

    if (status === 'completed') {
      task.completedAt = Date.now();
    }

    plan.updatedAt = Date.now();
    this.save();
    debug(`Updated task status: ${taskId} -> ${status}`);

    return true;
  }

  /**
   * 更新任务
   */
  updateTask(taskId: string, updates: Partial<Task>): boolean {
    const plan = this.getCurrentPlan();
    if (!plan) return false;

    const task = plan.tasks.get(taskId);
    if (!task) return false;

    Object.assign(task, updates);
    task.updatedAt = Date.now();
    plan.updatedAt = Date.now();
    this.save();

    return true;
  }

  /**
   * 删除任务
   */
  deleteTask(taskId: string): boolean {
    const plan = this.getCurrentPlan();
    if (!plan) return false;

    // 先删除子任务
    const task = plan.tasks.get(taskId);
    if (task) {
      for (const subTaskId of task.subTasks) {
        this.deleteTask(subTaskId);
      }
    }

    const deleted = plan.tasks.delete(taskId);
    if (deleted) {
      plan.updatedAt = Date.now();
      this.save();
      info(`Deleted task: ${taskId}`);
    }

    return deleted;
  }

  /**
   * 获取任务
   */
  getTask(taskId: string): Task | undefined {
    const plan = this.getCurrentPlan();
    if (!plan) return undefined;
    return plan.tasks.get(taskId);
  }

  /**
   * 获取所有任务
   */
  getAllTasks(options?: {
    status?: Task['status'];
    priority?: Task['priority'];
    tags?: string[];
  }): Task[] {
    const plan = this.getCurrentPlan();
    if (!plan) return [];

    let tasks = Array.from(plan.tasks.values());

    if (options?.status) {
      tasks = tasks.filter(t => t.status === options.status);
    }

    if (options?.priority) {
      tasks = tasks.filter(t => t.priority === options.priority);
    }

    if (options?.tags && options.tags.length > 0) {
      tasks = tasks.filter(t =>
        t.tags.some(tag => options.tags!.includes(tag))
      );
    }

    // 按优先级和创建时间排序
    const priorityOrder = { urgent: 0, high: 1, medium: 2, low: 3 };
    tasks.sort((a, b) => {
      const priorityDiff = priorityOrder[a.priority] - priorityOrder[b.priority];
      if (priorityDiff !== 0) return priorityDiff;
      return b.createdAt - a.createdAt;
    });

    return tasks;
  }

  /**
   * 获取进度摘要
   */
  getProgress(): {
    total: number;
    completed: number;
    inProgress: number;
    blocked: number;
    pending: number;
    percentComplete: number;
  } {
    const tasks = this.getAllTasks();
    const total = tasks.length;
    
    const completed = tasks.filter(t => t.status === 'completed').length;
    const inProgress = tasks.filter(t => t.status === 'in_progress').length;
    const blocked = tasks.filter(t => t.status === 'blocked').length;
    const pending = tasks.filter(t => t.status === 'pending').length;

    return {
      total,
      completed,
      inProgress,
      blocked,
      pending,
      percentComplete: total > 0 ? Math.round((completed / total) * 100) : 0,
    };
  }

  /**
   * 导出为文本
   */
  export(): string {
    const plan = this.getCurrentPlan();
    if (!plan) return 'No active plan';

    const parts: string[] = [
      `# Task Plan: ${plan.name}`,
      plan.description || '',
      '',
    ];

    const progress = this.getProgress();
    parts.push(
      `**Progress:** ${progress.completed}/${progress.total} (${progress.percentComplete}%)`,
      `- Completed: ${progress.completed}`,
      `- In Progress: ${progress.inProgress}`,
      `- Blocked: ${progress.blocked}`,
      `- Pending: ${progress.pending}`,
      '',
      '---',
      '',
    );

    // 按状态分组显示任务
    const byStatus = {
      in_progress: this.getAllTasks({ status: 'in_progress' }),
      blocked: this.getAllTasks({ status: 'blocked' }),
      pending: this.getAllTasks({ status: 'pending' }),
      completed: this.getAllTasks({ status: 'completed' }),
    };

    for (const [status, tasks] of Object.entries(byStatus)) {
      if (tasks.length > 0) {
        parts.push(`## ${status.replace('_', ' ').toUpperCase()}`);
        parts.push('');
        for (const task of tasks) {
          const priorityIcon = {
            urgent: '🔴',
            high: '🟠',
            medium: '🟡',
            low: '🟢',
          }[task.priority];
          
          parts.push(`- ${priorityIcon} [${task.id.slice(-6)}] ${task.title}`);
          if (task.description) {
            parts.push(`  ${task.description}`);
          }
        }
        parts.push('');
      }
    }

    return parts.join('\n');
  }
}
