/**
 * 会话存储管理
 * 
 * 参考 claude-code-learning 的会话存储设计
 * 支持会话的创建、加载、保存和删除
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync, readdirSync, unlinkSync } from 'fs';
import { join, dirname } from 'path';
import { getSessionStorageDir, getProjectRoot } from '../bootstrap/state.js';
import { debug, warn } from './logger.js';

/**
 * 会话消息接口
 */
export interface SessionMessage {
  role: 'user' | 'assistant' | 'system' | 'tool';
  content: string;
  timestamp?: string;
  toolName?: string;
  toolCallId?: string;
}

/**
 * 会话接口
 */
export interface Session {
  /** 会话 ID */
  id: string;
  
  /** 会话标题 */
  title?: string;
  
  /** 创建时间 */
  createdAt: string;
  
  /** 最后更新时间 */
  updatedAt: string;
  
  /** 消息历史 */
  messages: SessionMessage[];
  
  /** 使用的模型 */
  model?: string;
  
  /** 会话元数据 */
  metadata?: Record<string, any>;
}

/**
 * 获取会话目录
 */
function getSessionDir(): string {
  return join(getSessionStorageDir(), '.source-deploy', 'sessions');
}

/**
 * 获取会话文件路径
 */
function getSessionPath(sessionId: string): string {
  return join(getSessionDir(), `${sessionId}.json`);
}

/**
 * 确保会话目录存在
 */
function ensureSessionDir(): void {
  const dir = getSessionDir();
  if (!existsSync(dir)) {
    mkdirSync(dir, { recursive: true });
  }
}

/**
 * 生成会话 ID
 */
function generateSessionId(): string {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substring(2, 11);
  return `session_${timestamp}_${random}`;
}

/**
 * 创建新会话
 */
export function createSession(title?: string, metadata?: Record<string, any>): Session {
  ensureSessionDir();
  
  const now = new Date().toISOString();
  const session: Session = {
    id: generateSessionId(),
    title: title || '新会话',
    createdAt: now,
    updatedAt: now,
    messages: [],
    metadata: metadata || {},
  };
  
  const path = getSessionPath(session.id);
  writeFileSync(path, JSON.stringify(session, null, 2), 'utf-8');
  
  debug(`Created session ${session.id}`);
  return session;
}

/**
 * 加载会话
 */
export function loadSession(sessionId: string): Session | null {
  const path = getSessionPath(sessionId);
  
  if (!existsSync(path)) {
    return null;
  }
  
  try {
    const content = readFileSync(path, 'utf-8');
    const session = JSON.parse(content) as Session;
    debug(`Loaded session ${sessionId} with ${session.messages.length} messages`);
    return session;
  } catch (error) {
    warn(`Failed to load session ${sessionId}: ${error}`);
    return null;
  }
}

/**
 * 保存会话
 */
export function saveSession(session: Session): void {
  ensureSessionDir();
  session.updatedAt = new Date().toISOString();
  
  const path = getSessionPath(session.id);
  writeFileSync(path, JSON.stringify(session, null, 2), 'utf-8');
  
  debug(`Saved session ${session.id} with ${session.messages.length} messages`);
}

/**
 * 添加消息到会话
 */
export function addMessage(sessionId: string, message: SessionMessage): Session | null {
  const session = loadSession(sessionId);
  
  if (!session) {
    return null;
  }
  
  session.messages.push({
    ...message,
    timestamp: new Date().toISOString(),
  });
  
  saveSession(session);
  return session;
}

/**
 * 删除会话
 */
export function deleteSession(sessionId: string): boolean {
  const path = getSessionPath(sessionId);
  
  if (!existsSync(path)) {
    return false;
  }
  
  try {
    unlinkSync(path);
    debug(`Deleted session ${sessionId}`);
    return true;
  } catch (error) {
    warn(`Failed to delete session ${sessionId}: ${error}`);
    return false;
  }
}

/**
 * 列出所有会话
 */
export function listSessions(): Session[] {
  const dir = getSessionDir();
  
  if (!existsSync(dir)) {
    return [];
  }
  
  try {
    const files = readdirSync(dir).filter(f => f.endsWith('.json'));
    const sessions: Session[] = [];
    
    for (const file of files) {
      const sessionId = file.replace('.json', '');
      const session = loadSession(sessionId);
      if (session) {
        sessions.push(session);
      }
    }
    
    // 按更新时间排序（最新的在前）
    sessions.sort((a, b) => 
      new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
    );
    
    debug(`Listed ${sessions.length} sessions`);
    return sessions;
  } catch (error) {
    warn(`Failed to list sessions: ${error}`);
    return [];
  }
}

/**
 * 获取最近的会话
 */
export function getRecentSessions(limit: number = 10): Session[] {
  const sessions = listSessions();
  return sessions.slice(0, limit);
}

/**
 * 搜索会话
 */
export function searchSessions(query: string): Session[] {
  const sessions = listSessions();
  const lowerQuery = query.toLowerCase();
  
  return sessions.filter(session => 
    session.title?.toLowerCase().includes(lowerQuery) ||
    session.messages.some(m => m.content.toLowerCase().includes(lowerQuery))
  );
}

/**
 * 清空会话消息
 */
export function clearSessionMessages(sessionId: string): Session | null {
  const session = loadSession(sessionId);
  
  if (!session) {
    return null;
  }
  
  session.messages = [];
  saveSession(session);
  
  debug(`Cleared messages for session ${sessionId}`);
  return session;
}

/**
 * 导出会话到 JSON
 */
export function exportSession(sessionId: string): string | null {
  const session = loadSession(sessionId);
  
  if (!session) {
    return null;
  }
  
  return JSON.stringify(session, null, 2);
}

/**
 * 导入会话
 */
export function importSession(json: string): Session | null {
  try {
    const session = JSON.parse(json) as Session;
    
    // 验证必要字段
    if (!session.id || !session.createdAt) {
      return null;
    }
    
    // 生成新 ID 避免冲突
    session.id = generateSessionId();
    session.updatedAt = new Date().toISOString();
    
    ensureSessionDir();
    const path = getSessionPath(session.id);
    writeFileSync(path, JSON.stringify(session, null, 2), 'utf-8');
    
    debug(`Imported session ${session.id}`);
    return session;
  } catch (error) {
    warn(`Failed to import session: ${error}`);
    return null;
  }
}

/**
 * 获取会话统计
 */
export function getSessionStats(): {
  totalSessions: number;
  totalMessages: number;
  oldestSession?: string;
  newestSession?: string;
} {
  const sessions = listSessions();
  
  if (sessions.length === 0) {
    return {
      totalSessions: 0,
      totalMessages: 0,
    };
  }
  
  const totalMessages = sessions.reduce((sum, s) => sum + s.messages.length, 0);
  
  return {
    totalSessions: sessions.length,
    totalMessages,
    oldestSession: sessions[sessions.length - 1]?.createdAt,
    newestSession: sessions[0]?.createdAt,
  };
}
