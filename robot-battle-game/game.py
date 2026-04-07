#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机器人大战游戏 - 主游戏逻辑（简化版）
"""

import random
from robot import Robot, create_robot

class Game:
    """游戏主控制器"""
    
    def __init__(self):
        self.robots = []
        self.battle = None
        self.game_over = False
    
    def create_robot(self, name=None):
        """创建新机器人"""
        if name is None:
            name = input("请输入机器人名称: ").strip()
            if not name:
                name = f"机器人{len(self.robots) + 1}"
        
        print("\n=== 选择机器人类型 ===")
        print("1. 均衡型 (各项能力平均)")
        print("2. 攻击型 (高攻击，低防御)")
        print("3. 防御型 (高防御，低速度)")
        print("4. 速度型 (高速度，低生命)")
        
        while True:
            choice = input("请选择类型 (1-4): ").strip()
            if choice in ['1', '2', '3', '4']:
                break
            print("无效选择，请重新输入")
        
        robot = Robot(name)
        
        # 根据类型调整属性
        if choice == '1':  # 均衡型
            robot.hp = 120
            robot.max_hp = 120
            robot.attack = 25
            robot.defense = 20
            robot.speed = 15
            robot.energy = 100
        elif choice == '2':  # 攻击型
            robot.hp = 100
            robot.max_hp = 100
            robot.attack = 35
            robot.defense = 15
            robot.speed = 18
            robot.energy = 100
        elif choice == '3':  # 防御型
            robot.hp = 150
            robot.max_hp = 150
            robot.attack = 18
            robot.defense = 30
            robot.speed = 10
            robot.energy = 100
        elif choice == '4':  # 速度型
            robot.hp = 90
            robot.max_hp = 90
            robot.attack = 22
            robot.defense = 15
            robot.speed = 28
            robot.energy = 100
        
        print(f"\n✅ 机器人 '{name}' 创建成功！")
        robot.display_status()
        return robot
    
    def setup_battle(self):
        """设置战斗"""
        print("\n" + "="*50)
        print("        🤖 机器人大战 - 战斗设置 🤖")
        print("="*50)
        
        # 创建玩家机器人
        print("\n【创建你的机器人】")
        player_robot = self.create_robot()
        self.robots.append(player_robot)
        
        # 创建敌方机器人
        print("\n【生成敌方机器人】")
        enemy_names = ["毁灭者", "钢铁巨兽", "雷霆战神", "暗影刺客", "火焰魔王"]
        enemy_name = random.choice(enemy_names)
        enemy_robot = Robot(enemy_name)
        
        # 随机生成敌人属性
        enemy_robot.hp = random.randint(100, 140)
        enemy_robot.max_hp = enemy_robot.hp
        enemy_robot.attack = random.randint(20, 30)
        enemy_robot.defense = random.randint(15, 25)
        enemy_robot.speed = random.randint(12, 22)
        enemy_robot.energy = 100
        
        print(f"\n⚠️  遭遇敌人：{enemy_name}")
        enemy_robot.display_status()
        
        self.robots.append(enemy_robot)
        
        # 创建战斗实例
        self.battle = Battle(self.robots[0], self.robots[1])
    
    def play(self):
        """开始游戏"""
        print("\n" + "="*50)
        print("        🎮 欢迎进入机器人大战游戏 🎮")
        print("="*50)
        print("\n游戏规则:")
        print("- 回合制战斗，速度高的先行动")
        print("- 普通攻击消耗 0 能量")
        print("- 技能攻击消耗能量，威力更大")
        print("- 防御可以减少受到的伤害")
        print("- 修理可以恢复生命值")
        print("- 先将对方生命值降为 0 者获胜")
        
        input("\n按回车键开始游戏...")
        
        # 设置战斗
        self.setup_battle()
        
        # 开始战斗
        print("\n" + "="*50)
        print("              ⚔️  战斗开始！⚔️")
        print("="*50)
        
        while not self.battle.is_over():
            self.battle.display_status()
            
            # 获取玩家行动
            current_robot = self.battle.get_current_robot()
            if current_robot == self.robots[0]:
                action = self.get_player_action()
            else:
                action = self.get_enemy_action()
            
            # 执行行动
            result = self.battle.execute_action(action)
            print(f"\n{result}")
            
            # 检查战斗是否结束
            if self.battle.is_over():
                break
        
        # 显示战斗结果
        self.show_result()
    
    def get_player_action(self):
        """获取玩家行动"""
        robot = self.robots[0]
        
        print(f"\n【{robot.name} 的回合】")
        print("请选择行动:")
        print("1. 普通攻击 (消耗 0 能量)")
        print("2. 强力攻击 (消耗 20 能量)")
        print("3. 防御 (消耗 10 能量)")
        print("4. 修理 (消耗 30 能量)")
        print("5. 终极技能 (消耗 50 能量)")
        print(f"\n当前能量：{robot.energy}/100")
        
        while True:
            choice = input("请输入选择 (1-5): ").strip()
            if choice in ['1', '2', '3', '4', '5']:
                actions = {
                    '1': 'attack',
                    '2': 'strong_attack',
                    '3': 'defend',
                    '4': 'repair',
                    '5': 'ultimate'
                }
                return actions[choice]
            print("无效选择，请重新输入")
    
    def get_enemy_action(self):
        """获取敌人行动 (AI)"""
        robot = self.robots[1]
        
        # 简单的 AI 逻辑
        if robot.energy >= 50 and robot.hp < robot.max_hp * 0.5:
            return 'ultimate'  # 生命低时使用终极技能
        elif robot.energy >= 30 and robot.hp < robot.max_hp * 0.7:
            return 'repair'  # 生命较低时修理
        elif robot.energy >= 20:
            return random.choice(['attack', 'strong_attack', 'strong_attack'])
        else:
            return 'attack'
    
    def show_result(self):
        """显示战斗结果"""
        print("\n" + "="*50)
        print("              🏆 战斗结束 🏆")
        print("="*50)
        
        winner = self.battle.get_winner()
        if winner:
            if winner == self.robots[0]:
                print(f"\n🎉 恭喜你！{winner.name} 获得了胜利！")
                print("   你证明了你是最强的机器人指挥官！")
            else:
                print(f"\n💀 很遗憾，{winner.name} 击败了你的机器人")
                print("   下次再战吧！")
        else:
            print("\n🤝 战斗以平局结束！")
        
        print("\n最终状态:")
        for robot in self.robots:
            robot.display_status()
        
        print("\n感谢游玩机器人大战游戏！")


def main():
    """游戏入口"""
    game = Game()
    game.play()


if __name__ == "__main__":
    main()
