# 📖 交互模式使用指南

**更新时间**: 2026-04-06 22:58

---

## 🎯 当前交互模式

### 简化输出模式（默认）

**特点**:
- ✅ 工具调用自动执行
- ✅ 结果直接显示
- ⚠️ 不显示详细工具调用过程

**示例**:
```bash
❯ 创建文件 test.txt 内容是'Hello'

文件 `test.txt` 已成功创建，内容为"Hello"。
```

**背后执行**:
```
1. AI 分析请求
2. 调用 file_write 工具
3. 执行文件创建
4. 显示结果
```

---

## 🔍 查看详细工具调用

### 方法 1: 使用详细模式

```bash
./start.sh --verbose "创建文件 test.txt"
```

**输出**:
```
[INFO] 使用 Qwen 作为 LLM Provider
[INFO] Registered 40 tools
[DEBUG] Turn 1/15
[DEBUG] LLM response: content=0, toolCalls=1
[DEBUG] Checking tool call: file_write
🔧 正在调用工具：file_write
   参数：{"file_path": "test.txt", "content": "Hello"}
✅ 文件创建成功
```

---

### 方法 2: 查看日志文件

```bash
# 设置日志级别为 debug
export LOG_LEVEL=debug
./start.sh "创建文件"
```

---

## 🛠️ 工具调用机制

### 工作流程

```
用户请求
  ↓
AI 分析 → 决定使用哪个工具
  ↓
调用工具 → 执行操作
  ↓
返回结果 → 显示给用户
```

---

### 可用工具（40 个）

**文件操作** (5 个):
- file_read - 读取文件
- file_write - 创建文件
- file_edit - 编辑文件
- file_delete - 删除文件
- directory_create - 创建目录

**搜索工具** (2 个):
- grep - 文本搜索
- glob - 文件匹配

**任务管理** (8 个):
- task_create - 创建任务
- task_update - 更新任务
- task_get - 查看详情
- task_list - 查看列表
- task_stop - 停止任务
- task_output - 查看输出
- task_complete - 完成任务
- task_delete - 删除任务

**增强版工具** (12 个):
- task_create_enhanced - 【推荐】创建任务
- task_update_enhanced - 【推荐】更新任务
- task_get_enhanced - 【推荐】查看详情
- task_list_enhanced - 【推荐】查看列表
- task_stop_enhanced - 【推荐】停止任务
- task_output_enhanced - 【推荐】查看输出
- task_complete_enhanced - 【推荐】完成任务
- task_delete_enhanced - 【推荐】删除任务
- skill_enhanced - 【推荐】技能管理
- agent_enhanced - 【推荐】代理管理
- lsp_enhanced - 【推荐】代码智能
- config_enhanced - 【推荐】配置管理
- web_fetch_enhanced - 【推荐】网页获取
- send_message_enhanced - 【推荐】消息发送

**其他工具** (13 个):
- bash - 执行命令
- brief - 简报生成
- 等等...

---

## 💡 使用技巧

### 1. 明确指定工具

```bash
# 使用增强版
❯ 用 task_create_enhanced 创建任务：xxx

# 使用简化版
❯ 用 task_create 创建任务：xxx
```

---

### 2. 查看详细执行

```bash
# 开启 debug 日志
export LOG_LEVEL=debug
./start.sh "创建文件"

# 查看完整工具调用流程
```

---

### 3. 复杂任务分解

```bash
# 不要一次性做太多
❯ 创建项目，包含 src/tests/docs，初始化 git，安装依赖

# 分解为多个步骤
❯ 创建目录 src tests docs
❯ 初始化 git
❯ 安装依赖
```

---

## ⚙️ 配置选项

### 日志级别

```bash
# .env 文件
LOG_LEVEL=info     # 默认（简洁输出）
LOG_LEVEL=debug    # 调试模式（详细输出）
LOG_LEVEL=warn     # 仅警告
LOG_LEVEL=error    # 仅错误
```

---

### 工具调用轮数

```typescript
// src/core/QueryEngine.ts
const MAX_TURNS = 15;  // 最多 15 轮工具调用
```

---

## 🐛 常见问题

### Q: 为什么看不到工具调用过程？

**A**: 默认使用简化输出模式。要查看详细过程：
```bash
export LOG_LEVEL=debug
./start.sh "创建文件"
```

---

### Q: 工具调用失败怎么办？

**A**: 检查日志：
```bash
export LOG_LEVEL=debug
./start.sh "操作"
# 查看错误信息
```

---

### Q: 复杂任务做到一半停止？

**A**: 增加 MAX_TURNS：
```typescript
// 从 15 增加到 30
const MAX_TURNS = 30;
```

---

## 📊 性能优化

### 当前设置

| 配置 | 值 | 说明 |
|------|-----|------|
| **MAX_TURNS** | 15 | 最多 15 轮工具调用 |
| **LOG_LEVEL** | info | 简洁输出 |
| **打字速度** | 15ms/字符 | 流式输出速度 |

---

### 调整建议

**需要更详细输出**:
```bash
export LOG_LEVEL=debug
```

**需要支持更复杂任务**:
```typescript
const MAX_TURNS = 30;  // 增加到 30 轮
```

**需要更快响应**:
```typescript
// 减少打字速度
await new Promise(r => setTimeout(r, 5));  // 5ms/字符
```

---

## ✅ 总结

**当前状态**:
- ✅ 工具功能正常（40 个工具可用）
- ✅ 增强版工具优先（15 个增强版）
- ✅ 简化输出模式（默认）
- ✅ 支持详细日志（debug 模式）

**推荐使用**:
- ✅ 日常使用简化模式
- ✅ 调试时使用 debug 模式
- ✅ 复杂任务分解为多步

---

_更新时间：2026-04-06 22:58_  
_工具数量：40 个_  
_默认模式：简化输出_  
_详细模式：LOG_LEVEL=debug_
