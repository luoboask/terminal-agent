#!/usr/bin/env python3
"""
背包界面组件 - macOS 风格
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, 
    QFrame, QPushButton, QGridLayout, QDialog, QDialogButtonBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from .styles import MacOSTheme


class InventoryItemCard(QFrame):
    """单个物品卡片"""
    
    use_clicked = pyqtSignal(object)  # 使用物品信号
    
    def __init__(self, item, count: int = 1):
        super().__init__()
        self.item = item
        self.count = count
        self.setup_ui()
        
    def setup_ui(self):
        """设置 UI"""
        self.setFixedSize(100, 120)
        self.setObjectName("inventoryItemCard")
        self.setStyleSheet(MacOSTheme.inventory_item_card())
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 物品图标
        self.icon_label = QLabel(getattr(self.item, 'icon', '📦'))
        self.icon_label.setFont(QFont("Arial", 36))
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.icon_label)
        
        # 物品名称
        self.name_label = QLabel(getattr(self.item, 'name', '未知物品'))
        self.name_label.setFont(QFont("SF Pro Text", 11))
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setWordWrap(True)
        layout.addWidget(self.name_label)
        
        # 数量
        self.count_label = QLabel(f"x{self.count}")
        self.count_label.setFont(QFont("SF Pro Text", 10, QFont.Weight.Bold))
        self.count_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.count_label.setStyleSheet("color: #8E8E93;")
        layout.addWidget(self.count_label)
        
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.use_clicked.emit(self.item)


class InventoryWidget(QWidget):
    """背包界面组件"""
    
    item_used = pyqtSignal(object)  # 物品使用信号
    
    def __init__(self, inventory: list = None):
        super().__init__()
        self.inventory = inventory or []
        self.setup_ui()
        
    def setup_ui(self):
        """设置 UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("🎒 背包")
        title_label.setFont(QFont("SF Pro Text", 20, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #000000;")
        main_layout.addWidget(title_label)
        
        # 物品网格
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setObjectName("inventoryScroll")
        scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollArea QWidget {
                background: transparent;
            }
        """)
        
        # 网格容器
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(12)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll.setWidget(self.grid_container)
        main_layout.addWidget(scroll, 1)
        
        # 刷新显示
        self.refresh_display()
        
    def refresh_display(self):
        """刷新物品显示"""
        # 清空现有物品
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 添加物品卡片
        if not self.inventory:
            empty_label = QLabel("背包是空的")
            empty_label.setFont(QFont("SF Pro Text", 14))
            empty_label.setStyleSheet("color: #8E8E93;")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid_layout.addWidget(empty_label, 0, 0, 1, 3)
            return
        
        # 统计物品数量
        item_counts = {}
        for item in self.inventory:
            item_id = getattr(item, 'id', str(item))
            if item_id not in item_counts:
                item_counts[item_id] = {'item': item, 'count': 0}
            item_counts[item_id]['count'] += 1
        
        # 创建物品卡片
        row, col = 0, 0
        max_cols = 5
        for item_data in item_counts.values():
            card = InventoryItemCard(item_data['item'], item_data['count'])
            card.use_clicked.connect(self.on_item_used)
            self.grid_layout.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
                
    def on_item_used(self, item):
        """物品使用处理"""
        self.item_used.emit(item)
        
    def update_inventory(self, inventory: list):
        """更新背包数据"""
        self.inventory = inventory
        self.refresh_display()
