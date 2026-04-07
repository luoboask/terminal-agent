# 📖 原始源码任务系统实现分析

**分析时间**: 2026-04-07 01:15  
**源码位置**: `/tmp/claude-code-learning/source/src/utils/tasks.ts`

---

## 🎯 原始源码实现方式

### 核心架构

**存储方式**: 文件系统（每个任务一个 JSON 文件）

**目录结构**:
```
~/.claude-code/tasks/<taskListId>/
├── .highwatermark      # 最高任务 ID
├── .lock               # 锁文件（防止并发冲突）
├── 1.json              # 任务 1
├── 2.json              # 任务 2
└── 3.json              # 任务 3
```

---

### 核心函数

#### 1. createTask

```typescript
export async function createTask(
  taskListId: string,
  taskData: Omit<Task, 'id'>,
): Promise<string> {
  const lockPath = await ensureTaskListLockFile(taskListId);

  let release: (() => Promise<void>) | undefined;
  try {
    // 获取任务列表的独占锁
    release = await lockfile.lock(lockPath, LOCK_OPTIONS);

    // 读取最高任务 ID
    const highestId = await findHighestTaskId(taskListId);
    const id = String(highestId + 1);
    
    // 创建任务对象
    const task: Task = { id, ...taskData };
    
    // 写入文件
    const path = getTaskPath(taskListId, id);
    await writeFile(path, jsonStringify(task, null, 2));
    
    notifyTasksUpdated();
    return id;
  } finally {
    if (release) {
      await release();  // 释放锁
    }
  }
}
```

**特点**:
- ✅ 使用文件锁防止并发冲突
- ✅ 自动递增任务 ID
- ✅ 每个任务独立文件
- ✅ 通知监听器更新

---

#### 2. getTask

```typescript
export async function getTask(
  taskListId: string,
  taskId: string,
): Promise<Task | null> {
  const path = getTaskPath(taskListId, taskId);
  
  try {
    const content = await readFile(path, 'utf-8');
    return jsonParse(content);  // 安全的 JSON 解析
  } catch (error) {
    if (getErrnoCode(error) === 'ENOENT') {
      return null;  // 任务不存在
    }
    throw error;
  }
}
```

---

#### 3. updateTask

```typescript
export async function updateTask(
  taskListId: string,
  taskId: string,
  updates: Partial<Task>,
): Promise<void> {
  const lockPath = await ensureTaskListLockFile(taskListId);

  let release: (() => Promise<void>) | undefined;
  try {
    // 获取锁
    release = await lockfile.lock(lockPath, LOCK_OPTIONS);

    // 读取现有任务
    const task = await getTask(taskListId, taskId);
    if (!task) {
      throw new Error(`Task ${taskId} not found`);
    }

    // 合并更新
    const updatedTask = { ...task, ...updates };
    
    // 写回文件
    const path = getTaskPath(taskListId, taskId);
    await writeFile(path, jsonStringify(updatedTask, null, 2));
    
    notifyTasksUpdated();
  } finally {
    if (release) {
      await release();  // 释放锁
    }
  }
}
```

---

#### 4. listTasks

```typescript
export async function listTasks(
  taskListId: string,
  status?: TaskStatus,
): Promise<Task[]> {
  const dir = getTasksDir(taskListId);
  
  // 读取所有任务文件
  const files = await readdir(dir);
  const tasks: Task[] = [];
  
  for (const file of files) {
    if (!file.endsWith('.json')) continue;
    
    const content = await readFile(join(dir, file), 'utf-8');
    const task = jsonParse(content);
    
    // 可选：按状态筛选
    if (status && task.status !== status) continue;
    
    tasks.push(task);
  }
  
  // 按创建时间排序
  return tasks.sort((a, b) => parseInt(a.id) - parseInt(b.id));
}
```

---

### 并发控制

**文件锁机制**:
```typescript
const LOCK_OPTIONS = {
  retries: {
    retries: 30,        // 重试 30 次
    minTimeout: 5,      // 最小超时 5ms
    maxTimeout: 100,    // 最大超时 100ms
  },
};

// 获取锁
const release = await lockfile.lock(lockPath, LOCK_OPTIONS);

try {
  // 临界区操作
} finally {
  await release();  // 释放锁
}
```

