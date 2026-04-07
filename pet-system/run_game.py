#!/usr/bin/env python3
"""
宠物系统启动脚本
"""
import sys
import os

# 确保在正确的目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=" * 50)
print("🐾 养成式宠物系统 🐾")
print("=" * 50)
print()

# 测试导入所有模块
print("📦 加载模块...")
try:
    from pet import Pet, PetType
    print("  ✅ 宠物模块")
except Exception as e:
    print(f"  ❌ 宠物模块错误：{e}")
    sys.exit(1)

try:
    from storage import PetStorage
    print("  ✅ 存储模块")
except Exception as e:
    print(f"  ❌ 存储模块错误：{e}")
    sys.exit(1)

try:
    from ui import UI, Colors
    print("  ✅ UI 模块")
except Exception as e:
    print(f"  ❌ UI 模块错误：{e}")
    sys.exit(1)

try:
    from shop import Shop
    print("  ✅ 商店模块")
except Exception as e:
    print(f"  ❌ 商店模块错误：{e}")
    sys.exit(1)

try:
    from achievements import AchievementSystem
    print("  ✅ 成就模块")
except Exception as e:
    print(f"  ❌ 成就模块错误：{e}")
    sys.exit(1)

try:
    from events import EventSystem
    print("  ✅ 事件模块")
except Exception as e:
    print(f"  ❌ 事件模块错误：{e}")
    sys.exit(1)

try:
    from weather import WeatherSystem
    print("  ✅ 天气模块")
except Exception as e:
    print(f"  ❌ 天气模块错误：{e}")
    sys.exit(1)

try:
    from decoration import DecorationSystem
    print("  ✅ 装饰模块")
except Exception as e:
    print(f"  ❌ 装饰模块错误：{e}")
    sys.exit(1)

print()
print("✨ 所有模块加载成功！")
print()

# 运行主程序
print("🎮 启动游戏...")
print("=" * 50)
print()

import main
main.main()
