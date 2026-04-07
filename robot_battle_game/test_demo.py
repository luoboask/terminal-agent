#!/usr/bin/env python3
"""
🤖 机甲风暴 - 演示模式（自动战斗）
"""

from mech import Mech, MechType, Weapon, Element, create_default_mechs
from battle_system import BattleSystem, BattleConfig
import random


def auto_battle_action(mech, battle):
    """自动战斗行动"""
    if not mech.is_alive:
        return None
    
    # 确定敌我
    enemy_team = battle.enemy_team if mech in battle.player_team else battle.player_team
    
    # 寻找最近的目标
    closest_target = None
    min_dist = float('inf')
    
    for enemy in enemy_team:
        if enemy.is_alive:
            dist = battle.get_distance(mech.position, enemy.position)
            if dist < min_dist:
                min_dist = dist
                closest_target = enemy
    
    if not closest_target:
        return ("end_turn",)
    
    # 优先使用技能
    if mech.skills and mech.ap >= 5 and random.random() < 0.3:
        for i, skill in enumerate(mech.skills):
            if skill.is_ready() and mech.ap >= skill.ap_cost:
                print(f"  ✨ {mech.name} 使用技能：{skill.name}!")
                return ("skill", i, [])
    
    # 如果能攻击就攻击
    if mech.main_weapon and min_dist <= mech.main_weapon.range and mech.ap >= mech.main_weapon.ap_cost:
        print(f"  ⚔️ {mech.name} 使用 {mech.main_weapon.name} 攻击 {closest_target.name}!")
        return ("attack", 0, closest_target)
    
    # 否则移动靠近
    if mech.ap >= 2:
        new_x = mech.position[0]
        new_y = mech.position[1]
        
        if closest_target.position[0] > mech.position[0]:
            new_x += 1
        elif closest_target.position[0] < mech.position[0]:
            new_x -= 1
        
        if closest_target.position[1] > mech.position[1]:
            new_y += 1
        elif closest_target.position[1] < mech.position[1]:
            new_y -= 1
        
        new_pos = (min(7, max(0, new_x)), min(7, max(0, new_y)))
        if new_pos != mech.position:
            print(f"  🦶 {mech.name} 移动到 {new_pos}")
            return ("move", new_pos)
    
    return ("end_turn",)


def print_battle_status(battle):
    """打印战斗状态"""
    print("\n" + "="*50)
    print("⚔️  战场状态")
    print("="*50)
    
    print("\n🔵 玩家战队:")
    for mech in battle.player_team:
        if mech.is_alive:
            hp_bar = mech._get_hp_bar(8)
            print(f"  {mech.name:8} HP:{hp_bar} {mech.hp:3}/{mech.max_hp}  AP:{mech.ap:2}  pos:{mech.position}")
        else:
            print(f"  {mech.name:8} ❌ 击坠")
    
    print("\n🔴 敌方战队:")
    for mech in battle.enemy_team:
        if mech.is_alive:
            hp_bar = mech._get_hp_bar(8)
            print(f"  {mech.name:8} HP:{hp_bar} {mech.hp:3}/{mech.max_hp}  AP:{mech.ap:2}  pos:{mech.position}")
        else:
            print(f"  {mech.name:8} ❌ 击坠")
    
    print("="*50)


def main():
    """自动战斗演示"""
    print("="*50)
    print("🤖 机甲风暴 - 自动战斗演示")
    print("="*50)
    
    # 创建机甲
    all_mechs = create_default_mechs()
    player_team = [all_mechs[0], all_mechs[1]]  # 烈焰战神 + 寒冰守卫
    enemy_team = [all_mechs[2], all_mechs[3]]   # 雷霆射手 + 圣光天使
    
    print("\n📦 对战双方:")
    print(f"  🔵 玩家：{player_team[0].name}, {player_team[1].name}")
    print(f"  🔴 敌方：{enemy_team[0].name}, {enemy_team[1].name}")
    
    # 创建战斗系统
    config = BattleConfig(grid_size=8, max_ap=10, element_multiplier=1.5)
    battle = BattleSystem(player_team, enemy_team, config)
    
    print("\n🎮 战斗开始!\n")
    
    round_num = 1
    max_rounds = 15
    
    while round_num <= max_rounds:
        print(f"\n{'─'*50}")
        print(f"📍 第 {round_num} 回合")
        print(f"{'─'*50}")
        
        # 重置回合
        for mech in battle.player_team + battle.enemy_team:
            if mech.is_alive:
                mech.reset_turn()
        
        # 检查胜利
        result = battle.check_victory()
        if result is True:
            print("\n🎉 玩家获胜!")
            break
        elif result is False:
            print("\n💀 敌方获胜!")
            break
        
        # 玩家回合
        print("\n🔵 玩家行动:")
        for mech in battle.player_team:
            if mech.is_alive:
                print(f"\n  → {mech.name}:")
                while mech.ap >= 2:
                    action = auto_battle_action(mech, battle)
                    if action:
                        battle.execute_action(mech, action)
                        if action[0] == "end_turn":
                            break
                    else:
                        break
        
        # 检查胜利
        result = battle.check_victory()
        if result is not None:
            break
        
        # 敌方回合
        print("\n🔴 敌方行动:")
        for mech in battle.enemy_team:
            if mech.is_alive:
                print(f"\n  → {mech.name}:")
                while mech.ap >= 2:
                    action = auto_battle_action(mech, battle)
                    if action:
                        battle.execute_action(mech, action)
                        if action[0] == "end_turn":
                            break
                    else:
                        break
        
        print_battle_status(battle)
        round_num += 1
    
    # 最终结果
    print("\n" + "="*50)
    print("🏆 战斗结束!")
    print("="*50)
    print_battle_status(battle)
    
    print("\n📜 最近战况:")
    for log in battle.get_battle_log(10):
        print(f"  {log}")


if __name__ == "__main__":
    main()
