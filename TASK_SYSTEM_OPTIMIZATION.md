# 任务系统优化文档

## 📋 优化概述

参考 claude-code-learning (source/src) 的设计，对任务系统进行了全面优化。

## 🎯 主要改进

### 1️⃣ 简化任务状态

**优化前：**
```typescript
type TaskStatus = 'pending' | 'in_progress' | 'completed' | 'failed' | 'stopped' | 'cancelled'
```

**优化后：**
```typescript
type TaskStatus = 'pending' | 'in_progress' | 'completed'
```

参考 claude-code-learning 的 3 状态设计，简化状态管理。

### 2️⃣ 新增任务字段

| 字段 | 类型 | 说明 | 参考 |
|------|------|------|------|
| `subject` | string | 任务标题 | ✅ claude-code-learning |
| `activeForm` | string | 进行中时显示的文本（如 "Running tests"） | ✅ claude-code-learning |
| `blocks` | string[] | 此任务阻塞的其他任务 ID | ✅ claude-code-learning |
| `blockedBy` | string[] | 阻塞此任务的其他任务 ID | ✅ claude-code-learning |
| `owner` | string | 负责此任务的 agent ID | ✅ claude-code-learning |

### 3️⃣ 存储方式优化

**优化前：**
- 单 JSON 文件存储所有任务
- 并发写入可能冲突

**优化后：**
- 每任务一个 JSON 文件
- 更好的可扩展性
- 支持文件锁机制（未来实现）

**目录结构：**
```
.source-deploy-tasks/
├── task_1775527788488_xxx.json
├── task_1775527788489_yyy.json
├── task_1775527788490_zzz.json
└── .highwatermark  # 高水位标记
```

### 4️⃣ 高水位标记

防止任务 ID 复用，即使任务被删除，其 ID 也不会被重新分配。

```typescript
// 高水位标记文件
.source-deploy-tasks/.highwatermark

// 内容：最大任务 ID 数值
12345
```

### 5️⃣ 简洁的输出格式

**优化前：**
```
📋 **任务列表**

⏳ 🟡 #task_xxx: 持久化测试 2
✅ 🔴 #task_yyy: 开发坦克大战游戏
```

**优化后：**
```
⏳ 🟡 #task_xxx: 持久化测试 2
✅ 🔴 #task_yyy: 开发坦克大战游戏
```

**带阻塞关系：**
```
⏳ 🟡 #task_xxx: 修复 bug [blocked by #task_yyy, #task_zzz]
✅ 🔴 #task_yyy: 添加测试
```

## 📊 对比总结

| 特性 | 优化前 | 优化后 | claude-code-learning |
|------|--------|--------|---------------------|
| 任务状态 | 6 种 | 3 种 | 3 种 ✅ |
| 存储方式 | 单文件 | 每任务一文件 | 每任务一文件 ✅ |
| 阻塞关系 | ❌ | ✅ | ✅ |
| activeForm | ❌ | ✅ | ✅ |
| 高水位标记 | ❌ | ✅ | ✅ |
| 输出格式 | 详细 | 简洁 | 简洁 ✅ |
| 文件锁 | ❌ | 待实现 | ✅ |

## 🔧 使用示例

### 创建任务

```typescript
import { createTask } from './utils/taskStorageV2.js';

const task = createTask({
  subject: '修复登录 bug',
  description: '用户反馈登录时偶尔会超时',
  priority: 'high',
  status: 'pending',
  activeForm: '修复登录 bug',
  blocks: [],
  blockedBy: [],
  metadata: { type: 'bug_fix' }
});
```

### 更新任务

```typescript
import { updateTask } from './utils/taskStorageV2.js';

updateTask('task_xxx', {
  status: 'in_progress',
  activeForm: '正在修复登录 bug'
});
```

### 列出任务

```typescript
import { listTasksSimple } from './utils/taskStorageV2.js';

const output = listTasksSimple();
console.log(output);
// ⏳ 🔴 #task_xxx: 修复登录 bug
// ✅ 🟡 #task_yyy: 添加测试
```

### 阻塞关系

```typescript
// 任务 A 阻塞任务 B
updateTask('task_a', {
  blocks: ['task_b']
});

updateTask('task_b', {
  blockedBy: ['task_a']
});

// 列出任务时会自动显示阻塞关系
// ⏳ 🔴 #task_b: 添加测试 [blocked by #task_a]
```

## 📁 文件变更

### 新增文件
- `src/utils/taskStorageV2.ts` - 新版任务存储模块
- `TASK_SYSTEM_OPTIMIZATION.md` - 本文档

### 修改文件
- `src/tools/TaskList.ts` - 使用简洁输出格式

### 已弃用
- `src/utils/taskStorage.ts` - 旧版（保留向后兼容）
- `scripts/cleanup_tasks.py` - 由新系统自动管理
- `scripts/complete_tasks.py` - 由新系统自动管理

## 🚀 迁移指南

### 自动迁移

旧任务文件会保持兼容，新任务使用新格式。

### 手动清理

```bash
# 清理旧任务文件
rm -rf .source-deploy-tasks.json

# 新系统会自动创建目录
```

## 💡 最佳实践

### 1. 任务状态流转

```
pending → in_progress → completed
```

避免跳过状态，确保任务生命周期清晰。

### 2. 使用 activeForm

```typescript
// 好的 activeForm
activeForm: 'Running tests'
activeForm: 'Fixing login bug'
activeForm: 'Deploying to production'

// 不好的 activeForm
activeForm: 'Working on it'  // 太模糊
activeForm: 'Task'  // 无意义
```

### 3. 阻塞关系

```typescript
// 任务依赖链
task_a (基础功能) → blocks → task_b (依赖功能) → blocks → task_c (集成功能)

// 列出任务时
#task_c: 集成功能 [blocked by #task_b]
#task_b: 依赖功能 [blocked by #task_a]
#task_a: 基础功能
```

### 4. 任务清理

系统会自动清理：
- 已完成超过 24 小时的任务
- 名称为 `undefined` 的任务

## 🔗 参考

- [claude-code-learning/source/src/utils/tasks.ts](https://github.com/luoboask/claude-code-learning/blob/main/source/src/utils/tasks.ts)
- [claude-code-learning/source/src/tools/TaskListTool/TaskListTool.ts](https://github.com/luoboask/claude-code-learning/blob/main/source/src/tools/TaskListTool/TaskListTool.ts)
- [claude-code-learning/source/src/tools/TaskCreateTool/TaskCreateTool.ts](https://github.com/luoboask/claude-code-learning/blob/main/source/src/tools/TaskCreateTool/TaskCreateTool.ts)

---

_最后更新：2026-04-07_
