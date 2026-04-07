/**
 * 任务存储模块 V2
 * 
 * 参考 claude-code-learning 设计：
 * - 简化的任务状态（pending, in_progress, completed）
 * - 支持任务阻塞关系（blocks/blockedBy）
 * - 支持 activeForm（进行中时显示的文本）
 * - 高水位标记防止 ID 复用
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync, readdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { debug, warn } from './logger.js';

// 获取当前文件所在目录
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// 任务存储目录（固定在 source-deploy 目录）
const TASK_STORAGE_DIR = join(__dirname, '../../.source-deploy-tasks');

// 高水位标记文件
const HIGH_WATER_MARK_FILE = '.highwatermark';

// 任务状态（参考 claude-code-learning）
export type TaskStatus = 'pending' | 'in_progress' | 'completed';
export const TASK_STATUSES: TaskStatus[] = ['pending', 'in_progress', 'completed'];

// 任务接口
export interface Task {
  id: string;
  subject: string;  // 标题（使用 subject 而非 title，与 claude-code-learning 一致）
  description: string;
  activeForm?: string;  // 进行中时显示的文本（如 "Running tests"）
  priority: 'low' | 'medium' | 'high';
  status: TaskStatus;
  owner?: string;  // agent ID
  blocks: string[];  // 此任务阻塞的其他任务 ID
  blockedBy: string[];  // 阻塞此任务的其他任务 ID
  metadata?: Record<string, any>;
  createdAt: string;
  updatedAt?: string;
  completedAt?: string;
}

/**
 * 确保任务存储目录存在
 */
function ensureTaskDir(): void {
  if (!existsSync(TASK_STORAGE_DIR)) {
    mkdirSync(TASK_STORAGE_DIR, { recursive: true });
  }
}

/**
 * 获取任务文件路径
 */
function getTaskPath(taskId: string): string {
  return join(TASK_STORAGE_DIR, `${taskId}.json`);
}

/**
 * 获取高水位标记文件路径
 */
function getHighWaterMarkPath(): string {
  return join(TASK_STORAGE_DIR, HIGH_WATER_MARK_FILE);
}

/**
 * 读取高水位标记
 */
function readHighWaterMark(): number {
  const path = getHighWaterMarkPath();
  try {
    const content = readFileSync(path, 'utf-8').trim();
    const value = parseInt(content, 10);
    return isNaN(value) ? 0 : value;
  } catch {
    return 0;
  }
}

/**
 * 写入高水位标记
 */
function writeHighWaterMark(value: number): void {
  ensureTaskDir();
  writeFileSync(getHighWaterMarkPath(), String(value), 'utf-8');
}

/**
 * 生成唯一任务 ID
 */
function generateTaskId(): string {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substring(2, 11);
  return `task_${timestamp}_${random}`;
}

/**
 * 加载所有任务
 */
export function loadTasks(): Task[] {
  try {
    ensureTaskDir();
    
    if (!existsSync(TASK_STORAGE_DIR)) {
      return [];
    }
    
    const files = readdirSync(TASK_STORAGE_DIR).filter(f => f.endsWith('.json'));
    const tasks: Task[] = [];
    
    for (const file of files) {
      try {
        const content = readFileSync(join(TASK_STORAGE_DIR, file), 'utf-8');
        const task = JSON.parse(content) as Task;
        tasks.push(task);
      } catch (error) {
        warn(`Failed to load task ${file}: ${error}`);
      }
    }
    
    // 按创建时间排序（最新的在前）
    tasks.sort((a, b) => 
      new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    );
    
    debug(`Loaded ${tasks.length} tasks from storage`);
    return tasks;
  } catch (error) {
    warn(`Failed to load tasks: ${error}`);
    return [];
  }
}

/**
 * 创建任务
 */
export function createTask(task: Omit<Task, 'id' | 'createdAt'>): Task {
  ensureTaskDir();
  
  const taskId = generateTaskId();
  const now = new Date().toISOString();
  
  const newTask: Task = {
    ...task,
    id: taskId,
    createdAt: now,
    blocks: task.blocks || [],
    blockedBy: task.blockedBy || [],
  };
  
  const path = getTaskPath(taskId);
  writeFileSync(path, JSON.stringify(newTask, null, 2), 'utf-8');
  
  debug(`Created task ${taskId}: ${newTask.subject}`);
  return newTask;
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
  
  const task = tasks[taskIndex];
  const updatedTask = {
    ...task,
    ...updates,
    id: taskId,  // 确保 ID 不被修改
    updatedAt: new Date().toISOString(),
  };
  
  // 如果状态变为 completed，设置 completedAt
  if (updates.status === 'completed' && !updatedTask.completedAt) {
    updatedTask.completedAt = new Date().toISOString();
  }
  
  tasks[taskIndex] = updatedTask;
  saveTasks(tasks);
  
  debug(`Updated task ${taskId}`);
  return updatedTask;
}

