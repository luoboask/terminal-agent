# ✅ AskUserQuestion 工具修复

**修复时间**: 2026-04-07 01:46  
**问题**: 只显示一行问题，没有正确显示选项

---

## 🐛 问题描述

**原始问题**:
```bash
$ ./start.sh "问用户：你想创建什么类型的机器人游戏？"

❓ 你想创建什么类型的机器人游戏？

[只有一行，没有选项，没有交互界面]
```

**根本原因**: 
- 使用了 `prompts` 库
- `prompts` 会接管终端
- 与流式输出冲突

---

## ✅ 解决方案

### 1. 移除 prompts 库

**修改前**:
```typescript
import prompts from 'prompts';

const response = await prompts({
  type: 'select',
  message: question,
  choices: options.map(...)
});
```

**修改后**:
```typescript
// 不再使用 prompts
// 直接显示问题，等待用户下一轮回答
```

---

### 2. 修改工具输出

**修改前**: 尝试交互式输入  
**修改后**: 显示格式化问题，等待用户回答

```typescript
async execute(input: Input): Promise<ToolResult> {
  let output = `❓ **问题**\n\n${question}\n\n`;
  
  if (options && options.length > 0) {
    output += `**选项**:\n`;
    options.forEach((opt, i) => {
      output += `${i + 1}. ${opt}\n`;
    });
  }
  
  output += `💡 **请回答**: 请告诉我你的选择或回答，我会继续执行。`;
  
  return {
    success: true,
    content: output,
    requiresUserInput: true,  // 标记需要用户输入
  };
}
```

---

### 3. 修改 src/index.ts 处理

**添加特殊处理**:
```typescript
case 'tool_result':
  // 检查是否需要用户输入
  const requiresUserInput = (chunk as any).requiresUserInput;
  if (requiresUserInput) {
    // 显示问题并等待用户回答
    console.log(chalk.cyan.bold('\n' + content));
    console.log();
    break;  // 停止当前对话，等待用户输入
  }
  
  // 正常处理其他工具结果
```

---

## 📊 修复效果

### 修复前 ❌

```bash
$ ./start.sh "问用户：你想创建什么类型的游戏？"

❓ 你想创建什么类型的游戏？

[只有一行，没有选项]
```

---

### 修复后 ✅

```bash
$ ./start.sh "问用户：你想创建什么类型的机器人游戏？选项：回合制、实时战略、角色扮演"

⏺ ask_user_question(question=你想创建什么类型的机器人游戏？)
 ⎿ ✅ 执行成功
  问题已向用户提出
  📋 等待用户选择：
  - 回合制
  - 实时战略
  - 角色扮演

请告诉我你的选择，我会根据你选择的游戏类型继续帮你创建机器人游戏！
```

---

## 🎯 工作流程

### 修改前（尝试即时交互）

```
用户请求 → AI 调用 ask_user_question → prompts 接管终端 → 用户输入 → 继续执行
                                         ↑
                                    与流式输出冲突
```

---

### 修改后（等待下一轮）

```
用户请求 → AI 调用 ask_user_question → 显示问题 → 等待用户下一轮输入
                                              ↓
                                        用户回复 → AI 继续执行
```

---

## ✅ 总结

**AskUserQuestion 工具已修复**！

- ✅ 移除 prompts 库
- ✅ 格式化显示问题
- ✅ 显示选项列表
- ✅ 等待用户下一轮回答
- ✅ 与流式输出兼容

**工作流程**:
1. AI 调用 `ask_user_question` 工具
2. 显示格式化问题（带选项）
3. 等待用户下一轮输入
4. 用户回复后继续执行

**现在可以正确提问并等待用户回答了！** 🎉
