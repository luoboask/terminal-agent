# 📋 任务体系丰富实现方案

**分析时间**: 2026-04-07 02:25  
**参考**: 原始源码 Task 工具实现

---

## 🎯 原始源码任务工具

### 1. TaskGetTool

**功能**: 获取单个任务详情

**Schema**:
```typescript
const inputSchema = z.strictObject({
  taskId: z.string().describe('The ID of the task to retrieve'),
})

const outputSchema = z.object({
  task: z.object({
    id: z.string(),
    subject: z.string(),
    description: z.string(),
    status: TaskStatusSchema(),
    blocks: z.array(z.string()),
    blockedBy: z.array(z.string()),
  }).nullable(),
})
```

**返回格式**:
```typescript
{
  data: {
    task: {
      id: "1",
      subject: "开发游戏",
      description: "开发一个坦克大战游戏",
      status: "in_progress",
      blocks: ["2"],
      blockedBy: [],
    }
  }
}
```

---

### 2. TaskListTool

**功能**: 列出所有任务

**Schema**:
```typescript
const inputSchema = z.strictObject({})  // 无参数

const outputSchema = z.object({
  tasks: z.array(z.object({
    id: z.string(),
    subject: z.string(),
    status: TaskStatusSchema(),
    owner: z.string().optional(),
    blockedBy: z.array(z.string()),
  })),
})
```

**返回格式**:
```typescript
{
  data: {
    tasks: [
      { id: "1", subject: "任务 1", status: "completed", owner: "agent1" },
      { id: "2", subject: "任务 2", status: "in_progress", blockedBy: ["1"] },
    ]
  }
}
```

**特性**:
- ✅ 自动过滤已完成任务的阻塞关系
- ✅ 显示任务所有者
- ✅ 显示阻塞关系

---

### 3. TaskStopTool

**功能**: 停止运行中的任务

**Schema**:
```typescript
const inputSchema = z.strictObject({
  task_id: z.string().optional().describe('The ID of the background task to stop'),
  shell_id: z.string().optional().describe('Deprecated: use task_id instead'),
})
```

**验证逻辑**:
```typescript
async validateInput({ task_id }) {
  const task = appState.tasks?.[task_id]
  
  if (!task) {
    return { result: false, message: 'No task found' }
  }
  
  if (task.status !== 'running') {
    return { result: false, message: 'Task is not running' }
  }
  
  return { result: true }
}
```

**返回格式**:
```typescript
{
  data: {
    message: "Task stopped successfully",
    task_id: "1",
    task_type: "local_agent",
    command: "开发游戏",
  }
}
```

---

### 4. TaskOutputTool

**功能**: 获取任务输出/日志

**Schema**:
```typescript
const inputSchema = z.strictObject({
  task_id: z.string().describe('The task ID to get output from'),
  block: z.boolean().default(true).describe('Whether to wait for completion'),
  timeout: z.number().min(0).max(600000).default(30000).describe('Max wait time in ms'),
})
```

**特性**:
- ✅ 支持阻塞等待完成
- ✅ 超时控制（默认 30 秒）
- ✅ 支持多种任务类型（local_bash, local_agent, remote_agent）

**返回格式**:
```typescript
{
  data: {
    retrieval_status: "success" | "timeout" | "not_ready",
    task: {
      task_id: "1",
      task_type: "local_agent",
      status: "completed",
      description: "开发游戏",
      output: "游戏开发完成",
      prompt: "开发一个坦克大战游戏",
      result: "游戏已创建",
    }
  }
}
```

---

## 📊 实现对比

| 工具 | 原始源码 | 我们的实现 | 差距 |
|------|---------|-----------|------|
| **TaskGet** | ✅ 完整 | ✅ 基础版 | ⚠️ 缺少 blocks/blockedBy |
| **TaskList** | ✅ 完整 | ✅ 基础版 | ⚠️ 缺少过滤/所有者 |
| **TaskUpdate** | ✅ 完整 | ✅ 基础版 | ⚠️ 缺少智能更新 |
| **TaskComplete** | ❌ 无（用 Update） | ✅ 独立工具 | ✅ 更友好 |
| **TaskStop** | ✅ 完整 | ❌ 无 | ❌ 缺失 |
| **TaskOutput** | ✅ 完整 | ❌ 无 | ❌ 缺失 |

