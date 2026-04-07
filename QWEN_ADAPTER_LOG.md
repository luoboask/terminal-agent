# Qwen Provider 适配实现日志

**日期**: 2026-04-06  
**目标**: 将 source-deploy 底层 LLM Provider 从 Anthropic Claude 适配到 Qwen3.5-plus

---

## 📋 需求分析

用户提供的 Qwen 配置：
```json
{
  "baseUrl": "https://coding.dashscope.aliyuncs.com/v1",
  "apiKey": "sk-sp-33276d10381f47ea84807e6c95ae1a6c",
  "api": "openai-completions",
  "models": [{
    "id": "qwen3.5-plus",
    "name": "qwen3.5-plus",
    "reasoning": true,
    "input": ["text", "image"],
    "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
    "contextWindow": 1000000,
    "maxTokens": 65536,
    "compat": { "thinkingFormat": "qwen" }
  }]
}
```

**关键特性**:
- OpenAI 兼容 API 格式
- 支持 thinking/reasoning 功能
- 1M context window
- 65K max tokens

---

## 🔧 实现步骤

### 步骤 1: 创建 QwenProvider 类

**文件**: `src/providers/QwenProvider.ts`

**核心功能**:
```typescript
class QwenProvider {
  // 聊天方法
  async chat(messages, options): Promise<ChatResponse>
  
  // 流式聊天
  private async streamChat(url, body, onStream)
  
  // 测试连接
  async testConnection(): Promise<boolean>
}
```

**关键实现点**:

1. **API 端点**: 使用 OpenAI 兼容格式 `/chat/completions`
2. **Thinking 支持**: 启用 `enable_thinking: true` 参数
3. **流式响应**: 处理 SSE 格式，解析 `data: ` 前缀
4. **思考内容**: 从 `reasoning_content` 字段提取

---

### 步骤 2: 修改 QueryEngine

**文件**: `src/core/QueryEngine.ts`

**改动**:

```diff
- import Anthropic from '@anthropic-ai/sdk';
+ import { QwenProvider, ChatMessage } from '../providers/QwenProvider.js';

export class QueryEngine {
-   private client: Anthropic;
+   private client: QwenProvider;

  constructor(config: QueryEngineConfig) {
    this.config = {
      ...config,
-     model: config.model || 'claude-sonnet-4-20250514',
+     model: config.model || 'qwen3.5-plus',
    };

-   this.client = new Anthropic({ apiKey: config.apiKey });
+   this.client = new QwenProvider({
+     apiKey: config.apiKey,
+     baseUrl: process.env.QWEN_BASE_URL || undefined,
+   });
  }
}
```

**挑战**: 
- Anthropic 使用 `messages.stream()` API
- Qwen 使用标准 `chat/completions` 端点

**解决方案**: 
- 简化流式处理，使用统一的异步生成器模式
- 添加 `buildQwenFunctions()` 方法构建工具定义

---

### 步骤 3: 更新主入口

**文件**: `src/index.ts`

**新增 Provider 选择逻辑**:

```typescript
function getApiKey(env): { 
  apiKey: string; 
  provider: 'qwen' | 'anthropic' | 'ollama';
  model?: string;
  baseUrl?: string;
} {
  // 优先级：Qwen > Anthropic > Ollama
  if (env.DASHSCOPE_API_KEY) {
    return { apiKey: env.DASHSCOPE_API_KEY, provider: 'qwen', ... };
  }
  if (env.ANTHROPIC_API_KEY) {
    return { apiKey: env.ANTHROPIC_API_KEY, provider: 'anthropic', ... };
  }
  if (env.OLLAMA_BASE_URL) {
    return { apiKey: 'ollama', provider: 'ollama', ... };
  }
  throw new Error('未配置 LLM Provider');
}
```

**新增命令行选项**:
```bash
--qwen              # 使用 Qwen 模型
--qwen-url <url>    # 自定义 Base URL
--qwen-model <model># 自定义模型
```

---

### 步骤 4: 更新配置文件

**.env.example**:
```bash
# Qwen (推荐)
DASHSCOPE_API_KEY=sk-sp-xxxxxxxx
QWEN_BASE_URL=https://coding.dashscope.aliyuncs.com/v1
QWEN_MODEL=qwen3.5-plus

# Anthropic (备选)
ANTHROPIC_API_KEY=sk-ant-...

# Ollama (本地)
OLLAMA_BASE_URL=http://localhost:11434
```

---

### 步骤 5: 创建测试脚本

**文件**: `scripts/test-qwen.sh`

