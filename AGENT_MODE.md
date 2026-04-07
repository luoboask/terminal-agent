# 🤖 Source Deploy - Agent 模式对话

**更新时间**: 2026-04-06 19:06  
**核心特点**: **不是问答，是代理执行**

---

## 💬 两种对话模式对比

### 模式 A: 传统问答（Chatbot）

```
用户："怎么创建文件？"
AI: "你可以使用 echo 命令：echo '内容' > 文件名"

用户："grep 怎么用？"
AI: "grep 的用法是：grep [选项] 模式 文件"
```

**特点**:
- ❌ 只给建议，不执行
- ❌ 需要用户自己动手
- ❌ 像搜索引擎 + 文档

---

### 模式 B: Agent 模式（Source Deploy）✅

```
用户："创建文件 test.txt 内容是'Hello'"
AI: [自动调用 file_write 工具]
    ✅ 文件已创建！

用户："搜索代码中的 TODO"
AI: [自动调用 grep 工具]
    ✅ 找到 5 个匹配...
```

**特点**:
- ✅ **主动执行** - 不只是说，直接做
- ✅ **工具调用** - 自动选择正确的工具
- ✅ **多步协作** - 复杂任务分解执行
- ✅ **结果反馈** - 清晰的执行报告

---

## 🎯 Agent 模式的核心特征

### 1. 意图理解 → 工具选择

```
用户："把 config.json 里的 debug 改成 false"

Agent 思考过程:
🧠 理解意图：修改配置文件
🧠 分析任务：需要读取 → 编辑 → 写入
🧠 选择工具：file_read → file_edit → (自动完成)
🧠 执行：调用 file_edit 工具
✅ 完成：config.json 已更新
```

**不是**:
```
❌ "你可以用 sed 命令：sed -i 's/true/false/' config.json"
```

---

### 2. 自主决策

```
用户："这个项目有多少个 TypeScript 文件？"

Agent 决策:
1. 需要查找 .ts 文件 → 选择 glob 工具
2. 需要统计数量 → 计算结果
3. 返回报告

✅ 找到 15 个 TypeScript 文件：
   - src/index.ts
   - src/utils.ts
   ...
```

**不是**:
```
❌ "你可以运行：find . -name '*.ts' | wc -l"
```

---

### 3. 多步骤执行

```
用户："创建一个新的 Node.js 项目"

Agent 执行计划:
Step 1: 创建目录 my-project
Step 2: 初始化 package.json (npm init -y)
Step 3: 创建 src 目录
Step 4: 创建 index.ts 文件
Step 5: 创建 README.md

✅ 完成！项目结构已创建：
my-project/
├── package.json
├── README.md
└── src/
    └── index.ts
```

**不是**:
```
❌ "你需要执行以下命令：
     1. mkdir my-project
     2. cd my-project
     3. npm init -y
     ..."
```

---

### 4. 错误处理和恢复

```
用户："删除 /root/important.txt"

Agent 检测:
⚠️ 权限不足：无法删除系统文件
💡 建议：这个文件可能很重要，确定要删除吗？
   或者你想删除的是当前目录下的文件？
```

**而不是**:
```
❌ "rm: cannot remove '/root/important.txt': Permission denied"
```

---

## 🔄 Agent 工作流程

### 完整循环

```
┌─────────────┐
│  用户输入   │
│ "创建文件"  │
└──────┬──────┘
       ↓
┌─────────────┐
│  意图理解   │
│ 需要创建文件│
└──────┬──────┘
       ↓
┌─────────────┐
│  工具选择   │
│ file_write  │
└──────┬──────┘
       ↓
┌─────────────┐
│  参数提取   │
│ path, content│
└──────┬──────┘
       ↓
┌─────────────┐
│  工具执行   │
│ 实际写入文件│
└──────┬──────┘
       ↓
┌─────────────┐
│  结果验证   │
│ 文件存在？  │
└──────┬──────┘
       ↓
┌─────────────┐
│  反馈用户   │
│ "文件已创建"│
└─────────────┘
```

**每一步都是自动的！**

---

## 📊 实际对话示例

### 示例 1: 简单任务

```
❯ 创建文件 hello.txt 内容是'World'

[Agent 思考]
- 意图：创建文件
- 工具：file_write
- 参数：{ file_path: "hello.txt", content: "World" }

[执行工具]
✅ file_write 成功

[反馈]
文件 `hello.txt` 已成功创建，内容为 "World"。
```

**实际日志**:
```
[DEBUG] Turn 1/5
[DEBUG] LLM response: content=0, toolCalls=1
[DEBUG] Checking tool call: file_write { file_path: "hello.txt", content: "World" }
[DEBUG] Executing tool: file_write
[DEBUG] Continuing to next turn...
[DEBUG] Turn 2/5
[DEBUG] LLM response: content=31, toolCalls=0
文件已成功创建...
[DEBUG] No tool calls, conversation complete
```

---

### 示例 2: 多步骤任务

