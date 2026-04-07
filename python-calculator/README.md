# Python Calculator

一个简单的命令行计算器，支持基本算术运算。

## 功能特性

- ✅ 加法运算
- ✅ 减法运算
- ✅ 乘法运算
- ✅ 除法运算（包含除零错误处理）
- ✅ 交互式命令行界面
- ✅ 完整的单元测试

## 项目结构

```
python-calculator/
├── calculator.py      # 主程序文件
├── test_calculator.py # 单元测试文件
└── README.md          # 项目说明文档
```

## 安装要求

- Python 3.6+
- 无需额外依赖（使用标准库）

## 使用方法

### 1. 运行计算器

```bash
python calculator.py
```

### 2. 交互模式

启动后，您可以输入表达式进行计算：

```
>>> 10 + 5
15.0
>>> 20 - 8
12.0
>>> 6 * 7
42.0
>>> 100 / 4
25.0
>>> quit
感谢使用！再见！
```

### 3. 支持的运算符

| 运算符 | 功能 | 示例 |
|--------|------|------|
| `+` | 加法 | `5 + 3` |
| `-` | 减法 | `10 - 4` |
| `*` | 乘法 | `6 * 7` |
| `/` | 除法 | `20 / 5` |

### 4. 退出命令

输入以下任一命令退出程序：
- `quit`
- `exit`
- `q`

## 运行测试

```bash
python test_calculator.py
```

或者使用 unittest 模块：

```bash
python -m unittest test_calculator.py
```

## 代码示例

### 作为模块导入使用

```python
from calculator import Calculator

calc = Calculator()

# 执行各种运算
result = calc.add(10, 5)      # 15.0
result = calc.subtract(10, 5) # 5.0
result = calc.multiply(10, 5) # 50.0
result = calc.divide(10, 5)   # 2.0
```

### 错误处理

```python
from calculator import Calculator

calc = Calculator()

# 除零错误
try:
    result = calc.divide(10, 0)
except ValueError as e:
    print(f"错误：{e}")  # 输出：错误：除数不能为零
```

## 许可证

本项目采用 MIT 许可证。

## 贡献

欢迎提交 Issue 和 Pull Request！
