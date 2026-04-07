#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机器人格斗游戏测试脚本（自动模式）
"""

import random
import time
from robot import Robot

class RobotFightingTest:
    """机器人格斗测试类"""
    
    def __init__(self):
        self.robot1 = None
        self.robot2 = None
        self.round = 1
        self.max_rounds = 10
        
    def create_robots(self):
        """创建两个对战机器人"""
        print("\n🤖 创建对战机器人...")
        
        # 机器人 1 - 雷霆
        self.robot1 = Robot("雷霆")
        self.robot1.attack = 25
        self.robot1.defense = 15
        self.robot1.speed = 20
        self.robot1.max_health = 120
        self.robot1.health = 120
        
        # 机器人 2 - 铁壁
        self.robot2 = Robot("铁壁")
        self.robot2.attack = 18
        self.robot2.defense = 25
        self.robot2.speed = 12
        self.robot2.max_health = 150
        self.robot2.health = 150
        
        print(f"\n✅ {self.robot1.name} 已就绪!")
        self.robot1.show_status()
        
        print(f"\n✅ {self.robot2.name} 已就绪!")
        self.robot2.show_status()
        
        input("\n按回车键开始战斗...")
        
    def get_action(self, robot):
        """获取机器人行动"""
        actions = ["attack", "heavy_attack", "defend", "heal"]
        return random.choice(actions)
    
    def execute_action(self, attacker, defender, action):
        """执行行动"""
        if action == "attack":
            damage = attacker.attack_power()
            defender.take_damage(damage)
            print(f"⚔️  {attacker.name} 发动普通攻击，造成 {damage} 点伤害!")
            
        elif action == "heavy_attack":
            if random.random() < 0.7:  # 70% 命中率
                damage = int(attacker.attack_power() * 1.5)
                defender.take_damage(damage)
                print(f"💥 {attacker.name} 发动重击，造成 {damage} 点伤害!")
            else:
                print(f"💨 {attacker.name} 的重击被闪避了!")
                
        elif action == "defend":
            attacker.defending = True
            print(f"🛡️  {attacker.name} 进入防御状态!")
            
        elif action == "heal":
            heal_amount = random.randint(10, 20)
            attacker.health = min(attacker.max_health, attacker.health + heal_amount)
            print(f"💖 {attacker.name} 修复了 {heal_amount} 点生命值!")
    
    def fight_round(self):
        """进行一个回合"""
        print(f"\n{'='*50}")
        print(f"⚡ 第 {self.round} 回合")
        print(f"{'='*50}")
        
        # 根据速度决定行动顺序
        if self.robot1.speed >= self.robot2.speed:
            first, second = self.robot1, self.robot2
        else:
            first, second = self.robot2, self.robot1
        
        # 第一个机器人行动
        action1 = self.get_action(first)
        first.defending = False
        self.execute_action(first, second, action1)
        
        if second.health <= 0:
            return first
        
        time.sleep(1)
        
        # 第二个机器人行动
        action2 = self.get_action(second)
        second.defending = False
        self.execute_action(second, first, action2)
        
        if first.health <= 0:
            return second
            
        time.sleep(1)
        
        # 显示状态
        print(f"\n📊 当前状态:")
        print(f"  {self.robot1.name}: ❤️  {self.robot1.health}/{self.robot1.max_health}")
        print(f"  {self.robot2.name}: ❤️  {self.robot2.health}/{self.robot2.max_health}")
        
        return None
    
    def start_game(self):
        """开始游戏"""
        print("\n" + "="*50)
        print("🤖 机器人格斗游戏 🤖")
        print("="*50)
        
        self.create_robots()
        
        winner = None
        
        while self.round <= self.max_rounds:
            winner = self.fight_round()
            
            if winner:
                break
                
            self.round += 1
            time.sleep(1)
        
        # 游戏结束
        print("\n" + "="*50)
        if winner:
            print(f"🏆 恭喜 {winner.name} 获胜!")
        else:
            print("🤝 战斗结束，平局!")
        print("="*50)
        
        # 最终状态
        print("\n📊 最终状态:")
        self.robot1.get_status()
        self.robot2.get_status()

if __name__ == "__main__":
    game = RobotFightingTest()
    game.start_game()
