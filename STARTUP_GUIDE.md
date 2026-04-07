# 🚀 Source Deploy 启动指南

**更新时间**: 2026-04-06 21:00

---

## 📋 快速启动

### 方式 1: 使用启动脚本（推荐）⭐⭐⭐⭐⭐

```bash
cd source-deploy

# 交互模式
./start.sh

# 直接执行提示
./start.sh "创建文件 test.txt 内容是'Hello'"

# 详细日志模式
./start.sh --verbose "搜索代码中的 TODO"

# 查看帮助
./start.sh --help
```

---

### 方式 2: 使用快速脚本（最简洁）⭐⭐⭐⭐

```bash
cd source-deploy

# 交互模式
./run

# 直接执行
./run "创建文件 hello.txt"
```

---

### 方式 3: 直接用 Bun（原始方式）⭐⭐⭐

```bash
cd source-deploy

# 交互模式
bun run src/index.ts

# 直接执行
bun run src/index.ts --prompt "你的提示"

# 详细日志
bun run src/index.ts --verbose --prompt "搜索 TODO"
```

---

## 📋 启动脚本对比

| 脚本 | 优点 | 缺点 | 推荐场景 |
|------|------|------|----------|
| **start.sh** | 功能完整，有颜色输出，检查环境 | 代码较长 | 日常使用 |
| **run** | 极简，一行命令 | 无环境检查 | 快速测试 |
| **bun run** | 原始方式 | 需要记参数 | 调试开发 |

---

## 🔧 启动脚本功能

### start.sh 的功能

1. **环境检查**
   - ✅ 检查 `.env` 文件是否存在
   - ✅ 检查 Bun 是否安装
   - ✅ 友好的错误提示

2. **命令行参数**
   ```bash
   ./start.sh --api-key YOUR_KEY "提示"
   ./start.sh --verbose "提示"
   ./start.sh --help
   ```

3. **彩色输出**
   - 🔵 蓝色标题
   - 🟢 绿色提示
   - 🟡 黄色警告
   - 🔴 红色错误

4. **智能模式**
   - 有提示 → 直接执行
   - 无提示 → 交互模式

---

## 💡 使用示例

### 示例 1: 交互模式

```bash
./start.sh
```

**输出**:
```
╔═══════════════════════════════════════════════════════╗
║     Source Deploy - Claude Code Local Version         ║
╚═══════════════════════════════════════════════════════╝

进入交互模式
提示：输入命令后按回车，输入 'exit' 或 Ctrl+C 退出

❯ 创建文件 test.txt 内容是'Hello'
✅ 文件已创建！

❯ 
```

---

### 示例 2: 直接执行

```bash
./start.sh "创建 Node.js 项目结构"
```

**输出**:
```
╔═══════════════════════════════════════════════════════╗
║     Source Deploy - Claude Code Local Version         ║
╚═══════════════════════════════════════════════════════╝

执行提示：创建 Node.js 项目结构

✅ 好的，正在创建...
   1. 创建目录 my-project
   2. 初始化 package.json
   3. 创建 src 目录
完成！
```

---

### 示例 3: 详细日志

```bash
./start.sh --verbose "搜索代码中的 TODO"
```

**输出**:
```
[INFO] 使用 Qwen (通义千问) 作为 LLM Provider
[INFO] Registered 8 tools
[DEBUG] Submitting message: 搜索代码中的 TODO
[DEBUG] Turn 1/5
[DEBUG] Executing tool: grep
...
```

---

### 示例 4: 指定 API Key

```bash
./start.sh --api-key sk-sp-xxxxx "创建文件 test.txt"
```

**用途**: 临时使用不同的 API Key

---

## ⚙️ 配置说明

### 环境变量 (.env)

```bash
# 必需：API Key
DASHSCOPE_API_KEY=sk-sp-xxxxxxxxxxxxxxxx

# 可选：自定义配置
QWEN_BASE_URL=https://coding.dashscope.aliyuncs.com/v1
QWEN_MODEL=qwen3.5-plus

# 可选：调试
LOG_LEVEL=debug
SKIP_PERMISSION_CHECK=1
```

### 快速配置

```bash
# 复制示例配置
cp .env.example .env

# 编辑（填入你的 API Key）
vi .env

# 或者用 echo 快速设置
echo "DASHSCOPE_API_KEY=sk-sp-你的 KEY" > .env
```

---

## 🐛 常见问题

### 问题 1: 未找到 .env 文件

```
⚠️  未找到 .env 文件

请先配置环境变量：
  cp .env.example .env
  vi .env  # 编辑并填入 DASHSCOPE_API_KEY
```

**解决**:
```bash
cp .env.example .env
vi .env  # 填入你的 API Key
```

---

### 问题 2: 未找到 Bun

```
❌ 错误：未找到 Bun

请先安装 Bun: https://bun.sh/
  curl -fsSL https://bun.sh/install | bash
```

**解决**:
```bash
curl -fsSL https://bun.sh/install | bash
```

---

### 问题 3: 权限不足

```
❌ Permission denied
```

**解决**:
```bash
chmod +x start.sh run
```

---

### 问题 4: API Key 无效

```
Error: Qwen API 请求失败：401
```

**解决**:
1. 检查 `.env` 中的 API Key 是否正确
2. 确认 API Key 未过期
3. 检查网络连接

---

## 🎯 最佳实践

### 1. 添加别名（推荐）

```bash
# 在 ~/.bashrc 或 ~/.zshrc 中添加
alias sd='cd ~/.openclaw/workspace-claude-code-agent/source-deploy && ./start.sh'
alias sdr='cd ~/.openclaw/workspace-claude-code-agent/source-deploy && ./run'
```

然后：
```bash
sd  # 启动
sdr "创建文件"  # 直接执行
```

---

### 2. 创建全局命令

```bash
# 创建符号链接
ln -s ~/.openclaw/workspace-claude-code-agent/source-deploy/start.sh /usr/local/bin/sourcedeploy
```

然后任何地方都能用：
```bash
sourcedeploy "创建文件"
```

---

### 3. 使用环境变量

```bash
# 在 ~/.bashrc 中添加
export SOURCE_DEPLOY_HOME=~/.openclaw/workspace-claude-code-agent/source-deploy
```

然后：
```bash
cd $SOURCE_DEPLOY_HOME
./start.sh
```

---

## 📊 启动流程

```
./start.sh
    ↓
检查 .env 文件
    ↓
检查 Bun 是否安装
    ↓
解析命令行参数
    ↓
构建启动命令
    ↓
显示启动信息
    ↓
执行 bun run src/index.ts
    ↓
进入交互模式 或 执行提示
```

---

## 🎮 快速参考卡

```bash
# 启动方式
./start.sh                    # 交互模式
./start.sh "提示"              # 直接执行
./start.sh --verbose "提示"    # 详细日志
./start.sh --help             # 查看帮助

# 快速脚本
./run "提示"                  # 最简洁

# 原始方式
bun run src/index.ts          # 交互
bun run src/index.ts --prompt "提示"  # 执行

# 配置
cp .env.example .env          # 复制配置
vi .env                       # 编辑
./start.sh --api-key KEY      # 临时指定 Key
```

---

## ✅ 总结

**推荐启动方式**:

```bash
cd source-deploy
./start.sh
```

**最简单**:

```bash
cd source-deploy
./run "你的提示"
```

**最灵活**:

```bash
bun run src/index.ts --verbose --prompt "提示"
```

---

_最后更新：2026-04-06 21:00_  
_启动脚本版本：v1.0_
