#!/bin/bash

# 系统性测试所有工具（完整版 - 40 个工具）
# 使用方式：./test-all-tools-full.sh

set -e

echo "╔═══════════════════════════════════════════════════════╗"
echo "║   Source Deploy - 全面工具测试 (40 个工具完整版)        ║"
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
    
    if echo "exit" | timeout 30 ./start.sh -p "$command" 2>&1 | grep -qi "$expected"; then
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
    rm -f test-*.txt test-*.py test-*.md test-*.json 2>/dev/null || true
    rm -rf test-dir-* 2>/dev/null || true
}

# 开始测试
echo "📁 文件操作工具测试 (5 个)"
echo "────────────────────────────────────────"

test_tool "file_write" "用 file_write 创建文件 test-write.txt 内容是'Hello World'" "文件.*创建"
test_tool "file_read" "读取 test-write.txt 的内容" "Hello World"
test_tool "file_edit" "编辑 test-write.txt，把 Hello 改成 Hi" "编辑.*完成"
test_tool "file_delete" "删除文件 test-write.txt" "删除"
test_tool "directory_create" "创建目录 test-dir-1" "目录.*创建"

echo ""
echo "🔍 搜索工具测试 (2 个)"
echo "────────────────────────────────────────"

test_tool "grep" "在 test-edit.txt 中搜索 Hi" "搜索"
test_tool "glob" "查找当前目录所有.txt 文件" ".txt"

echo ""
echo "📋 Task 管理工具测试 (13 个)"
echo "────────────────────────────────────────"

test_tool "task_create" "创建任务：测试任务 1" "任务"
test_tool "task_create_enhanced" "创建任务：测试任务 2，优先级 high" "任务创建"
test_tool "task_update" "更新任务状态" "更新"
test_tool "task_update_enhanced" "更新任务为已完成" "更新"
test_tool "task_get" "获取任务详情" "任务详情"
test_tool "task_get_enhanced" "获取任务详细信息" "详情"
test_tool "task_list" "查看任务列表" "任务"
test_tool "task_list_enhanced" "查看所有任务" "任务列表"
test_tool "task_stop" "停止任务" "停止"
test_tool "task_output" "查看任务输出" "输出"
test_tool "task_complete" "完成任务" "完成"
test_tool "task_complete_enhanced" "完成任务并总结" "完成"
test_tool "task_delete" "删除任务" "删除"
test_tool "task_delete_enhanced" "删除任务并确认" "删除"

echo ""
echo "🔧 Bash 工具测试 (1 个)"
echo "────────────────────────────────────────"

test_tool "bash" "用 bash 执行 echo 'Hello'" "Hello"

echo ""
echo "📊 简报工具测试 (2 个)"
echo "────────────────────────────────────────"

test_tool "brief" "生成简报，主题测试" "简报"
test_tool "brief_enhanced" "生成简报，主题测试，要点：要点 1、要点 2" "简报"

echo ""
echo "⚙️  配置工具测试 (1 个)"
echo "────────────────────────────────────────"

test_tool "config_enhanced" "设置配置 test.key 为 testvalue" "配置"

echo ""
echo "💬 交互工具测试 (2 个)"
echo "────────────────────────────────────────"

test_tool "ask_user" "问用户问题" "问"
test_tool "ask_user_question" "问用户：你喜欢什么颜色" "问题"

echo ""
echo "🌐 网络工具测试 (2 个)"
echo "────────────────────────────────────────"

test_tool "web_search" "搜索 Python 教程" "搜索"
test_tool "web_fetch_enhanced" "获取网页 https://example.com 的内容" "获取"

echo ""
echo "🤖 技能工具测试 (2 个)"
echo "────────────────────────────────────────"

test_tool "skill" "列出所有技能" "技能"
test_tool "skill_enhanced" "列出所有技能" "技能"

echo ""
echo "👥 代理工具测试 (2 个)"
echo "────────────────────────────────────────"

test_tool "agent" "列出所有代理" "代理"
test_tool "agent_enhanced" "列出所有代理" "代理"

echo ""
echo "💻 LSP 工具测试 (2 个)"
echo "────────────────────────────────────────"

test_tool "lsp" "诊断当前文件" "诊断"
test_tool "lsp_enhanced" "诊断 package.json" "诊断"

echo ""
echo "📡 MCP 工具测试 (3 个)"
echo "────────────────────────────────────────"

test_tool "mcp" "列出 MCP 资源" "MCP"
test_tool "list_mcp_resources" "列出所有 MCP 服务器" "MCP"
test_tool "read_mcp_resource" "读取 MCP 资源" "MCP"

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

TOTAL=$((PASSED + FAILED))
if [ $TOTAL -gt 0 ]; then
    RATE=$((PASSED * 100 / TOTAL))
    echo "通过率：${RATE}%"
fi

if [ $FAILED -eq 0 ]; then
    echo "🎉 所有测试通过！"
    exit 0
else
    echo "⚠️  有 $FAILED 个测试失败"
    exit 1
fi
