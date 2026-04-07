# 🔧 CLI 工具调用循环补充计划

**执行时间**: 2026-04-06 18:46  
**目标**: 实现完整的对话→工具调用→执行→结果处理循环

---

## 🎯 问题分析

### 当前状态
```typescript
// QueryEngine.submitMessage() 现状
async *submitMessage(prompt: string): AsyncGenerator<StreamMessage> {
  // 1. 添加用户消息
  this.messages.push({ role: 'user', content: prompt });
  
  // 2. 调用 LLM
  const response = await this.client.chat(messages, { tools: [...] });
  
  // 3. 返回文本
  yield { type: 'text', content: response.content };
  
  // ❌ 缺少：检测工具调用 → 执行工具 → 返回结果 → 继续对话
}
```

### 需要实现的功能
```typescript
async *submitMessage(prompt: string): AsyncGenerator<StreamMessage> {
  // 现有功能
  - 发送消息给 LLM
  - 流式返回文本
  
  // 新增功能
  + 解析 LLM 返回的工具调用
  + 执行工具
  + 将工具结果返回给 LLM
  + 获取最终回复
  + 支持多轮工具调用
}
```

---

## 📋 实施步骤

### 阶段 1: 分析 Qwen 工具调用格式 (15min)
- Qwen 的 function_call 响应格式
- 与 Anthropic 的差异

### 阶段 2: 修改 QwenProvider (20min)
- 支持 function_call 参数
- 解析工具调用响应

### 阶段 3: 增强 QueryEngine (40min)
- 实现工具调用检测
- 添加工具执行循环
- 处理多轮对话

### 阶段 4: 测试验证 (15min)
- 测试单个工具调用
- 测试多轮工具调用
- 测试错误处理

---

## ✅ 成功标准

- [ ] AI 能自动调用工具（不只是显示计划）
- [ ] 工具执行结果返回给 AI
- [ ] AI 基于工具结果继续对话
- [ ] 支持连续调用多个工具
- [ ] 错误处理完善

---

开始执行...
