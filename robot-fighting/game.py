#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机器人格斗游戏主程序
"""

import random
import time
from robot import Robot

class RobotFightingGame:
    """机器人格斗游戏类"""
    
    def __init__(self):
        self.robot1 = None
        self.robot2 = None
        self.round = 1
        self.max_rounds = 10
        
    def create_robots(self):
        """创建两个对战机器人"""
        print("\n🤖 创建对战机器人...")
        
        # 机器人 1
        name1 = "雷霆"
        self.robot1 = Robot(name1)
        self.robot1.randomize_attributes()
        
        # 机器人 2
        name2 = "铁壁"
        self.robot2 = Robot(name2)
        self.robot2.randomize_attributes()
        
        print(f"\n✅ {self.robot1.name} vs {self.robot2.name}")
        print("-" * 50)
        self.robot1.display_status()
        print("-" * 50)
        self.robot2.display_status()
        
    def battle_round(self):
        """执行一个战斗回合"""
        print(f"\n⚔️  第 {self.round} 回合开始！")
        print("=" * 50)
        
        # 决定谁先攻击（速度高的先手）
        if self.robot1.speed >= self.robot2.speed:
            first, second = self.robot1, self.robot2
        else:
            first, second = self.robot2, self.robot1
            
        # 第一台机器人攻击
        if first.is_alive():
            damage = first.attack(second)
            print(f"💥 {first.name} 攻击 {second.name}，造成 {damage} 点伤害！")
            time.sleep(0.5)
            
        # 第二台机器人攻击
        if second.is_alive():
            damage = second.attack(first)
            print(f"💥 {second.name} 攻击 {first.name}，造成 {damage} 点伤害！")
            time.sleep(0.5)
            
        # 显示状态
        print("\n📊 当前状态:")
        print(f"  {self.robot1.name}: HP {self.robot1.current_hp}/{self.robot1.max_hp}")
        print(f"  {self.robot2.name}: HP {self.robot2.current_hp}/{self.robot2.max_hp}")
        
        self.round += 1
        
    def check_winner(self):
        """检查是否有获胜者"""
        if not self.robot1.is_alive():
            return self.robot2
        if not self.robot2.is_alive():
            return self.robot1
        return None
        
    def play(self):
        """开始游戏"""
        print("\n" + "=" * 50)
        print("🎮 欢迎进入机器人格斗竞技场！")
        print("=" * 50)
        
        self.create_robots()
        
        input("\n按 Enter 开始战斗...")
        
        while self.round <= self.max_rounds:
            self.battle_round()
            
            winner = self.check_winner()
            if winner:
                break
                
            time.sleep(1)
            
        # 游戏结束
        print("\n" + "=" * 50)
        print("🏆 游戏结束！")
        print("=" * 50)
        
        winner = self.check_winner()
        if winner:
            print(f"🎉 获胜者是：{winner.name}！")
            print(f"   剩余 HP: {winner.current_hp}/{winner.max_hp}")
        else:
            print("🤝 平局！双方都耗尽了能量。")
            
        # 最终状态
        print("\n📋 最终统计:")
        self.robot1.display_status()
        self.robot2.display_status()
        
def main():
    """主函数"""
    game = RobotFightingGame()
    game.play()
    
if __name__ == "__main__":
    main()
