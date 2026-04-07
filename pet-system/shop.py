"""
商店系统 - 宠物商店和物品管理
"""
import random
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass


class ItemType(Enum):
    """物品类型"""
    FOOD = "食物"
    TOY = "玩具"
    MEDICINE = "药品"
    DECORATION = "装饰"
    SPECIAL = "特殊"


@dataclass
class Item:
    """物品类"""
    id: str
    name: str
    description: str
    item_type: ItemType
    price: int
    effect: dict
    icon: str = "📦"
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.item_type.name,
            "price": self.price,
            "effect": self.effect,
            "icon": self.icon
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Item":
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            item_type=ItemType[data["type"]],
            price=data["price"],
            effect=data["effect"],
            icon=data.get("icon", "📦")
        )


class Shop:
    """宠物商店"""
    
    # 预定义商品列表
    DEFAULT_ITEMS = [
        # 食物类
        Item("food_normal", "普通粮食", "基础的宠物粮食，恢复少量饥饿", 
             ItemType.FOOD, 10, {"hunger": 20, "health": 2}, "🍖"),
        Item("food_premium", "营养大餐", "高品质的宠物食品，恢复大量饥饿和健康", 
             ItemType.FOOD, 25, {"hunger": 35, "health": 8}, "🍱"),
        Item("food_snack", "美味零食", "宠物喜欢的零食，提升心情", 
             ItemType.FOOD, 15, {"hunger": 10, "happiness": 15}, "🍪"),
        Item("food_treat", "豪华套餐", "顶级宠物美食，全方位提升", 
             ItemType.FOOD, 50, {"hunger": 50, "happiness": 20, "health": 10}, "🎂"),
        Item("food_bad", "过期食物", "已经过期的食物，小心食用...", 
             ItemType.FOOD, 5, {"hunger": 15, "health": -15}, "🥫"),
        
        # 玩具类
        Item("toy_ball", "弹力球", "经典的宠物玩具", 
             ItemType.TOY, 20, {"happiness": 15, "energy": -5, "exp": 5}, "⚽"),
        Item("toy_frisbee", "飞盘", "户外玩耍的好伙伴", 
             ItemType.TOY, 30, {"happiness": 25, "energy": -10, "exp": 8}, "🥏"),
        Item("toy_mouse", "玩具老鼠", "猫咪最爱的玩具", 
             ItemType.TOY, 25, {"happiness": 20, "energy": -8, "exp": 6}, "🐭"),
        Item("toy_bone", "骨头玩具", "狗狗的最爱", 
             ItemType.TOY, 25, {"happiness": 22, "energy": -8, "exp": 7}, "🦴"),
        Item("toy_puzzle", "益智玩具", "锻炼宠物的智力", 
             ItemType.TOY, 40, {"happiness": 18, "energy": -12, "exp": 15}, "🧩"),
        
        # 药品类
        Item("med_heal", "治疗药水", "恢复宠物健康", 
             ItemType.MEDICINE, 30, {"health": 30}, "💊"),
        Item("med_super", "超级药剂", "强力恢复健康", 
             ItemType.MEDICINE, 60, {"health": 60}, "💉"),
        Item("med_energy", "能量饮料", "恢复宠物精力", 
             ItemType.MEDICINE, 25, {"energy": 40}, "⚡"),
        Item("med_vitamin", "维生素", "提升宠物体质", 
             ItemType.MEDICINE, 35, {"health": 15, "exp": 10}, "💊"),
        
        # 装饰类
        Item("dec_collar", "可爱项圈", "给宠物戴上漂亮的项圈", 
             ItemType.DECORATION, 50, {"accessory": "项圈"}, "🎀"),
        Item("dec_hat", "时尚帽子", "让宠物更时尚", 
             ItemType.DECORATION, 80, {"accessory": "帽子"}, "🎩"),
        Item("dec_glasses", "酷酷眼镜", "增加宠物的魅力", 
             ItemType.DECORATION, 60, {"accessory": "眼镜"}, "👓"),
        Item("dec_bow", "蝴蝶结", "可爱的蝴蝶结装饰", 
             ItemType.DECORATION, 45, {"accessory": "蝴蝶结"}, "🎗️"),
        Item("dec_crown", "王者之冠", "尊贵的象征", 
             ItemType.DECORATION, 200, {"accessory": "王冠", "happiness": 30}, "👑"),
        
        # 特殊类
        Item("special_xp", "经验药水", "直接获得经验值", 
             ItemType.SPECIAL, 100, {"exp": 50}, "✨"),
        Item("special_luck", "幸运符", "增加幸运事件触发率", 
             ItemType.SPECIAL, 150, {"luck": True}, "🍀"),
        Item("special_egg", "神秘蛋", "孵化出随机宠物", 
             ItemType.SPECIAL, 300, {"egg": True}, "🥚"),
        Item("special_rename", "改名卡", "可以给宠物改名", 
             ItemType.SPECIAL, 50, {"rename": True}, "📝"),
    ]
    
    def __init__(self):
        self.items: Dict[str, Item] = {}
        self.daily_specials: List[str] = []
        self._init_shop()
    
    def _init_shop(self):
        """初始化商店"""
        for item in self.DEFAULT_ITEMS:
            self.items[item.id] = item
        self._generate_daily_specials()
    
    def _generate_daily_specials(self):
        """生成每日特价商品"""
        # 随机选择 3 个商品作为特价
        all_items = list(self.items.keys())
        self.daily_specials = random.sample(all_items, min(3, len(all_items)))
    
    def get_item(self, item_id: str) -> Optional[Item]:
        """获取商品信息"""
        return self.items.get(item_id)
    
    def get_items_by_type(self, item_type: ItemType) -> List[Item]:
        """按类型获取商品"""
        return [item for item in self.items.values() if item.item_type == item_type]
    
    def get_daily_specials(self) -> List[Item]:
        """获取每日特价商品"""
        return [self.items[item_id] for item_id in self.daily_specials]
    
    def get_discount_price(self, item_id: str) -> int:
        """获取特价商品价格（8 折）"""
        if item_id in self.daily_specials:
            item = self.items[item_id]
            return int(item.price * 0.8)
        return self.items[item_id].price if item_id in self.items else 0
    
    def display(self, show_all: bool = True):
        """显示商店商品"""
        print("\n" + "=" * 60)
        print("🏪 宠物商店")
        print("=" * 60)
        
        # 显示每日特价
        if self.daily_specials:
            print("\n🔥 今日特价 (8 折优惠) 🔥")
            print("-" * 40)
            for item_id in self.daily_specials:
                item = self.items[item_id]
                original_price = item.price
                discount_price = int(item.price * 0.8)
                print(f"  {item.icon} {item.name}")
                print(f"     {item.description}")
                print(f"     💰 {discount_price}金币 (原价：{original_price})")
        
        if not show_all:
            return
        
        # 按类型显示所有商品
        for item_type in ItemType:
            print(f"\n【{item_type.value}】")
            print("-" * 40)
            items = self.get_items_by_type(item_type)
            for item in items:
                price_display = f"💰 {item.price}"
                if item.id in self.daily_specials:
                    price_display += f" (特价：{int(item.price * 0.8)})"
                print(f"  {item.icon} {item.name}: {item.description}")
                print(f"     {price_display}金币")
        
        print("=" * 60)


