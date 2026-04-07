"""
机甲类定义 - 机器人大战游戏核心模块
"""

from enum import Enum
from typing import List, Tuple, Optional
import random


class MechType(Enum):
    """机甲类型"""
    ASSAULT = "突击型"      # 高机动、近战强力
    ARTILLERY = "炮击型"    # 远程攻击、火力覆盖
    DEFENSE = "防御型"      # 高护甲、团队保护
    SUPPORT = "支援型"      # 治疗、增益、侦查


class Element(Enum):
    """属性类型"""
    FIRE = "火"
    ICE = "冰"
    ELECTRIC = "电"
    NORMAL = "普通"


# 属性克制关系：key 克制 value
ELEMENT_COUNTER = {
    Element.FIRE: Element.ICE,
    Element.ICE: Element.ELECTRIC,
    Element.ELECTRIC: Element.FIRE
}


class Weapon:
    """武器类"""
    def __init__(self, name: str, damage: int, range_: int, ap_cost: int, 
                 element: Element = Element.NORMAL, weapon_type: str = "物理"):
        self.name = name
        self.damage = damage
        self.range = range_
        self.ap_cost = ap_cost
        self.element = element
        self.weapon_type = weapon_type
    
    def __str__(self):
        return f"{self.name} (伤害:{self.damage} 射程:{self.range} AP:{self.ap_cost})"


class Skill:
    """技能类"""
    def __init__(self, name: str, effect: str, ap_cost: int, cooldown: int = 0):
        self.name = name
        self.effect = effect
        self.ap_cost = ap_cost
        self.cooldown = cooldown
        self.current_cooldown = 0
    
    def is_ready(self) -> bool:
        return self.current_cooldown == 0
    
    def use(self):
        self.current_cooldown = self.cooldown
    
    def tick(self):
        if self.current_cooldown > 0:
            self.current_cooldown -= 1
    
    def __str__(self):
        status = "就绪" if self.is_ready() else f"CD:{self.current_cooldown}"
        return f"{self.name} ({self.effect}) AP:{self.ap_cost} [{status}]"


class Mech:
    """机甲类"""
    def __init__(self, name: str, mech_type: MechType, hp: int, attack: int, 
                 defense: int, speed: int, element: Element = Element.NORMAL):
        self.name = name
        self.mech_type = mech_type
        self.element = element
        
        # 基础属性
        self.max_hp = hp
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.speed = speed
        
        # 战斗属性
        self.ap = 10  # 行动点数
        self.max_ap = 10
        self.position = (0, 0)
        
        # 装备
        self.main_weapon: Optional[Weapon] = None
        self.sub_weapon: Optional[Weapon] = None
        self.skills: List[Skill] = []
        
        # 状态
        self.is_alive = True
        self.buffs = []
        self.debuffs = []
    
    def take_damage(self, damage: int, element: Element = Element.NORMAL) -> int:
        """受到伤害，返回实际伤害值"""
        # 属性克制计算
        multiplier = 1.0
        if element in ELEMENT_COUNTER and ELEMENT_COUNTER[element] == self.element:
            multiplier = 1.5  # 被克制，伤害增加
        elif self.element in ELEMENT_COUNTER and ELEMENT_COUNTER[self.element] == element:
            multiplier = 0.7  # 克制对方，伤害减少
        
        # 防御减免
        actual_damage = max(1, int((damage - self.defense * 0.3) * multiplier))
        self.hp = max(0, self.hp - actual_damage)
        
        if self.hp == 0:
            self.is_alive = False
        
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """治疗，返回实际治疗量"""
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old_hp
    
    def move(self, new_position: Tuple[int, int], max_distance: int) -> bool:
        """移动到新位置"""
        old_x, old_y = self.position
        new_x, new_y = new_position
        distance = abs(new_x - old_x) + abs(new_y - old_y)
        
        if distance <= max_distance:
            self.position = new_position
            self.ap -= 2  # 移动消耗 AP
            return True
        return False
    
    def attack_target(self, target: 'Mech', weapon: Optional[Weapon] = None) -> Tuple[bool, int]:
        """攻击目标，返回 (是否命中，伤害值)"""
        if weapon is None:
            weapon = self.main_weapon
        
        if weapon is None:
            return False, 0
        
        if self.ap < weapon.ap_cost:
            return False, 0
        
        # 距离检查
        distance = abs(self.position[0] - target.position[0]) + \
                   abs(self.position[1] - target.position[1])
        
        if distance > weapon.range:
            return False, 0
        
        self.ap -= weapon.ap_cost
        
        # 命中率计算（简单版本）
        hit_rate = 0.85 + (self.speed - target.speed) * 0.02
        hit_rate = max(0.5, min(0.95, hit_rate))
        
        if random.random() > hit_rate:
            return False, 0
        
        # 计算伤害
        damage = self.take_damage(weapon.damage, weapon.element)
        return True, damage
    
    def use_skill(self, skill_index: int, targets: List['Mech'] = None) -> bool:
        """使用技能"""
        if skill_index < 0 or skill_index >= len(self.skills):
            return False
        
        skill = self.skills[skill_index]
        
        if not skill.is_ready():
            return False
        
        if self.ap < skill.ap_cost:
            return False
        
        self.ap -= skill.ap_cost
        skill.use()
        return True
    
    def reset_turn(self):
        """回合开始重置"""
        self.ap = min(self.max_ap, self.ap + 5)  # 每回合恢复 5 点 AP
        for skill in self.skills:
            skill.tick()
    
    def get_status(self) -> str:
        """获取状态字符串"""
        status = "存活" if self.is_alive else "❌ 击坠"
        hp_bar = self._get_hp_bar()
        return f"{self.name} [{self.mech_type.value}] {status}\n  HP: {hp_bar} {self.hp}/{self.max_hp}\n  AP: {self.ap}/{self.max_ap}\n  位置：{self.position}"
    
    def _get_hp_bar(self, length: int = 10) -> str:
        """获取 HP 条"""
        ratio = self.hp / self.max_hp
        filled = int(length * ratio)
        return f"[{'█' * filled}{'░' * (length - filled)}]"
    
    def __str__(self):
        return f"{self.name} ({self.mech_type.value}) - HP:{self.hp}/{self.max_hp}"


