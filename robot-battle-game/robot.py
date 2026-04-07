#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机器人大战游戏 - 机器人模块
"""

import random
from typing import Optional, Dict, List


class Skill:
    """技能类"""
    def __init__(self, name: str, damage: int, accuracy: float, cooldown: int = 0, 
                 description: str = "", effect: str = "damage"):
        self.name = name
        self.damage = damage
        self.accuracy = accuracy  # 命中率 0-1
        self.cooldown = cooldown
        self.current_cooldown = 0
        self.description = description
        self.effect = effect  # damage, heal, buff, debuff
    
    def can_use(self) -> bool:
        return self.current_cooldown == 0
    
    def use(self):
        self.current_cooldown = self.cooldown
    
    def reduce_cooldown(self):
        if self.current_cooldown > 0:
            self.current_cooldown -= 1
    
    def __str__(self):
        status = "可用" if self.can_use() else f"冷却中 ({self.current_cooldown})"
        return f"{self.name} - 伤害:{self.damage} 命中:{self.accuracy*100:.0f}% [{status}]"


class Robot:
    """机器人类"""
    
    # 预设技能
    DEFAULT_SKILLS = [
        Skill("普通攻击", 15, 0.95, 0, "基础攻击技能"),
        Skill("激光炮", 25, 0.80, 2, "高伤害激光攻击", "damage"),
        Skill("导弹连射", 20, 0.85, 1, "连续发射导弹", "damage"),
        Skill("能量护盾", 0, 1.0, 3, "减少下次受到的伤害", "buff"),
        Skill("修复程序", 0, 1.0, 3, "恢复生命值", "heal"),
        Skill("电磁脉冲", 10, 0.70, 2, "降低敌人命中率", "debuff"),
    ]
    
    ROBOT_TYPES = {
        "突击型": {"hp": 120, "attack": 18, "defense": 10, "speed": 15},
        "坦克型": {"hp": 180, "attack": 12, "defense": 20, "speed": 8},
        "狙击型": {"hp": 100, "attack": 25, "defense": 8, "speed": 12},
        "平衡型": {"hp": 140, "attack": 15, "defense": 14, "speed": 13},
    }
    
    def __init__(self, name: str, robot_type: str = "平衡型", player_id: int = 1):
        self.name = name
        self.robot_type = robot_type
        self.player_id = player_id
        
        # 基础属性
        stats = self.ROBOT_TYPES.get(robot_type, self.ROBOT_TYPES["平衡型"])
        self.max_hp = stats["hp"]
        self.hp = self.max_hp
        self.base_attack = stats["attack"]
        self.base_defense = stats["defense"]
        self.speed = stats["speed"]
        
        # 战斗状态
        self.attack_buff = 0
        self.defense_buff = 0
        self.accuracy_buff = 0
        self.shield_active = False
        self.shield_strength = 0
        
        # 技能
        self.skills = self._create_skills()
        
        # 统计
        self.total_damage = 0
        self.damage_taken = 0
        self.skills_used = 0
    
    def _create_skills(self) -> List[Skill]:
        """创建技能列表"""
        skills = []
        for skill in self.DEFAULT_SKILLS:
            skills.append(Skill(
                name=skill.name,
                damage=skill.damage,
                accuracy=skill.accuracy,
                cooldown=skill.cooldown,
                description=skill.description,
                effect=skill.effect
            ))
        return skills
    
    @property
    def attack(self) -> int:
        return self.base_attack + self.attack_buff
    
    @property
    def defense(self) -> int:
        return self.base_defense + self.defense_buff
    
    @property
    def is_alive(self) -> bool:
        return self.hp > 0
    
    @property
    def hp_percentage(self) -> float:
        return self.hp / self.max_hp
    
    def take_damage(self, damage: int) -> int:
        """受到伤害，返回实际伤害值"""
        # 计算防御减免
        actual_damage = max(1, damage - self.defense)
        
        # 护盾减免
        if self.shield_active and self.shield_strength > 0:
            absorbed = min(actual_damage, self.shield_strength)
            self.shield_strength -= absorbed
            actual_damage -= absorbed
            if self.shield_strength <= 0:
                self.shield_active = False
        
        self.hp = max(0, self.hp - actual_damage)
        self.damage_taken += actual_damage
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """治疗，返回实际治疗量"""
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old_hp
    
    def use_skill(self, skill_index: int, target: Optional['Robot'] = None) -> Dict:
        """使用技能"""
        result = {
            "success": False,
            "message": "",
            "damage": 0,
            "heal": 0,
            "skill_name": ""
        }
        
        if skill_index < 0 or skill_index >= len(self.skills):
            result["message"] = "无效的技能索引"
            return result
        
        skill = self.skills[skill_index]
        result["skill_name"] = skill.name
        
        if not skill.can_use():
            result["message"] = f"{skill.name} 还在冷却中"
            return result
        
        # 使用技能
        skill.use()
        self.skills_used += 1
        
        # 命中判定
        hit_chance = skill.accuracy + self.accuracy_buff * 0.1
        if random.random() > hit_chance:
            result["message"] = f"{self.name} 使用 {skill.name}，但是未命中！"
            return result
        
        result["success"] = True
        
        # 根据效果类型处理
        if skill.effect == "damage" and target:
            damage = skill.damage + self.attack // 2
            actual_damage = target.take_damage(damage)
            self.total_damage += actual_damage
            result["damage"] = actual_damage
            result["message"] = f"{self.name} 使用 {skill.name} 对 {target.name} 造成 {actual_damage} 点伤害！"
            
            # 电磁脉冲特殊效果
            if skill.name == "电磁脉冲":
                target.accuracy_buff = -2
                result["message"] += f" {target.name} 命中率下降！"
        
        elif skill.effect == "heal":
            heal_amount = int(self.max_hp * 0.25)
            actual_heal = self.heal(heal_amount)
            result["heal"] = actual_heal
            result["message"] = f"{self.name} 使用 {skill.name} 恢复了 {actual_heal} 点生命值！"
        
        elif skill.effect == "buff":
            if skill.name == "能量护盾":
                self.shield_active = True
                self.shield_strength = int(self.max_hp * 0.3)
                result["message"] = f"{self.name} 激活 {skill.name}，获得 {self.shield_strength} 点护盾！"
        
        elif skill.effect == "debuff" and target:
            target.defense_buff = -5
            result["message"] = f"{self.name} 使用 {skill.name}，{target.name} 防御力下降！"
        
        return result
    
    def basic_attack(self, target: 'Robot') -> Dict:
        """普通攻击"""
        return self.use_skill(0, target)
    
    def end_turn(self):
        """回合结束，减少技能冷却"""
        for skill in self.skills:
            skill.reduce_cooldown()
        
        # 清除临时增益
        self.attack_buff = 0
        self.defense_buff = 0
        self.accuracy_buff = 0
    
    def get_status(self) -> str:
        """获取状态字符串"""
        hp_bar = self._get_hp_bar()
        return (f"{self.name} [{self.robot_type}]\n"
                f"  {hp_bar} {self.hp}/{self.max_hp}\n"
                f"  攻击:{self.attack} 防御:{self.defense} 速度:{self.speed}")
    
    def _get_hp_bar(self, length: int = 20) -> str:
        """获取血条"""
        filled = int(length * self.hp_percentage)
        empty = length - filled
        return f"[{'█' * filled}{'░' * empty}]"
    
    def get_skills_info(self) -> str:
        """获取技能信息"""
        lines = ["技能列表:"]
        for i, skill in enumerate(self.skills):
            lines.append(f"  {i}. {skill}")
        return "\n".join(lines)
    
    def reset(self):
        """重置机器人状态"""
        self.hp = self.max_hp
        self.attack_buff = 0
        self.defense_buff = 0
        self.accuracy_buff = 0
        self.shield_active = False
        self.shield_strength = 0
        self.total_damage = 0
        self.damage_taken = 0
        self.skills_used = 0
        for skill in self.skills:
            skill.current_cooldown = 0


def create_robot(name: str, robot_type: str = "平衡型", player_id: int = 1) -> Robot:
    """工厂函数创建机器人"""
    return Robot(name, robot_type, player_id)
