# -*- coding: utf-8 -*-
"""
机器人大战游戏 - 主程序
"""

import random
import time
from typing import List, Optional, Dict
from robot import Robot, create_robot, Skill


class Battle:
    """战斗系统类"""
    
    def __init__(self, robots: List[Robot], battle_mode: str = "pve"):
        self.robots = robots
        self.battle_mode = battle_mode  # pve, pvp, ai_vs_ai
        self.current_turn = 0
        self.battle_log: List[str] = []
        self.winner: Optional[Robot] = None
        
    def log(self, message: str):
        """记录战斗日志"""
        self.battle_log.append(message)
        print(message)
        
    def get_alive_robots(self) -> List[Robot]:
        """获取存活的机器人"""
        return [r for r in self.robots if r.is_alive]
    
    def get_robot_order(self) -> List[Robot]:
        """根据速度决定行动顺序"""
        alive = self.get_alive_robots()
        return sorted(alive, key=lambda r: r.speed + random.randint(0, 5), reverse=True)
    
    def is_battle_over(self) -> bool:
        """判断战斗是否结束"""
        alive = self.get_alive_robots()
        if len(alive) <= 1:
            if len(alive) == 1:
                self.winner = alive[0]
            return True
        return False
    
    def player_choice(self, robot: Robot, enemies: List[Robot]) -> tuple:
        """玩家选择行动"""
        print(f"\n{'='*50}")
        print(f"{robot.name} 的回合!")
        print(f"{'='*50}")
        
        # 显示敌人状态
        print("\n敌方状态:")
        for i, enemy in enumerate(enemies):
            if enemy.is_alive:
                print(f"  {i}. {enemy.name} - HP: {enemy.hp}/{enemy.max_hp}")
        
        # 选择目标
        while True:
            try:
                target_idx = int(input("\n选择目标 (编号): "))
                if 0 <= target_idx < len(enemies) and enemies[target_idx].is_alive:
                    target = enemies[target_idx]
                    break
                print("无效的目标，请重新选择")
            except EOFError:
                # 非交互式环境，随机选择目标
                target = random.choice([e for e in enemies if e.is_alive])
                print(f"\n⚡  自动选择目标：{target.name}")
                break
            except (ValueError, IndexError):
                print("请输入有效的数字")
        
        # 选择行动
        print(f"\n选择行动:")
        print("  0. 普通攻击")
        for i, skill in enumerate(robot.skills[1:], 1):
            status = "可用" if skill.can_use() else f"冷却 ({skill.current_cooldown})"
            print(f"  {i}. {skill.name} - {skill.description} [{status}]")
        print("  D. 防御 (本回合防御加倍)")
        
        while True:
            try:
                choice = input("\n你的选择: ").strip().upper()
            except EOFError:
                # 非交互式环境，使用普通攻击
                print("\n⚡  自动选择：普通攻击")
                return ('skill', 0, target)
            
            if choice == 'D':
                return ('defend', None, target)
            
            try:
                skill_idx = int(choice)
                if 0 <= skill_idx < len(robot.skills):
                    skill = robot.skills[skill_idx]
                    if skill.can_use():
                        return ('skill', skill_idx, target)
                    else:
                        print(f"{skill.name} 还在冷却中，请选择其他技能")
                        continue
                print("无效的技能编号")
            except ValueError:
                print("请输入有效的数字")
    
    def ai_choice(self, robot: Robot, enemies: List[Robot]) -> tuple:
        """AI 选择行动"""
        # 选择血量最低的敌人
        alive_enemies = [e for e in enemies if e.is_alive]
        if not alive_enemies:
            return ('skip', None, None)
            
        target = min(alive_enemies, key=lambda e: e.hp)
        
        # 根据血量决定是否使用治疗
        if robot.hp < robot.max_hp * 0.3:
            heal_skill = next((s for s in robot.skills if s.effect == "heal" and s.can_use()), None)
            if heal_skill:
                return ('skill', robot.skills.index(heal_skill), robot)
        
        # 随机选择可用技能
        available_skills = [i for i, s in enumerate(robot.skills) if s.can_use()]
        if available_skills and random.random() < 0.6:
            skill_idx = random.choice(available_skills)
            return ('skill', skill_idx, target)
        
        return ('skill', 0, target)  # 普通攻击
    
    def execute_action(self, robot: Robot, action_type: str, skill_idx: int, target: Robot) -> Dict:
        """执行行动"""
        result = {"damage": 0, "heal": 0, "message": ""}
        
        if action_type == 'defend':
            robot.defense_buff = robot.defense
            result["message"] = f"{robot.name} 进入防御姿态，防御力提升!"
            
        elif action_type == 'skill':
            if skill_idx == 0:
                # 普通攻击
                result = robot.basic_attack(target)
            else:
                result = robot.use_skill(skill_idx, target)
        
        if result.get("message"):
            self.log(result["message"])
            
        return result
    
    def run(self, auto_play: bool = False):
        """运行战斗"""
        self.log(f"\n{'='*60}")
        self.log(f"战斗开始！{len(self.robots)} 台机器人进入战场!")
        self.log(f"{'='*60}\n")
        
        # 显示初始状态
        for robot in self.robots:
            self.log(robot.get_status())
            self.log("")
        
        time.sleep(1)
        
        while not self.is_battle_over():
            self.current_turn += 1
            self.log(f"\n{'='*60}")
            self.log(f"第 {self.current_turn} 回合")
            self.log(f"{'='*60}")
            
            order = self.get_robot_order()
            
            for robot in order:
                if not robot.is_alive:
                    continue
                    
                if self.is_battle_over():
                    break
                
                # 确定敌人
                enemies = [r for r in self.robots if r.player_id != robot.player_id and r.is_alive]
                if not enemies:
                    continue
                
                # 决定行动
                # PVP 模式或 PVE 模式下玩家控制时，使用玩家选择
                # 否则使用 AI 选择
                if self.battle_mode == "pvp":
                    action = self.player_choice(robot, enemies)
                elif self.battle_mode == "pve" and robot.player_id == 1 and not auto_play:
                    try:
                        action = self.player_choice(robot, enemies)
                    except EOFError:
                        # 非交互式环境，切换到 AI 控制
                        self.log(f"\n⚡  {robot.name} 切换到 AI 控制（非交互式环境）...")
                        action = self.ai_choice(robot, enemies)
                else:
                    action = self.ai_choice(robot, enemies)
                    self.log(f"\n{robot.name} 思考中...")
                    time.sleep(1)
                
                # 执行行动
                action_type, skill_idx, target = action
                if target and target.is_alive:
                    self.execute_action(robot, action_type, skill_idx, target)
                
                robot.end_turn()
                
                # 显示状态
                print(f"\n{robot.get_status()}")
                if target and target.is_alive:
                    print(f"{target.get_status()}")
                
                time.sleep(1.5)
        
        # 战斗结束
        self.log(f"\n{'='*60}")
        if self.winner:
            self.log(f"🏆 战斗结束！获胜者是：{self.winner.name}!")
            self.log(f"{'='*60}")
        else:
            self.log("🤝 战斗平局!")
            
        # 显示统计
        self.show_stats()
        
        return self.winner
    
    def show_stats(self):
        """显示战斗统计"""
        print("\n📊 战斗统计:")
        print("-" * 40)
        for robot in self.robots:
            print(f"{robot.name}:")
            print(f"  总伤害：{robot.total_damage}")
            print(f"  受到伤害：{robot.damage_taken}")
            print(f"  使用技能次数：{robot.skills_used}")
            print()