class Inventory:
    """背包系统"""
    
    def __init__(self):
        self.items: Dict[str, int] = {}  # item_id -> quantity
        self.coins: int = 100  # 初始金币
        self.max_capacity: int = 50  # 最大容量
    
    def add_item(self, item_id: str, quantity: int = 1) -> bool:
        """添加物品到背包"""
        current_count = sum(self.items.values())
        if current_count + quantity > self.max_capacity:
            return False
        
        if item_id in self.items:
            self.items[item_id] += quantity
        else:
            self.items[item_id] = quantity
        return True
    
    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """从背包移除物品"""
        if item_id not in self.items or self.items[item_id] < quantity:
            return False
        
        self.items[item_id] -= quantity
        if self.items[item_id] <= 0:
            del self.items[item_id]
        return True
    
    def has_item(self, item_id: str, quantity: int = 1) -> bool:
        """检查是否有物品"""
        return item_id in self.items and self.items[item_id] >= quantity
    
    def get_quantity(self, item_id: str) -> int:
        """获取物品数量"""
        return self.items.get(item_id, 0)
    
    def add_coins(self, amount: int):
        """增加金币"""
        self.coins += amount
    
    def remove_coins(self, amount: int) -> bool:
        """消耗金币"""
        if self.coins >= amount:
            self.coins -= amount
            return True
        return False
    
    def buy_item(self, shop: Shop, item_id: str) -> tuple[bool, str]:
        """购买物品"""
        item = shop.get_item(item_id)
        if not item:
            return False, "商品不存在！"
        
        price = shop.get_discount_price(item_id)
        
        if not self.remove_coins(price):
            return False, f"金币不足！需要{price}金币，你只有{self.coins}金币"
        
        if not self.add_item(item_id):
            self.add_coins(price)  # 退还金币
            return False, "背包已满！"
        
        return True, f"成功购买 {item.icon} {item.name}！花费{price}金币"
    
    def use_item(self, item_id: str, pet) -> tuple[bool, str]:
        """使用物品"""
        if not self.has_item(item_id):
            return False, "没有这个物品！"
        
        item = Item.from_dict({
            "id": item_id,
            "name": "",
            "description": "",
            "type": "SPECIAL",
            "price": 0,
            "effect": {},
            "icon": ""
        })
        
        # 从商店获取物品信息
        shop = Shop()
        shop_item = shop.get_item(item_id)
        if shop_item:
            item = shop_item
        
        effect = item.effect
        messages = []
        
        # 应用效果
        if "hunger" in effect:
            pet.hunger = min(100, pet.hunger + effect["hunger"])
            messages.append(f"饥饿{'+' if effect['hunger'] > 0 else ''}{effect['hunger']}")
        
        if "happiness" in effect:
            pet.happiness = min(100, pet.happiness + effect["happiness"])
            messages.append(f"心情{'+' if effect['happiness'] > 0 else ''}{effect['happiness']}")
        
        if "health" in effect:
            pet.health = min(100, pet.health + effect["health"])
            messages.append(f"健康{'+' if effect['health'] > 0 else ''}{effect['health']}")
        
        if "energy" in effect:
            pet.energy = min(100, pet.energy + effect["energy"])
            messages.append(f"精力{'+' if effect['energy'] > 0 else ''}{effect['energy']}")
        
        if "exp" in effect:
            pet.gain_exp(effect["exp"])
            messages.append(f"经验+{effect['exp']}")
        
        if "accessory" in effect:
            pet.appearance["accessory"] = effect["accessory"]
            messages.append(f"装备了{effect['accessory']}")
        
        if "rename" in effect:
            self.remove_item(item_id)
            return True, "改名卡已使用！请输入新名字："
        
        # 消耗物品（特殊物品除外）
        if item.item_type != ItemType.SPECIAL:
            self.remove_item(item_id)
        
        message = f"使用了{item.icon} {item.name}！\n" + ", ".join(messages)
        return True, message
    
    def display(self, shop: Shop = None):
        """显示背包内容"""
        print("\n" + "=" * 50)
        print("🎒 背包")
        print("=" * 50)
        print(f"💰 金币：{self.coins}")
        print(f"📦 容量：{sum(self.items.values())}/{self.max_capacity}")
        print("-" * 50)
        
        if not self.items:
            print("  背包是空的...")
        else:
            if shop is None:
                shop = Shop()
            
            for item_id, quantity in self.items.items():
                item = shop.get_item(item_id)
                if item:
                    print(f"  {item.icon} {item.name} x{quantity}")
                    print(f"     {item.description}")
                else:
                    print(f"  📦 未知物品 x{quantity}")
        
        print("=" * 50)
    
    def to_dict(self) -> dict:
        """序列化"""
        return {
            "items": self.items,
            "coins": self.coins,
            "max_capacity": self.max_capacity
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Inventory":
        """反序列化"""
        inv = cls()
        inv.items = data.get("items", {})
        inv.coins = data.get("coins", 100)
        inv.max_capacity = data.get("max_capacity", 50)
        return inv
