#!/usr/bin/env python3
"""
🤖 机器人战斗游戏 🤖
一个回合制策略战斗游戏
"""

import random
import time
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class AttackType(Enum):
    """攻击类型"""
    NORMAL = "普通攻击"
    SPECIAL = "特殊攻击"
    DEFEND = "防御"
    HEAL = "治疗"


@dataclass
class Robot:
    """机器人类"""
    name: str
    hp: int
    max_hp: int
    attack: int
    defense: int
    energy: int
    max_energy: int
    special_name: str
    
    def is_alive(self) -> bool:
        return self.hp > 0
    
    def take_damage(self, damage: int) -> int:
        """受到伤害，返回实际伤害值"""
        actual_damage = max(1, damage - self.defense // 2)
        self.hp = max(0, self.hp - actual_damage)
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """治疗，返回实际治疗量"""
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old_hp
    
    def gain_energy(self, amount: int):
        """获得能量"""
        self.energy = min(self.max_energy, self.energy + amount)
    
    def use_energy(self, amount: int) -> bool:
        """消耗能量，成功返回 True"""
        if self.energy >= amount:
            self.energy -= amount
            return True
        return False
    
    def get_status_bar(self, length: int = 20) -> str:
        """获取状态条"""
        hp_ratio = self.hp / self.max_hp
        energy_ratio = self.energy / self.max_energy
        
        hp_bars = int(hp_ratio * length)
        energy_bars = int(energy_ratio * length)
        
        hp_bar = "█" * hp_bars + "░" * (length - hp_bars)
        energy_bar = "█" * energy_bars + "░" * (length - energy_bars)
        
        return f"HP: [{hp_bar}] {self.hp}/{self.max_hp}  能量: [{energy_bar}] {self.energy}/{self.max_energy}"


class BattleGame:
    """战斗游戏类"""
    
    def __init__(self):
        self.player: Optional[Robot] = None
        self.enemy: Optional[Robot] = None
        self.round_num = 0
        self.game_log: List[str] = []
    
    def log(self, message: str):
        """记录日志"""
        self.game_log.append(message)
        print(message)
    
    def create_player_robot(self):
        """创建玩家机器人"""
        print("\n" + "="*50)
        print("🤖 创建你的机器人 🤖")
        print("="*50)
        
        name = input("请输入机器人名字: ").strip() or "勇者机器人"
        
        print("\n选择机器人类型:")
        print("1. ⚔️ 战士型 - 高攻击，中等防御")
        print("2. 🛡️ 坦克型 - 高防御，中等攻击")
        print("3. ⚡ 刺客型 - 超高攻击，低防御")
        print("4. 💚 医疗型 - 可治疗，均衡属性")
        
        while True:
            choice = input("\n请选择 (1-4): ").strip()
            if choice in ["1", "2", "3", "4"]:
                break
            print("无效选择，请重新输入")
        
        if choice == "1":  # 战士
            robot = Robot(
                name=name,
                hp=120, max_hp=120,
                attack=25, defense=15,
                energy=50, max_energy=100,
                special_name="致命一击"
            )
        elif choice == "2":  # 坦克
            robot = Robot(
                name=name,
                hp=150, max_hp=150,
                attack=18, defense=25,
                energy=50, max_energy=100,
                special_name="反击风暴"
            )
        elif choice == "3":  # 刺客
            robot = Robot(
                name=name,
                hp=90, max_hp=90,
                attack=35, defense=8,
                energy=50, max_energy=100,
                special_name="影袭"
            )
        else:  # 医疗
            robot = Robot(
                name=name,
                hp=110, max_hp=110,
                attack=20, defense=15,
                energy=50, max_energy=100,
                special_name="能量灌注"
            )
        
        self.player = robot
        self.log(f"\n✨ {name} 创建成功!")
        return robot
    
    def create_enemy_robot(self):
        """创建敌人机器人"""
        enemy_names = ["黑暗机甲", "毁灭者", "钢铁巨兽", "暗影刺客", "雷霆战士"]
        enemy_types = [
            ("黑暗机甲", 130, 22, 18, "黑暗冲击"),
            ("毁灭者", 160, 20, 22, "毁灭炮击"),
            ("钢铁巨兽", 180, 18, 28, "碾压"),
            ("暗影刺客", 100, 32, 10, "致命暗杀"),
            ("雷霆战士", 125, 26, 15, "雷霆一击"),
        ]
        
        enemy = random.choice(enemy_types)
        self.enemy = Robot(
            name=enemy[0],
            hp=enemy[1], max_hp=enemy[1],
            attack=enemy[2], defense=enemy[3],
            energy=50, max_energy=100,
            special_name=enemy[4]
        )
        
        self.log(f"\n⚠️  遭遇敌人：{self.enemy.name}!")
        return self.enemy
    
    def show_battle_status(self):
        """显示战斗状态"""
        print("\n" + "="*50)
        print(f"⚔️  第 {self.round_num} 回合 ⚔️")
        print("="*50)
        print(f"\n👤 {self.player.name}")
        print(self.player.get_status_bar())
        print(f"攻击：{self.player.attack}  防御：{self.player.defense}")
        
        print(f"\n👾 {self.enemy.name}")
        print(self.enemy.get_status_bar())
        print(f"攻击：{self.enemy.attack}  防御：{self.enemy.defense}")
        print("="*50)
    
    def player_turn(self):
        """玩家回合"""
        print(f"\n🎮 {self.player.name} 的回合")
        print("\n选择行动:")
        print("1. ⚔️ 普通攻击 (恢复 15 能量)")
        print(f"2. 💥 特殊攻击 - {self.player.special_name} (消耗 30 能量)")
        print("3. 🛡️ 防御 (恢复 20 能量，本回合防御加倍)")
        print("4. 💚 治疗 (消耗 25 能量，恢复 30 HP)")
        
        while True:
            choice = input("\n请选择 (1-4): ").strip()
            if choice in ["1", "2", "3", "4"]:
                break
            print("无效选择")
        
        defended = False
        
        if choice == "1":  # 普通攻击
            damage = self.player.attack + random.randint(-3, 5)
            actual_damage = self.enemy.take_damage(damage)
            self.player.gain_energy(15)
            self.log(f"⚔️ {self.player.name} 发动普通攻击，造成 {actual_damage} 点伤害!")
        
        elif choice == "2":  # 特殊攻击
            if self.player.use_energy(30):
                damage = int(self.player.attack * 1.8) + random.randint(5, 10)
                actual_damage = self.enemy.take_damage(damage)
                self.log(f"💥 {self.player.name} 发动 [{self.player.special_name}]! 造成 {actual_damage} 点伤害!")
            else:
                self.log(f"❌ 能量不足! {self.player.name} 行动失败!")
                return False
        
        elif choice == "3":  # 防御
            self.player.gain_energy(20)
            defended = True
            self.log(f"🛡️ {self.player.name} 进入防御姿态!")
        
        elif choice == "4":  # 治疗
            if self.player.use_energy(25):
                heal_amount = 30 + random.randint(-5, 5)
                actual_heal = self.player.heal(heal_amount)
                self.log(f"💚 {self.player.name} 进行治疗，恢复 {actual_heal} 点 HP!")
            else:
                self.log(f"❌ 能量不足! {self.player.name} 行动失败!")
                return False
        
        return defended
    
    def enemy_turn(self, player_defended: bool):
        """敌人回合"""
        print(f"\n👾 {self.enemy.name} 的回合")
        time.sleep(1)
        
        # 简单的 AI 逻辑
        action_choice = random.random()
        
        if self.enemy.energy >= 30 and action_choice > 0.6:  # 30% 概率使用特殊攻击
            if self.enemy.use_energy(30):
                damage = int(self.enemy.attack * 1.8) + random.randint(3, 8)
                if player_defended:
                    damage = damage // 2
                actual_damage = self.player.take_damage(damage)
                self.log(f"💥 {self.enemy.name} 发动 [{self.enemy.special_name}]! 造成 {actual_damage} 点伤害!")
            else:
                self.enemy_attack(player_defended)
        elif self.enemy.hp < self.enemy.max_hp * 0.3 and action_choice > 0.4:  # 低血量时可能治疗
            heal_amount = 25 + random.randint(-3, 5)
            actual_heal = self.enemy.heal(heal_amount)
            self.enemy.gain_energy(10)
            self.log(f"💚 {self.enemy.name} 进行治疗，恢复 {actual_heal} 点 HP!")
        else:
            self.enemy_attack(player_defended)
    
    def enemy_attack(self, player_defended: bool):
        """敌人普通攻击"""
        damage = self.enemy.attack + random.randint(-2, 4)
        if player_defended:
            damage = damage // 2
        actual_damage = self.player.take_damage(damage)
        self.enemy.gain_energy(15)
        self.log(f"⚔️ {self.enemy.name} 发动攻击，造成 {actual_damage} 点伤害!")
    
    def check_winner(self) -> Optional[str]:
        """检查是否有胜利者"""
        if not self.player.is_alive():
            return "enemy"
        if not self.enemy.is_alive():
            return "player"
        return None
    
    def battle_loop(self):
        """战斗主循环"""
        self.round_num = 0
        
        while True:
            self.round_num += 1
            self.show_battle_status()
            
            # 玩家回合
            player_defended = self.player_turn()
            
            # 检查胜利
            winner = self.check_winner()
            if winner:
                break
            
            # 敌人回合
            self.enemy_turn(player_defended)
            
            # 检查胜利
            winner = self.check_winner()
            if winner:
                break
            
            input("\n按回车键继续下一回合...")
        
        self.show_result(winner)
    
    def show_result(self, winner: str):
        """显示战斗结果"""
        print("\n" + "="*50)
        if winner == "player":
            print("🎉🎉🎉 胜利! 🎉🎉🎉")
            print(f"✨ {self.player.name} 击败了 {self.enemy.name}!")
        else:
            print("💀💀💀 失败! 💀💀💀")
            print(f"😢 {self.player.name} 被 {self.enemy.name} 击败了...")
        print("="*50)
        
        print("\n📊 战斗统计:")
        print(f"总回合数：{self.round_num}")
        print(f"玩家剩余 HP: {self.player.hp}/{self.player.max_hp}")
        print(f"敌人剩余 HP: {self.enemy.hp}/{self.enemy.max_hp}")
    
    def play_again(self) -> bool:
        """询问是否再玩一次"""
        choice = input("\n是否再玩一次？(y/n): ").strip().lower()
        return choice == 'y'
    
    def run(self):
        """运行游戏"""
        print("\n" + "="*50)
        print("🤖 欢迎来到机器人战斗游戏! 🤖")
        print("="*50)
        
        while True:
            self.game_log = []
            self.create_player_robot()
            self.create_enemy_robot()
            
            input("\n按回车键开始战斗...")
            self.battle_loop()
            
            if not self.play_again():
                print("\n感谢游玩! 再见! 👋")
                break
            
            print("\n" + "="*50)
            print("新的战斗即将开始!")
            print("="*50)


if __name__ == "__main__":
    game = BattleGame()
    game.run()
