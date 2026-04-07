#!/usr/bin/env python3
"""
养成式宠物系统 - 主程序（增强 UI 版）
"""
from pet import Pet, PetType
from storage import PetStorage
from ui import UI, Colors, animate_text, clear_screen
from shop import Shop, ItemType
from achievements import AchievementSystem
from events import EventSystem
from weather import WeatherSystem
import time
import random

def create_pet_ui():
    """UI 方式创建宠物"""
    clear_screen()
    UI.print_header("✨ 创建你的新宠物 ✨")
    
    # 输入名字
    name = input(f"{Colors.CYAN}请输入宠物的名字：{Colors.RESET}").strip()
    if not name:
        name = "小宠物"
    
    # 选择宠物类型
    print(f"\n{Colors.YELLOW}选择宠物类型:{Colors.RESET}")
    pet_types = [
        ("🐱", "小猫", PetType.CAT),
        ("🐶", "小狗", PetType.DOG),
        ("🐰", "小兔", PetType.RABBIT),
        ("🐦", "小鸟", PetType.BIRD),
        ("🐟", "小鱼", PetType.FISH),
    ]
    
    for i, (icon, name_zh, _) in enumerate(pet_types, 1):
        print(f"  {i}. {icon} {name_zh}")
    
    choice = input(f"\n{Colors.CYAN}请选择 (1-5)：{Colors.RESET}").strip()
    try:
        idx = int(choice) - 1
        idx = max(0, min(len(pet_types) - 1, idx))
        pet_type = pet_types[idx][2]
    except:
        pet_type = PetType.CAT
    
    return Pet(name, pet_type)

