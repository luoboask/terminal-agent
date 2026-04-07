#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机器人类定义
"""

import random
from typing import Optional


class Robot:
    """机器人基类"""
    
    def __init__(self, name: str, hp: int = 100, attack: int = 15, defense: int = 10):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.energy = 100
        self.is_alive = True
    
    def take_damage(self, damage: int) -> int:
        """承受伤害"""
        actual_damage = max(1, damage - self.defense)
        self.hp -= actual_damage
        if self.hp <= 0:
            self.hp = 0
            self.is_alive = False
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """治疗"""
        heal_amount = min(amount, self.max_hp - self.hp)
        self.hp += heal_amount
        return heal_amount
    
    def basic_attack(self, target: 'Robot') -> dict:
        """基础攻击"""
        damage = random.randint(self.attack - 5, self.attack + 5)
        actual_damage = target.take_damage(damage)
        self.energy = min(100, self.energy + 10)
        return {
            'attacker': self.name,
            'target': target.name,
            'damage': actual_damage,
            'type': 'basic'
        }
    
    def special_attack(self, target: 'Robot') -> Optional[dict]:
        """特殊攻击"""
        if self.energy < 30:
            return None
        
        self.energy -= 30
        damage = random.randint(self.attack * 1.5 - 5, self.attack * 1.5 + 5)
        actual_damage = target.take_damage(int(damage))
        return {
            'attacker': self.name,
            'target': target.name,
            'damage': actual_damage,
            'type': 'special'
        }
    
    def defend(self) -> dict:
        """防御"""
        self.defense += 5
        self.energy = min(100, self.energy + 15)
        return {
            'robot': self.name,
            'action': 'defend',
            'defense_boost': 5
        }
    
    def reset_defense(self):
        """重置防御"""
        self.defense = max(10, self.defense - 5)
    
    def get_status(self) -> str:
        """获取状态字符串"""
        hp_bar = self._create_bar(self.hp, self.max_hp, 20)
        energy_bar = self._create_bar(self.energy, 100, 10)
        status = "⚡" if self.energy >= 30 else "⚠️"
        return f"{status} {self.name}: HP [{hp_bar}] {self.hp}/{self.max_hp} | EP [{energy_bar}] {self.energy}/100"
    
    @staticmethod
    def _create_bar(current: int, maximum: int, length: int) -> str:
        """创建进度条"""
        filled = int(length * current / maximum)
        empty = length - filled
        return "█" * filled + "░" * empty
    
    def __str__(self) -> str:
        return f"{self.name} (HP: {self.hp}/{self.max_hp})"


class AttackRobot(Robot):
    """攻击型机器人"""
    
    def __init__(self, name: str):
        super().__init__(name, hp=80, attack=25, defense=8)
    
    def special_attack(self, target: Robot) -> Optional[dict]:
        """狂暴攻击"""
        if self.energy < 30:
            return None
        
        self.energy -= 30
        damage = random.randint(self.attack * 2 - 5, self.attack * 2 + 5)
        actual_damage = target.take_damage(int(damage))
        return {
            'attacker': self.name,
            'target': target.name,
            'damage': actual_damage,
            'type': 'special',
            'skill_name': '狂暴攻击'
        }


class TankRobot(Robot):
    """坦克型机器人"""
    
    def __init__(self, name: str):
        super().__init__(name, hp=150, attack=12, defense=15)
    
    def special_attack(self, target: Robot) -> Optional[dict]:
        """反击护盾"""
        if self.energy < 30:
            return None
        
        self.energy -= 30
        self.defense += 10
        heal = self.heal(20)
        return {
            'robot': self.name,
            'action': 'special',
            'skill_name': '反击护盾',
            'defense_boost': 10,
            'heal': heal
        }


class SpeedRobot(Robot):
    """速度型机器人"""
    
    def __init__(self, name: str):
        super().__init__(name, hp=70, attack=18, defense=6)
    
    def special_attack(self, target: Robot) -> Optional[dict]:
        """连击"""
        if self.energy < 30:
            return None
        
        self.energy -= 30
        total_damage = 0
        for _ in range(3):
            damage = random.randint(self.attack - 3, self.attack + 3)
            total_damage += target.take_damage(damage)
        return {
            'attacker': self.name,
            'target': target.name,
            'damage': total_damage,
            'type': 'special',
            'skill_name': '连击',
            'hits': 3
        }
