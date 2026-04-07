# Claude Code 源码改造日志

> 📝 记录从 claude-code-learning 源码到 source-deploy 简化版的改造过程

---

## 📅 2026-04-06 - 集成 source-deploy 与原始源码三大系统

### 任务背景

用户要求将新部署的 `source-deploy` 项目与 `claude-code-learning` 项目中 `source/src` 下的完整系统进行集成：
1. **Agent 系统** - 多代理协作、子代理管理
2. **工具系统** - 45 个完整工具（当前简化版只有 5 个）
3. **记忆系统** - 4 层记忆（长期记忆、会话笔记、项目上下文、任务计划）

### 执行步骤

#### 阶段 1: 分析原始源码结构 ✅

**分析结果**:
- `source/src/tools/` - 45 个工具实现
- `source/src/Tool.ts` (30KB) - 工具抽象基类
- `source/src/tools.ts` (17KB) - 工具注册表
- `source/src/memdir/` - 记忆目录
- `source/src/components/memory/` - 记忆 UI 组件
- `source/src/components/agents/` - Agent 系统 UI
- `source/src/tools/shared/spawnMultiAgent.ts` (35KB) - 多代理生成

**关键文件**:
- `main.tsx` (804KB) - 入口文件
- `query.ts` (69KB) - 查询编排
- `QueryEngine.ts` (47KB) - 引擎核心
- `Tool.ts` (30KB) - 工具抽象
- `tools.ts` (17KB) - 工具注册表

#### 阶段 2: 工具系统扩展 ✅

**目标**: 从 5 个工具扩展到核心子集（12 个工具）

**新增工具**:
1. ✅ `FileWrite.ts` - 创建/覆盖文件
2. ✅ `FileDelete.ts` - 删除文件
3. ✅ `DirectoryCreate.ts` - 创建目录
4. ✅ `GitDiff.ts` - Git 差异查看
5. ✅ `TodoWrite.ts` - 任务列表管理
6. ✅ `WebSearch.ts` - 网络搜索
7. ✅ `AskUser.ts` - 向用户提问

**工具分类**:
```
文件操作 (5): file_read, file_write, file_edit, file_delete, directory_create
搜索 (2): grep, glob
执行 (1): bash
版本控制 (1): git_diff
任务管理 (1): todo_write
网络 (1): web_search
交互 (1): ask_user
总计：12 个工具
```

**代码统计**:
- 每个工具约 2-5KB
- 新增工具代码总计约 18KB
- 原始源码工具系统约 100KB
- **压缩率：82%**

#### 阶段 3: 记忆系统增强 ✅

**目标**: 实现 4 层记忆架构

**新增模块**:
1. ✅ `LongTermMemory.ts` (4.4KB) - 长期记忆
   - 跨会话持久化
   - 重要性评分 (1-10)
   - 分类：fact/observation/preference/knowledge/lesson
   
2. ✅ `SessionNotes.ts` (2.8KB) - 会话笔记
   - 当前会话临时上下文
   - 会话结束自动清理
   - 类型：context/decision/observation/pending
   
3. ✅ `ProjectContext.ts` (5.8KB) - 项目上下文
   - 项目特定配置
   - 自动发现 (package.json)
   - 技术栈检测
   
4. ✅ `TaskPlanner.ts` (9.4KB) - 任务计划
   - 待办事项管理
   - 任务依赖关系
   - 进度追踪
   - 父子任务层次

**增强 MemoryManager**:
- 整合 4 层记忆系统
- 提供统一 API
- 生成包含所有记忆层的系统提示

**代码统计**:
- 新增记忆代码约 22KB
- 原始源码记忆系统约 50KB
- **压缩率：56%**

#### 阶段 4: Agent 系统 ⏳

**分析结果**:
原始 Agent 系统非常复杂：
- `AgentTool.tsx` (233KB) - Agent 工具主实现
- `spawnMultiAgent.ts` (35KB) - 多代理生成
- `runAgent.ts` (35KB) - Agent 运行逻辑
- `agentMemory.ts` (6KB) - Agent 记忆
- `forkSubagent.ts` (9KB) - Agent 分叉
- 大量 React/UI 代码

**决定暂缓原因**:
1. 复杂度高（涉及 TMUX、分屏管理等终端 UI）
2. 依赖重（需要大量 React 组件）
3. 优先级低（工具和记忆是基础）
4. OpenClaw 已有 subagent 机制可替代

**未来计划**:
```
source-deploy/src/agents/
├── AgentManager.ts   # Agent 管理器
├── BaseAgent.ts      # Agent 基类
├── SubAgent.ts       # 子代理实现
└── config.ts         # Agent 配置解析
```

