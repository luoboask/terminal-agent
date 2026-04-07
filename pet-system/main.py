#!/usr/bin/env python3
"""
养成式宠物系统 - 主程序
"""
from pet import Pet
from storage import PetStorage
import time

def display_pet_status(pet: Pet):
    """显示宠物状态"""
    print("\n" + "=" * 50)
    print(f"🐾 {pet.name} 的状态")
    print("=" * 50)
    print(f"📊 等级：{pet.level}  |  经验：{pet.exp}/{pet.exp_to_next_level}")
    print(f"❤️  健康：{pet.health}/100  |  心情：{pet.happiness}/100")
    print(f"🍖 饥饿：{pet.hunger}/100  |  精力：{pet.energy}/100")
    print(f"🎂 年龄：{pet.age} 天  |  💩 清洁：{pet.cleanliness}/100")
    print(f"🏆 成长阶段：{pet.growth_stage}")
    
    # 显示状态条
    print("\n状态条:")
    print(f"健康   [{'█' * (pet.health // 5)}{'░' * (20 - pet.health // 5)}] {pet.health}%")
    print(f"心情   [{'█' * (pet.happiness // 5)}{'░' * (20 - pet.happiness // 5)}] {pet.happiness}%")
    print(f"饥饿   [{'█' * (pet.hunger // 5)}{'░' * (20 - pet.hunger // 5)}] {pet.hunger}%")
    print(f"精力   [{'█' * (pet.energy // 5)}{'░' * (20 - pet.energy // 5)}] {pet.energy}%")
    print(f"清洁   [{'█' * (pet.cleanliness // 5)}{'░' * (20 - pet.cleanliness // 5)}] {pet.cleanliness}%")
    print("=" * 50)

def display_menu():
    """显示主菜单"""
    print("\n🎮 养成式宠物系统 🎮")
    print("-" * 30)
    print("1. 🍖 喂食")
    print("2. 🎾 玩耍")
    print("3. 📚 训练")
    print("4. 😴 休息")
    print("5. 🛁 清洁")
    print("6. 💊 治疗")
    print("7. 📊 查看状态")
    print("8. 💾 保存游戏")
    print("9. 📂 加载游戏")
    print("0. 🚪 退出")
    print("-" * 30)

def main():
    """主函数"""
    print("🎉 欢迎来到养成式宠物系统！🎉")
    
    storage = PetStorage()
    pet = None
    
    # 尝试加载已有存档
    if storage.exists():
        choice = input("\n发现存档，是否加载？(y/n): ").strip().lower()
        if choice == 'y':
            pet = storage.load()
            if pet:
                print(f"\n✅ 加载成功！欢迎回来，{pet.name}！")
    
    # 创建新宠物
    if not pet:
        print("\n✨ 让我们创建你的新宠物吧！✨")
        name = input("请输入宠物的名字：").strip()
        if not name:
            name = "小宠物"
        
        print("\n选择宠物类型:")
        print("1. 🐱 小猫")
        print("2. 🐶 小狗")
        print("3. 🐰 小兔")
        print("4. 🐼 熊猫")
        
        pet_type = input("请选择 (1-4): ").strip()
        type_map = {'1': 'cat', '2': 'dog', '3': 'rabbit', '4': 'panda'}
        pet_type = type_map.get(pet_type, 'cat')
        
        pet = Pet(name, pet_type)
        print(f"\n🎊 恭喜你获得了 {name}！🎊")
        display_pet_status(pet)
    
    # 主游戏循环
    while True:
        display_menu()
        choice = input("请选择操作：").strip()
        
        if choice == '1':  # 喂食
            print("\n选择食物:")
            print("1. 🍎 普通食物 (+15 饥饿，+5 健康)")
            print("2. 🍰 美味甜点 (+25 饥饿，+10 心情，-5 健康)")
            print("3. 🥩 营养大餐 (+35 饥饿，+15 健康)")
            food = input("选择 (1-3): ").strip()
            food_map = {'1': 'normal', '2': 'sweet', '3': 'premium'}
            result = pet.feed(food_map.get(food, 'normal'))
            print(f"\n{result}")
            
        elif choice == '2':  # 玩耍
            print("\n选择活动:")
            print("1. 🎾 玩球 (-15 精力，+20 心情)")
            print("2. 🏃 散步 (-25 精力，+30 心情，+5 健康)")
            print("3. 🎪 表演 (-35 精力，+40 心情，+10 经验)")
            activity = input("选择 (1-3): ").strip()
            activity_map = {'1': 'ball', '2': 'walk', '3': 'show'}
            result = pet.play(activity_map.get(activity, 'ball'))
            print(f"\n{result}")
            
        elif choice == '3':  # 训练
            result = pet.train()
            print(f"\n{result}")
            
        elif choice == '4':  # 休息
            hours = input("休息几小时？(1-12): ").strip()
            try:
                hours = int(hours)
                hours = max(1, min(12, hours))
            except:
                hours = 1
            result = pet.rest(hours)
            print(f"\n{result}")
            
        elif choice == '5':  # 清洁
            result = pet.clean()
            print(f"\n{result}")
            
        elif choice == '6':  # 治疗
            result = pet.heal()
            print(f"\n{result}")
            
        elif choice == '7':  # 查看状态
            display_pet_status(pet)
            
        elif choice == '8':  # 保存
            if storage.save(pet):
                print("\n✅ 游戏已保存！")
            else:
                print("\n❌ 保存失败！")
                
        elif choice == '9':  # 加载
            loaded_pet = storage.load()
            if loaded_pet:
                pet = loaded_pet
                print(f"\n✅ 加载成功！欢迎回来，{pet.name}！")
                display_pet_status(pet)
            else:
                print("\n❌ 没有存档或加载失败！")
                
        elif choice == '0':  # 退出
            print("\n💝 感谢游玩！下次再见！💝")
            break
            
        else:
            print("\n❌ 无效的选择，请重新输入！")
        
        # 检查宠物状态
        if pet.health <= 0:
            print("\n💔 很遗憾，你的宠物因为健康值过低而离开了...")
            print("请重新开始游戏吧！")
            break
        
        # 时间流逝效果
        pet.pass_time(0.5)  # 每次操作后时间流逝

if __name__ == "__main__":
    main()
