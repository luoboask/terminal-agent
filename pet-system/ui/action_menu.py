#!/usr/bin/env python3
"""
动作菜单组件 - macOS 风格卡片按钮
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont


class ActionButton(QFrame):
    """macOS 风格动作按钮"""
    
    clicked = pyqtSignal(str)
    
    def __init__(self, icon: str, text: str, action_id: str, parent=None):
        super().__init__(parent)
        self.action_id = action_id
        self.setup_ui(icon, text)
        
    def setup_ui(self, icon: str, text: str):
        """设置 UI"""
        self.setFixedSize(140, 120)
        self.setObjectName("actionButton")
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(10, 15, 10, 15)
        
        # 图标
        self.icon_label = QLabel(icon)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setFont(QFont("Apple Color Emoji", 36))
        
        # 文字
        self.text_label = QLabel(text)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setFont(QFont("PingFang SC", 13, QFont.Weight.Medium))
        self.text_label.setStyleSheet("color: #3C3C43;")
        
        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)
        
        # 应用样式
        self.apply_style()
        
    def apply_style(self):
        """应用样式"""
        self.setStyleSheet("""
            QFrame#actionButton {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E5E5EA;
            }
            QFrame#actionButton:hover {
                background-color: #F2F2F7;
                border: 1px solid #007AFF;
            }
            QFrame#actionButton:pressed {
                background-color: #E5E5EA;
            }
        """)
        
    def enterEvent(self, event):
        """鼠标进入动画"""
        self.animate_scale(1.05)
        
    def leaveEvent(self, event):
        """鼠标离开动画"""
        self.animate_scale(1.0)
        
    def animate_scale(self, scale: float):
        """缩放动画"""
        # 简单实现，实际可以使用 QPropertyAnimation
        pass
    
    def mousePressEvent(self, event):
        """点击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.action_id)
        super().mousePressEvent(event)


class ActionMenuWidget(QWidget):
    """动作菜单组件"""
    
    action_triggered = pyqtSignal(str)
    
    # 预定义动作
    ACTIONS = [
        ("🍖", "喂食", "feed"),
        ("🎮", "玩耍", "play"),
        ("📚", "训练", "train"),
        ("😴", "休息", "rest"),
        ("🛁", "清洁", "clean"),
        ("💊", "治疗", "heal"),
        ("🏪", "商店", "shop"),
        ("🎒", "背包", "inventory"),
        ("🏆", "成就", "achievements"),
        ("📊", "状态", "status"),
        ("💾", "保存", "save"),
        ("⚙️", "设置", "settings"),
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """设置 UI"""
        self.setObjectName("actionMenu")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(12)
        
        # 标题
        title = QLabel("动作菜单")
        title.setFont(QFont("PingFang SC", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #000000; padding-bottom: 10px;")
        layout.addWidget(title)
        
        # 按钮网格
        grid_layout = QHBoxLayout()
        grid_layout.setSpacing(12)
        
        # 分两行显示
        row1 = QHBoxLayout()
        row2 = QHBoxLayout()
        row1.setSpacing(12)
        row2.setSpacing(12)
        
        buttons = []
        for i, (icon, text, action_id) in enumerate(self.ACTIONS):
            btn = ActionButton(icon, text, action_id)
            btn.clicked.connect(self.on_action_clicked)
            buttons.append(btn)
            
            if i < 6:
                row1.addWidget(btn)
            else:
                row2.addWidget(btn)
        
        row1.addStretch()
        row2.addStretch()
        
        layout.addLayout(row1)
        layout.addLayout(row2)
        layout.addStretch()
        
        # 应用样式
        self.setStyleSheet("""
            QWidget#actionMenu {
                background-color: #F2F2F7;
                border-radius: 16px;
            }
        """)
        
    def on_action_clicked(self, action_id: str):
        """处理动作点击"""
        self.action_triggered.emit(action_id)
        
    def set_action_enabled(self, action_id: str, enabled: bool):
        """设置动作是否可用"""
        for child in self.findChildren(ActionButton):
            if child.action_id == action_id:
                child.setEnabled(enabled)
                child.setStyleSheet(f"""
                    QFrame#actionButton {{
                        background-color: #FFFFFF;
                        border-radius: 12px;
                        border: 1px solid #E5E5EA;
                        opacity: {1.0 if enabled else 0.5};
                    }}
                """)
                break