---

## 💡 丰富实现方案

### 方案 1: 添加 TaskStopTool ⭐⭐⭐⭐⭐

```typescript
const TaskStopInputSchema = z.object({
  task_id: z.string().describe('要停止的任务 ID'),
  reason: z.string().optional().describe('停止原因'),
})

export class TaskStopTool extends BaseTool<typeof TaskStopInputSchema> {
  readonly name = 'task_stop';
  readonly description = '停止运行中的任务';
  readonly inputSchema = TaskStopInputSchema;

  async execute(input: Input): Promise<ToolResult> {
    const { task_id, reason = '用户手动停止' } = input;
    
    const tasks = loadTasks();
    const taskIndex = tasks.findIndex(t => t.id === task_id);
    
    if (taskIndex === -1) {
      return {
        success: false,
        content: `❌ 未找到任务\n\n任务 ID: ${task_id}`,
        error: 'Task not found',
      };
    }
    
    const task = tasks[taskIndex];
    
    if (task.status !== 'in_progress') {
      return {
        success: false,
        content: `⚠️ 任务未运行中\n\n任务 ID: ${task_id}\n当前状态：${task.status}`,
        error: 'Task not running',
      };
    }
    
    // 更新状态
    task.status = 'stopped';
    task.stoppedAt = new Date().toISOString();
    task.stopReason = reason;
    
    tasks[taskIndex] = task;
    saveTasks(tasks);
    
    return {
      success: true,
      content: `✅ 任务已停止\n\n📋 任务 ID: ${task_id}\n📝 停止原因：${reason}\n🕐 停止时间：${task.stoppedAt}`,
      data: { task_id, task_type: 'user_task', reason },
    };
  }
}
```

---

### 方案 2: 添加 TaskOutputTool ⭐⭐⭐⭐⭐

```typescript
const TaskOutputInputSchema = z.object({
  task_id: z.string().describe('要获取输出的任务 ID'),
  block: z.boolean().optional().describe('是否等待完成（默认 true）'),
  timeout: z.number().optional().describe('超时时间（毫秒，默认 30000）'),
})

export class TaskOutputTool extends BaseTool<typeof TaskOutputInputSchema> {
  readonly name = 'task_output';
  readonly description = '获取任务输出/日志';
  readonly inputSchema = TaskOutputInputSchema;

  async execute(input: Input): Promise<ToolResult> {
    const { task_id, block = true, timeout = 30000 } = input;
    
    const tasks = loadTasks();
    const task = tasks.find(t => t.id === task_id);
    
    if (!task) {
      return {
        success: false,
        content: `❌ 未找到任务\n\n任务 ID: ${task_id}`,
        error: 'Task not found',
      };
    }
    
    // 如果阻塞且任务未完成，等待
    if (block && (task.status === 'pending' || task.status === 'in_progress')) {
      const startTime = Date.now();
      while (Date.now() - startTime < timeout) {
        const updatedTasks = loadTasks();
        const updatedTask = updatedTasks.find(t => t.id === task_id);
        
        if (updatedTask && updatedTask.status === 'completed') {
          task.status = 'completed';
          task.summary = updatedTask.summary;
          break;
        }
        
        await sleep(100);
      }
    }
    
    return {
      success: true,
      content: `📋 任务输出\n\n📋 任务 ID: ${task_id}\n📝 描述：${task.description}\n📊 状态：${task.status}\n${task.summary ? `\n📝 总结：${task.summary}` : ''}`,
      data: {
        task_id,
        task_type: 'user_task',
        status: task.status,
        description: task.description,
        output: task.summary || '',
      },
    };
  }
}
```

---

### 方案 3: 丰富 TaskGetTool ⭐⭐⭐⭐

