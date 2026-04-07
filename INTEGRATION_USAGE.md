# 项目管理系统集成使用指南

## 📋 概述

展示如何将**项目管理系统**、**任务系统**、**会话系统**和**WorktreeTool**结合起来使用。

## 🎯 典型使用场景

### 场景 1：多项目并行开发

#### 背景
你同时开发两个项目：
- **Project A** - 电商网站（主项目）
- **Project B** - 数据分析工具（使用 worktree）

#### 工作流程

```typescript
// ============ 1. 初始化 ============

// 启动时自动初始化项目状态
import { initState, printState } from './src/bootstrap/state.js';
initState(process.cwd());
printState();
// 📊 当前状态:
//   项目根目录：/Users/dhr/projects/ecommerce
//   原始工作目录：/Users/dhr/projects/ecommerce
//   会话项目目录：(使用项目根目录)
//   工作树模式：❌

// ============ 2. 加载项目设置 ============

import { getSettings, initProjectSettings } from './src/utils/projectSettings.js';
initProjectSettings();

const settings = getSettings();
console.log(`模型：${settings.model}`);  // qwen3.5-plus
console.log(`Max Tokens: ${settings.maxTokens}`);  // 4096

// ============ 3. 创建会话 ============

import { createSession, addMessage } from './src/utils/sessionStorage.js';

// 为 Project A 创建会话
const sessionA = createSession('电商网站 - 购物车功能');
addMessage(sessionA.id, {
  role: 'user',
  content: '帮我实现购物车功能'
});

// ============ 4. 创建任务 ============

import { createTask } from './src/utils/taskStorageV2.js';

const task1 = createTask({
  subject: '实现购物车添加商品',
  description: '实现 addToCart 函数',
  priority: 'high',
  status: 'pending',
  activeForm: '实现购物车添加商品'
});

const task2 = createTask({
  subject: '实现购物车删除商品',
  description: '实现 removeFromCart 函数',
  priority: 'medium',
  status: 'pending',
  activeForm: '实现购物车删除商品'
});

// ============ 5. 查看任务列表 ============

import { listTasksSimple } from './src/utils/taskStorageV2.js';
console.log(listTasksSimple());
// ⏳ 🔴 #task_xxx: 实现购物车添加商品
// ⏳ 🟡 #task_yyy: 实现购物车删除商品

// ============ 6. 切换到 Project B（使用 worktree） ============

import { WorktreeTool } from './src/tools/WorktreeTool.js';

// 创建 Project B 的 worktree
const worktreeResult = await new WorktreeTool().execute({
  action: 'create',
  worktreePath: '../data-analytics',
  branch: 'feature-analysis'
});
// ✅ Worktree 已创建
// 📁 路径：/Users/dhr/projects/data-analytics
// 🌿 分支：feature-analysis

// 切换到 Project B
await new WorktreeTool().execute({
  action: 'switch',
  worktreePath: '../data-analytics'
});
// ✅ 已切换到 Worktree
// 📁 路径：/Users/dhr/projects/data-analytics
// 🏠 原路径：/Users/dhr/projects/ecommerce

// ============ 7. Project B 的工作 ============

// 此时项目根目录已自动更新
import { getProjectRoot } from './src/bootstrap/state.js';
console.log(getProjectRoot());  // /Users/dhr/projects/data-analytics

// 为 Project B 创建会话
const sessionB = createSession('数据分析 - 用户行为分析');
addMessage(sessionB.id, {
  role: 'user',
  content: '帮我实现用户行为分析功能'
});

// 为 Project B 创建任务
const task3 = createTask({
  subject: '实现用户行为追踪',
  description: '追踪用户点击、浏览等行为',
  priority: 'high',
  status: 'pending',
  activeForm: '实现用户行为追踪'
});

// ============ 8. 切换回 Project A ============

await new WorktreeTool().execute({
  action: 'switch',
  worktreePath: '/Users/dhr/projects/ecommerce'
});
// ✅ 已切换到 Worktree
// 📁 路径：/Users/dhr/projects/ecommerce

// ============ 9. 跨项目恢复会话 ============

import { resumeSession } from './src/utils/sessionStorage.js';

// 从 Project B 恢复会话到 Project A
const resumedSession = resumeSession(
  sessionB.id,
  '/Users/dhr/projects/data-analytics',  // 源项目
  '/Users/dhr/projects/ecommerce'        // 目标项目
);

// ============ 10. 完成任务 ============

import { updateTask } from './src/utils/taskStorageV2.js';

updateTask(task1.id, {
  status: 'completed',
  activeForm: '实现购物车添加商品'
});

// ============ 11. 查看最终状态 ============

printState();
// 📊 当前状态:
//   项目根目录：/Users/dhr/projects/ecommerce
//   原始工作目录：/Users/dhr/projects/ecommerce
//   会话项目目录：(使用项目根目录)
//   工作树模式：✅

const stats = require('./src/utils/sessionStorage.js').getSessionStats();
console.log(stats);
// {
//   totalSessions: 2,
//   totalMessages: 4,
//   oldestSession: '...',
//   newestSession: '...'
// }
```

