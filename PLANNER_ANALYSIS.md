# 🔍 Planner 分析报告

**分析时间**: 2026-04-06 18:27  
**分析对象**: claude-code-learning source/src 源码

---

## 📊 源码结构概览

| 目录 | 文件数 | 说明 |
|------|--------|------|
| `tools/` | 43 个 | 完整工具集 |
| `components/` | 146 个 | UI 组件 (Ink/React) |
| `hooks/` | 87 个 | React Hooks |
| `utils/` | 331 个 | 工具函数 |
| `memdir/` | 10 个 | 记忆系统核心 |
| `coordinator/` | 1 个 | Agent 协调器 |
| `commands/` | 103 个 | 命令处理 |
| `services/` | 38 个 | 服务层 |

**核心文件**:
- `main.tsx` (804KB) - 入口
- `query.ts` (69KB) - 查询编排
- `QueryEngine.ts` (47KB) - 引擎核心
- `Tool.ts` (30KB) - 工具抽象
- `tools.ts` (17KB) - 工具注册表

---

## 🛠️ 工具系统分析

### 43 个工具分类

| 类别 | 工具 | 优先级 |
|------|------|--------|
| **基础操作** (5 个) | Bash, FileRead, FileEdit, Grep, Glob | ✅ 已有 |
| **文件扩展** (4 个) | FileWrite, FileDelete, NotebookEdit, PowerShell | 🔴 高 |
| **任务管理** (6 个) | TaskCreate, TaskGet, TaskList, TaskOutput, TaskStop, TaskUpdate | 🟡 中 |
| **团队协作** (4 个) | TeamCreate, TeamDelete, SendMessage, TodoWrite | 🟢 低 |
| **MCP 集成** (4 个) | MCPTool, ListMcpResources, ReadMcpResource, McpAuth | 🔴 高 |
| **Agent 系统** (3 个) | AgentTool, AskUserQuestion, SkillTool | 🟡 中 |
| **网络相关** (3 个) | WebFetch, WebSearch, RemoteTrigger | 🟢 低 |
| **开发工具** (5 个) | LSP, REPL, Config, Brief, ToolSearch | 🟢 低 |
| **计划模式** (4 个) | EnterPlanMode, ExitPlanMode, EnterWorktree, ExitWorktree | 🟢 低 |
| **其他** (5 个) | Sleep, ScheduleCron, SyntheticOutput, TaskCreate, TaskGet | 🟢 低 |

### 工具抽象设计

```typescript
// Tool.ts 核心接口
export interface BaseTool {
  name: string;
  description: string;
  input_schema: ToolInputJSONSchema;
  execute(input: unknown): Promise<ToolResult>;
}

// 工具结果类型
export interface ToolResult {
  content: string;
  isError?: boolean;
  system?: ToolResultSystemContent;
}
```

---

## 🧠 记忆系统分析

### 4 层记忆架构 (`memdir/memoryTypes.ts`)

```typescript
export const MEMORY_TYPES = [
  'user',       // 用户角色、偏好、知识
  'feedback',   // 工作流程指导（避免/确认）
  'project',    // 项目状态、目标、决策
  'reference',  // 外部资源位置
] as const
```

### 各层详细说明

| 类型 | 作用域 | 保存时机 | 示例 |
|------|--------|----------|------|
| **user** | 始终 private | 了解用户角色、偏好时 | "用户是数据科学家，偏好简洁回复" |
| **feedback** | 默认 private | 用户纠正或确认方法时 | "测试不要 mock 数据库，去年吃过亏" |
| **project** | 偏向 team | 了解项目目标、截止日期 | "移动版本发布前冻结合并" |
| **reference** | 通常 team | 发现外部资源位置 | "Pipeline bug  tracked in Linear 'INGEST'" |

### 核心文件

| 文件 | 大小 | 功能 |
|------|------|------|
| `memoryTypes.ts` | 23KB | 记忆类型定义和保存规则 |
| `memdir.ts` | 21KB | 记忆目录管理和存储 |
| `paths.ts` | 11KB | 记忆文件路径计算 |
| `teamMemPaths.ts` | 12KB | 团队成员记忆路径 |
| `findRelevantMemories.ts` | 5KB | 相关记忆检索 |

---

## 🤖 Agent 系统分析

### Coordinator 模式 (`coordinator/coordinatorMode.ts`)

