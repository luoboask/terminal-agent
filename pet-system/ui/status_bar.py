#!/usr/bin/env python3
"""
状态栏组件 - macOS 风格进度条
"""
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QProgressBar
from PyQt6.QtCore import Qt, QPropertyAnimation, pyqtProperty
from typing import Dict, List, Tuple

from .styles import MacOSTheme


class AnimatedProgressBar(QProgressBar):
    """带动画效果的进度条"""
    
    def __init__(self, color: str = "#007AFF", height: int = 12):
        super().__init__()
        self.setRange(0, 100)
        self.setValue(50)
        self.setFixedHeight(height)
        self.setTextVisible(False)
        
        # 创建动画
        self._animation = QPropertyAnimation(self, b"value")
        self._animation.setDuration(500)
        self._animation.setEasingCurve(Qt.EasingCurve.OutCubic)
        
        # 应用样式
        self.setStyleSheet(self._get_stylesheet(color))
    
    def _get_stylesheet(self, color: str) -> str:
        """生成进度条样式"""
        return f"""
            QProgressBar {{
                background-color: {MacOSTheme.BG_TERTIARY};
                border-radius: {MacOSTheme.RADIUS_SMALL}px;
                border: none;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: {MacOSTheme.RADIUS_SMALL}px;
            }}
        """
    
    def set_value_animated(self, value: int):
        """动画设置数值"""
        self._animation.setStartValue(self.value())
        self._animation.setEndValue(value)
        self._animation.start()


class StatusItem(QWidget):
    """单个状态项"""
    
    def __init__(self, icon: str, label: str, color: str, max_value: int = 100):
        super().__init__()
        self.max_value = max_value
        
        # 图标标签
        self.icon_label = QLabel(icon)
        self.icon_label.setFixedSize(24, 24)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet(f"""
            QLabel {{
                font-size: 18px;
                padding: 2px;
            }}
        """)
        
        # 文字标签
        self.name_label = QLabel(label)
        self.name_label.setStyleSheet(f"""
            QLabel {{
                font-size: 13px;
                color: {MacOSTheme.TEXT_SECONDARY};
                font-weight: 500;
            }}
        """)
        
        # 数值标签
        self.value_label = QLabel("50/100")
        self.value_label.setFixedWidth(50)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.value_label.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                color: {MacOSTheme.TEXT_TERTIARY};
            }}
        """)
        
        # 进度条
        self.progress_bar = AnimatedProgressBar(color)
        
        # 布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(8)
        
        layout.addWidget(self.icon_label)
        layout.addWidget(self.name_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.value_label)
    
    def set_value(self, value: int, animate: bool = True):
        """设置状态值"""
        value = max(0, min(self.max_value, value))
        self.value_label.setText(f"{value}/{self.max_value}")
        
        if animate:
            self.progress_bar.set_value_animated(value)
        else:
            self.progress_bar.setValue(value)


class StatusBarWidget(QWidget):
    """状态栏组件"""
    
    # 状态配置：(图标，名称，颜色)
    STATUS_CONFIG: List[Tuple[str, str, str]] = [
        ("❤️", "健康", "#FF3B30"),
        ("😊", "心情", "#FF9500"),
        ("🍖", "饥饿", "#5856D6"),
        ("⚡", "精力", "#34C759"),
        ("🛁", "清洁", "#FF2D55"),
    ]
    
    def __init__(self, pet=None):
        super().__init__()
        self.pet = pet
        
        # 状态项字典
        self.status_items: Dict[str, StatusItem] = {}
        
        self._init_ui()
        
        if self.pet:
            self.update_all()
    
    def _init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)
        
        # 标题
        title = QLabel("📊 宠物状态")
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                font-weight: 600;
                color: {MacOSTheme.TEXT_PRIMARY};
                padding: 4px 0;
            }}
        """)
        layout.addWidget(title)
        
        # 状态项容器
        self.status_container = QWidget()
        self.status_layout = QVBoxLayout(self.status_container)
        self.status_layout.setContentsMargins(0, 0, 0, 0)
        self.status_layout.setSpacing(6)
        
        # 创建状态项
        for icon, name, color in self.STATUS_CONFIG:
            item = StatusItem(icon, name, color)
            self.status_items[name] = item
            self.status_layout.addWidget(item)
        
        layout.addWidget(self.status_container)
        
        # 应用背景样式
        self.setStyleSheet(f"""
            StatusBarWidget {{
                background-color: {MacOSTheme.BG_PRIMARY};
                border-radius: {MacOSTheme.RADIUS_MEDIUM}px;
            }}
        """)
    
    def update_all(self):
        """更新所有状态"""
        if not self.pet:
            return
        
        # 映射宠物属性到状态项
        self.status_items["健康"].set_value(self.pet.health)
        self.status_items["心情"].set_value(self.pet.happiness)
        self.status_items["饥饿"].set_value(self.pet.hunger)
        self.status_items["精力"].set_value(self.pet.energy)
        self.status_items["清洁"].set_value(self.pet.cleanliness)
    
    def update_health(self, value: int):
        """更新健康值"""
        self.status_items["健康"].set_value(value)
    
    def update_happiness(self, value: int):
        """更新心情值"""
        self.status_items["心情"].set_value(value)
    
    def update_hunger(self, value: int):
        """更新饥饿值"""
        self.status_items["饥饿"].set_value(value)
    
    def update_energy(self, value: int):
        """更新精力值"""
        self.status_items["精力"].set_value(value)
    
    def update_cleanliness(self, value: int):
        """更新清洁值"""
        self.status_items["清洁"].set_value(value)
    
    def set_pet(self, pet):
        """设置宠物对象"""
        self.pet = pet
        self.update_all()
