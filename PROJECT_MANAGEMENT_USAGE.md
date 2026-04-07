# 项目管理系统使用指南

## 📋 概述

已按照 claude-code-learning 的设计实现了完整的项目管理系统，包括：

1. **状态管理** - 项目根目录、工作目录、会话目录
2. **项目设置** - 多层级配置管理
3. **会话存储** - 会话创建、加载、保存

## 🚀 快速开始

### 1️⃣ 初始化状态

```typescript
import { initState } from './src/bootstrap/state.js';

// 启动时初始化
initState(process.cwd());
```

### 2️⃣ 使用项目根目录

```typescript
import { getProjectRoot, getOriginalCwd } from './src/bootstrap/state.js';

// 获取项目根目录（用于项目身份标识）
const projectRoot = getProjectRoot();

// 获取原始工作目录（用于文件操作）
const originalCwd = getOriginalCwd();
```

### 3️⃣ 管理项目设置

```typescript
import { 
  getSettings, 
  updateProjectSettings,
  getProjectSettings 
} from './src/utils/projectSettings.js';

// 获取合并后的设置（会话 > 项目 > 全局）
const settings = getSettings();

// 更新项目设置
updateProjectSettings({
  model: 'qwen3.5-plus',
  maxTokens: 4096,
  verbose: true
});

// 获取项目特定设置
const projectSettings = getProjectSettings();
```

### 4️⃣ 管理会话

```typescript
import {
  createSession,
  loadSession,
  saveSession,
  addMessage,
  listSessions
} from './src/utils/sessionStorage.js';

// 创建新会话
const session = createSession('我的会话');

// 添加消息
addMessage(session.id, {
  role: 'user',
  content: '你好'
});

addMessage(session.id, {
  role: 'assistant',
  content: '你好！有什么可以帮你的吗？'
});

// 保存会话
saveSession(session);

// 加载会话
const loaded = loadSession(session.id);

// 列出所有会话
const sessions = listSessions();
```

## 📁 目录结构

```
<projectRoot>/
├── .source-deploy/
│   ├── settings.json          # 项目设置
│   ├── sessions/              # 会话存储
│   │   ├── session_xxx.json
│   │   └── session_yyy.json
│   └── tasks/                 # 任务存储
│       ├── task_xxx.json
│       └── task_yyy.json
└── ...项目文件
```

## 🔧 API 参考

### 状态管理 (state.ts)

```typescript
// 初始化
initState(cwd: string): void

// 项目根目录
getProjectRoot(): string
setProjectRoot(cwd: string): void

// 原始工作目录
getOriginalCwd(): string
setOriginalCwd(cwd: string): void

// 会话项目目录
getSessionProjectDir(): string | null
setSessionProjectDir(projectDir: string | null): void
getSessionStorageDir(): string  // 获取有效的会话存储目录

// 工作树模式
isWorktreeModeEnabled(): boolean
enableWorktreeMode(): void
disableWorktreeMode(): void

// 调试
exportState(): State
printState(): void
```

### 项目设置 (projectSettings.ts)

```typescript
// 获取设置
getSettings(): Settings
getGlobalSettings(): Settings
getProjectSettings(): Settings
getSessionSettings(): Settings

// 更新设置
updateGlobalSettings(changes): void
updateProjectSettings(changes): void
updateSessionSettings(changes): void

// 快捷方法
getSetting(key): value
setSetting(key, value): void
resetProjectSettings(): void
initProjectSettings(): void
```

### 会话存储 (sessionStorage.ts)

```typescript
// 会话管理
createSession(title?, metadata?): Session
loadSession(sessionId): Session | null
saveSession(session): void
deleteSession(sessionId): boolean

// 消息管理
addMessage(sessionId, message): Session | null
clearSessionMessages(sessionId): Session | null

// 查询
listSessions(): Session[]
getRecentSessions(limit): Session[]
searchSessions(query): Session[]
getSessionStats(): Stats

// 导入导出
exportSession(sessionId): string | null
importSession(json): Session | null
```

## 📊 设置层级

```
全局设置 (~/.source-deploy/settings.json)
    ↓ (继承)
项目设置 (<projectRoot>/.source-deploy/settings.json)
    ↓ (继承)
会话设置 (<sessionDir>/.source-deploy/session-settings.json)
```

**优先级：** 会话 > 项目 > 全局

## 💡 最佳实践

### 1. 项目身份稳定

```typescript
// ✅ 正确：启动时设置一次
initState(process.cwd());

// ❌ 错误：会话中频繁修改
setProjectRoot('/new/path');  // 避免这样做
```

### 2. 会话与项目分离

```typescript
// ✅ 正确：会话可以跨项目
setSessionProjectDir('/other/project');
const storageDir = getSessionStorageDir();  // 会话存储在其他项目
const projectRoot = getProjectRoot();       // 但项目身份不变
```

### 3. 设置使用

```typescript
// ✅ 正确：使用合并后的设置
const settings = getSettings();

// ✅ 正确：更新会话级别设置
setSetting('model', 'qwen3.5-plus');

// ❌ 错误：直接修改全局设置文件
```

### 4. 会话管理

```typescript
// ✅ 正确：及时保存
addMessage(sessionId, message);  // 自动保存

// ✅ 正确：定期清理旧会话
const sessions = listSessions();
sessions.forEach(s => {
  if (isOld(s)) deleteSession(s.id);
});
```

## 🔗 相关文件

- `src/bootstrap/state.ts` - 状态管理
- `src/utils/projectSettings.ts` - 项目设置
- `src/utils/sessionStorage.ts` - 会话存储
- `PROJECT_MANAGEMENT_ANALYSIS.md` - 设计分析

## 📝 示例代码

### 完整工作流程

```typescript
import { initState, getProjectRoot } from './src/bootstrap/state.js';
import { initProjectSettings, getSettings } from './src/utils/projectSettings.js';
import { createSession, addMessage, listSessions } from './src/utils/sessionStorage.js';

// 1. 初始化
initState(process.cwd());
initProjectSettings();

// 2. 获取设置
const settings = getSettings();
console.log(`使用模型：${settings.model}`);

// 3. 创建会话
const session = createSession('新项目');

// 4. 添加消息
addMessage(session.id, {
  role: 'user',
  content: '帮我创建一个新项目'
});

// 5. 列出会话
const sessions = listSessions();
console.log(`共有 ${sessions.length} 个会话`);
```

---

_最后更新：2026-04-07_
_参考：claude-code-learning source/src_
