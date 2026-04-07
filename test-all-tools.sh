#!/bin/bash

# 系统性测试所有工具
# 使用方式：./test-all-tools.sh

set -e

echo "╔═══════════════════════════════════════════════════════╗"
echo "║        Source Deploy - 全面工具测试                    ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

cd "$(dirname "$0")"

# 测试结果统计
PASSED=0
FAILED=0
SKIPPED=0

# 测试函数
test_tool() {
    local tool_name=$1
    local command=$2
    local expected=$3
    
    echo "🧪 测试：$tool_name"
    echo "   命令：$command"
    
    if echo "exit" | ./start.sh -p "$command" 2>&1 | grep -q "$expected"; then
        echo "   ✅ 通过"
        ((PASSED++))
    else
        echo "   ❌ 失败"
        ((FAILED++))
    fi
    echo ""
}

# 清理测试文件
cleanup() {
    rm -f test-*.txt test-*.py test-*.md 2>/dev/null || true
    rm -rf test-dir-* 2>/dev/null || true
}

# 开始测试
echo "📁 文件操作工具测试"
echo "────────────────────────────────────────"

test_tool "file_write" "创建文件 test-write.txt 内容是'Hello World'" "文件创建成功"
test_tool "file_read" "读取 test-write.txt 的内容" "Hello World"
test_tool "file_edit" "编辑 test-write.txt，把 Hello 改成 Hi" "Hi World"
test_tool "directory_create" "创建目录 test-dir-1" "目录.*已成功创建"

echo ""
echo "🔍 搜索工具测试"
echo "────────────────────────────────────────"

test_tool "grep" "在 test-write.txt 中搜索 Hi" "搜索"
test_tool "glob" "查找当前目录所有.txt 文件" ".txt"

echo ""
echo "📋 Task 管理工具测试"
echo "────────────────────────────────────────"

test_tool "task_create_enhanced" "创建任务：测试任务，优先级 high" "任务创建成功"
test_tool "task_list_enhanced" "查看所有任务" "任务"

echo ""
echo "💬 交互工具测试"
echo "────────────────────────────────────────"

test_tool "ask_user_question" "问用户：你喜欢什么颜色？选项：红色、蓝色、绿色" "问题"

echo ""
echo "📊 简报工具测试"
echo "────────────────────────────────────────"

test_tool "brief_enhanced" "生成简报，主题测试，要点：要点 1、要点 2、要点 3" "简报"

echo ""
echo "⚙️  配置工具测试"
echo "────────────────────────────────────────"

test_tool "config_enhanced" "设置配置 test.key 为 testvalue" "配置"

echo ""
echo "═══════════════════════════════════════════════════════"
echo "测试结果汇总"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "✅ 通过：$PASSED"
echo "❌ 失败：$FAILED"
echo "⏭️  跳过：$SKIPPED"
echo ""

# 清理
cleanup

if [ $FAILED -eq 0 ]; then
    echo "🎉 所有测试通过！"
    exit 0
else
    echo "⚠️  有 $FAILED 个测试失败"
    exit 1
fi
