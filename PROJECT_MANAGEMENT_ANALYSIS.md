# claude-code-learning 项目管理分析

## 📋 概述

claude-code-learning (source/src) 使用多层次的项目管理架构，包括：

1. **项目根目录 (projectRoot)** - 项目身份标识
2. **工作目录 (originalCwd)** - 文件操作基准
3. **会话目录 (sessionProjectDir)** - 会话存储位置
4. **设置系统 (settings)** - 项目配置管理

## 🏗️ 架构设计

### 1️⃣ 项目根目录 (projectRoot)

**定义：**
```typescript
// src/bootstrap/state.ts
let STATE = {
  projectRoot: string,  // 稳定项目根目录
  originalCwd: string,  // 原始工作目录
  sessionProjectDir: string | null,  // 会话项目目录
}
```

**特点：**
- 启动时设置一次（包括 --worktree 标志）
- 用于项目身份标识（历史、技能、会话）
- 不用于文件操作
- 跨会话保持稳定

**获取方法：**
```typescript
export function getProjectRoot(): string {
  return STATE.projectRoot
}

export function setProjectRoot(cwd: string): void {
  STATE.projectRoot = cwd.normalize('NFC')
}
```

### 2️⃣ 工作目录管理

**原始工作目录：**
```typescript
export function getOriginalCwd(): string {
  return STATE.originalCwd
}

export function setOriginalCwd(cwd: string): void {
  STATE.originalCwd = cwd.normalize('NFC')
}
```

**会话项目目录：**
```typescript
export function setSessionProjectDir(projectDir: string | null): void {
  STATE.sessionProjectDir = projectDir
}

export function getSessionProjectDir(): string | null {
  return STATE.sessionProjectDir
}
```

### 3️⃣ 项目设置系统

**设置层级：**
```
1. 全局设置 (~/.claude/settings.json)
2. 项目设置 (<projectRoot>/.claude/settings.json)
3. 会话设置 (<sessionDir>/settings.json)
4. MDM 设置 (企业强制设置)
```

**设置管理：**
```typescript
// src/utils/settings/settings.ts
export function getSettings(): Settings {
  // 合并多层级设置
}

export function updateSettings(changes: Partial<Settings>): void {
  // 更新设置
}

export function getProjectSettings(): ProjectSettings {
  // 获取项目特定设置
}
```

### 4️⃣ 工作树 (Worktree) 支持

**Git 工作树管理：**
```typescript
// src/utils/worktreeModeEnabled.ts
export function isWorktreeModeEnabled(): boolean {
  // 检测是否在 git worktree 模式
}

export function getWorktreePaths(): string[] {
  // 获取所有工作树路径
}
```

**工作树切换：**
```typescript
// src/tools/EnterWorktreeTool.ts
export const EnterWorktreeTool = buildTool({
  name: 'enter_worktree',
  description: '切换到 git worktree',
  async call({ worktreePath }, context) {
    // 切换工作树
    setProjectRoot(worktreePath)
  },
})
```

## 📊 项目存储结构

```
<projectRoot>/
├── .claude/
│   ├── settings.json        # 项目设置
│   ├── skills/              # 项目技能
│   ├── history/             # 会话历史
│   └── sessions/            # 会话存储
├── .source-deploy-tasks/    # 任务存储（我们的实现）
└── ...项目文件
```

## 🔧 关键设计原则

### 1️⃣ 项目身份稳定

```typescript
// 项目根目录一旦设置，不会改变
STATE.projectRoot = resolvedCwd  // 启动时设置

// 即使切换工作目录，项目身份不变
process.chdir('/tmp')  // 文件操作
getProjectRoot()       // 仍返回原始项目根目录
```

### 2️⃣ 会话与项目分离

```typescript
// 会话可以跨项目
setSessionProjectDir('/other/project')  // 会话存储在其他项目
getProjectRoot()                        // 但项目身份不变
```

### 3️⃣ 设置继承

```
全局设置
    ↓ (继承)
项目设置
    ↓ (继承)
会话设置
    ↓ (覆盖)
MDM 设置 (最高优先级)
```

### 4️⃣ 跨项目恢复

```typescript
// src/utils/crossProjectResume.ts
export async function resumeSession(
  sessionId: string,
  projectDir?: string
): Promise<Session> {
  // 可以从其他项目恢复会话
  setSessionProjectDir(projectDir)
  return loadSession(sessionId)
}
```

## 📁 我们的实现对比

| 特性 | claude-code-learning | source-deploy | 状态 |
|------|---------------------|---------------|------|
| 项目根目录 | ✅ projectRoot | ❌ 未实现 | ⚠️ |
| 工作目录管理 | ✅ 3 层目录 | ❌ 未实现 | ⚠️ |
| 项目设置 | ✅ 多层级 | ❌ 未实现 | ⚠️ |
| 工作树支持 | ✅ Git worktree | ❌ 未实现 | ⚠️ |
| 跨项目恢复 | ✅ | ❌ 未实现 | ⚠️ |
| 任务系统 | ✅ | ✅ taskStorageV2 | ✅ |
| 会话存储 | ✅ JSONL | ❌ 未实现 | ⚠️ |

## 💡 建议实现

### 短期（本周）
1. **项目根目录管理**
   ```typescript
   // src/bootstrap/state.ts
   let projectRoot: string
   
   export function getProjectRoot(): string
   export function setProjectRoot(cwd: string): void
   ```

2. **项目设置**
   ```typescript
   // src/utils/projectSettings.ts
   export function getProjectSettings(): ProjectSettings
   export function updateProjectSettings(changes: Partial<ProjectSettings>): void
   ```

### 中期（本月）
3. **工作目录管理**
   ```typescript
   export function getOriginalCwd(): string
   export function getSessionProjectDir(): string | null
   ```

4. **会话存储**
   ```
   .source-deploy/
   └── sessions/
       └── <sessionId>.jsonl
   ```

### 长期（下月）
5. **跨项目恢复**
6. **Git worktree 支持**
7. **MDM 设置支持**

## 🔗 参考文件

- [src/bootstrap/state.ts](/tmp/claude-code-learning/source/src/bootstrap/state.ts) - 状态管理
- [src/utils/settings/settings.ts](/tmp/claude-code-learning/source/src/utils/settings/settings.ts) - 设置系统
- [src/utils/crossProjectResume.ts](/tmp/claude-code-learning/source/src/utils/crossProjectResume.ts) - 跨项目恢复
- [src/tools/EnterWorktreeTool.ts](/tmp/claude-code-learning/source/src/tools/EnterWorktreeTool.ts) - 工作树切换

---

_分析日期：2026-04-07_
_参考版本：claude-code-learning source/src_
