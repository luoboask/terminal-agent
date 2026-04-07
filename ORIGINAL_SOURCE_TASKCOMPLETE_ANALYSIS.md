# 📖 原始源码 TaskComplete/TaskUpdate 实现分析

**分析时间**: 2026-04-07 02:20  
**源码位置**: `/tmp/claude-code-learning/source/src/tools/TaskUpdateTool/TaskUpdateTool.ts`

---

## 🎯 原始源码实现

### 注意

**原始源码中没有 TaskCompleteTool**，只有 **TaskUpdateTool**。完成任务只是将 status 设置为 'completed'。

---

## 📋 TaskUpdateTool Schema

```typescript
const inputSchema = z.strictObject({
  taskId: z.string().describe('The ID of the task to update'),
  subject: z.string().optional().describe('New subject for the task'),
  description: z.string().optional().describe('New description'),
  activeForm: z.string().optional().describe('Present continuous form'),
  status: TaskStatusSchema().optional().describe('New status'),
  addBlocks: z.array(z.string()).optional().describe('Task IDs that this task blocks'),
  addBlockedBy: z.array(z.string()).optional().describe('Task IDs that block this task'),
  owner: z.string().optional().describe('New owner'),
  metadata: z.record(z.string(), z.unknown()).optional().describe('Metadata'),
})
```

**TaskStatus**:
```typescript
const TaskStatusSchema = z.enum(['pending', 'in_progress', 'completed'])
```

---

## 🔧 核心实现

### call 函数

```typescript
async call(
  {
    taskId,
    subject,
    description,
    activeForm,
    status,
    owner,
    addBlocks,
    addBlockedBy,
    metadata,
  },
  context,
) {
  const taskListId = getTaskListId()

  // 1. 自动展开任务列表
  context.setAppState(prev => {
    if (prev.expandedView === 'tasks') return prev
    return { ...prev, expandedView: 'tasks' as const }
  })

  // 2. 检查任务是否存在
  const existingTask = await getTask(taskListId, taskId)
  if (!existingTask) {
    return {
      data: {
        success: false,
        taskId,
        updatedFields: [],
        error: 'Task not found',
      },
    }
  }

  const updatedFields: string[] = []

  // 3. 构建更新对象
  const updates: {
    subject?: string
    description?: string
    activeForm?: string
    status?: TaskStatus
    owner?: string
    metadata?: Record<string, unknown>
  } = {}

  // 4. 更新字段（只有当值不同时才更新）
  if (subject !== undefined && subject !== existingTask.subject) {
    updates.subject = subject
    updatedFields.push('subject')
  }
  if (description !== undefined && description !== existingTask.description) {
    updates.description = description
    updatedFields.push('description')
  }
  if (activeForm !== undefined && activeForm !== existingTask.activeForm) {
    updates.activeForm = activeForm
    updatedFields.push('activeForm')
  }
  if (owner !== undefined && owner !== existingTask.owner) {
    updates.owner = owner
    updatedFields.push('owner')
  }
  
  // 5. 自动设置 owner（当状态变为 in_progress 且没有 owner 时）
  if (
    isAgentSwarmsEnabled() &&
    status === 'in_progress' &&
    owner === undefined &&
    !existingTask.owner
  ) {
    const agentName = getAgentName()
    if (agentName) {
      updates.owner = agentName
      updatedFields.push('owner')
    }
  }
  
  // 6. 合并 metadata
  if (metadata !== undefined) {
    const merged = { ...(existingTask.metadata ?? {}) }
    for (const [key, value] of Object.entries(metadata)) {
      if (value === null) {
        delete merged[key]
      } else {
        merged[key] = value
      }
    }
    updates.metadata = merged
    updatedFields.push('metadata')
  }
  
  // 7. 处理删除
  if (status !== undefined) {
    if (status === 'deleted') {
      const deleted = await deleteTask(taskListId, taskId)
      return {
        data: {
          success: deleted,
          taskId,
          updatedFields: deleted ? ['deleted'] : [],
          error: deleted ? undefined : 'Failed to delete task',
          statusChange: deleted
            ? { from: existingTask.status, to: 'deleted' }
            : undefined,
        },
      }
    }
    
    // 8. 处理状态变更
    updates.status = status
    updatedFields.push('status')
    
    // 9. 执行完成钩子
    if (status === 'completed') {
      const generator = executeTaskCompletedHooks(
        taskId,
        existingTask.subject,
        existingTask.description,
        getAgentName(),
        getTeamName(),
        undefined,
        context?.abortController?.signal,
      )
      // Fire and forget
      generator.next().catch(() => {})
    }
  }
  
  // 10. 处理依赖关系
  if (addBlocks?.length) {
    for (const blockedTaskId of addBlocks) {
      const blockedTask = await getTask(taskListId, blockedTaskId)
      if (blockedTask && !blockedTask.blockedBy.includes(taskId)) {
        await updateTask(taskListId, blockedTaskId, {
          addBlockedBy: [taskId],
        })
      }
    }
  }
  
  if (addBlockedBy?.length) {
    for (const blockingTaskId of addBlockedBy) {
      const blockingTask = await getTask(taskListId, blockingTaskId)
      if (blockingTask && !blockingTask.blocks.includes(taskId)) {
        await updateTask(taskListId, blockingTaskId, {
          addBlocks: [taskId],
        })
      }
    }
  }
  
  // 11. 更新任务
  const updatedTask = await updateTask(taskListId, taskId, updates)
  
  // 12. 返回结果
  return {
    data: {
      success: !!updatedTask,
      taskId,
      updatedFields,
      statusChange: {
        from: existingTask.status,
        to: status || existingTask.status,
      },
      verificationNudgeNeeded: 
        status === 'completed' && 
        getFeatureValue_CACHED_MAY_BE_STALE('tengu_verification_nudge', false),
    },
  }
}
```

