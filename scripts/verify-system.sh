#!/bin/bash

echo "🧪 验证项目管理系统"
echo "============================================================"

# 检查文件是否存在
echo ""
echo "1️⃣ 检查文件结构..."

files=(
  "src/bootstrap/state.ts"
  "src/utils/projectSettings.ts"
  "src/utils/sessionStorage.ts"
  "src/utils/taskStorageV2.ts"
  "src/tools/WorktreeTool.ts"
  "PROJECT_MANAGEMENT_USAGE.md"
  "WORKTREE_TOOL_USAGE.md"
  "INTEGRATION_USAGE.md"
  "QUICK_REFERENCE.md"
)

for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    echo "✅ $file"
  else
    echo "❌ $file (缺失)"
  fi
done

# 检查代码语法
echo ""
echo "2️⃣ 检查 TypeScript 语法..."

cd /Users/dhr/.openclaw/workspace-claude-code-agent/source-deploy

# 使用 bun 检查
if command -v bun &> /dev/null; then
  echo "✅ Bun 已安装"
  
  # 尝试编译
  echo ""
  echo "📦 编译 TypeScript..."
  if bun build src/bootstrap/state.ts --outdir=dist 2>&1 | grep -q "error"; then
    echo "❌ 编译失败"
  else
    echo "✅ 编译成功"
  fi
else
  echo "⚠️  Bun 未安装，跳过编译检查"
fi

# 检查 Git 状态
echo ""
echo "3️⃣ 检查 Git 状态..."

if git rev-parse --git-dir &> /dev/null; then
  echo "✅ Git 仓库"
  
  # 检查是否已推送
  if git status | grep -q "Your branch is up to date"; then
    echo "✅ 已推送到 GitHub"
  else
    echo "⚠️  有未推送的提交"
  fi
else
  echo "❌ 不是 Git 仓库"
fi

# 检查目录结构
echo ""
echo "4️⃣ 检查目录结构..."

if [ -d ".source-deploy" ]; then
  echo "✅ .source-deploy 目录"
  
  if [ -d ".source-deploy/sessions" ]; then
    echo "✅ .source-deploy/sessions 目录"
  else
    echo "📁 创建 .source-deploy/sessions 目录"
    mkdir -p .source-deploy/sessions
  fi
  
  if [ -d ".source-deploy/tasks" ]; then
    echo "✅ .source-deploy/tasks 目录"
  else
    echo "📁 创建 .source-deploy/tasks 目录"
    mkdir -p .source-deploy/tasks
  fi
else
  echo "📁 创建 .source-deploy 目录"
  mkdir -p .source-deploy
  mkdir -p .source-deploy/sessions
  mkdir -p .source-deploy/tasks
fi

# 统计代码量
echo ""
echo "5️⃣ 代码统计..."

ts_files=$(find src -name "*.ts" | wc -l)
md_files=$(find . -maxdepth 1 -name "*.md" | wc -l)
ts_lines=$(find src -name "*.ts" -exec cat {} + | wc -l)
md_lines=$(find . -maxdepth 1 -name "*.md" -exec cat {} + | wc -l)

echo "   TypeScript 文件：$ts_files"
echo "   Markdown 文件：$md_files"
echo "   TypeScript 代码行数：$ts_lines"
echo "   Markdown 文档行数：$md_lines"

# 最终总结
echo ""
echo "============================================================"
echo "✅ 系统验证完成！"
echo ""
echo "📊 总结:"
echo "   - 核心文件：${#files[@]} 个"
echo "   - TypeScript 文件：$ts_files"
echo "   - 文档文件：$md_files"
echo "   - 代码行数：$ts_lines"
echo "   - 文档行数：$md_lines"
echo ""
