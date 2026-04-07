# Source-Deploy 集成指南

## 概述

本文档记录了将 `claude-code-learning` 项目中的完整系统集成到 `source-deploy` 的过程。

### 集成目标

将原始源码的三大核心系统迁移到 source-deploy：
1. ✅ **工具系统** - 从 5 个工具扩展到 12 个工具
2. ✅ **记忆系统** - 实现 4 层记忆架构
3. ⏳ **Agent 系统** -  deferred to future iteration（复杂度较高）

---

## 一、工具系统集成

### 1.1 原始 vs 简化版对比

| 类别 | 原始源码 (45+ 工具) | Source-Deploy (12 工具) | 状态 |
|------|---------------------|------------------------|------|
| **文件操作** | FileRead, FileWrite, FileEdit, FileDelete, DirectoryCreate, FileMove, NotebookEdit... | ✅ FileRead, FileWrite, FileEdit, FileDelete, DirectoryCreate | 核心功能已实现 |
| **搜索** | Grep, Glob, ToolSearch | ✅ Grep, Glob | 已实现 |
| **执行** | Bash, PowerShell, REPL | ✅ Bash | 核心已实现 |
| **版本控制** | GitDiff, GitCommit, GitPush... | ✅ GitDiff | 核心已实现 |
| **任务管理** | TodoWrite, TaskCreate, TaskGet, TaskUpdate, TaskList... | ✅ TodoWrite | 简化版已实现 |
| **网络** | WebSearch, WebFetch, HttpGet, HttpPost... | ✅ WebSearch | 核心已实现 |
| **交互** | AskUserQuestion, SendMessage | ✅ AskUser | 已实现 |
| **MCP** | MCPTool, ListMcpResources, ReadMcpResource | ⬜ 已有 McpClient | 独立模块 |
| **Agent** | AgentTool, TeamCreate, TeamDelete | ⏳ 未实现 | 待后续 |
| **高级** | LSP, Tungsten, Workflow, SkillTool... | ⬜ 未实现 | 冷门功能暂缓 |

### 1.2 新增工具详情

#### FileWriteTool (`file_write`)
- **功能**: 创建或覆盖文件
- **输入**: `file_path` (string), `content` (string)
- **输出**: 操作类型 (create/update), 文件路径，原始内容
- **特性**: 
  - 自动创建父目录
  - 安全检查（UNC 路径阻止）
  - 返回 diff 信息

#### FileDeleteTool (`file_delete`)
- **功能**: 删除单个文件
- **输入**: `file_path` (string)
- **输出**: 成功/失败消息
- **特性**: 
  - 防止删除目录
  - 存在性检查

#### DirectoryCreateTool (`directory_create`)
- **功能**: 创建目录（包括父目录）
- **输入**: `path` (string)
- **输出**: 成功/失败消息
- **特性**: 递归创建

#### GitDiffTool (`git_diff`)
- **功能**: 获取 Git 差异
- **输入**: `file_path` (optional), `staged` (boolean), `commit_range` (string)
- **输出**: Diff 输出，解析后的 hunks
- **特性**: 
  - 支持暂存区/工作区
  - 支持 commit 范围
  - 自动解析 unified diff 格式

#### TodoWriteTool (`todo_write`)
- **功能**: 任务列表管理
- **输入**: `todos` (array), `operation` (set/add/update/delete)
- **输出**: 受影响的任务，完整任务列表
- **特性**: 
  - 支持优先级 (low/medium/high)
  - 支持状态 (pending/in_progress/completed)
  - 内存存储（后续可持久化）

#### WebSearchTool (`web_search`)
- **功能**: 网络搜索
- **输入**: `query` (string), `count` (number), `freshness` (day/week/month/year)
- **输出**: 搜索结果（标题、URL、摘要）
- **依赖**: `BRAVE_SEARCH_API_KEY` 环境变量

#### AskUserTool (`ask_user`)
- **功能**: 向用户提问
- **输入**: `question` (string), `allow_multiple` (boolean)
- **输出**: 问题状态（awaiting_response）
- **注意**: 实际交互由上层应用处理

### 1.3 工具抽象对比

