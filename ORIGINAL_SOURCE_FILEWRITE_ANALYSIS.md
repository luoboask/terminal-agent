# 📖 原始源码 FileWriteTool 实现分析

**分析时间**: 2026-04-07 02:00  
**源码位置**: `/tmp/claude-code-learning/source/src/tools/FileWriteTool/FileWriteTool.ts`

---

## 🎯 原始源码实现

### Schema 定义

```typescript
const inputSchema = lazySchema(() =>
  z.strictObject({
    file_path: z
      .string()
      .describe('The absolute path to the file to write (must be absolute, not relative)'),
    content: z.string().describe('The content to write to the file'),
  }),
)
```

**特点**:
- ✅ `file_path` 必需（必须是绝对路径）
- ✅ `content` 必需（要写入的内容）
- ✅ 严格模式（strictObject）

---

### 核心实现

```typescript
async call({ file_path, content }, context) {
  // 1. 扩展路径（处理 ~ 和相对路径）
  const fullFilePath = expandPath(file_path)
  const dir = dirname(fullFilePath)

  // 2. 确保父目录存在
  await getFsImplementation().mkdir(dir)

  // 3. 文件历史备份（如果启用）
  if (fileHistoryEnabled()) {
    await fileHistoryTrackEdit(...)
  }

  // 4. 检查文件是否被意外修改
  let meta = readFileSyncWithMetadata(fullFilePath)
  if (meta !== null) {
    const lastWriteTime = getFileModificationTime(fullFilePath)
    const lastRead = readFileState.get(fullFilePath)
    if (lastWriteTime > lastRead.timestamp) {
      throw new Error(FILE_UNEXPECTEDLY_MODIFIED_ERROR)
    }
  }

  // 5. 写入文件（保持编码和换行符）
  const enc = meta?.encoding ?? 'utf8'
  writeTextContent(fullFilePath, content, enc, 'LF')

  // 6. 通知 LSP 服务器
  const lspManager = getLspServerManager()
  if (lspManager) {
    lspManager.changeFile(fullFilePath, content)
    lspManager.saveFile(fullFilePath)
  }

  // 7. 计算 git diff（如果启用）
  let gitDiff = await fetchSingleFileGitDiff(fullFilePath)

  // 8. 返回结果
  if (oldContent) {
    return {
      data: {
        type: 'update',
        filePath: file_path,
        content,
        structuredPatch: patch,
        originalFile: oldContent,
        gitDiff,
      },
    }
  } else {
    return {
      data: {
        type: 'create',
        filePath: file_path,
        content,
        structuredPatch: [],
        originalFile: null,
        gitDiff,
      },
    }
  }
}
```

---

## 📊 关键特性

### 1. 路径处理

```typescript
// 扩展路径（处理 ~ 和相对路径）
const fullFilePath = expandPath(file_path)

// backfill 确保是绝对路径
backfillObservableInput(input) {
  if (typeof input.file_path === 'string') {
    input.file_path = expandPath(input.file_path)
  }
}
```

---

### 2. 目录创建

```typescript
// 确保父目录存在
await getFsImplementation().mkdir(dir)
```

**注意**: 目录创建在写入之前，且是同步的（避免并发问题）

---

### 3. 文件历史

```typescript
if (fileHistoryEnabled()) {
  await fileHistoryTrackEdit(
    updateFileHistoryState,
    fullFilePath,
    parentMessage.uuid,
  )
}
```

**功能**: 备份编辑前的内容，支持撤销

---

### 4. 并发检测

```typescript
// 检查文件是否被意外修改
if (meta !== null) {
  const lastWriteTime = getFileModificationTime(fullFilePath)
  const lastRead = readFileState.get(fullFilePath)
  if (lastWriteTime > lastRead.timestamp) {
    throw new Error(FILE_UNEXPECTEDLY_MODIFIED_ERROR)
  }
}
```

**目的**: 防止并发编辑导致数据丢失

---

### 5. 写入文件

```typescript
// 保持编码和换行符
const enc = meta?.encoding ?? 'utf8'
writeTextContent(fullFilePath, content, enc, 'LF')
```

**特点**: 
- 保持原有编码（UTF-8 或其他）
- 统一使用 LF 换行符