/**
 * 删除任务
 */
export function deleteTask(taskId: string): boolean {
  const path = getTaskPath(taskId);
  
  if (!existsSync(path)) {
    return false;
  }
  
  // 更新高水位标记
  const numericId = parseInt(taskId.split('_')[1] || '0', 10);
  if (!isNaN(numericId)) {
    const currentMark = readHighWaterMark();
    if (numericId > currentMark) {
      writeHighWaterMark(numericId);
    }
  }
  
  // 删除文件
  const { unlinkSync } = require('fs');
  unlinkSync(path);
  
  debug(`Deleted task ${taskId}`);
  return true;
}

/**
 * 保存所有任务
 */
export function saveTasks(tasks: Task[]): void {
  ensureTaskDir();
  // 每个任务保存为单独的文件
  for (const task of tasks) {
    const path = getTaskPath(task.id);
    writeFileSync(path, JSON.stringify(task, null, 2), 'utf-8');
  }
}

/**
 * 获取任务列表（简洁格式，参考 claude-code-learning）
 */
export function listTasksSimple(): string {
  const tasks = loadTasks();
  
  // 过滤内部任务
  const visibleTasks = tasks.filter(t => !t.metadata?._internal);
  
  // 构建已完成任务 ID 集合（用于过滤阻塞关系）
  const completedTaskIds = new Set(
    visibleTasks.filter(t => t.status === 'completed').map(t => t.id)
  );
  
  if (visibleTasks.length === 0) {
    return 'No tasks found';
  }
  
  const lines = visibleTasks.map(task => {
    const statusIcon = {
      pending: '⚪',
      in_progress: '⏳',
      completed: '✅'
    }[task.status] || '⚪';
    
    const priorityIcon = {
      low: '🟢',
      medium: '🟡',
      high: '🔴'
    }[task.priority] || '⚪';
    
    const owner = task.owner ? ` (${task.owner})` : '';
    
    // 过滤已完成的阻塞任务
    const activeBlockedBy = task.blockedBy.filter(id => !completedTaskIds.has(id));
    const blocked = activeBlockedBy.length > 0
      ? ` [blocked by ${activeBlockedBy.map(id => `#${id}`).join(', ')}]`
      : '';
    
    return `${statusIcon} ${priorityIcon} #${task.id}: ${task.subject}${owner}${blocked}`;
  });
  
  return lines.join('\n');
}

/**
 * 批量完成任务
 */
export function completeTasks(filter: (task: Task) => boolean): number {
  const tasks = loadTasks();
  let completedCount = 0;
  const now = new Date().toISOString();
  
  for (const task of tasks) {
    if (task.status !== 'completed' && filter(task)) {
      task.status = 'completed';
      task.completedAt = now;
      task.updatedAt = now;
      completedCount++;
    }
  }
  
  saveTasks(tasks);
  return completedCount;
}

/**
 * 清理任务（删除已完成超过指定时间的任务）
 */
export function cleanupTasks(maxAgeHours: number = 24): number {
  const tasks = loadTasks();
  const now = Date.now();
  const maxAgeMs = maxAgeHours * 60 * 60 * 1000;
  
  let deletedCount = 0;
  const tasksToDelete: string[] = [];
  
  for (const task of tasks) {
    // 删除已完成的任务
    if (task.status === 'completed' && task.completedAt) {
      const completedAt = new Date(task.completedAt).getTime();
      if (now - completedAt > maxAgeMs) {
        tasksToDelete.push(task.id);
      }
    }
    
    // 删除名称为 undefined 的任务
    if (!task.subject || task.subject === 'undefined') {
      tasksToDelete.push(task.id);
    }
  }
  
  // 删除任务
  for (const taskId of tasksToDelete) {
    if (deleteTask(taskId)) {
      deletedCount++;
    }
  }
  
  debug(`Cleaned up ${deletedCount} tasks`);
  return deletedCount;
}
