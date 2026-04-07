"""
战斗系统模块 - 机器人大战游戏核心模块
"""

from typing import List, Tuple, Optional
from mech import Mech, MechType, Weapon, Element


class BattleConfig:
    """战斗配置"""
    def __init__(self, grid_size: int = 8, max_ap: int = 10, 
                 element_multiplier: float = 1.5):
        self.grid_size = grid_size
        self.max_ap = max_ap
        self.element_multiplier = element_multiplier


class BattleSystem:
    """战斗系统"""
    
    def __init__(self, player_team: List[Mech], enemy_team: List[Mech], 
                 config: Optional[BattleConfig] = None):
        self.player_team = player_team
        self.enemy_team = enemy_team
        self.config = config or BattleConfig()
        self.current_round = 1
        self.battle_log = []
        
        # 初始化位置
        self._init_positions()
    
    def _init_positions(self):
        """初始化机甲位置"""
        # 玩家方在下半区
        for i, mech in enumerate(self.player_team):
            mech.position = (i, self.config.grid_size - 1)
        
        # 敌方在上半区
        for i, mech in enumerate(self.enemy_team):
            mech.position = (i, 0)
    
    def get_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """计算曼哈顿距离"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def is_valid_position(self, pos: Tuple[int, int]) -> bool:
        """检查位置是否有效"""
        x, y = pos
        return 0 <= x < self.config.grid_size and 0 <= y < self.config.grid_size
    
    def execute_action(self, mech: Mech, action: Tuple) -> bool:
        """执行行动"""
        action_type = action[0]
        
        if action_type == "move":
            return self._execute_move(mech, action[1])
        
        elif action_type == "attack":
            weapon_idx = action[1]
            target = action[2]
            weapon = mech.main_weapon if weapon_idx == 0 else mech.sub_weapon
            return self._execute_attack(mech, target, weapon)
        
        elif action_type == "defend":
            return self._execute_defend(mech)
        
        elif action_type == "skill":
            skill_idx = action[1]
            targets = action[2] if len(action) > 2 else []
            return self._execute_skill(mech, skill_idx, targets)
        
        elif action_type == "end_turn":
            return True
        
        return False
    
    def _execute_move(self, mech: Mech, new_pos: Tuple[int, int]) -> bool:
        """执行移动"""
        if not self.is_valid_position(new_pos):
            self._log(f"❌ {mech.name} 移动失败：位置无效")
            return False
        
        distance = self.get_distance(mech.position, new_pos)
        ap_cost = 2  # 移动消耗 AP
        
        if mech.ap < ap_cost:
            self._log(f"❌ {mech.name} AP 不足，无法移动")
            return False
        
        old_pos = mech.position
        mech.position = new_pos
        mech.ap -= ap_cost
        
        self._log(f"🦶 {mech.name} 从 {old_pos} 移动到 {new_pos} (消耗 {ap_cost} AP)")
        return True
    
    def _execute_attack(self, attacker: Mech, target: Mech, weapon: Weapon) -> bool:
        """执行攻击"""
        if not weapon:
            self._log(f"❌ {attacker.name} 没有装备武器")
            return False
        
        if attacker.ap < weapon.ap_cost:
            self._log(f"❌ {attacker.name} AP 不足，无法使用 {weapon.name}")
            return False
        
        if not target.is_alive:
            self._log(f"❌ {target.name} 已被击坠，无法攻击")
            return False
        
        distance = self.get_distance(attacker.position, target.position)
        
        if distance > weapon.range:
            self._log(f"❌ {attacker.name} 距离目标太远 (距离:{distance}, 射程:{weapon.range})")
            return False
        
        # 执行攻击
        attacker.ap -= weapon.ap_cost
        hit, damage = attacker.attack_target(target, weapon)
        
        if hit:
            self._log(f"⚔️ {attacker.name} 使用 {weapon.name} 攻击 {target.name}!")
            self._log(f"   💥 造成 {damage} 点伤害! {target.name} HP: {target.hp}/{target.max_hp}")
            
            # 属性克制提示
            if weapon.element != Element.NORMAL:
                if weapon.element in {Element.FIRE, Element.ICE, Element.ELECTRIC}:
                    counter_map = {Element.FIRE: Element.ICE, Element.ICE: Element.ELECTRIC, Element.ELECTRIC: Element.FIRE}
                    if counter_map.get(weapon.element) == target.element:
                        self._log(f"   🔥 属性克制！伤害增加!")
        else:
            self._log(f"💨 {attacker.name} 的攻击被 {target.name} 躲开了!")
        
        return True
    
    def _execute_defend(self, mech: Mech) -> bool:
        """执行防御"""
        if mech.ap < 3:
            self._log(f"❌ {mech.name} AP 不足，无法防御")
            return False
        
        mech.ap -= 3
        mech.defense = int(mech.defense * 1.5)  # 临时提升防御
        self._log(f"🛡️ {mech.name} 进入防御姿态，防御力提升!")
        return True
    
    def _execute_skill(self, mech: Mech, skill_idx: int, targets: List[Mech]) -> bool:
        """执行技能"""
        if skill_idx < 0 or skill_idx >= len(mech.skills):
            self._log(f"❌ 无效的技能索引")
            return False
        
        skill = mech.skills[skill_idx]
        
        if not skill.is_ready():
            self._log(f"❌ {skill.name} 还在冷却中")
            return False
        
        if mech.ap < skill.ap_cost:
            self._log(f"❌ {mech.name} AP 不足，无法使用 {skill.name}")
            return False
        
        mech.ap -= skill.ap_cost
        skill.use()
        
        self._log(f"✨ {mech.name} 使用技能 {skill.name}!")
        self._log(f"   效果：{skill.effect}")
        
        # 简单处理技能效果
        if "治疗" in skill.effect or "恢复" in skill.effect:
            for target in targets or [mech]:
                heal_amount = 50
                actual_heal = target.heal(heal_amount)
                self._log(f"   💚 {target.name} 恢复 {actual_heal} HP")
        
        elif "伤害" in skill.effect:
            all_targets = self.player_team if mech in self.enemy_team else self.enemy_team
            for target in all_targets:
                if target.is_alive:
                    damage = 30
                    actual_damage = target.take_damage(damage)
                    self._log(f"   💥 {target.name} 受到 {actual_damage} 点伤害")
        
        return True
    
    def check_victory(self) -> Optional[bool]:
        """检查胜利条件，返回 True(玩家胜)/False(敌方胜)/None(继续)"""
        player_alive = sum(1 for m in self.player_team if m.is_alive)
        enemy_alive = sum(1 for m in self.enemy_team if m.is_alive)
        
        if player_alive > 0 and enemy_alive == 0:
            self._log("🎉 玩家战队获胜!")
            return True
        
        if player_alive == 0 and enemy_alive > 0:
            self._log("💀 敌方战队获胜!")
            return False
        
        return None
    
    def _log(self, message: str):
        """记录战斗日志"""
        self.battle_log.append(f"[第{self.current_round}回合] {message}")
        print(message)
    
    def get_battle_log(self, last_n: int = 10) -> List[str]:
        """获取最近的战斗日志"""
        return self.battle_log[-last_n:]
    
    def print_status(self):
        """打印战场状态"""
        print("\n" + "="*60)
        print("⚔️  战场状态")
        print("="*60)
        
        print("\n🔵 玩家战队:")
        for mech in self.player_team:
            print(f"  {mech.get_status()}")
            if mech.main_weapon:
                print(f"    主武器：{mech.main_weapon.name}")
        
        print("\n🔴 敌方战队:")
        for mech in self.enemy_team:
            if mech.is_alive:
                print(f"  {mech.get_status()}")
                if mech.main_weapon:
                    print(f"    主武器：{mech.main_weapon.name}")
            else:
                print(f"  ❌ {mech.name} [已击坠]")
        
        print("="*60)