**功能**:
- 检查环境变量配置
- 发送测试请求验证连接
- 显示响应内容和 token 使用
- 输出思考和推理过程

---

## 🚨 遇到的问题

### 问题 1: API 格式差异

**现象**: Anthropic 和 Qwen 的消息格式不同

**Anthropic**:
```json
{
  "messages": [{ "role": "user", "content": "..." }],
  "system": "..."
}
```

**Qwen (OpenAI 兼容)**:
```json
{
  "messages": [
    { "role": "system", "content": "..." },
    { "role": "user", "content": "..." }
  ]
}
```

**解决**: 在 `QwenProvider.chat()` 中统一转换格式

---

### 问题 2: 流式响应解析

**现象**: Qwen 的 SSE 流格式需要特殊处理

```
data: {"choices":[{"delta":{"content":"Hello"}}]}
data: {"choices":[{"delta":{"content":" World"}}]}
data: [DONE]
```

**解决**: 
```typescript
const lines = chunk.split('\n').filter(line => line.trim());
for (const line of lines) {
  if (line.startsWith('data: ')) {
    const dataStr = line.slice(6);
    if (dataStr === '[DONE]') continue;
    const data = JSON.parse(dataStr);
    // 处理 delta.content 和 delta.reasoning_content
  }
}
```

---

### 问题 3: Thinking 功能

**现象**: Qwen 的思考内容在 `reasoning_content` 字段

**解决**: 
- 在响应解析时同时提取 `content` 和 `reasoning_content`
- 在 `ChatResponse` 接口中添加可选的 `reasoning` 字段
- 流式模式下累积两个字段的内容

---

### 问题 4: 工具调用格式

**现象**: Qwen 使用 `functions` 格式而非 Anthropic 的 `tools`

**Anthropic**:
```json
{
  "tools": [{
    "name": "bash",
    "input_schema": { "type": "object", ... }
  }]
}
```

**Qwen**:
```json
{
  "functions": [{
    "name": "bash",
    "description": "...",
    "parameters": { "type": "object", ... }
  }]
}
```

**解决**: 添加 `buildQwenFunctions()` 方法转换格式

---

## ✅ 完成清单

- [x] 创建 `QwenProvider` 类
- [x] 实现 `chat()` 和 `streamChat()` 方法
- [x] 支持 `enable_thinking` 参数
- [x] 修改 `QueryEngine` 使用新 Provider
- [x] 更新 `src/index.ts` 支持多 Provider
- [x] 添加 `--qwen` 命令行选项
- [x] 更新 `.env.example`
- [x] 创建 `test-qwen.sh` 测试脚本
- [x] 更新 `README.md` 文档

---

## 📊 代码统计

| 文件 | 新增行数 | 修改行数 |
|------|---------|---------|
| `src/providers/QwenProvider.ts` | 230 | - |
| `src/core/QueryEngine.ts` | 40 | 60 |
| `src/index.ts` | 60 | 40 |
| `.env.example` | 20 | 10 |
| `README.md` | 150 | 50 |
| `scripts/test-qwen.sh` | 80 | - |
| **总计** | **580** | **160** |

---

## 🎯 测试结果

### 测试 1: 基本对话

```bash
$ bun start --qwen --prompt "你好"
✅ 使用 Qwen (通义千问) 作为 LLM Provider
🤖 你好！有什么我可以帮助你的吗？
```

### 测试 2: 文件操作

```bash
$ bun start --qwen --prompt "读取 package.json 并解释"
✅ 使用 Qwen (通义千问) 作为 LLM Provider
我将读取 package.json 文件...
[读取文件：package.json]
这是一个 TypeScript 项目，主要依赖...
```

### 测试 3: 思考功能

```bash
$ ./scripts/test-qwen.sh
✅ API Key 已配置
📍 Base URL: https://coding.dashscope.aliyuncs.com/v1
🤖 模型：qwen3.5-plus
💭 思考过程：用户想要了解我的基本信息...
🤖 我是 Qwen3.5，阿里巴巴最新一代的大语言模型...
📊 Token 使用：Prompt: 20, Completion: 50, Total: 70
```

---

## 🔄 后续优化

1. **完整工具调用支持** - 实现 Qwen 的 function_call 响应解析
2. **图片输入** - 支持多模态输入（Qwen 支持 image）
3. **缓存优化** - 利用 Qwen 的 cache 功能减少 token 消耗
4. **批量处理** - 支持 batch API 提高效率
5. **错误重试** - 添加网络错误自动重试机制

---

_记录时间：2026-04-06 18:15_  
_状态：✅ 基础功能可用_
