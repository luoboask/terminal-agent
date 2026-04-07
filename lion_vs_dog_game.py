#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🦁 狮子大战小狗 🐕
一个有趣的回合制战斗游戏
"""

import random
import time

class Character:
    def __init__(self, name, health, attack, defense, skills):
        self.name = name
        self.max_health = health
        self.health = health
        self.attack = attack
        self.defense = defense
        self.skills = skills
    
    def is_alive(self):
        return self.health > 0
    
    def take_damage(self, damage):
        actual_damage = max(1, damage - self.defense)
        self.health = max(0, self.health - actual_damage)
        return actual_damage
    
    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)
    
    def display_status(self):
        health_bar = "❤️" * (self.health // 10) + "💔" * ((self.max_health - self.health) // 10)
        print(f"{self.name}: {health_bar} {self.health}/{self.max_health} HP")


class Skill:
    def __init__(self, name, damage, accuracy, effect=None):
        self.name = name
        self.damage = damage
        self.accuracy = accuracy
        self.effect = effect


def create_lion():
    """创建狮子角色"""
    skills = [
        Skill("利爪攻击", 25, 0.9),
        Skill("怒吼", 15, 1.0, "intimidate"),
        Skill("猛扑", 35, 0.7),
        Skill("王者之怒", 45, 0.6)
    ]
    return Character("🦁 草原之王", 150, 30, 8, skills)


def create_dog():
    """创建小狗角色"""
    skills = [
        Skill("汪汪咬", 20, 0.95),
        Skill("灵活闪避", 0, 1.0, "dodge"),
        Skill("疯狂乱咬", 30, 0.75),
        Skill("主人呼唤", 0, 1.0, "heal")
    ]
    return Character("🐕 勇敢小狗", 120, 25, 5, skills)


def player_turn(player, enemy):
    """玩家回合"""
    print(f"\n{'='*50}")
    print(f"⚔️  {player.name} 的回合!")
    print(f"{'='*50}")
    
    player.display_status()
    enemy.display_status()
    
    print("\n选择技能:")
    for i, skill in enumerate(player.skills, 1):
        print(f"  {i}. {skill.name} (伤害: {skill.damage}, 命中: {skill.accuracy*100:.0f}%)")
    
    while True:
        try:
            choice = int(input(f"\n请输入技能编号 (1-{len(player.skills)}): "))
            if 1 <= choice <= len(player.skills):
                break
            print("无效的选择，请重新输入!")
        except ValueError:
            print("请输入数字!")
    
    skill = player.skills[choice - 1]
    use_skill(player, enemy, skill)


def enemy_turn(enemy, player):
    """敌人回合"""
    print(f"\n{'='*50}")
    print(f"😈 {enemy.name} 的回合!")
    print(f"{'='*50}")
    
    time.sleep(1)
    skill = random.choice(enemy.skills)
    use_skill(enemy, player, skill)


def use_skill(attacker, defender, skill):
    """使用技能"""
    print(f"\n✨ {attacker.name} 使用了 {skill.name}!")
    time.sleep(0.5)
    
    # 检查命中
    if random.random() > skill.accuracy:
        print(f"💨 攻击未命中!")
        return
    
    # 处理特殊效果
    if skill.effect == "heal":
        heal_amount = 30
        attacker.heal(heal_amount)
        print(f"💖 {attacker.name} 恢复了 {heal_amount} 点生命值!")
    elif skill.effect == "dodge":
        print(f"🙈 {attacker.name} 进入了闪避状态，下次攻击有 50% 几率躲避!")
        # 简化处理，这里只是显示效果
    elif skill.effect == "intimidate":
        print(f"😱 {defender.name} 被吓住了，防御力暂时下降!")
        damage = skill.damage
        actual_damage = defender.take_damage(damage)
        print(f"💥 造成 {actual_damage} 点伤害!")
    else:
        damage = skill.damage
        actual_damage = defender.take_damage(damage)
        print(f"💥 造成 {actual_damage} 点伤害!")
    
    if not defender.is_alive():
        print(f"\n💀 {defender.name} 被打败了!")


def battle():
    """主战斗循环"""
    print("\n" + "🎮"*30)
    print("🦁  狮 子 大 战 小 狗  🐕")
    print("🎮"*30)
    
    print("\n选择你的角色:")
    print("1. 🦁 狮子 (高血量，高攻击)")
    print("2. 🐕 小狗 (灵活，有治疗技能)")
    
    while True:
        choice = input("\n请输入选择 (1 或 2): ")
        if choice == "1":
            player = create_lion()
            enemy = create_dog()
            break
        elif choice == "2":
            player = create_dog()
            enemy = create_lion()
            break
        print("无效选择，请重新输入!")
    
    print(f"\n🎯 战斗开始! {player.name} VS {enemy.name}")
    time.sleep(1)
    
    turn = 0
    while player.is_alive() and enemy.is_alive():
        turn += 1
        print(f"\n{'🔥'*20}")
        print(f"第 {turn} 回合")
        print(f"{'🔥'*20}")
        
        # 玩家回合
        player_turn(player, enemy)
        
        if not enemy.is_alive():
            break
        
        # 敌人回合
        enemy_turn(enemy, player)
    
    # 战斗结束
    print(f"\n{'🏆'*30}")
    if player.is_alive():
        print(f"🎉 恭喜! {player.name} 获得了胜利!")
        print(f"🏆 你是一位真正的战士!")
    else:
        print(f"😢 遗憾! {player.name} 被打败了...")
        print(f"💪 不要放弃，再来一次!")
    print(f"{'🏆'*30}")
    
    # 显示最终状态
    print(f"\n最终状态:")
    player.display_status()
    enemy.display_status()


def main():
    """主函数"""
    while True:
        battle()
        
        again = input("\n是否再来一局？(y/n): ").lower()
        if again != 'y':
            print("\n感谢游玩! 再见! 👋")
            break
        print("\n" + "="*60)


if __name__ == "__main__":
    main()