---

### 场景 2：团队协作开发

#### 背景
团队开发一个项目，多个成员需要共享会话和任务。

#### 工作流程

```typescript
// ============ 1. 配置项目设置 ============

import { updateProjectSettings } from './src/utils/projectSettings.js';

updateProjectSettings({
  model: 'qwen3.5-plus',
  maxTokens: 8192,
  mcpServers: {
    github: {
      command: 'npx',
      args: ['-y', '@modelcontextprotocol/server-github']
    }
  },
  toolPermissions: {
    allowAlways: ['file_read', 'grep', 'glob'],
    requireConfirm: ['file_write', 'bash'],
    deny: []
  }
});

// ============ 2. 成员 A 开始工作 ============

// 创建会话
const session = createSession('用户认证模块');
addMessage(session.id, {
  role: 'user',
  content: '实现 JWT 认证'
});

// 创建任务
const task = createTask({
  subject: '实现 JWT 认证',
  description: '使用 jsonwebtoken 库',
  priority: 'high',
  status: 'in_progress',
  owner: 'member-a',
  activeForm: '实现 JWT 认证'
});

// ============ 3. 成员 B 继续工作 ============

// 加载会话（跨项目恢复）
const loadedSession = resumeSession(
  session.id,
  '/projects/main',  // 源项目
  '/projects/branch' // 目标项目（成员 B 的 worktree）
);

// 继续会话
addMessage(loadedSession.id, {
  role: 'user',
  content: '添加 refresh token 支持'
});

// 更新任务
updateTask(task.id, {
  status: 'in_progress',
  owner: 'member-b',
  activeForm: '添加 refresh token 支持'
});

// ============ 4. 查看会话历史 ============

const fullSession = loadSession(session.id);
console.log(fullSession.messages);
// [
//   { role: 'user', content: '实现 JWT 认证' },
//   { role: 'assistant', content: '...' },
//   { role: 'user', content: '添加 refresh token 支持' }
// ]

// ============ 5. 导出会话用于分享 ============

import { exportSession } from './src/utils/sessionStorage.js';

const json = exportSession(session.id);
// 可以发送给团队成员

// ============ 6. 团队成员导入会话 ============

import { importSession } from './src/utils/sessionStorage.js';

const imported = importSession(json);
// 团队成员现在有相同的会话
```

---

### 场景 3：功能开发完整流程

#### 背景
开发一个新功能，从需求分析到完成。

#### 工作流程

