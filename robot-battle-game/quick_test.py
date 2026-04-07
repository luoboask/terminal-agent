#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试机器人战斗
"""

from robot import create_robot
from main import Battle

print("🤖 机器人大战 - 快速测试")
print("=" * 50)

# 创建两个机器人
robot1 = create_robot("雷霆 -001", "狙击型", 1)
robot2 = create_robot("风暴 -002", "平衡型", 2)

print(f"\n🔵 {robot1.name} [{robot1.robot_type}]")
print(f"🔴 {robot2.name} [{robot2.robot_type}]")

# 创建战斗
battle = Battle([robot1, robot2], "ai_vs_ai")

# 运行自动战斗（快速模式）
print("\n⚔️  战斗开始！\n")
battle.run(auto_play=True)

print("\n✅ 测试完成！")