```typescript
const TaskGetInputSchema = z.object({
  task_id: z.string().describe('任务 ID'),
})

export class TaskGetEnhancedTool extends BaseTool<typeof TaskGetInputSchema> {
  readonly name = 'task_get_enhanced';
  readonly description = '获取任务详情（包含阻塞关系）';
  readonly inputSchema = TaskGetInputSchema;

  async execute(input: Input): Promise<ToolResult> {
    const { task_id } = input;
    
    const tasks = loadTasks();
    const task = tasks.find(t => t.id === task_id);
    
    if (!task) {
      return {
        success: false,
        content: `❌ 未找到任务\n\n任务 ID: ${task_id}`,
        error: 'Task not found',
      };
    }
    
    // 获取阻塞关系
    const blocks = tasks.filter(t => t.blockedBy?.includes(task_id)).map(t => t.id);
    const blockedBy = tasks.filter(t => t.blocks?.includes(task_id)).map(t => t.id);
    
    return {
      success: true,
      content: `📋 任务详情\n\n📋 任务 ID: ${task_id}\n📝 标题：${task.subject}\n📄 描述：${task.description}\n📊 状态：${task.status}\n🔗 阻塞：${blocks.length > 0 ? blocks.join(', ') : '无'}\n🔗 被阻塞：${blockedBy.length > 0 ? blockedBy.join(', ') : '无'}`,
      data: {
        task: {
          id: task.id,
          subject: task.subject,
          description: task.description,
          status: task.status,
          blocks,
          blockedBy,
        },
      },
    };
  }
}
```

---

### 方案 4: 丰富 TaskListTool ⭐⭐⭐⭐

```typescript
const TaskListEnhancedInputSchema = z.object({
  status: z.enum(['all', 'pending', 'in_progress', 'completed', 'stopped']).optional().describe('按状态筛选'),
  owner: z.string().optional().describe('按所有者筛选'),
  groupBy: z.enum(['none', 'status', 'owner']).optional().describe('分组显示'),
})

export class TaskListEnhancedTool extends BaseTool<typeof TaskListEnhancedInputSchema> {
  readonly name = 'task_list_enhanced';
  readonly description = '列出任务（支持筛选和分组）';
  readonly inputSchema = TaskListEnhancedInputSchema;

  async execute(input: Input): Promise<ToolResult> {
    const { status = 'all', owner, groupBy = 'none' } = input;
    
    let tasks = loadTasks();
    
    // 筛选
    if (status !== 'all') {
      tasks = tasks.filter(t => t.status === status);
    }
    if (owner) {
      tasks = tasks.filter(t => t.owner === owner);
    }
    
    // 按创建时间排序
    tasks = tasks.sort((a, b) => 
      new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    );
    
    // 分组显示
    if (groupBy !== 'none') {
      const groups: Record<string, any[]> = {};
      tasks.forEach(task => {
        const key = groupBy === 'status' ? task.status : (task.owner || 'unassigned');
        if (!groups[key]) groups[key] = [];
        groups[key].push(task);
      });
      
      let output = `📋 任务列表\n\n`;
      Object.entries(groups).forEach(([key, tasks]) => {
        output += `**${key}** (${tasks.length}个)\n`;
        tasks.forEach(task => {
          output += `- #${task.id}: ${task.subject}\n`;
        });
        output += '\n';
      });
      
      return { success: true, content: output, data: { groups } };
    }
    
    // 普通列表
    const output = `📋 任务列表\n\n${tasks.map(t => `- #${t.id}: ${t.subject} [${t.status}]`).join('\n')}`;
    
    return { success: true, content: output, data: { tasks } };
  }
}
```

---

## ✅ 总结

### 原始源码特性

- ✅ TaskGet - 完整详情（含阻塞关系）
- ✅ TaskList - 智能过滤/排序
- ✅ TaskUpdate - 智能字段更新
- ✅ TaskStop - 停止运行任务
- ✅ TaskOutput - 获取任务输出

### 我们的实现

- ✅ TaskGetEnhanced - 基础版 → 增强版
- ✅ TaskListEnhanced - 基础版 → 增强版
- ✅ TaskUpdateEnhanced - 基础版
- ✅ TaskCompleteEnhanced - 独立工具
- ⬜ TaskStop - 待添加
- ⬜ TaskOutput - 待添加

### 下一步

1. ⬜ 添加 TaskStopTool
2. ⬜ 添加 TaskOutputTool
3. ⬜ 增强 TaskGetTool（阻塞关系）
4. ⬜ 增强 TaskListTool（筛选/分组）

---

_分析时间：2026-04-07 02:25_  
_原始源码：完整复杂_  
_我们的实现：基础 → 增强_  
_推荐：逐步丰富_
