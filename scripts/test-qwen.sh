#!/bin/bash

# Qwen Provider 测试脚本
# 用于验证 Qwen3.5-plus API 配置和连接

set -e

echo "╔═══════════════════════════════════════════════════════╗"
echo "║     Source Deploy - Qwen Provider 测试                ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

# 加载 .env 文件
if [ -f .env ]; then
    echo "📄 加载 .env 文件..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# 检查 API Key
if [ -z "$DASHSCOPE_API_KEY" ]; then
    echo "❌ 错误：DASHSCOPE_API_KEY 未设置"
    echo ""
    echo "请设置环境变量："
    echo "  export DASHSCOPE_API_KEY=sk-sp-xxxxxxxx"
    echo ""
    echo "或在 .env 文件中配置："
    echo "  DASHSCOPE_API_KEY=sk-sp-xxxxxxxx"
    exit 1
fi

echo "✅ API Key 已配置"

# 设置 Base URL
BASE_URL="${QWEN_BASE_URL:-https://coding.dashscope.aliyuncs.com/v1}"
echo "📍 Base URL: $BASE_URL"

# 设置模型
MODEL="${QWEN_MODEL:-qwen3.5-plus}"
echo "🤖 模型：$MODEL"
echo ""

# 测试连接
echo "🔗 测试 API 连接..."
echo ""

RESPONSE=$(curl -s -X POST "$BASE_URL/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -d "{
    \"model\": \"$MODEL\",
    \"messages\": [
      {
        \"role\": \"user\",
        \"content\": \"你好，请用一句话介绍你自己\"
      }
    ],
    \"max_tokens\": 100,
    \"enable_thinking\": true
  }")

# 解析响应
if echo "$RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
    ERROR_MSG=$(echo "$RESPONSE" | jq -r '.error.message')
    echo "❌ API 请求失败："
    echo "   $ERROR_MSG"
    exit 1
fi

CONTENT=$(echo "$RESPONSE" | jq -r '.choices[0].message.content')
REASONING=$(echo "$RESPONSE" | jq -r '.choices[0].message.reasoning_content // empty')
USAGE=$(echo "$RESPONSE" | jq -r '.usage')

echo "✅ 连接成功！"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 响应内容:"
echo ""
if [ -n "$REASONING" ]; then
    echo "💭 思考过程："
    echo "   $REASONING"
    echo ""
fi
echo "🤖 $CONTENT"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Token 使用:"
echo "   Prompt Tokens: $(echo "$USAGE" | jq -r '.prompt_tokens')"
echo "   Completion Tokens: $(echo "$USAGE" | jq -r '.completion_tokens')"
echo "   Total Tokens: $(echo "$USAGE" | jq -r '.total_tokens')"
echo ""

echo "✅ Qwen Provider 测试完成！"
echo ""
echo "下一步："
echo "  1. 运行 'bun start' 启动 REPL 交互模式"
echo "  2. 运行 'bun start --prompt \"你的问题\"' 直接执行"
echo "  3. 查看 README.md 了解更多用法"
echo ""
