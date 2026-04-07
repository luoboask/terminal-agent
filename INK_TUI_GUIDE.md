# Ink TUI 实施指南

## 📋 概述

Ink 是一个使用 React 构建终端用户界面的框架。claude-code-learning 项目使用 Ink 实现了完整的 TUI 界面。

## 🎯 Ink 核心概念

### 1️⃣ 基本组件

```typescript
import { Box, Text } from './ink.js';

// Box - 类似 div style="display: flex"
<Box flexDirection="column" padding={1}>
  <Text color="cyan">Hello</Text>
  <Text color="green">World</Text>
</Box>

// Text - 文本显示
<Text color="red" bold>
  红色粗体文本
</Text>
```

### 2️⃣ 布局组件

```typescript
import { Box, Text, Spacer } from './ink.js';

// 垂直布局
<Box flexDirection="column">
  <Text>第一行</Text>
  <Text>第二行</Text>
</Box>

// 水平布局
<Box flexDirection="row">
  <Text>左侧</Text>
  <Spacer />  {/* 自动填充空间 */}
  <Text>右侧</Text>
</Box>

// 带边框的盒子
<Box borderStyle="round" borderColor="cyan" padding={1}>
  <Text>带边框的内容</Text>
</Box>
```

### 3️⃣ 交互组件

```typescript
import { Box, Text, Button } from './ink.js';

// 按钮
<Button
  label="确认"
  onClick={() => console.log('Clicked!')}
/>

// 可聚焦的盒子
<Box
  tabIndex={0}
  onFocus={() => console.log('Focused')}
  onBlur={() => console.log('Blurred')}
  onKeyDown={(e) => console.log('Key:', e.key)}
>
  <Text>按 Tab 聚焦</Text>
</Box>
```

## 🔧 claude-code-learning 的 Ink 实现

### 主入口

```typescript
// main.tsx
import { renderAndRun } from './interactiveHelpers.js';
import App from './ink/components/App.js';

// 渲染 Ink 应用
renderAndRun(<App />, options);
```

### App 组件

```typescript
// ink/components/App.tsx
import React from 'react';
import { Box, Text } from '../ink.js';
import { MessageList } from './MessageList.js';
import { InputPrompt } from './InputPrompt.js';
import { StatusBar } from './StatusBar.js';

export default function App() {
  return (
    <Box flexDirection="column" height="100%">
      {/* 消息列表 */}
      <Box flexGrow={1}>
        <MessageList messages={messages} />
      </Box>
      
      {/* 输入提示 */}
      <InputPrompt value={input} onChange={setInput} />
      
      {/* 状态栏 */}
      <StatusBar status={status} />
    </Box>
  );
}
```

### 消息列表

```typescript
// ink/components/MessageList.tsx
import React from 'react';
import { Box, Text } from '../ink.js';

export function MessageList({ messages }) {
  return (
    <Box flexDirection="column">
      {messages.map((msg, i) => (
        <Message key={i} message={msg} />
      ))}
    </Box>
  );
}

function Message({ message }) {
  const isUser = message.role === 'user';
  
  return (
    <Box
      flexDirection="column"
      padding={1}
      backgroundColor={isUser ? 'blue' : 'black'}
    >
      <Text color={isUser ? 'white' : 'green'}>
        {message.content}
      </Text>
    </Box>
  );
}
```

### 输入提示

```typescript
// ink/components/InputPrompt.tsx
import React, { useState } from 'react';
import { Box, Text } from '../ink.js';

export function InputPrompt({ value, onChange }) {
  return (
    <Box flexDirection="row" padding={1}>
      <Text color="cyan">❯ </Text>
      <Text>{value}</Text>
      <Cursor />  {/* 闪烁的光标 */}
    </Box>
  );
}

function Cursor() {
  const [visible, setVisible] = useState(true);
  
  React.useEffect(() => {
    const timer = setInterval(() => {
      setVisible(v => !v);
    }, 500);
    return () => clearInterval(timer);
  }, []);
  
  return (
    <Text backgroundColor="white" opacity={visible ? 1 : 0}> </Text>
  );
}
```

### 状态栏

```typescript
// ink/components/StatusBar.tsx
import React from 'react';
import { Box, Text } from '../ink.js';

export function StatusBar({ status }) {
  return (
    <Box
      flexDirection="row"
      justifyContent="space-between"
      padding={1}
      backgroundColor="black"
    >
      <Text color="gray">模型：{status.model}</Text>
      <Text color="gray">Token: {status.tokens}</Text>
      <Text color="gray">状态：{status.state}</Text>
    </Box>
  );
}
```

## 📦 实施步骤

### Phase 1: 基础框架

1. **安装 Ink**
```bash
bun add ink react
```

