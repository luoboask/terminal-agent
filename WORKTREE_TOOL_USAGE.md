# WorktreeTool 使用指南

## 📋 概述

`WorktreeTool` 是 Git Worktree 管理工具，支持：

- **列出** - 查看所有 worktree
- **创建** - 创建新的 worktree
- **切换** - 切换到指定 worktree
- **删除** - 删除 worktree
- **清理** - 清理无效的 worktree

## 🚀 使用示例

### 1️⃣ 列出所有 Worktree

```typescript
worktree({ action: 'list' })
```

**输出：**
```
📋 Worktree 列表

✅ /Users/dhr/projects/my-app (refs/heads/main)
⚪ /Users/dhr/projects/my-app-feature (refs/heads/feature-branch)
```

### 2️⃣ 创建 Worktree

```typescript
// 创建新分支的 worktree
worktree({
  action: 'create',
  worktreePath: '../my-app-feature',
  branch: 'feature-branch'
})

// 创建与当前分支相同的 worktree
worktree({
  action: 'create',
  worktreePath: '../my-app-test'
})

// 强制创建（如果路径已存在）
worktree({
  action: 'create',
  worktreePath: '../my-app-feature',
  branch: 'feature-branch',
  force: true
})
```

**输出：**
```
✅ Worktree 已创建

📁 路径：/Users/dhr/projects/my-app-feature
🌿 分支：feature-branch
```

### 3️⃣ 切换 Worktree

```typescript
worktree({
  action: 'switch',
  worktreePath: '../my-app-feature'
})
```

**输出：**
```
✅ 已切换到 Worktree

📁 路径：/Users/dhr/projects/my-app-feature
🏠 原路径：/Users/dhr/projects/my-app

💡 提示：项目根目录已更新，后续操作将在此 worktree 中进行。
```

### 4️⃣ 删除 Worktree

```typescript
// 删除 worktree
worktree({
  action: 'delete',
  worktreePath: '../my-app-feature'
})

// 强制删除（如果有未提交的更改）
worktree({
  action: 'delete',
  worktreePath: '../my-app-feature',
  force: true
})
```

**输出：**
```
✅ Worktree 已删除

📁 路径：/Users/dhr/projects/my-app-feature
```

### 5️⃣ 清理无效 Worktree

```typescript
worktree({ action: 'prune' })
```

**输出：**
```
✅ 已清理无效的 Worktree

没有需要清理的 worktree
```

## 📊 完整工作流程

### 场景 1：多分支并行开发

```typescript
// 1. 列出当前 worktree
worktree({ action: 'list' })
// ✅ /projects/my-app (main)

// 2. 创建 feature 分支的 worktree
worktree({
  action: 'create',
  worktreePath: '../my-app-feature',
  branch: 'feature-login'
})

// 3. 切换到 feature worktree
worktree({
  action: 'switch',
  worktreePath: '../my-app-feature'
})

// 4. 在 feature worktree 中工作...
// ...开发新功能...

// 5. 切换回主 worktree
worktree({
  action: 'switch',
  worktreePath: '/projects/my-app'
})

// 6. 在主 worktree 中继续工作...
```

### 场景 2：代码审查

```typescript
// 1. 创建审查分支的 worktree
worktree({
  action: 'create',
  worktreePath: '../my-app-review',
  branch: 'review/pr-123'
})

// 2. 切换到审查 worktree
worktree({
  action: 'switch',
  worktreePath: '../my-app-review'
})

// 3. 审查代码...

// 4. 审查完成后删除 worktree
worktree({
  action: 'delete',
  worktreePath: '../my-app-review'
})
```

## 🔧 API 参考

### 输入参数

```typescript
interface WorktreeInput {
  /** 操作类型 */
  action: 'list' | 'create' | 'switch' | 'delete' | 'prune';
  
  /** Worktree 路径（create/switch/delete 必需） */
  worktreePath?: string;
  
  /** 分支名称（create 可选） */
  branch?: string;
  
  /** 是否强制操作（create/delete 可选） */
  force?: boolean;
}
```

### 输出格式

**成功：**
```
✅ 操作成功

📁 路径：...
🌿 分支：...
```

**失败：**
```
❌ 操作失败

📁 路径：...

❌ 错误：...
```

## 💡 最佳实践

### 1. 命名约定

```bash
# 好的命名
../my-app-feature      # 功能开发
../my-app-hotfix       # 紧急修复
../my-app-review       # 代码审查
../my-app-experiment   # 实验性功能

# 避免的命名
../feature             # 太模糊
../test                # 容易混淆
../tmp                 # 临时目录
```

### 2. 分支管理

```typescript
// ✅ 为每个 worktree 创建独立分支
worktree({
  action: 'create',
  worktreePath: '../my-app-feature',
  branch: 'feature-login'
})

// ❌ 避免多个 worktree 使用同一分支
// 可能导致冲突
```

### 3. 清理策略

```typescript
// 定期清理不再使用的 worktree
worktree({ action: 'list' })
// 检查哪些 worktree 不再需要

worktree({
  action: 'delete',
  worktreePath: '../my-app-old-feature'
})

// 清理无效的 worktree 引用
worktree({ action: 'prune' })
```

### 4. 项目根目录管理

```typescript
// 切换 worktree 会自动更新项目根目录
worktree({
  action: 'switch',
  worktreePath: '../my-app-feature'
})

// 验证当前项目根目录
import { getProjectRoot } from './src/bootstrap/state.js';
console.log(getProjectRoot());  // /Users/dhr/projects/my-app-feature
```

## ⚠️ 注意事项

### 1. Git 要求

- 必须在 Git 仓库中使用
- Git 版本建议 2.5+（支持 worktree）

### 2. 路径要求

- worktree 路径不能在主仓库内
- 建议使用相对路径（如 `../my-app-feature`）

### 3. 分支限制

- 不能同时 checkout 同一分支到多个 worktree
- 主仓库的 HEAD 分支不能在 worktree 中 checkout

### 4. 文件锁

- 某些文件（如 `.git/index`）在每个 worktree 中是独立的
- 某些文件（如 `.git/config`）是共享的

## 🔗 相关资源

- [Git Worktree 官方文档](https://git-scm.com/docs/git-worktree)
- [Git Worktree 教程](https://www.git-tower.com/learn/git/faq/git-worktree)
- [PROJECT_MANAGEMENT_USAGE.md](PROJECT_MANAGEMENT_USAGE.md) - 项目管理使用指南

---

_最后更新：2026-04-07_