class Game:
    """游戏主类"""
    
    def __init__(self):
        self.robots: List[Robot] = []
        self.player_count = 0
        
    def show_title(self):
        """显示标题"""
        title = """
        ╔════════════════════════════════════════╗
        ║         🤖 机器人大战 🤖                ║
        ║           ROBOT BATTLE                 ║
        ╚════════════════════════════════════════╝
        """
        print(title)
        
    def show_robot_types(self):
        """显示机器人类型"""
        print("\n📋 机器人类型:")
        print("-" * 40)
        types_info = {
            "突击型": "高攻击，中等血量 - 适合进攻",
            "坦克型": "超高血量，高防御 - 适合防守",
            "狙击型": "超高攻击，低血量 - 玻璃大炮",
            "平衡型": "各项均衡 - 适合新手"
        }
        for t, desc in types_info.items():
            print(f"  {t}: {desc}")
        print()
        
    def create_player_robot(self, player_id: int) -> Robot:
        """创建玩家机器人"""
        print(f"\n{'='*50}")
        print(f"玩家 {player_id} 创建机器人")
        print(f"{'='*50}")
        
        name = input("请输入机器人名字: ").strip()
        if not name:
            name = f"机器人{player_id}"
            
        self.show_robot_types()
        
        while True:
            robot_type = input("选择机器人类型 (突击型/坦克型/狙击型/平衡型): ").strip()
            if robot_type in Robot.ROBOT_TYPES:
                break
            print("无效的类型，请重新输入")
            
        robot = create_robot(name, robot_type, player_id)
        print(f"\n✅ {name} 创建成功!")
        print(robot.get_status())
        
        return robot
    
    def create_ai_robot(self, player_id: int) -> Robot:
        """创建 AI 机器人"""
        names = ["雷霆", "风暴", "暗影", "烈焰", "冰霜", "闪电", "钢铁", "毁灭"]
        types = list(Robot.ROBOT_TYPES.keys())
        
        name = f"{random.choice(names)}-{random.randint(100, 999)}"
        robot_type = random.choice(types)
        
        robot = create_robot(name, robot_type, player_id)
        print(f"🤖 AI 机器人 {name} ({robot_type}) 已准备!")
        
        return robot
    
    def setup_1v1_pve(self):
        """设置 1v1 人机对战"""
        print("\n🎮 人机对战模式")
        
        # 玩家机器人
        player_robot = self.create_player_robot(1)
        self.robots.append(player_robot)
        
        # AI 机器人
        ai_robot = self.create_ai_robot(2)
        self.robots.append(ai_robot)
        
        return Battle(self.robots, "pve")
    
    def setup_1v1_pvp(self):
        """设置 1v1 玩家对战"""
        print("\n🎮 玩家对战模式")
        
        # 玩家 1
        robot1 = self.create_player_robot(1)
        self.robots.append(robot1)
        
        input("\n按回车键切换到玩家 2...")
        
        # 玩家 2
        robot2 = self.create_player_robot(2)
        self.robots.append(robot2)
        
        return Battle(self.robots, "pvp")
    
    def setup_ai_vs_ai(self):
        """设置 AI 对战 AI"""
        print("\n🤖 AI 对战模式")
        
        robot1 = self.create_ai_robot(1)
        self.robots.append(robot1)
        
        robot2 = self.create_ai_robot(2)
        self.robots.append(robot2)
        
        return Battle(self.robots, "ai_vs_ai")
    
    def main_menu(self) -> Optional[str]:
        """显示主菜单"""
        print("\n" + "="*50)
        print("请选择游戏模式:")
        print("="*50)
        print("  1. 人机对战 (玩家 vs 电脑)")
        print("  2. 玩家对战 (玩家 1 vs 玩家 2)")
        print("  3. AI 对战 (电脑 vs 电脑)")
        print("  4. 退出游戏")
        print("="*50)
        
        choice = input("你的选择 (1-4): ").strip()
        
        if choice == '1':
            return 'pve'
        elif choice == '2':
            return 'pvp'
        elif choice == '3':
            return 'ai'
        elif choice == '4':
            return 'quit'
        else:
            print("无效选择")
            return None
    
    def run(self):
        """运行游戏"""
        self.show_title()
        
        while True:
            # 重置
            self.robots = []
            
            mode = self.main_menu()
            
            if mode == 'quit':
                print("\n感谢游玩！再见！👋")
                break
                
            if not mode:
                continue
            
            # 创建战斗
            if mode == 'pve':
                battle = self.setup_1v1_pve()
            elif mode == 'pvp':
                battle = self.setup_1v1_pvp()
            else:
                battle = self.setup_ai_vs_ai()
            
            # 运行战斗
            if mode == 'ai':
                battle.run(auto_play=True)
            else:
                battle.run()
            
            # 询问是否继续
            again = input("\n再来一局？(y/n): ").strip().lower()
            if again != 'y':
                print("\n感谢游玩！再见！👋")
                break


def main():
    """主函数"""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
