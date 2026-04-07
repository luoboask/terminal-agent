# 工具状态清单

## 📊 总览

- **工具文件数**: 31 个
- **已注册工具**: 24 个
- **缺失注册**: 7 个

## ✅ 已注册工具 (24 个)

### 文件操作 (6 个)
1. ✅ bash
2. ✅ file_read
3. ✅ file_edit
4. ✅ grep
5. ✅ glob
6. ✅ file_write
7. ✅ directory_create

### 任务管理 (8 个)
8. ✅ task_create
9. ✅ task_update
10. ✅ task_get
11. ✅ task_list
12. ✅ task_stop
13. ✅ task_output
14. ✅ task_complete
15. ✅ task_delete

### MCP 服务器 (3 个)
16. ✅ list_mcp_resources
17. ✅ mcp
18. ✅ read_mcp_resource

### 通信与协作 (4 个)
19. ✅ send_message
20. ✅ brief
21. ✅ skill
22. ✅ agent

### 网络 (1 个)
23. ✅ web_fetch

### 其他 (2 个)
24. ✅ lsp

## ❌ 未注册工具 (7 个)

1. ❌ file_delete - 文件删除工具
2. ❌ git_diff - Git 差异工具
3. ❌ worktree - Git Worktree 工具
4. ❌ todo_write - Todo 列表工具
5. ❌ web_search - 网络搜索工具
6. ❌ ask_user - 用户问答工具
7. ❌ ask_user_question - 用户问答工具（多选）

## 🔧 修复建议

在 `src/index.ts` 中添加以下注册：

```typescript
registry.register(new FileDeleteTool());
registry.register(new GitDiffTool());
registry.register(new WorktreeTool());
registry.register(new TodoWriteTool());
registry.register(new WebSearchTool());
registry.register(new AskUserTool());
```

## 📝 备注

- `ask_user` 和 `ask_user_question` 可能是同一个工具的不同名称
- 部分工具可能已废弃或正在开发中
