import { writeFileSync, readFileSync, existsSync } from 'fs';
import { join } from 'path';
import { debug, info, error } from '../utils/logger.js';

/**
 * 长期记忆 (Long-term Memory)
 * 
 * 参考自 source/src/memdir/ 和 source/src/utils/memory/
 * 
 * 特点：
 * - 跨会话持久化
 * - 重要事实和观察
 * - 用户偏好和项目知识
 */

export interface LongTermMemoryEntry {
  id: string;
  content: string;
  category: 'fact' | 'observation' | 'preference' | 'knowledge' | 'lesson';
  importance: number; // 1-10
  timestamp: number;
  lastAccessed?: number;
  accessCount: number;
  tags: string[];
}

export interface LongTermMemoryConfig {
  filePath: string;
  maxEntries?: number;
  minImportance?: number; // 最低重要性阈值
}

/**
 * 长期记忆管理器
 * 
 * 存储持久化的重要信息，包括：
 * - 用户偏好和工作习惯
 * - 项目架构和决策
 * - 学到的经验和教训
 * - 重要的观察和事实
 */
export class LongTermMemory {
  private config: LongTermMemoryConfig;
  private entries: LongTermMemoryEntry[] = [];
  private initialized = false;

  constructor(config: LongTermMemoryConfig) {
    this.config = {
      ...config,
      maxEntries: config.maxEntries || 500,
      minImportance: config.minImportance || 5,
    };
  }

  async initialize(): Promise<void> {
    if (this.initialized) return;

    if (existsSync(this.config.filePath)) {
      try {
        const content = readFileSync(this.config.filePath, 'utf-8');
        this.entries = JSON.parse(content);
        debug(`Loaded ${this.entries.length} long-term memories`);
      } catch (err) {
        error('Failed to load long-term memories:', err);
        this.entries = [];
      }
    }

    this.initialized = true;
  }

  private save(): void {
    try {
      writeFileSync(this.config.filePath, JSON.stringify(this.entries, null, 2), 'utf-8');
    } catch (err) {
      error('Failed to save long-term memories:', err);
    }
  }

  /**
   * 添加长期记忆
   */
  add(entry: Omit<LongTermMemoryEntry, 'id' | 'timestamp' | 'accessCount'>): LongTermMemoryEntry {
    // 检查重要性阈值
    if (entry.importance < this.config.minImportance!) {
      debug(`Skipping low-importance memory (${entry.importance} < ${this.config.minImportance})`);
      // 仍然保存但记录日志
    }

    const newEntry: LongTermMemoryEntry = {
      ...entry,
      id: `ltm_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
      timestamp: Date.now(),
      accessCount: 0,
    };

    this.entries.unshift(newEntry);
    
    // 限制数量
    if (this.entries.length > this.config.maxEntries!) {
      this.entries = this.entries.slice(0, this.config.maxEntries);
    }

    this.save();
    info(`Added long-term memory: ${newEntry.id} (importance: ${entry.importance})`);

    return newEntry;
  }

  /**
   * 检索长期记忆
   */
  retrieve(options?: {
    query?: string;
    categories?: LongTermMemoryEntry['category'][];
    tags?: string[];
    minImportance?: number;
    limit?: number;
  }): LongTermMemoryEntry[] {
    let results = [...this.entries];

    if (options?.query) {
      const query = options.query.toLowerCase();
      results = results.filter(e => 
        e.content.toLowerCase().includes(query) ||
        e.tags.some(tag => tag.toLowerCase().includes(query))
      );
    }

    if (options?.categories && options.categories.length > 0) {
      results = results.filter(e => options.categories!.includes(e.category));
    }

    if (options?.tags && options.tags.length > 0) {
      results = results.filter(e =>
        e.tags.some(tag => options.tags!.includes(tag))
      );
    }

    if (options?.minImportance) {
      results = results.filter(e => e.importance >= options.minImportance!);
    }

    // 按重要性和最近访问时间排序
    results.sort((a, b) => {
      const importanceDiff = b.importance - a.importance;
      if (importanceDiff !== 0) return importanceDiff;
      return (b.lastAccessed || 0) - (a.lastAccessed || 0);
    });

    const limit = options?.limit || 20;
    return results.slice(0, limit);
  }

  /**
   * 更新访问统计
   */
  recordAccess(id: string): void {
    const entry = this.entries.find(e => e.id === id);
    if (entry) {
      entry.lastAccessed = Date.now();
      entry.accessCount++;
      this.save();
    }
  }

  /**
   * 删除记忆
   */
  delete(id: string): boolean {
    const index = this.entries.findIndex(e => e.id === id);
    if (index === -1) return false;

    this.entries.splice(index, 1);
    this.save();
    return true;
  }

  /**
   * 获取所有记忆（用于导出）
   */
  getAll(): LongTermMemoryEntry[] {
    return [...this.entries];
  }
}
