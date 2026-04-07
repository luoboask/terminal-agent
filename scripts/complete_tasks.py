#!/usr/bin/env python3
"""
批量完成任务脚本
用法：
  python scripts/complete_tasks.py --all          # 完成所有待处理任务
  python scripts/complete_tasks.py --pattern "坦克"  # 完成包含"坦克"的任务
  python scripts/complete_tasks.py --ids id1 id2   # 完成指定 ID 的任务
"""

import json
import os
import argparse
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

def complete_tasks(pattern=None, task_ids=None, complete_all=False):
    """批量完成任务"""
    tasks = load_tasks()
    
    print(f"📊 当前任务总数：{len(tasks)}")
    
    completed_count = 0
    now = datetime.now().timestamp() * 1000
    
    for task in tasks:
        # 跳过已完成的
        if task.get('status') in ['completed', 'failed']:
            continue
        
        # 检查是否匹配
        should_complete = False
        
        if complete_all:
            should_complete = True
        elif task_ids and task.get('id') in task_ids:
            should_complete = True
        elif pattern and pattern in task.get('title', ''):
            should_complete = True
        
        if should_complete:
            task['status'] = 'completed'
            task['completed_at'] = now
            task['updated_at'] = now
            completed_count += 1
            
            status_icon = {
                'low': '🟢',
                'medium': '🟡',
                'high': '🔴'
            }.get(task.get('priority'), '⚪')
            
            print(f"✅ {status_icon} #{task.get('id', 'unknown')[-10:]}: {task.get('title', '无标题')}")
    
    save_tasks(tasks)
    
    print(f"\n🎉 完成：{completed_count} 个任务")
    
    # 显示剩余待处理任务
    pending = [t for t in tasks if t.get('status') == 'pending']
    print(f"\n📋 剩余待处理：{len(pending)} 个任务")
    
    for task in pending:
        status_icon = {
            'low': '🟢',
            'medium': '🟡',
            'high': '🔴'
        }.get(task.get('priority'), '⚪')
        print(f"⚪ {status_icon} #{task.get('id', 'unknown')[-10:]}: {task.get('title', '无标题')}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='批量完成任务')
    parser.add_argument('--all', action='store_true', help='完成所有待处理任务')
    parser.add_argument('--pattern', type=str, help='完成标题包含指定文本的任务')
    parser.add_argument('--ids', type=str, nargs='+', help='完成指定 ID 的任务')
    
    args = parser.parse_args()
    
    if not any([args.all, args.pattern, args.ids]):
        print("❌ 请指定完成条件:")
        print("  --all          完成所有待处理任务")
        print("  --pattern 文本  完成标题包含文本的任务")
        print("  --ids id1 id2   完成指定 ID 的任务")
        print("\n示例:")
        print("  python scripts/complete_tasks.py --all")
        print("  python scripts/complete_tasks.py --pattern 坦克")
        print("  python scripts/complete_tasks.py --ids task_xxx task_yyy")
    else:
        complete_tasks(
            pattern=args.pattern,
            task_ids=args.ids,
            complete_all=args.all
        )
