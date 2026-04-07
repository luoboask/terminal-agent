import { writeFileSync, readFileSync, existsSync, mkdirSync } from 'fs';
import { join } from 'path';
import { debug, warn, info } from '../utils/logger.js';
import { LongTermMemory, LongTermMemoryConfig } from './LongTermMemory.js';
import { SessionNotes, SessionNotesConfig } from './SessionNotes.js';
import { ProjectContext, ProjectContextConfig } from './ProjectContext.js';
import { TaskPlanner, TaskPlannerConfig } from './TaskPlanner.js';

/**
 * 基础记忆条目（向后兼容）
 */
export interface MemoryEntry {
  id: string;
  type: 'note' | 'fact' | 'task' | 'observation';
  content: string;
  timestamp: number;
  tags?: string[];
  metadata?: Record<string, unknown>;
}

/**
 * 记忆管理器配置
 */
export interface MemoryConfig {
  memoryDir: string;
  maxMemories?: number;
  projectRoot?: string;
  sessionId?: string;
}

/**
 * 4 层记忆系统
 * 
 * 参考自 source/src/memdir/, source/src/state/, source/src/tasks/
 * 
 * 层次结构：
 * 1. **长期记忆 (Long-term Memory)** - 跨会话持久化的重要信息
 * 2. **会话笔记 (Session Notes)** - 当前会话的临时上下文
 * 3. **项目上下文 (Project Context)** - 项目特定的配置和知识
 * 4. **任务计划 (Task Plans)** - 待办事项和进度追踪
 * 
 * 设计原则：
 * - 每层有明确的职责和生命周期
 * - 支持独立使用和组合使用
 * - 与 OpenClaw 记忆系统对接兼容
 */
export class MemoryManager {
  private config: MemoryConfig;
  private memories: MemoryEntry[] = [];
  private initialized = false;
  
  // 4 层记忆系统
  public longTerm?: LongTermMemory;
  public sessionNotes?: SessionNotes;
  public projectContext?: ProjectContext;
  public taskPlanner?: TaskPlanner;

  constructor(config: MemoryConfig) {
    this.config = {
      ...config,
      maxMemories: config.maxMemories || 1000,
      projectRoot: config.projectRoot || process.cwd(),
      sessionId: config.sessionId || `session_${Date.now()}`,
    };
  }

  /**
   * 初始化记忆系统
   */
  async initialize(): Promise<void> {
    if (this.initialized) {
      return;
    }

    const { memoryDir, projectRoot, sessionId } = this.config;

    // 创建记忆目录
    if (!existsSync(memoryDir)) {
      mkdirSync(memoryDir, { recursive: true });
      debug(`Created memory directory: ${memoryDir}`);
    }

    // 加载基础记忆
    await this.loadMemories();
    
    // 初始化 4 层记忆系统
    await this.initializeLayers();
    
    this.initialized = true;
    info(`Memory manager initialized with ${this.memories.length} base memories + 4-layer system`);
  }

  /**
   * 初始化 4 层记忆系统
   */
  private async initializeLayers(): Promise<void> {
    const { memoryDir, projectRoot, sessionId } = this.config;

    // 1. 长期记忆
    const ltmConfig: LongTermMemoryConfig = {
      filePath: join(memoryDir, 'long-term.json'),
      maxEntries: 500,
      minImportance: 5,
    };
    this.longTerm = new LongTermMemory(ltmConfig);
    await this.longTerm.initialize();

    // 2. 会话笔记
    const notesConfig: SessionNotesConfig = {
      maxNotes: 100,
    };
    this.sessionNotes = new SessionNotes(sessionId!, notesConfig);

    // 3. 项目上下文
    const ctxConfig: ProjectContextConfig = {
      projectRoot: projectRoot!,
      contextFile: '.source-deploy-context.json',
    };
    this.projectContext = new ProjectContext(ctxConfig);
    await this.projectContext.initialize();

    // 4. 任务计划
    const plannerConfig: TaskPlannerConfig = {
      filePath: join(memoryDir, 'tasks.json'),
    };
    this.taskPlanner = new TaskPlanner(plannerConfig);
    await this.taskPlanner.initialize();

    info('4-layer memory system initialized');
  }