#### 阶段 5: 测试验证 ✅

**创建集成测试**: `tests/integration.test.ts`

**测试覆盖**:
- Tool System Integration (10 tests)
  - FileWriteTool: create, update, nested directories
  - FileDeleteTool: delete, error handling
  - DirectoryCreateTool: create, nested, exists
  - TodoWriteTool: add, update status
  
- Memory System Integration (7 tests)
  - 4-layer initialization
  - Long-term memory CRUD
  - Session notes CRUD
  - Project context auto-discovery
  - Task planner CRUD
  - System prompt generation
  - Persistence and reload

- Tool Registry Integration (2 tests)
  - Register all tools
  - Get tool by name

**测试结果**:
```
✅ 20 pass
✅ 0 fail
✅ 52 expect() calls
```

#### 阶段 6: 文档编写 ✅

**创建文档**:
1. ✅ `INTEGRATION_GUIDE.md` (11KB) - 完整集成指南
   - 工具系统对比
   - 记忆系统架构
   - Agent 系统分析
   - 使用示例
   - 后续优化建议

2. ✅ 更新 `IMPLEMENTATION_LOG.md` - 本日志

---

### 成果总结

#### 代码统计

| 系统 | 原始源码 | Source-Deploy | 压缩率 | 状态 |
|------|----------|---------------|--------|------|
| 工具系统 | ~100KB (45+ 工具) | ~18KB (12 工具) | 82% ↓ | ✅ 完成 |
| 记忆系统 | ~50KB | ~22KB | 56% ↓ | ✅ 完成 |
| Agent 系统 | ~200KB | 0KB | 100% ↓ | ⏳ 暂缓 |
| **总计** | **~350KB** | **~40KB** | **88% ↓** | - |

#### 新增文件清单

```
source-deploy/src/tools/
├── FileWrite.ts          ✅ 新增 (3.1KB)
├── FileDelete.ts         ✅ 新增 (2.2KB)
├── DirectoryCreate.ts    ✅ 新增 (2.1KB)
├── GitDiff.ts            ✅ 新增 (4.5KB)
├── TodoWrite.ts          ✅ 新增 (5.0KB)
├── WebSearch.ts          ✅ 新增 (3.3KB)
├── AskUser.ts            ✅ 新增 (1.9KB)
└── index.ts              ✅ 新增 (1.5KB)

source-deploy/src/memory/
├── LongTermMemory.ts     ✅ 新增 (4.4KB)
├── SessionNotes.ts       ✅ 新增 (2.8KB)
├── ProjectContext.ts     ✅ 新增 (5.8KB)
├── TaskPlanner.ts        ✅ 新增 (9.4KB)
├── MemoryManager.ts      ✏️ 增强 (+8KB)
└── index.ts              ✅ 新增 (0.8KB)

source-deploy/
├── INTEGRATION_GUIDE.md  ✅ 新增 (11KB)
└── tests/integration.test.ts ✅ 新增 (11KB)
```

#### 修改文件

```
source-deploy/src/index.ts  ✏️ 更新
- 导入新工具（12 个）
- 更新工具注册逻辑
- 更新系统提示
```

---

### 设计原则

1. **简洁优先**: 只实现核心功能，避免过度工程
2. **CLI 友好**: 移除 React/UI 依赖，纯终端环境
3. **类型安全**: 保持 Zod Schema 验证
4. **向后兼容**: 保留原有 API，渐进式增强
5. **OpenClaw 兼容**: 预留对接接口

---

### 后续优化建议

#### 高优先级
1. ⬜ **工具持久化**: TodoWrite 任务保存到文件（当前内存存储）
2. ⬜ **WebSearch 降级**: 无 API key 时使用 web_search 技能
3. ⬜ **Git 工具增强**: 添加 GitCommit, GitLog, GitStatus

#### 中优先级
4. ⬜ **记忆压缩**: 定期总结长期记忆（使用 LLM）
5. ⬜ **语义搜索**: 集成 Ollama 嵌入模型
6. ⬜ **Agent 系统 MVP**: 最简单的 Fan-out 模式

#### 低优先级
7. ⬜ **MCP 工具桥接**: 通过 MCP 连接更多外部工具
8. ⬜ **LSP 集成**: 代码分析和智能提示
9. ⬜ **Skill 系统**: 自定义技能封装

---

## 📅 2026-04-06 - 项目初始化

### 阶段 1: 源码分析

#### 任务
- [x] 克隆 claude-code-learning 仓库
- [x] 分析 source/src 目录结构
- [x] 统计文件数量和类型
- [x] 查看入口文件和核心依赖

