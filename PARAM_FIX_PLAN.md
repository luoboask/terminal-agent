# 🔧 参数命名统一修复计划

**问题**: FileRead 等工具的参数名不一致（`path` vs `file_path`）

**影响**: LLM 调用工具时传递错误的参数名，导致 `undefined` 错误

**解决方案**: 统一所有工具的参数命名为 `file_path`, `dir_path`, `path`

---

## 📋 待修复的工具

| 工具 | 当前参数名 | 应改为 | 文件 |
|------|-----------|--------|------|
| FileRead | `path` | `file_path` | FileRead.ts |
| Glob | `pattern` | ✅ 已正确 | - |
| Grep | `pattern`, `path` | `pattern`, `search_path` | Grep.ts |

---

## 🔍 检查清单

```bash
# 检查所有工具的参数定义
grep -n "z.object" src/tools/*.ts | head -20
```

---

开始修复...