  /**
   * 加载基础记忆
   */
  private async loadMemories(): Promise<void> {
    const indexPath = join(this.config.memoryDir, 'index.json');
    
    if (!existsSync(indexPath)) {
      this.memories = [];
      return;
    }

    try {
      const content = readFileSync(indexPath, 'utf-8');
      this.memories = JSON.parse(content);
    } catch (err) {
      warn('Failed to load memories:', err);
      this.memories = [];
    }
  }

  /**
   * 保存基础记忆
   */
  private saveMemories(): void {
    const indexPath = join(this.config.memoryDir, 'index.json');
    
    try {
      writeFileSync(indexPath, JSON.stringify(this.memories, null, 2), 'utf-8');
    } catch (err) {
      warn('Failed to save memories:', err);
    }
  }

  // ========== 基础记忆 API（向后兼容）==========

  addMemory(entry: Omit<MemoryEntry, 'id' | 'timestamp'>): MemoryEntry {
    const newEntry: MemoryEntry = {
      ...entry,
      id: `mem_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
      timestamp: Date.now(),
    };

    this.memories.unshift(newEntry);

    if (this.memories.length > this.config.maxMemories!) {
      this.memories = this.memories.slice(0, this.config.maxMemories);
    }

    this.saveMemories();
    debug(`Added base memory: ${newEntry.id}`);

    return newEntry;
  }

  getMemories(options?: {
    type?: MemoryEntry['type'];
    tags?: string[];
    limit?: number;
    query?: string;
  }): MemoryEntry[] {
    let results = [...this.memories];

    if (options?.type) {
      results = results.filter(m => m.type === options.type);
    }

    if (options?.tags && options.tags.length > 0) {
      results = results.filter(m => 
        m.tags?.some(tag => options.tags!.includes(tag))
      );
    }

    if (options?.query) {
      const query = options.query.toLowerCase();
      results = results.filter(m => 
        m.content.toLowerCase().includes(query)
      );
    }

    const limit = options?.limit || 50;
    return results.slice(0, limit);
  }

  deleteMemory(id: string): boolean {
    const index = this.memories.findIndex(m => m.id === id);
    
    if (index === -1) {
      return false;
    }

    this.memories.splice(index, 1);
    this.saveMemories();
    debug(`Deleted base memory: ${id}`);
    
    return true;
  }

  clearMemories(): void {
    this.memories = [];
    this.saveMemories();
    debug('Cleared all base memories');
  }

  exportMemories(): string {
    return this.memories.map(m => 
      `[${m.type.toUpperCase()}] ${new Date(m.timestamp).toISOString()}\n${m.content}`
    ).join('\n\n---\n\n');
  }

  // ========== 4 层记忆系统 API ==========

  /**
   * 添加长期记忆
   */
  addLongTermMemory(content: string, category: 'fact' | 'observation' | 'preference' | 'knowledge' | 'lesson', importance: number, tags: string[] = []): ReturnType<LongTermMemory['add']> {
    if (!this.longTerm) {
      throw new Error('Memory system not initialized');
    }
    return this.longTerm.add({ content, category, importance, tags });
  }

  /**
   * 检索长期记忆
   */
  retrieveLongTermMemories(options?: Parameters<LongTermMemory['retrieve']>[0]): ReturnType<LongTermMemory['retrieve']> {
    if (!this.longTerm) {
      throw new Error('Memory system not initialized');
    }
    return this.longTerm.retrieve(options);
  }

  /**
   * 添加会话笔记
   */
  addSessionNote(content: string, type: 'context' | 'decision' | 'observation' | 'pending'): ReturnType<SessionNotes['add']> {
    if (!this.sessionNotes) {
      throw new Error('Memory system not initialized');
    }
    return this.sessionNotes.add({ content, type });
  }

  /**
   * 获取会话笔记
   */
  getSessionNotes(options?: Parameters<SessionNotes['getNotes']>[0]): ReturnType<SessionNotes['getNotes']> {
    if (!this.sessionNotes) {
      throw new Error('Memory system not initialized');
    }
    return this.sessionNotes.getNotes(options);
  }

  /**
   * 获取项目上下文
   */
  getProjectContext(): ReturnType<ProjectContext['get']> {
    if (!this.projectContext) {
      throw new Error('Memory system not initialized');
    }
    return this.projectContext.get();
  }

  /**
   * 更新项目上下文
   */
  updateProjectContext(data: Partial<ReturnType<ProjectContext['get']>>): void {
    if (!this.projectContext) {
      throw new Error('Memory system not initialized');
    }
    this.projectContext.update(data);
  }

  /**
   * 创建任务
   */
  createTask(title: string, options?: Parameters<TaskPlanner['createTask']>[1]): ReturnType<TaskPlanner['createTask']> {
    if (!this.taskPlanner) {
      throw new Error('Memory system not initialized');
    }
    return this.taskPlanner.createTask(title, options);
  }

  /**
   * 更新任务状态
   */
  updateTaskStatus(taskId: string, status: Parameters<TaskPlanner['updateTaskStatus']>[1]): ReturnType<TaskPlanner['updateTaskStatus']> {
    if (!this.taskPlanner) {
      throw new Error('Memory system not initialized');
    }
    return this.taskPlanner.updateTaskStatus(taskId, status);
  }

  /**
   * 获取所有任务
   */
  getAllTasks(options?: Parameters<TaskPlanner['getAllTasks']>[0]): ReturnType<TaskPlanner['getAllTasks']> {
    if (!this.taskPlanner) {
      throw new Error('Memory system not initialized');
    }
    return this.taskPlanner.getAllTasks(options);
  }

  /**
   * 获取任务进度
   */
  getTaskProgress(): ReturnType<TaskPlanner['getProgress']> {
    if (!this.taskPlanner) {
      throw new Error('Memory system not initialized');
    }
    return this.taskPlanner.getProgress();
  }

  /**
   * 生成完整的系统提示（包含所有记忆层）
   */
  generateSystemPrompt(): string {
    const parts: string[] = ['## Memory Context'];

    // 项目上下文
    if (this.projectContext) {
      const ctx = this.projectContext.toSystemPrompt();
      if (ctx) {
        parts.push(ctx);
      }
    }

    // 任务进度
    if (this.taskPlanner) {
      const progress = this.taskPlanner.getProgress();
      parts.push(`\n**Task Progress:** ${progress.completed}/${progress.total} (${progress.percentComplete}%)`);
      
      const inProgress = this.taskPlanner.getAllTasks({ status: 'in_progress' });
      if (inProgress.length > 0) {
        parts.push('\n**In Progress:**');
        for (const task of inProgress.slice(0, 3)) {
          parts.push(`- ${task.title}`);
        }
      }
    }

    // 最近的会话笔记
    if (this.sessionNotes) {
      const recent = this.sessionNotes.getRecent(5);
      if (recent.length > 0) {
        parts.push('\n**Recent Session Notes:**');
        for (const note of recent) {
          parts.push(`- [${note.type}] ${note.content.slice(0, 100)}...`);
        }
      }
    }

    // 重要的长期记忆
    if (this.longTerm) {
      const important = this.longTerm.retrieve({ minImportance: 7, limit: 5 });
      if (important.length > 0) {
        parts.push('\n**Key Long-term Memories:**');
        for (const mem of important) {
          parts.push(`- [${mem.category}] ${mem.content.slice(0, 100)}...`);
        }
      }
    }

    return parts.join('\n');
  }
}