#### 发现

**项目规模**:
```
source/src/
├── 1884 个 TypeScript 文件
├── main.tsx (804KB) - 入口文件
├── QueryEngine.ts (47KB) - 查询引擎
├── Tool.ts (30KB) - 工具抽象
├── tools/ (45 个工具实现)
├── components/ (146 个 UI 组件)
├── hooks/ (87 个 React Hooks)
└── utils/ (331 个工具函数)
```

**核心架构** (6 层):
```
用户交互层 → 表现层 (Ink/React) → 状态管理层 → 核心引擎层 → 工具层 → 服务层 → 扩展层
```

**主要依赖**:
- @anthropic-ai/sdk - Anthropic API 客户端
- ink - Terminal UI 框架 (React for Terminal)
- react - UI 框架
- zod - Schema 验证
- @modelcontextprotocol/sdk - MCP 协议

---

### 阶段 2: 项目结构设计

#### 决策

**保留的核心功能**:

### 阶段 1: 源码分析

#### 任务
- [x] 克隆 claude-code-learning 仓库
- [x] 分析 source/src 目录结构
- [x] 统计文件数量和类型
- [x] 查看入口文件和核心依赖

#### 发现

**项目规模**:
```
source/src/
├── 1884 个 TypeScript 文件
├── main.tsx (804KB) - 入口文件
├── QueryEngine.ts (47KB) - 查询引擎
├── Tool.ts (30KB) - 工具抽象
├── tools/ (45 个工具实现)
├── components/ (146 个 UI 组件)
├── hooks/ (87 个 React Hooks)
└── utils/ (331 个工具函数)
```

**核心架构** (6 层):
```
用户交互层 → 表现层 (Ink/React) → 状态管理层 → 核心引擎层 → 工具层 → 服务层 → 扩展层
```

**主要依赖**:
- @anthropic-ai/sdk - Anthropic API 客户端
- ink - Terminal UI 框架 (React for Terminal)
- react - UI 框架
- zod - Schema 验证
- @modelcontextprotocol/sdk - MCP 协议

---

### 阶段 2: 项目结构设计

#### 决策

**保留的核心功能**:
1. ✅ QueryEngine - 查询引擎（简化版）
2. ✅ Tool 系统 - 工具抽象和注册
3. ✅ 基础工具 - Bash, FileRead, FileEdit, Grep, Glob
4. ✅ 记忆系统 - 简化版 JSON 存储
5. ✅ MCP 客户端 - 基础连接功能

**移除的复杂功能**:
1. ❌ Ink/React UI - 使用简单终端输出替代
2. ❌ 复杂权限管理 - 简化为基础检查
3. ❌ Skill/Plugin 系统 - 暂不实现
4. ❌ OAuth 认证流程 - 仅支持 API Key
5. ❌ 团队协作功能 - 单用户版本

**目标结构**:
```
source-deploy/
├── src/
│   ├── index.ts           # 主入口 (vs 原始 main.tsx 804KB)
│   ├── core/
│   │   ├── QueryEngine.ts # 6KB (vs 47KB)
│   │   └── Tool.ts        # 2KB (vs 30KB)
│   ├── tools/             # 5 个基础工具
│   ├── memory/            # 简化记忆系统
│   ├── mcp/               # 简化 MCP 客户端
│   └── utils/             # 日志和辅助函数
├── tests/                 # 单元测试
└── 配置文件
```

---

### 阶段 3: 配置文件创建

#### package.json

**设计考虑**:
- 使用 ES Modules (`"type": "module"`)
- 支持 Bun 和 Node.js
- 最小化依赖

**最终依赖**:
```json
{
  "dependencies": {
    "@anthropic-ai/sdk": "^0.36.0",      // Anthropic API
    "@modelcontextprotocol/sdk": "^1.7.0", // MCP 协议
    "zod": "^3.24.0",                     // Schema 验证
    "chalk": "^5.4.0",                    // 终端颜色
    "commander": "^13.1.0"                // CLI 框架
  },
  "devDependencies": {
    "@types/node": "^22.13.0",
    "typescript": "^5.8.0"
  }
}
```

#### tsconfig.json

**关键配置**:
```json
{
  "target": "ES2022",
  "module": "ESNext",
  "moduleResolution": "bundler",
  "jsx": "react-jsx",          // 保留，以防后续添加 UI
  "strict": true,
  "paths": {                   // 路径别名
    "@/*": ["src/*"],
    "@core/*": ["src/core/*"],
    ...
  }
}
```

---

### 阶段 4: 核心代码实现

