#!/usr/bin/env python3
"""
macOS 风格主窗口
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QFrame, QLabel, QPushButton,
    QGraphicsDropShadowEffect, QSystemTrayIcon, QMenu
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon, QFont, QAction

from .styles import MacOSTheme
from .pet_widget import PetWidget
from .status_bar import StatusBarWidget
from .action_menu import ActionMenuWidget
from .shop_widget import ShopWidget
from .inventory_widget import InventoryWidget
from .achievements_widget import AchievementsWidget
from .dialogs import MacOSSystemTray

import sys
import os

# 添加父目录到路径以便导入 pet 模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pet import Pet


class TitleBar(QFrame):
    """macOS 风格标题栏"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TitleBar")
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)
        
        # 窗口控制按钮（红黄绿）
        buttons_frame = QFrame()
        buttons_layout = QHBoxLayout(buttons_frame)
        buttons_layout.setSpacing(6)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        self.close_btn = QPushButton()
        self.close_btn.setObjectName("CloseButton")
        self.close_btn.setFixedSize(12, 12)
        self.close_btn.clicked.connect(self.parent().close)
        
        self.minimize_btn = QPushButton()
        self.minimize_btn.setObjectName("MinimizeButton")
        self.minimize_btn.setFixedSize(12, 12)
        self.minimize_btn.clicked.connect(lambda: self.parent().showMinimized())
        
        self.maximize_btn = QPushButton()
        self.maximize_btn.setObjectName("MaximizeButton")
        self.maximize_btn.setFixedSize(12, 12)
        self.maximize_btn.clicked.connect(lambda: self.parent().showMaximized() if not self.parent().isMaximized() else self.parent().showNormal())
        
        buttons_layout.addWidget(self.close_btn)
        buttons_layout.addWidget(self.minimize_btn)
        buttons_layout.addWidget(self.maximize_btn)
        
        # 标题
        self.title_label = QLabel("🐾 宠物养成系统")
        self.title_label.setObjectName("TitleLabel")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 添加弹性空间
        layout.addWidget(buttons_frame)
        layout.addWidget(self.title_label, 1)
        
        # 右侧占位（保持标题居中）
        placeholder = QFrame()
        placeholder.setFixedSize(50, 12)
        layout.addWidget(placeholder)


class MainWindow(QMainWindow):
    """macOS 风格主窗口"""
    
    # 信号
    pet_updated = pyqtSignal()
    game_saved = pyqtSignal(bool)
    game_loaded = pyqtSignal(bool)
    
    def __init__(self, pet: Pet = None):
        super().__init__()
        self.pet = pet or Pet("小宠物")
        self.theme = MacOSTheme()
        
        self.setup_window()
        self.setup_ui()
        self.apply_styles()
        self.setup_system_tray()
        
        # 自动保存定时器（每 5 分钟）
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.start(5 * 60 * 1000)  # 5 分钟
        
        # 状态更新定时器（每秒）
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_pet_status)
        self.update_timer.start(1000)
        
    def setup_window(self):
        """设置窗口属性"""
        self.setWindowTitle("🐾 宠物养成系统")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        # 设置窗口背景透明（用于圆角效果）
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(self.theme.shadow_color)
        self.setGraphicsEffect(shadow)
        
    def setup_ui(self):
        """设置界面"""
        # 中央部件
        central_widget = QWidget()
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 标题栏
        self.title_bar = TitleBar(self)
        main_layout.addWidget(self.title_bar)
        
        # 内容区域
        content_frame = QFrame()
        content_frame.setObjectName("ContentFrame")
        main_layout.addWidget(content_frame, 1)
        
        content_layout = QHBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # 左侧：宠物展示区
        left_panel = QFrame()
        left_panel.setObjectName("LeftPanel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(20)
        
        # 宠物组件
        self.pet_widget = PetWidget(self.pet)
        left_layout.addWidget(self.pet_widget, 1)
        
        # 状态栏
        self.status_bar = StatusBarWidget(self.pet)
        left_layout.addWidget(self.status_bar)
        
        content_layout.addWidget(left_panel, 2)
        
        # 右侧：功能面板
        right_panel = QFrame()
        right_panel.setObjectName("RightPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(20)
        
        # 功能切换按钮
        self.action_menu = ActionMenuWidget()
        self.action_menu.action_selected.connect(self.on_action_selected)
        right_layout.addWidget(self.action_menu)
        
        # 功能页面栈
        self.stack_widget = QStackedWidget()
        
        # 添加各个页面
        self.shop_widget = ShopWidget(self.pet)
        self.inventory_widget = InventoryWidget(self.pet)
        self.achievements_widget = AchievementsWidget(self.pet)
        
        self.stack_widget.addWidget(self.shop_widget)
        self.stack_widget.addWidget(self.inventory_widget)
        self.stack_widget.addWidget(self.achievements_widget)
        
        right_layout.addWidget(self.stack_widget, 1)
        
        content_layout.addWidget(right_panel, 1)
        
        # 底部状态栏
        self.bottom_status = QLabel("💰 金币：100  |  📅 第 1 天  |  ☀️ 晴天")
        self.bottom_status.setObjectName("BottomStatus")
        main_layout.addWidget(self.bottom_status)
        
    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet(self.theme.main_window_style)
        self.title_bar.setStyleSheet(self.theme.title_bar_style)
        
    def setup_system_tray(self):
        """设置系统托盘"""
        self.tray = MacOSSystemTray(self)
        self.tray.show()
        
    def on_action_selected(self, action_id: str):
        """处理动作选择"""
        action_map = {
            'shop': 0,
            'inventory': 1,
            'achievements': 2,
        }
        
        if action_id in action_map:
            self.stack_widget.setCurrentIndex(action_map[action_id])
            
    def update_pet_status(self):
        """更新宠物状态"""
        self.pet_widget.update_display()
        self.status_bar.update_all()
        self.update_bottom_status()
        
    def update_bottom_status(self):
        """更新底部状态栏"""
        weather_icons = {
            'sunny': '☀️',
            'cloudy': '☁️',
            'rainy': '🌧️',
            'snowy': '❄️',
        }
        # 这里应该从 weather_system 获取，暂时用默认值
        self.bottom_status.setText(
            f"💰 金币：{self.pet.coins}  |  📅 第 {getattr(self, 'day', 1)} 天  |  ☀️ 晴天"
        )
        
    def auto_save(self):
        """自动保存"""
        from storage import PetStorage
        storage = PetStorage()
        if storage.save(self.pet):
            print("✅ 自动保存成功")
            
    def closeEvent(self, event):
        """关闭事件"""
        # 保存游戏
        self.auto_save()
        
        # 显示退出确认
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self,
            '确认退出',
            '游戏已自动保存，确定要退出吗？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()
