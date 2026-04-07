#!/bin/bash

echo "========================================"
echo "🧪 测试所有工具"
echo "========================================"
echo ""

# 测试 file_read
echo "1️⃣ 测试 file_read..."
./start.sh "读取 pet-system/pet.py" 2>&1 | grep -E "成功读取 | 失败 | ❌" | head -3
echo ""

# 测试 file_write
echo "2️⃣ 测试 file_write..."
./start.sh "创建文件 test-tools.txt，内容是 Hello World" 2>&1 | grep -E "创建成功 | 失败 | ❌" | head -3
echo ""

# 测试 glob
echo "3️⃣ 测试 glob..."
./start.sh "查找所有 py 文件" 2>&1 | grep -E "找到 | 失败 | ❌" | head -3
echo ""

# 测试 bash
echo "4️⃣ 测试 bash..."
./start.sh "运行命令 ls -la | head -5" 2>&1 | grep -E "执行成功 | 失败 | ❌" | head -3
echo ""

# 测试 session_save
echo "5️⃣ 测试 session_save..."
./start.sh "保存当前会话" 2>&1 | grep -E "已保存 | 失败 | ❌" | head -3
echo ""

# 测试 session_load
echo "6️⃣ 测试 session_load..."
./start.sh "加载会话 session-history.json" 2>&1 | grep -E "已加载 | 失败 | ❌" | head -3
echo ""

# 测试 file_cache
echo "7️⃣ 测试 file_cache..."
./start.sh "使用 file_cache 查看缓存" 2>&1 | grep -E "缓存 | 失败 | ❌" | head -3
echo ""

# 清理测试文件
rm -f test-tools.txt 2>/dev/null

echo "========================================"
echo "✅ 测试完成"
echo "========================================"
