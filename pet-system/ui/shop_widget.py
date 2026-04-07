#!/usr/bin/env python3
"""
商店界面组件 - macOS 风格
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QFrame, QGridLayout, QSpacerItem, QSizePolicy,
    QDialog, QDialogButtonBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from .styles import MacOSTheme


class ShopItemCard(QFrame):
    """商店物品卡片"""
    
    purchase_requested = pyqtSignal(object)  # 发送 item 对象
    
    def __init__(self, item, parent=None):
        super().__init__(parent)
        self.item = item
        self.setup_ui()
        
    def setup_ui(self):
        """设置 UI"""
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {MacOSTheme.BG_PRIMARY};
                border-radius: 12px;
                border: 1px solid {MacOSTheme.BORDER};
                padding: 12px;
            }}
            QFrame:hover {{
                border: 1px solid {MacOSTheme.PRIMARY_BLUE};
                background-color: {MacOSTheme.BG_HOVER};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # 物品图标和名称
        icon_label = QLabel(self.item.icon)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFont(QFont("Arial", 36))
        layout.addWidget(icon_label)
        
        # 名称
        name_label = QLabel(self.item.name)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setFont(QFont("SF Pro Text", 14, QFont.Weight.Bold))
        name_label.setStyleSheet(f"color: {MacOSTheme.TEXT_PRIMARY};")
        layout.addWidget(name_label)
        
        # 描述
        desc_label = QLabel(self.item.description)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setFont(QFont("SF Pro Text", 11))
        desc_label.setStyleSheet(f"color: {MacOSTheme.TEXT_SECONDARY};")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # 价格
        price_label = QLabel(f"💰 {self.item.price}")
        price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        price_label.setFont(QFont("SF Pro Text", 13, QFont.Weight.Bold))
        price_label.setStyleSheet(f"color: {MacOSTheme.PRIMARY_ORANGE};")
        layout.addWidget(price_label)
        
        # 购买按钮
        buy_btn = QPushButton("购买")
        buy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        buy_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MacOSTheme.PRIMARY_BLUE};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {MacOSTheme.hover_color(MacOSTheme.PRIMARY_BLUE, 0.8)};
            }}
            QPushButton:pressed {{
                background-color: {MacOSTheme.hover_color(MacOSTheme.PRIMARY_BLUE, 0.6)};
            }}
        """)
        buy_btn.clicked.connect(lambda: self.purchase_requested.emit(self.item))
        layout.addWidget(buy_btn)


class ShopWidget(QWidget):
    """商店界面组件"""
    
    item_purchased = pyqtSignal(object)  # 发送购买的物品
    
    def __init__(self, shop, pet, parent=None):
        super().__init__(parent)
        self.shop = shop
        self.pet = pet
        self.setup_ui()
        
    def setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题栏
        header_layout = QHBoxLayout()
        
        title = QLabel("🏪 宠物商店")
        title.setFont(QFont("SF Pro Text", 24, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {MacOSTheme.TEXT_PRIMARY};")
        header_layout.addWidget(title)
        
        # 金币显示
        self.coins_label = QLabel(f"💰 {self.pet.coins}")
        self.coins_label.setFont(QFont("SF Pro Text", 18, QFont.Weight.Bold))
        self.coins_label.setStyleSheet(f"color: {MacOSTheme.PRIMARY_ORANGE};")
        header_layout.addStretch()
        header_layout.addWidget(self.coins_label)
        
        layout.addLayout(header_layout)
        
        # 分类标签
        category_layout = QHBoxLayout()
        category_layout.setSpacing(8)
        
        self.category_buttons = {}
        categories = [
            ("all", "全部", "📦"),
            ("food", "食物", "🍎"),
            ("toy", "玩具", "🎾"),
            ("medicine", "药品", "💊"),
            ("decoration", "装饰", "🎀"),
        ]
        
        for cat_id, cat_name, icon in categories:
            btn = QPushButton(f"{icon} {cat_name}")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {MacOSTheme.BG_SECONDARY};
                    color: {MacOSTheme.TEXT_SECONDARY};
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-size: 13px;
                }}
                QPushButton:checked {{
                    background-color: {MacOSTheme.PRIMARY_BLUE};
                    color: white;
                }}
                QPushButton:hover:!checked {{
                    background-color: {MacOSTheme.BG_TERTIARY};
                }}
            """)
            btn.clicked.connect(lambda checked, cid=cat_id: self.filter_items(cid))
            category_layout.addWidget(btn)
            self.category_buttons[cat_id] = btn
        
        # 默认选中全部
        self.category_buttons["all"].setChecked(True)
        
        layout.addLayout(category_layout)
        
        # 商品网格
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameStyle(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        
        self.items_container = QWidget()
        self.items_layout = QGridLayout(self.items_container)
        self.items_layout.setSpacing(16)
        self.items_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll.setWidget(self.items_container)
        layout.addWidget(scroll)
        
        # 关闭按钮
        close_btn = QPushButton("关闭商店")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {MacOSTheme.BG_SECONDARY};
                color: {MacOSTheme.TEXT_SECONDARY};
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {MacOSTheme.BG_TERTIARY};
            }}
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 加载商品
        self.load_items()
        
    def filter_items(self, category: str):
        """筛选商品"""
        # 更新按钮状态
        for btn_id, btn in self.category_buttons.items():
            if btn_id != category:
                btn.setChecked(False)
        
        self.load_items(category)
        
    def load_items(self, category: str = "all"):
        """加载商品列表"""
        # 清空现有商品
        while self.items_layout.count():
            item = self.items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 获取商品
        items = self.shop.get_all_items()
        if category != "all":
            type_map = {
                "food": "食物",
                "toy": "玩具",
                "medicine": "药品",
                "decoration": "装饰",
            }
            items = [item for item in items if item.item_type.value == type_map.get(category)]
        
        # 添加商品卡片
        row, col = 0, 0
        max_cols = 4
        
        for item in items:
            card = ShopItemCard(item)
            card.purchase_requested.connect(self.on_purchase)
            self.items_layout.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # 添加弹性空间
        if col > 0:
            for c in range(col, max_cols):
                spacer = QSpacerItem(100, 100, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                self.items_layout.addItem(spacer, row, c)
    
    def on_purchase(self, item):
        """处理购买"""
        if self.pet.coins >= item.price:
            self.pet.coins -= item.price
            self.pet.inventory.append(item)
            self.coins_label.setText(f"💰 {self.pet.coins}")
            self.item_purchased.emit(item)
        else:
            # 金币不足提示
            from .dialogs import MessageDialog
            dialog = MessageDialog(
                "金币不足",
                f"需要 {item.price} 金币，但你只有 {self.pet.coins} 金币",
                "error",
                self
            )
            dialog.exec()
    
    def update_coins(self):
        """更新金币显示"""
        self.coins_label.setText(f"💰 {self.pet.coins}")
