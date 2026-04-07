"""
装饰系统 - 宠物外观和房间装饰
"""
from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime


class DecorationType(Enum):
    """装饰类型"""
    HAT = "帽子"
    NECKLACE = "项链"
    CLOTHES = "衣服"
    SHOES = "鞋子"
    BACK = "背部装饰"
    FACE = "面部装饰"


class Color(Enum):
    """颜色枚举"""
    RED = "红色"
    BLUE = "蓝色"
    GREEN = "绿色"
    YELLOW = "黄色"
    PURPLE = "紫色"
    PINK = "粉色"
    BLACK = "黑色"
    WHITE = "白色"
    ORANGE = "橙色"
    BROWN = "棕色"
    GOLD = "金色"
    SILVER = "银色"


class Decoration:
    """单个装饰品"""
    
    def __init__(self, id: str, name: str, description: str,
                 decoration_type: DecorationType,
                 price: int = 0,
                 effects: Optional[Dict[str, int]] = None,
                 rarity: str = "common"):
        self.id = id
        self.name = name
        self.description = description
        self.decoration_type = decoration_type
        self.price = price
        self.effects = effects or {}  # 属性加成
        self.rarity = rarity  # common, rare, epic, legendary
        self.owned = False
        self.equip_time: Optional[datetime] = None
    
    @property
    def rarity_color(self) -> str:
        """获取稀有度颜色"""
        colors = {
            "common": "⚪",
            "rare": "🔵",
            "epic": "🟣",
            "legendary": "🟡"
        }
        return colors.get(self.rarity, "⚪")
    
    def to_dict(self) -> dict:
        """序列化"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.decoration_type.name,
            "price": self.price,
            "effects": self.effects,
            "rarity": self.rarity,
            "owned": self.owned,
            "equip_time": self.equip_time.isoformat() if self.equip_time else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Decoration":
        """反序列化"""
        dec = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            decoration_type=DecorationType[data["type"]],
            price=data.get("price", 0),
            effects=data.get("effects", {}),
            rarity=data.get("rarity", "common")
        )
        dec.owned = data.get("owned", False)
        if data.get("equip_time"):
            dec.equip_time = datetime.fromisoformat(data["equip_time"])
        return dec
    
    def __str__(self):
        return f"{self.rarity_color} {self.name} ({self.decoration_type.value})"


class DecorationSystem:
    """装饰系统管理器"""
    
    # 预定义装饰品
    DEFAULT_DECORATIONS = [
        # 帽子类
        Decoration("hat_cap", "棒球帽", "普通的棒球帽", DecorationType.HAT, 100, 
                  {"happiness": 2}, "common"),
        Decoration("hat_crown", "小王冠", "精致的小王冠", DecorationType.HAT, 500,
                  {"happiness": 5, "exp_bonus": 0.1}, "rare"),
        Decoration("hat_wizard", "魔法帽", "神秘的魔法帽", DecorationType.HAT, 1000,
                  {"happiness": 8, "exp_bonus": 0.15}, "epic"),
        Decoration("hat_golden", "黄金头冠", "闪耀的黄金头冠", DecorationType.HAT, 5000,
                  {"happiness": 15, "exp_bonus": 0.2, "health_bonus": 5}, "legendary"),
        
        # 项链类
        Decoration("neck_collar", "普通项圈", "基础的宠物项圈", DecorationType.NECKLACE, 50,
                  {}, "common"),
        Decoration("neck_bell", "铃铛项圈", "会发出清脆声音的铃铛", DecorationType.NECKLACE, 150,
                  {"happiness": 3}, "common"),
        Decoration("neck_diamond", "钻石项链", "闪耀的钻石项链", DecorationType.NECKLACE, 2000,
                  {"happiness": 10, "exp_bonus": 0.1}, "epic"),
        
        # 衣服类
        Decoration("cloth_tshirt", "T 恤衫", "简单的 T 恤", DecorationType.CLOTHES, 80,
                  {}, "common"),
        Decoration("cloth_sweater", "毛衣", "温暖的毛衣", DecorationType.CLOTHES, 200,
                  {"health": 2}, "common"),
        Decoration("cloth_armor", "小盔甲", "帅气的盔甲", DecorationType.CLOTHES, 800,
                  {"health": 10, "happiness": 5}, "rare"),
        Decoration("cloth_robe", "魔法长袍", "蕴含魔力的长袍", DecorationType.CLOTHES, 3000,
                  {"health": 15, "exp_bonus": 0.15}, "legendary"),
        
        # 背部装饰
        Decoration("back_wings", "小翅膀", "可爱的天使翅膀", DecorationType.BACK, 300,
                  {"happiness": 5, "energy": 5}, "rare"),
        Decoration("back_cape", "英雄披风", "飘扬的英雄披风", DecorationType.BACK, 600,
                  {"happiness": 8, "health": 5}, "epic"),
        Decoration("back_jetpack", "小火箭", "迷你火箭背包", DecorationType.BACK, 1500,
                  {"energy": 15, "exp_bonus": 0.1}, "epic"),
        
        # 面部装饰
        Decoration("face_glasses", "小眼镜", "学者风的眼镜", DecorationType.FACE, 120,
                  {"exp_bonus": 0.05}, "common"),
        Decoration("face_mask", "超级英雄面具", "酷酷的面具", DecorationType.FACE, 250,
                  {"happiness": 5}, "rare"),
        Decoration("face_monocle", "单片眼镜", "绅士的象征", DecorationType.FACE, 400,
                  {"exp_bonus": 0.1, "happiness": 3}, "epic"),
    ]
    
    def __init__(self):
        self.decorations: Dict[str, Decoration] = {}
        self.equipped: Dict[DecorationType, str] = {}  # type -> decoration_id
        self.coins = 500  # 初始金币
        self._init_decorations()
    
    def _init_decorations(self):
        """初始化装饰品"""
        for dec in self.DEFAULT_DECORATIONS:
            self.decorations[dec.id] = dec
    
    def buy(self, decoration_id: str) -> tuple:
        """购买装饰品"""
        if decoration_id not in self.decorations:
            return False, "该装饰品不存在！"
        
        dec = self.decorations[decoration_id]
        if dec.owned:
            return False, "你已经拥有这个装饰品了！"
        
        if self.coins < dec.price:
            return False, f"金币不足！需要 {dec.price} 金币，你只有 {self.coins} 金币"
        
        self.coins -= dec.price
        dec.owned = True
        return True, f"成功购买 {dec.name}！花费 {dec.price} 金币"
    
    def equip(self, decoration_id: str) -> tuple:
        """装备装饰品"""
        if decoration_id not in self.decorations:
            return False, "该装饰品不存在！"
        
        dec = self.decorations[decoration_id]
        if not dec.owned:
            return False, "你还没有拥有这个装饰品！"
        
        # 卸下同类型的装饰品
        dec_type = dec.decoration_type
        if dec_type in self.equipped:
            old_id = self.equipped[dec_type]
            if old_id != decoration_id:
                self.decorations[old_id].equip_time = None
        
        # 装备新装饰品
        self.equipped[dec_type] = decoration_id
        dec.equip_time = datetime.now()
        return True, f"装备了 {dec.name}！"
    
    def unequip(self, decoration_type: DecorationType) -> tuple:
        """卸下装饰品"""
        if decoration_type not in self.equipped:
            return False, "该位置没有装备装饰品！"
        
        dec_id = self.equipped[decoration_type]
        dec = self.decorations[dec_id]
        dec.equip_time = None
        del self.equipped[decoration_type]
        return True, f"卸下了 {dec.name}"
    
    def get_effects(self) -> Dict[str, int]:
        """获取所有装备的总效果"""
        effects = {}
        for dec_type, dec_id in self.equipped.items():
            dec = self.decorations[dec_id]
            for stat, value in dec.effects.items():
                effects[stat] = effects.get(stat, 0) + value
        return effects
    
    def get_equipped_list(self) -> List[Decoration]:
        """获取已装备的装饰品列表"""
        return [self.decorations[dec_id] for dec_id in self.equipped.values() 
                if dec_id in self.decorations]
    
    def get_owned_list(self) -> List[Decoration]:
        """获取已拥有的装饰品列表"""
        return [dec for dec in self.decorations.values() if dec.owned]
    
    def get_available_list(self) -> List[Decoration]:
        """获取可购买的装饰品列表"""
        return [dec for dec in self.decorations.values() if not dec.owned]
    
    def earn_coins(self, amount: int):
        """获得金币"""
        self.coins += amount
    
    def spend_coins(self, amount: int) -> bool:
        """花费金币"""
        if self.coins >= amount:
            self.coins -= amount
            return True
        return False
    
    def to_dict(self) -> dict:
        """序列化"""
        return {
            "decorations": {k: v.to_dict() for k, v in self.decorations.items()},
            "equipped": {k.name: v for k, v in self.equipped.items()},
            "coins": self.coins
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "DecorationSystem":
        """反序列化"""
        system = cls()
        system.decorations = {
            k: Decoration.from_dict(v) for k, v in data["decorations"].items()
        }
        system.equipped = {
            DecorationType[k]: v for k, v in data.get("equipped", {}).items()
        }
        system.coins = data.get("coins", 500)
        return system
    
    def display_inventory(self):
        """显示装饰品背包"""
        print("\n" + "=" * 50)
        print("🎒 装饰品背包")
        print("=" * 50)
        print(f"💰 金币：{self.coins}")
        
        owned = self.get_owned_list()
        if not owned:
            print("\n你还没有任何装饰品！去商店看看吧～")
            return
        
        print(f"\n已拥有：{len(owned)} 件")
        for dec in owned:
            equipped = "✨ [装备中]" if dec.id in self.equipped.values() else ""
            print(f"  {dec} {equipped}")
        
        # 显示当前装备
        equipped = self.get_equipped_list()
        if equipped:
            print("\n📌 当前装备:")
            for dec in equipped:
                print(f"  {dec.decoration_type.value}: {dec.name}")
        print("=" * 50)
    
    def display_shop(self):
        """显示商店"""
        print("\n" + "=" * 50)
        print("🏪 装饰品商店")
        print("=" * 50)
        print(f"💰 你的金币：{self.coins}")
        
        available = self.get_available_list()
        if not available:
            print("\n🎉 恭喜！你已经购买了所有装饰品！")
            return
        
        # 按类型分组显示
        for dec_type in DecorationType:
            items = [d for d in available if d.decoration_type == dec_type]
            if items:
                print(f"\n【{dec_type.value}】")
                for dec in items:
                    print(f"  {dec.rarity_color} {dec.id}: {dec.name}")
                    print(f"      价格：{dec.price} 金币")
                    print(f"      效果：{dec.effects if dec.effects else '无'}")
                    print(f"      {dec.description}")
        
        print("=" * 50)


class PetAppearance:
    """宠物外观管理"""
    
    def __init__(self):
        self.size = "小"  # 小、中、大
        self.color = "棕色"
        self.pattern = "纯色"  # 纯色、条纹、斑点、渐变
        self.shiny = False  # 是否闪光
        self.accessories: List[str] = []  # 已装备的饰品 ID
    
    @property
    def display_name(self) -> str:
        """获取外观显示名称"""
        prefix = "✨ " if self.shiny else ""
        return f"{prefix}{self.color}{self.pattern}({self.size})"
    
    def evolve(self, new_size: str):
        """进化外观"""
        self.size = new_size
    
    def set_color(self, color: str):
        """设置颜色"""
        self.color = color
    
    def set_pattern(self, pattern: str):
        """设置花纹"""
        self.pattern = pattern
    
    def set_shiny(self, shiny: bool):
        """设置闪光"""
        self.shiny = shiny
    
    def add_accessory(self, accessory_id: str):
        """添加饰品"""
        if accessory_id not in self.accessories:
            self.accessories.append(accessory_id)
    
    def remove_accessory(self, accessory_id: str):
        """移除饰品"""
        if accessory_id in self.accessories:
            self.accessories.remove(accessory_id)
    
    def to_dict(self) -> dict:
        """序列化"""
        return {
            "size": self.size,
            "color": self.color,
            "pattern": self.pattern,
            "shiny": self.shiny,
            "accessories": self.accessories
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "PetAppearance":
        """反序列化"""
        app = cls()
        app.size = data.get("size", "小")
        app.color = data.get("color", "棕色")
        app.pattern = data.get("pattern", "纯色")
        app.shiny = data.get("shiny", False)
        app.accessories = data.get("accessories", [])
        return app
    
    def __str__(self):
        shiny_mark = "✨" if self.shiny else ""
        return f"{shiny_mark}{self.color}{self.pattern} {self.size}体型"
