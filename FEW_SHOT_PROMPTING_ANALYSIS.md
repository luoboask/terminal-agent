# 📖 原始源码中的 Few-Shot Prompting 分析

**分析时间**: 2026-04-07 00:15  
**源码位置**: `/tmp/claude-code-learning/source/src/tools/AgentTool/prompt.ts`

---

## 🔍 Few-Shot Prompting 实现

### 位置

**文件**: `AgentTool/prompt.ts`  
**函数**: `getPrompt()`  
**行数**: 约 115-190 行

---

## 📋 示例结构

### 示例类型

原始源码使用**XML 标签格式**的示例：

```typescript
const forkExamples = `Example usage:

<example>
user: "What's left on this branch before we can ship?"
assistant: <thinking>Forking this — it's a survey question...</thinking>
${AGENT_TOOL_NAME}({
  name: "ship-audit",
  description: "Branch ship-readiness audit",
  prompt: "Audit what's left..."
})
assistant: Ship-readiness audit running.
</example>

<example>
user: "so is the gate wired up or not"
assistant: Still waiting on the audit...
</example>

<example>
user: "Can you get a second opinion..."
assistant: <thinking>I'll ask the code-reviewer agent...</thinking>
${AGENT_TOOL_NAME}({
  name: "migration-review",
  subagent_type: "code-reviewer",
  prompt: "Review migration 0042..."
})
</example>
`
```

---

## 🎯 示例设计原则

### 1. 场景覆盖

**3 种典型场景**:
1. **Fork 场景** - 分叉任务给子代理
2. **等待场景** - 等待子代理完成
3. **独立评审** - 使用特定类型的子代理

---

### 2. 示例格式

**XML 标签结构**:
```xml
<example>
user: "用户输入"
assistant: <thinking>思考过程</thinking>
assistant: 工具调用
assistant: 响应
</example>
```

**优点**:
- ✅ 结构清晰
- ✅ 易于解析
- ✅ 包含思考过程
- ✅ 展示完整流程

---

### 3. 思考过程展示

**示例中包含 `<thinking>` 标签**:
```typescript
assistant: <thinking>
Forking this — it's a survey question. 
I want the punch list, not the git output in my context.
</thinking>
```

**目的**:
- 展示 AI 的决策过程
- 解释为什么选择这个工具
- 帮助用户理解 AI 行为

---

### 4. 注释说明

**示例中包含 `<commentary>` 标签**:
```typescript
<commentary>
Turn ends here. The coordinator knows nothing about the findings yet. 
What follows is a SEPARATE turn — the notification arrives from outside, 
as a user-role message. It is not something the coordinator writes.
</commentary>
```

**目的**:
- 解释示例的关键点
- 说明注意事项
- 提供额外上下文

---

## 📊 示例内容分析

### 示例 1: Fork 审计任务

**场景**: 用户询问分支是否可以发布

**AI 行为**:
1. 思考：这是一个调查性问题，需要清单而不是详细输出
2. 行动：Fork 给 ship-audit 代理
3. 响应：告知用户审计正在进行

**关键点**:
- ✅ 展示何时使用 Fork
- ✅ 展示如何写 Fork 提示
- ✅ 展示等待结果的行为

---

### 示例 2: 等待结果

**场景**: 用户在等待时询问结果

**AI 行为**:
1. 不编造结果
2. 告知用户仍在等待
3. 提供状态更新

**关键点**:
- ✅ 展示不编造结果
- ✅ 展示如何等待
- ✅ 展示状态更新

---

### 示例 3: 独立评审

**场景**: 用户要求第二意见

**AI 行为**:
1. 思考：使用 code-reviewer 代理获得独立意见
2. 行动：启动子代理，提供完整上下文
3. 响应：告知用户已启动评审

**关键点**:
- ✅ 展示使用特定类型的子代理
- ✅ 展示如何写完整提示
- ✅ 展示独立评审的价值

---

## 💡 设计原则总结

### 1. 真实性

**示例必须真实可信**:
- ✅ 展示真实的用户输入
- ✅ 展示合理的 AI 响应
- ✅ 包含思考过程和注释

---

### 2. 完整性

**示例展示完整流程**:
- ✅ 用户输入
- ✅ AI 思考
- ✅ 工具调用
- ✅ AI 响应
- ✅ 后续行为

---

### 3. 多样性

**覆盖不同场景**:
- ✅ Fork 场景
- ✅ 等待场景
- ✅ 独立评审场景
- ✅ 代码编写场景
- ✅ 问候场景

---

### 4. 教育性

**示例包含教学元素**:
- ✅ `<thinking>` 展示决策
- ✅ `<commentary>` 解释要点
- ✅ 展示最佳实践
- ✅ 展示注意事项

---

## 🔧 在 Source Deploy 中的应用

### 当前缺失

**Source Deploy 目前没有 Few-Shot Examples**:
```typescript
// 当前只有规则描述
const systemPrompt = `
🚨 CRITICAL RULES:
1. MUST use tools...
2. Call each tool ONLY ONCE...
`;
```

---

### 建议添加

**添加 Few-Shot Examples**:
```typescript
const systemPrompt = `
📝 EXAMPLES - Follow this pattern:

<example>
user: 创建文件 test.txt 内容是'Hello'
assistant: 🔧 正在调用工具：file_write
   参数：file_path: test.txt, content: Hello
   ✅ file_write 执行完成
   结果：✅ 文件已创建
</example>

<example>
user: 读取 test.txt 的内容
assistant: 🔧 正在调用工具：file_read
   参数：file_path: test.txt
   ✅ file_read 执行完成
   结果：Hello World
</example>

<example>
user: 编辑 test.txt，把 Hello 改成 Hi
assistant: 🔧 正在调用工具：file_edit
   参数：file_path: test.txt, oldText: Hello, newText: Hi
   ✅ file_edit 执行完成
   结果：文件已编辑
</example>
`;
```

---

## ✅ 总结

### 原始源码的 Few-Shot 设计

| 特点 | 说明 |
|------|------|
| **格式** | XML 标签（`<example>`） |
| **数量** | 3-5 个场景 |
| **内容** | 用户输入 + AI 思考 + 工具调用 + 响应 |
| **注释** | `<thinking>` 和 `<commentary>` |
| **场景** | 覆盖典型使用场景 |

---

### 在 Source Deploy 中的应用

**建议**:
1. ✅ 添加 3-5 个典型场景示例
2. ✅ 使用简洁的格式（不需要 XML）
3. ✅ 包含工具调用过程
4. ✅ 展示正确的行为模式

**预期效果**:
- ✅ AI 更可能调用工具
- ✅ 减少直接返回文本
- ✅ 提高工具调用一致性

---

_分析时间：2026-04-07 00:15_  
_源码位置：AgentTool/prompt.ts_  
_示例数量：3-5 个_  
_格式：XML 标签_
