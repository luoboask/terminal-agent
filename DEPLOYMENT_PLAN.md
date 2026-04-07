# Claude Code 本地部署方案

> ⚠️ **重要说明**：本方案用于学习和研究目的。Claude Code 是 Anthropic 的商业产品，请遵守相关许可协议。

---

## 🎯 目标

在本地部署 **claude-code-learning** 项目中分析的 Claude Code CLI 源码，实现可运行的本地版本。

---

## 📋 前置分析

### 源码来源
- **项目**: https://github.com/luoboask/claude-code-learning
- **源码位置**: `source/src/` 目录
- **入口文件**: `main.tsx` (804KB)
- **语言**: TypeScript
- **运行时**: Bun

### 核心组件
| 组件 | 文件数 | 说明 |
|------|--------|------|
| 工具实现 | 45 个 | BashTool, FileEdit, Grep, MCPTool 等 |
| UI 组件 | 146 个 | Ink (React for Terminal) 组件 |
| Hooks | 87 个 | 状态管理 React Hooks |
| 工具函数 | 331 个 | utils/ 目录 |

---

## 🏗️ 部署架构

```
┌─────────────────────────────────────────────────────┐
│                 Claude Code Local                   │
├─────────────────────────────────────────────────────┤
│  CLI Interface (Ink + React)                        │
│  ├── components/ (146 UI 组件)                       │
│  └── hooks/ (87 Hooks)                              │
├─────────────────────────────────────────────────────┤
│  Core Engine                                        │
│  ├── main.tsx (入口)                                │
│  ├── query.ts (查询编排)                            │
│  ├── QueryEngine.ts (引擎核心)                      │
│  └── Tool.ts (工具抽象)                             │
├─────────────────────────────────────────────────────┤
│  Tools Layer                                        │
│  ├── tools.ts (工具注册表)                          │
│  └── tools/ (45 个工具实现)                          │
├─────────────────────────────────────────────────────┤
│  Services Layer                                     │
│  ├── MCP Client (Model Context Protocol)            │
│  ├── LSP Client (Language Server Protocol)          │
│  ├── OAuth Client                                   │
│  └── Anthropic API Client                           │
├─────────────────────────────────────────────────────┤
│  Memory System                                      │
│  ├── Long-term Memory                               │
│  ├── Session Notes                                  │
│  ├── Project Context                                │
│  └── Task Plans                                     │
└─────────────────────────────────────────────────────┘
```

---

## 📦 依赖清单

### 核心运行时
```bash
# Bun 运行时 (推荐，比 Node.js 更快)
curl -fsSL https://bun.sh/install | bash

# 或 Node.js 18+
nvm install 18
```

### NPM 依赖 (估计)
```json
{
  "dependencies": {
    "@anthropic-ai/sdk": "^0.x.x",      // Anthropic API
    "ink": "^4.x.x",                     // Terminal UI
    "react": "^18.x.x",                  // UI 框架
    "zod": "^3.x.x",                     // Schema 验证
    "@modelcontextprotocol/sdk": "^1.x" // MCP 协议
  },
  "devDependencies": {
    "typescript": "^5.x.x",
    "@types/react": "^18.x.x",
    "@types/node": "^20.x.x"
  }
}
```

### 系统工具
```bash
# Git
brew install git

# 可选：MCP 服务器
# - GitHub MCP
# - Sentry MCP
# - 自定义 MCP 服务器
```

---

## 🚀 部署步骤

### 阶段 1: 准备环境 (预计 30 分钟)

```bash
# 1. 创建项目目录
mkdir -p ~/projects/claude-code-local
cd ~/projects/claude-code-local

# 2. 克隆学习项目获取源码
git clone https://github.com/luoboask/claude-code-learning.git source
cd source

# 3. 检查源码完整性
ls -la source/src/
# 应包含：main.tsx, query.ts, QueryEngine.ts, Tool.ts, tools/, components/, hooks/
```

### 阶段 2: 提取和整理源码 (预计 2-4 小时)

```bash
# 1. 创建独立项目结构
cd ~/projects/claude-code-local
mkdir -p claude-code-local/{src,tests,docs,scripts}

# 2. 复制核心源码
cp -r source/source/src/* claude-code-local/src/

# 3. 初始化项目
cd claude-code-local
bun init  # 或 npm init

# 4. 安装依赖 (需要根据 package.json 分析)
bun install
```

### 阶段 3: 分析和修复依赖 (预计 4-8 小时)

**关键任务**:
1. 分析 `main.tsx` 的导入语句，识别所有依赖
2. 创建 `package.json` 列出所有 NPM 包
3. 处理可能的内部模块引用
4. 修复 TypeScript 配置

```bash
# 分析导入语句
grep -r "import.*from" src/ | grep -v "\.ts" | sort -u

# 创建 TypeScript 配置
cat > tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "lib": ["ES2022"],
    "moduleResolution": "bundler",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "outDir": "./dist",
    "rootDir": "./src",
    "jsx": "react-jsx",
    "allowSyntheticDefaultImports": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
EOF
```

### 阶段 4: 配置 API 和认证 (预计 1-2 小时)

**需要配置的内容**:

