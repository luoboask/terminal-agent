#!/bin/bash

# 清理 source-deploy 缓存和临时文件

set -e

echo "🧹 清理缓存和临时文件..."

# 临时文件目录
if [ -d ".source-deploy-temp" ]; then
  echo "🗑️  删除 .source-deploy-temp/"
  rm -rf .source-deploy-temp/
fi

# Python 缓存
if [ -d "__pycache__" ]; then
  echo "🗑️  删除 __pycache__/"
  rm -rf __pycache__/
fi

# 游戏项目缓存
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Bun 编译产物
if [ -d "dist" ]; then
  echo "🗑️  删除 dist/"
  rm -rf dist/
fi

# 备份文件
find . -name "*.bak" -delete 2>/dev/null || true
find . -name "*.backup" -delete 2>/dev/null || true

# 日志文件
find . -name "*.log" -delete 2>/dev/null || true

# 测试文件
rm -f test-*.py test-*.txt 2>/dev/null || true

# 旧的任务文件（如果使用新系统）
if [ -f ".source-deploy-tasks.json" ] && [ -d ".source-deploy-tasks" ]; then
  echo "⚠️  检测到旧任务文件格式"
  echo "   建议手动检查后删除：rm .source-deploy-tasks.json"
fi

echo "✅ 清理完成！"
echo ""
echo "📊 清理内容:"
echo "  - 临时文件目录"
echo "  - Python 缓存"
echo "  - Bun 编译产物"
echo "  - 备份文件"
echo "  - 日志文件"
echo "  - 测试文件"
