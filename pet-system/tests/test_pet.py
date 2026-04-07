"""
宠物类单元测试
"""
import unittest
from datetime import datetime
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pet import Pet, PetType, PetMood


class TestPetInitialization(unittest.TestCase):
    """测试宠物初始化"""
    
    def test_create_pet_with_default_type(self):
        """测试创建默认类型的宠物"""
        pet = Pet("旺财")
        self.assertEqual(pet.name, "旺财")
        self.assertEqual(pet.pet_type, PetType.DOG)
        
    def test_create_pet_with_custom_type(self):
        """测试创建自定义类型的宠物"""
        pet = Pet("咪咪", PetType.CAT)
        self.assertEqual(pet.pet_type, PetType.CAT)
        
    def test_pet_initial_stats(self):
        """测试宠物初始属性"""
        pet = Pet("测试")
        self.assertEqual(pet.level, 1)
        self.assertEqual(pet.exp, 0)
        self.assertEqual(pet.exp_to_next_level, 100)
        self.assertEqual(pet.health, 100)
        self.assertEqual(pet.happiness, 70)
        self.assertEqual(pet.energy, 80)
        self.assertEqual(pet.cleanliness, 80)
        self.assertEqual(pet.hunger, 50)
        
    def test_pet_initial_state(self):
        """测试宠物初始状态"""
        pet = Pet("测试")
        self.assertEqual(pet.mood, PetMood.NORMAL)
        self.assertFalse(pet.is_sleeping)
        self.assertTrue(pet.is_alive)
        
    def test_pet_growth_stage(self):
        """测试成长阶段"""
        pet = Pet("测试")
        self.assertEqual(pet.growth_stage, "幼年期")


class TestPetAttributes(unittest.TestCase):
    """测试宠物属性"""
    
    def test_age_property(self):
        """测试年龄属性"""
        pet = Pet("测试")
        self.assertEqual(pet.age, 0)
        
    def test_appearance(self):
        """测试外观"""
        pet = Pet("测试")
        self.assertEqual(pet.appearance["size"], "小")
        self.assertEqual(pet.appearance["color"], "棕色")
        self.assertIsNone(pet.appearance["accessory"])


class TestPetMood(unittest.TestCase):
    """测试宠物心情系统"""
    
    def test_mood_update_low_health(self):
        """测试低健康时心情更新"""
        pet = Pet("测试")
        pet.health = 25
        pet._update_mood()
        self.assertEqual(pet.mood, PetMood.SAD)
        
    def test_mood_update_low_hunger(self):
        """测试低饥饿时心情更新"""
        pet = Pet("测试")
        pet.hunger = 20
        pet._update_mood()
        self.assertEqual(pet.mood, PetMood.ANGRY)
        
    def test_mood_update_low_energy(self):
        """测试低精力时心情更新"""
        pet = Pet("测试")
        pet.energy = 15
        pet._update_mood()
        self.assertEqual(pet.mood, PetMood.SLEEPY)
        
    def test_mood_update_high_stats(self):
        """测试高属性时心情更新"""
        pet = Pet("测试")
        pet.happiness = 85
        pet.health = 85
        pet._update_mood()
        self.assertEqual(pet.mood, PetMood.HAPPY)
        
    def test_mood_update_normal(self):
        """测试正常状态心情"""
        pet = Pet("测试")
        pet._update_mood()
        self.assertEqual(pet.mood, PetMood.NORMAL)


class TestPetGrowth(unittest.TestCase):
    """测试宠物成长系统"""
    
    def test_check_evolution_level_5(self):
        """测试 5 级时进化"""
        pet = Pet("测试")
        pet.level = 5
        pet._check_evolution()
        self.assertEqual(pet.appearance["size"], "中")
        
    def test_check_evolution_already_evolved(self):
        """测试已进化后不再进化"""
        pet = Pet("测试")
        pet.level = 10
        pet.appearance["size"] = "中"
        pet._check_evolution()
        self.assertEqual(pet.appearance["size"], "中")
        
    def test_growth_stage_levels(self):
        """测试不同等级的成长阶段"""
        stages = [
            (1, "幼年期"),
            (4, "幼年期"),
            (5, "成长期"),
            (9, "成长期"),
            (10, "成熟期"),
            (14, "成熟期"),
            (15, "完全体"),
            (20, "完全体"),
        ]
        for level, expected_stage in stages:
            pet = Pet("测试")
            pet.level = level
            self.assertEqual(pet.growth_stage, expected_stage, f"Level {level} should be {expected_stage}")