**重试策略**:
- 重试 30 次
- 指数退避（5ms → 100ms）
- 总等待时间约 2.6 秒
- 支持 10+ 并发 Agent

---

### 任务数据结构

```typescript
export type Task = {
  id: string;                    // 任务 ID（数字字符串）
  subject: string;               // 标题
  description: string;           // 描述
  activeForm?: string;           // 进行中的显示文本
  owner?: string;                // 所有者（Agent ID）
  status: TaskStatus;            // pending | in_progress | completed
  blocks: string[];              // 被此任务阻塞的任务 ID
  blockedBy: string[];           // 阻塞此任务的任务 ID
  metadata?: Record<string, unknown>;  // 元数据
};
```

---

## 📊 实现对比

| 特性 | 原始源码 | 我们的实现 |
|------|---------|-----------|
| **存储方式** | 文件系统（每任务一文件） | JSON 文件（单文件） |
| **并发控制** | ✅ 文件锁 | ❌ 无 |
| **任务 ID** | 自动递增 | UUID |
| **目录结构** | `~/.claude-code/tasks/<id>/` | `./.source-deploy-tasks.json` |
| **通知机制** | ✅ 事件通知 | ❌ 无 |
| **安全性** | ✅ 安全 JSON 解析 | ⚠️ JSON.parse |
| **性能** | 中（多文件） | 高（单文件） |
| **适用场景** | 多 Agent 并发 | 单 Agent |

---

## 💡 改进建议

### 方案 1: 保持当前实现（推荐）⭐⭐⭐⭐⭐

**理由**:
- ✅ 简单高效
- ✅ 单文件易管理
- ✅ 适合单 Agent 场景
- ✅ 无额外依赖

**适用**: 个人使用、单 Agent 场景

---

### 方案 2: 参考原始源码（高级）⭐⭐⭐⭐

**改进点**:
1. 添加文件锁机制
2. 每个任务独立文件
3. 自动递增 ID
4. 事件通知机制

**优点**:
- ✅ 支持多 Agent 并发
- ✅ 更健壮
- ✅ 更接近原始源码

**缺点**:
- ❌ 复杂度增加
- ❌ 需要锁文件管理
- ❌ 多文件管理

**适用**: 多 Agent 并发场景

---

### 方案 3: 混合方案（最佳）⭐⭐⭐⭐⭐

**思路**: 保持单文件存储，添加锁机制

```typescript
import lockfile from 'proper-lockfile';

let fileLock: (() => Promise<void>) | null = null;

export async function updateTask(taskId: string, updates: Partial<Task>): Promise<Task | null> {
  // 获取文件锁
  if (!fileLock) {
    fileLock = await lockfile.lock(TASK_STORAGE_FILE, { retries: 5 });
  }
  
  try {
    // 读取任务
    const tasks = loadTasks();
    const taskIndex = tasks.findIndex(t => t.id === taskId);
    
    if (taskIndex === -1) return null;
    
    // 更新任务
    tasks[taskIndex] = { ...tasks[taskIndex], ...updates };
    
    // 保存
    saveTasks(tasks);
    
    return tasks[taskIndex];
  } finally {
    // 释放锁
    if (fileLock) {
      await fileLock();
      fileLock = null;
    }
  }
}
```

---

## ✅ 总结

### 原始源码实现

- ✅ 文件系统存储（每任务一文件）
- ✅ 文件锁并发控制
- ✅ 自动递增 ID
- ✅ 事件通知机制
- ✅ 安全 JSON 解析

### 我们的实现

- ✅ JSON 文件存储（单文件）
- ❌ 无并发控制
- ✅ UUID 任务 ID
- ❌ 无事件通知
- ⚠️ 标准 JSON.parse

### 推荐方案

**保持当前实现**（单文件 JSON 存储）

**理由**:
1. ✅ 简单高效
2. ✅ 适合单 Agent 场景
3. ✅ 无额外依赖
4. ✅ 易于调试

**如需支持多 Agent**，可以参考原始源码添加文件锁机制。

---

_分析时间：2026-04-07 01:15_  
_原始源码：文件系统 + 文件锁_  
_我们的实现：单 JSON 文件_  
_推荐：保持当前实现_
