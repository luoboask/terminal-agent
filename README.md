# Terminal Agent

一个强大的终端 AI 助手，支持多种 LLM Provider（Qwen/Ollama/Anthropic 等）。

## ✨ 特性

- 🤖 **多 Provider 支持** - Qwen/通义千问、Ollama 本地模型、Anthropic Claude
- 🛠️ **丰富工具集** - 文件操作、搜索、命令执行、任务管理等 20+ 工具
- 📦 **智能分块** - 大文件自动分块读写，支持 256KB+ 文件
- 💾 **持久化** - 超大内容自动保存到临时文件
- 🎯 **渠道支持** - 本地 TUI、Telegram、Discord（计划中）
- 🔒 **安全限制** - 工具输出大小限制，防止上下文爆炸

## 🚀 快速开始

### 安装依赖

```bash
bun install
```

### 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入你的 API Key
```

### 运行

```bash
# 交互模式
./start.sh

# 直接执行
./start.sh "创建一个测试文件"

# 使用 Ollama 本地模型
./start.sh --ollama "你好"
```

## 📋 工具列表

### 文件操作
| 工具 | 说明 | 限制 |
|------|------|------|
| file_read | 读取文件 | 256KB / 2000 行 |
| file_write | 写入文件 | 支持分块写入 |
| file_edit | 编辑文件 | - |
| file_delete | 删除文件 | - |
| directory_create | 创建目录 | - |

### 搜索工具
| 工具 | 说明 | 限制 |
|------|------|------|
| grep | 文本搜索 | 250 条 / 20K 字符 |
| glob | 文件搜索 | 100 条 / 100K 字符 |

### 执行工具
| 工具 | 说明 | 限制 |
|------|------|------|
| bash | 执行命令 | 30K 字符输出 |

### 交互工具
| 工具 | 说明 | 环境要求 |
|------|------|------|
| ask_user | 向用户提问 | 交互式终端 |

### 任务管理
| 工具 | 说明 |
|------|------|
| task_create | 创建任务 |
| task_update | 更新任务 |
| task_get | 获取任务 |
| task_list | 列出任务 |
| task_stop | 停止任务 |
| task_output | 获取输出 |
| task_complete | 完成任务 |
| task_delete | 删除任务 |

### 其他工具
- web_fetch - 获取网页内容
- brief - 简报生成
- skill - 技能管理
- agent - Agent 管理
- mcp - MCP 工具支持

## 🔧 配置

### 环境变量

```bash
# Qwen/通义千问（推荐）
DASHSCOPE_API_KEY=your_key_here

# Anthropic Claude（可选）
ANTHROPIC_API_KEY=your_key_here

# Ollama 本地模型（可选）
OLLAMA_URL=http://localhost:11434
```

### 模型配置

```bash
# 使用 Qwen
./start.sh --qwen --qwen-model qwen3.5-plus

# 使用 Ollama
./start.sh --ollama --ollama-model llama3.1:8b

# 使用自定义 API Key
./start.sh --api-key sk-xxx "你的问题"
```

## 📊 大文件处理

### 自动分块

当文件超过 25KB 时，系统会自动提示使用分块写入：

```typescript
// 大文件分块写入示例
file_write({
  file_path: "large_file.txt",
  content: "...第一块内容...",  // 约 20KB
  is_chunk: true,
  chunk_index: 0,
  total_chunks: 5
})
```

### 自动持久化

工具输出超过限制时自动保存到临时文件：

```
内容过大，已保存到临时文件
文件大小：150KB
临时文件：.source-deploy-temp/large_content_xxx.txt

预览：
第一行内容...
第二行内容...
...

使用 Bash 命令读取完整内容：cat .source-deploy-temp/large_content_xxx.txt
```

## 🎯 最佳实践

### 1. 读取大文件

```bash
# 使用 offset 和 limit 分块读取
file_read({ file_path: "large.txt", offset: 1, limit: 2000 })
file_read({ file_path: "large.txt", offset: 2001, limit: 2000 })
```

### 2. 写入大文件

```bash
# 分块写入
file_write({ file_path: "output.txt", content: "...", is_chunk: true, chunk_index: 0, total_chunks: 3 })
file_write({ file_path: "output.txt", content: "...", is_chunk: true, chunk_index: 1, total_chunks: 3 })
file_write({ file_path: "output.txt", content: "...", is_chunk: true, chunk_index: 2, total_chunks: 3 })
```

### 3. 搜索大量结果

```bash
# 使用分页
grep({ pattern: "TODO", head_limit: 250, offset: 0 })
grep({ pattern: "TODO", head_limit: 250, offset: 250 })
```

## 📁 项目结构

```
terminal-agent/
├── src/
│   ├── core/           # 核心引擎
│   ├── tools/          # 工具实现
│   ├── providers/      # LLM Provider
│   ├── memory/         # 记忆系统
│   ├── mcp/            # MCP 集成
│   ├── utils/          # 工具函数
│   └── index.ts        # 主入口
├── tests/              # 测试文件
├── scripts/            # 脚本
├── .env.example        # 环境变量示例
├── start.sh            # 启动脚本
└── README.md           # 本文档
```

## 🧪 测试

```bash
# 运行所有测试
bun test

# 测试特定工具
bun run tests/test-file-write.ts
```

## 📚 文档

- [多渠道支持指南](CHANNELS_GUIDE.md)
- [Ink TUI 实施指南](INK_TUI_GUIDE.md)
- [修复计划](FIX_PLAN.md)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

本项目灵感来源于 [claude-code-learning](https://github.com/luoboask/claude-code-learning) 项目，但已完全重写，与 Claude 无任何关系。
