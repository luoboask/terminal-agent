#!/usr/bin/env python3
"""
Python Calculator - 一个简单的命令行计算器
支持基本算术运算：加、减、乘、除
"""


class Calculator:
    """计算器类，提供基本算术运算"""
    
    def add(self, a, b):
        """加法运算"""
        return a + b
    
    def subtract(self, a, b):
        """减法运算"""
        return a - b
    
    def multiply(self, a, b):
        """乘法运算"""
        return a * b
    
    def divide(self, a, b):
        """除法运算"""
        if b == 0:
            raise ValueError("除数不能为零")
        return a / b
    
    def calculate(self, a, operator, b):
        """
        根据运算符执行计算
        
        参数:
            a: 第一个操作数
            operator: 运算符 (+, -, *, /)
            b: 第二个操作数
            
        返回:
            计算结果
        """
        if operator == '+':
            return self.add(a, b)
        elif operator == '-':
            return self.subtract(a, b)
        elif operator == '*':
            return self.multiply(a, b)
        elif operator == '/':
            return self.divide(a, b)
        else:
            raise ValueError(f"不支持的运算符：{operator}")


def main():
    """主函数 - 交互式计算器"""
    calc = Calculator()
    
    print("=" * 40)
    print("    Python 计算器")
    print("=" * 40)
    print("支持的操作：+ (加), - (减), * (乘), / (除)")
    print("输入 'q' 退出程序")
    print("=" * 40)
    
    while True:
        try:
            # 获取用户输入
            user_input = input("\n请输入表达式 (例如：3 + 4): ").strip()
            
            if user_input.lower() == 'q':
                print("感谢使用，再见！")
                break
            
            # 解析输入
            parts = user_input.split()
            if len(parts) != 3:
                print("错误：请输入格式为 '数字 运算符 数字' 的表达式")
                continue
            
            num1 = float(parts[0])
            operator = parts[1]
            num2 = float(parts[2])
            
            # 执行计算
            result = calc.calculate(num1, operator, num2)
            print(f"结果：{num1} {operator} {num2} = {result}")
            
        except ValueError as e:
            print(f"错误：{e}")
        except Exception as e:
            print(f"发生错误：{e}")


if __name__ == "__main__":
    main()
