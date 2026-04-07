"""
天气系统 - 影响宠物状态和事件
"""
import random
from enum import Enum
from datetime import datetime
from typing import Optional, Dict, List


class WeatherType(Enum):
    """天气类型"""
    SUNNY = "晴天"
    CLOUDY = "多云"
    RAINY = "雨天"
    SNOWY = "雪天"
    STORMY = "暴风雨"
    FOGGY = "雾天"
    WINDY = "大风"


class Weather:
    """天气类"""
    
    # 天气效果配置
    WEATHER_EFFECTS = {
        WeatherType.SUNNY: {
            "happiness": 5,
            "energy": 5,
            "outdoor_activity_bonus": 1.2,
            "description": "阳光明媚，宠物心情愉悦！"
        },
        WeatherType.CLOUDY: {
            "happiness": 0,
            "energy": 0,
            "outdoor_activity_bonus": 1.0,
            "description": "云层较厚，适合室内活动。"
        },
        WeatherType.RAINY: {
            "happiness": -5,
            "energy": -5,
            "outdoor_activity_bonus": 0.5,
            "description": "下雨了，宠物不太想出门。"
        },
        WeatherType.SNOWY: {
            "happiness": 10,
            "energy": -10,
            "outdoor_activity_bonus": 0.8,
            "description": "下雪了，宠物很兴奋但容易冷！"
        },
        WeatherType.STORMY: {
            "happiness": -15,
            "energy": -10,
            "outdoor_activity_bonus": 0.0,
            "description": "暴风雨！宠物很害怕，只能待在室内。"
        },
        WeatherType.FOGGY: {
            "happiness": -3,
            "energy": 0,
            "outdoor_activity_bonus": 0.6,
            "description": "大雾弥漫，视线不佳。"
        },
        WeatherType.WINDY: {
            "happiness": 0,
            "energy": -5,
            "outdoor_activity_bonus": 0.7,
            "description": "大风天气，外出要注意安全。"
        }
    }
    
    def __init__(self):
        self.current_weather = WeatherType.SUNNY
        self.weather_duration = 0  # 剩余持续时间（小时）
        self.last_change = datetime.now()
        self.weather_history: List[WeatherType] = []
    
    def change_weather(self, weather_type: Optional[WeatherType] = None):
        """改变天气"""
        if weather_type is None:
            # 随机选择天气，晴天概率更高
            weights = [0.35, 0.2, 0.15, 0.1, 0.05, 0.1, 0.05]
            weather_type = random.choices(list(WeatherType), weights=weights)[0]
        
        self.weather_history.append(self.current_weather)
        self.current_weather = weather_type
        self.weather_duration = random.randint(2, 6)  # 持续 2-6 小时
        self.last_change = datetime.now()
        
        effect = self.WEATHER_EFFECTS[weather_type]
        return f"🌤️ 天气变为：{weather_type.value}\n{effect['description']}"
    
    def apply_weather_effect(self, pet) -> Dict[str, int]:
        """应用天气效果到宠物"""
        effect = self.WEATHER_EFFECTS[self.current_weather]
        changes = {}
        
        if "happiness" in effect:
            old_val = pet.happiness
            pet.happiness = max(0, min(100, pet.happiness + effect["happiness"]))
            changes["happiness"] = pet.happiness - old_val
            
        if "energy" in effect:
            old_val = pet.energy
            pet.energy = max(0, min(100, pet.energy + effect["energy"]))
            changes["energy"] = pet.energy - old_val
        
        return changes
    
    def get_outdoor_bonus(self) -> float:
        """获取户外活动加成"""
        return self.WEATHER_EFFECTS[self.current_weather]["outdoor_activity_bonus"]
    
    def can_go_outdoor(self) -> bool:
        """判断是否可以户外活动"""
        return self.current_weather != WeatherType.STORMY
    
    def to_dict(self) -> dict:
        """序列化"""
        return {
            "current_weather": self.current_weather.name,
            "weather_duration": self.weather_duration,
            "last_change": self.last_change.isoformat(),
            "weather_history": [w.name for w in self.weather_history[-10:]]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Weather":
        """反序列化"""
        weather = cls()
        weather.current_weather = WeatherType[data["current_weather"]]
        weather.weather_duration = data.get("weather_duration", 0)
        if data.get("last_change"):
            weather.last_change = datetime.fromisoformat(data["last_change"])
        weather.weather_history = [WeatherType[name] for name in data.get("weather_history", [])]
        return weather
    
    def __str__(self):
        icons = {
            WeatherType.SUNNY: "☀️",
            WeatherType.CLOUDY: "☁️",
            WeatherType.RAINY: "🌧️",
            WeatherType.SNOWY: "❄️",
            WeatherType.STORMY: "⛈️",
            WeatherType.FOGGY: "🌫️",
            WeatherType.WINDY: "💨"
        }
        icon = icons.get(self.current_weather, "🌤️")
        return f"{icon} {self.current_weather.value}"


class WeatherSystem:
    """天气系统管理器"""
    
    def __init__(self):
        self.weather = Weather()
        self.weather_change_interval = 4  # 每 4 小时变化一次
    
    def update(self, game_hours: int):
        """更新天气（根据游戏时间）"""
        self.weather.weather_duration -= 1
        if self.weather.weather_duration <= 0:
            self.weather.change_weather()
    
    def get_weather_display(self) -> str:
        """获取天气显示字符串"""
        return str(self.weather)
    
    def get_weather_effect_info(self) -> str:
        """获取天气效果信息"""
        effect = Weather.WEATHER_EFFECTS[self.weather.current_weather]
        lines = [f"当前天气：{self.weather.current_weather.value}"]
        lines.append(effect["description"])
        
        if effect["happiness"] != 0:
            sign = "+" if effect["happiness"] > 0 else ""
            lines.append(f"心情影响：{sign}{effect['happiness']}")
        if effect["energy"] != 0:
            sign = "+" if effect["energy"] > 0 else ""
            lines.append(f"精力影响：{sign}{effect['energy']}")
        
        return "\n".join(lines)
