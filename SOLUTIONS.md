# 🔧 Source Deploy 三大挑战解决方案

**更新时间**: 2026-04-06 19:14  
**目标**: 解决实际使用中的痛点

---

## 挑战 1: 大文件编辑需要精确定位

### ❌ 问题场景

```
❯ 在 plane-game.html 中添加碰撞检测函数

[Agent 困惑]
- 文件有 256 行，插在哪里？
- 是覆盖还是插入？
- 会不会破坏现有代码？
```

### ✅ 解决方案

#### 方案 A: 指定行号（最精确）⭐⭐⭐⭐⭐

```bash
# 先查看文件结构，找到目标行号
grep -n "function gameLoop" plane-game.html
# 输出：159:        function gameLoop() {

# 然后明确告诉 Agent
❯ 在第 159 行的 gameLoop 函数前面添加碰撞检测函数
```

**优点**: 
- ✅ 100% 精确
- ✅ 不会误操作
- ✅ Agent 理解无歧义

**工具辅助**:
```bash
# 快速查找行号
grep -n "TODO\|FIXME\|这里添加" file.txt

# 查看特定行范围
sed -n '150,170p' file.txt
```

---

#### 方案 B: 锚点定位（自然语言）⭐⭐⭐⭐

```bash
❯ 在 updateBullets 函数后面添加 checkCollisions 函数
❯ 在 HTML 的 </head>标签前添加新的<style>块
❯ 在 package.json 的 dependencies 字段里添加新依赖
```

**优点**:
- ✅ 不需要记行号
- ✅ 用代码结构定位
- ✅ 更自然

**技巧**:
- 使用函数名、标签名、字段名作为锚点
- 说明是"前面"、"后面"、"里面"

---

#### 方案 C: 分块编辑（适合超大文件）⭐⭐⭐

```bash
# 把大文件拆成小块
❯ 把 plane-game.html 的玩家代码提取到 player.js
❯ 把敌机代码提取到 enemies.js
❯ 然后在主文件中引用这些模块
```

**优点**:
- ✅ 每个文件都小
- ✅ 易于维护
- ✅ 可以并行开发

---

#### 方案 D: Bash 辅助（终极方案）⭐⭐⭐⭐

当 Agent 搞不定时，直接用 bash：

```bash
# 示例：在第 X 行后插入内容
head -n 159 plane-game.html > /tmp/part1.txt
cat new-code.txt >> /tmp/part1.txt
tail -n +160 plane-game.html >> /tmp/part1.txt
mv /tmp/part1.txt plane-game.html

# 示例：替换第 X-Y 行
sed -i 'X,Yd' plane-game.html  # 先删除
# 再插入...
```

**封装成脚本**:
```bash
#!/bin/bash
# insert-after.sh - 在某行后插入文件
FILE=$1
LINE=$2
INSERT_FILE=$3

head -n $LINE $FILE > /tmp/temp.txt
cat $INSERT_FILE >> /tmp/temp.txt
tail -n +$((LINE + 1)) $FILE >> /tmp/temp.txt
mv /tmp/temp.txt $FILE
echo "✅ 已在第 $LINE 行后插入内容"
```

使用：
```bash
./insert-after.sh plane-game.html 159 collision-code.txt
```

---

## 挑战 2: 连续读取会被重复检测阻止

### ❌ 问题场景

```
❯ 修改 plane-game.html，先读取看看

Turn 1: [Agent 调用 file_read]
⚠️ Blocked: 检测到重复调用 file_read
Turn 2: [Agent 再次尝试 file_read]
⚠️ Blocked again!
```

### ✅ 解决方案

#### 方案 A: 一次性说明需求（推荐）⭐⭐⭐⭐⭐

```bash
# ❌ 错误方式（会触发重复检测）
❯ 先读取 plane-game.html
❯ 然后在第 100 行添加代码

# ✅ 正确方式（一步到位）
❯ 读取 plane-game.html 并在第 100 行后添加碰撞检测代码
```

**关键**: 把"读取 + 修改"放在一个请求里说

---

#### 方案 B: 明确只需要一次读取 ⭐⭐⭐⭐

```bash
❯ 我需要修改 plane-game.html，请先读取一次文件内容，然后在 gameLoop 函数前添加代码

注意：只需要读取一次，不要重复读取
```

**效果**: Agent 会明白只需要一次 file_read

---

#### 方案 C: 临时禁用重复检测 ⭐⭐

修改 `.env` 文件：
```bash
# 添加这行（仅开发调试用）
DISABLE_REPEAT_CHECK=1
```

或者在代码中调整阈值：
```typescript
// src/core/QueryEngine.ts
private readonly MAX_RECENT_CALLS = 20; // 从 10 改成 20
```

**注意**: 这会降低保护，慎用！

---

#### 方案 D: 手动读取 + Agent 修改 ⭐⭐⭐⭐

```bash
# 步骤 1: 自己读取
cat plane-game.html | head -50

# 步骤 2: 告诉 Agent 精确位置
❯ 我看了文件，在第 159 行有 gameLoop 函数，在那里添加...
```

**优点**:
- ✅ 完全控制
- ✅ 不会触发检测
- ✅ 最高效

---

#### 方案 E: 使用不同的工具 ⭐⭐⭐

```bash
# 不用 file_read，用 bash
❯ 用 bash 执行 "cat plane-game.html | head -50"

这样不会触发 file_read 的重复检测
```

---

## 挑战 3: 复杂逻辑可能超时

### ❌ 问题场景

