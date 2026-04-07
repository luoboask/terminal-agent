"""
随机事件系统 - 增加游戏趣味性
"""
import random
from datetime import datetime
from typing import Optional, Tuple, List
from enum import Enum


class EventType(Enum):
    """事件类型"""
    GOOD = "好事"
    BAD = "坏事"
    NEUTRAL = "普通"
    SPECIAL = "特殊"


class RandomEvent:
    """随机事件类"""
    
    def __init__(self, id: str, name: str, description: str, 
                 event_type: EventType,
                 effects: dict,
                 probability: float = 0.1):
        self.id = id
        self.name = name
        self.description = description
        self.event_type = event_type
        self.effects = effects  # 对宠物属性的影响
        self.probability = probability  # 发生概率
        self.triggered = False
        self.triggered_date: Optional[datetime] = None
    
    def trigger(self, pet) -> Tuple[bool, str]:
        """触发事件
        
        Args:
            pet: Pet 对象
            
        Returns:
            (是否成功触发，事件结果描述)
        """
        self.triggered = True
        self.triggered_date = datetime.now()
        
        messages = []
        
        # 应用效果
        for attr, value in self.effects.items():
            if hasattr(pet, attr):
                current_value = getattr(pet, attr)
                new_value = max(0, min(100, current_value + value))
                setattr(pet, attr, new_value)
                
                if value > 0:
                    messages.append(f"{attr}+{value}")
                elif value < 0:
                    messages.append(f"{attr}{value}")
        
        result_msg = f"🎲 {self.name}!\n{self.description}"
        if messages:
            result_msg += f"\n效果：{', '.join(messages)}"
        
        return True, result_msg
    
    def to_dict(self) -> dict:
        """序列化为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.event_type.name,
            "effects": self.effects,
            "probability": self.probability,
            "triggered": self.triggered,
            "triggered_date": self.triggered_date.isoformat() if self.triggered_date else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "RandomEvent":
        """从字典反序列化"""
        event = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            event_type=EventType[data["type"]],
            effects=data["effects"],
            probability=data.get("probability", 0.1)
        )
        event.triggered = data.get("triggered", False)
        if data.get("triggered_date"):
            event.triggered_date = datetime.fromisoformat(data["triggered_date"])
        return event


class EventSystem:
    """随机事件系统管理器"""
    
    # 预定义事件列表
    DEFAULT_EVENTS = [
        # 好事
        RandomEvent("find_treasure", "发现宝藏", 
                   "你的宠物在院子里发现了一个宝箱！",
                   EventType.GOOD,
                   {"happiness": 20, "energy": 10},
                   0.05),
        
        RandomEvent("gift_from_neighbor", "邻居送礼",
                   "邻居看到你可爱的宠物，送了一些零食",
                   EventType.GOOD,
                   {"hunger": 15, "happiness": 10},
                   0.08),
        
        RandomEvent("beautiful_weather", "晴朗天气",
                   "今天阳光明媚，宠物心情很好",
                   EventType.GOOD,
                   {"happiness": 15, "energy": 5},
                   0.1),
        
        RandomEvent("lucky_day", "幸运日",
                   "今天是宠物的幸运日！",
                   EventType.GOOD,
                   {"health": 10, "happiness": 20},
                   0.03),
        
        RandomEvent("unexpected_friend", "意外之友",
                   "一只流浪动物想和你的宠物做朋友",
                   EventType.GOOD,
                   {"happiness": 25},
                   0.04),
        
        # 坏事
        RandomEvent("caught_cold", "感冒了",
                   "宠物不小心着凉感冒了",
                   EventType.BAD,
                   {"health": -15, "energy": -10},
                   0.05),
        
        RandomEvent("lost_toy", "玩具丢失",
                   "宠物最喜欢的玩具找不到了",
                   EventType.BAD,
                   {"happiness": -20},
                   0.06),
        
        RandomEvent("bad_food", "食物变质",
                   "宠物不小心吃了变质的食物",
                   EventType.BAD,
                   {"health": -20, "hunger": -10},
                   0.03),
        
        RandomEvent("thunder_storm", "雷雨天气",
                   "雷雨天气让宠物感到害怕",
                   EventType.BAD,
                   {"happiness": -15, "energy": -5},
                   0.04),
        
        RandomEvent("dirty_mess", "弄脏了",
                   "宠物在外面玩得满身是泥",
                   EventType.BAD,
                   {"cleanliness": -30, "happiness": -5},
                   0.07),
        
        # 中性事件
        RandomEvent("lazy_day", "慵懒的一天",
                   "宠物今天特别懒，什么都不想做",
                   EventType.NEUTRAL,
                   {"energy": 10, "hunger": -5},
                   0.08),
        
        RandomEvent("curious_mood", "好奇心爆发",
                   "宠物对周围的一切都充满好奇",
                   EventType.NEUTRAL,
                   {"energy": -10, "happiness": 5},
                   0.07),
        
        RandomEvent("appetite_increase", "食欲大增",
                   "宠物今天特别能吃",
                   EventType.NEUTRAL,
                   {"hunger": -15, "health": 5},
                   0.06),
        
        RandomEvent("playful_mood", "玩耍兴致",
                   "宠物精力充沛，想玩耍",
                   EventType.NEUTRAL,
                   {"energy": -5, "happiness": 10},
                   0.08),
        
        # 特殊事件
        RandomEvent("rare_encounter", "稀有遭遇",
                   "宠物遇到了一只稀有的动物朋友！",
                   EventType.SPECIAL,
                   {"happiness": 30, "health": 10, "exp": 50},
                   0.01),
        
        RandomEvent("mysterious_gift", "神秘礼物",
                   "一个神秘人留下了礼物",
                   EventType.SPECIAL,
                   {"hunger": 30, "happiness": 30, "health": 20},
                   0.02),
        
        RandomEvent("power_awakening", "潜能觉醒",
                   "宠物的潜能突然觉醒！",
                   EventType.SPECIAL,
                   {"health": 25, "energy": 25, "exp": 100},
                   0.005),
        
        RandomEvent("ancient_blessing", "古老祝福",
                   "宠物获得了古老的祝福",
                   EventType.SPECIAL,
                   {"health": 50, "happiness": 50},
                   0.003),
    ]
    
    def __init__(self):
        self.events: dict[str, RandomEvent] = {}
        self.triggered_events: List[RandomEvent] = []
        self.event_count = 0
        self._init_events()
    
    def _init_events(self):
        """初始化事件"""
        for event in self.DEFAULT_EVENTS:
            self.events[event.id] = event
    
    def check_random_event(self, pet) -> Optional[Tuple[RandomEvent, str]]:
        """检查是否触发随机事件
        
        Args:
            pet: Pet 对象
            
        Returns:
            (触发的事件，事件描述) 或 None
        """
        # 30% 的概率触发事件
        if random.random() > 0.3:
            return None
        
        # 根据宠物状态筛选合适的事件
        available_events = []
        
        for event in self.events.values():
            # 坏事在宠物状态好时概率降低
            if event.event_type == EventType.BAD:
                if pet.health < 50 or pet.happiness < 50:
                    weight = event.probability * 0.5
                else:
                    weight = event.probability
            # 好事在宠物状态差时概率降低
            elif event.event_type == EventType.GOOD:
                if pet.health < 30 or pet.happiness < 30:
                    weight = event.probability * 1.5
                else:
                    weight = event.probability
            else:
                weight = event.probability
            
            available_events.append((event, weight))
        
        if not available_events:
            return None
        
        # 根据权重选择事件
        total_weight = sum(w for _, w in available_events)
        if total_weight == 0:
            return None
        
        rand = random.random() * total_weight
        cumulative = 0
        
        for event, weight in available_events:
            cumulative += weight
            if rand <= cumulative:
                # 触发事件
                success, message = event.trigger(pet)
                if success:
                    self.triggered_events.append(event)
                    self.event_count += 1
                    return (event, message)
                break
        
        return None
    
    def get_triggered_events(self) -> List[RandomEvent]:
        """获取已触发的事件列表"""
        return self.triggered_events
    
    def get_event_statistics(self) -> dict:
        """获取事件统计"""
        stats = {
            "total": self.event_count,
            "by_type": {}
        }
        
        for event_type in EventType:
            count = sum(1 for e in self.triggered_events 
                       if e.event_type == event_type)
            stats["by_type"][event_type.name] = count
        
        return stats
    
    def to_dict(self) -> dict:
        """序列化"""
        return {
            "events": {k: v.to_dict() for k, v in self.events.items()},
            "triggered_events": [e.id for e in self.triggered_events],
            "event_count": self.event_count
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "EventSystem":
        """反序列化"""
        system = cls()
        
        # 恢复事件状态
        if "events" in data:
            for event_id, event_data in data["events"].items():
                if event_id in system.events:
                    event = system.events[event_id]
                    event.triggered = event_data.get("triggered", False)
                    if event_data.get("triggered_date"):
                        event.triggered_date = datetime.fromisoformat(
                            event_data["triggered_date"])
        
        system.event_count = data.get("event_count", 0)
        
        return system
    
    def display(self):
        """显示事件统计"""
        print("\n" + "=" * 50)
        print("🎲 随机事件统计")
        print("=" * 50)
        
        stats = self.get_event_statistics()
        print(f"总触发次数：{stats['total']}")
        print("\n按类型统计:")
        for event_type, count in stats["by_type"].items():
            emoji = {"GOOD": "✨", "BAD": "⚠️", "NEUTRAL": "➖", "SPECIAL": "🌟"}
            print(f"  {emoji.get(event_type, '')} {event_type}: {count}次")
        
        if self.triggered_events:
            print("\n最近触发的事件:")
            for event in self.triggered_events[-5:]:
                status = "✅" if event.triggered else "⏳"
                print(f"  {status} {event.name}")
        
        print("=" * 50)


# 便捷函数
def generate_daily_event(pet) -> Optional[str]:
    """生成每日特殊事件
    
    Args:
        pet: Pet 对象
        
    Returns:
        事件描述或 None
    """
    event_system = EventSystem()
    
    # 每日事件必定触发
    special_events = [e for e in event_system.events.values() 
                     if e.event_type == EventType.SPECIAL]
    
    if special_events and random.random() < 0.1:  # 10% 概率触发特殊事件
        event = random.choice(special_events)
        _, message = event.trigger(pet)
        return message
    
    return None
