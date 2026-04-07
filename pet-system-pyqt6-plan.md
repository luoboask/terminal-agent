# PyQt6 macOS 风格宠物系统改进方案

**创建日期**: 2026-04-08  
**当前版本**: 控制台版本  
**目标版本**: PyQt6 GUI 版本

---

## 📊 当前系统分析

### 现有模块

| 模块 | 行数 | 功能 | PyQt6 适配难度 |
|------|------|------|---------------|
| pet.py | 440 | 宠物核心逻辑 | ⭐ 简单（逻辑不变） |
| ui.py | 424 | 控制台 UI | ⭐⭐⭐⭐⭐ 完全重写 |
| main.py | 236 | 主程序 | ⭐⭐⭐ 中等修改 |
| shop.py | 355 | 商店系统 | ⭐⭐ 简单修改 |
| events.py | 372 | 随机事件 | ⭐ 简单修改 |
| quests.py | 408 | 任务系统 | ⭐⭐ 中等修改 |
| achievements.py | 207 | 成就系统 | ⭐ 简单修改 |
| decoration.py | 379 | 装饰系统 | ⭐⭐ 中等修改 |
| weather.py | 181 | 天气系统 | ⭐ 简单修改 |
| social.py | 265 | 社交功能 | ⭐⭐ 中等修改 |
| storage.py | 74 | 数据存储 | ⭐ 保持不变 |

---

## 🎨 PyQt6 UI 设计方案

### 1. 主窗口设计

```python
# ui_main_window.py
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class PetGameWindow(QMainWindow):
    """宠物游戏主窗口"""
    
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('宠物养成游戏 - macOS 风格')
        self.setGeometry(100, 100, 900, 700)
        
        # 创建标签页
        tabs = QTabWidget()
        tabs.addTab(MainTab(), '🏠 主页')
        tabs.addTab(InteractionTab(), '🎮 互动')
        tabs.addTab(ShopTab(), '🏪 商店')
        tabs.addTab(StatusTab(), '📊 状态')
        
        self.setCentralWidget(tabs)
        
        # macOS 风格
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f7;
            }
            QTabWidget::pane {
                border: 1px solid #d1d1d1;
                background-color: white;
                border-radius: 10px;
            }
        """)
```

### 2. 宠物显示组件

```python
# ui_pet_display.py
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QProgressBar
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont

class PetDisplayWidget(QWidget):
    """宠物显示组件"""
    
    def __init__(self, pet):
        super().__init__()
        self.pet = pet
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        
        # 宠物图片
        self.pet_image = QLabel()
        self.pet_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pet_image.setPixmap(QPixmap('assets/pet_normal.png'))
        
        # 宠物名字
        self.name_label = QLabel(self.pet.name)
        self.name_label.setFont(QFont('SF Pro Display', 24, QFont.Weight.Bold))
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 状态进度条
        self.hp_bar = QProgressBar()
        self.hp_bar.setValue(self.pet.health)
        self.hp_bar.setStyleSheet("""
            QProgressBar {
                border-radius: 5px;
                background-color: #e5e5e5;
            }
            QProgressBar::chunk {
                background-color: #34c759;
                border-radius: 5px;
            }
        """)
        
        layout.addWidget(self.pet_image)
        layout.addWidget(self.name_label)
        layout.addWidget(self.hp_bar)
        
        self.setLayout(layout)
```

### 3. 互动界面

```python
# ui_interaction.py
from PyQt6.QtWidgets import QWidget, QPushButton, QGridLayout, QLabel
from PyQt6.QtCore import pyqtSignal

class InteractionPanel(QWidget):
    """互动面板"""
    
    # 信号
    feed_signal = pyqtSignal()
    play_signal = pyqtSignal()
    train_signal = pyqtSignal()
    rest_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        layout = QGridLayout()
        layout.setSpacing(15)
        
        # 互动按钮
        buttons = [
            ('🍖 喂食', self.feed_signal),
            ('🎾 玩耍', self.play_signal),
            ('📚 训练', self.train_signal),
            ('😴 休息', self.rest_signal),
        ]
        
        for i, (text, signal) in enumerate(buttons):
            btn = QPushButton(text)
            btn.setFixedSize(150, 80)
            btn.clicked.connect(signal)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    border: 1px solid #d1d1d1;
                    border-radius: 10px;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: #007aff;
                    color: white;
                }
            """)
            
            row = i // 2
            col = i % 2
            layout.addWidget(btn, row, col)
        
        self.setLayout(layout)
```

### 4. 商店界面

