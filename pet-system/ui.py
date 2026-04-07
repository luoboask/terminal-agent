#!/usr/bin/env python3
"""
增强 UI 模块 - 彩色输出、动画效果、更好的视觉体验
"""
import sys
import time
import shutil
from typing import Optional

# ANSI 颜色代码
class Colors:
    """颜色定义"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    
    # 前景色
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # 亮色前景
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    # 背景色
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


def supports_color() -> bool:
    """检查终端是否支持颜色"""
    try:
        import os
        if os.name == 'nt':
            return True
        return sys.stdout.isatty()
    except:
        return False


# 全局颜色开关
USE_COLOR = supports_color()


def c(text: str, color: str = Colors.RESET) -> str:
    """给文本添加颜色"""
    if USE_COLOR:
        return f"{color}{text}{Colors.RESET}"
    return text


def print_color(text: str, color: str = Colors.RESET, end: str = "\n"):
    """打印彩色文本"""
    print(c(text, color), end=end)


def print_banner(title: str, subtitle: str = "", width: int = 60):
    """打印横幅标题"""
    print()
    print(c("=" * width, Colors.BRIGHT_CYAN))
    print(c(" " * ((width - len(title)) // 2), end=""))
    print(c(title, Colors.BOLD + Colors.BRIGHT_WHITE))
    if subtitle:
        print(c(" " * ((width - len(subtitle)) // 2), end=""))
        print(c(subtitle, Colors.DIM + Colors.CYAN))
    print(c("=" * width, Colors.BRIGHT_CYAN))
    print()


def print_section(title: str, width: int = 50):
    """打印章节标题"""
    print()
    print(c("─" * width, Colors.CYAN))
    print(c(f"  {title}", Colors.BOLD + Colors.BRIGHT_CYAN))
    print(c("─" * width, Colors.CYAN))


def print_success(message: str):
    """打印成功消息"""
    print(f"\n{c('✅', Colors.GREEN)} {c(message, Colors.GREEN)}")


def print_error(message: str):
    """打印错误消息"""
    print(f"\n{c('❌', Colors.RED)} {c(message, Colors.RED)}")


def print_warning(message: str):
    """打印警告消息"""
    print(f"\n{c('⚠️', Colors.YELLOW)} {c(message, Colors.YELLOW)}")


def print_info(message: str):
    """打印信息消息"""
    print(f"\n{c('ℹ️', Colors.BLUE)} {c(message, Colors.BLUE)}")


def create_progress_bar(current: int, max_val: int, width: int = 20, 
                       fill_char: str = "█", empty_char: str = "░") -> str:
    """创建进度条"""
    if max_val == 0:
        percent = 0
    else:
        percent = int((current / max_val) * 100)
    
    filled = int((current / max_val) * width) if max_val > 0 else 0
    filled = min(filled, width)
    empty = width - filled
    
    bar = f"{fill_char * filled}{empty_char * empty}"
    return f"[{bar}] {percent:3d}%"


def get_status_color(value: int) -> str:
    """根据数值获取颜色"""
    if value >= 80:
        return Colors.BRIGHT_GREEN
    elif value >= 60:
        return Colors.GREEN
    elif value >= 40:
        return Colors.YELLOW
    elif value >= 20:
        return Colors.BRIGHT_YELLOW
    else:
        return Colors.RED


def print_pet_status(pet, width: int = 55):
    """打印宠物状态（增强版）"""
    print()
    print(c("╔" + "═" * (width - 2) + "╗", Colors.BRIGHT_CYAN))
    
    # 宠物名称和类型
    header = f"🐾 {pet.name} ({pet.pet_type.value})"
    padding = (width - 2 - len(header)) // 2
    print(c("║" + " " * padding + header + " " * (width - 2 - padding - len(header)) + "║", Colors.BRIGHT_WHITE))
    
    print(c("╠" + "═" * (width - 2) + "╣", Colors.BRIGHT_CYAN))
    
    # 等级和经验
    level_info = f"📊 等级：Lv.{pet.level}  |  经验：{pet.exp}/{pet.exp_to_next_level}"
    print(c("║ " + level_info + " " * (width - 3 - len(level_info)) + "║", Colors.WHITE))
    
    # 成长阶段
    stage_info = f"🏆 成长阶段：{pet.growth_stage}"
    print(c("║ " + stage_info + " " * (width - 3 - len(stage_info)) + "║", Colors.DIM))
    
    print(c("╠" + "═" * (width - 2) + "╣", Colors.BRIGHT_CYAN))
    
    # 状态条
    stats = [
        ("❤️ 健康", pet.health, get_status_color(pet.health)),
        ("😊 心情", pet.happiness, get_status_color(pet.happiness)),
        ("🍖 饥饿", pet.hunger, get_status_color(pet.hunger)),
        ("⚡ 精力", pet.energy, get_status_color(pet.energy)),
        ("🛁 清洁", pet.cleanliness, get_status_color(pet.cleanliness)),
    ]
    
    for label, value, color in stats:
        bar = create_progress_bar(value, 100, 18)
        # 根据数值给进度条上色
        bar_colored = ""
        filled = int((value / 100) * 18)
        for i, char in enumerate(bar):
            if i < filled:
                bar_colored += c(char, color)
            else:
                bar_colored += char
        line = f"{label}: {bar_colored}"
        print(c("║ " + line + " " * (width - 3 - len(line.replace('\033[', '').replace('m', ''))) + "║", Colors.WHITE))
    
    print(c("╠" + "═" * (width - 2) + "╣", Colors.BRIGHT_CYAN))
    
    # 其他信息
    age_info = f"🎂 年龄：{pet.age} 天  |  💫 心情：{pet.mood.value}"
    print(c("║ " + age_info + " " * (width - 3 - len(age_info)) + "║", Colors.WHITE))
    
    # 外观信息
    if pet.appearance.get("accessory"):
        acc_info = f"🎀 装饰：{pet.appearance['accessory']}"
        print(c("║ " + acc_info + " " * (width - 3 - len(acc_info)) + "║", Colors.BRIGHT_MAGENTA))
    
    print(c("╚" + "═" * (width - 2) + "╝", Colors.BRIGHT_CYAN))
    print()


def print_menu(options: list, title: str = "菜单", width: int = 40):
    """打印菜单"""
    print()
    print(c("┌" + "─" * (width - 2) + "┐", Colors.BRIGHT_YELLOW))
    print(c("│" + " " * ((width - 2 - len(title)) // 2) + title + " " * (width - 2 - ((width - 2 - len(title)) // 2) - len(title)) + "│", Colors.BOLD + Colors.BRIGHT_YELLOW))
    print(c("├" + "─" * (width - 2) + "┤", Colors.BRIGHT_YELLOW))
    
    for key, text in options:
        line = f"  {key}. {text}"
        print(c("│" + line + " " * (width - 2 - len(line)) + "│", Colors.WHITE))
    
    print(c("└" + "─" * (width - 2) + "┘", Colors.BRIGHT_YELLOW))


def animate_text(text: str, delay: float = 0.03, color: str = Colors.RESET):
    """打字机效果动画"""
    for char in text:
        print(c(char, color), end="", flush=True)
        time.sleep(delay)
    print()


def animate_emoji(emojis: list, repeats: int = 3, delay: float = 0.2):
    """表情动画"""
    for _ in range(repeats):
        for emoji in emojis:
            print(f"\r{emoji}", end="", flush=True)
            time.sleep(delay)
    print("\r ", end="", flush=True)


def print_level_up_animation(pet):
    """升级动画"""
    print()
    animate_emoji(["🌟", "⭐", "✨", "💫"], 2, 0.15)
    animate_text(f"🎉 恭喜！{pet.name} 升级到了 Lv.{pet.level}！", 0.05, Colors.BRIGHT_YELLOW)
    animate_emoji(["🎊", "🎈", "🎉"], 2, 0.15)
    print()


def print_achievement_unlocked(achievement_name: str):
    """成就解锁动画"""
    print()
    print(c("╔" + "═" * 40 + "╗", Colors.BRIGHT_YELLOW))
    print(c("║" + " " * 10 + "🏆 成就解锁！" + " " * 13 + "║", Colors.BOLD + Colors.BRIGHT_YELLOW))
    print(c("╠" + "═" * 40 + "╣", Colors.BRIGHT_YELLOW))
    print(c("║ " + achievement_name + " " * (38 - len(achievement_name)) + "║", Colors.WHITE))
    print(c("╚" + "═" * 40 + "╝", Colors.BRIGHT_YELLOW))
    print()


def clear_screen():
    """清屏"""
    import os
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


def print_weather_status(weather):
    """打印天气状态"""
    weather_icons = {
        "sunny": "☀️",
        "cloudy": "☁️",
        "rainy": "🌧️",
        "snowy": "❄️",
        "windy": "💨",
        "stormy": "⛈️"
    }
    icon = weather_icons.get(weather.current_weather, "🌤️")
    print(c(f"\n{icon} 当前天气：{weather.current_weather_name}", Colors.BRIGHT_CYAN))


def print_coins(coins: int):
    """打印金币显示"""
    print(c(f"💰 金币：{coins}", Colors.BRIGHT_YELLOW))


class UI:
    """UI 工具类 - 提供统一的界面输出方法"""
    
    @staticmethod
    def print_header(title: str):
        """打印标题头"""
        width = 60
        print()
        print(c("╔" + "═" * (width - 2) + "╗", Colors.BRIGHT_CYAN))
        print(c("║" + title.center(width - 2) + "║", Colors.BOLD + Colors.BRIGHT_CYAN))
        print(c("╚" + "═" * (width - 2) + "╝", Colors.BRIGHT_CYAN))
        print()
    
    @staticmethod
    def print_section(title: str):
        """打印章节标题"""
        print()
        print(c("─" * 50, Colors.CYAN))
        print(c(f"  {title}", Colors.BOLD + Colors.CYAN))
        print(c("─" * 50, Colors.CYAN))
    
    @staticmethod
    def print_status(name: str, value: int, max_value: int = 100, icon: str = "📊"):
        """打印状态条"""
        bar_width = 20
        filled = int((value / max_value) * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)
        color = Colors.GREEN if value > 60 else Colors.YELLOW if value > 30 else Colors.RED
        print(c(f"  {icon} {name}: [{bar}] {value}/{max_value}", color))
    
    @staticmethod
    def print_info(message: str):
        """打印信息"""
        print(c(f"  ℹ️  {message}", Colors.CYAN))
    
    @staticmethod
    def print_success(message: str):
        """打印成功消息"""
        print(c(f"  ✅ {message}", Colors.BRIGHT_GREEN))
    
    @staticmethod
    def print_warning(message: str):
        """打印警告消息"""
        print(c(f"  ⚠️  {message}", Colors.BRIGHT_YELLOW))
    
    @staticmethod
    def print_error(message: str):
        """打印错误消息"""
        print(c(f"  ❌ {message}", Colors.BRIGHT_RED))
    
    @staticmethod
    def print_menu(options: list, title: str = "菜单"):
        """打印菜单选项
        
        Args:
            options: 列表，每项为 (key, description, icon) 或 (key, description)
            title: 菜单标题
        """
        print()
        print(c(f"  📋 {title}", Colors.BOLD + Colors.BRIGHT_YELLOW))
        print(c("  " + "─" * 40, Colors.DIM))
        
        for opt in options:
            if len(opt) == 3:
                key, desc, icon = opt
            else:
                key, desc = opt
                icon = "  "
            print(c(f"  [{key}] {icon} {desc}", Colors.WHITE))
        
        print(c("  " + "─" * 40, Colors.DIM))
    
    @staticmethod
    def print_pet_card(pet):
        """打印宠物卡片"""
        from pet import PetMood
        
        print()
        print(c("  ╔" + "═" * 46 + "╗", Colors.BRIGHT_MAGENTA))
        print(c("  ║" + f" 🐾 {pet.name} ".center(46) + "║", Colors.BOLD + Colors.BRIGHT_MAGENTA))
        print(c("  ╠" + "═" * 46 + "╣", Colors.BRIGHT_MAGENTA))
        print(c(f"  ║  等级：Lv.{pet.level}  |  经验：{pet.exp}/{pet.exp_to_next_level}  ".ljust(47) + "║", Colors.WHITE))
        print(c(f"  ║  阶段：{pet.growth_stage}  ".ljust(47) + "║", Colors.WHITE))
        print(c(f"  ║  心情：{pet.mood.value}  ".ljust(47) + "║", Colors.WHITE))
        print(c("  ╠" + "═" * 46 + "╣", Colors.BRIGHT_MAGENTA))
        print(c("  ║  状态：", Colors.BRIGHT_MAGENTA), end="")
        
        # 状态条
        status_list = [
            ("❤️ 健康", pet.health, Colors.RED if pet.health < 30 else Colors.GREEN),
            ("😊 心情", pet.happiness, Colors.BLUE),
            ("🍖 饥饿", pet.hunger, Colors.YELLOW),
            ("⚡ 精力", pet.energy, Colors.CYAN),
            ("🛁 清洁", pet.cleanliness, Colors.MAGENTA)
        ]
        
        for name, val, color in status_list:
            bar = "█" * (val // 5) + "░" * (20 - val // 5)
            print(c(f"{name} [{bar}] {val}%", color))
            if name != "🛁 清洁":
                print(c("  ║  ", Colors.BRIGHT_MAGENTA), end="")
        
        print(c("  ╚" + "═" * 46 + "╝", Colors.BRIGHT_MAGENTA))
        print()
    
    @staticmethod
    def print_shop_item(item, index: int):
        """打印商店物品"""
        rarity_colors = {
            "common": Colors.WHITE,
            "rare": Colors.BLUE,
            "epic": Colors.MAGENTA,
            "legendary": Colors.BRIGHT_YELLOW
        }
        color = rarity_colors.get(getattr(item, 'rarity', 'common'), Colors.WHITE)
        print(c(f"  [{index}] {item.icon} {item.name} - {item.price}💰", color))
        print(c(f"      {item.description}", Colors.DIM))
    
    @staticmethod
    def print_achievement(achievement):
        """打印成就"""
        status = "🏆" if achievement.unlocked else "🔒"
        color = Colors.BRIGHT_YELLOW if achievement.unlocked else Colors.DIM
        print(c(f"  {status} {achievement.name} ({achievement.progress}/{achievement.requirement})", color))
        if not achievement.unlocked:
            print(c(f"      {achievement.description}", Colors.DIM))
    
    @staticmethod
    def confirm(prompt: str = "确定吗？") -> bool:
        """确认输入"""
        choice = input(c(f"  {prompt} (y/n): ", Colors.YELLOW)).strip().lower()
        return choice == 'y'
    
    @staticmethod
    def get_input(prompt: str, default: str = "") -> str:
        """获取输入"""
        result = input(c(f"  {prompt}", Colors.CYAN)).strip()
        return result if result else default