def main():
    """主函数"""
    clear_screen()
    UI.print_header("🎉 欢迎来到养成式宠物系统！🎉")
    
    # 初始化系统
    storage = PetStorage()
    shop = Shop()
    achievements = AchievementSystem()
    event_system = EventSystem()
    weather_system = WeatherSystem()
    
    pet = None
    
    # 尝试加载已有存档
    if storage.exists():
        print(f"\n{Colors.GREEN}发现存档！{Colors.RESET}")
        choice = input("是否加载？(y/n): ").strip().lower()
        if choice == 'y':
            pet = storage.load()
            if pet:
                print(f"\n{Colors.GREEN}✅ 加载成功！欢迎回来，{pet.name}！{Colors.RESET}")
                achievements.load_progress(pet)
    
    # 创建新宠物
    if not pet:
        time.sleep(0.5)
        pet = create_pet_ui()
        print(f"\n{Colors.RAINBOW}🎊 恭喜你获得了 {pet.name}！🎊{Colors.RESET}")
        UI.print_pet_status(pet)
    
    # 主游戏循环
    day = 1
    while True:
        # 更新天气
        weather = weather_system.get_current_weather()
        weather_system.apply_weather_effect(pet)
        
        # 显示主菜单
        UI.print_menu(day, weather)
        
        choice = input(f"\n{Colors.CYAN}请选择操作：{Colors.RESET}").strip()
        
        if choice == '1':  # 喂食
            clear_screen()
            UI.print_section("🍖 喂食")
            print("\n选择食物:")
            foods = [
                ("1", "🍎 普通粮食", "+20 饥饿，+2 健康", 10),
                ("2", "🍪 美味零食", "+10 饥饿，+15 心情", 15),
                ("3", "🍱 营养大餐", "+35 饥饿，+8 健康", 25),
                ("4", "🎂 豪华套餐", "+50 饥饿，+20 心情，+10 健康", 50),
            ]
            for code, name, effect, price in foods:
                print(f"  {code}. {name} ({effect}) - 💰{price}")
            
            food_choice = input(f"\n{Colors.CYAN}选择 (1-4)：{Colors.RESET}").strip()
            food_map = {'1': 'food_normal', '2': 'food_snack', '3': 'food_premium', '4': 'food_treat'}
            item_id = food_map.get(food_choice, 'food_normal')
            item = shop.get_item(item_id)
            
            if item:
                result = pet.use_item(item)
                print(f"\n{Colors.GREEN}{result}{Colors.RESET}")
            else:
                print(f"\n{Colors.RED}无效的选择！{Colors.RESET}")
            
        elif choice == '2':  # 玩耍
            clear_screen()
            UI.print_section("🎾 玩耍")
            print("\n选择活动:")
            activities = [
                ("1", "🎾 玩球", "-15 精力，+20 心情，+5 经验"),
                ("2", "🏃 散步", "-25 精力，+30 心情，+10 经验，+5 健康"),
                ("3", "🎪 表演", "-35 精力，+40 心情，+15 经验"),
                ("4", "🧩 益智游戏", "-20 精力，+25 心情，+20 经验"),
            ]
            for code, name, effect in activities:
                print(f"  {code}. {name} ({effect})")
            
            activity_choice = input(f"\n{Colors.CYAN}选择 (1-4)：{Colors.RESET}").strip()
            activity_map = {'1': 'ball', '2': 'walk', '3': 'show', '4': 'puzzle'}
            result = pet.play(activity_map.get(activity_choice, 'ball'))
            print(f"\n{Colors.GREEN}{result}{Colors.RESET}")
            
        elif choice == '3':  # 训练
            clear_screen()
            UI.print_section("📚 训练")
            result = pet.train()
            print(f"\n{Colors.GREEN}{result}{Colors.RESET}")
            
        elif choice == '4':  # 休息
            clear_screen()
            UI.print_section("😴 休息")
            hours = input("休息几小时？(1-12): ").strip()
            try:
                hours = int(hours)
                hours = max(1, min(12, hours))
            except:
                hours = 1
            result = pet.rest(hours)
            print(f"\n{Colors.GREEN}{result}{Colors.RESET}")
            
        elif choice == '5':  # 清洁
            clear_screen()
            UI.print_section("🛁 清洁")
            result = pet.clean()
            print(f"\n{Colors.GREEN}{result}{Colors.RESET}")
            
        elif choice == '6':  # 商店
            clear_screen()
            UI.print_section("🏪 宠物商店")
            print(f"\n💰 当前金币：{pet.coins}")
            shop.display_items()
            
            buy_choice = input(f"\n{Colors.CYAN}要购买什么？(输入物品 ID 或 q 返回)：{Colors.RESET}").strip()
            if buy_choice != 'q':
                item = shop.get_item(buy_choice)
                if item:
                    if pet.coins >= item.price:
                        pet.coins -= item.price
                        pet.inventory.append(item)
                        print(f"\n{Colors.GREEN}✅ 购买了 {item.name}！{Colors.RESET}")
                    else:
                        print(f"\n{Colors.RED}❌ 金币不足！{Colors.RESET}")
                else:
                    print(f"\n{Colors.RED}❌ 无效的物品 ID！{Colors.RESET}")
            
        elif choice == '7':  # 成就
            clear_screen()
            UI.print_section("🏆 成就系统")
            achievements.display_achievements()
            input("\n按回车继续...")
            
        elif choice == '8':  # 查看状态
            clear_screen()
            UI.print_pet_status(pet)
            
        elif choice == '9':  # 保存
            if storage.save(pet):
                print(f"\n{Colors.GREEN}✅ 游戏已保存！{Colors.RESET}")
            else:
                print(f"\n{Colors.RED}❌ 保存失败！{Colors.RESET}")
                
        elif choice == 's':  # 加载
            loaded_pet = storage.load()
            if loaded_pet:
                pet = loaded_pet
                print(f"\n{Colors.GREEN}✅ 加载成功！欢迎回来，{pet.name}！{Colors.RESET}")
                UI.print_pet_status(pet)
            else:
                print(f"\n{Colors.RED}❌ 没有存档或加载失败！{Colors.RESET}")
                
        elif choice == '0':  # 退出
            print(f"\n{Colors.RAINBOW}💝 感谢游玩！下次再见！💝{Colors.RESET}")
            break
            
        else:
            print(f"\n{Colors.RED}❌ 无效的选择，请重新输入！{Colors.RESET}")
        
        # 检查宠物状态
        if pet.health <= 0:
            print(f"\n{Colors.RED}💔 很遗憾，你的宠物因为健康值过低而离开了...{Colors.RESET}")
            print("请重新开始游戏吧！")
            break
        
        # 检查升级
        if pet.check_level_up():
            print(f"\n{Colors.RAINBOW}🎉 {pet.name} 升级到了 {pet.level} 级！{Colors.RESET}")
        
        # 更新成就
        achievements.update_all(pet)
        
        # 随机事件
        if random.random() < 0.15:  # 15% 概率触发事件
            event = event_system.get_random_event()
            if event:
                print(f"\n{Colors.YELLOW}{event.trigger(pet)[1]}{Colors.RESET}")
        
        # 时间流逝
        pet.pass_time(0.5)
        day += 1

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}游戏已退出。再见！{Colors.RESET}")
