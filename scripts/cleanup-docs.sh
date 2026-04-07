#!/bin/bash

# 清理不必要的历史文档

set -e

echo "🧹 清理历史文档..."

# 保留的文档
KEEP_DOCS="README.md|CHANNELS_GUIDE.md|INK_TUI_GUIDE.md|FIX_PLAN.md|GITHUB_SETUP_COMPLETE.md|LICENSE"

# 删除所有其他 .md 文件
find . -maxdepth 1 -name "*.md" -type f | grep -vE "$KEEP_DOCS" | while read file; do
  echo "🗑️  删除：$file"
  rm "$file"
done

# 删除测试文件
rm -f *.txt *.py *.html 2>/dev/null || true
rm -rf robot_battle_game/ robot-game-3d/ tank-battle/ 2>/dev/null || true
rm -f robot_battle.py robot_battle_demo.py snake_game.py snake_game.html tank_battle.py tank_battle_3d.py 2>/dev/null || true

# 删除测试脚本
rm -f test-*.sh test-*.py 2>/dev/null || true

# 删除临时文件
rm -rf __pycache__/ .source-deploy-temp/ 2>/dev/null || true

echo "✅ 清理完成！"
echo ""
echo "保留的核心文档："
ls -la *.md LICENSE
