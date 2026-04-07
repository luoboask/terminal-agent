#!/usr/bin/env python3
"""
🤖 机甲风暴 - 主程序
机甲风暴 (Mecha Storm) - 机器人大战游戏
"""

from mech import Mech, MechType, Weapon, Element, create_default_mechs
from battle_system import BattleSystem, BattleConfig


def print_battle_status(battle):
    """打印战斗状态"""
    print("\n" + "="*60)
    print("⚔️  战场状态")
    print("="*60)
    
    print("\n🔵 玩家战队:")
    for mech in battle.player_team:
        if mech.is_alive:
            hp_percent = (mech.hp / mech.max_hp) * 100
            bar = "█" * int(hp_percent / 10) + "░" * (10 - int(hp_percent / 10))
            print(f"  {mech.name} [{mech.mech_type.value}]")
            print(f"    HP: [{bar}] {mech.hp}/{mech.max_hp}")
            print(f"    AP: {mech.ap}/10  位置：{mech.position}")
            if mech.main_weapon:
                print(f"    武器：{mech.main_weapon.name}")
    
    print("\n🔴 敌方战队:")
    for mech in battle.enemy_team:
        if mech.is_alive:
            hp_percent = (mech.hp / mech.max_hp) * 100
            bar = "█" * int(hp_percent / 10) + "░" * (10 - int(hp_percent / 10))
            print(f"  {mech.name} [{mech.mech_type.value}]")
            print(f"    HP: [{bar}] {mech.hp}/{mech.max_hp}")
            print(f"    AP: {mech.ap}/10  位置：{mech.position}")
            if mech.main_weapon:
                print(f"    武器：{mech.main_weapon.name}")
        else:
            print(f"  ❌ {mech.name} [已击坠]")
    
    print("="*60)


def print_available_actions(mech, battle):
    """打印可用行动"""
    print(f"\n🎯 {mech.name} 的可用行动 (AP: {mech.ap}):")
    print("  1. 移动 (消耗 2 AP)")
    
    idx = 2
    if mech.main_weapon:
        print(f"  {idx}. 攻击：{mech.main_weapon.name} (伤害:{mech.main_weapon.damage}, 范围:{mech.main_weapon.range}, AP:{mech.main_weapon.ap_cost})")
        idx += 1
    
    if mech.sub_weapon:
        print(f"  {idx}. 攻击：{mech.sub_weapon.name} (伤害:{mech.sub_weapon.damage}, 范围:{mech.sub_weapon.range}, AP:{mech.sub_weapon.ap_cost})")
        idx += 1
    
    for i, skill in enumerate(mech.skills):
        status = "✓" if skill.is_ready() else f"CD:{skill.current_cooldown}"
        print(f"  {idx}. 技能：{skill.name} ({skill.effect}) AP:{skill.ap_cost} [{status}]")
        idx += 1
    
    print(f"  {idx}. 防御 (消耗 3 AP, 防御 +50%)")
    print(f"  {idx + 1}. 结束回合")


def get_player_action(mech, battle):
    """获取玩家输入"""
    print_available_actions(mech, battle)
    
    while True:
        try:
            choice = input("\n请选择行动 (输入数字): ").strip()
            if not choice.isdigit():
                print("❌ 请输入有效的数字!")
                continue
                
            choice_num = int(choice)
            
            if choice_num == 1:
                # 移动
                print("请输入新位置 (格式：x,y)，范围 0-7:")
                pos_input = input("位置：").strip()
                try:
                    x, y = map(int, pos_input.split(","))
                    if 0 <= x <= 7 and 0 <= y <= 7:
                        return ("move", (x, y))
                    else:
                        print("❌ 位置超出范围!")
                except ValueError:
                    print("❌ 格式错误！请使用 x,y 格式")
            
            elif choice_num == 2 and mech.main_weapon:
                # 主武器攻击
                weapon = mech.main_weapon
                return get_attack_action(mech, battle, weapon, 0)
            
            elif choice_num == 3 and mech.sub_weapon:
                # 副武器攻击
                weapon = mech.sub_weapon
                return get_attack_action(mech, battle, weapon, 1)
            
            elif mech.main_weapon and choice_num == 3 + len(mech.skills):
                # 防御
                return ("defend",)
            
            elif mech.main_weapon and choice_num == 4 + len(mech.skills):
                # 结束回合
                return ("end_turn",)
            
            elif mech.skills and 3 <= choice_num <= 2 + len(mech.skills):
                # 使用技能
                skill_idx = choice_num - 3
                return get_skill_action(mech, battle, skill_idx)
            
            else:
                print("❌ 无效的选择!")
        
        except KeyboardInterrupt:
            print("\n\n游戏退出!")
            exit()
        except Exception as e:
            print(f"❌ 错误：{e}")


def get_attack_action(mech, battle, weapon, weapon_idx):
    """获取攻击目标"""
    if mech.ap < weapon.ap_cost:
        print(f"❌ AP 不足! 需要 {weapon.ap_cost} 点")
        return None
    
    print("\n选择目标:")
    targets = []
    enemy_team = battle.enemy_team if mech in battle.player_team else battle.player_team
    
    for i, enemy in enumerate(enemy_team):
        if enemy.is_alive:
            dist = battle.get_distance(mech.position, enemy.position)
            if dist <= weapon.range:
                targets.append(enemy)
                print(f"  {i+1}. {enemy.name} (距离:{dist}, HP:{enemy.hp})")
            else:
                print(f"  {i+1}. {enemy.name} (距离:{dist}, HP:{enemy.hp}) - 超出射程")
    
    if not targets:
        print("❌ 没有可攻击的目标!")
        return None
    
    try:
        target_idx = int(input("目标编号：")) - 1
        if 0 <= target_idx < len(enemy_team):
            target = enemy_team[target_idx]
            if not target.is_alive:
                print("❌ 目标已被击坠!")
                return None
            return ("attack", weapon_idx, target)
        else:
            print("❌ 无效的目标!")
    except ValueError:
        print("❌ 请输入有效的数字!")
    
    return None


