"""
机器人类定义
包含不同类型的机器人及其属性、技能
"""

import random
from enum import Enum
from typing import List, Dict, Optional
from config import RobotType, SkillType


class Skill:
    """技能类"""
    
    def __init__(self, name: str, skill_type: SkillType, damage: int, 
                 accuracy: float, cooldown: int, description: str):
        self.name = name
        self.skill_type = skill_type
        self.damage = damage
        self.accuracy = accuracy  # 命中率 0-1
        self.cooldown = cooldown  # 冷却回合数
        self.current_cooldown = 0
        self.description = description
    
    def can_use(self) -> bool:
        """技能是否可用"""
        return self.current_cooldown == 0
    
    def use(self) -> bool:
        """使用技能，返回是否命中"""
        if not self.can_use():
            return False
        self.current_cooldown = self.cooldown
        return random.random() <= self.accuracy
    
    def reduce_cooldown(self):
        """减少冷却时间"""
        if self.current_cooldown > 0:
            self.current_cooldown -= 1
    
    def __str__(self):
        status = "可用" if self.can_use() else f"冷却中({self.current_cooldown})"
        return f"{self.name} [{status}] - {self.description}"


class Robot:
    """机器人类"""
    
    def __init__(self, name: str, robot_type: RobotType, player_id: int = 0):
        self.name = name
        self.robot_type = robot_type
        self.player_id = player_id  # 0 表示玩家，1 表示敌人
        
        # 根据类型设置基础属性
        self._set_base_stats()
        
        # 当前状态
        self.current_hp = self.max_hp
        self.current_energy = self.max_energy
        self.is_alive = True
        self.level = 1
        self.exp = 0
        
        # 技能列表
        self.skills: List[Skill] = []
        self._init_skills()
    
    def _set_base_stats(self):
        """根据机器人类型设置基础属性"""
        if self.robot_type == RobotType.WARRIOR:
            self.max_hp = 150
            self.max_energy = 80
            self.attack = 25
            self.defense = 20
            self.speed = 15
            self.critical_rate = 0.15
        elif self.robot_type == RobotType.ASSASSIN:
            self.max_hp = 100
            self.max_energy = 100
            self.attack = 35
            self.defense = 12
            self.speed = 25
            self.critical_rate = 0.25
        elif self.robot_type == RobotType.TANK:
            self.max_hp = 200
            self.max_energy = 60
            self.attack = 18
            self.defense = 30
            self.speed = 10
            self.critical_rate = 0.10
        elif self.robot_type == RobotType.SNIPER:
            self.max_hp = 90
            self.max_energy = 90
            self.attack = 40
            self.defense = 10
            self.speed = 20
            self.critical_rate = 0.30
        elif self.robot_type == RobotType.SUPPORT:
            self.max_hp = 120
            self.max_energy = 120
            self.attack = 15
            self.defense = 15
            self.speed = 18
            self.critical_rate = 0.10
        else:
            # 默认属性
            self.max_hp = 120
            self.max_energy = 80
            self.attack = 20
            self.defense = 15
            self.speed = 15
            self.critical_rate = 0.15
    
    def _init_skills(self):
        """初始化技能"""
        if self.robot_type == RobotType.WARRIOR:
            self.skills = [
                Skill("重击", SkillType.ATTACK, 35, 0.9, 2, "强力近战攻击"),
                Skill("战吼", SkillType.BUFF, 0, 1.0, 3, "提升攻击力 30%"),
                Skill("旋风斩", SkillType.ATTACK, 25, 0.85, 3, "对敌人造成多次伤害"),
            ]
        elif self.robot_type == RobotType.ASSASSIN:
            self.skills = [
                Skill("背刺", SkillType.ATTACK, 45, 0.8, 2, "高伤害背后攻击"),
                Skill("隐身", SkillType.BUFF, 0, 1.0, 4, "提升闪避率"),
                Skill("致命一击", SkillType.ATTACK, 60, 0.7, 5, "超高伤害但命中率低"),
            ]
        elif self.robot_type == RobotType.TANK:
            self.skills = [
                Skill("盾击", SkillType.ATTACK, 20, 0.95, 1, "稳定的攻击"),
                Skill("铁壁", SkillType.BUFF, 0, 1.0, 3, "大幅提升防御"),
                Skill("嘲讽", SkillType.DEBUFF, 0, 0.9, 3, "强制敌人攻击自己"),
            ]
        elif self.robot_type == RobotType.SNIPER:
            self.skills = [
                Skill("精准射击", SkillType.ATTACK, 50, 0.85, 2, "高伤害远程攻击"),
                Skill("瞄准", SkillType.BUFF, 0, 1.0, 2, "提升下次攻击命中率"),
                Skill("狙击", SkillType.ATTACK, 80, 0.6, 5, "超远距离致命一击"),
            ]
        elif self.robot_type == RobotType.SUPPORT:
            self.skills = [
                Skill("能量光束", SkillType.ATTACK, 20, 0.9, 1, "基础能量攻击"),
                Skill("修复", SkillType.HEAL, 40, 1.0, 3, "恢复生命值"),
                Skill("能量充能", SkillType.BUFF, 0, 1.0, 3, "恢复能量"),
            ]
    
    def take_damage(self, damage: int) -> int:
        """受到伤害，返回实际伤害值"""
        # 计算防御减免
        actual_damage = max(1, damage - self.defense // 2)
        
        # 暴击判断
        is_critical = random.random() < self.critical_rate
        if is_critical:
            actual_damage = int(actual_damage * 1.5)
        
        self.current_hp = max(0, self.current_hp - actual_damage)
        
        if self.current_hp == 0:
            self.is_alive = False
        
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """治疗，返回实际治疗量"""
        actual_heal = min(amount, self.max_hp - self.current_hp)
        self.current_hp += actual_heal
        return actual_heal
    
    def use_skill(self, skill_index: int, target: Optional['Robot'] = None) -> Dict:
        """使用技能"""
        result = {
            'success': False,
            'message': '',
            'damage': 0,
            'heal': 0,
            'is_critical': False
        }
        
        if skill_index < 0 or skill_index >= len(self.skills):
            result['message'] = "无效的技能索引"
            return result
        
        skill = self.skills[skill_index]
        
        if not skill.can_use():
            result['message'] = f"{skill.name} 还在冷却中"
            return result
        
        # 消耗能量
        energy_cost = skill.damage // 2 if skill.damage > 0 else 10
        if self.current_energy < energy_cost:
            result['message'] = "能量不足"
            return result
        
        self.current_energy -= energy_cost
        
        # 使用技能
        if skill.skill_type == SkillType.ATTACK:
            if target is None:
                result['message'] = "需要指定目标"
                self.current_energy += energy_cost
                return result
            
            if skill.use():  # 命中
                damage = skill.damage + self.attack // 2
                is_critical = random.random() < self.critical_rate
                if is_critical:
                    damage = int(damage * 1.5)
                
                actual_damage = target.take_damage(damage)
                result['damage'] = actual_damage
                result['is_critical'] = is_critical
                result['success'] = True
                result['message'] = f"{self.name} 使用 {skill.name} 对 {target.name} 造成 {actual_damage} 点伤害！"
            else:
                result['message'] = f"{self.name} 使用 {skill.name} 但未命中！"
                # 未命中返还部分能量
                self.current_energy += energy_cost // 2
        
        elif skill.skill_type == SkillType.HEAL:
            if skill.use():
                actual_heal = self.heal(skill.damage)
                result['heal'] = actual_heal
                result['success'] = True
                result['message'] = f"{self.name} 使用 {skill.name} 恢复了 {actual_heal} 点生命值！"
        
        elif skill.skill_type == SkillType.BUFF:
            if skill.use():
                result['success'] = True
                result['message'] = f"{self.name} 使用 {skill.name}，效果生效！"
                # 简单实现：立即恢复一些生命值或能量
                if self.robot_type == RobotType.SUPPORT or self.robot_type == RobotType.TANK:
                    heal_amount = self.max_hp // 5
                    actual_heal = self.heal(heal_amount)
                    result['heal'] = actual_heal
                    result['message'] += f" 恢复了 {actual_heal} 点生命值"
        
        elif skill.skill_type == SkillType.DEBUFF:
            if skill.use():
                result['success'] = True
                result['message'] = f"{self.name} 使用 {skill.name}，效果生效！"
        
        # 减少其他技能的冷却
        for s in self.skills:
            if s != skill:
                s.reduce_cooldown()
        
        return result
    
    def basic_attack(self, target: 'Robot') -> Dict:
        """普通攻击"""
        result = {
            'success': False,
            'message': '',
            'damage': 0,
            'is_critical': False
        }
        
        # 命中率基于速度
        hit_chance = 0.8 + (self.speed - target.speed) * 0.01
        hit_chance = max(0.5, min(0.95, hit_chance))
        
        if random.random() <= hit_chance:
            damage = self.attack
            is_critical = random.random() < self.critical_rate
            if is_critical:
                damage = int(damage * 1.5)
            
            actual_damage = target.take_damage(damage)
            result['damage'] = actual_damage
            result['is_critical'] = is_critical
            result['success'] = True
            
            crit_str = " (暴击!)" if is_critical else ""
            result['message'] = f"{self.name} 普通攻击对 {target.name} 造成 {actual_damage} 点伤害{crit_str}！"
        else:
            result['message'] = f"{self.name} 的普通攻击未命中！"
        
        # 攻击后恢复少量能量
        self.current_energy = min(self.max_energy, self.current_energy + 5)
        
        # 减少技能冷却
        for skill in self.skills:
            skill.reduce_cooldown()
        
        return result
    
    def recover(self):
        """回合结束恢复"""
        # 每回合自然恢复能量
        recover_energy = max(5, self.max_energy // 10)
        self.current_energy = min(self.max_energy, self.current_energy + recover_energy)
    
    def gain_exp(self, exp: int):
        """获得经验"""
        self.exp += exp
        # 简单升级机制
        exp_needed = self.level * 100
        if self.exp >= exp_needed:
            self.level_up()
    
    def level_up(self):
        """升级"""
        self.level += 1
        self.exp = 0
        # 提升属性
        self.max_hp += 20
        self.max_energy += 10
        self.attack += 3
        self.defense += 2
        self.current_hp = self.max_hp
        self.current_energy = self.max_energy
    
    def get_status(self) -> str:
        """获取状态字符串"""
        hp_percent = self.current_hp / self.max_hp * 100
        energy_percent = self.current_energy / self.max_energy * 100
        
        status_lines = [
            f"{self.name} (Lv.{self.level} {self.robot_type.value})",
            f"HP: {self.current_hp}/{self.max_hp} [{'█' * int(hp_percent/10)}{'░' * (10-int(hp_percent/10))}] {hp_percent:.0f}%",
            f"能量：{self.current_energy}/{self.max_energy} [{'█' * int(energy_percent/10)}{'░' * (10-int(energy_percent/10))}] {energy_percent:.0f}%",
            f"攻击：{self.attack} 防御：{self.defense} 速度：{self.speed}"
        ]
        
        return "\n".join(status_lines)
    
    def get_skills_info(self) -> str:
        """获取技能信息"""
        lines = ["技能列表:"]
        for i, skill in enumerate(self.skills):
            lines.append(f"  [{i+1}] {skill}")
        return "\n".join(lines)
    
    def __str__(self):
        return f"{self.name} [{self.robot_type.value}]"