```
❯ 开发一个完整的飞机大战游戏，包含玩家、敌机、子弹、碰撞检测、音效、动画...

[Agent 思考中...]
[10 秒过去了...]
[30 秒过去了...]
⏱️ 超时！
```

### ✅ 解决方案

#### 方案 A: 分解任务（最重要！）⭐⭐⭐⭐⭐

```bash
# ❌ 错误方式（太复杂）
❯ 开发完整飞机游戏

# ✅ 正确方式（分解为小步骤）
❯ 第一步：创建 HTML 文件，包含 canvas 和基本结构
❯ 第二步：添加玩家飞机，三角形，键盘控制
❯ 第三步：添加敌机系统，红色方块，每 2 秒生成
❯ 第四步：添加子弹系统，空格键发射
❯ 第五步：添加碰撞检测和分数系统
❯ 第六步：添加音效和游戏结束逻辑
```

**原则**:
- 每个步骤能在 10-20 秒内完成
- 每个步骤只做一件事
- 上一步完成后，再进行下一步

---

#### 方案 B: 提供代码模板 ⭐⭐⭐⭐

```bash
❯ 添加敌机系统，参考这个模板：

const enemies = [];
function spawnEnemy() {
    const enemy = { x: ..., y: ..., speed: 2 };
    enemies.push(enemy);
}
setInterval(spawnEnemy, 2000);

请根据这个模板完善敌机系统
```

**优点**:
- ✅ Agent 不需要从零思考
- ✅ 减少计算量
- ✅ 更快完成

---

#### 方案 C: 设置合理的超时时间 ⭐⭐

如果是长时间任务，提前说明：

```bash
❯ 我要添加一个复杂的碰撞检测系统，可能需要一些时间思考，请慢慢来，不用着急

这样即使超过 30 秒也不会被误判为卡住
```

---

#### 方案 D: 混合编程（Agent + 人工）⭐⭐⭐⭐⭐

```bash
# 步骤 1: Agent 创建框架
❯ 创建游戏基础结构

# 步骤 2: 人工补充复杂逻辑
vi plane-game.html
# 手动添加碰撞检测等复杂代码

# 步骤 3: Agent 继续简单部分
❯ 现在添加分数显示 UI
```

**优点**:
- ✅ 发挥各自优势
- ✅ Agent 做重复工作
- ✅ 人类处理复杂逻辑
- ✅ 效率最高

---

#### 方案 E: 使用伪代码引导 ⭐⭐⭐

```bash
❯ 实现碰撞检测，逻辑如下：

1. 遍历所有子弹和敌机
2. 计算距离：dx = bullet.x - enemy.x, dy = ...
3. 如果距离 < 半径之和，判定为击中
4. 移除子弹和敌机，+10 分
5. 如果敌机撞到玩家，游戏结束

请按这个逻辑实现代码
```

**效果**: Agent 只需要翻译伪代码，不需要思考算法

---

## 🎯 综合最佳实践

### 推荐的完整工作流

```bash
# 1. 备份文件
cp file.html file.html.bak

# 2. 查看结构，找到目标位置
grep -n "function XXX" file.html

# 3. 用自然语言描述需求（包含行号）
❯ 在第 159 行的 gameLoop 函数前面添加碰撞检测函数，
   需要检测子弹击中敌机和敌机撞到玩家两种情况

# 4. 如果 Agent 卡住，提供伪代码
❯ 按照这个逻辑实现：
   for each bullet:
     for each enemy:
       if distance < threshold: hit!

# 5. 如果还是不行，用 bash 辅助
head -n 159 file.html > part1.txt
cat collision.txt >> part1.txt
tail -n +160 file.html >> part1.txt
mv part1.txt file.html

# 6. 验证结果
grep -A5 "checkCollision" file.html
```

---

## 📊 方案对比表

| 方案 | 难度 | 可靠性 | 推荐度 | 适用场景 |
|------|------|--------|--------|----------|
| **指定行号** | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 精确编辑 |
| **锚点定位** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 自然语言 |
| **分块编辑** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | 超大文件 |
| **Bash 辅助** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 复杂编辑 |
| **任务分解** | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 复杂逻辑 |
| **代码模板** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 减少思考 |
| **伪代码引导** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 算法实现 |
| **混合编程** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 高难度任务 |

---

## 💡 速查清单

### 编辑大文件时
- [ ] 先用 `grep -n` 找行号
- [ ] 明确说明"在第 X 行..."
- [ ] 或者说"在 XXX 函数后面..."
- [ ] 必要时用 bash 辅助

### 避免重复检测
- [ ] 把"读取 + 修改"放在一个请求里
- [ ] 明确说"只需要读取一次"
- [ ] 或者自己先读取，再让 Agent 修改
- [ ] 用 bash 读取代替 file_read

### 防止超时
- [ ] 分解为小步骤（每步<20 秒）
- [ ] 提供代码模板或伪代码
- [ ] 复杂逻辑人工处理
- [ ] 提前说明"这个比较复杂"

---

## 🎓 总结

**核心原则**:

1. **精确优于模糊** - 行号 > 函数名 > 大概位置
2. **分解优于整体** - 小步骤 > 大任务
3. **引导优于等待** - 提供模板/伪代码 > 让 AI 从零思考
4. **混合优于单一** - Agent+ 人工 > 纯 Agent

**记住这句话**:

> **"好的提示词 = 精确的位置 + 清晰的需求 + 适当的引导"**

---

_最后更新：2026-04-06 19:14_  
_实战检验：飞机大战游戏开发过程_
