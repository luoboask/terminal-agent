# 📦 Bun 安装指南

**更新时间**: 2026-04-06 21:05  
**状态**: ⏳ 正在安装中...

---

## 🚀 快速安装

### macOS/Linux
```bash
curl -fsSL https://bun.sh/install | bash
```

### Windows
```powershell
powershell -c "irm bun.sh/install.ps1 | iex"
```

---

## 📋 安装步骤

### 步骤 1: 下载安装脚本
```bash
curl -fsSL https://bun.sh/install -o install-bun.sh
```

### 步骤 2: 执行安装
```bash
bash install-bun.sh
```

### 步骤 3: 重启终端或刷新配置
```bash
source ~/.bashrc   # 或 source ~/.zshrc
```

### 步骤 4: 验证安装
```bash
bun --version
```

---

## ⚙️ 手动安装（可选）

### 从 GitHub Releases 下载

```bash
# macOS (Apple Silicon)
curl -Lo bun.zip https://github.com/oven-sh/bun/releases/latest/download/bun-darwin-aarch64.zip
unzip bun.zip
mv bun /usr/local/bin/

# macOS (Intel)
curl -Lo bun.zip https://github.com/oven-sh/bun/releases/latest/download/bun-darwin-x64.zip
unzip bun.zip
mv bun /usr/local/bin/

# Linux (x64)
curl -Lo bun.zip https://github.com/oven-sh/bun/releases/latest/download/bun-linux-x64.zip
unzip bun.zip
mv bun /usr/local/bin/
```

---

## 🔧 配置环境变量

### macOS/Linux
编辑 `~/.bashrc` 或 `~/.zshrc`:
```bash
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"
```

然后：
```bash
source ~/.bashrc  # 或 source ~/.zshrc
```

### Windows
在系统环境变量中添加：
```
BUN_INSTALL=C:\Users\YourName\.bun
PATH=%PATH%;%BUN_INSTALL%\bin
```

---

## ✅ 验证安装

```bash
# 检查版本
bun --version

# 应该输出版本号，如：1.0.0
```

---

## 🐛 常见问题

### 问题 1: 权限不足

```bash
# 解决方法 1: 使用 sudo
sudo curl -fsSL https://bun.sh/install | bash

# 解决方法 2: 修改目录权限
sudo chown -R $(whoami) ~/.bun
```

### 问题 2: 找不到 bun 命令

```bash
# 检查 PATH
echo $PATH

# 手动添加
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"

# 添加到 ~/.bashrc 或 ~/.zshrc
echo 'export BUN_INSTALL="$HOME/.bun"' >> ~/.bashrc
echo 'export PATH="$BUN_INSTALL/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### 问题 3: 下载速度慢

```bash
# 使用镜像（如果可用）
# 或手动下载后安装
curl -Lo bun.zip https://github.com/oven-sh/bun/releases/latest/download/bun-darwin-aarch64.zip
unzip bun.zip
mv bun ~/.bun/bin/
```

---

## 📊 安装进度

**当前状态**: ⏳ 下载中...

**预计时间**: 2-5 分钟（取决于网络速度）

**下载内容**:
- Bun 运行时
- bunfig.toml 配置文件
- 环境变量配置

---

## 🎯 安装后步骤

### 1. 验证安装
```bash
bun --version
```

### 2. 测试 Source Deploy
```bash
cd ~/.openclaw/workspace-claude-code-agent/source-deploy
./start.sh
```

### 3. 运行第一个命令
```bash
./start.sh "你好"
```

---

## 💡 提示

- 安装过程中会询问是否添加环境变量到 shell 配置
- 建议选择 "yes" 以自动配置
- 安装完成后需要重启终端或运行 `source ~/.bashrc`

---

_最后更新：2026-04-06 21:05_  
_安装状态：进行中..._
