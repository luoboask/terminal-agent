"""
机器人大战游戏 - 配置文件
"""

# 游戏窗口设置
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

# 机器人类型
ROBOT_TYPES = {
    'warrior': {
        'name': '战士型',
        'hp': 150,
        'attack': 25,
        'defense': 20,
        'speed': 10,
        'color': RED,
        'skills': ['重击', '防御姿态']
    },
    'assassin': {
        'name': '刺客型',
        'hp': 100,
        'attack': 35,
        'defense': 10,
        'speed': 25,
        'color': PURPLE,
        'skills': ['快速连击', '闪避']
    },
    'tank': {
        'name': '坦克型',
        'hp': 200,
        'attack': 15,
        'defense': 35,
        'speed': 5,
        'color': BLUE,
        'skills': ['铁壁防御', '反击']
    },
    'sniper': {
        'name': '狙击型',
        'hp': 80,
        'attack': 45,
        'defense': 8,
        'speed': 15,
        'color': GREEN,
        'skills': ['精准射击', '远程打击']
    }
}

# 技能定义
SKILLS = {
    '重击': {
        'damage_multiplier': 1.5,
        'accuracy': 0.9,
        'energy_cost': 20,
        'description': '造成 150% 伤害，命中率 90%'
    },
    '防御姿态': {
        'defense_bonus': 15,
        'duration': 3,
        'energy_cost': 15,
        'description': '提升防御力 15 点，持续 3 回合'
    },
    '快速连击': {
        'damage_multiplier': 0.7,
        'hit_count': 3,
        'accuracy': 0.85,
        'energy_cost': 25,
        'description': '连续攻击 3 次，每次造成 70% 伤害'
    },
    '闪避': {
        'dodge_chance': 0.5,
        'duration': 2,
        'energy_cost': 20,
        'description': '50% 几率闪避攻击，持续 2 回合'
    },
    '铁壁防御': {
        'defense_bonus': 25,
        'duration': 3,
        'energy_cost': 25,
        'description': '提升防御力 25 点，持续 3 回合'
    },
    '反击': {
        'counter_damage': 0.5,
        'duration': 3,
        'energy_cost': 20,
        'description': '受到攻击时反弹 50% 伤害，持续 3 回合'
    },
    '精准射击': {
        'damage_multiplier': 2.0,
        'accuracy': 0.95,
        'energy_cost': 30,
        'description': '造成 200% 伤害，命中率 95%'
    },
    '远程打击': {
        'damage_multiplier': 1.3,
        'accuracy': 0.9,
        'ignore_defense': 0.5,
        'energy_cost': 25,
        'description': '造成 130% 伤害，无视 50% 防御'
    }
}

# 游戏状态
GAME_STATES = {
    'MENU': 'menu',
    'SELECT': 'select',
    'BATTLE': 'battle',
    'VICTORY': 'victory',
    'DEFEAT': 'defeat'
}