1. **Anthropic API Key**
```bash
# .env 文件
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

2. **MCP 服务器配置**
```json
// mcp-config.json
{
  "servers": {
    "github": {
      "url": "https://api.githubcopilot.com/mcp/",
      "transport": "http"
    },
    "sentry": {
      "url": "https://mcp.sentry.dev/mcp",
      "transport": "http"
    }
  }
}
```

3. **本地记忆存储**
```bash
# 创建记忆目录
mkdir -p ~/.claude-code-local/{memory,sessions,cache}
```

### 阶段 5: 构建和测试 (预计 2-4 小时)

```bash
# 1. TypeScript 编译检查
bun run build  # 或 tsc --noEmit

# 2. 运行测试 (如果有)
bun test

# 3. 启动 CLI
bun run src/main.tsx

# 4. 基础功能测试
# - 文件读取
# - 命令执行
# - API 调用
```

### 阶段 6: 优化和定制 (持续)

- [ ] 移除不必要的 UI 组件
- [ ] 简化状态管理逻辑
- [ ] 添加自定义工具
- [ ] 集成 OpenClaw 记忆系统
- [ ] 性能优化

---

## 🔧 技术挑战与解决方案

### 挑战 1: 源码完整性
**问题**: source map 逆向的源码可能不完整或有混淆

**解决方案**:
- 对比多个版本的 source map
- 参考官方文档补充缺失部分
- 逐步测试并修复运行时错误

### 挑战 2: 内部依赖
**问题**: 可能有未发布的内部 NPM 包

**解决方案**:
- 用公开包替代（如 @anthropic-ai/sdk）
- 自行实现简化版本
- 使用 Mock 进行隔离测试

### 挑战 3: API 认证
**问题**: 原版使用 Anthropic 专有认证流程

**解决方案**:
- 直接使用 Anthropic API Key
- 实现简化的 OAuth 流程
- 或完全替换为本地模型（Ollama）

### 挑战 4: UI 组件依赖
**问题**: 146 个 Ink 组件可能有复杂的状态依赖

**解决方案**:
- 优先保证 CLI 功能，UI 可简化
- 使用终端原生输出替代复杂 UI
- 分阶段实现 UI 组件

---

## 📁 推荐项目结构

```
claude-code-local/
├── src/
│   ├── index.ts              # 新入口（简化版 main.tsx）
│   ├── core/
│   │   ├── engine.ts         # QueryEngine 简化版
│   │   ├── query.ts          # 查询编排
│   │   └── tool.ts           # 工具抽象基类
│   ├── tools/
│   │   ├── bash.ts           # Bash 工具
│   │   ├── file-edit.ts      # 文件编辑
│   │   ├── grep.ts           # 搜索工具
│   │   ├── mcp-tool.ts       # MCP 集成
│   │   └── ...               # 其他工具
│   ├── memory/
│   │   ├── index.ts          # 记忆系统入口
│   │   ├── long-term.ts      # 长期记忆
│   │   ├── session.ts        # 会话笔记
│   │   └── project.ts        # 项目上下文
│   ├── mcp/
│   │   ├── client.ts         # MCP 客户端
│   │   └── servers.ts        # 服务器配置
│   └── utils/
│       └── ...               # 工具函数
├── tests/
│   ├── tools/
│   └── core/
├── docs/
│   ├── ARCHITECTURE.md
│   └── API.md
├── scripts/
│   ├── setup.sh
│   └── deploy.sh
├── package.json
├── tsconfig.json
├── .env.example
└── README.md
```

---

## 🎯 里程碑

| 阶段 | 目标 | 预计时间 |
|------|------|----------|
| M1 | 环境准备完成，源码提取完毕 | 4 小时 |
| M2 | 依赖分析完成，package.json 创建 | 8 小时 |
| M3 | TypeScript 编译通过 | 4 小时 |
| M4 | 基础 CLI 可运行 | 8 小时 |
| M5 | 核心工具可用（Bash/File/Grep） | 16 小时 |
| M6 | MCP 集成完成 | 8 小时 |
| M7 | 完整功能测试通过 | 8 小时 |

**总计**: 约 56 小时（约 7 个工作日）

---

## ⚠️ 风险与注意事项

1. **法律风险**: 仅供学习研究，不要用于商业用途
2. **API 成本**: Anthropic API 调用会产生费用
3. **维护成本**: 源码较大，后续维护需要投入
4. **技术债务**: 逆向工程的源码可能存在隐藏问题

---

## 🔄 替代方案

如果上述方案太复杂，可以考虑：

### 方案 B: 基于官方 CLI 扩展
- 使用官方 `claude` CLI
- 通过 Skills/Hooks/MCP 扩展功能
- 优点：稳定、合法、易维护
- 缺点：依赖 Anthropic 服务

### 方案 C: 自研简化版
- 参考架构设计，从头实现核心功能
- 只实现需要的工具（Bash/File/Grep）
- 集成 Ollama 本地模型
- 优点：完全可控、无法律问题
- 缺点：开发周期长

---

## 📝 下一步行动

1. **确认方向**: 选择完整部署 (本方案) / 官方扩展 / 自研简化版
2. **克隆源码**: `git clone https://github.com/luoboask/claude-code-learning.git`
3. **源码分析**: 详细分析 `source/src/` 目录结构和依赖
4. **创建仓库**: 建立 `claude-code-local` 项目仓库
5. **开始实施**: 按阶段逐步推进

---

_创建时间：2026-04-06_  
_版本：v1.0_  
_状态：待审核_
