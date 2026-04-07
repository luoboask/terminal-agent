"""
游戏模块 - 包含 Robot 类和 Battle 类
"""

import random


class Robot:
    """机器人类，代表游戏中的战斗单位"""
    
    def __init__(self, name, health=100, attack=10, defense=5):
        """
        初始化机器人
        
        参数:
            name: 机器人名称
            health: 生命值 (默认 100)
            attack: 攻击力 (默认 10)
            defense: 防御力 (默认 5)
        """
        self.name = name
        self.max_health = health
        self.health = health
        self.attack = attack
        self.defense = defense
        self.is_alive = True
    
    def take_damage(self, damage):
        """
        受到伤害
        
        参数:
            damage: 原始伤害值
            
        返回:
            实际受到的伤害
        """
        actual_damage = max(1, damage - self.defense)
        self.health -= actual_damage
        self.health = max(0, self.health)
        
        if self.health <= 0:
            self.is_alive = False
        
        return actual_damage
    
    def attack_target(self, target):
        """
        攻击目标
        
        参数:
            target: 被攻击的 Robot 对象
            
        返回:
            造成的实际伤害
        """
        if not self.is_alive:
            return 0
        
        # 添加随机波动 (±20%)
        damage = self.attack * random.uniform(0.8, 1.2)
        damage = int(damage)
        
        actual_damage = target.take_damage(damage)
        return actual_damage
    
    def heal(self, amount):
        """
        治疗
        
        参数:
            amount: 治疗量
        """
        if not self.is_alive:
            return
        
        self.health = min(self.max_health, self.health + amount)
    
    def __str__(self):
        status = "存活" if self.is_alive else "已击败"
        return f"{self.name} [HP: {self.health}/{self.max_health}] [{status}]"
    
    def __repr__(self):
        return f"Robot(name='{self.name}', health={self.health}, attack={self.attack}, defense={self.defense})"


class Battle:
    """战斗类，管理两个机器人之间的战斗"""
    
    def __init__(self, robot1, robot2):
        """
        初始化战斗
        
        参数:
            robot1: 第一个 Robot 对象
            robot2: 第二个 Robot 对象
        """
        self.robot1 = robot1
        self.robot2 = robot2
        self.turn = 0
        self.battle_log = []
        self.winner = None
    
    def log(self, message):
        """记录战斗日志"""
        self.battle_log.append(message)
        print(message)
    
    def execute_turn(self):
        """
        执行一个回合
        
        返回:
            回合描述
        """
        self.turn += 1
        
        # 确定攻击顺序 (随机)
        if random.choice([True, False]):
            attacker, defender = self.robot1, self.robot2
        else:
            attacker, defender = self.robot2, self.robot1
        
        # 执行攻击
        damage = attacker.attack_target(defender)
        
        log_entry = f"第 {self.turn} 回合: {attacker.name} 攻击 {defender.name}, 造成 {damage} 点伤害"
        self.log(log_entry)
        
        return log_entry
    
    def is_over(self):
        """检查战斗是否结束"""
        if not self.robot1.is_alive:
            self.winner = self.robot2
            return True
        if not self.robot2.is_alive:
            self.winner = self.robot1
            return True
        return False
    
    def fight(self, max_turns=50):
        """
        进行完整战斗
        
        参数:
            max_turns: 最大回合数 (默认 50)
            
        返回:
            获胜的 Robot 对象，平局则返回 None
        """
        self.log("=" * 50)
        self.log(f"战斗开始! {self.robot1.name} VS {self.robot2.name}")
        self.log("=" * 50)
        
        while not self.is_over() and self.turn < max_turns:
            self.execute_turn()
            self.log(f"  {self.robot1}")
            self.log(f"  {self.robot2}")
            self.log("-" * 50)
        
        # 战斗结束
        self.log("=" * 50)
        if self.winner:
            self.log(f"战斗结束! 获胜者: {self.winner.name}")
        else:
            self.log("战斗结束! 结果: 平局")
        self.log("=" * 50)
        
        return self.winner
    
    def get_battle_summary(self):
        """
        获取战斗摘要
        
        返回:
            包含战斗信息的字典
        """
        return {
            "robot1": self.robot1.name,
            "robot2": self.robot2.name,
            "total_turns": self.turn,
            "winner": self.winner.name if self.winner else "平局",
            "log": self.battle_log
        }


# 示例用法
if __name__ == "__main__":
    # 创建两个机器人
    r1 = Robot("钢铁战士", health=120, attack=15, defense=8)
    r2 = Robot("闪电先锋", health=100, attack=18, defense=5)
    
    print(f"机器人 1: {r1}")
    print(f"机器人 2: {r2}")
    print()
    
    # 创建战斗并执行
    battle = Battle(r1, r2)
    winner = battle.fight()
    
    # 显示战斗摘要
    print("\n战斗摘要:")
    summary = battle.get_battle_summary()
    print(f"  总回合数：{summary['total_turns']}")
    print(f"  获胜者：{summary['winner']}")
