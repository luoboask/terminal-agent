"""
任务系统 - 每日任务和剧情任务
"""
import random
from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass


class QuestType(Enum):
    """任务类型"""
    DAILY = "每日任务"
    STORY = "剧情任务"
    ACHIEVEMENT = "成就任务"
    SPECIAL = "特殊任务"


class QuestStatus(Enum):
    """任务状态"""
    LOCKED = "未解锁"
    ACTIVE = "进行中"
    COMPLETED = "已完成"
    CLAIMED = "已领取奖励"
    FAILED = "失败"


@dataclass
class Quest:
    """任务类"""
    id: str
    name: str
    description: str
    quest_type: QuestType
    objective: str  # 任务目标描述
    target_count: int  # 目标数量
    current_count: int = 0
    status: QuestStatus = QuestStatus.LOCKED
    reward_coins: int = 50
    reward_exp: int = 30
    reward_items: List[str] = None
    unlock_level: int = 1
    deadline: Optional[datetime] = None
    
    def __post_init__(self):
        if self.reward_items is None:
            self.reward_items = []
    
    def progress(self, amount: int = 1):
        """推进任务进度"""
        if self.status in [QuestStatus.ACTIVE]:
            self.current_count += amount
            if self.current_count >= self.target_count:
                self.status = QuestStatus.COMPLETED
                return True
        return False
    
    def reset(self):
        """重置任务（用于每日任务）"""
        self.current_count = 0
        self.status = QuestStatus.ACTIVE
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'quest_type': self.quest_type.value,
            'objective': self.objective,
            'target_count': self.target_count,
            'current_count': self.current_count,
            'status': self.status.value,
            'reward_coins': self.reward_coins,
            'reward_exp': self.reward_exp,
            'reward_items': self.reward_items,
            'unlock_level': self.unlock_level,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Quest':
        """从字典创建"""
        return cls(
            id=data['id'],
            name=data['name'],
            description=data['description'],
            quest_type=QuestType(data['quest_type']),
            objective=data['objective'],
            target_count=data['target_count'],
            current_count=data.get('current_count', 0),
            status=QuestStatus(data.get('status', 'LOCKED')),
            reward_coins=data.get('reward_coins', 50),
            reward_exp=data.get('reward_exp', 30),
            reward_items=data.get('reward_items', []),
            unlock_level=data.get('unlock_level', 1),
        )