def get_skill_action(mech, battle, skill_idx):
    """获取技能目标"""
    skill = mech.skills[skill_idx]
    
    if not skill.is_ready():
        print(f"❌ 技能还在冷却中!")
        return None
    
    if mech.ap < skill.ap_cost:
        print(f"❌ AP 不足!")
        return None
    
    # 简单处理：治疗技能选择队友，攻击技能选择敌人
    if "治疗" in skill.effect or "恢复" in skill.effect:
        print("\n选择队友:")
        teammates = [m for m in battle.player_team if m.is_alive]
        for i, teammate in enumerate(teammates):
            print(f"  {i+1}. {teammate.name} (HP:{teammate.hp})")
        
        try:
            idx = int(input("目标编号：")) - 1
            if 0 <= idx < len(teammates):
                return ("skill", skill_idx, [teammates[idx]])
        except ValueError:
            pass
    else:
        # 攻击技能
        return ("skill", skill_idx, [])
    
    return None


def auto_enemy_action(mech, battle):
    """敌方自动行动"""
    if not mech.is_alive:
        return None
    
    # 寻找最近的目标
    closest_target = None
    min_dist = float('inf')
    
    for player in battle.player_team:
        if player.is_alive:
            dist = battle.get_distance(mech.position, player.position)
            if dist < min_dist:
                min_dist = dist
                closest_target = player
    
    if not closest_target:
        return ("end_turn",)
    
    # 如果有武器可以攻击
    if mech.main_weapon and min_dist <= mech.main_weapon.range:
        print(f"  🤖 {mech.name} 使用 {mech.main_weapon.name} 攻击 {closest_target.name}!")
        return ("attack", 0, closest_target)
    
    # 否则移动靠近
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
        print(f"  🤖 {mech.name} 移动到 {new_pos}")
        return ("move", new_pos)
    
    return ("end_turn",)


def main():
    """主游戏循环"""
    print("="*60)
    print("🤖 欢迎来到《机甲风暴》(Mecha Storm)!")
    print("="*60)
    
    # 创建机甲
    all_mechs = create_default_mechs()
    player_team = [all_mechs[0], all_mechs[1]]  # 烈焰战神 + 寒冰守卫
    enemy_team = [all_mechs[2], all_mechs[3]]   # 雷霆射手 + 圣光天使
    
    print(f"\n📦 玩家战队:")
    for mech in player_team:
        print(f"  • {mech.name} ({mech.mech_type.value}) - HP:{mech.max_hp}")
        print(f"    武器：{mech.main_weapon.name if mech.main_weapon else '无'}")
    
    print(f"\n📦 敌方战队:")
    for mech in enemy_team:
        print(f"  • {mech.name} ({mech.mech_type.value}) - HP:{mech.max_hp}")
        print(f"    武器：{mech.main_weapon.name if mech.main_weapon else '无'}")
    
    # 创建战斗系统
    config = BattleConfig(
        grid_size=8,
        max_ap=10,
        element_multiplier=1.5
    )
    
    battle = BattleSystem(player_team, enemy_team, config)
    
    print("\n🎮 战斗开始!")
    print("提示：输入位置时使用 x,y 格式，如 3,4")
    
    round_num = 1
    max_rounds = 20
    
    while round_num <= max_rounds:
        print(f"\n{'='*60}")
        print(f"📍 第 {round_num} 回合")
        print(f"{'='*60}")
        
        # 重置回合
        for mech in battle.player_team + battle.enemy_team:
            if mech.is_alive:
                mech.reset_turn()
        
        print_battle_status(battle)
        
        # 检查胜利条件
        result = battle.check_victory()
        if result is True:
            print("\n🎉 恭喜！玩家获胜!")
            break
        elif result is False:
            print("\n💀 失败！敌方获胜!")
            break
        
        # 玩家回合
        print("\n🔵 === 玩家回合 ===")
        for mech in battle.player_team:
            if mech.is_alive:
                print(f"\n⚡ {mech.name} 行动!")
                
                while mech.ap >= 2:  # 至少需要 2 AP 才能行动
                    action = get_player_action(mech, battle)
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
        
        if battle.check_victory() is not None:
            break
        
        # 敌方回合
        print("\n🔴 === 敌方回合 ===")
        for mech in battle.enemy_team:
            if mech.is_alive:
                print(f"\n⚡ {mech.name} 行动!")
                
                while mech.ap >= 2:
                    action = auto_enemy_action(mech, battle)
                    if action:
                        battle.execute_action(mech, action)
                        if action[0] == "end_turn":
                            break
                    else:
                        break
        
        round_num += 1
    
    # 显示最终结果
    print("\n" + "="*60)
    print("🏆 战斗结束!")
    print("="*60)
    print_battle_status(battle)
    
    print("\n📜 战斗日志:")
    for log in battle.get_battle_log(15):
        print(f"  {log}")


if __name__ == "__main__":
    main()
