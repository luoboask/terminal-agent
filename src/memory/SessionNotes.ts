import { debug, info } from '../utils/logger.js';

/**
 * 会话笔记 (Session Notes)
 * 
 * 参考自 source/src/state/ 中的会话状态管理
 * 
 * 特点：
 * - 当前会话临时上下文
 * - 会话结束后自动清理
 * - 用于追踪当前对话中的重要信息
 */

export interface SessionNote {
  id: string;
  content: string;
  type: 'context' | 'decision' | 'observation' | 'pending';
  timestamp: number;
  relatedMessageId?: string;
}

export interface SessionNotesConfig {
  maxNotes?: number;
  autoExpireMinutes?: number; // 自动过期时间（可选）
}

/**
 * 会话笔记管理器
 * 
 * 管理当前会话的临时上下文，包括：
 * - 当前讨论的主题和上下文
 * - 临时决定和观察
 * - 待处理的事项
 * 
 * 注意：这些数据不会持久化，会话结束后丢失
 */
export class SessionNotes {
  private config: SessionNotesConfig;
  private notes: SessionNote[] = [];
  private sessionId: string;

  constructor(sessionId: string, config: SessionNotesConfig = {}) {
    this.sessionId = sessionId;
    this.config = {
      maxNotes: config.maxNotes || 100,
      autoExpireMinutes: config.autoExpireMinutes,
    };
    
    debug(`Session notes initialized for session: ${sessionId}`);
  }

  /**
   * 添加会话笔记
   */
  add(note: Omit<SessionNote, 'id' | 'timestamp'>): SessionNote {
    const newNote: SessionNote = {
      ...note,
      id: `note_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
      timestamp: Date.now(),
    };

    this.notes.unshift(newNote);

    // 限制数量
    if (this.notes.length > this.config.maxNotes!) {
      this.notes = this.notes.slice(0, this.config.maxNotes);
    }

    debug(`Added session note: ${newNote.id} (${note.type})`);
    return newNote;
  }

  /**
   * 获取会话笔记
   */
  getNotes(options?: {
    type?: SessionNote['type'];
    limit?: number;
    query?: string;
  }): SessionNote[] {
    let results = [...this.notes];

    if (options?.type) {
      results = results.filter(n => n.type === options.type);
    }

    if (options?.query) {
      const query = options.query.toLowerCase();
      results = results.filter(n =>
        n.content.toLowerCase().includes(query)
      );
    }

    const limit = options?.limit || 50;
    return results.slice(0, limit);
  }

  /**
   * 获取最近笔记
   */
  getRecent(limit: number = 10): SessionNote[] {
    return this.notes.slice(0, limit);
  }

  /**
   * 删除笔记
   */
  delete(id: string): boolean {
    const index = this.notes.findIndex(n => n.id === id);
    if (index === -1) return false;

    this.notes.splice(index, 1);
    debug(`Deleted session note: ${id}`);
    return true;
  }

  /**
   * 清空所有笔记
   */
  clear(): void {
    this.notes = [];
    info('Cleared all session notes');
  }

  /**
   * 获取会话 ID
   */
  getSessionId(): string {
    return this.sessionId;
  }

  /**
   * 导出为文本
   */
  export(): string {
    return this.notes.map(n => 
      `[${n.type.toUpperCase()}] ${new Date(n.timestamp).toISOString()}\n${n.content}`
    ).join('\n\n---\n\n');
  }
}
