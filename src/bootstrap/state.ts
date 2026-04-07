/**
 * 全局状态管理
 * 
 * 参考 claude-code-learning/src/bootstrap/state.ts
 * 管理项目根目录、工作目录、会话等项目级状态
 */

import { normalize } from 'path';

/**
 * 全局状态接口
 */
interface State {
  /** 稳定项目根目录 - 启动时设置，用于项目身份标识 */
  projectRoot: string;
  
  /** 原始工作目录 - 启动时的工作目录 */
  originalCwd: string;
  
  /** 会话项目目录 - 会话存储位置 (null = 使用 originalCwd) */
  sessionProjectDir: string | null;
  
  /** 是否启用了工作树模式 */
  worktreeMode: boolean;
}

/**
 * 全局状态实例
 */
const STATE: State = {
  projectRoot: process.cwd(),
  originalCwd: process.cwd(),
  sessionProjectDir: null,
  worktreeMode: false,
};

/**
 * 初始化状态
 * @param cwd - 当前工作目录
 */
export function initState(cwd: string): void {
  const normalized = normalize(cwd);
  STATE.projectRoot = normalized;
  STATE.originalCwd = normalized;
  STATE.sessionProjectDir = null;
  STATE.worktreeMode = false;
}

// ============ 项目根目录管理 ============

/**
 * 获取项目根目录
 * 用于项目身份标识（历史、技能、会话），不用于文件操作
 */
export function getProjectRoot(): string {
  return STATE.projectRoot;
}

/**
 * 设置项目根目录
 * 仅用于启动时或 --worktree 标志，会话中不应修改
 */
export function setProjectRoot(cwd: string): void {
  STATE.projectRoot = normalize(cwd);
}

// ============ 原始工作目录管理 ============

/**
 * 获取原始工作目录
 */
export function getOriginalCwd(): string {
  return STATE.originalCwd;
}

/**
 * 设置原始工作目录
 */
export function setOriginalCwd(cwd: string): void {
  STATE.originalCwd = normalize(cwd);
}

// ============ 会话项目目录管理 ============

/**
 * 获取会话项目目录
 * @returns 会话存储目录，null 表示使用 originalCwd
 */
export function getSessionProjectDir(): string | null {
  return STATE.sessionProjectDir;
}

/**
 * 设置会话项目目录
 * @param projectDir - 项目目录，null 表示使用 originalCwd
 */
export function setSessionProjectDir(projectDir: string | null): void {
  STATE.sessionProjectDir = projectDir ? normalize(projectDir) : null;
}

/**
 * 获取有效的会话存储目录
 * @returns 会话存储目录（projectRoot 或 sessionProjectDir）
 */
export function getSessionStorageDir(): string {
  return STATE.sessionProjectDir || STATE.projectRoot;
}

// ============ 工作树管理 ============

/**
 * 检查工作树模式是否启用
 */
export function isWorktreeModeEnabled(): boolean {
  return STATE.worktreeMode;
}

/**
 * 启用工作树模式
 */
export function enableWorktreeMode(): void {
  STATE.worktreeMode = true;
}

/**
 * 禁用工作树模式
 */
export function disableWorktreeMode(): void {
  STATE.worktreeMode = false;
}

// ============ 状态导出 ============

/**
 * 导出当前状态（用于调试）
 */
export function exportState(): State {
  return { ...STATE };
}

/**
 * 打印状态（用于调试）
 */
export function printState(): void {
  console.log('📊 当前状态:');
  console.log(`  项目根目录：${STATE.projectRoot}`);
  console.log(`  原始工作目录：${STATE.originalCwd}`);
  console.log(`  会话项目目录：${STATE.sessionProjectDir || '(使用项目根目录)'}`);
  console.log(`  工作树模式：${STATE.worktreeMode ? '✅' : '❌'}`);
}
