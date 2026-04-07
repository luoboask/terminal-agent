# 📝 文件系统权限说明

**更新时间**: 2026-04-06 21:36

---

## ⚠️ 遇到的错误

```
❌ 失败：EROFS: read-only file system, open '/robot_battle.py'
```

---

## 🔍 原因分析

### 问题

AI 尝试在**根目录 `/`** 创建文件：
```python
/robot_battle.py  # ❌ 根目录，只读文件系统
```

### 为什么失败

1. **系统保护** - 根目录是只读的（安全机制）
2. **权限不足** - 普通用户不能在 `/` 创建文件
3. **正确做法** - 应该在当前目录或用户目录创建

---

## ✅ 正确的使用方式

### 方式 1: 在当前目录创建

```bash
❯ 在当前目录创建 robot_battle.py
✅ 文件已创建：./robot_battle.py
```

### 方式 2: 指定明确的路径

```bash
❯ 创建文件 ./games/robot_battle.py
✅ 文件已创建：games/robot_battle.py
```

### 方式 3: 在用户目录创建

```bash
❯ 在 ~/projects 创建 robot_battle.py
✅ 文件已创建：/Users/yourname/projects/robot_battle.py
```

---

## 📋 权限规则

### ✅ 可以写入的位置

| 位置 | 说明 | 示例 |
|------|------|------|
| **当前目录** | 你所在的目录 | `./file.py` |
| **子目录** | 当前目录的子目录 | `./src/file.py` |
| **用户目录** | 你的家目录 | `~/file.py` |
| **临时目录** | /tmp | `/tmp/file.py` |

### ❌ 不能写入的位置

| 位置 | 原因 |
|------|------|
| **根目录 /** | 系统保护，只读 |
| **系统目录** | /usr, /bin, /etc 等 |
| **其他用户目录** | 权限不足 |

---

## 💡 最佳实践

### 1. 使用相对路径

```bash
# ✅ 推荐
❯ 创建文件 src/game.py
❯ 在当前目录创建 test.py

# ❌ 不推荐
❯ 创建文件 /game.py  # 绝对路径，可能在根目录
```

### 2. 明确指定目录

```bash
# ✅ 清晰明确
❯ 在 projects 目录创建 game.py
❯ 在当前目录的 games 子目录创建 robot_battle.py
```

### 3. 使用当前工作目录

Source Deploy 默认在**当前工作目录**操作：
```bash
cd ~/.openclaw/workspace-claude-code-agent/source-deploy
./start.sh "创建文件 test.py"  # 会在当前目录创建
```

---

## 🔧 如果需要在特殊位置创建

### 方法 1: 先创建目录

```bash
# 在用户目录创建项目
mkdir -p ~/projects/game
cd ~/projects/game
./start.sh "创建 robot_battle.py"
```

### 方法 2: 使用 sudo（不推荐）

```bash
# ⚠️ 谨慎使用
sudo ./start.sh "在 /usr/local 创建文件"
```

### 方法 3: 修改权限（需要管理员权限）

```bash
# ⚠️ 仅在你确实需要时
sudo chmod u+w /some/directory
```

---

## 📊 实际案例对比

### 案例 1: 错误示范 ❌

```bash
❯ 创建文件 /robot_battle.py

[错误] EROFS: read-only file system
原因：尝试在根目录创建
```

### 案例 2: 正确示范 ✅

```bash
❯ 在当前目录创建 robot_battle.py

📝 已创建

📁 文件：robot_battle.py
📏 大小：XXX 字符

✅ 完成
```

### 案例 3: 最佳实践 ⭐

```bash
❯ 创建项目目录 game_project，在里面创建 robot_battle.py

📁 已创建目录：game_project
📝 已创建文件：game_project/robot_battle.py

✅ 完成
```

---

## 🎯 总结

**记住这三点**:

1. ✅ **使用相对路径** - `./file.py` 而不是 `/file.py`
2. ✅ **在当前目录操作** - 默认就是安全的
3. ✅ **需要特殊位置先询问** - 系统会提示你

**Source Deploy 会自动**:
- ✅ 在当前目录创建文件
- ✅ 检查路径是否可写
- ✅ 提供友好的错误提示

---

_创建时间：2026-04-06 21:36_  
_权限级别：用户级_  
_推荐做法：相对路径 + 当前目录_
