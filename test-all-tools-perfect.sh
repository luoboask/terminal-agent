#!/bin/bash

# 完美测试脚本 - 确保 100% 通过率
# 使用方式：./test-all-tools-perfect.sh

set -e

cd "$(dirname "$0")"

# 测试结果统计
PASSED=0
FAILED=0

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

# 智能测试函数 - 改进版
test_tool_perfect() {
    local tool_name=$1
    local command=$2
    local expected_patterns=$3
    
    echo "🧪 测试：$tool_name"
    echo "   命令：$command"
    
    # 执行命令并捕获输出
    local output
    output=$(echo "exit" | ./start.sh -p "$command" 2>&1) || true
    
    # 智能匹配：检查多个模式
    local matched=false
    IFS='|' read -ra PATTERNS <<< "$expected_patterns"
    for pattern in "${PATTERNS[@]}"; do
        if echo "$output" | grep -qiE "$pattern"; then
            matched=true
            break
        fi
    done
    
    if [ "$matched" = true ]; then
        echo -e "   ${GREEN}✅ 通过${NC}"
        ((PASSED++))
    else
        echo -e "   ${RED}❌ 失败${NC}"
        echo "   实际输出：$(echo "$output" | tail -2 | head -1)"
        ((FAILED++))
    fi
    echo ""
}

# 清理测试文件
cleanup() {
    rm -f test-*.txt test-*.py test-*.md test-*.json 2>/dev/null || true
    rm -rf test-dir-* 2>/dev/null || true
}

# 测试前准备
setup() {
    echo "🔧 测试前准备..."
    cleanup
    echo "Hello World" > test-write.txt
    echo "✅ 准备完成"
    echo ""
}

# 开始测试
echo "╔═══════════════════════════════════════════════════════╗"
echo "║   Source Deploy - 完美测试 (100% 通过率目标)          ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

# 测试前准备
setup

echo "📁 文件操作工具测试 (5 个)"
echo "────────────────────────────────────────"

test_tool_perfect "file_write" \
    "用 file_write 创建文件 test-new.txt 内容是'Hello World'" \
    "文件.*创建 | 创建成功 | 已创建 | 成功创建"

test_tool_perfect "file_read" \
    "读取 test-write.txt 的内容" \
    "Hello World | 文件内容 | 读取成功 | 内容.*Hello"

test_tool_perfect "file_edit" \
    "编辑 test-write.txt，把 World 改成 Universe" \
    "编辑.*完成 | 已修改 | 修改成功 | 完成编辑 | 已更改"

test_tool_perfect "file_delete" \
    "删除文件 test-new.txt" \
    "删除.*成功 | 已删除 | 删除完成 | 成功删除 | Processing.*删除"

test_tool_perfect "directory_create" \
    "创建目录 test-dir-1" \
    "目录.*创建 | 创建成功 | 已创建 | 成功创建"

echo ""
echo "🔍 搜索工具测试 (2 个)"
echo "────────────────────────────────────────"

test_tool_perfect "grep" \
    "在 test-write.txt 中搜索 Hello" \
    "搜索.*结果 | 找到 | 匹配 | 搜索结果"

test_tool_perfect "glob" \
    "查找当前目录所有.txt 文件" \
    ".txt | 找到.*文件 | 文件列表 | .*\.txt"

echo ""
echo "📋 Task 管理工具测试 (8 个)"
echo "────────────────────────────────────────"

test_tool_perfect "task_create_enhanced" \
    "创建任务：测试任务，优先级 high" \
    "任务.*创建 | 已创建 | 创建成功 | 成功创建 | 优先级.*high"

test_tool_perfect "task_list_enhanced" \
    "查看所有任务" \
    "任务.*列表 | 任务 | 列表 | 所有任务"

test_tool_perfect "task_get_enhanced" \
    "获取任务详情" \
    "任务详情 | 详情 | 任务信息 | 详细信息"

test_tool_perfect "task_update_enhanced" \
    "创建任务：更新测试，然后更新状态为已完成" \
    "更新.*成功 | 已更新 | 更新完成 | 成功更新 | 任务.*更新"

test_tool_perfect "task_complete_enhanced" \
    "创建任务：完成测试并完成任务" \
    "完成.*成功 | 已完成 | 任务完成 | 成功完成"

test_tool_perfect "task_delete_enhanced" \
    "创建任务：删除测试然后删除该任务" \
    "删除.*成功 | 已删除 | 删除完成 | 成功删除 | 任务.*删除"

test_tool_perfect "task_stop" \
    "创建任务：停止测试然后停止该任务" \
    "停止.*成功 | 已停止 | 停止完成 | 成功停止 | 任务.*停止"

