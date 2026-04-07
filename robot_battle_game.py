#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 机器人大战游戏
一个基于 Python 的回合制机器人大战游戏！
"""

import random
from typing import List, Optional
from enum import Enum
from dataclasses import dataclass, field


class RobotType(Enum):
    """机器人类型"""
    WARRIOR = "战士"
    ASSASSIN = "刺客"
    TANK = "坦克"
    SNIPER = "狙击手"
    SUPPORT = "支援"


@dataclass
class Skill:
    """技能类"""
    name: str
    damage: int
    accuracy: float
    cooldown: int = 0
    current_cooldown: int = 0
    
    def is_ready(self) -> bool:
        return self.current_cooldown <= 0
    
    def use(self):
        self.current_cooldown = self.cooldown
    
    def cooldown_tick(self):
        if self.current_cooldown > 0:
            self.current_cooldown -= 1


@dataclass
class Robot:
    """机器人类"""
    name: str
    robot_type: RobotType
    hp: int
    max_hp: int
    attack: int
    defense: int
    speed: int
    skills: List[Skill] = field(default_factory=list)
    is_alive: bool = True
    dodge_rate: float = 0.0
    critical_rate: float = 0.1
    
    def __post_init__(self):
        if self.robot_type == RobotType.ASSASSIN:
            self.dodge_rate = 0.3
            self.critical_rate = 0.25
        elif self.robot_type == RobotType.TANK:
            self.defense += 20
            self.max_hp += 50
            self.hp += 50
        elif self.robot_type == RobotType.SNIPER:
            self.attack += 15
            self.critical_rate = 0.3
        elif self.robot_type == RobotType.SUPPORT:
            self.skills.append(Skill("修复光束", -30, 0.95, 3))
    
    def take_damage(self, damage: int) -> int:
        actual_damage = max(1, damage - self.defense // 2)
        
        if random.random() < self.dodge_rate:
            print(f"  ⚡ {self.name} 闪避了攻击!")
            return 0
        
        is_critical = random.random() < self.critical_rate
        if is_critical:
            actual_damage = int(actual_damage * 1.5)
            print(f"  💥 暴击! {actual_damage} 点伤害!")
        
        self.hp -= actual_damage
        if self.hp <= 0:
            self.hp = 0
            self.is_alive = False
        
        return actual_damage
    
    def heal(self, amount: int):
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        healed = self.hp - old_hp
        if healed > 0:
            print(f"  💚 {self.name} 恢复了 {healed} 点生命值!")
    
    def basic_attack(self, target: 'Robot') -> int:
        damage = self.attack + random.randint(-5, 10)
        return target.take_damage(damage)
    
    def use_skill(self, skill: Skill, target: 'Robot') -> bool:
        if not skill.is_ready():
            print(f"  ⏰ 技能 {skill.name} 还在冷却中!")
            return False
        
        if random.random() > skill.accuracy:
            print(f"  ❌ {self.name} 使用 {skill.name} 未命中!")
            skill.use()
            return False
        
        print(f"  ⚔️ {self.name} 使用技能：{skill.name}!")
        
        if skill.damage < 0:
            self.heal(abs(skill.damage))
        else:
            damage = skill.damage + random.randint(-3, 5)
            target.take_damage(damage)
        
        skill.use()
        return True
    
    def cooldown_tick(self):
        for skill in self.skills:
            skill.cooldown_tick()
    
    def display_status(self):
        hp_bar_len = int(self.hp * 20 / self.max_hp)
        hp_bar = "█" * hp_bar_len + "░" * (20 - hp_bar_len)
        status = "存活" if self.is_alive else "❌ 已击败"
        print(f"  [{status}] {self.name} ({self.robot_type.value})")
        print(f"  HP: [{hp_bar}] {self.hp}/{self.max_hp}")
        print(f"  攻击:{self.attack} 防御:{self.defense} 速度:{self.speed}")
        if self.skills:
            skills_str = ", ".join([f"{s.name}(CD:{s.current_cooldown})" for s in self.skills])
            print(f"  技能：{skills_str}")


class Battle:
    """战斗类"""
    
    def __init__(self, team1: List[Robot], team2: List[Robot]):
        self.team1 = team1
        self.team2 = team2
        self.turn_count = 0
    
    def get_all_alive(self) -> List[Robot]:
        return [r for r in self.team1 + self.team2 if r.is_alive]
    
    def get_team_alive(self, team_num: int) -> List[Robot]:
        team = self.team1 if team_num == 1 else self.team2
        return [r for r in team if r.is_alive]
    
    def select_target(self, attacker: Robot, enemy_team: List[Robot]) -> Optional[Robot]:
        alive_enemies = [e for e in enemy_team if e.is_alive]
        if not alive_enemies:
            return None
        return min(alive_enemies, key=lambda x: x.hp)
    
    def execute_turn(self, robot: Robot):
        if not robot.is_alive:
            return
        
        enemy_team = self.team2 if robot in self.team1 else self.team1
        
        if not self.get_team_alive(2 if robot in self.team1 else 1):
            return
        
        target = self.select_target(robot, enemy_team)
        if not target:
            return
        
        print(f"\n  → {robot.name} 的回合:")
        
        use_skill = False
        selected_skill = None
        
        for skill in robot.skills:
            if skill.is_ready():
                if skill.damage < 0 and robot.hp < robot.max_hp * 0.5:
                    use_skill = True
                    selected_skill = skill
                    break
                elif skill.damage > 0 and random.random() < 0.4:
                    use_skill = True
                    selected_skill = skill
                    break
        
        if use_skill and selected_skill:
            robot.use_skill(selected_skill, target)
        else:
            damage = robot.basic_attack(target)
            print(f"  🗡️ {robot.name} 攻击 {target.name}, 造成 {damage} 点伤害!")
        
        for r in self.get_all_alive():
            r.cooldown_tick()
    
    def check_winner(self) -> int:
        team1_alive = any(r.is_alive for r in self.team1)
        team2_alive = any(r.is_alive for r in self.team2)
        
        if not team1_alive and not team2_alive:
            return 0
        elif not team1_alive:
            return 2
        elif not team2_alive:
            return 1
        return -1
    
    def run(self) -> int:
        print("\n" + "=" * 60)
        print("🎮 战斗开始!".center(60))
        print("=" * 60)
        
        self.turn_count = 0
        max_turns = 50
        
        while max_turns > 0:
            self.turn_count += 1
            max_turns -= 1
            
            print(f"\n{'='*60}")
            print(f"⚔️  回合 {self.turn_count}".center(60))
            print(f"{'='*60}")
            
            print("\n【队伍 1】")
            for robot in self.team1:
                robot.display_status()
            
            print("\n【队伍 2】")
            for robot in self.team2:
                robot.display_status()
            
            all_alive = self.get_all_alive()
            all_alive.sort(key=lambda x: x.speed, reverse=True)
            
            for robot in all_alive:
                if robot.is_alive:
                    self.execute_turn(robot)
                    
                    winner = self.check_winner()
                    if winner != -1:
                        break
            
            winner = self.check_winner()
            if winner != -1:
                break
        
        self.show_result(winner)
        return winner
    
    def show_result(self, winner: int):
        print("\n" + "=" * 60)
        print("🏆 战斗结束!".center(60))
        print("=" * 60)
        
        if winner == 0:
            print("\n  🤝 平局！双方都全军覆没!")
        elif winner == 1:
            print("\n  🎉 队伍 1 获胜!")
            for robot in self.team1:
                if robot.is_alive:
                    print(f"    ✅ {robot.name} 存活 (HP: {robot.hp})")
        else:
            print("\n  🎉 队伍 2 获胜!")
            for robot in self.team2:
                if robot.is_alive:
                    print(f"    ✅ {robot.name} 存活 (HP: {robot.hp})")
        
        print(f"\n  总共进行了 {self.turn_count} 回合")


class Game:
    """游戏主类"""
    
    def __init__(self):
        self.teams: List[List[Robot]] = [[], []]
    
    def create_robot(self, name: str, robot_type: RobotType) -> Robot:
        stats = {
            RobotType.WARRIOR: {"hp": 120, "attack": 25, "defense": 15, "speed": 10},
            RobotType.ASSASSIN: {"hp": 90, "attack": 30, "defense": 8, "speed": 18},
            RobotType.TANK: {"hp": 150, "attack": 15, "defense": 25, "speed": 6},
            RobotType.SNIPER: {"hp": 80, "attack": 35, "defense": 5, "speed": 12},
            RobotType.SUPPORT: {"hp": 100, "attack": 18, "defense": 12, "speed": 11},
        }
        
        s = stats[robot_type]
        skills = []
        
        if robot_type == RobotType.WARRIOR:
            skills.append(Skill("强力打击", 35, 0.85, 2))
            skills.append(Skill("冲锋", 20, 0.95, 1))
        elif robot_type == RobotType.ASSASSIN:
            skills.append(Skill("背刺", 45, 0.7, 3))
            skills.append(Skill("烟雾弹", 10, 0.9, 2))
        elif robot_type == RobotType.TANK:
            skills.append(Skill("嘲讽", 15, 0.95, 2))
            skills.append(Skill("护盾", -20, 0.9, 4))
        elif robot_type == RobotType.SNIPER:
            skills.append(Skill("瞄准射击", 50, 0.6, 3))
            skills.append(Skill("快速射击", 20, 0.95, 1))
        
        return Robot(
            name=name,
            robot_type=robot_type,
            hp=s["hp"],
            max_hp=s["hp"],
            attack=s["attack"],
            defense=s["defense"],
            speed=s["speed"],
            skills=skills
        )
    
    def setup_teams(self):
        print("\n" + "=" * 60)
        print("🤖 机器人配置".center(60))
        print("=" * 60)
        
        print("\n【配置队伍 1】")
        self.teams[0] = [
            self.create_robot("雷霆战士", RobotType.WARRIOR),
            self.create_robot("暗影刺客", RobotType.ASSASSIN),
            self.create_robot("钢铁坦克", RobotType.TANK),
        ]
        
        print("\n【配置队伍 2】")
        self.teams[1] = [
            self.create_robot("鹰眼狙击手", RobotType.SNIPER),
            self.create_robot("圣光支援", RobotType.SUPPORT),
            self.create_robot("烈焰战士", RobotType.WARRIOR),
        ]
        
        print("\n✅ 队伍配置完成!")
        
        for i, team in enumerate(self.teams, 1):
            print(f"\n【队伍 {i}】")
            for robot in team:
                print(f"  • {robot.name} - {robot.robot_type.value}")
    
    def run(self):
        print("\n" + "🎮" * 30)
        print("机器人战斗游戏".center(60))
        print("🎮" * 30)
        
        print("\n  欢迎来到机器人战斗游戏!")
        print("  本游戏包含 5 种机器人类型:")
        print("  • 战士 - 均衡型，攻守兼备")
        print("  • 刺客 - 高闪避，高暴击")
        print("  • 坦克 - 高血量，高防御")
        print("  • 狙击手 - 高攻击，高暴击")
        print("  • 支援 - 可治疗队友")
        
        self.setup_teams()
        
        print("\n按回车键开始战斗...")
        input()
        
        battle = Battle(self.teams[0], self.teams[1])
        battle.run()
        
        print("\n" + "=" * 60)
        print("感谢游玩!".center(60))
        print("=" * 60)


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
