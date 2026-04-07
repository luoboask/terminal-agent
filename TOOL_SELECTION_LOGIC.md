# 🤖 工具选择逻辑 - AI 如何选择工具

**创建时间**: 2026-04-06 22:36

---

## 📊 工具选择机制

### 当前实现

**AI 没有自动优先级**，工具选择完全基于：

1. **LLM 的判断** - AI 根据用户请求决定使用哪个工具
2. **工具名称匹配** - AI 看到工具列表后选择合适的
3. **工具描述** - 描述更准确的工具更容易被选中

---

## 🔍 实际工作流程

### 步骤 1: 工具列表发送给 LLM

```typescript
// QueryEngine 将所有注册的工具发送给 LLM
const tools = QwenProvider.buildTools(this.config.toolRegistry);

// 工具列表包含：
[
  { name: 'task_create', description: '创建任务（简化版）' },
  { name: 'task_create_enhanced', description: '创建任务（增强版）- 支持完整字段和 Hooks' },
  { name: 'task_update', description: '更新任务（简化版）' },
  { name: 'task_update_enhanced', description: '更新任务（增强版）- 支持完整字段和 Hooks' },
  // ... 其他工具
]
```

---

### 步骤 2: LLM 决定使用哪个工具

```
用户：创建一个任务：完成首页开发，优先级 high

LLM 思考：
- 用户提到了"优先级"
- task_create 不支持优先级字段
- task_create_enhanced 支持优先级字段
- 选择 task_create_enhanced ✅
```

---

### 步骤 3: 执行工具

```typescript
const tool = this.config.toolRegistry.get('task_create_enhanced');
await tool.execute({ subject: '完成首页开发', priority: 'high' });
```

---

## 🎯 当前优先级规则

### 规则 1: LLM 自主选择 ⭐⭐⭐⭐⭐

**AI 会根据以下因素选择**：

1. **功能匹配度**
   - 用户需求包含"优先级" → 选择支持优先级的工具
   - 用户需求包含"归档" → 选择支持归档的工具

2. **工具描述**
   - 描述更详细的工具更容易被选中
   - 增强版描述通常更长更详细

3. **字段匹配**
   - 用户提供的字段在哪个工具中 → 选择哪个工具

---

### 规则 2: 无硬编码优先级

```typescript
// ❌ 没有这样的代码
if (userRequest.includes('enhanced')) {
  useEnhancedVersion();  // 不存在
}

// ✅ 实际代码
const tool = registry.get(toolName);  // 完全基于 LLM 的选择
```

---

## 📋 实际测试结果

### 测试 1: 简单任务

```bash
❯ 创建一个任务：完成首页开发

AI 选择：task_create 或 task_create_enhanced
原因：两个工具都能完成，AI 可能随机选择
```

---

### 测试 2: 带优先级的任务

```bash
❯ 创建一个任务：完成首页开发，优先级 high

AI 选择：task_create_enhanced ✅
原因：只有增强版支持 priority 字段
```

---

### 测试 3: 带归档的任务

```bash
❯ 完成任务 task_xxx，归档

AI 选择：task_complete_enhanced ✅
原因：只有增强版支持 archive 字段
```

---

### 测试 4: 配置管理

```bash
❯ 设置配置：database.host 为 localhost

AI 选择：config_enhanced ✅
原因：只有增强版有配置管理功能
```

---

## 💡 如何影响 AI 的选择

### 方法 1: 明确指定工具 ⭐⭐⭐⭐⭐

```bash
# 明确使用增强版
❯ 用 task_create_enhanced 创建任务：xxx

# 明确使用简化版
❯ 用 task_create 创建任务：xxx
```

---

### 方法 2: 使用增强版特有的功能 ⭐⭐⭐⭐

```bash
# 提到"优先级"→ AI 会选择增强版
❯ 创建一个任务：xxx，优先级 high

# 提到"归档"→ AI 会选择增强版
❯ 完成任务 task_xxx，归档

# 提到"元数据"→ AI 会选择增强版
❯ 创建任务：xxx，元数据 {"key": "value"}
```

---

### 方法 3: 修改工具描述 ⭐⭐⭐

```typescript
// 增强版描述更详细
readonly description = '创建任务（增强版）- 支持完整字段和 Hooks - 推荐使用';

// 简化版描述较简单
readonly description = '创建任务（简化版）';
```

**效果**: AI 更容易选择描述更详细的工具

---

## 🔧 如何添加优先级（如果需要）

### 方案 1: 修改工具描述（推荐）

```typescript
// 增强版添加"推荐使用"标记
export class TaskCreateEnhancedTool extends BaseTool {
  readonly name = 'task_create_enhanced';
  readonly description = '【推荐】创建任务（增强版）- 支持优先级、元数据、Hooks';
}

// 简化版保持简单
export class TaskCreateTool extends BaseTool {
  readonly name = 'task_create';
  readonly description = '创建任务（简化版）- 基础功能';
}
```

---

### 方案 2: 添加工具优先级标记

```typescript
// 在工具类中添加优先级标记
export class TaskCreateEnhancedTool extends BaseTool {
  readonly priority = 10;  // 高优先级
}

export class TaskCreateTool extends BaseTool {
  readonly priority = 1;   // 低优先级
}

// 修改 ToolRegistry 的 list 方法
list(): BaseTool<any>[] {
  return Array.from(this.tools.values())
    .sort((a, b) => (b.priority || 0) - (a.priority || 0));
}
```

---

### 方案 3: 移除简化版（不推荐）

```typescript
// ❌ 不推荐：直接不注册简化版
// registry.register(new TaskCreateTool());  // 注释掉

// ✅ 推荐：保留简化版作为备选
registry.register(new TaskCreateTool());
registry.register(new TaskCreateEnhancedTool());
```

---

## 📊 当前行为总结

### AI 的选择逻辑

```
用户请求
  ↓
LLM 分析需求
  ↓
查看工具列表（包含简化版和增强版）
  ↓
选择最匹配的工具
  ├─ 如果需求简单 → 可能选择简化版
  ├─ 如果需求复杂 → 选择增强版
  └─ 如果提到特定字段 → 选择支持该字段的工具
  ↓
执行工具
```

---

### 实际表现

| 用户需求 | AI 选择 | 原因 |
|---------|--------|------|
| "创建任务" | 随机 | 两个都能用 |
| "创建任务，优先级 high" | task_create_enhanced ✅ | 只有增强版支持 priority |
| "完成任务，归档" | task_complete_enhanced ✅ | 只有增强版支持 archive |
| "设置配置" | config_enhanced ✅ | 只有增强版有配置功能 |
| "获取网页" | 随机 | 两个都能用（但增强版功能更多） |

---

## ✅ 总结

### 当前有优先级吗？

**❌ 没有硬编码优先级**

AI 完全基于：
- 功能匹配度
- 工具描述
- 字段支持

自主选择工具

---

### 需要添加优先级吗？

**推荐方案**：修改工具描述

```typescript
// 增强版描述添加"【推荐】"标记
readonly description = '【推荐】创建任务（增强版）- 支持优先级、元数据、Hooks';
```

**效果**：AI 会更倾向于选择增强版

---

### 用户如何确保使用增强版？

**方法 1**：明确指定
```bash
❯ 用 task_create_enhanced 创建任务
```

**方法 2**：使用增强版特有功能
```bash
❯ 创建任务：xxx，优先级 high
```

---

_创建时间：2026-04-06 22:36_  
_当前优先级：无（AI 自主选择）_  
_推荐方案：修改工具描述添加"【推荐】"标记_
