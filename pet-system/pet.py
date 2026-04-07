"""
宠物类 - 核心宠物逻辑
"""
import random
from datetime import datetime
from enum import Enum


class PetType(Enum):
    """宠物类型"""
    DOG = "狗狗"
    CAT = "猫咪"
    BIRD = "小鸟"
    FISH = "小鱼"
    RABBIT = "兔子"


class PetMood(Enum):
    """宠物心情状态"""
    HAPPY = "开心"
    NORMAL = "普通"
    SAD = "难过"
    ANGRY = "生气"
    SLEEPY = "困倦"


class Pet:
    """宠物类"""
    
    def __init__(self, name: str, pet_type: PetType = PetType.DOG):
        self.name = name
        self.pet_type = pet_type
        self.level = 1
        self.exp = 0
        self.exp_to_next = 100
        self.exp_to_next_level = 100  # 别名，兼容 main.py
        
        # 基础属性 (0-100)
        self.hunger = 50  # 饥饿度 (越低越饿)
        self.happiness = 70  # 心情值
        self.health = 100  # 健康值
        self.energy = 80  # 精力值
        self.cleanliness = 80  # 清洁度
        
        # 状态
        self.mood = PetMood.NORMAL
        self.is_sleeping = False
        self.is_alive = True
        
        # 统计
        self.birth_date = datetime.now()
        self.total_interactions = 0
        self.favorite_food = None
        
        # 外观
        self.appearance = self._get_initial_appearance()
        self._age = 0  # 年龄（天数）
        
    @property
    def age(self) -> int:
        """获取宠物年龄（天数）"""
        return self._age
    
    @property
    def growth_stage(self) -> str:
        """获取成长阶段"""
        if self.level < 5:
            return "幼年期"
        elif self.level < 10:
            return "成长期"
        elif self.level < 15:
            return "成熟期"
        else:
            return "完全体"
        
    def _get_initial_appearance(self) -> dict:
        """获取初始外观"""
        return {
            "size": "小",
            "color": "棕色",
            "accessory": None
        }
    
    def _update_mood(self):
        """根据属性更新心情状态"""
        if self.health < 30:
            self.mood = PetMood.SAD
        elif self.hunger < 30:
            self.mood = PetMood.ANGRY
        elif self.energy < 20:
            self.mood = PetMood.SLEEPY
        elif self.happiness > 80 and self.health > 80:
            self.mood = PetMood.HAPPY
        else:
            self.mood = PetMood.NORMAL
    
    def _check_evolution(self):
        """检查是否可以进化"""
        if self.level >= 5 and self.appearance["size"] == "小":
            self.appearance["size"] = "中"
            return True, "宠物成长到了中等体型！"
        elif self.level >= 10 and self.appearance["size"] == "中":
            self.appearance["size"] = "大"
            return True, "宠物成长到了大型体型！"
        return False, ""
    
    def feed(self, food_type: str = "普通粮食"):
        """喂食"""
        if self.is_sleeping:
            return False, "宠物正在睡觉，不能喂食..."
        
        self.total_interactions += 1
        food_values = {
            "普通粮食": {"hunger": 20, "health": 2, "exp": 5},
            "美味零食": {"hunger": 15, "happiness": 10, "exp": 8},
            "营养大餐": {"hunger": 30, "health": 5, "exp": 10},
            "过期食物": {"hunger": 10, "health": -10, "exp": 2}
        }
        
        values = food_values.get(food_type, food_values["普通粮食"])
        
        # 应用效果
        self.hunger = min(100, self.hunger + values["hunger"])
        if "health" in values:
            self.health = max(0, min(100, self.health + values["health"]))
        if "happiness" in values:
            self.happiness = max(0, min(100, self.happiness + values["happiness"]))
        
        self.gain_exp(values["exp"])
        self._update_mood()
        
        message = f"喂食{food_type}成功！"
        if food_type == "过期食物" and values["health"] < 0:
            message += " 宠物看起来不太舒服..."
        
        return True, message
    
    def play(self, toy_type: str = "球"):
        """玩耍"""
        if self.is_sleeping:
            return False, "宠物正在睡觉，不能玩耍..."
        
        if self.energy < 20:
            return False, "宠物太累了，需要休息..."
        
        self.total_interactions += 1
        
        toy_effects = {
            "球": {"happiness": 15, "energy": -10, "exp": 8},
            "飞盘": {"happiness": 20, "energy": -15, "exp": 10},
            "逗猫棒": {"happiness": 18, "energy": -12, "exp": 9},
            "积木": {"happiness": 12, "energy": -8, "exp": 6}
        }
        
        effects = toy_effects.get(toy_type, toy_effects["球"])
        
        self.happiness = min(100, self.happiness + effects["happiness"])
        self.energy = max(0, self.energy + effects["energy"])
        self.hunger = max(0, self.hunger - 5)  # 玩耍会消耗饥饿度
        
        self.gain_exp(effects["exp"])
        self._update_mood()
        
        return True, f"和{toy_type}玩耍很开心！心情提升了~"
    
    def train(self, skill: str = "握手"):
        """训练"""
        if self.is_sleeping:
            return False, "宠物正在睡觉，不能训练..."
        
        if self.energy < 30:
            return False, "宠物精力不足，需要休息..."
        
        self.total_interactions += 1
        self.energy = max(0, self.energy - 20)
        self.hunger = max(0, self.hunger - 10)
        
        # 训练成功率与心情和健康有关
        success_rate = (self.happiness + self.health) / 2
        success = random.randint(1, 100) <= success_rate
        
        if success:
            exp_gain = 15
            self.gain_exp(exp_gain)
            return True, f"训练成功！宠物学会了{skill}，获得{exp_gain}经验！"
        else:
            exp_gain = 5
            self.gain_exp(exp_gain)
            return True, f"训练失败... 但宠物还是获得了{exp_gain}经验值"
    
    def rest(self, hours: int = 1):
        """休息/睡觉
        
        Args:
            hours: 休息的小时数，默认 1 小时
        """
        if self.is_sleeping:
            # 继续睡觉
            recover_energy = hours * 10
            self.energy = min(100, self.energy + recover_energy)
            if self.energy >= 100:
                self.wake_up()
                return True, f"宠物休息了{hours}小时，精力完全恢复了！"
            return True, f"宠物继续睡觉... 精力恢复中 ({self.energy}%)"
        
        # 开始休息
        self.is_sleeping = True
        recover_energy = hours * 10
        self.energy = min(100, self.energy + recover_energy)
        self._update_mood()
        
        if self.energy >= 100:
            self.wake_up()
            return True, f"宠物休息了{hours}小时，精力完全恢复了！"
        return True, f"宠物开始休息，{hours}小时后精力恢复到{self.energy}%"
    
    def wake_up(self):
        """醒来"""
        if not self.is_sleeping:
            return False, "宠物没有睡觉..."
        
        self.is_sleeping = False
        self._update_mood()
        return True, "宠物醒来了！"
    
    def clean(self):
        """清洁"""
        self.total_interactions += 1
        self.cleanliness = 100
        self.happiness = min(100, self.happiness + 5)
        self.health = min(100, self.health + 2)
        self._update_mood()
        return True, "宠物变得干净了！"
    
    def heal(self):
        """治疗"""
        if self.health >= 100:
            return False, "宠物很健康，不需要治疗！"
        
        self.total_interactions += 1
        heal_amount = 20
        self.health = min(100, self.health + heal_amount)
        self.happiness = max(0, self.happiness - 5)  # 治疗可能会有点不舒服
        self._update_mood()
        return True, f"治疗成功！健康值恢复了 {heal_amount} 点"
    
    def gain_exp(self, amount: int):
        """获得经验值"""
        self.exp += amount
        
        while self.exp >= self.exp_to_next:
            self.level_up()
    
    def level_up(self):
        """升级"""
        self.exp -= self.exp_to_next
        self.level += 1
        self.exp_to_next = int(self.exp_to_next * 1.5)
        
        # 升级奖励
        self.health = min(100, self.health + 10)
        self.energy = min(100, self.energy + 10)
    
    def pass_time(self, hours: int = 1):
        """时间流逝效果"""
        if self.is_sleeping and hours <= 8:
            # 睡觉时恢复精力
            self.energy = min(100, self.energy + hours * 10)
            if hours >= 8:
                self.wake_up()
        else:
            # 正常时间流逝
            self.hunger = max(0, self.hunger - hours * 5)
            self.energy = max(0, self.energy - hours * 3)
            self.cleanliness = max(0, self.cleanliness - hours * 2)
            
            # 饥饿或脏乱会影响健康
            if self.hunger < 20:
                self.health = max(0, self.health - hours * 2)
            if self.cleanliness < 30:
                self.health = max(0, self.health - hours)
        
        self._update_mood()
        
        # 检查生命状态
        if self.health <= 0:
            self.is_alive = False
            return False, "宠物已经离开了..."
        
        return True, "时间流逝..."
    
    def get_status(self) -> dict:
        """获取宠物状态"""
        return {
            "name": self.name,
            "type": self.pet_type.value,
            "level": self.level,
            "exp": f"{self.exp}/{self.exp_to_next}",
            "hunger": self.hunger,
            "happiness": self.happiness,
            "health": self.health,
            "energy": self.energy,
            "cleanliness": self.cleanliness,
            "mood": self.mood.value,
            "is_sleeping": self.is_sleeping,
            "is_alive": self.is_alive,
            "appearance": self.appearance,
            "age_days": (datetime.now() - self.birth_date).days,
            "interactions": self.total_interactions
        }
    
    def to_dict(self) -> dict:
        """序列化为字典"""
        return {
            "name": self.name,
            "pet_type": self.pet_type.name,
            "level": self.level,
            "exp": self.exp,
            "exp_to_next": self.exp_to_next,
            "hunger": self.hunger,
            "happiness": self.happiness,
            "health": self.health,
            "energy": self.energy,
            "cleanliness": self.cleanliness,
            "mood": self.mood.name,
            "is_sleeping": self.is_sleeping,
            "is_alive": self.is_alive,
            "birth_date": self.birth_date.isoformat(),
            "total_interactions": self.total_interactions,
            "appearance": self.appearance
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Pet":
        """从字典反序列化"""
        pet = cls(data["name"], PetType[data["pet_type"]])
        pet.level = data["level"]
        pet.exp = data["exp"]
        pet.exp_to_next = data["exp_to_next"]
        pet.hunger = data["hunger"]
        pet.happiness = data["happiness"]
        pet.health = data["health"]
        pet.energy = data["energy"]
        pet.cleanliness = data["cleanliness"]
        pet.mood = PetMood[data["mood"]]
        pet.is_sleeping = data["is_sleeping"]
        pet.is_alive = data["is_alive"]
        pet.birth_date = datetime.fromisoformat(data["birth_date"])
        pet.total_interactions = data["total_interactions"]
        pet.appearance = data["appearance"]
        return pet
    
    def __str__(self):
        """字符串表示"""
        status = self.get_status()
        bars = {
            "饥饿": "█" * (status["hunger"] // 10),
            "心情": "█" * (status["happiness"] // 10),
            "健康": "█" * (status["health"] // 10),
            "精力": "█" * (status["energy"] // 10)
        }
        
        return f"""
╔═══════════════════════════════════════╗
║  🐾 {status['name']} ({status['type']})  Lv.{status['level']}
╠═══════════════════════════════════════╣
║  经验：{status['exp']}
║  心情：{status['mood']}
║  状态：{'💤 睡觉中' if status['is_sleeping'] else '🌟 清醒'}
╠═══════════════════════════════════════╣
║  饥饿：[{bars['饥饿']}] {status['hunger']}%
║  心情：[{bars['心情']}] {status['happiness']}%
║  健康：[{bars['健康']}] {status['health']}%
║  精力：[{bars['精力']}] {status['energy']}%
╠═══════════════════════════════════════╣
║  体型：{status['appearance']['size']}
║  年龄：{status['age_days']} 天
║  互动：{status['interactions']} 次
╚═══════════════════════════════════════╝
"""
