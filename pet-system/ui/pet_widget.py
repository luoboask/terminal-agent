#!/usr/bin/env python3
"""
宠物显示组件 - macOS 风格
"""
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsView, QGraphicsScene
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QBrush, QPen

from pet import Pet, PetMood, PetType
from .styles import MacOSTheme


class PetAnimationLabel(QLabel):
    """支持动画的宠物标签"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 200)
        self.animation_offset = 0
        self.animation_direction = 1
        self.animation_speed = 2
        
        # 呼吸动画定时器
        self.breath_timer = QTimer(self)
        self.breath_timer.timeout.connect(self._update_breath)
        self.breath_timer.start(50)
        
    def _update_breath(self):
        """更新呼吸动画"""
        self.animation_offset += self.animation_speed * self.animation_direction
        if abs(self.animation_offset) > 5:
            self.animation_direction *= -1
        self.update()
    
    def paintEvent(self, event):
        """自定义绘制"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制宠物（用圆形占位，后续可替换为图片）
        center_x = self.width() // 2
        center_y = self.height() // 2 + self.animation_offset
        radius = min(self.width(), self.height()) // 2 - 10
        
        # 阴影
        shadow_color = QColor(0, 0, 0, 40)
        painter.setBrush(QBrush(shadow_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center_x, center_y + 5, radius, radius)
        
        # 宠物身体
        gradient = QColor(102, 126, 234)  # 蓝紫色
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(78, 101, 208), 2))
        painter.drawEllipse(center_x, center_y, radius, radius)
        
        # 眼睛
        eye_color = QColor(255, 255, 255)
        painter.setBrush(QBrush(eye_color))
        painter.setPen(Qt.PenStyle.NoPen)
        
        # 左眼
        painter.drawEllipse(center_x - 30, center_y - 20, 15, 15)
        # 右眼
        painter.drawEllipse(center_x + 30, center_y - 20, 15, 15)
        
        # 眼珠
        pupil_color = QColor(50, 50, 50)
        painter.setBrush(QBrush(pupil_color))
        painter.drawEllipse(center_x - 28, center_y - 18, 8, 8)
        painter.drawEllipse(center_x + 32, center_y - 18, 8, 8)
        
        # 嘴巴
        painter.setPen(QPen(QColor(255, 255, 255), 3))
        painter.drawLine(center_x - 15, center_y + 20, center_x, center_y + 30)
        painter.drawLine(center_x, center_y + 30, center_x + 15, center_y + 20)
        
        # 腮红
        blush_color = QColor(255, 182, 193, 150)
        painter.setBrush(QBrush(blush_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center_x - 50, center_y + 5, 12, 8)
        painter.drawEllipse(center_x + 38, center_y + 5, 12, 8)


class PetWidget(QWidget):
    """宠物显示组件"""
    
    # 信号
    interaction_requested = pyqtSignal(str)  # 请求互动
    mood_changed = pyqtSignal(PetMood)  # 心情变化
    
    def __init__(self, pet: Pet, parent=None):
        super().__init__(parent)
        self.pet = pet
        self.setup_ui()
        self.setup_animations()
        self.update_display()
        
    def setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 宠物名称标签
        self.name_label = QLabel(self.pet.name)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                font-weight: bold;
                color: {MacOSTheme.TEXT_PRIMARY};
                padding: 10px;
                background: {MacOSTheme.BG_SECONDARY};
                border-radius: 12px;
            }}
        """)
        layout.addWidget(self.name_label)
        
        # 宠物动画显示区
        self.pet_animation = PetAnimationLabel(self)
        self.pet_animation.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.pet_animation, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 等级标签
        self.level_label = QLabel(f"Lv.{self.pet.level}")
        self.level_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.level_label.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                color: {MacOSTheme.PRIMARY_BLUE};
                font-weight: bold;
                padding: 5px 15px;
                background: {MacOSTheme.BG_TERTIARY};
                border-radius: 8px;
            }}
        """)
        layout.addWidget(self.level_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 心情标签
        self.mood_label = QLabel(self.pet.mood.value)
        self.mood_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mood_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                color: {MacOSTheme.TEXT_SECONDARY};
                padding: 5px;
            }}
        """)
        layout.addWidget(self.mood_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 成长阶段
        self.stage_label = QLabel(f"{self.pet.growth_stage}")
        self.stage_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stage_label.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                color: {MacOSTheme.TEXT_TERTIARY};
            }}
        """)
        layout.addWidget(self.stage_label, alignment=Qt.AlignmentFlag.AlignCenter)
    
    def setup_animations(self):
        """设置动画"""
        # 升级动画
        self.level_animation = QPropertyAnimation(self, b"pos")
        self.level_animation.setDuration(500)
        self.level_animation.setEasingCurve(QEasingCurve.Type.OutBounce)
    
    def update_display(self):
        """更新显示"""
        self.name_label.setText(self.pet.name)
        self.level_label.setText(f"Lv.{self.pet.level}")
        self.mood_label.setText(self.pet.mood.value)
        self.stage_label.setText(self.pet.growth_stage)
        
        # 根据心情更新颜色
        mood_colors = {
            PetMood.HAPPY: MacOSTheme.PRIMARY_GREEN,
            PetMood.NORMAL: MacOSTheme.PRIMARY_BLUE,
            PetMood.SAD: "#5AC8FA",
            PetMood.ANGRY: MacOSTheme.PRIMARY_RED,
            PetMood.SLEEPY: MacOSTheme.PRIMARY_ORANGE,
        }
        color = mood_colors.get(self.pet.mood, MacOSTheme.PRIMARY_BLUE)
        self.mood_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                color: {color};
                padding: 5px;
                font-weight: bold;
            }}
        """)
    
    def play_interaction_effect(self, effect_type: str):
        """播放互动特效
        
        Args:
            effect_type: 特效类型 (feed, play, train, clean)
        """
        # 简单的缩放动画
        self.pet_animation.scale_animation = QPropertyAnimation(
            self.pet_animation, b"geometry"
        )
        # 这里可以添加更复杂的动画效果
        print(f"播放 {effect_type} 特效")
    
    def set_mood(self, mood: PetMood):
        """设置心情"""
        if self.pet.mood != mood:
            self.pet.mood = mood
            self.mood_changed.emit(mood)
            self.update_display()
    
    def level_up_effect(self):
        """升级特效"""
        # 可以添加粒子效果、闪光等
        self.update_display()


class ProgressBar(QWidget):
    """macOS 风格进度条"""
    
    def __init__(self, value: int = 50, max_value: int = 100, color: str = None, parent=None):
        super().__init__(parent)
        self.value = value
        self.max_value = max_value
        self.color = color or MacOSTheme.PRIMARY_BLUE
        self.setFixedHeight(20)
        
    def paintEvent(self, event):
        """绘制进度条"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 背景
        painter.setBrush(QBrush(QColor(MacOSTheme.BG_TERTIARY)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 10, 10)
        
        # 进度
        if self.max_value > 0:
            width = int((self.value / self.max_value) * (self.width() - 4))
            progress_rect = self.rect().adjusted(2, 2, -self.width() + width + 2, -2)
            
            # 渐变色
            gradient = QColor(self.color)
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(progress_rect, 8, 8)
    
    def set_value(self, value: int):
        """设置进度值"""
        self.value = max(0, min(self.max_value, value))
        self.update()
