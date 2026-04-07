#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机器人大战游戏 - 启动脚本
"""

import sys
import os

# 确保当前目录在路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import main

if __name__ == "__main__":
    main()
