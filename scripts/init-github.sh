#!/bin/bash

# Terminal Agent - GitHub 仓库初始化脚本

set -e

echo "🚀 初始化 Terminal Agent GitHub 仓库..."

# 检查是否在 git 仓库中
if [ ! -d ".git" ]; then
  echo "📁 初始化 Git 仓库..."
  git init
fi

# 检查远程仓库
if ! git remote | grep -q "origin"; then
  echo "🔗 请设置远程仓库地址："
  echo "   git remote add origin https://github.com/YOUR_USERNAME/terminal-agent.git"
  echo ""
  read -p "是否现在设置？(y/n) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "输入仓库地址： " REPO_URL
    git remote add origin "$REPO_URL"
  fi
fi

# 添加文件
echo "📦 添加文件..."
git add -A

# 提交
echo "💾 提交更改..."
git commit -m "Initial commit: Terminal Agent v0.1.0

✨ 功能:
- 多 Provider 支持 (Qwen/Ollama/Anthropic)
- 20+ 工具集 (文件操作/搜索/命令执行/任务管理)
- 大文件处理 (分块写入/自动持久化)
- 工具输出限制 (防止上下文爆炸)
- 多渠道支持 (本地 TUI/Telegram/Discord)

📚 文档:
- README.md - 项目说明
- CHANNELS_GUIDE.md - 多渠道支持指南
- INK_TUI_GUIDE.md - Ink TUI 实施指南
- FIX_PLAN.md - 修复与优化计划

🔧 优化:
- FileRead: 256KB 文件限制
- Bash: 30K 字符输出限制
- Grep: 250 条/20K 字符限制
- Glob: 100 条/100K 字符限制
- 3 次重复调用阻止机制
- 临时文件自动清理"

# 显示状态
echo ""
echo "✅ 初始化完成！"
echo ""
echo "下一步："
echo "  1. git push -u origin main"
echo "  2. 在 GitHub 上创建仓库并添加描述"
echo "  3. 添加 GitHub Actions CI/CD（可选）"
echo ""