**原始源码 (Tool.ts - 30KB)**:
```typescript
// 复杂的权限上下文、进度追踪、JSX 渲染等
export type ToolUseContext = {
  options: { ... }
  abortController: AbortController
  readFileState: FileStateCache
  getAppState(): AppState
  setAppState(f: (prev: AppState) => AppState): void
  // ... 50+ 个字段
}

export interface ToolDef<Input, Output> {
  name: string
  description: string
  inputSchema: z.ZodType
  outputSchema?: z.ZodType
  prompt(): Promise<string>
  validateInput(input, context): ValidationResult
  checkPermissions(input, context): PermissionDecision
  call(input, context, signal, parentMessage): Promise<ToolResult>
  renderToolUseMessage(...): React.ReactNode
  // ... 20+ 个方法
}
```

**Source-Deploy (Tool.ts - 简化版)**:
```typescript
export interface ToolDefinition<T> {
  name: string;
  description: string;
  inputSchema: T;
  execute: (input: z.infer<T>) => Promise<ToolResult>;
}

export abstract class BaseTool<T> {
  abstract readonly name: string;
  abstract readonly description: string;
  abstract readonly inputSchema: T;
  abstract execute(input: z.infer<T>): Promise<ToolResult>;
  validateInput(input: unknown): z.infer<T> | null;
  getDefinition(): ToolDefinition<T>;
}
```

**设计决策**:
- ✅ 移除 React/JSX 依赖（纯 CLI 环境）
- ✅ 简化权限检查（基于文件系统）
- ✅ 移除进度追踪（由 QueryEngine 统一管理）
- ✅ 保持 Zod Schema 验证（类型安全）

---

## 二、记忆系统集成

### 2.1 4 层记忆架构

```
┌─────────────────────────────────────────┐
│         MemoryManager (统一入口)         │
├─────────────────────────────────────────┤
│  ┌─────────────────────────────────┐   │
│  │ 1. LongTermMemory (长期记忆)     │   │
│  │    - 跨会话持久化                │   │
│  │    - 重要性评分 (1-10)           │   │
│  │    - 分类：fact/observation/etc  │   │
│  │    - 文件：memory/long-term.json │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │ 2. SessionNotes (会话笔记)       │   │
│  │    - 当前会话临时上下文          │   │
│  │    - 会话结束自动清理            │   │
│  │    - 类型：context/decision/etc  │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │ 3. ProjectContext (项目上下文)   │   │
│  │    - 项目特定配置                │   │
│  │    - 自动发现 (package.json)     │   │
│  │    - 文件：.source-deploy-context│   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │ 4. TaskPlanner (任务计划)        │   │
│  │    - 待办事项管理                │   │
│  │    - 任务依赖关系                │   │
│  │    - 进度追踪                    │   │
│  │    - 文件：memory/tasks.json     │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### 2.2 原始 vs 简化版对比

| 功能 | 原始源码 | Source-Deploy | 状态 |
|------|----------|---------------|------|
| **持久化存储** | memdir/ 复杂结构 | ✅ memory/*.json | 已实现 |
| **会话状态** | state/AppState | ✅ SessionNotes | 已实现 |
| **项目配置** | context.ts + CLAUDE.md | ✅ ProjectContext | 已实现 + 自动发现 |
| **任务管理** | tasks/Task.ts (复杂) | ✅ TaskPlanner (简化) | 核心已实现 |
| **记忆压缩** | 自动总结/合并 | ⬜ 未实现 | 待后续 |
| **语义搜索** | RAG/嵌入 | ⬜ 未实现 | 待后续 |
| **OpenClaw 对接** | - | ✅ 兼容设计 | 预留接口 |

### 2.3 使用示例

```typescript
import { MemoryManager } from './memory/index.js';

// 初始化
const memory = new MemoryManager({
  memoryDir: '.source-deploy-memory',
  projectRoot: process.cwd(),
  sessionId: 'session_123',
});
await memory.initialize();

// 1. 添加长期记忆
memory.addLongTermMemory(
  '用户偏好使用 TypeScript 进行开发',
  'preference',
  8, // 重要性 8/10
  ['typescript', 'preference']
);