# 预设机甲模板
def create_default_mechs() -> List[Mech]:
    """创建默认机甲"""
    mechs = [
        Mech("烈焰战神", MechType.ASSAULT, hp=120, attack=25, defense=15, speed=18, element=Element.FIRE),
        Mech("寒冰守卫", MechType.DEFENSE, hp=180, attack=15, defense=25, speed=10, element=Element.ICE),
        Mech("雷霆射手", MechType.ARTILLERY, hp=100, attack=30, defense=10, speed=15, element=Element.ELECTRIC),
        Mech("圣光天使", MechType.SUPPORT, hp=90, attack=12, defense=12, speed=16, element=Element.NORMAL),
    ]
    
    # 添加默认武器
    mechs[0].main_weapon = Weapon("烈焰斩", damage=35, range_=2, ap_cost=4, element=Element.FIRE)
    mechs[0].sub_weapon = Weapon("火焰机枪", damage=15, range_=4, ap_cost=2, element=Element.FIRE)
    
    mechs[1].main_weapon = Weapon("冰霜重炮", damage=25, range_=3, ap_cost=4, element=Element.ICE)
    mechs[1].sub_weapon = Weapon("护盾发生器", damage=0, range_=1, ap_cost=3, element=Element.ICE)
    
    mechs[2].main_weapon = Weapon("雷电狙击", damage=45, range_=8, ap_cost=5, element=Element.ELECTRIC)
    mechs[2].sub_weapon = Weapon("电击手枪", damage=18, range_=4, ap_cost=2, element=Element.ELECTRIC)
    
    mechs[3].main_weapon = Weapon("圣光射线", damage=20, range_=5, ap_cost=3, element=Element.NORMAL)
    mechs[3].sub_weapon = Weapon("治疗光束", damage=0, range_=4, ap_cost=3, element=Element.NORMAL)
    
    # 添加技能
    mechs[0].skills.append(Skill("烈焰风暴", "对范围内敌人造成 50 点伤害", ap_cost=6, cooldown=3))
    mechs[1].skills.append(Skill("绝对零度", "冻结敌人 1 回合", ap_cost=5, cooldown=4))
    mechs[2].skills.append(Skill("雷暴降临", "对全体敌人造成 30 点伤害", ap_cost=7, cooldown=5))
    mechs[3].skills.append(Skill("神圣复苏", "复活一个队友并恢复 50HP", ap_cost=8, cooldown=6))
    mechs[3].skills.append(Skill("能量护盾", "为队友提供护盾", ap_cost=4, cooldown=2))
    
    return mechs


if __name__ == "__main__":
    # 测试代码
    print("=== 机甲系统测试 ===\n")
    
    mechs = create_default_mechs()
    for mech in mechs:
        print(mech.get_status())
        print(f"  主武器：{mech.main_weapon}")
        print(f"  技能：{', '.join([str(s) for s in mech.skills])}")
        print()
