"""
成就系统 - 宠物成就管理
"""
from enum import Enum
from datetime import datetime
from typing import Dict, List, Optional


class AchievementType(Enum):
    """成就类型"""
    INTERACTION = "互动"
    GROWTH = "成长"
    CARE = "照顾"
    SPECIAL = "特殊"


class Achievement:
    """单个成就"""
    
    def __init__(self, id: str, name: str, description: str, 
                 achievement_type: AchievementType,
                 requirement: int, reward_exp: int = 50):
        self.id = id
        self.name = name
        self.description = description
        self.achievement_type = achievement_type
        self.requirement = requirement  # 达成所需的数量
        self.reward_exp = reward_exp
        self.unlocked = False
        self.unlocked_date: Optional[datetime] = None
        self.progress = 0  # 当前进度
    
    def check_unlock(self, current_value: int) -> bool:
        """检查是否解锁成就"""
        if not self.unlocked and current_value >= self.requirement:
            self.unlocked = True
            self.unlocked_date = datetime.now()
            self.progress = current_value
            return True
        self.progress = min(current_value, self.requirement)
        return False
    
    def to_dict(self) -> dict:
        """序列化为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.achievement_type.name,
            "requirement": self.requirement,
            "reward_exp": self.reward_exp,
            "unlocked": self.unlocked,
            "unlocked_date": self.unlocked_date.isoformat() if self.unlocked_date else None,
            "progress": self.progress
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Achievement":
        """从字典反序列化"""
        achievement = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            achievement_type=AchievementType[data["type"]],
            requirement=data["requirement"],
            reward_exp=data["reward_exp"]
        )
        achievement.unlocked = data["unlocked"]
        achievement.progress = data["progress"]
        if data.get("unlocked_date"):
            achievement.unlocked_date = datetime.fromisoformat(data["unlocked_date"])
        return achievement
    
    def __str__(self):
        status = "✅" if self.unlocked else "🔒"
        return f"{status} {self.name}: {self.description} ({self.progress}/{self.requirement})"


class AchievementSystem:
    """成就系统管理器"""
    
    # 预定义成就列表
    DEFAULT_ACHIEVEMENTS = [
        # 互动类成就
        Achievement("first_interaction", "初次互动", "第一次与宠物互动", 
                   AchievementType.INTERACTION, 1, 20),
        Achievement("friendly", "友好伙伴", "与宠物互动 50 次", 
                   AchievementType.INTERACTION, 50, 50),
        Achievement("best_friend", "最佳拍档", "与宠物互动 200 次", 
                   AchievementType.INTERACTION, 200, 100),
        Achievement("soulmate", "灵魂伴侣", "与宠物互动 1000 次", 
                   AchievementType.INTERACTION, 1000, 200),
        
        # 成长类成就
        Achievement("first_level", "初出茅庐", "宠物达到 5 级", 
                   AchievementType.GROWTH, 5, 30),
        Achievement("experienced", "经验丰富", "宠物达到 10 级", 
                   AchievementType.GROWTH, 10, 60),
        Achievement("veteran", "资深训练师", "宠物达到 20 级", 
                   AchievementType.GROWTH, 20, 120),
        Achievement("master", "大师级", "宠物达到 50 级", 
                   AchievementType.GROWTH, 50, 300),
        
        # 照顾类成就
        Achievement("good_feeder", "喂食达人", "喂食 100 次", 
                   AchievementType.CARE, 100, 50),
        Achievement("clean_master", "清洁大师", "清洁 50 次", 
                   AchievementType.CARE, 50, 40),
        Achievement("health_keeper", "健康卫士", "治疗 20 次", 
                   AchievementType.CARE, 20, 60),
        Achievement("perfect_care", "完美照顾", "所有属性保持在 90 以上 10 次", 
                   AchievementType.CARE, 10, 150),
        
        # 特殊成就
        Achievement("lucky", "幸运儿", "触发 10 次幸运事件", 
                   AchievementType.SPECIAL, 10, 100),
        Achievement("survivor", "生存专家", "宠物存活 30 天", 
                   AchievementType.SPECIAL, 30, 200),
        Achievement("rich", "小富翁", "拥有 1000 金币", 
                   AchievementType.SPECIAL, 1000, 150),
    ]
    
    def __init__(self):
        self.achievements: Dict[str, Achievement] = {}
        self.total_exp_reward = 0
        self._init_achievements()
    
    def _init_achievements(self):
        """初始化成就"""
        for achievement in self.DEFAULT_ACHIEVEMENTS:
            self.achievements[achievement.id] = achievement
    
    def update_progress(self, achievement_id: str, current_value: int) -> Optional[Achievement]:
        """更新成就进度"""
        if achievement_id not in self.achievements:
            return None
        
        achievement = self.achievements[achievement_id]
        if achievement.check_unlock(current_value):
            self.total_exp_reward += achievement.reward_exp
            return achievement
        return None
    
    def get_unlocked_achievements(self) -> List[Achievement]:
        """获取已解锁的成就列表"""
        return [a for a in self.achievements.values() if a.unlocked]
    
    def get_locked_achievements(self) -> List[Achievement]:
        """获取未解锁的成就列表"""
        return [a for a in self.achievements.values() if not a.unlocked]
    
    def get_progress(self, achievement_type: Optional[AchievementType] = None) -> dict:
        """获取成就进度"""
        if achievement_type:
            achievements = [a for a in self.achievements.values() 
                          if a.achievement_type == achievement_type]
        else:
            achievements = list(self.achievements.values())
        
        total = len(achievements)
        unlocked = sum(1 for a in achievements if a.unlocked)
        
        return {
            "total": total,
            "unlocked": unlocked,
            "locked": total - unlocked,
            "percentage": (unlocked / total * 100) if total > 0 else 0
        }
    
    def to_dict(self) -> dict:
        """序列化"""
        return {
            "achievements": {k: v.to_dict() for k, v in self.achievements.items()},
            "total_exp_reward": self.total_exp_reward
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "AchievementSystem":
        """反序列化"""
        system = cls()
        system.achievements = {
            k: Achievement.from_dict(v) for k, v in data["achievements"].items()
        }
        system.total_exp_reward = data.get("total_exp_reward", 0)
        return system
    
    def display(self):
        """显示所有成就"""
        print("\n" + "=" * 50)
        print("🏆 成就系统")
        print("=" * 50)
        
        # 按类型分组显示
        for achievement_type in AchievementType:
            print(f"\n【{achievement_type.value}】")
            achievements = [a for a in self.achievements.values() 
                          if a.achievement_type == achievement_type]
            for achievement in achievements:
                print(f"  {achievement}")
        
        # 显示总进度
        progress = self.get_progress()
        print(f"\n📊 总进度：{progress['unlocked']}/{progress['total']} "
              f"({progress['percentage']:.1f}%)")
        print(f"⭐ 成就经验奖励：{self.total_exp_reward}")
        print("=" * 50)