#### 4.1 工具抽象 (Tool.ts)

**原始实现** (30KB):
- 复杂的权限检查系统
- 工具调用追踪
- 进度报告
- SDK 兼容性层

**简化版** (2KB):
```typescript
export abstract class BaseTool<T extends ToolInputSchema> {
  abstract readonly name: string;
  abstract readonly description: string;
  abstract readonly inputSchema: T;
  abstract execute(input: z.infer<T>): Promise<ToolResult>;
}
```

**问题与解决**:
- **问题**: 原始 Tool 类有大量抽象方法和钩子
- **解决**: 只保留核心接口，移除所有可选钩子

#### 4.2 查询引擎 (QueryEngine.ts)

**原始实现** (47KB):
- 完整的会话状态管理
- 流式处理管道
- 工具调用检测和结果回灌
- 技能/插件集成
- 持久化逻辑

**简化版** (6KB):
```typescript
export class QueryEngine {
  async *submitMessage(prompt: string): AsyncGenerator<StreamMessage> {
    // 1. 调用 Anthropic API
    // 2. 流式返回文本
    // 3. 检测工具调用
    // 4. 执行工具并返回结果
  }
}
```

**问题与解决**:
- **问题**: 原始 submitMessage 方法有 500+ 行代码
- **解决**: 提取核心流程，移除边界情况处理
- **问题**: 流式处理逻辑复杂
- **解决**: 使用 Anthropic SDK 的内置 stream API

#### 4.3 Bash 工具 (BashTool.ts)

**原始实现** (160KB):
- 24 项安全检查
- 路径白名单验证
- 命令模式匹配
- 交互式确认对话框

**简化版** (2KB):
```typescript
async execute(input: { command: string }) {
  // 1. 基础危险命令检测
  // 2. 执行命令
  // 3. 返回结果或错误
}
```

**问题与解决**:
- **问题**: 原始安全检查太复杂，难以复用
- **解决**: 只保留基础危险命令列表警告
- **注意**: ⚠️ 生产环境需要更严格的安全措施

#### 4.4 文件工具 (FileRead/FileEdit)

**原始实现**:
- 符号链接处理
- 大文件流式读取
- Diff 生成
- 多位置匹配处理

**简化版**:
- 基础路径安全检查
- 文件大小限制 (10MB)
- 简单查找替换

**问题与解决**:
- **问题**: 原始 file_edit 处理多个匹配位置
- **解决**: 要求 oldText 必须唯一匹配，否则报错

#### 4.5 搜索工具 (Grep/Glob)

**策略**: 使用系统命令而非纯 JS 实现

```typescript
// Grep: 优先使用 ripgrep (rg), 回退到 grep
const command = hasRg ? 'rg' : 'grep';

// Glob: 使用 find 命令
const command = `find "${path}" -name "${pattern}"`;
```

**优势**:
- 性能更好
- 代码更简洁
- 功能更强大

---

### 阶段 5: 记忆系统

**原始实现** (memdir/ 目录，约 20KB):
- 后台记忆提取
- 质量验证机制
- 记忆压缩和归档
- 多种记忆类型

**简化版** (MemoryManager.ts, 4KB):
```typescript
export class MemoryManager {
  addMemory(entry): MemoryEntry
  getMemories(options): MemoryEntry[]
  deleteMemory(id): boolean
  exportMemories(): string
}
```

**存储格式**:
```json
[
  {
    "id": "mem_123456_abc",
    "type": "note",
    "content": "...",
    "timestamp": 1234567890,
    "tags": ["important"]
  }
]
```

---

### 阶段 6: MCP 客户端

**原始实现** (services/mcp/, 约 25 个文件):
- 服务器自动发现
- 连接池管理
- 资源缓存
- 错误恢复机制

**简化版** (McpClient.ts, 5KB):
```typescript
export class McpClient {
  connect(): Promise<void>
  listTools(): Promise<McpTool[]>
  callTool(server, tool, args): Promise<string>
  listResources(): Promise<McpResource[]>
  readResource(uri): Promise<string>
}
```

**问题与解决**:
- **问题**: MCP SDK 文档不完善
- **解决**: 参考官方示例代码

---

### 阶段 7: 主入口 (index.ts)

**原始实现** (main.tsx, 804KB):
- CLI 参数解析
- MDM 设置读取
- Keychain 预取
- 遥测初始化
- 插件/技能加载
- Ink UI 渲染

**简化版** (index.ts, 7KB):
```typescript
async function main() {
  // 1. 解析命令行参数
  // 2. 加载环境变量
  // 3. 创建工具注册表
  // 4. 初始化记忆系统
  // 5. 创建查询引擎
  // 6. 启动 REPL 或执行单次提示
}
```

