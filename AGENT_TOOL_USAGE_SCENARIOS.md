# 📖 原始源码中 AgentTool 的调用场景

**分析时间**: 2026-04-07 00:20  
**源码位置**: `tools/AgentTool/prompt.ts` + built-in agents

---

## 🎯 AgentTool 调用场景

### 核心原则

**原文**:
> "Use this agent when you need to..."

**调用 AgentTool 的核心条件**:
1. **任务复杂** - 需要多步骤执行
2. **专业化** - 需要特定领域的专业知识
3. **并行工作** - 可以与其他任务并行执行
4. **后台运行** - 不需要立即得到结果

---

## 📋 内置 Agent 类型及使用场景

### 1. general-purpose (通用代理)

**whenToUse**:
> "General-purpose agent for researching complex questions, searching for code, and executing multi-step tasks. When you are searching for a file and are not confident that you will find the right match in the first few tries use this agent to perform the search for you."

**调用场景**:
- ✅ 研究复杂问题
- ✅ 搜索代码（不确定在哪里）
- ✅ 执行多步骤任务
- ✅ 需要多次尝试的搜索

**示例**:
```typescript
AgentTool({
  description: "Search for authentication code",
  subagent_type: "general-purpose",
  prompt: "Find all files related to authentication in this codebase..."
})
```

---

### 2. Explore (探索代理)

**whenToUse**:
> "Software exploration agent for investigating codebases and understanding complex systems."

**调用场景**:
- ✅ 探索陌生代码库
- ✅ 理解复杂系统
- ✅ 调查代码结构
- ✅ 不需要修改代码

**特点**:
- ❌ 不允许修改文件
- ❌ 不允许调用其他 Agent
- ✅ 只能读取和分析

---

### 3. Plan (计划代理)

**whenToUse**:
> "Software architect agent for designing implementation plans. Use this when you need to plan the implementation strategy for a task."

**调用场景**:
- ✅ 设计实现方案
- ✅ 制定分步计划
- ✅ 考虑架构权衡
- ✅ 识别关键文件

**特点**:
- ❌ 不允许修改文件
- ❌ 不允许调用其他 Agent
- ✅ 只返回计划

---

### 4. claude-code-guide (指南代理)

**whenToUse**:
> "Use this agent when the user asks questions about: (1) Claude Code features, hooks, slash commands; (2) Claude Agent SDK; (3) Claude API usage."

**调用场景**:
- ✅ 用户询问 Claude Code 功能
- ✅ 询问如何构建自定义 Agent
- ✅ 询问 Claude API 使用
- ✅ 需要官方文档解答

**示例**:
```typescript
AgentTool({
  description: "Question about MCP servers",
  subagent_type: "claude-code-guide",
  prompt: "How do I configure MCP servers in Claude Code?"
})
```

---

### 5. verification (验证代理)

**whenToUse**:
> "Use this agent to verify that changes are correct and complete. Run in background to check work while you continue with other tasks."

**调用场景**:
- ✅ 验证修改是否正确
- ✅ 检查是否遗漏
- ✅ 后台运行验证
- ✅ 并行工作

**特点**:
- ✅ 后台运行
- ✅ 完成后通知
- ✅ 不阻塞主线程

---

## 🔧 调用 AgentTool 的时机

### 何时调用 AgentTool

**原文明确说明**:

1. **复杂任务**:
   > "When the task requires multiple steps or specialized knowledge"

2. **并行工作**:
   > "When you have genuinely independent work to do in parallel"

3. **专业化需求**:
   > "When you need specialized expertise (code review, testing, etc.)"

4. **后台任务**:
   > "Use background when you have other work to do while the agent runs"

---

### 何时**不**调用 AgentTool

**原文说明**:

1. **简单任务**:
   > "Don't delegate simple tasks that you can complete yourself"

2. **需要立即结果**:
   > "Don't spawn an agent if you need the results immediately"

3. **任务不明确**:
   > "Don't spawn an agent without a clear task description"

---

## 📖 调用示例

### 示例 1: 代码审查

