#!/usr/bin/env python3
"""
清理任务列表脚本
用法：python scripts/cleanup_tasks.py
"""

import json
import os
from datetime import datetime

TASKS_FILE = '.source-deploy-tasks.json'

def load_tasks():
    """加载任务"""
    if not os.path.exists(TASKS_FILE):
        return []
    
    with open(TASKS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_tasks(tasks):
    """保存任务"""
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

def cleanup_tasks():
    """清理任务列表"""
    tasks = load_tasks()
    
    print(f"📊 清理前：{len(tasks)} 个任务")
    
    # 1. 删除已完成超过 24 小时的任务
    now = datetime.now().timestamp() * 1000
    active_tasks = []
    
    for task in tasks:
        # 保留未完成的任务
        if task.get('status') not in ['completed', 'failed']:
            active_tasks.append(task)
            continue
        
        # 保留最近 24 小时完成的的任务
        updated_at = task.get('updated_at', 0)
        if now - updated_at < 24 * 60 * 60 * 1000:  # 24 小时
            active_tasks.append(task)
    
    # 2. 删除名称为 undefined 的任务
    active_tasks = [t for t in active_tasks if t.get('title') and t.get('title') != 'undefined']
    
    # 3. 删除重复的任务（相同标题）
    seen_titles = set()
    unique_tasks = []
    for task in active_tasks:
        title = task.get('title', '')
        if title not in seen_titles:
            seen_titles.add(title)
            unique_tasks.append(task)
    
    print(f"📊 清理后：{len(unique_tasks)} 个任务")
    print(f"🗑️  删除：{len(tasks) - len(unique_tasks)} 个任务")
    
    save_tasks(unique_tasks)
    
    # 显示剩余任务
    print("\n📋 剩余任务:")
    for task in unique_tasks:
        status_icon = {
            'pending': '⚪',
            'in_progress': '⏳',
            'completed': '✅',
            'failed': '❌'
        }.get(task.get('status'), '⚪')
        
        priority_icon = {
            'low': '🟢',
            'medium': '🟡',
            'high': '🔴'
        }.get(task.get('priority'), '⚪')
        
        print(f"{status_icon} {priority_icon} #{task.get('id', 'unknown')[-10:]}: {task.get('title', '无标题')}")

if __name__ == "__main__":
    cleanup_tasks()
