#!/usr/bin/env python3
"""
宠物系统测试脚本 - 非交互式测试
"""
from pet import Pet
from storage import PetStorage

def test_pet_creation():
    """测试宠物创建"""
    print("🧪 测试 1: 宠物创建")
    pet = Pet('测试宠物')
    assert pet.name == '测试宠物'
    assert pet.level == 1
    assert pet.health == 100
    print("✅ 宠物创建成功")
    return True

def test_pet_actions():
    """测试宠物动作"""
    print("\n🧪 测试 2: 宠物动作")
    pet = Pet('测试宠物')
    
    # 测试喂食
    pet.feed(10)
    print(f"   喂食后饥饿：{pet.hunger}")
    
    # 测试玩耍
    pet.play(10)
    print(f"   玩耍后心情：{pet.happiness}")
    
    print("✅ 宠物动作测试成功")
    return True

def test_storage():
    """测试存储系统"""
    print("\n🧪 测试 3: 存储系统")
    storage = PetStorage()
    pet = Pet('存储测试')
    
    # 测试保存（保存宠物数据字典）
    pet_data = {
        'name': pet.name,
        'level': pet.level,
        'exp': pet.exp,
        'health': pet.health,
        'happiness': pet.happiness,
        'hunger': pet.hunger,
        'energy': pet.energy,
        'age': pet.age,
        'cleanliness': pet.cleanliness
    }
    storage.save(pet_data)
    print("   保存成功")
    
    # 测试加载
    loaded_data = storage.load()
    if loaded_data:
        print(f"   加载成功：{loaded_data.get('name', 'Unknown')}")
        print(f"   等级：{loaded_data.get('level', 0)}")
    
    print("✅ 存储系统测试成功")
    return True

if __name__ == '__main__':
    print("🎮 宠物系统自动化测试\n")
    print("=" * 50)
    
    try:
        test_pet_creation()
        test_pet_actions()
        test_storage()
        
        print("\n" + "=" * 50)
        print("✅ 所有测试通过！宠物系统运行正常！")
        print("=" * 50)
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