---

## 📊 关键特性

### 1. 文件锁机制

```typescript
// 在 updateTask 函数中
let release: (() => Promise<void>) | undefined
try {
  release = await lockfile.lock(path, LOCK_OPTIONS)
  return await updateTaskUnsafe(taskListId, taskId, updates)
} finally {
  await release?.()
}
```

**目的**: 防止并发修改

---

### 2. 智能字段更新

```typescript
// 只有当值不同时才更新
if (subject !== undefined && subject !== existingTask.subject) {
  updates.subject = subject
  updatedFields.push('subject')
}
```

**优点**: 避免不必要的更新

---

### 3. 自动设置 owner

```typescript
// 当状态变为 in_progress 且没有 owner 时，自动设置当前 agent 为 owner
if (
  isAgentSwarmsEnabled() &&
  status === 'in_progress' &&
  owner === undefined &&
  !existingTask.owner
) {
  const agentName = getAgentName()
  if (agentName) {
    updates.owner = agentName
    updatedFields.push('owner')
  }
}
```

**目的**: 任务列表可以显示谁在执行任务

---

### 4. 完成钩子

```typescript
// 当状态变为 completed 时，执行完成钩子
if (status === 'completed') {
  const generator = executeTaskCompletedHooks(...)
  generator.next().catch(() => {})  // Fire and forget
}
```

**目的**: 通知其他组件任务已完成

---

### 5. 依赖关系管理

```typescript
// 添加阻塞关系
if (addBlocks?.length) {
  for (const blockedTaskId of addBlocks) {
    await updateTask(taskListId, blockedTaskId, {
      addBlockedBy: [taskId],
    })
  }
}

// 添加被阻塞关系
if (addBlockedBy?.length) {
  for (const blockingTaskId of addBlockedBy) {
    await updateTask(taskListId, blockingTaskId, {
      addBlocks: [taskId],
    })
  }
}
```

**目的**: 管理任务之间的依赖关系

---

## 📊 实现对比

| 特性 | 原始源码 | 我们的实现 |
|------|---------|-----------|
| **Schema** | taskId | taskId + task_id ✅ |
| **文件锁** | ✅ proper-lockfile | ❌ 无 |
| **智能更新** | ✅ 值不同才更新 | ⚠️ 总是更新 |
| **自动 owner** | ✅ in_progress 时 | ❌ 无 |
| **完成钩子** | ✅ executeTaskCompletedHooks | ❌ 无 |
| **依赖管理** | ✅ addBlocks/addBlockedBy | ❌ 无 |
| **状态变更** | ✅ from/to | ⚠️ 简化版 |
| **删除任务** | ✅ status='deleted' | ❌ 无 |

---

## 💡 改进建议

### 方案 1: 保持当前实现（推荐）⭐⭐⭐⭐⭐

**理由**:
- ✅ 简单高效
- ✅ 适合单 Agent 场景
- ✅ 无额外依赖
- ✅ 支持两种命名（taskId/task_id）

**适用**: 个人使用、单 Agent 场景

---

### 方案 2: 参考原始源码（高级）⭐⭐⭐⭐

**改进点**:
1. 添加文件锁机制
2. 智能字段更新（值不同才更新）
3. 自动设置 owner
4. 完成钩子
5. 依赖关系管理

**优点**:
- ✅ 更健壮
- ✅ 支持并发
- ✅ 功能完整

**缺点**:
- ❌ 复杂度增加
- ❌ 需要额外依赖（proper-lockfile）
- ❌ 性能开销

**适用**: 多 Agent 并发场景

---

### 方案 3: 混合方案（最佳）⭐⭐⭐⭐⭐

**思路**: 保持简单实现，添加关键特性

```typescript
// 1. 智能字段更新
const updates: Partial<Task> = {}
const updatedFields: string[] = []

if (summary !== undefined && summary !== task.summary) {
  updates.summary = summary
  updatedFields.push('summary')
}

// 2. 完成钩子（简化版）
if (status === 'completed') {
  console.log(`✅ Task ${taskId} completed: ${task.summary}`)
}

// 3. 返回详细结果
return {
  success: true,
  taskId,
  updatedFields,
  statusChange: {
    from: task.status,
    to: status,
  },
}
```

---

## ✅ 总结

### 原始源码实现

- ✅ 文件锁机制
- ✅ 智能字段更新
- ✅ 自动设置 owner
- ✅ 完成钩子
- ✅ 依赖关系管理
- ✅ 状态变更记录
- ✅ 删除任务支持

### 我们的实现

- ✅ 支持两种命名（taskId/task_id）
- ✅ 文件持久化存储
- ❌ 无文件锁
- ❌ 无智能更新
- ❌ 无自动 owner
- ❌ 无完成钩子
- ❌ 无依赖管理

### 推荐方案

**保持当前实现**（简单 + 支持两种命名）

**理由**:
1. ✅ 简单高效
2. ✅ 适合当前场景
3. ✅ 无额外依赖
4. ✅ AI 友好（支持两种命名）

**如需生产级功能**，可以参考原始源码添加：
- 文件锁机制
- 智能字段更新
- 完成钩子

---

_分析时间：2026-04-07 02:20_  
_原始源码：复杂完整_  
_我们的实现：简单 AI 友好_  
_推荐：保持当前实现_
