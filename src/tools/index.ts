/**
 * 工具系统导出
 * 
 * 参考自 source/src/tools.ts (17KB)
 * 原始实现包含 45+ 个工具，这里是核心子集
 * 
 * 工具类别：
 * 1. 文件操作 - FileRead, FileWrite, FileEdit, FileDelete, DirectoryCreate
 * 2. 搜索工具 - Grep, Glob
 * 3. 执行工具 - Bash
 * 4. 版本控制 - GitDiff
 * 5. 任务管理 - TodoWrite
 * 6. 网络工具 - WebSearch
 * 7. 交互工具 - AskUser
 */

// 核心工具（已有）
export { BashTool } from './BashTool.js';
export { FileReadTool } from './FileRead.js';
export { FileEditTool } from './FileEdit.js';
export { GrepTool } from './Grep.js';
export { GlobTool } from './Glob.js';

// 新增工具
export { FileWriteTool } from './FileWrite.js';
export { FileDeleteTool } from './FileDelete.js';
export { DirectoryCreateTool } from './DirectoryCreate.js';
export { WebFetchTool } from './WebFetch.js';
export { TaskCreateTool } from './TaskCreate.js';
export { TaskUpdateTool } from './TaskUpdate.js';
export { TaskGetTool } from './TaskGet.js';
export { TaskListTool } from './TaskList.js';
export { TaskStopTool } from './TaskStop.js';
export { TaskOutputTool } from './TaskOutput.js';
export { TaskCompleteTool } from './TaskComplete.js';
export { TaskDeleteTool } from './TaskDelete.js';
export { SendMessageTool } from './SendMessage.js';
export { BriefTool } from './Brief.js';
export { SkillTool } from './Skill.js';
export { AgentTool } from './Agent.js';
// AskUserQuestionTool 已合并到 AskUserTool
export { ReadMcpResourceTool } from './ReadMcpResource.js';
export { LSPTool } from './LSP.js';
export { ListMcpResourcesTool } from './ListMcpResources.js';
export { MCPTool } from './MCPTool.js';
export { WorktreeTool } from './WorktreeTool.js';
export { GitDiffTool } from './GitDiff.js';
export { TodoWriteTool } from './TodoWrite.js';
export { WebSearchTool } from './WebSearch.js';
export { AskUserTool } from './AskUser.js';
export { ProjectSummaryTool } from './ProjectSummary.js';
export { SessionSaveTool } from './SessionSave.js';
export { SessionLoadTool } from './SessionLoad.js';

// 工具元数据
export const TOOL_CATEGORIES = {
  FILE_OPERATIONS: ['file_read', 'file_write', 'file_edit', 'file_delete', 'directory_create'],
  SEARCH: ['grep', 'glob'],
  EXECUTION: ['bash'],
  VERSION_CONTROL: ['git_diff', 'worktree'],
  TASK_MANAGEMENT: ['todo_write', 'task_create', 'task_update', 'task_get', 'task_list', 'task_stop', 'task_output', 'task_complete', 'task_delete'],
  WEB: ['web_search', 'web_fetch'],
  INTERACTION: ['ask_user', 'ask_user_question', 'send_message'],
  MCP: ['list_mcp_resources', 'mcp', 'read_mcp_resource'],
  CODE_INTELLIGENCE: ['lsp'],
  BRIEF: ['brief'],
  SKILL: ['skill'],
  AGENT: ['agent'],
} as const;

export const ALL_TOOLS = [
  'bash',
  'file_read',
  'file_write',
  'file_edit',
  'file_delete',
  'directory_create',
  'grep',
  'glob',
  'git_diff',
  'worktree',
  'todo_write',
  'task_create',
  'task_update',
  'task_get',
  'task_list',
  'task_stop',
  'task_output',
  'task_complete',
  'task_delete',
  'web_search',
  'web_fetch',
  'ask_user',
  'ask_user_question',
  'send_message',
  'brief',
  'skill',
  'agent',
  'list_mcp_resources',
  'mcp',
  'read_mcp_resource',
  'lsp',
  'project_summary',
] as const;

export type ToolName = typeof ALL_TOOLS[number];
export { FileCacheTool } from './FileCache.js';