2. **创建 Ink 入口**
```typescript
// src/tui/index.tsx
import React from 'react';
import { render } from 'ink';
import App from './App.js';

const { waitUntilExit } = render(<App />);
await waitUntilExit();
```

3. **创建 App 组件**
```typescript
// src/tui/App.tsx
import React from 'react';
import { Box, Text } from 'ink';

export default function App() {
  return (
    <Box flexDirection="column">
      <Text color="cyan">Source Deploy TUI</Text>
      <Text>按 Ctrl+C 退出</Text>
    </Box>
  );
}
```

### Phase 2: 消息界面

4. **消息列表组件**
```typescript
// src/tui/MessageList.tsx
import React from 'react';
import { Box, Text } from 'ink';

export function MessageList({ messages }) {
  return (
    <Box flexDirection="column">
      {messages.map((msg, i) => (
        <Box key={i} padding={1}>
          <Text color={msg.role === 'user' ? 'blue' : 'green'}>
            {msg.role}: {msg.content}
          </Text>
        </Box>
      ))}
    </Box>
  );
}
```

5. **输入组件**
```typescript
// src/tui/Input.tsx
import React, { useState } from 'react';
import { Box, Text, useInput } from 'ink';

export function Input({ onSubmit }) {
  const [value, setValue] = useState('');
  
  useInput((input, key) => {
    if (key.return) {
      onSubmit(value);
      setValue('');
    } else if (key.backspace) {
      setValue(v => v.slice(0, -1));
    } else if (input) {
      setValue(v => v + input);
    }
  });
  
  return (
    <Box padding={1}>
      <Text color="cyan">❯ </Text>
      <Text>{value}</Text>
    </Box>
  );
}
```

### Phase 3: 完整界面

6. **整合所有组件**
```typescript
// src/tui/App.tsx
import React, { useState } from 'react';
import { Box, Text } from 'ink';
import { MessageList } from './MessageList.js';
import { Input } from './Input.js';
import { StatusBar } from './StatusBar.js';

export default function App() {
  const [messages, setMessages] = useState([]);
  
  const handleSubmit = async (text) => {
    // 添加用户消息
    setMessages(m => [...m, { role: 'user', content: text }]);
    
    // 调用 AI
    const response = await callAI(text);
    
    // 添加 AI 回复
    setMessages(m => [...m, { role: 'assistant', content: response }]);
  };
  
  return (
    <Box flexDirection="column" height="100%">
      <MessageList messages={messages} />
      <Input onSubmit={handleSubmit} />
      <StatusBar status={{ model: 'qwen3.5-plus', tokens: 1000 }} />
    </Box>
  );
}
```

## 🎨 样式参考

### 颜色

```typescript
<Text color="black">黑色</Text>
<Text color="red">红色</Text>
<Text color="green">绿色</Text>
<Text color="yellow">黄色</Text>
<Text color="blue">蓝色</Text>
<Text color="magenta">紫色</Text>
<Text color="cyan">青色</Text>
<Text color="white">白色</Text>
<Text color="gray">灰色</Text>
```

### 边框

```typescript
<Box borderStyle="single">
  <Text>单线边框</Text>
</Box>

<Box borderStyle="double">
  <Text>双线边框</Text>
</Box>

<Box borderStyle="round">
  <Text>圆角边框</Text>
</Box>

<Box borderStyle="bold">
  <Text>粗边框</Text>
</Box>
```

### 布局

```typescript
// Flexbox
<Box flexDirection="row" justifyContent="space-between">
  <Text>左侧</Text>
  <Text>右侧</Text>
</Box>

// 内边距
<Box padding={1}>
  <Text>内容</Text>
</Box>

// 外边距
<Box marginTop={1} marginLeft={2}>
  <Text>内容</Text>
</Box>
```

## 📚 资源

- [Ink 官方文档](https://github.com/vadimdemedes/ink)
- [React 文档](https://react.dev)
- [claude-code-learning Ink 实现](/tmp/claude-code-learning/source/src/ink/)

## ⚠️ 注意事项

1. **性能优化**
   - 使用 `React.memo` 避免不必要的重渲染
   - 使用 `useMemo` 缓存计算结果
   - 避免在渲染函数中创建新对象

2. **终端兼容性**
   - 测试不同终端（iTerm2, Terminal, Windows Terminal）
   - 处理不同尺寸和颜色支持
   - 使用 `process.stdout.isTTY` 检测终端

3. **键盘处理**
   - 使用 `useInput` hook 处理键盘输入
   - 支持 Ctrl+C, Ctrl+D 等快捷键
   - 处理箭头键导航

4. **鼠标支持**
   - 使用 `<AlternateScreen>` 启用鼠标跟踪
   - 处理点击和悬停事件
   - 支持滚动

---

_最后更新：2026-04-07_