**核心概念**:
- **Coordinator Agent** - 主代理，负责任务分解和分配
- **Worker Agents** - 工作代理，执行具体任务
- **SendMessage Tool** - Agent 间通信

**关键特性**:
```typescript
// Coordinator 模式下 Worker 可用工具
const ASYNC_AGENT_ALLOWED_TOOLS = new Set([
  'bash', 'file_read', 'file_edit', 'grep', 'glob',
  // ... 其他基础工具
])

// 内部工具（不暴露给 Worker）
const INTERNAL_WORKER_TOOLS = new Set([
  'team_create', 'team_delete', 'send_message',
  'synthetic_output'
])
```

### Agent 工具 (`tools/AgentTool/`)

**功能**:
- 创建和管理子代理
- 任务分配和进度追踪
- 结果收集和合并

---

## 📋 集成优先级和建议

### 阶段 1: 工具系统扩展 (2 小时) 🔴

**优先添加的工具** (从 5 个 → 15 个):
1. ✅ **FileWrite** - 文件写入（高频使用）
2. ✅ **MCPTool** - MCP 协议支持（核心扩展能力）
3. ✅ **ListMcpResources** - 列出 MCP 资源
4. ⬜ **TaskCreate/TaskList** - 任务管理基础
5. ⬜ **LSP** - 代码智能提示

**实施策略**:
- 提取原始工具的 `execute()` 逻辑
- 简化权限检查和 UI 反馈
- 适配 Qwen Provider 的 function_call 格式

### 阶段 2: 记忆系统增强 (1 小时) 🟡

**当前状态**: 简化的 MemoryManager（文件存储）

**目标架构**:
```
source-deploy/src/memory/
├── MemoryManager.ts      # 现有，保持不变
├── types.ts              # ⬜ 新增：4 种记忆类型定义
├── paths.ts              # ⬜ 新增：路径计算
├── user.ts               # ⬜ 新增：用户记忆管理
├── feedback.ts           # ⬜ 新增：反馈记忆管理
├── project.ts            # ⬜ 新增：项目记忆管理
└── reference.ts          # ⬜ 新增：参考记忆管理
```

**实施策略**:
- 直接复用 `memoryTypes.ts` 的类型定义（非常完善）
- 简化存储逻辑，使用现有文件结构
- 保持与 OpenClaw MEMORY.md 的兼容

### 阶段 3: Agent 系统 (1 小时) 🟢

**最小可行实现**:
```
source-deploy/src/agents/
├── BaseAgent.ts          # ⬜ Agent 基类
├── SubAgent.ts           # ⬜ 子代理实现
├── AgentManager.ts       # ⬜ Agent 管理器
└── config.ts             # ⬜ .claude/agents/*.md解析
```

**核心功能**:
- 从配置文件加载 Agent 定义
- 使用 `subagent` API 创建子代理
- 简单的任务分配和结果收集

**简化点**:
- 不支持复杂的团队管理
- 不使用 Coordinator 模式（太复杂）
- 基于现有的 `sessions_spawn` 实现

---

## ⚠️ 风险和挑战

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 工具依赖复杂 | 高 | 只提取核心逻辑，跳过权限/缓存等高级功能 |
| 记忆系统冲突 | 中 | 保持与 OpenClaw 记忆系统的接口兼容 |
| Agent 系统过于复杂 | 中 | 先实现最简版本，后续迭代 |
| 代码量过大 | 中 | 分阶段实施，每阶段验证后再继续 |

---

## 📅 实施时间表

| 阶段 | 任务 | 预计时间 | 产出 |
|------|------|----------|------|
| 1 | 工具系统扩展 (5→15 个) | 2h | +10 个工具文件 |
| 2 | 记忆系统 4 层实现 | 1h | 6 个记忆模块 |
| 3 | Agent 系统基础版 | 1h | 4 个 Agent 模块 |
| 4 | 集成测试 | 30min | 测试用例 |
| 5 | 文档更新 | 30min | TOOLS.md, AGENTS.md |

**总计**: ~5 小时

---

## ✅ 下一步行动

1. **Executor 开始阶段 1** - 提取并适配 10 个核心工具
2. 每个工具完成后由 Reviewer 审查
3. 阶段 1 完成后进入阶段 2（记忆系统）
4. 最后实现阶段 3（Agent 系统）

---

_Plan approved by: Harness Agent_  
_Next: Executor 开始实施_