```typescript
// 场景：需要独立审查代码
AgentTool({
  name: "migration-review",
  description: "Independent migration review",
  subagent_type: "code-reviewer",
  prompt: "Review migration 0042_user_schema.sql for safety. " +
          "Context: we're adding a NOT NULL column to a 50M-row table. " +
          "Report: is this safe, and if not, what specifically breaks?"
})
```

---

### 示例 2: 并行研究

```typescript
// 场景：可以并行研究的独立问题
AgentTool({
  description: "Research authentication options",
  subagent_type: "general-purpose",
  prompt: "Research OAuth2 vs JWT for our use case...",
  run_in_background: true  // 后台运行
})
```

---

### 示例 3: Fork 自己

```typescript
// 场景：调查性问题，不需要保留中间结果
AgentTool({
  name: "ship-audit",
  description: "Branch ship-readiness audit",
  // 不指定 subagent_type = Fork 自己
  prompt: "Audit what's left before this branch can ship..."
})
```

---

## 🎯 Fork vs Spawn 的区别

### Fork (分叉自己)

**何时使用**:
> "Fork yourself when the intermediate tool output isn't worth keeping in your context."

**特点**:
- ✅ 继承完整上下文
- ✅ 共享 prompt 缓存
- ✅ 适合调查性问题
- ❌ 不指定 subagent_type

**示例**:
```typescript
AgentTool({
  name: "research-task",
  // 没有 subagent_type = Fork
  prompt: "Research this open-ended question..."
})
```

---

### Spawn (创建新代理)

**何时使用**:
> "Spawn a specialized agent when you need specific expertise."

**特点**:
- ❌ 从零开始（无上下文）
- ✅ 专业化知识
- ✅ 完整提示
- ✅ 指定 subagent_type

**示例**:
```typescript
AgentTool({
  subagent_type: "code-reviewer",  // 指定类型
  prompt: "Review this code..."  // 需要完整提示
})
```

---

## 📊 调用决策树

```
需要帮助？
  │
  ├─ 简单任务 → 自己完成
  │
  ├─ 复杂任务？
  │    │
  │    ├─ 需要专业知识？ → Spawn 专业代理
  │    │
  │    ├─ 调查性问题？ → Fork 自己
  │    │
  │    └─ 多步骤任务？ → Spawn 通用代理
  │
  └─ 可以并行？
       │
       ├─ 是 → 后台运行 (run_in_background: true)
       │
       └─ 否 → 前台运行 (默认)
```

---

## 💡 最佳实践

### 1. 写提示的原则

**原文**:
> "Brief the agent like a smart colleague who just walked into the room"

**要点**:
- ✅ 解释目标和原因
- ✅ 描述已尝试的方法
- ✅ 提供足够上下文
- ❌ 不要只给狭窄指令

---

### 2. 不要委托理解

**原文**:
> "Never delegate understanding."

**错误示例**:
```typescript
// ❌ 错误：委托理解
"based on your findings, fix the bug"
```

**正确示例**:
```typescript
// ✅ 正确：包含理解
"Change line 42 in src/auth.ts from X to Y because..."
```

---

### 3. 后台任务使用

**原文**:
> "When an agent runs in the background, you will be automatically notified when it completes — do NOT sleep, poll, or proactively check on its progress."

**要点**:
- ✅ 设置 run_in_background: true
- ✅ 继续其他工作
- ❌ 不要轮询进度
- ❌ 不要主动检查

---

## ✅ 总结

### 调用 AgentTool 的场景

| 场景 | 推荐操作 |
|------|---------|
| **复杂问题** | Spawn general-purpose |
| **专业需求** | Spawn 专业代理 |
| **调查研究** | Fork 自己 |
| **代码审查** | Spawn code-reviewer |
| **并行工作** | 后台运行 |
| **简单任务** | 自己完成 |

---

### 关键要点

1. **明确任务描述** - 提供完整上下文
2. **选择正确类型** - Fork vs Spawn
3. **合理使用后台** - 真正独立的工作
4. **不要委托理解** - 包含你的理解
5. **等待通知** - 不要轮询进度

---

_分析时间：2026-04-07 00:20_  
_内置 Agent 类型：6+ 个_  
_调用场景：明确定义_  
_最佳实践：文档完善_