// 2. 添加会话笔记
memory.addSessionNote(
  '正在调试 API 连接问题',
  'context'
);

// 3. 更新项目上下文
memory.updateProjectContext({
  name: 'my-project',
  languages: ['typescript', 'nodejs'],
  buildCommand: 'npm run build',
});

// 4. 创建任务
const task = memory.createTask('修复登录 bug', {
  priority: 'high',
  description: '用户报告无法登录',
  tags: ['bug', 'urgent'],
});
memory.updateTaskStatus(task.id, 'in_progress');

// 5. 检索记忆
const importantMemories = memory.retrieveLongTermMemories({
  minImportance: 7,
  limit: 10,
});

// 6. 生成系统提示（包含所有记忆层）
const prompt = memory.generateSystemPrompt();
```

---

## 三、Agent 系统（deferred）

### 3.1 原始源码分析

原始 Agent 系统包含以下复杂功能：
- **子代理管理**: `spawnMultiAgent.ts` (35KB)
- **多代理协作**: Writer/Reviewer 模式、Fan-out 模式
- **Agent 配置**: `.claude/agents/*.md` 解析
- **通信协议**: Agent 间消息传递
- **进度追踪**: 实时状态更新
- **TMUX/分屏集成**: 终端 UI 管理

### 3.2 为何暂缓

1. **复杂度高**: 涉及大量 React/UI 代码，不适合纯 CLI 环境
2. **依赖重**: 需要 TMUX、分屏管理等终端能力
3. **优先级低**: 工具和记忆系统是基础，Agent 是高级功能
4. **可替代方案**: OpenClaw 已有 subagent 机制

### 3.3 未来实现方案

```
source-deploy/src/agents/
├── AgentManager.ts       # Agent 管理器
├── BaseAgent.ts          # Agent 基类
├── SubAgent.ts           # 子代理实现
├── config.ts             # Agent 配置解析
└── index.ts              # 统一导出
```

**简化设计**:
- 通过 OpenClaw `sessions_spawn` 创建子代理
- 使用文件系统进行 Agent 间通信
- 支持简单的 Fan-out 模式（并行执行多个任务）

---

## 四、与 OpenClaw 的对接

### 4.1 记忆系统兼容

Source-Deploy 的记忆系统设计时考虑了与 OpenClaw 的兼容：

```typescript
// OpenClaw 记忆文件位置
~/.openclaw/workspace-<agent>/memory/YYYY-MM-DD.md
~/.openclaw/workspace-<agent>/MEMORY.md

// Source-Deploy 记忆文件位置
<source-deploy-root>/.source-deploy-memory/long-term.json
<source-deploy-root>/.source-deploy-memory/tasks.json
```

**对接点**:
1. **双向同步**: 可将重要记忆同步到 OpenClaw MEMORY.md
2. **共享项目上下文**: 读取 OpenClaw 的 PROJECT_CONTEXT.md
3. **任务互通**: OpenClaw TaskPlanner ↔ Source-Deploy TaskPlanner

### 4.2 工具系统扩展

可通过以下方式扩展工具：

```typescript
// 方式 1: 直接注册新工具
registry.register(new MyCustomTool());

// 方式 2: 使用 OpenClaw Skills
// （需要实现 Skill 适配器）

// 方式 3: MCP 工具
// 通过 McpClient 连接外部 MCP 服务器
```

---

## 五、测试与验证

### 5.1 工具测试

```bash
cd /Users/dhr/.openclaw/workspace-claude-code-agent/source-deploy

# 测试 FileWrite
echo '{"tool": "file_write", "input": {"file_path": "/tmp/test.txt", "content": "Hello"}}' | bun run src/index.ts --prompt "test"

# 测试 GitDiff（在 git 仓库中）
bun run src/index.ts --prompt "显示最近的 git 变更"

# 测试 TodoWrite
bun run src/index.ts --prompt "创建一个任务列表：1. 学习 TypeScript 2. 构建项目"
```

### 5.2 记忆系统测试

```typescript
// tests/memory.test.ts
import { MemoryManager } from '../src/memory/index.js';

describe('MemoryManager', () => {
  it('should initialize 4-layer system', async () => {
    const memory = new MemoryManager({ memoryDir: '/tmp/test-memory' });
    await memory.initialize();
    
    expect(memory.longTerm).toBeDefined();
    expect(memory.sessionNotes).toBeDefined();
    expect(memory.projectContext).toBeDefined();
    expect(memory.taskPlanner).toBeDefined();
  });

  it('should add and retrieve long-term memory', async () => {
    const memory = new MemoryManager({ memoryDir: '/tmp/test-memory' });
    await memory.initialize();
    
    const entry = memory.addLongTermMemory('Test fact', 'fact', 7, ['test']);
    expect(entry.id).toBeDefined();
    
    const retrieved = memory.retrieveLongTermMemories({ query: 'Test' });
    expect(retrieved.length).toBeGreaterThan(0);
  });
});
```

---

## 六、后续优化建议

### 高优先级
1. **工具持久化**: TodoWrite 任务保存到文件（当前是内存存储）
2. **WebSearch 降级**: 无 API key 时使用 web_search 技能
3. **Git 工具增强**: 添加 GitCommit, GitLog, GitStatus

### 中优先级
4. **记忆压缩**: 定期总结长期记忆（使用 LLM）
5. **语义搜索**: 集成 Ollama 嵌入模型
6. **Agent 系统 MVP**: 最简单的 Fan-out 模式

### 低优先级
7. **MCP 工具桥接**: 通过 MCP 连接更多外部工具
8. **LSP 集成**: 代码分析和智能提示
9. **Skill 系统**: 自定义技能封装

---

## 七、文件清单

### 新增文件
```
source-deploy/src/tools/
├── FileWrite.ts          ✅ 新增
├── FileDelete.ts         ✅ 新增
├── DirectoryCreate.ts    ✅ 新增
├── GitDiff.ts            ✅ 新增
├── TodoWrite.ts          ✅ 新增
├── WebSearch.ts          ✅ 新增
├── AskUser.ts            ✅ 新增
└── index.ts              ✅ 新增（统一导出）

source-deploy/src/memory/
├── LongTermMemory.ts     ✅ 新增
├── SessionNotes.ts       ✅ 新增
├── ProjectContext.ts     ✅ 新增
├── TaskPlanner.ts        ✅ 新增
├── MemoryManager.ts      ✏️ 增强（4 层架构）
└── index.ts              ✅ 新增（统一导出）

source-deploy/
├── INTEGRATION_GUIDE.md  ✅ 本文档
└── IMPLEMENTATION_LOG.md ✏️ 更新
```

### 修改文件
```
source-deploy/src/index.ts  ✏️ 更新（注册新工具，更新系统提示）
```

---

## 八、总结

### 完成情况
- ✅ **工具系统**: 从 5 个扩展到 12 个（+140%）
- ✅ **记忆系统**: 实现完整的 4 层架构
- ⏳ **Agent 系统**: 已分析，暂缓实现

### 代码统计
- 新增工具代码：~2.5KB × 7 = ~17.5KB
- 新增记忆代码：~4KB + ~3KB + ~6KB + ~9KB = ~22KB
- 总计新增：~40KB 源代码

### 与原始源码的差异
| 维度 | 原始源码 | Source-Deploy | 压缩率 |
|------|----------|---------------|--------|
| 工具系统 | 45+ 工具，~100KB | 12 工具，~18KB | 82% ↓ |
| 记忆系统 | 分散多处，~50KB | 集中 4 层，~22KB | 56% ↓ |
| Agent 系统 | 完整实现，~200KB | 未实现 | 100% ↓ |
| **总计** | **~350KB** | **~40KB** | **88% ↓** |

### 设计原则
1. **简洁优先**: 只实现核心功能，避免过度工程
2. **CLI 友好**: 移除 React/UI 依赖，纯终端环境
3. **类型安全**: 保持 Zod Schema 验证
4. **向后兼容**: 保留原有 API，渐进式增强
5. **OpenClaw 兼容**: 预留对接接口

---

*最后更新：2026-04-06*
