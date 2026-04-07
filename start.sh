#!/bin/bash

# ============================================
# Source Deploy 启动脚本
# ============================================
# 用法：
#   ./start.sh              # 交互模式
#   ./start.sh "创建文件"    # 直接执行提示
#   ./start.sh --help       # 显示帮助
# ============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 脚本目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查 .env 文件
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  未找到 .env 文件${NC}"
    echo ""
    echo "请先配置环境变量："
    echo "  cp .env.example .env"
    echo "  vi .env  # 编辑并填入 DASHSCOPE_API_KEY"
    echo ""
    echo "或者使用命令行参数："
    echo "  ./start.sh --api-key YOUR_API_KEY \"你的提示\""
    echo ""
    exit 1
fi

# 检查 Bun 是否安装
if ! command -v bun &> /dev/null; then
    echo -e "${RED}❌ 错误：未找到 Bun${NC}"
    echo ""
    echo "请先安装 Bun: https://bun.sh/"
    echo "  curl -fsSL https://bun.sh/install | bash"
    echo ""
    exit 1
fi

# 设置日志级别（不打印任何日志到用户侧）
export LOG_LEVEL=none

# 解析命令行参数
PROMPT=""
API_KEY=""
VERBOSE=false
HELP=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --api-key)
            API_KEY="$2"
            shift 2
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --help|-h)
            HELP=true
            shift
            ;;
        *)
            PROMPT="$1"
            shift
            ;;
    esac
done

# 显示帮助
if [ "$HELP" = true ]; then
    echo -e "${BLUE}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║     Source Deploy - Claude Code Local Version         ║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "用法:"
    echo "  ./start.sh                          # 交互模式"
    echo "  ./start.sh \"你的提示\"                # 直接执行提示"
    echo "  ./start.sh --api-key KEY \"提示\"     # 指定 API Key"
    echo "  ./start.sh --verbose                # 详细日志模式"
    echo "  ./start.sh --help                   # 显示帮助"
    echo ""
    echo "示例:"
    echo "  ./start.sh"
    echo "  ./start.sh \"创建文件 test.txt 内容是'Hello'\""
    echo "  ./start.sh --verbose \"搜索代码中的 TODO\""
    echo ""
    exit 0
fi

# 构建启动命令
CMD="bun run src/index.ts"

# 添加 verbose 选项
if [ "$VERBOSE" = true ]; then
    CMD="$CMD --verbose"
fi

# 添加 API Key
if [ -n "$API_KEY" ]; then
    CMD="$CMD --api-key $API_KEY"
fi

# 添加提示
if [ -n "$PROMPT" ]; then
    CMD="$CMD --prompt \"$PROMPT\""
fi

# 显示启动信息
echo -e "${BLUE}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Source Deploy - Claude Code Local Version         ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

if [ -n "$PROMPT" ]; then
    echo -e "${GREEN}执行提示:${NC} $PROMPT"
    echo ""
else
    echo -e "${GREEN}进入交互模式${NC}"
    echo -e "${YELLOW}提示:${NC} 输入命令后按回车，输入 'exit' 或 Ctrl+C 退出"
    echo ""
fi

# 执行
eval $CMD
