# 多渠道支持指南

## 📋 概述

Terminal Agent 支持多种交互渠道：

| 渠道 | 状态 | 说明 |
|------|------|------|
| **本地 TUI** | ✅ 完全支持 | 终端交互界面 |
| **AskUser** | ✅ 支持 | 问答工具 |
| **Telegram** | ⚠️ 计划中 | 需要渠道适配 |
| **Discord** | ⚠️ 计划中 | 需要渠道适配 |
| **Webhook** | ⚠️ 计划中 | HTTP 回调 |

## 🎯 渠道检测

### 环境变量

```bash
# 设置渠道（逗号分隔）
export OPENCLAW_CHANNELS=telegram,discord

# 设置渠道配置
export OPENCLAW_TELEGRAM_BOT_TOKEN=xxx
export OPENCLAW_DISCORD_BOT_TOKEN=xxx
```

### 检测逻辑

```typescript
// 检测是否在交互式环境
function isInteractive(): boolean {
  return process.stdin.isTTY === true;
}

// 检测是否启用了渠道
function hasChannels(): boolean {
  const channels = process.env.OPENCLAW_CHANNELS;
  return channels && channels.length > 0;
}
```

## 🔧 AskUserTool

### 使用示例

```typescript
// 简单问题
ask_user({
  question: "你想创建什么类型的项目？"
})
```

### 输出格式

**成功响应：**
```
✅ 用户回答

问题：你想创建什么类型的项目？
回答：Web 应用
```

**错误响应（非交互式环境）：**
```
❌ 非交互式环境

💡 说明：ask_user 工具需要在交互式终端中运行。
当前环境不支持用户输入。

问题：你想创建什么类型的项目？

建议：
1. 在本地终端运行 terminal-agent
2. 或者在上下文中直接提供答案
```

## 📱 渠道适配计划

### Phase 1: 本地 TUI ✅

- [x] 交互式终端支持
- [x] AskUserTool
- [x] EOFError 处理

### Phase 2: Telegram ⚠️

- [ ] Telegram Bot 集成
- [ ] 消息收发
- [ ] 内联按钮支持

### Phase 3: Discord ⚠️

- [ ] Discord Bot 集成
- [ ] Slash Commands
- [ ] 按钮交互

### Phase 4: Webhook ⚠️

- [ ] HTTP 回调端点
- [ ] 异步响应处理
- [ ] 状态跟踪

## 🔐 安全考虑

### 渠道权限

| 渠道 | 权限要求 |
|------|---------|
| 本地 TUI | 无 |
| Telegram | Bot Token |
| Discord | Bot Token + Guild ID |
| Webhook | Secret Key |

### 敏感操作

以下操作需要额外确认：

1. **文件删除** - 需要确认
2. **命令执行** - 危险命令检测
3. **外部 API** - API Key 验证

## 📊 渠道对比

| 特性 | 本地 TUI | Telegram | Discord | Webhook |
|------|---------|----------|---------|---------|
| 实时交互 | ✅ | ✅ | ✅ | ❌ |
| 富文本 | ✅ | ⚠️ | ✅ | ✅ |
| 按钮交互 | ✅ | ✅ | ✅ | ❌ |
| 文件上传 | ✅ | ✅ | ✅ | ✅ |
| 离线支持 | ❌ | ✅ | ✅ | ✅ |

## 🛠️ 开发指南

### 添加新渠道

1. **创建渠道适配器**

```typescript
// src/channels/TelegramChannel.ts
export class TelegramChannel {
  async sendMessage(chatId: string, text: string) {
    // ...
  }
  
  async askQuestion(chatId: string, question: Question) {
    // ...
  }
}
```

2. **注册渠道**

```typescript
// src/channels/index.ts
export const channels = {
  telegram: TelegramChannel,
  discord: DiscordChannel,
  webhook: WebhookChannel,
};
```

3. **更新渠道检测**

```typescript
// src/tools/AskUser.ts
private hasChannels(): boolean {
  const channels = process.env.OPENCLAW_CHANNELS;
  return channels && channels.length > 0;
}
```

## 📝 最佳实践

### 1. 渠道感知

```typescript
// 根据渠道调整输出
if (hasChannels()) {
  // 渠道模式：使用简短消息
  return `✅ 完成`;
} else {
  // 本地 TUI：使用详细输出
  return `✅ 任务完成！\n\n详细信息：...`;
}
```

### 2. 超时处理

```typescript
// 渠道模式下设置超时
const timeout = hasChannels() ? 30000 : 0; // 渠道模式 30 秒超时
```

### 3. 错误处理

```typescript
try {
  const result = await tool.execute(input);
  return formatForChannel(result);
} catch (err) {
  return formatErrorForChannel(err, currentChannel);
}
```

## 📚 参考

- [Ink - React for Terminal](https://github.com/vadimdemedes/ink)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Discord API](https://discord.com/developers/docs/intro)