class TestPetInteractions(unittest.TestCase):
    """测试宠物互动"""
    
    def setUp(self):
        """设置测试夹具"""
        self.pet = Pet("测试")
        
    def test_feed_increase_hunger(self):
        """测试喂食增加饥饿度"""
        initial_hunger = self.pet.hunger
        self.pet.feed(20)
        self.assertGreater(self.pet.hunger, initial_hunger)
        self.assertLessEqual(self.pet.hunger, 100)
        
    def test_feed_cannot_exceed_100(self):
        """测试喂食不能超过 100"""
        self.pet.hunger = 90
        self.pet.feed(20)
        self.assertEqual(self.pet.hunger, 100)
        
    def test_play_increase_happiness(self):
        """测试玩耍增加心情"""
        initial_happiness = self.pet.happiness
        self.pet.play()
        self.assertGreater(self.pet.happiness, initial_happiness)
        
    def test_sleep_restore_energy(self):
        """测试睡觉恢复精力"""
        self.pet.energy = 30
        self.pet.sleep()
        self.assertGreater(self.pet.energy, 30)
        
    def test_clean_increase_cleanliness(self):
        """测试清洁增加清洁度"""
        initial_cleanliness = self.pet.cleanliness
        self.pet.clean()
        self.assertGreater(self.pet.cleanliness, initial_cleanliness)
        
    def test_train_increase_exp(self):
        """测试训练增加经验"""
        initial_exp = self.pet.exp
        self.pet.train()
        self.assertGreater(self.pet.exp, initial_exp)


class TestPetLevelUp(unittest.TestCase):
    """测试宠物升级"""
    
    def setUp(self):
        """设置测试夹具"""
        self.pet = Pet("测试")
        
    def test_level_up_when_exp_sufficient(self):
        """测试经验足够时升级"""
        self.pet.exp = 100
        self.pet.check_level_up()
        self.assertEqual(self.pet.level, 2)
        self.assertEqual(self.pet.exp, 0)
        
    def test_no_level_up_when_exp_insufficient(self):
        """测试经验不足时不升级"""
        self.pet.exp = 50
        self.pet.check_level_up()
        self.assertEqual(self.pet.level, 1)
        self.assertEqual(self.pet.exp, 50)
        
    def test_exp_to_next_increases(self):
        """测试升级后所需经验增加"""
        self.pet.exp = 100
        self.pet.check_level_up()
        self.assertGreater(self.pet.exp_to_next_level, 100)


class TestPetSurvival(unittest.TestCase):
    """测试宠物生存机制"""
    
    def setUp(self):
        """设置测试夹具"""
        self.pet = Pet("测试")
        
    def test_starvation_damage(self):
        """测试饥饿造成伤害"""
        self.pet.hunger = 0
        self.pet.update_survival()
        self.assertLess(self.pet.health, 100)
        
    def test_low_cleanliness_damage(self):
        """测试低清洁度造成伤害"""
        self.pet.cleanliness = 0
        self.pet.update_survival()
        self.assertLess(self.pet.health, 100)
        
    def test_death_when_health_zero(self):
        """测试健康为零时死亡"""
        self.pet.health = 0
        self.pet.check_alive()
        self.assertFalse(self.pet.is_alive)


class TestPetStatistics(unittest.TestCase):
    """测试宠物统计"""
    
    def test_interaction_count_increases(self):
        """测试互动次数增加"""
        pet = Pet("测试")
        initial_count = pet.total_interactions
        pet.feed(10)
        self.assertGreater(pet.total_interactions, initial_count)


class TestPetSerialization(unittest.TestCase):
    """测试宠物序列化"""
    
    def test_to_dict(self):
        """测试转换为字典"""
        pet = Pet("测试")
        pet.level = 5
        data = pet.to_dict()
        
        self.assertEqual(data["name"], "测试")
        self.assertEqual(data["level"], 5)
        self.assertEqual(data["pet_type"], "狗狗")
        
    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            "name": "恢复的宠物",
            "pet_type": "猫咪",
            "level": 10,
            "exp": 500,
            "health": 80,
            "happiness": 90
        }
        pet = Pet.from_dict(data)
        
        self.assertEqual(pet.name, "恢复的宠物")
        self.assertEqual(pet.pet_type, PetType.CAT)
        self.assertEqual(pet.level, 10)
        self.assertEqual(pet.exp, 500)


if __name__ == "__main__":
    unittest.main()