class QuestSystem:
    """任务系统"""
    
    # 预设任务模板
    DAILY_QUESTS = [
        Quest(
            id="daily_feed",
            name="喂食时间",
            description="每天喂食宠物",
            quest_type=QuestType.DAILY,
            objective="喂食",
            target_count=3,
            reward_coins=30,
            reward_exp=20,
        ),
        Quest(
            id="daily_play",
            name="快乐时光",
            description="每天和宠物玩耍",
            quest_type=QuestType.DAILY,
            objective="玩耍",
            target_count=5,
            reward_coins=40,
            reward_exp=25,
        ),
        Quest(
            id="daily_train",
            name="刻苦训练",
            description="每天训练宠物",
            quest_type=QuestType.DAILY,
            objective="训练",
            target_count=2,
            reward_coins=50,
            reward_exp=40,
        ),
        Quest(
            id="daily_clean",
            name="清洁小能手",
            description="每天给宠物洗澡",
            quest_type=QuestType.DAILY,
            objective="洗澡",
            target_count=1,
            reward_coins=35,
            reward_exp=25,
        ),
    ]
    
    STORY_QUESTS = [
        Quest(
            id="story_001",
            name="新的开始",
            description="欢迎来到宠物世界！和你的宠物打个招呼吧。",
            quest_type=QuestType.STORY,
            objective="互动",
            target_count=1,
            reward_coins=100,
            reward_exp=50,
            unlock_level=1,
            reward_items=["新手礼包"],
        ),
        Quest(
            id="story_002",
            name="第一次喂食",
            description="你的宠物饿了，喂它一些食物吧。",
            quest_type=QuestType.STORY,
            objective="喂食",
            target_count=1,
            reward_coins=50,
            reward_exp=30,
            unlock_level=1,
            reward_items=["狗粮 x3"],
        ),
        Quest(
            id="story_003",
            name="成长之路",
            description="让你的宠物达到 5 级。",
            quest_type=QuestType.STORY,
            objective="升级",
            target_count=5,
            reward_coins=200,
            reward_exp=100,
            unlock_level=1,
            reward_items=["成长药剂"],
        ),
        Quest(
            id="story_004",
            name="社交达人",
            description="拜访其他玩家的宠物 3 次。",
            quest_type=QuestType.STORY,
            objective="拜访",
            target_count=3,
            reward_coins=150,
            reward_exp=80,
            unlock_level=5,
        ),
    ]
    
    def __init__(self):
        self.quests: Dict[str, Quest] = {}
        self.completed_quests: List[str] = []
        self.daily_reset_time: Optional[datetime] = None
        self._init_default_quests()
    
    def _init_default_quests(self):
        """初始化默认任务"""
        # 添加每日任务
        for quest in self.DAILY_QUESTS:
            new_quest = Quest(
                id=quest.id,
                name=quest.name,
                description=quest.description,
                quest_type=quest.quest_type,
                objective=quest.objective,
                target_count=quest.target_count,
                reward_coins=quest.reward_coins,
                reward_exp=quest.reward_exp,
                status=QuestStatus.ACTIVE,
            )
            self.quests[new_quest.id] = new_quest
        
        # 添加剧情任务（初始只解锁第一个）
        for quest in self.STORY_QUESTS[:1]:
            new_quest = Quest(
                id=quest.id,
                name=quest.name,
                description=quest.description,
                quest_type=quest.quest_type,
                objective=quest.objective,
                target_count=quest.target_count,
                reward_coins=quest.reward_coins,
                reward_exp=quest.reward_exp,
                reward_items=quest.reward_items,
                unlock_level=quest.unlock_level,
                status=QuestStatus.ACTIVE,
            )
            self.quests[new_quest.id] = new_quest
    
    def get_quest(self, quest_id: str) -> Optional[Quest]:
        """获取任务"""
        return self.quests.get(quest_id)
    
    def get_active_quests(self, quest_type: Optional[QuestType] = None) -> List[Quest]:
        """获取进行中的任务"""
        quests = [q for q in self.quests.values() 
                  if q.status in [QuestStatus.ACTIVE, QuestStatus.COMPLETED]]
        if quest_type:
            quests = [q for q in quests if q.quest_type == quest_type]
        return quests
    
    def get_claimable_quests(self) -> List[Quest]:
        """获取可领取奖励的任务"""
        return [q for q in self.quests.values() 
                if q.status == QuestStatus.COMPLETED]
    
    def progress_quest(self, quest_id: str, amount: int = 1) -> bool:
        """推进任务进度"""
        quest = self.quests.get(quest_id)
        if quest and quest.status == QuestStatus.ACTIVE:
            return quest.progress(amount)
        return False
    
    def progress_by_action(self, action: str, amount: int = 1) -> List[str]:
        """根据动作推进相关任务"""
        completed = []
        action_map = {
            'feed': ['daily_feed', 'story_002'],
            'play': ['daily_play'],
            'train': ['daily_train'],
            'clean': ['daily_clean'],
            'interact': ['story_001'],
            'level_up': ['story_003'],
            'visit': ['story_004'],
        }
        
        for quest_id in action_map.get(action, []):
            if self.progress_quest(quest_id, amount):
                completed.append(quest_id)
                # 检查是否解锁下一个剧情任务
                self._check_story_progression()
        
        return completed
    
    def _check_story_progression(self):
        """检查是否解锁新的剧情任务"""
        completed_story = [q for q in self.quests.values() 
                          if q.quest_type == QuestType.STORY 
                          and q.status == QuestStatus.COMPLETED]
        
        # 根据已完成的任务解锁新任务
        for quest in self.STORY_QUESTS:
            if quest.id not in self.quests:
                # 检查前置任务是否完成
                prev_quest_idx = self.STORY_QUESTS.index(quest) - 1
                if prev_quest_idx < 0 or \
                   self.STORY_QUESTS[prev_quest_idx].id in self.completed_quests or \
                   self.quests.get(self.STORY_QUESTS[prev_quest_idx].id, 
                                   Quest("", "", "", QuestType.STORY, "", 0)).status == QuestStatus.COMPLETED:
                    # 解锁新任务
                    new_quest = Quest(
                        id=quest.id,
                        name=quest.name,
                        description=quest.description,
                        quest_type=quest.quest_type,
                        objective=quest.objective,
                        target_count=quest.target_count,
                        reward_coins=quest.reward_coins,
                        reward_exp=quest.reward_exp,
                        reward_items=quest.reward_items,
                        unlock_level=quest.unlock_level,
                        status=QuestStatus.ACTIVE,
                    )
                    self.quests[new_quest.id] = new_quest
    
    def claim_reward(self, quest_id: str) -> Optional[dict]:
        """领取任务奖励"""
        quest = self.quests.get(quest_id)
        if not quest or quest.status != QuestStatus.COMPLETED:
            return None
        
        quest.status = QuestStatus.CLAIMED
        self.completed_quests.append(quest_id)
        
        return {
            'coins': quest.reward_coins,
            'exp': quest.reward_exp,
            'items': quest.reward_items,
        }
    
    def reset_daily_quests(self):
        """重置每日任务"""
        now = datetime.now()
        if self.daily_reset_time and now - self.daily_reset_time < timedelta(days=1):
            return False
        
        for quest in self.quests.values():
            if quest.quest_type == QuestType.DAILY:
                quest.reset()
        
        self.daily_reset_time = now
        return True
    
    def check_level_unlock(self, level: int):
        """检查等级解锁新任务"""
        for quest in self.STORY_QUESTS:
            if quest.id not in self.quests and level >= quest.unlock_level:
                # 检查前置任务
                prev_quest_idx = self.STORY_QUESTS.index(quest) - 1
                if prev_quest_idx < 0 or \
                   self.quests.get(self.STORY_QUESTS[prev_quest_idx].id) and \
                   self.quests[self.STORY_QUESTS[prev_quest_idx].id].status == QuestStatus.COMPLETED:
                    new_quest = Quest(
                        id=quest.id,
                        name=quest.name,
                        description=quest.description,
                        quest_type=quest.quest_type,
                        objective=quest.objective,
                        target_count=quest.target_count,
                        reward_coins=quest.reward_coins,
                        reward_exp=quest.reward_exp,
                        reward_items=quest.reward_items,
                        unlock_level=quest.unlock_level,
                        status=QuestStatus.ACTIVE,
                    )
                    self.quests[new_quest.id] = new_quest
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'quests': {qid: q.to_dict() for qid, q in self.quests.items()},
            'completed_quests': self.completed_quests,
            'daily_reset_time': self.daily_reset_time.isoformat() if self.daily_reset_time else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'QuestSystem':
        """从字典创建"""
        system = cls()
        system.quests = {qid: Quest.from_dict(qdata) for qid, qdata in data.get('quests', {}).items()}
        system.completed_quests = data.get('completed_quests', [])
        if data.get('daily_reset_time'):
            system.daily_reset_time = datetime.fromisoformat(data['daily_reset_time'])
        return system


if __name__ == "__main__":
    # 测试任务系统
    quest_system = QuestSystem()
    
    print("=== 任务系统测试 ===\n")
    
    # 显示所有任务
    print("当前任务：")
    for quest in quest_system.get_active_quests():
        print(f"  {quest.name}: {quest.current_count}/{quest.target_count} - {quest.status.value}")
    
    # 推进任务
    print("\n喂食宠物...")
    completed = quest_system.progress_by_action('feed', 1)
    print(f"完成的任务：{completed}")
    
    # 显示更新后的任务
    print("\n更新后的任务：")
    for quest in quest_system.get_active_quests():
        print(f"  {quest.name}: {quest.current_count}/{quest.target_count} - {quest.status.value}")
    
    # 领取奖励
    claimable = quest_system.get_claimable_quests()
    if claimable:
        print(f"\n可领取奖励的任务：{[q.name for q in claimable]}")
