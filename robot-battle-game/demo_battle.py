#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机器人大战游戏 - 自动演示模式
展示 AI 对战 AI 的自动战斗
"""

import random
import time
from robot import Robot, create_robot
from main import Battle

def demo_battle():
    """演示战斗"""
    print("\n" + "="*60)
    print("           🤖 机器人大战 - 自动演示 🤖")
    print("="*60)
    
    # 创建两个机器人
    robot_types = list(Robot.ROBOT_TYPES.keys())
    
    robot1 = create_robot("雷霆 -001", random.choice(robot_types), 1)
    robot2 = create_robot("风暴 -002", random.choice(robot_types), 2)
    
    print(f"\n🔵 蓝方：{robot1.name} [{robot1.robot_type}]")
    print(robot1.get_status())
    print()
    print(f"🔴 红方：{robot2.name} [{robot2.robot_type}]")
    print(robot2.get_status())
    
    # 支持非交互式运行（检测 EOF）
    try:
        input("\n按回车键开始战斗...")
    except EOFError:
        # 非交互式环境，自动开始
        print("\n⚡  自动开始战斗...")
        time.sleep(1)
    
    # 创建战斗
    battle = Battle([robot1, robot2], "ai_vs_ai")
    
    # 运行自动战斗
    print("\n" + "="*60)
    print("                  ⚔️  战斗开始！⚔️")
    print("="*60)
    
    battle.run(auto_play=True)
    
    print("\n感谢观看！")


if __name__ == "__main__":
    demo_battle()