**CLI 选项**:
```bash
-k, --api-key <key>       # API Key
-m, --model <model>       # 模型名称
-p, --prompt <prompt>     # 直接执行
--ollama                  # 使用 Ollama
-v, --verbose             # 详细日志
```

---

## 📊 改造总结

### 代码量对比

| 组件 | 原始 | 简化版 | 压缩比 |
|------|------|--------|--------|
| 入口文件 | 804KB | 7KB | 99% |
| QueryEngine | 47KB | 6KB | 87% |
| Tool.ts | 30KB | 2KB | 93% |
| BashTool | 160KB | 2KB | 99% |
| UI 组件 | ~500KB | 0 | 100% |
| **总计** | **~2MB** | **~50KB** | **97%** |

### 依赖对比

| 类别 | 原始 | 简化版 |
|------|------|--------|
| 核心依赖 | 50+ | 5 |
| UI 相关 | ink, react, ink-spinner 等 | 无 |
| 内部依赖 | 大量 src/ 内部导入 | 无 |
| 外部 API | Anthropic, OAuth 等 | Anthropic |

### 功能对比

| 功能 | 原始 | 简化版 | 状态 |
|------|------|--------|------|
| 对话 | ✅ | ✅ | 完整 |
| Bash 工具 | ✅ | ✅ | 基础 |
| 文件读写 | ✅ | ✅ | 基础 |
| 搜索工具 | ✅ | ✅ | 基础 |
| MCP 集成 | ✅ | ✅ | 基础 |
| 记忆系统 | ✅ | ✅ | 简化 |
| Terminal UI | ✅ | ❌ | 移除 |
| 权限管理 | ✅ | ⚠️ | 简化 |
| Skill/Plugin | ✅ | ❌ | 移除 |
| OAuth | ✅ | ❌ | 移除 |
| 团队协作 | ✅ | ❌ | 移除 |

---

## 🔧 遇到的问题

### 问题 1: 循环依赖

**现象**: 原始代码中大量使用循环导入

**原始代码**:
```typescript
// main.tsx imports commands.ts
// commands.ts imports main.tsx via require()
```

**解决**: 
- 重新设计模块结构
- 使用依赖注入
- 避免跨层级导入

### 问题 2: 内部依赖

**现象**: 原始代码导入大量内部模块

```typescript
import { something } from './utils/internalThing.js';
```

**解决**:
- 识别核心功能所需的最小依赖集
- 用公开 NPM 包替代
- 自行实现简化版本

### 问题 3: TypeScript 配置

**现象**: 原始代码使用特殊的 Bun 特性

```typescript
import { feature } from 'bun:bundle';
```

**解决**:
- 使用标准 ES Modules
- 移除 Bun 特定导入
- 保持 Node.js 兼容性

### 问题 4: 流式处理

**现象**: 原始流式处理逻辑复杂

**解决**:
- 使用 Anthropic SDK 的 stream API
- 简化为统一的 StreamMessage 类型
- 分类型处理（text/tool_use/tool_result/error）

---

## ✅ 测试覆盖

### 单元测试

```bash
$ bun test

tests/tool.test.ts:
✓ BashTool > should execute simple commands [12ms]
✓ BashTool > should handle command errors [5ms]
✓ BashTool > should respect timeout [1003ms]
✓ FileReadTool > should read existing files [3ms]
✓ FileReadTool > should handle missing files [1ms]
✓ FileReadTool > should respect maxLines [2ms]
✓ FileEditTool > should fail on missing files [1ms]
✓ FileEditTool > should fail when text not found [2ms]
✓ GrepTool > should find patterns [15ms]
✓ GrepTool > should handle no matches [8ms]
✓ GlobTool > should find matching files [10ms]
✓ GlobTool > should handle no matches [5ms]
✓ ToolRegistry > should register and retrieve tools [1ms]
✓ ToolRegistry > should return undefined for unknown tools [0ms]

14 tests passed
```

---

## 🎯 下一步计划

### 立即可做

1. [ ] 添加 WebFetch 工具
2. [ ] 实现 Token 计数
3. [ ] 添加配置文件支持
4. [ ] 改进错误处理

### 需要调研

1. [ ] 如何安全地执行 Bash 命令
2. [ ] 如何实现更好的记忆提取
3. [ ] 如何支持更多 LLM 后端

### 长期目标

1. [ ] 可选的 UI 层
2. [ ] 完整的 MCP 支持
3. [ ] Skill/Plugin 系统

---

_最后更新：2026-04-06_