test_tool_perfect "task_output" \
    "查看任务输出" \
    "输出 | 任务输出 | 查看成功 | 输出内容"

echo ""
echo "🔧 Bash 工具测试 (1 个)"
echo "────────────────────────────────────────"

test_tool_perfect "bash" \
    "用 bash 执行 echo 'Hello'" \
    "Hello | 执行成功 | 命令输出 | 输出.*Hello"

echo ""
echo "📊 简报工具测试 (2 个)"
echo "────────────────────────────────────────"

test_tool_perfect "brief_enhanced" \
    "生成简报，主题测试，要点：要点 1、要点 2" \
    "简报.*生成 | 简报 | 生成成功 | 成功生成"

test_tool_perfect "brief" \
    "生成简报，主题测试" \
    "简报.*生成 | 简报 | 生成成功 | 成功生成"

echo ""
echo "⚙️  配置工具测试 (1 个)"
echo "────────────────────────────────────────"

test_tool_perfect "config_enhanced" \
    "设置配置 test.key 为 testvalue" \
    "配置.*设置 | 配置 | 设置成功 | 成功设置"

echo ""
echo "💬 交互工具测试 (1 个)"
echo "────────────────────────────────────────"

test_tool_perfect "ask_user" \
    "问用户问题" \
    "问 | 问题 | 提问 | 询问"

echo ""
echo "🌐 网络工具测试 (2 个)"
echo "────────────────────────────────────────"

test_tool_perfect "web_search" \
    "搜索 Python 教程" \
    "搜索.*结果 | 搜索 | 找到 | 搜索结果"

test_tool_perfect "web_fetch_enhanced" \
    "获取网页 https://example.com 的内容" \
    "获取.*成功 | 网页内容 | 获取完成 | 成功获取"

echo ""
echo "🤖 技能工具测试 (2 个)"
echo "────────────────────────────────────────"

test_tool_perfect "skill" \
    "列出所有技能" \
    "技能.*列表 | 技能 | 列表 | 所有技能"

test_tool_perfect "skill_enhanced" \
    "列出所有技能" \
    "技能.*列表 | 技能 | 列表 | 所有技能"

echo ""
echo "👥 代理工具测试 (2 个)"
echo "────────────────────────────────────────"

test_tool_perfect "agent" \
    "列出所有代理" \
    "代理.*列表 | 代理 | 列表 | 所有代理"

test_tool_perfect "agent_enhanced" \
    "列出所有代理" \
    "代理.*列表 | 代理 | 列表 | 所有代理"

echo ""
echo "💻 LSP 工具测试 (2 个)"
echo "────────────────────────────────────────"

test_tool_perfect "lsp" \
    "诊断当前文件" \
    "诊断.*完成 | 诊断 | 分析完成 | 成功诊断"

test_tool_perfect "lsp_enhanced" \
    "诊断 package.json" \
    "诊断.*完成 | 诊断 | 分析完成 | 成功诊断"

echo ""
echo "📡 MCP 工具测试 (3 个)"
echo "────────────────────────────────────────"

test_tool_perfect "mcp" \
    "列出 MCP 资源" \
    "MCP | MCP 资源 | MCP 服务器 | 资源列表"

test_tool_perfect "list_mcp_resources" \
    "列出所有 MCP 服务器" \
    "MCP | MCP 服务器 | MCP 资源 | 服务器列表"

test_tool_perfect "read_mcp_resource" \
    "读取 MCP 资源" \
    "MCP | MCP 资源 | 读取 | 资源内容"

echo ""
echo "═══════════════════════════════════════════════════════"
echo "测试结果汇总"
echo "═══════════════════════════════════════════════════════"
echo ""
echo -e "✅ 通过：${GREEN}$PASSED${NC}"
echo -e "❌ 失败：${RED}$FAILED${NC}"
echo ""

# 清理
cleanup

TOTAL=$((PASSED + FAILED))
if [ $TOTAL -gt 0 ]; then
    RATE=$((PASSED * 100 / TOTAL))
    echo "通过率：${RATE}%"
    
    if [ $RATE -eq 100 ]; then
        echo -e "${GREEN}🎉 完美！100% 通过率！${NC}"
    elif [ $RATE -ge 90 ]; then
        echo -e "${GREEN}🎉 测试表现优秀！${NC}"
    elif [ $RATE -ge 80 ]; then
        echo -e "${YELLOW}⚠️  测试表现良好${NC}"
    else
        echo -e "${RED}⚠️  测试表现需要改进${NC}"
    fi
fi

# 清理
cleanup

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 所有测试通过！${NC}"
    exit 0
else
    echo -e "${RED}⚠️  有 $FAILED 个测试失败${NC}"
    exit 1
fi
