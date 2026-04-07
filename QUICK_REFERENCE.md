# 快速参考卡片

## 🚀 日常使用速查

### 项目状态

```typescript
// 初始化（启动时）
initState(process.cwd());

// 查看状态
printState();

// 获取项目根目录
getProjectRoot();
```

### 项目设置

```typescript
// 获取设置
const settings = getSettings();

// 更新设置
updateProjectSettings({
  model: 'qwen3.5-plus',
  maxTokens: 4096
});

// 重置设置
resetProjectSettings();
```

### 会话管理

```typescript
// 创建会话
const session = createSession('会话标题');

// 添加消息
addMessage(session.id, {
  role: 'user',
  content: '消息内容'
});

// 列出会话
const sessions = listSessions();

// 搜索会话
const found = searchSessions('关键词');

// 删除会话
deleteSession(session.id);
```

### 任务管理

```typescript
// 创建任务
createTask({
  subject: '任务标题',
  description: '任务描述',
  priority: 'high',
  status: 'pending',
  activeForm: '进行中...'
});

// 查看任务
console.log(listTasksSimple());

// 更新任务
updateTask(taskId, {
  status: 'completed'
});

// 清理任务
cleanupTasks(24);  // 清理 24 小时前的已完成任务
```

### Worktree 管理

```typescript
// 列出 worktree
worktree({ action: 'list' })

// 创建 worktree
worktree({
  action: 'create',
  worktreePath: '../feature-login',
  branch: 'feature/login'
})

// 切换 worktree
worktree({
  action: 'switch',
  worktreePath: '../feature-login'
})

// 删除 worktree
worktree({
  action: 'delete',
  worktreePath: '../feature-login'
})

// 清理无效 worktree
worktree({ action: 'prune' })
```

### 跨项目恢复

```typescript
// 从其他项目加载会话
const session = loadSession('session_id', '/other/project');

// 跨项目恢复会话
resumeSession(
  'session_id',
  '/project-a',  // 源项目
  '/project-b'   // 目标项目
);
```

---

## 📁 目录结构

```
<projectRoot>/
├── .source-deploy/
│   ├── settings.json        # 项目设置
│   ├── sessions/            # 会话存储
│   │   └── session_xxx.json
│   └── tasks/               # 任务存储
│       └── task_xxx.json
└── ...项目文件
```

---

## 🎯 常用工作流

### 开始新任务

```typescript
// 1. 创建会话
const session = createSession('新功能开发');

// 2. 创建任务
createTask({
  subject: '实现新功能',
  priority: 'high',
  activeForm: '实现新功能中'
});

// 3. 添加消息
addMessage(session.id, {
  role: 'user',
  content: '帮我实现新功能'
});
```

### 切换项目

```typescript
// 1. 创建 worktree
worktree({
  action: 'create',
  worktreePath: '../feature',
  branch: 'feature-branch'
});

// 2. 切换
worktree({
  action: 'switch',
  worktreePath: '../feature'
});

// 3. 验证
console.log(getProjectRoot());  // 新路径
```

### 完成任务

```typescript
// 1. 更新任务状态
updateTask(taskId, { status: 'completed' });

// 2. 添加完成消息
addMessage(session.id, {
  role: 'assistant',
  content: '任务已完成'
});

// 3. 清理（24 小时后自动）
cleanupTasks(24);
```

---

## ⚠️ 注意事项

### 项目根目录

- ✅ 启动时设置一次
- ❌ 避免在会话中频繁修改
- ✅ worktree 切换会自动更新

### 会话管理

- ✅ 及时保存消息
- ✅ 定期清理旧会话
- ❌ 避免创建过多会话

### 任务管理

- ✅ 使用 activeForm 描述进行中状态
- ✅ 及时更新任务状态
- ✅ 定期清理已完成任务

### Worktree

- ✅ 使用有意义的命名
- ✅ 完成后及时删除
- ❌ 避免过多 worktree

---

## 📊 状态图标

| 图标 | 含义 |
|------|------|
| ⚪ | 待处理 |
| ⏳ | 进行中 |
| ✅ | 已完成 |
| ❌ | 失败 |
| 🟢 | 低优先级 |
| 🟡 | 中优先级 |
| 🔴 | 高优先级 |

---

_最后更新：2026-04-07_
