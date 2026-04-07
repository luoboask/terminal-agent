#!/bin/bash

echo "========================================"
echo "🧪 测试所有 34 个工具"
echo "========================================"
echo ""

# 文件操作工具 (7 个)
echo "📁 文件操作工具 (7 个)"
echo "1️⃣ file_read..." && ./start.sh "读取 pet-system/pet.py" 2>&1 | grep -E "成功 | 失败 | ❌" | head -1
echo "2️⃣ file_write..." && ./start.sh "创建文件 test-tool.txt 内容是 Test" 2>&1 | grep -E "成功 | 失败 | ❌" | head -1
echo "3️⃣ file_edit..." && ./start.sh "编辑文件 test-tool.txt，把 Test 改成 Hello" 2>&1 | grep -E "成功 | 失败 | ❌" | head -1
echo "4️⃣ file_delete..." && ./start.sh "删除文件 test-tool.txt" 2>&1 | grep -E "成功 | 失败 | ❌" | head -1
echo "5️⃣ directory_create..." && ./start.sh "创建目录 test-dir" 2>&1 | grep -E "成功 | 失败 | ❌" | head -1
echo "6️⃣ glob..." && ./start.sh "查找所有 txt 文件" 2>&1 | grep -E "找到 | 失败 | ❌" | head -1
echo "7️⃣ grep..." && ./start.sh "在 src 目录搜索 import" 2>&1 | grep -E "找到 | 失败 | ❌" | head -1
echo ""

# 搜索工具 (2 个)
echo "🔍 搜索工具 (2 个)"
echo "8️⃣ web_search..." && ./start.sh "搜索 Python 新闻" 2>&1 | grep -E "成功 | 失败 | ❌" | head -1
echo "9️⃣ web_fetch..." && ./start.sh "获取 https://example.com 内容" 2>&1 | grep -E "成功 | 失败 | ❌" | head -1
echo ""

# 任务管理工具 (8 个)
echo "📋 任务管理工具 (8 个)"
echo "🔟 task_create..." && ./start.sh "创建任务：测试任务" 2>&1 | grep -E "成功 | 失败 | ❌" | head -1
echo "1️⃣1️⃣ task_list..." && ./start.sh "列出所有任务" 2>&1 | grep -E "成功 | 失败 | ❌" | head -1
echo "1️⃣2️⃣ task_get..." && ./start.sh "获取第一个任务的详情" 2>&1 | grep -E "成功 | 失败 | ❌" | head -1
echo "1️⃣3️⃣ task_update..." && ./start.sh "更新第一个任务状态为 in_progress" 2>&1 | grep -E "成功 | 失败 | ❌" | head -1
echo "1️⃣4️⃣ task_complete..." && ./start.sh "完成第一个任务" 2>&1 | grep -E "成功 | 失败 | ❌" | head -1
echo "1️⃣5️⃣ task_stop..." && ./start.sh "停止第一个任务" 2>&1 | grep -E "成功 | 失败 | ❌" | head -1
echo "1️⃣6️⃣ task_output..." && ./start.sh "获取第一个任务的输出" 2>&1 | grep -E "成功 | 失败 | ❌" | head -1
echo "1️⃣7️⃣ task_delete..." && ./start.sh "删除第一个任务" 2>&1 | grep -E "成功 | 失败 | ❌" | head -1
echo ""

# 会话和缓存工具 (3 个)
echo "💾 会话和缓存工具 (3 个)"
echo "1️⃣8️⃣ session_save..." && ./start.sh "保存当前会话" 2>&1 | grep -E "成功 | 失败 | ❌" | head -1
echo "1️⃣9️⃣ session_load..." && ./start.sh "加载会话 session-history.json" 2>&1 | grep -E "成功 | 失败 | ❌" | head -1
echo "2️⃣0️⃣ file_cache..." && ./start.sh "使用 file_cache 查看缓存" 2>&1 | grep -E "成功 | 失败 | ❌" | head -1
echo ""

# 项目和工具管理 (2 个)
echo "📊 项目和工具管理 (2 个)"
echo "2️⃣1️⃣ project_summary..." && ./start.sh "总结当前项目" 2>&1 | grep -E "成功 | 失败 | ❌" | head -1
echo "2️⃣2️⃣ brief..." && ./start.sh "生成项目简报" 2>&1 | grep -E "成功 | 失败 | ❌" | head -1
echo ""

# 其他工具 (12 个)
echo "🔧 其他工具 (12 个)"
echo "2️⃣3️⃣ bash..." && ./start.sh "运行命令 echo Hello" 2>&1 | grep -E "成功 | 失败 | ❌" | head -1
echo "2️⃣4️⃣ git_diff..." && ./start.sh "查看 git 变更" 2>&1 | grep -E "成功 | 失败 | ❌" | head -1
echo "2️⃣5️⃣ worktree..." && ./start.sh "查看 worktree 状态" 2>&1 | grep -E "成功 | 失败 | ❌" | head -1
echo "2️⃣6️⃣ todo_write..." && ./start.sh "创建 todo 项：测试" 2>&1 | grep -E "成功 | 失败 | ❌" | head -1
echo "2️⃣7️⃣ ask_user..." && ./start.sh "问用户一个问题" 2>&1 | grep -E "成功 | 失败 | ❌" | head -1
echo "2️⃣8️⃣ skill..." && ./start.sh "列出可用技能" 2>&1 | grep -E "成功 | 失败 | ❌" | head -1
echo "2️⃣9️⃣ agent..." && ./start.sh "列出可用 agent" 2>&1 | grep -E "成功 | 失败 | ❌" | head -1
echo "3️⃣0️⃣ send_message..." && ./start.sh "发送测试消息" 2>&1 | grep -E "成功 | 失败 | ❌" | head -1
echo "3️⃣1️⃣ list_mcp_resources..." && ./start.sh "列出 MCP 资源" 2>&1 | grep -E "成功 | 失败 | ❌" | head -1
echo "3️⃣2️⃣ read_mcp_resource..." && ./start.sh "读取 MCP 资源" 2>&1 | grep -E "成功 | 失败 | ❌" | head -1
echo "3️⃣3️⃣ mcp..." && ./start.sh "调用 MCP 工具" 2>&1 | grep -E "成功 | 失败 | ❌" | head -1
echo "3️⃣4️⃣ lsp..." && ./start.sh "LSP 代码分析" 2>&1 | grep -E "成功 | 失败 | ❌" | head -1
echo ""

# 清理测试文件
rm -f test-tool.txt 2>/dev/null
rm -rf test-dir 2>/dev/null

echo "========================================"
echo "✅ 34 个工具测试完成"
echo "========================================"