```typescript
// ============ 1. 需求分析阶段 ============

const session = createSession('需求分析 - 支付功能');

addMessage(session.id, {
  role: 'user',
  content: '分析支付功能需求'
});

// ============ 2. 创建任务列表 ============

const tasks = [
  '设计支付流程',
  '集成支付宝 SDK',
  '集成微信支付 SDK',
  '实现回调处理',
  '编写测试用例'
];

tasks.forEach((title, index) => {
  createTask({
    subject: title,
    description: `支付功能开发 - 任务 ${index + 1}`,
    priority: index === 0 ? 'high' : 'medium',
    status: 'pending',
    activeForm: title,
    metadata: { phase: 'development' }
  });
});

// ============ 3. 查看任务 ============

console.log(listTasksSimple());
// ⏳ 🔴 #xxx: 设计支付流程
// ⏳ 🟡 #xxx: 集成支付宝 SDK
// ⏳ 🟡 #xxx: 集成微信支付 SDK
// ⏳ 🟡 #xxx: 实现回调处理
// ⏳ 🟡 #xxx: 编写测试用例

// ============ 4. 开始开发 ============

// 更新第一个任务状态
updateTask(tasks[0].id, {
  status: 'in_progress',
  activeForm: '设计支付流程'
});

// 添加开发会话消息
addMessage(session.id, {
  role: 'assistant',
  content: '支付流程图：\n用户 → 选择支付方式 → 支付网关 → 回调 → 完成'
});

// ============ 5. 使用 worktree 隔离开发 ============

// 创建功能分支的 worktree
await new WorktreeTool().execute({
  action: 'create',
  worktreePath: '../payment-feature',
  branch: 'feature/payment'
});

await new WorktreeTool().execute({
  action: 'switch',
  worktreePath: '../payment-feature'
});

// ============ 6. 在 worktree 中开发 ============

// 此时项目根目录已切换到 feature 分支
console.log(getProjectRoot());  // /projects/payment-feature

// 继续开发...
addMessage(session.id, {
  role: 'user',
  content: '实现支付宝 SDK 集成'
});

// ============ 7. 完成任务 ============

updateTask(tasks[0].id, { status: 'completed' });
updateTask(tasks[1].id, { 
  status: 'in_progress',
  activeForm: '集成支付宝 SDK'
});

// ============ 8. 代码审查 ============

// 创建审查 worktree
await new WorktreeTool().execute({
  action: 'create',
  worktreePath: '../payment-review',
  branch: 'review/payment'
});

// ============ 9. 清理 ============

// 删除审查 worktree
await new WorktreeTool().execute({
  action: 'delete',
  worktreePath: '../payment-review'
});

// 清理已完成的任务（24 小时后）
import { cleanupTasks } from './src/utils/taskStorageV2.js';
cleanupTasks(24);  // 清理超过 24 小时的已完成任务

// ============ 10. 最终统计 ============

const stats = getSessionStats();
console.log(`会话数：${stats.totalSessions}`);
console.log(`消息数：${stats.totalMessages}`);

const taskStats = listTasksSimple();
console.log(taskStats);
```

---

## 📊 功能对比表

| 功能 | 单项目 | 多项目 | Worktree | 团队协作 |
|------|--------|--------|----------|---------|
| **项目根目录** | ✅ | ✅ | ✅ | ✅ |
| **会话管理** | ✅ | ✅ | ✅ | ✅ |
| **任务管理** | ✅ | ✅ | ✅ | ✅ |
| **设置管理** | ✅ | ✅ | ✅ | ✅ |
| **跨项目恢复** | ❌ | ✅ | ✅ | ✅ |
| **Worktree 切换** | ❌ | ❌ | ✅ | ✅ |
| **会话共享** | ❌ | ❌ | ❌ | ✅ |

---

## 💡 最佳实践

### 1. 项目初始化

```typescript
// 每次启动时
initState(process.cwd());
initProjectSettings();
```

### 2. 会话管理

```typescript
// 为每个功能创建独立会话
const session = createSession('功能名称');

// 及时保存
addMessage(session.id, message);  // 自动保存

// 定期清理
cleanupTasks(24);  // 清理 24 小时前的已完成任务
```

### 3. Worktree 使用

```typescript
// 命名规范
worktree({
  action: 'create',
  worktreePath: '../feature-login',  // 功能
  branch: 'feature/login'
});

worktree({
  action: 'create',
  worktreePath: '../hotfix-bug',  // 修复
  branch: 'hotfix/bug-fix'
});

// 及时清理
worktree({
  action: 'delete',
  worktreePath: '../feature-login'
});
```

### 4. 任务管理

```typescript
// 使用 activeForm
createTask({
  subject: '实现功能',
  activeForm: '实现功能中'  // 进行时形式
});

// 及时更新状态
updateTask(taskId, { status: 'completed' });
```

---

## 🔗 相关文档

- `PROJECT_MANAGEMENT_USAGE.md` - 项目管理系统
- `WORKTREE_TOOL_USAGE.md` - WorktreeTool
- `TASK_SYSTEM_OPTIMIZATION.md` - 任务系统

---

_最后更新：2026-04-07_
