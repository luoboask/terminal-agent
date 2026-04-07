"""
社交系统 - 宠物拜访、好友互动
"""
import random
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum


class RelationshipLevel(Enum):
    """关系等级"""
    STRANGER = "陌生"
    ACQUAINTANCE = "相识"
    FRIEND = "朋友"
    GOOD_FRIEND = "好友"
    BEST_FRIEND = "挚友"


class FriendPet:
    """好友宠物类"""
    
    def __init__(self, owner_name: str, pet_name: str, pet_type: str, level: int):
        self.owner_name = owner_name
        self.pet_name = pet_name
        self.pet_type = pet_type
        self.level = level
        self.relationship = RelationshipLevel.STRANGER
        self.friendship_points = 0
        self.last_visit = None
        self.total_visits = 0
        self.gifts_received = 0
        
    def to_dict(self) -> dict:
        return {
            "owner_name": self.owner_name,
            "pet_name": self.pet_name,
            "pet_type": self.pet_type,
            "level": self.level,
            "relationship": self.relationship.value,
            "friendship_points": self.friendship_points,
            "last_visit": self.last_visit.isoformat() if self.last_visit else None,
            "total_visits": self.total_visits,
            "gifts_received": self.gifts_received
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'FriendPet':
        friend = cls(
            data["owner_name"],
            data["pet_name"],
            data["pet_type"],
            data["level"]
        )
        friend.relationship = RelationshipLevel(data["relationship"])
        friend.friendship_points = data.get("friendship_points", 0)
        friend.last_visit = datetime.fromisoformat(data["last_visit"]) if data.get("last_visit") else None
        friend.total_visits = data.get("total_visits", 0)
        friend.gifts_received = data.get("gifts_received", 0)
        return friend
    
    def update_relationship(self):
        """根据友谊点数更新关系等级"""
        if self.friendship_points >= 1000:
            self.relationship = RelationshipLevel.BEST_FRIEND
        elif self.friendship_points >= 500:
            self.relationship = RelationshipLevel.GOOD_FRIEND
        elif self.friendship_points >= 200:
            self.relationship = RelationshipLevel.FRIEND
        elif self.friendship_points >= 50:
            self.relationship = RelationshipLevel.ACQUAINTANCE
        else:
            self.relationship = RelationshipLevel.STRANGER


class SocialSystem:
    """社交系统"""
    
    def __init__(self):
        self.friends: List[FriendPet] = []
        self.visit_log: List[dict] = []
        self.social_stats = {
            "total_visits": 0,
            "total_gifts_sent": 0,
            "total_gifts_received": 0,
            "friendships_made": 0
        }
        
    def add_friend(self, friend: FriendPet) -> bool:
        """添加好友"""
        # 检查是否已是好友
        for f in self.friends:
            if f.pet_name == friend.pet_name and f.owner_name == friend.owner_name:
                return False
        self.friends.append(friend)
        self.social_stats["friendships_made"] += 1
        return True
    
    def remove_friend(self, pet_name: str, owner_name: str) -> bool:
        """删除好友"""
        for i, friend in enumerate(self.friends):
            if friend.pet_name == pet_name and friend.owner_name == owner_name:
                self.friends.pop(i)
                return True
        return False
    
    def get_friend(self, pet_name: str) -> Optional[FriendPet]:
        """获取好友信息"""
        for friend in self.friends:
            if friend.pet_name == pet_name:
                return friend
        return None
    
    def visit_friend(self, friend: FriendPet) -> dict:
        """拜访好友"""
        result = {
            "success": True,
            "message": "",
            "rewards": {}
        }
        
        # 增加友谊点数
        points_gained = random.randint(5, 15)
        friend.friendship_points += points_gained
        friend.total_visits += 1
        friend.last_visit = datetime.now()
        friend.update_relationship()
        
        self.social_stats["total_visits"] += 1
        
        # 随机事件
        event_roll = random.random()
        if event_roll < 0.3:
            # 找到物品
            found_items = ["🍎 苹果", "🍪 饼干", "💰 金币", "🎁 礼物"]
            item = random.choice(found_items)
            result["message"] = f"拜访 {friend.owner_name} 的 {friend.pet_name} 时，意外发现了 {item}！"
            result["rewards"]["item"] = item
        elif event_roll < 0.5:
            # 获得金币
            coins = random.randint(10, 50)
            result["message"] = f"拜访 {friend.owner_name} 的 {friend.pet_name}，获得了 {coins} 金币！"
            result["rewards"]["coins"] = coins
        else:
            result["message"] = f"拜访了 {friend.owner_name} 的 {friend.pet_name}，友谊增加了 {points_gained} 点！"
        
        # 记录访问日志
        self.visit_log.append({
            "date": datetime.now().isoformat(),
            "friend": friend.pet_name,
            "owner": friend.owner_name,
            "points_gained": points_gained
        })
        
        return result
    
    def send_gift(self, friend: FriendPet, gift_name: str) -> dict:
        """赠送礼物"""
        result = {
            "success": True,
            "message": ""
        }
        
        # 增加友谊点数
        points_gained = random.randint(15, 30)
        friend.friendship_points += points_gained
        friend.gifts_received += 1
        friend.update_relationship()
        
        self.social_stats["total_gifts_sent"] += 1
        
        result["message"] = f"送给 {friend.owner_name} 的 {friend.pet_name} 一个 {gift_name}，友谊增加了 {points_gained} 点！"
        
        return result
    
    def play_with_friend(self, friend: FriendPet) -> dict:
        """与好友宠物玩耍"""
        result = {
            "success": True,
            "message": "",
            "rewards": {}
        }
        
        # 小游戏结果
        game_outcomes = [
            ("你们一起玩得很开心！", 20, 10),
            ("你的宠物赢了！", 25, 15),
            ("友谊赛平局！", 15, 10),
            ("虽然输了但很开心！", 10, 5)
        ]
        
        outcome = random.choice(game_outcomes)
        friendship_points = outcome[1]
        exp_reward = outcome[2]
        
        friend.friendship_points += friendship_points
        friend.update_relationship()
        
        result["message"] = outcome[0]
        result["rewards"]["exp"] = exp_reward
        result["rewards"]["friendship"] = friendship_points
        
        return result
    
    def get_friends_list(self) -> List[dict]:
        """获取好友列表"""
        return [friend.to_dict() for friend in self.friends]
    
    def get_statistics(self) -> dict:
        """获取社交统计"""
        return {
            **self.social_stats,
            "total_friends": len(self.friends),
            "best_friends": sum(1 for f in self.friends if f.relationship == RelationshipLevel.BEST_FRIEND),
            "good_friends": sum(1 for f in self.friends if f.relationship == RelationshipLevel.GOOD_FRIEND)
        }
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "friends": [f.to_dict() for f in self.friends],
            "visit_log": self.visit_log[-20:],  # 保留最近 20 条记录
            "social_stats": self.social_stats
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SocialSystem':
        """从字典加载"""
        social = cls()
        social.friends = [FriendPet.from_dict(f) for f in data.get("friends", [])]
        social.visit_log = data.get("visit_log", [])
        social.social_stats = data.get("social_stats", {
            "total_visits": 0,
            "total_gifts_sent": 0,
            "total_gifts_received": 0,
            "friendships_made": 0
        })
        return social


# 预设 NPC 宠物
NPC_PETS = [
    FriendPet("小明", "豆豆", "狗狗", 5),
    FriendPet("小红", "咪咪", "猫咪", 8),
    FriendPet("小刚", "小白", "兔子", 3),
    FriendPet("小丽", "花花", "小鸟", 12),
    FriendPet("小强", "阿黄", "狗狗", 15),
    FriendPet("小美", "雪球", "猫咪", 6),
    FriendPet("小杰", "团团", "兔子", 10),
    FriendPet("小芳", "啾啾", "小鸟", 4),
]


def generate_random_friend(player_level: int) -> FriendPet:
    """生成随机好友"""
    names = ["小明", "小红", "小刚", "小丽", "小强", "小美", "小杰", "小芳", "小伟", "小娜"]
    pet_names = ["豆豆", "咪咪", "小白", "花花", "阿黄", "雪球", "团团", "啾啾", "毛毛", "球球"]
    pet_types = ["狗狗", "猫咪", "兔子", "小鸟", "小鱼"]
    
    owner = random.choice(names)
    pet_name = random.choice(pet_names)
    pet_type = random.choice(pet_types)
    level = max(1, player_level + random.randint(-3, 3))
    
    return FriendPet(owner, pet_name, pet_type, level)