```python
# ui_shop.py
from PyQt6.QtWidgets import QWidget, QScrollArea, QGridLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt

class ShopWidget(QWidget):
    """商店组件"""
    
    def __init__(self, shop):
        super().__init__()
        self.shop = shop
        self.initUI()
        
    def initUI(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        container = QWidget()
        layout = QGridLayout()
        
        # 商品列表
        for i, item in enumerate(self.shop.items):
            item_widget = self.create_item_widget(item)
            row = i // 3
            col = i % 3
            layout.addWidget(item_widget, row, col)
        
        container.setLayout(layout)
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)
        
    def create_item_widget(self, item):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 商品图片
        image = QLabel()
        image.setPixmap(QPixmap(f'assets/{item.image}'))
        image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 商品名称
        name = QLabel(item.name)
        name.setStyleSheet('font-weight: bold; font-size: 14px;')
        
        # 价格
        price = QLabel(f'💰 {item.price}')
        price.setStyleSheet('color: #34c759;')
        
        # 购买按钮
        buy_btn = QPushButton('购买')
        buy_btn.setStyleSheet("""
            QPushButton {
                background-color: #007aff;
                color: white;
                border-radius: 5px;
                padding: 5px 15px;
            }
        """)
        
        layout.addWidget(image)
        layout.addWidget(name)
        layout.addWidget(price)
        layout.addWidget(buy_btn)
        
        widget.setLayout(layout)
        return widget
```

---

## 📁 新的目录结构

```
pet-system-pyqt6/
├── main.py                 # 主程序入口
├── requirements.txt        # 依赖：PyQt6
├── assets/                 # 资源文件
│   ├── images/            # 图片资源
│   │   ├── pet_normal.png
│   │   ├── pet_happy.png
│   │   └── ...
│   ├── sounds/            # 音效资源
│   └── icons/             # 图标资源
├── core/                   # 核心逻辑（复用现有代码）
│   ├── pet.py             # 宠物类
│   ├── shop.py            # 商店系统
│   ├── events.py          # 事件系统
│   └── storage.py         # 存储系统
└── ui/                     # PyQt6 UI
    ├── main_window.py      # 主窗口
    ├── pet_display.py      # 宠物显示
    ├── interaction.py      # 互动界面
    ├── shop.py            # 商店界面
    ├── status.py          # 状态界面
    └── widgets/           # 自定义组件
        ├── progress_bar.py
        └── buttons.py
```

---

## 🛠️ 实施步骤

### 阶段 1：环境准备（1 天）
- [ ] 安装 PyQt6: `pip install PyQt6`
- [ ] 准备素材资源（图片、音效）
- [ ] 创建项目结构

### 阶段 2：核心 UI（3 天）
- [ ] 主窗口框架
- [ ] 宠物显示组件
- [ ] 状态显示组件
- [ ] 基础样式（macOS 风格）

### 阶段 3：功能界面（3 天）
- [ ] 互动界面
- [ ] 商店界面
- [ ] 任务界面
- [ ] 成就界面

### 阶段 4：集成测试（2 天）
- [ ] 连接核心逻辑
- [ ] 测试所有功能
- [ ] 修复 bug
- [ ] 性能优化

### 阶段 5：美化完善（2 天）
- [ ] 添加动画效果
- [ ] 添加音效
- [ ] 优化 UI 细节
- [ ] 最终测试

**总计**: 约 11 个工作日

---

## 🎨 macOS 风格设计要点

### 颜色方案
```python
# macOS 风格颜色
COLORS = {
    'primary': '#007aff',      # 蓝色
    'success': '#34c759',      # 绿色
    'warning': '#ff9500',      # 橙色
    'danger': '#ff3b30',       # 红色
    'background': '#f5f5f7',   # 浅灰背景
    'card': '#ffffff',         # 白色卡片
    'text': '#1d1d1f',         # 深色文字
    'secondary_text': '#86868b' # 浅色文字
}
```

### 圆角和阴影
```python
# 圆角样式
border-radius: 10px;

# 阴影样式
box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
```

### 字体
```python
# 使用系统字体
font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display';
```

---

## 📊 代码量预估

| 模块 | 新增代码行数 | 复用代码行数 |
|------|------------|------------|
| UI 组件 | ~1500 行 | 0 行 |
| 核心逻辑 | 0 行 | ~2500 行 |
| 资源文件 | N/A | N/A |
| **总计** | **~1500 行** | **~2500 行** |

---

## 🚀 扩展功能建议

### 短期（1-2 个月）
1. 🎵 添加音效和背景音乐
2. 🎬 添加宠物动画（QPropertyAnimation）
3. 🌙 深色模式支持
4. 📱 触控板手势支持

### 中期（3-6 个月）
1. 🏆 成就系统可视化
2. 📊 统计图表（使用 PyQtGraph）
3. 🌐 多语言支持
4. 💾 云存档（iCloud 集成）

### 长期（6-12 个月）
1. 📱 macOS App Store 发布
2. 🎮 宠物小游戏集合
3. 🏠 多宠物管理
4. 🧬 宠物繁殖系统

---

## ⚠️ 注意事项

1. **性能优化**
   - 使用 QPixmapCache 缓存图片
   - 避免频繁重绘
   - 使用信号槽优化事件处理

2. **跨平台兼容**
   - 虽然目标是 macOS，但代码应保持跨平台能力
   - 使用相对路径
   - 测试 Windows/Linux 兼容性

3. **用户体验**
   - 保持界面简洁
   - 响应速度 < 100ms
   - 提供操作反馈

---

**创建完成!** 🎉
