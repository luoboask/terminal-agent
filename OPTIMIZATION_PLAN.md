# 🎯 复杂任务优化计划

**目标**: 解决 LLM 重复执行相同命令的问题

---

## 🔍 问题分析

### 当前行为
```
用户：创建文件 test.txt
Turn 1: bash echo '' > test.txt ✅
Turn 2: bash echo '' > test.txt ❌ 重复
Turn 3: bash echo '' > test.txt ❌ 重复
...
Turn 5: 达到最大轮数 ❌
```

### 根本原因

1. **LLM 不知道任务已完成**
   - 工具返回只有结果，没有"任务完成"信号
   - LLM 继续尝试"帮助"用户

2. **缺少上下文记忆**
   - 没有记录刚刚执行过的工具
   - 无法检测重复调用

3. **系统提示不够明确**
   - 没有说明"完成后停止"
   - 没有说明"不要重复相同操作"

---

## 💡 优化方案

### 方案 1: 增强系统提示 (立即实施)

添加明确的规则：
```typescript
const systemPrompt = `你是 AI 编程助手。

重要规则：
1. 每个工具只调用一次，除非用户明确要求重复
2. 任务完成后，直接回复总结，不要再调用工具
3. 如果刚执行过某个操作，不要重复执行
4. 检测到用户请求已完成时，停止工具调用`;
```

### 方案 2: 检测重复调用 (立即实施)

```typescript
// 在 QueryEngine 中添加
private recentToolCalls: Array<{name: string; args: string}> = [];

// 检测是否重复
isRepeatedToolCall(name: string, args: any): boolean {
  const sig = `${name}:${JSON.stringify(args)}`;
  return this.recentToolCalls.some(r => r === sig);
}

// 阻止重复
if (this.isRepeatedToolCall(toolCall.name, toolCall.args)) {
  yield { type: 'error', content: '检测到重复调用，任务可能已完成' };
  return; // 强制结束
}
```

### 方案 3: 改进工具返回格式 (立即实施)

```typescript
// 添加强调信息
yield {
  type: 'tool_result',
  content: `${result.content}\n\n✅ 操作已完成。如果没有其他需求，请直接回复用户。`,
};
```

---

## 📋 实施步骤

1. **增强系统提示** - 5min
2. **添加重复检测** - 10min  
3. **改进返回格式** - 5min
4. **测试验证** - 10min

**总计**: 30min

---

开始实施...
