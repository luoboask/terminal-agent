#!/usr/bin/env python3
"""
macOS 风格主题样式定义
"""
from dataclasses import dataclass


@dataclass
class MacOSTheme:
    """macOS 设计主题"""
    
    # ============ 颜色方案 ============
    # 主色调
    PRIMARY_BLUE: str = "#007AFF"
    PRIMARY_GREEN: str = "#34C759"
    PRIMARY_RED: str = "#FF3B30"
    PRIMARY_ORANGE: str = "#FF9500"
    PRIMARY_YELLOW: str = "#FFCC00"
    PRIMARY_PURPLE: str = "#AF52DE"
    PRIMARY_PINK: str = "#FF2D55"
    
    # 背景色
    BG_PRIMARY: str = "#FFFFFF"
    BG_SECONDARY: str = "#F2F2F7"
    BG_TERTIARY: str = "#E5E5EA"
    BG_DARK: str = "#1C1C1E"
    
    # 文字色
    TEXT_PRIMARY: str = "#000000"
    TEXT_SECONDARY: str = "#3C3C43"
    TEXT_TERTIARY: str = "#8E8E93"
    TEXT_WHITE: str = "#FFFFFF"
    TEXT_DISABLED: str = "#C7C7CC"
    
    # 状态颜色
    HEALTH_HIGH: str = "#34C759"
    HEALTH_MEDIUM: str = "#FFCC00"
    HEALTH_LOW: str = "#FF3B30"
    
    # 边框色
    BORDER_LIGHT: str = "#D1D1D6"
    BORDER_FOCUS: str = "#007AFF"
    
    # 阴影色
    SHADOW_LIGHT: str = "rgba(0, 0, 0, 0.08)"
    SHADOW_MEDIUM: str = "rgba(0, 0, 0, 0.12)"
    SHADOW_HEAVY: str = "rgba(0, 0, 0, 0.16)"
    
    # ============ 圆角规范 ============
    RADIUS_LARGE: int = 16
    RADIUS_MEDIUM: int = 12
    RADIUS_SMALL: int = 8
    RADIUS_BUTTON: int = 10
    RADIUS_PROGRESS: int = 6
    
    # ============ 间距规范 ============
    SPACING_XS: int = 4
    SPACING_S: int = 8
    SPACING_M: int = 16
    SPACING_L: int = 24
    SPACING_XL: int = 32
    
    # ============ 字体规范 ============
    FONT_FAMILY: str = "-apple-system, BlinkMacSystemFont, 'Helvetica Neue', 'PingFang SC', 'Microsoft YaHei', sans-serif"
    FONT_SIZE_XS: int = 11
    FONT_SIZE_S: int = 13
    FONT_SIZE_M: int = 15
    FONT_SIZE_L: int = 17
    FONT_SIZE_XL: int = 20
    FONT_SIZE_XXL: int = 24
    
    # ============ 动画时长 ============
    ANIMATION_FAST: int = 150
    ANIMATION_NORMAL: int = 250
    ANIMATION_SLOW: int = 350
    
    # ============ QSS 样式表 ============
    
    @staticmethod
    def get_main_window_style() -> str:
        """主窗口样式"""
        return f"""
        QMainWindow {{
            background-color: {MacOSTheme.BG_SECONDARY};
        }}
        """
    
    @staticmethod
    def get_central_widget_style() -> str:
        """中央容器样式"""
        return f"""
        QWidget#centralWidget {{
            background-color: {MacOSTheme.BG_PRIMARY};
            border-radius: {MacOSTheme.RADIUS_LARGE}px;
        }}
        """
    
    @staticmethod
    def get_card_style() -> str:
        """卡片容器样式"""
        return f"""
        QWidget#card {{
            background-color: {MacOSTheme.BG_PRIMARY};
            border-radius: {MacOSTheme.RADIUS_MEDIUM}px;
            border: 1px solid {MacOSTheme.BORDER_LIGHT};
        }}
        QWidget#card:hover {{
            border: 1px solid {MacOSTheme.PRIMARY_BLUE};
        }}
        """
    
    @staticmethod
    def get_button_style(primary: bool = False) -> str:
        """按钮样式"""
        if primary:
            return f"""
            QPushButton {{
                background-color: {MacOSTheme.PRIMARY_BLUE};
                color: {MacOSTheme.TEXT_WHITE};
                border: none;
                border-radius: {MacOSTheme.RADIUS_BUTTON}px;
                padding: {MacOSTheme.SPACING_S}px {MacOSTheme.SPACING_M}px;
                font-size: {MacOSTheme.FONT_SIZE_M}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #0062CC;
            }}
            QPushButton:pressed {{
                background-color: #0056B3;
            }}
            QPushButton:disabled {{
                background-color: {MacOSTheme.BG_TERTIARY};
                color: {MacOSTheme.TEXT_DISABLED};
            }}
            """
        else:
            return f"""
            QPushButton {{
                background-color: {MacOSTheme.BG_SECONDARY};
                color: {MacOSTheme.PRIMARY_BLUE};
                border: 1px solid {MacOSTheme.BORDER_LIGHT};
                border-radius: {MacOSTheme.RADIUS_BUTTON}px;
                padding: {MacOSTheme.SPACING_S}px {MacOSTheme.SPACING_M}px;
                font-size: {MacOSTheme.FONT_SIZE_M}px;
            }}
            QPushButton:hover {{
                background-color: {MacOSTheme.BG_TERTIARY};
                border-color: {MacOSTheme.PRIMARY_BLUE};
            }}
            QPushButton:pressed {{
                background-color: {MacOSTheme.BORDER_LIGHT};
            }}
            """
    
    @staticmethod
    def get_action_button_style() -> str:
        """动作按钮样式（大图标按钮）"""
        return f"""
        QPushButton#actionButton {{
            background-color: {MacOSTheme.BG_PRIMARY};
            border: 2px solid {MacOSTheme.BORDER_LIGHT};
            border-radius: {MacOSTheme.RADIUS_LARGE}px;
            padding: {MacOSTheme.SPACING_L}px;
            min-width: 100px;
            min-height: 100px;
        }}
        QPushButton#actionButton:hover {{
            border-color: {MacOSTheme.PRIMARY_BLUE};
            background-color: {MacOSTheme.BG_SECONDARY};
        }}
        QPushButton#actionButton:pressed {{
            background-color: {MacOSTheme.BG_TERTIARY};
        }}
        """
    
    @staticmethod
    def get_progress_bar_style() -> str:
        """进度条样式"""
        return f"""
        QProgressBar {{
            background-color: {MacOSTheme.BG_TERTIARY};
            border: none;
            border-radius: {MacOSTheme.RADIUS_PROGRESS}px;
            height: 12px;
            text-align: center;
        }}
        QProgressBar::chunk {{
            background-color: {MacOSTheme.PRIMARY_BLUE};
            border-radius: {MacOSTheme.RADIUS_PROGRESS}px;
        }}
        """
    
    @staticmethod
    def get_status_bar_style() -> str:
        """状态栏样式"""
        return f"""
        QWidget#statusBar {{
            background-color: {MacOSTheme.BG_PRIMARY};
            border-top: 1px solid {MacOSTheme.BORDER_LIGHT};
            padding: {MacOSTheme.SPACING_M}px;
        }}
        QLabel#statusLabel {{
            color: {MacOSTheme.TEXT_PRIMARY};
            font-size: {MacOSTheme.FONT_SIZE_S}px;
        }}
        """
    
    @staticmethod
    def get_label_style() -> str:
        """标签样式"""
        return f"""
        QLabel {{
            color: {MacOSTheme.TEXT_PRIMARY};
            font-size: {MacOSTheme.FONT_SIZE_M}px;
        }}
        QLabel#titleLabel {{
            font-size: {MacOSTheme.FONT_SIZE_XL}px;
            font-weight: bold;
            color: {MacOSTheme.TEXT_PRIMARY};
        }}
        QLabel#subtitleLabel {{
            font-size: {MacOSTheme.FONT_SIZE_S}px;
            color: {MacOSTheme.TEXT_TERTIARY};
        }}
        """
    
    @staticmethod
    def get_scroll_area_style() -> str:
        """滚动区域样式"""
        return f"""
        QScrollArea {{
            background-color: transparent;
            border: none;
        }}
        QScrollBar:vertical {{
            background-color: {MacOSTheme.BG_TERTIARY};
            width: 8px;
            border-radius: 4px;
        }}
        QScrollBar::handle:vertical {{
            background-color: {MacOSTheme.TEXT_TERTIARY};
            border-radius: 4px;
            min-height: 20px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {MacOSTheme.TEXT_SECONDARY};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        """
    
    @staticmethod
    def get_dialog_style() -> str:
        """对话框样式"""
        return f"""
        QDialog {{
            background-color: {MacOSTheme.BG_PRIMARY};
            border-radius: {MacOSTheme.RADIUS_LARGE}px;
        }}
        QLabel#dialogTitle {{
            font-size: {MacOSTheme.FONT_SIZE_L}px;
            font-weight: bold;
            color: {MacOSTheme.TEXT_PRIMARY};
        }}
        """
    
    @staticmethod
    def get_list_widget_style() -> str:
        """列表组件样式"""
        return f"""
        QListWidget {{
            background-color: {MacOSTheme.BG_PRIMARY};
            border: 1px solid {MacOSTheme.BORDER_LIGHT};
            border-radius: {MacOSTheme.RADIUS_MEDIUM}px;
            outline: none;
        }}
        QListWidget::item {{
            padding: {MacOSTheme.SPACING_M}px;
            border-bottom: 1px solid {MacOSTheme.BG_TERTIARY};
        }}
        QListWidget::item:selected {{
            background-color: {MacOSTheme.PRIMARY_BLUE};
            color: {MacOSTheme.TEXT_WHITE};
        }}
        QListWidget::item:hover {{
            background-color: {MacOSTheme.BG_SECONDARY};
        }}
        """
    
    @staticmethod
    def get_tab_widget_style() -> str:
        """标签页组件样式"""
        return f"""
        QTabWidget::pane {{
            border: 1px solid {MacOSTheme.BORDER_LIGHT};
            border-radius: {MacOSTheme.RADIUS_MEDIUM}px;
            background-color: {MacOSTheme.BG_PRIMARY};
        }}
        QTabBar::tab {{
            background-color: {MacOSTheme.BG_SECONDARY};
            padding: {MacOSTheme.SPACING_S}px {MacOSTheme.SPACING_M}px;
            margin-right: 2px;
            border-top-left-radius: {MacOSTheme.RADIUS_SMALL}px;
            border-top-right-radius: {MacOSTheme.RADIUS_SMALL}px;
        }}
        QTabBar::tab:selected {{
            background-color: {MacOSTheme.BG_PRIMARY};
            border-bottom: 2px solid {MacOSTheme.PRIMARY_BLUE};
        }}
        QTabBar::tab:hover:!selected {{
            background-color: {MacOSTheme.BG_TERTIARY};
        }}
        """
    
    @staticmethod
    def get_tool_tip_style() -> str:
        """工具提示样式"""
        return f"""
        QToolTip {{
            background-color: {MacOSTheme.BG_DARK};
            color: {MacOSTheme.TEXT_WHITE};
            border: none;
            border-radius: {MacOSTheme.RADIUS_SMALL}px;
            padding: {MacOSTheme.SPACING_S}px {MacOSTheme.SPACING_M}px;
            font-size: {MacOSTheme.FONT_SIZE_S}px;
        }}
        """
    
    @staticmethod
    def get_header_style() -> str:
        """标题栏样式"""
        return f"""
        QWidget#header {{
            background-color: {MacOSTheme.BG_PRIMARY};
            border-bottom: 1px solid {MacOSTheme.BORDER_LIGHT};
            padding: {MacOSTheme.SPACING_M}px;
        }}
        QLabel#headerTitle {{
            font-size: {MacOSTheme.FONT_SIZE_XL}px;
            font-weight: bold;
            color: {MacOSTheme.TEXT_PRIMARY};
        }}
        """
    
    @staticmethod
    def get_inventory_grid_style() -> str:
        """背包网格样式"""
        return f"""
        QWidget#inventoryGrid {{
            background-color: {MacOSTheme.BG_PRIMARY};
            border: 1px solid {MacOSTheme.BORDER_LIGHT};
            border-radius: {MacOSTheme.RADIUS_MEDIUM}px;
        }}
        QLabel#inventorySlot {{
            background-color: {MacOSTheme.BG_SECONDARY};
            border: 1px solid {MacOSTheme.BORDER_LIGHT};
            border-radius: {MacOSTheme.RADIUS_SMALL}px;
            min-width: 60px;
            min-height: 60px;
        }}
        QLabel#inventorySlot:hover {{
            border-color: {MacOSTheme.PRIMARY_BLUE};
            background-color: {MacOSTheme.BG_TERTIARY};
        }}
        """
    
    @staticmethod
    def get_shop_item_style() -> str:
        """商店物品样式"""
        return f"""
        QWidget#shopItem {{
            background-color: {MacOSTheme.BG_PRIMARY};
            border: 1px solid {MacOSTheme.BORDER_LIGHT};
            border-radius: {MacOSTheme.RADIUS_MEDIUM}px;
            padding: {MacOSTheme.SPACING_M}px;
        }}
        QWidget#shopItem:hover {{
            border-color: {MacOSTheme.PRIMARY_BLUE};
            background-color: {MacOSTheme.BG_SECONDARY};
        }}
        QLabel#shopItemName {{
            font-size: {MacOSTheme.FONT_SIZE_M}px;
            font-weight: bold;
            color: {MacOSTheme.TEXT_PRIMARY};
        }}
        QLabel#shopItemPrice {{
            font-size: {MacOSTheme.FONT_SIZE_S}px;
            color: {MacOSTheme.PRIMARY_ORANGE};
        }}
        """
    
    @classmethod
    def get_all_styles(cls) -> str:
        """获取所有样式"""
        return (
            cls.get_main_window_style() +
            cls.get_central_widget_style() +
            cls.get_card_style() +
            cls.get_button_style() +
            cls.get_action_button_style() +
            cls.get_progress_bar_style() +
            cls.get_status_bar_style() +
            cls.get_label_style() +
            cls.get_scroll_area_style() +
            cls.get_dialog_style() +
            cls.get_list_widget_style() +
            cls.get_tab_widget_style() +
            cls.get_tool_tip_style() +
            cls.get_header_style() +
            cls.get_inventory_grid_style() +
            cls.get_shop_item_style()
        )