```
❯ 帮我搭建一个 Express 项目

[Agent 思考]
- 意图：创建 Express 项目
- 步骤：
  1. 创建目录
  2. 初始化 npm
  3. 安装 express
  4. 创建基础文件

[执行 Step 1]
✅ bash: mkdir express-demo

[执行 Step 2]
✅ bash: cd express-demo && npm init -y

[执行 Step 3]
✅ bash: npm install express

[执行 Step 4]
✅ file_write: 创建 app.js

[反馈]
✅ Express 项目已创建！
express-demo/
├── package.json
├── app.js
└── node_modules/

运行方式：node app.js
```

---

### 示例 3: 带条件判断

```
❯ 检查有没有未提交的 git 变更

[Agent 思考]
- 意图：检查 git 状态
- 工具：bash (git status)
- 需要根据结果判断

[执行]
✅ bash: git status --porcelain

[分析结果]
- 如果有变更 → 列出文件
- 如果没有变更 → 告知干净

[反馈]
✅ 工作区干净，没有未提交的变更。
```

或者（如果有变更）:

```
[反馈]
⚠️ 发现 3 个未提交的变更：
 M src/index.ts
 M package.json
?? new-file.txt

需要我帮你提交吗？
```

---

## 🧠 Agent 的"思考"过程

### 透明化展示（调试模式）

```bash
# 开启详细日志
LOG_LEVEL=debug bun start
```

**你会看到**:

```
[DEBUG] Submitting message: 创建文件 test.txt
[DEBUG] Turn 1/5
[DEBUG] LLM response: content=0, toolCalls=1
[DEBUG] Checking tool call: file_write {
  file_path: "test.txt",
  content: "Hello"
}
[DEBUG] Executing tool: file_write
[DEBUG] FileWrite writing: test.txt
[DEBUG] Continuing to next turn...
[DEBUG] Turn 2/5
[DEBUG] LLM response: content=25, toolCalls=0
文件已成功创建...
[DEBUG] No tool calls, conversation complete
```

**每一秒都在发生什么**:
1. 用户输入 → LLM 理解
2. LLM 决定是否调用工具
3. 检查是否重复调用
4. 执行工具
5. 返回结果给 LLM
6. LLM 决定继续还是结束

---

## 🎯 和普通 Chatbot 的本质区别

| 维度 | Chatbot | Agent (Source Deploy) |
|------|---------|----------------------|
| **目标** | 回答问题 | 完成任务 |
| **输出** | 文本建议 | 实际行动 |
| **责任** | 用户执行 | Agent 执行 |
| **工具** | 不使用 | 自动调用 |
| **多步** | 不会规划 | 分解执行 |
| **错误** | 无法处理 | 尝试恢复 |
| **上下文** | 有限记忆 | 持续追踪 |

---

## 🔄 Agent vs Script

### 传统脚本

```bash
#!/bin/bash
# 固定流程
mkdir project
cd project
npm init -y
# ... 每步都要预先写好
```

**问题**:
- ❌ 只能执行预设步骤
- ❌ 遇到错误就停止
- ❌ 不能灵活应变

### Agent 方式

```
❯ 创建 Node.js 项目

Agent:
- 自动规划步骤
- 遇到错误会调整
- 可以根据情况变化
```

**优势**:
- ✅ 灵活应变
- ✅ 智能决策
- ✅ 自然语言交互

---

## 📈 能力层级

### Level 1: 被动回答（Chatbot）
```
Q: "怎么创建文件？"
A: "使用 echo 命令..."
```

### Level 2: 主动执行（Agent）✅ Source Deploy
```
Q: "创建文件 test.txt"
A: [执行] ✅ 已完成
```

### Level 3: 多步规划（高级 Agent）
```
Q: "搭建完整项目"
A: [规划→执行→验证→报告] ✅ 全部完成
```

### Level 4: 自主学习（未来）
```
Q: "优化这个项目"
A: [分析→学习→改进→总结] ✅ 持续进化
```

**Source Deploy 当前**: **Level 2-3** ⭐⭐⭐⭐

---

## 💡 实际使用体验

### 你说的话

```
"帮我把所有 TypeScript 文件里的 var 改成 let"
```

### Agent 的理解和执行

```
🧠 理解：批量修改代码
📋 计划：
   1. 找到所有 .ts 文件 (glob)
   2. 逐个读取 (file_read)
   3. 替换 var → let (file_edit)
   4. 统计修改数量

🔧 执行:
   ✅ glob: 找到 15 个文件
   ✅ file_edit: 修改 src/index.ts (3 处)
   ✅ file_edit: 修改 src/utils.ts (2 处)
   ...

📊 报告:
   完成！修改了 15 个文件，共 23 处 var → let
```

---

## 🎓 总结

### Agent 模式的特点

| 特点 | 说明 |
|------|------|
| **主动性** | 不只是说，直接做 |
| **工具使用** | 自动调用合适的工具 |
| **多步执行** | 复杂任务分解完成 |
| **智能决策** | 根据情况选择策略 |
| **错误恢复** | 遇到问题会调整 |
| **结果导向** | 以完成任务为目标 |

### 一句话总结

> **Source Deploy 不是聊天机器人，是你的 AI 编码代理**
> 
> 你说需求，TA 执行，就这么简单！

---

**最后更新**: 2026-04-06 19:06  
_体验真正的 Agent 对话吧！_ 🤖
