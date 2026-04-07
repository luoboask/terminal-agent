#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 机器人大战 - Robot Battle Game (演示版)
一个回合制机器人对战游戏 - 自动演示模式
"""

import random
import time
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class SkillType(Enum):
    """技能类型"""
    ATTACK = "攻击"
    DEFENSE = "防御"
    SPECIAL = "必杀"
    HEAL = "治疗"


@dataclass
class Skill:
    """技能类"""
    name: str
    skill_type: SkillType
    power: int
    accuracy: float
    cooldown: int = 0
    description: str = ""
    current_cooldown: int = 0

    def is_ready(self) -> bool:
        return self.current_cooldown <= 0

    def use(self):
        self.current_cooldown = self.cooldown

    def reduce_cooldown(self):
        if self.current_cooldown > 0:
            self.current_cooldown -= 1


@dataclass
class Robot:
    """机器人类"""
    name: str
    hp: int
    max_hp: int
    attack: int
    defense: int
    speed: int
    skills: List[Skill] = field(default_factory=list)
    energy: int = 100
    max_energy: int = 100
    
    def is_alive(self) -> bool:
        return self.hp > 0
    
    def take_damage(self, damage: int) -> int:
        actual_damage = max(1, damage - self.defense // 2)
        actual_damage = random.randint(int(actual_damage * 0.8), int(actual_damage * 1.2))
        self.hp = max(0, self.hp - actual_damage)
        return actual_damage
    
    def heal(self, amount: int) -> int:
        actual_heal = min(amount, self.max_hp - self.hp)
        self.hp += actual_heal
        return actual_heal
    
    def gain_energy(self, amount: int):
        self.energy = min(self.max_energy, self.energy + amount)
    
    def reset_cooldowns(self):
        for skill in self.skills:
            skill.reduce_cooldown()
    
    def get_available_skills(self) -> List[Skill]:
        return [s for s in self.skills if s.is_ready()]
    
    def get_hp_bar(self, length=20) -> str:
        filled = int(length * self.hp / self.max_hp) if self.max_hp > 0 else 0
        return '█' * filled + '░' * (length - filled)


class RobotBattle:
    """机器人大战游戏主类"""
    
    def __init__(self, auto_play=False):
        self.player: Optional[Robot] = None
        self.enemy: Optional[Robot] = None
        self.round_num = 0
        self.auto_play = auto_play
    
    def create_robots(self):
        """创建机器人"""
        # 玩家机器人 - 烈焰战神
        fire_skills = [
            Skill("火焰拳", SkillType.ATTACK, 25, 0.95, 0, "用燃烧的拳头攻击敌人"),
            Skill("烈焰风暴", SkillType.SPECIAL, 45, 0.80, 2, "释放强大的火焰风暴"),
            Skill("火焰护盾", SkillType.DEFENSE, 15, 1.0, 1, "生成火焰护盾提升防御"),
            Skill("能量修复", SkillType.HEAL, 30, 1.0, 2, "修复受损部件"),
        ]
        self.player = Robot(
            name="🔥 烈焰战神",
            hp=150, max_hp=150,
            attack=35, defense=20, speed=25,
            skills=fire_skills
        )
        
        # 敌方机器人 - 寒冰卫士
        ice_skills = [
            Skill("冰锥射击", SkillType.ATTACK, 28, 0.90, 0, "发射尖锐的冰锥"),
            Skill("绝对零度", SkillType.SPECIAL, 50, 0.75, 3, "释放极寒能量冻结敌人"),
            Skill("冰霜护甲", SkillType.DEFENSE, 20, 1.0, 1, "凝结冰霜提升防御"),
            Skill("冷却系统", SkillType.HEAL, 25, 1.0, 2, "启动冷却系统修复损伤"),
        ]
        self.enemy = Robot(
            name="❄️ 寒冰卫士",
            hp=140, max_hp=140,
            attack=38, defense=18, speed=22,
            skills=ice_skills
        )
    
    def display_status(self):
        """显示战斗状态"""
        print("\n" + "=" * 60)
        print(f"⚔️  第 {self.round_num} 回合  ⚔️".center(60))
        print("=" * 60)
        
        print(f"\n🤖 {self.player.name}")
        print(f"   HP: [{self.player.get_hp_bar()}] {self.player.hp}/{self.player.max_hp}")
        print(f"   ⚔️ 攻:{self.player.attack} 🛡️ 防:{self.player.defense} 💨 速:{self.player.speed}")
        
        print(f"\n   VS\n")
        
        print(f"🤖 {self.enemy.name}")
        print(f"   HP: [{self.enemy.get_hp_bar()}] {self.enemy.hp}/{self.enemy.max_hp}")
        print(f"   ⚔️ 攻:{self.enemy.attack} 🛡️ 防:{self.enemy.defense} 💨 速:{self.enemy.speed}")
        print()
    
    def choose_skill(self, robot: Robot, is_player: bool) -> Optional[Skill]:
        """选择技能"""
        available = robot.get_available_skills()
        
        if not available:
            return None
        
        if is_player and not self.auto_play:
            # 手动选择
            print(f"\n📋 {robot.name} 的可用技能:")
            for i, skill in enumerate(available, 1):
                cd = f" (CD:{skill.current_cooldown})" if skill.current_cooldown > 0 else ""
                print(f"  {i}. {skill.name} [{skill.skill_type.value}] 威力:{skill.power} 命中:{skill.accuracy*100:.0f}%{cd}")
            
            while True:
                try:
                    choice = input(f"\n请选择 (1-{len(available)}): ")
                    idx = int(choice) - 1
                    if 0 <= idx < len(available):
                        return available[idx]
                except:
                    pass
                print("❌ 无效输入")
        else:
            # AI 或自动模式
            if robot.hp < robot.max_hp * 0.3:
                heals = [s for s in available if s.skill_type == SkillType.HEAL]
                if heals:
                    return random.choice(heals)
            
            specials = [s for s in available if s.skill_type == SkillType.SPECIAL]
            if specials and random.random() < 0.5:
                return random.choice(specials)
            
            attacks = [s for s in available if s.skill_type == SkillType.ATTACK]
            if attacks:
                return random.choice(attacks)
            
            return random.choice(available)
    
    def execute_skill(self, attacker: Robot, defender: Robot, skill: Optional[Skill]):
        """执行技能"""
        if skill is None:
            dmg = defender.take_damage(attacker.attack // 2)
            print(f"⚔️ {attacker.name} 普通攻击！造成 {dmg} 点伤害")
            attacker.gain_energy(10)
            return
        
        if random.random() > skill.accuracy:
            print(f"💨 {attacker.name} 使用 {skill.name}，但是被躲开了！")
            skill.use()
            return
        
        skill.use()
        
        if skill.skill_type == SkillType.ATTACK:
            dmg = defender.take_damage(skill.power + attacker.attack // 3)
            print(f"🔥 {attacker.name} 使用 {skill.name}！造成 {dmg} 点伤害")
            attacker.gain_energy(15)
        
        elif skill.skill_type == SkillType.SPECIAL:
            dmg = defender.take_damage(skill.power + attacker.attack // 2)
            print(f"💥 {attacker.name} 释放必杀技 {skill.name}！！！造成 {dmg} 点巨额伤害")
            attacker.gain_energy(20)
        
        elif skill.skill_type == SkillType.DEFENSE:
            heal = attacker.heal(skill.power // 2)
            print(f"🛡️ {attacker.name} 使用 {skill.name}！恢复 {heal} 点生命")
            attacker.gain_energy(25)
        
        elif skill.skill_type == SkillType.HEAL:
            heal = attacker.heal(skill.power)
            print(f"💚 {attacker.name} 使用 {skill.name}！恢复 {heal} 点生命")
    
    def battle_round(self):
        """执行回合"""
        self.round_num += 1
        
        first, second = (self.player, self.enemy) if self.player.speed >= self.enemy.speed else (self.enemy, self.player)
        
        self.display_status()
        
        if first.is_alive():
            skill = self.choose_skill(first, first == self.player)
            if first.is_alive() and second.is_alive():
                self.execute_skill(first, second, skill)
        
        if second.is_alive() and first.is_alive():
            skill = self.choose_skill(second, second == self.player)
            if second.is_alive() and first.is_alive():
                self.execute_skill(second, first, skill)
        
        self.player.reset_cooldowns()
        self.enemy.reset_cooldowns()
        
        return self.player.is_alive() and self.enemy.is_alive()
    
    def start(self):
        """开始游戏"""
        print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║           🤖 欢迎来到 机器人大战 🤖                        ║
║              Robot Battle Arena                           ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
        """)
        
        self.create_robots()
        
        print(f"🎮 玩家：{self.player.name}")
        print(f"👾 敌人：{self.enemy.name}")
        
        if self.auto_play:
            print("\n🎬 自动演示模式开始...\n")
            time.sleep(1)
        
        while True:
            continuing = self.battle_round()
            
            if not continuing:
                break
            
            if self.auto_play:
                time.sleep(1.5)
            else:
                input("\n按回车继续...")
        
        # 显示结果
        self.display_status()
        
        if not self.player.is_alive():
            print("\n" + "💀" * 25)
            print("  你被打败了！游戏结束！".center(50))
            print("💀" * 25)
        else:
            print("\n" + "🏆" * 25)
            print(f"  恭喜！{self.player.name} 获胜！".center(50))
            print(f"  共进行了 {self.round_num} 回合".center(50))
            print("🏆" * 25)


def main():
    print("🎮 机器人大战 🎮")
    print("1. 手动模式")
    print("2. 自动演示")
    
    choice = input("\n请选择模式 (1/2): ").strip()
    auto = choice == "2"
    
    game = RobotBattle(auto_play=auto)
    game.start()
    
    if input("\n再来一局？(y/n): ").lower() == 'y':
        main()


if __name__ == "__main__":
    main()