---

### 6. LSP 通知

```typescript
const lspManager = getLspServerManager()
if (lspManager) {
  // 通知文件已修改
  lspManager.changeFile(fullFilePath, content)
  // 通知文件已保存
  lspManager.saveFile(fullFilePath)
}
```

**目的**: 让 LSP 服务器更新诊断信息

---

### 7. Git Diff

```typescript
let gitDiff = await fetchSingleFileGitDiff(fullFilePath)
```

**功能**: 计算 git diff，用于显示变更

---

### 8. 返回结果

**创建文件**:
```typescript
return {
  data: {
    type: 'create',
    filePath: file_path,
    content,
    structuredPatch: [],
    originalFile: null,
    gitDiff,
  },
}
```

**更新文件**:
```typescript
return {
  data: {
    type: 'update',
    filePath: file_path,
    content,
    structuredPatch: patch,
    originalFile: oldContent,
    gitDiff,
  },
}
```

---

## 📊 实现对比

| 特性 | 原始源码 | 我们的实现 |
|------|---------|-----------|
| **Schema** | content 必需 | content 可选 |
| **路径处理** | expandPath | resolve |
| **目录创建** | ✅ mkdir | ✅ mkdirSync |
| **文件历史** | ✅ 备份 | ❌ 无 |
| **并发检测** | ✅ 时间戳检查 | ❌ 无 |
| **编码保持** | ✅ 保持原编码 | ⚠️ 固定 UTF-8 |
| **LSP 通知** | ✅ 通知 | ❌ 无 |
| **Git Diff** | ✅ 计算 | ⚠️ 简化版 |
| **权限检查** | ✅ 检查 | ⚠️ 简化版 |

---

## 💡 改进建议

### 方案 1: 保持当前实现（推荐）⭐⭐⭐⭐⭐

**理由**:
- ✅ 简单高效
- ✅ 适合单 Agent 场景
- ✅ 无额外依赖
- ✅ content 可选更灵活

**适用**: 个人使用、快速开发

---

### 方案 2: 参考原始源码（高级）⭐⭐⭐⭐

**改进点**:
1. 添加文件历史备份
2. 添加并发检测
3. 添加 LSP 通知
4. 添加 Git Diff 计算
5. 添加权限检查

**优点**:
- ✅ 更健壮
- ✅ 支持并发
- ✅ 功能完整

**缺点**:
- ❌ 复杂度增加
- ❌ 需要额外依赖
- ❌ 性能开销

**适用**: 多用户、生产环境

---

### 方案 3: 混合方案（最佳）⭐⭐⭐⭐⭐

**思路**: 保持简单实现，添加关键特性

```typescript
// 1. 添加简单的文件历史
const backupPath = filePath + '.backup'
if (existsSync(filePath)) {
  copyFileSync(filePath, backupPath)
}

// 2. 简单的并发检测
const mtime = statSync(filePath).mtimeMs
if (lastReadMtime && mtime > lastReadMtime) {
  throw new Error('File was modified')
}

// 3. 保持 UTF-8 编码
writeFileSync(filePath, content, 'utf-8')
```

---

## ✅ 总结

### 原始源码实现

- ✅ content 必需
- ✅ 文件历史备份
- ✅ 并发检测
- ✅ LSP 通知
- ✅ Git Diff
- ✅ 权限检查
- ✅ 编码保持

### 我们的实现

- ✅ content 可选（更灵活）
- ✅ 目录创建
- ✅ 简化 diff
- ❌ 无文件历史
- ❌ 无并发检测
- ❌ 无 LSP 通知
- ❌ 无 Git Diff
- ⚠️ 固定 UTF-8

### 推荐方案

**保持当前实现**（content 可选 + 简单实现）

**理由**:
1. ✅ 简单高效
2. ✅ 适合当前场景
3. ✅ content 可选更灵活
4. ✅ 无额外依赖

**如需生产级功能**，可以参考原始源码添加：
- 文件历史备份
- 并发检测
- LSP 通知
- Git Diff

---

_分析时间：2026-04-07 02:00_  
_原始源码：复杂完整_  
_我们的实现：简单灵活_  
_推荐：保持当前实现_
