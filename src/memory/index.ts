/**
 * 记忆系统导出
 * 
 * 参考自 source/src/memdir/, source/src/state/, source/src/tasks/
 * 
 * 4 层记忆架构：
 * 1. **长期记忆 (Long-term Memory)** - 跨会话持久化
 * 2. **会话笔记 (Session Notes)** - 当前会话临时上下文
 * 3. **项目上下文 (Project Context)** - 项目特定配置
 * 4. **任务计划 (Task Plans)** - 待办事项和进度追踪
 */

export { MemoryManager, type MemoryConfig, type MemoryEntry } from './MemoryManager.js';
export { LongTermMemory, type LongTermMemoryConfig, type LongTermMemoryEntry } from './LongTermMemory.js';
export { SessionNotes, type SessionNotesConfig, type SessionNote } from './SessionNotes.js';
export { ProjectContext, type ProjectContextConfig, type ProjectContextData } from './ProjectContext.js';
export { TaskPlanner, type TaskPlannerConfig, type Task, type TaskPlan } from './TaskPlanner.js';
