"""
数据存储模块 - 负责宠物的持久化存储
"""
import json
import os
from datetime import datetime


class PetStorage:
    """宠物数据存储类"""
    
    def __init__(self, save_path="pet_save.json"):
        """
        初始化存储器
        
        Args:
            save_path: 保存文件路径
        """
        self.save_path = save_path
    
    def save(self, pet_data):
        """
        保存宠物数据
        
        Args:
            pet_data: 宠物数据字典
        """
        try:
            with open(self.save_path, 'w', encoding='utf-8') as f:
                json.dump(pet_data, f, indent=2, ensure_ascii=False, default=str)
            return True
        except Exception as e:
            print(f"保存失败：{e}")
            return False
    
    def load(self):
        """
        加载宠物数据
        
        Returns:
            dict: 宠物数据，如果不存在返回 None
        """
        if not os.path.exists(self.save_path):
            return None
        
        try:
            with open(self.save_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"加载失败：{e}")
            return None
    
    def delete(self):
        """删除存档"""
        if os.path.exists(self.save_path):
            os.remove(self.save_path)
            return True
        return False
    
    def exists(self):
        """检查是否存在存档"""
        return os.path.exists(self.save_path)
