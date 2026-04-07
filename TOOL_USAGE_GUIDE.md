# 工具使用指南

## 📊 工具总览

系统共有 **31 个工具**，分为以下几类：

### 文件操作 (7 个)
| 工具 | 用途 | 使用场景 |
|------|------|---------|
| `file_read` | 读取文件 | 查看文件内容（支持批量） |
| `file_write` | 创建文件 | 创建新文件 |
| `file_edit` | 编辑文件 | 修改现有文件内容 |
| `file_delete` | 删除文件 | 删除不需要的文件 |
| `directory_create` | 创建目录 | 创建文件夹 |
| `glob` | 文件搜索 | 查找匹配模式的文件 |
| `grep` | 文本搜索 | 在文件中搜索文本 |

### Git 工具 (2 个)
| 工具 | 用途 | 使用场景 |
|------|------|---------|
| `git_diff` | 查看变更 | 查看代码修改 |
| `worktree` | Git 工作树 | 管理多分支开发 |

### 任务管理 (8 个)
| 工具 | 用途 | 使用场景 |
|------|------|---------|
| `task_create` | 创建任务 | 记录待办事项 |
| `task_list` | 列出任务 | 查看任务列表 |
| `task_get` | 获取任务 | 查看任务详情 |
| `task_update` | 更新任务 | 修改任务状态 |
| `task_stop` | 停止任务 | 停止运行中的任务 |
| `task_output` | 获取输出 | 查看任务日志 |
| `task_complete` | 完成任务 | 标记任务完成 |
| `task_delete` | 删除任务 | 删除任务记录 |

### 项目分析 (1 个) ⭐ **推荐**
| 工具 | 用途 | 使用场景 |
|------|------|---------|
| `project_summary` | 项目总结 | **快速了解整个项目** |

### 网络工具 (2 个)
| 工具 | 用途 | 使用场景 |
|------|------|---------|
| `web_search` | 网络搜索 | 搜索信息 |
| `web_fetch` | 获取网页 | 抓取网页内容 |

### 命令执行 (1 个)
| 工具 | 用途 | 使用场景 |
|------|------|---------|
| `bash` | 执行命令 | 运行 shell 命令/脚本 |

### 其他工具 (10 个)
| 工具 | 用途 |
|------|------|
| `todo_write` | Todo 列表 |
| `send_message` | 发送消息 |
| `brief` | 生成简报 |
| `skill` | 技能管理 |
| `agent` | Agent 管理 |
| `list_mcp_resources` | MCP 资源 |
| `mcp` | MCP 工具调用 |
| `read_mcp_resource` | 读取 MCP 资源 |
| `lsp` | LSP 工具 |
| `ask_user` | 用户问答 |

---

## 🎯 常用场景推荐

### 场景 1：了解新项目
```bash
# 推荐：使用 project_summary
project_summary(project_path="my-project")

# 不推荐：手动读取多个文件
file_read(file_path="file1.py")
file_read(file_path="file2.py")
...
```

### 场景 2：查找文件
```bash
# 使用 glob
glob(pattern="*.py", path="src")
```

### 场景 3：查找代码
```bash
# 使用 grep
grep(pattern="def login", path="src")
```

### 场景 4：批量读取
```bash
# 使用 file_read 的 file_paths 参数
file_read(file_paths=["file1.py", "file2.py", "file3.py"])
```

### 场景 5：查看 Git 变更
```bash
# 使用 git_diff
git_diff()
```

### 场景 6：运行测试
```bash
# 使用 bash
bash(command="python3 test.py")
```

---

## 💡 工具选择建议

### ✅ 推荐使用
1. **`project_summary`** - 快速了解项目（最常用）
2. **`file_read` + `file_paths`** - 批量读取文件
3. **`glob`** - 查找文件
4. **`bash`** - 运行命令/脚本

### ⚠️ 谨慎使用
1. **`file_read` 单个文件** - 优先使用批量读取
2. **`task_*` 系列** - 除非需要任务管理
3. **`mcp_*` 系列** - 除非配置了 MCP

### ❌ 避免滥用
1. **重复读取同一文件** - 读取 1 次就够了
2. **无限读取不同文件** - 最多 3-5 个文件后总结
3. **不总结继续读取** - 读取后必须总结

---

## 📝 最佳实践

### 1. 项目分析
```bash
# ✅ 推荐
project_summary(project_path="my-project")

# ❌ 不推荐
file_read(file_path="file1.py")
file_read(file_path="file2.py")
file_read(file_path="file3.py")
...
```

### 2. 文件操作
```bash
# ✅ 推荐：批量读取
file_read(file_paths=["a.py", "b.py", "c.py"])

# ❌ 不推荐：逐个读取
file_read(file_path="a.py")
file_read(file_path="b.py")
file_read(file_path="c.py")
```

### 3. 搜索操作
```bash
# ✅ 推荐：使用专用工具
glob(pattern="*.py")  # 找文件
grep(pattern="def ")  # 找代码

# ❌ 不推荐：用 bash
bash(command="find . -name '*.py'")
bash(command="grep -r 'def ' .")
```

### 4. 任务管理
```bash
# ✅ 推荐：复杂项目使用
task_create(subject="实现功能 A")
task_create(subject="实现功能 B")
task_list()

# ❌ 不推荐：简单任务使用
# 简单任务直接做，不需要创建任务
```

---

## 🎯 总结

**最常用工具（占 80% 使用）：**
1. `project_summary` - 项目分析
2. `file_read` - 读取文件
3. `file_write` - 创建文件
4. `bash` - 执行命令
5. `glob` - 查找文件

**按需使用（占 15% 使用）：**
- `file_edit`, `grep`, `git_diff`, `task_*`

**特殊场景（占 5% 使用）：**
- `web_*`, `mcp_*`, `skill`, `agent`

**记住：** 工具在精不在多，掌握核心工具就能完成大部分任务！
