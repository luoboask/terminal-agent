#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 机器人大战 - Robot Battle Game
一个回合制机器人对战游戏
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
    power: int  # 威力/效果值
    accuracy: float  # 命中率 0-1
    cooldown: int = 0  # 冷却回合
    description: str = ""
    current_cooldown: int = 0  # 当前冷却

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
    hp: int  # 生命值
    max_hp: int
    attack: int  # 攻击力
    defense: int  # 防御力
    speed: int  # 速度（决定出手顺序）
    skills: List[Skill] = field(default_factory=list)
    energy: int = 100  # 能量值
    max_energy: int = 100
    
    def is_alive(self) -> bool:
        return self.hp > 0
    
    def take_damage(self, damage: int) -> int:
        """受到伤害，返回实际伤害值"""
        actual_damage = max(1, damage - self.defense // 2)
        actual_damage = random.randint(int(actual_damage * 0.8), int(actual_damage * 1.2))
        self.hp = max(0, self.hp - actual_damage)
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """治疗，返回实际治疗量"""
        actual_heal = min(amount, self.max_hp - self.hp)
        self.hp += actual_heal
        return actual_heal
    
    def gain_energy(self, amount: int):
        """获得能量"""
        self.energy = min(self.max_energy, self.energy + amount)
    
    def reset_cooldowns(self):
        """减少所有技能冷却"""
        for skill in self.skills:
            skill.reduce_cooldown()
    
    def get_available_skills(self) -> List[Skill]:
        """获取可用技能"""
        return [s for s in self.skills if s.is_ready()]
    
    def __str__(self) -> str:
        hp_bar = self._get_bar(self.hp, self.max_hp, 20)
        energy_bar = self._get_bar(self.energy, self.max_energy, 10)
        return f"""
╔══════════════════════════════════════╗
║  🤖 {self.name:^28} ║
╠══════════════════════════════════════╣
║  ❤️  HP: [{hp_bar}] {self.hp}/{self.max_hp}
║  ⚡  能量：[{energy_bar}] {self.energy}/{self.max_energy}
║  ⚔️  攻击：{self.attack}  🛡️  防御：{self.defense}
║  💨  速度：{self.speed}
╚══════════════════════════════════════╝
"""
    
    def _get_bar(self, current: int, maximum: int, length: int) -> str:
        filled = int(length * current / maximum) if maximum > 0 else 0
        return '█' * filled + '░' * (length - filled)


class RobotBattle:
    """机器人大战游戏主类"""
    
    def __init__(self):
        self.player: Optional[Robot] = None
        self.enemy: Optional[Robot] = None
        self.round_num = 0
        self.game_log: List[str] = []
    
    def log(self, message: str):
        """记录日志"""
        self.game_log.append(message)
        print(message)
    
    def create_default_robots(self):
        """创建默认机器人"""
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
    
    def display_battle_status(self):
        """显示战斗状态"""
        print("\n" + "=" * 60)
        print(f"⚔️  第 {self.round_num} 回合  ⚔️".center(60))
        print("=" * 60)
        print(self.player)
        print("    VS")
        print(self.enemy)
    
    def choose_skill(self, robot: Robot, is_player: bool) -> Optional[Skill]:
        """选择技能"""
        available_skills = robot.get_available_skills()
        
        if not available_skills:
            self.log(f"⚠️  {robot.name} 所有技能都在冷却中！只能普通攻击")
            return None
        
        if is_player:
            print(f"\n📋 {robot.name} 的可用技能:")
            for i, skill in enumerate(available_skills, 1):
                cd_info = f" (冷却:{skill.current_cooldown})" if skill.current_cooldown > 0 else ""
                print(f"  {i}. {skill.name} [{skill.skill_type.value}] - 威力:{skill.power} 命中:{skill.accuracy*100:.0f}%{cd_info}")
                print(f"     💬 {skill.description}")
            
            while True:
                try:
                    choice = input(f"\n请选择技能 (1-{len(available_skills)}): ")
                    idx = int(choice) - 1
                    if 0 <= idx < len(available_skills):
                        return available_skills[idx]
                    print("❌ 无效的选择，请重试")
                except ValueError:
                    print("❌ 请输入数字")
        else:
            # AI 选择技能
            # 优先使用必杀技，其次攻击，血量低时治疗
            if robot.hp < robot.max_hp * 0.3:
                heal_skills = [s for s in available_skills if s.skill_type == SkillType.HEAL]
                if heal_skills:
                    return random.choice(heal_skills)
            
            special_skills = [s for s in available_skills if s.skill_type == SkillType.SPECIAL]
            if special_skills and random.random() < 0.6:
                return random.choice(special_skills)
            
            attack_skills = [s for s in available_skills if s.skill_type == SkillType.ATTACK]
            if attack_skills:
                return random.choice(attack_skills)
            
            return random.choice(available_skills)
    
    def execute_skill(self, attacker: Robot, defender: Robot, skill: Optional[Skill]):
        """执行技能"""
        if skill is None:
            # 普通攻击
            damage = attacker.attack // 2
            actual_damage = defender.take_damage(damage)
            self.log(f"⚔️  {attacker.name} 发动普通攻击！造成 {actual_damage} 点伤害")
            attacker.gain_energy(10)
            return
        
        # 检查命中率
        if random.random() > skill.accuracy:
            self.log(f"💨 {attacker.name} 使用 {skill.name}，但是被躲开了！")
            skill.use()
            return
        
        skill.use()
        
        if skill.skill_type == SkillType.ATTACK:
            damage = skill.power + attacker.attack // 3
            actual_damage = defender.take_damage(damage)
            self.log(f"🔥 {attacker.name} 使用 {skill.name}！造成 {actual_damage} 点伤害")
            attacker.gain_energy(15)
        
        elif skill.skill_type == SkillType.SPECIAL:
            damage = skill.power + attacker.attack // 2
            actual_damage = defender.take_damage(damage)
            self.log(f"💥 {attacker.name} 释放必杀技 {skill.name}！！！造成 {actual_damage} 点巨额伤害")
            attacker.gain_energy(20)
        
        elif skill.skill_type == SkillType.DEFENSE:
            # 防御技能暂时简化为少量回血 + 能量回复
            heal_amount = skill.power // 2
            actual_heal = attacker.heal(heal_amount)
            attacker.gain_energy(25)
            self.log(f"🛡️ {attacker.name} 使用 {skill.name}！恢复了 {actual_heal} 点生命值")
        
        elif skill.skill_type == SkillType.HEAL:
            heal_amount = skill.power
            actual_heal = attacker.heal(heal_amount)
            self.log(f"💚 {attacker.name} 使用 {skill.name}！恢复了 {actual_heal} 点生命值")
    
    def battle_round(self):
        """执行一个回合"""
        self.round_num += 1
        
        # 决定出手顺序（速度高的先手）
        first, second = (self.player, self.enemy) if self.player.speed >= self.enemy.speed else (self.enemy, self.player)
        is_player_first = first == self.player
        
        self.display_battle_status()
        
        # 第一顺位行动
        if first.is_alive():
            skill = self.choose_skill(first, first == self.player)
            if first.is_alive() and second.is_alive():
                self.execute_skill(first, second, skill)
        
        # 第二顺位行动
        if second.is_alive() and first.is_alive():
            skill = self.choose_skill(second, second == self.player)
            if second.is_alive() and first.is_alive():
                self.execute_skill(second, first, skill)
        
        # 减少技能冷却
        self.player.reset_cooldowns()
        self.enemy.reset_cooldowns()
        
        # 检查战斗结束
        if not self.player.is_alive():
            return False
        if not self.enemy.is_alive():
            return True
        
        input("\n按回车键继续下一回合...")
        return True
    
    def start_game(self):
        """开始游戏"""
        print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║           🤖 欢迎来到 机器人大战 🤖                        ║
║              Robot Battle Arena                           ║
║                                                           ║
║   选择你的机器人，与敌人展开激烈对决！                     ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
        """)
        
        self.create_default_robots()
        
        self.log(f"⚡ 战斗即将开始！")
        self.log(f"🎮 玩家：{self.player.name}")
        self.log(f"👾 敌人：{self.enemy.name}")
        
        input("\n按回车键开始战斗...")
        
        # 战斗循环
        while True:
            player_wins = self.battle_round()
            
            if not self.player.is_alive():
                self.display_battle_status()
                print("\n" + "💀" * 30)
                print("  你被打败了！游戏结束！".center(60))
                print("💀" * 30)
                break
            
            if not self.enemy.is_alive():
                self.display_battle_status()
                print("\n" + "🏆" * 30)
                print(f"  恭喜！{self.player.name} 获得了胜利！".center(60))
                print(f"  共进行了 {self.round_num} 回合".center(60))
                print("🏆" * 30)
                break
        
        # 显示战斗日志摘要
        print("\n\n📜 战斗日志摘要:")
        for log in self.game_log[-10:]:
            print(f"  {log}")
        
        # 询问是否重玩
        play_again = input("\n是否再来一局？(y/n): ")
        if play_again.lower() == 'y':
            self.__init__()
            self.start_game()


def main():
    """主函数"""
    game = RobotBattle()
    game.start_game()


if __name__ == "__main__":
    main()
