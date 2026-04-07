/**
 * 任务存储模块
 * 
 * 使用文件持久化存储任务
 * 解决进程重启后任务丢失的问题
 */

import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { debug, warn } from './logger.js';

// 获取当前文件所在目录
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// 任务存储文件路径（固定在 source-deploy 目录）
const TASK_STORAGE_FILE = join(__dirname, '../../.source-deploy-tasks.json');

// 任务接口
export interface Task {
  id: string;
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high';
  status: 'pending' | 'in_progress' | 'completed' | 'stopped' | 'cancelled';
  createdAt: string;
  updatedAt?: string;
  completedAt?: string;
  metadata?: Record<string, any>;
}

/**
 * 加载任务列表
 */
export function loadTasks(): Task[] {
  try {
    if (!existsSync(TASK_STORAGE_FILE)) {
      return [];
    }
    
    const content = readFileSync(TASK_STORAGE_FILE, 'utf-8');
    const tasks = JSON.parse(content);
    debug(`Loaded ${tasks.length} tasks from storage`);
    return tasks;
  } catch (error) {
    warn(`Failed to load tasks: ${error}`);
    return [];
  }
}

/**
 * 保存任务列表
 */
export function saveTasks(tasks: Task[]): void {
  try {
    writeFileSync(TASK_STORAGE_FILE, JSON.stringify(tasks, null, 2), 'utf-8');
    debug(`Saved ${tasks.length} tasks to storage`);
  } catch (error) {
    warn(`Failed to save tasks: ${error}`);
  }
}

/**
 * 创建任务
 */
export function createTask(task: Task): Task {
  const tasks = loadTasks();
  tasks.push(task);
  saveTasks(tasks);
  return task;
}

/**
 * 更新任务
 */
export function updateTask(taskId: string, updates: Partial<Task>): Task | null {
  const tasks = loadTasks();
  const taskIndex = tasks.findIndex(t => t.id === taskId);
  
  if (taskIndex === -1) {
    return null;
  }
  
  // 更新任务
  tasks[taskIndex] = {
    ...tasks[taskIndex],
    ...updates,
    updatedAt: new Date().toISOString(),
  };
  
  saveTasks(tasks);
  return tasks[taskIndex];
}

/**
 * 获取任务
 */
export function getTask(taskId: string): Task | null {
  const tasks = loadTasks();
  return tasks.find(t => t.id === taskId) || null;
}

/**
 * 删除任务
 */
export function deleteTask(taskId: string): boolean {
  const tasks = loadTasks();
  const taskIndex = tasks.findIndex(t => t.id === taskId);
  
  if (taskIndex === -1) {
    return false;
  }
  
  tasks.splice(taskIndex, 1);
  saveTasks(tasks);
  return true;
}

/**
 * 列出任务
 */
export function listTasks(status?: string): Task[] {
  const tasks = loadTasks();
  
  if (status) {
    return tasks.filter(t => t.status === status);
  }
  
  return tasks;
}
