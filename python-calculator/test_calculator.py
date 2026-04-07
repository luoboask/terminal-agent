#!/usr/bin/env python3
"""
Python Calculator 测试文件
包含单元测试来验证计算器功能
"""

import unittest
from calculator import Calculator


class TestCalculator(unittest.TestCase):
    """计算器测试类"""

    def setUp(self):
        """每个测试前运行"""
        self.calc = Calculator()

    def test_add(self):
        """测试加法"""
        self.assertEqual(self.calc.add(2, 3), 5)
        self.assertEqual(self.calc.add(-1, 1), 0)
        self.assertEqual(self.calc.add(0, 0), 0)
        self.assertEqual(self.calc.add(100, 200), 300)

    def test_subtract(self):
        """测试减法"""
        self.assertEqual(self.calc.subtract(5, 3), 2)
        self.assertEqual(self.calc.subtract(1, 1), 0)
        self.assertEqual(self.calc.subtract(0, 5), -5)
        self.assertEqual(self.calc.subtract(100, 50), 50)

    def test_multiply(self):
        """测试乘法"""
        self.assertEqual(self.calc.multiply(3, 4), 12)
        self.assertEqual(self.calc.multiply(0, 100), 0)
        self.assertEqual(self.calc.multiply(-2, 3), -6)
        self.assertEqual(self.calc.multiply(10, 10), 100)

    def test_divide(self):
        """测试除法"""
        self.assertEqual(self.calc.divide(10, 2), 5)
        self.assertEqual(self.calc.divide(7, 2), 3.5)
        self.assertEqual(self.calc.divide(0, 5), 0)
        self.assertEqual(self.calc.divide(100, 10), 10)

    def test_divide_by_zero(self):
        """测试除以零"""
        with self.assertRaises(ValueError):
            self.calc.divide(10, 0)

    def test_invalid_operation(self):
        """测试无效操作"""
        with self.assertRaises(ValueError):
            self.calc.calculate(5, 5, '%')


class TestCalculatorRun(unittest.TestCase):
    """测试运行器功能"""

    def test_calculate_method(self):
        """测试 calculate 方法"""
        calc = Calculator()
        self.assertEqual(calc.calculate(5, 3, '+'), 8)
        self.assertEqual(calc.calculate(5, 3, '-'), 2)
        self.assertEqual(calc.calculate(5, 3, '*'), 15)
        self.assertEqual(calc.calculate(6, 3, '/'), 2)


if __name__ == '__main__':
    unittest.main()
