#!/usr/bin/env python3
"""
Soul Memory Module E: 熱度衰減器 (Heat Decay)

實現記憶熱度追蹤與衰減算法，優化清理策略

Author: Soul Memory System
Date: 2026-02-17
"""

import json
import os
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path


@dataclass
class MemoryHeat:
    """記憶熱度數據"""
    memory_id: str           # 記憶 ID
    content_hash: str        # 內容 hash
    priority: str = "N"      # 優先級 C/I/N
    created_time: float = 0  # 創建時間戳
    last_accessed: float = 0 # 最後訪問時間
    access_count: int = 0    # 訪問次數
    heat_score: float = 1.0  # 當前熱度分數
    decay_rate: float = 0.1  # 衰減率


@dataclass
class DecayConfig:
    """衰減配置"""
    # 不同優先級的衰減率（每日）
    critical_decay: float = 0.0     # Critical 永不衰減
    important_decay: float = 0.02   # Important 慢衰減
    normal_decay: float = 0.1       # Normal 快衰減
    
    # 熱度閾值
    archive_threshold: float = 0.2   # 低於此值建議歸檔
    delete_threshold: float = 0.05   # 低於此值建議刪除
    
    # 訪問加分
    access_boost: float = 0.3        # 每次訪問加分
    max_heat: float = 2.0            # 最大熱度上限


class HeatDecayManager:
    """
    熱度衰減管理器
    
    功能：
    1. 追蹤記憶訪問頻率
    2. 計算熱度衰減
    3. 提供清理建議
    4. 自動歸動歸檔/刪除低熱度記憶
    """
    
    # 預設衰減配置
    DEFAULT_CONFIG = DecayConfig()
    
    def __init__(self,
                 config_path: str = "/root/.openclaw/workspace/memory-system/config/heat_data.json",
                 config: Optional[DecayConfig] = None):
        """
        初始化熱度衰減管理器
        
        Args:
            config_path: 熱度數據存儲路徑
            config: 衰減配置
        """
        self.config_path = config_path
        self.config = config or self.DEFAULT_CONFIG
        self.heat_data: Dict[str, MemoryHeat] = {}
        
        # 確保目錄存在
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        # 載入現有數據
        self._load_data()
    
    def _load_data(self):
        """載入熱度數據"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for mem_id, heat_data in data.get('memories', {}).items():
                        self.heat_data[mem_id] = MemoryHeat(**heat_data)
            except Exception:
                pass
    
    def _save_data(self):
        """保存熱度數據"""
        data = {
            'memories': {
                mem_id: {
                    'memory_id': h.memory_id,
                    'content_hash': h.content_hash,
                    'priority': h.priority,
                    'created_time': h.created_time,
                    'last_accessed': h.last_accessed,
                    'access_count': h.access_count,
                    'heat_score': h.heat_score,
                    'decay_rate': h.decay_rate
                }
                for mem_id, h in self.heat_data.items()
            },
            'last_updated': time.time()
        }
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def register_memory(self, memory_id: str, content_hash: str, priority: str = "N"):
        """
        註冊新記憶
        
        Args:
            memory_id: 記憶 ID
            content_hash: 內容 hash
            priority: 優先級
        """
        now = time.time()
        
        # 根據優先級設置衰減率
        decay_rate = self._get_decay_rate(priority)
        
        # Critical 記憶起始熱度較高
        initial_heat = 1.5 if priority == "C" else 1.0
        
        self.heat_data[memory_id] = MemoryHeat(
            memory_id=memory_id,
            content_hash=content_hash,
            priority=priority,
            created_time=now,
            last_accessed=now,
            access_count=1,
            heat_score=initial_heat,
            decay_rate=decay_rate
        )
        
        self._save_data()
    
    def record_access(self, memory_id: str) -> float:
        """
        記錄記憶訪問
        
        Args:
            memory_id: 記憶 ID
            
        Returns:
            更新後的熱度分數
        """
        if memory_id not in self.heat_data:
            return 0.0
        
        heat = self.heat_data[memory_id]
        now = time.time()
        
        # 更新訪問統計
        heat.last_accessed = now
        heat.access_count += 1
        
        # 訪問加分
        heat.heat_score += self.config.access_boost
        heat.heat_score = min(heat.heat_score, self.config.max_heat)
        
        self._save_data()
        return heat.heat_score
    
    def apply_decay(self, memory_id: Optional[str] = None) -> Dict[str, float]:
        """
        應用熱度衰減
        
        Args:
            memory_id: 特定記憶 ID（None = 全部）
            
        Returns:
            更新後的熱度分數字典
        """
        now = time.time()
        day_seconds = 86400  # 一天的秒數
        
        results = {}
        
        targets = [memory_id] if memory_id else list(self.heat_data.keys())
        
        for mid in targets:
            if mid not in self.heat_data:
                continue
            
            heat = self.heat_data[mid]
            
            # 計算自上次更新以來的天數
            days_passed = (now - heat.last_accessed) / day_seconds
            
            # 應用衰減（指數衰減）
            # heat = heat * (1 - decay_rate) ^ days
            decay_factor = (1 - heat.decay_rate) ** days_passed
            heat.heat_score *= decay_factor
            
            # 確保最低熱度
            heat.heat_score = max(heat.heat_score, 0.0)
            
            results[mid] = heat.heat_score
        
        self._save_data()
        return results
    
    def get_cleanup_suggestions(self) -> Tuple[List[str], List[str]]:
        """
        獲取清理建議
        
        Returns:
            (歸檔列表, 刪除列表)
        """
        # 先應用衰減
        self.apply_decay()
        
        archive_list = []
        delete_list = []
        
        for mem_id, heat in self.heat_data.items():
            # Critical 永不刪除
            if heat.priority == "C":
                continue
            
            if heat.heat_score < self.config.delete_threshold:
                delete_list.append(mem_id)
            elif heat.heat_score < self.config.archive_threshold:
                archive_list.append(mem_id)
        
        return archive_list, delete_list
    
    def get_hot_memories(self, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        獲取最熱門的記憶
        
        Args:
            top_k: 返回數量
            
        Returns:
            [(memory_id, heat_score), ...]
        """
        sorted_memories = sorted(
            self.heat_data.items(),
            key=lambda x: x[1].heat_score,
            reverse=True
        )
        return [(mid, h.heat_score) for mid, h in sorted_memories[:top_k]]
    
    def get_memory_stats(self, memory_id: str) -> Optional[Dict]:
        """
        獲取記憶統計
        
        Args:
            memory_id: 記憶 ID
            
        Returns:
            統計字典
        """
        if memory_id not in self.heat_data:
            return None
        
        heat = self.heat_data[memory_id]
        now = time.time()
        
        return {
            'memory_id': memory_id,
            'priority': heat.priority,
            'heat_score': heat.heat_score,
            'access_count': heat.access_count,
            'age_days': (now - heat.created_time) / 86400,
            'last_accessed_days_ago': (now - heat.last_accessed) / 86400,
            'decay_rate': heat.decay_rate
        }
    
    def boost_memory(self, memory_id: str, boost_amount: float = 0.5) -> bool:
        """
        手動提升記憶熱度
        
        Args:
            memory_id: 記憶 ID
            boost_amount: 提升量
            
        Returns:
            是否成功
        """
        if memory_id not in self.heat_data:
            return False
        
        heat = self.heat_data[memory_id]
        heat.heat_score = min(heat.heat_score + boost_amount, self.config.max_heat)
        
        self._save_data()
        return True
    
    def update_priority(self, memory_id: str, new_priority: str) -> bool:
        """
        更新記憶優先級
        
        Args:
            memory_id: 記憶 ID
            new_priority: 新優先級
            
        Returns:
            是否成功
        """
        if memory_id not in self.heat_data:
            return False
        
        heat = self.heat_data[memory_id]
        heat.priority = new_priority
        heat.decay_rate = self._get_decay_rate(new_priority)
        
        # Critical 提升熱度
        if new_priority == "C":
            heat.heat_score = max(heat.heat_score, 1.5)
        
        self._save_data()
        return True
    
    def _get_decay_rate(self, priority: str) -> float:
        """根據優先級獲取衰減率"""
        rates = {
            "C": self.config.critical_decay,
            "I": self.config.important_decay,
            "N": self.config.normal_decay
        }
        return rates.get(priority, self.config.normal_decay)
    
    def get_summary(self) -> Dict:
        """獲取熱度摘要"""
        if not self.heat_data:
            return {
                'total_memories': 0,
                'avg_heat': 0,
                'by_priority': {}
            }
        
        by_priority = {'C': [], 'I': [], 'N': []}
        total_heat = 0
        
        for heat in self.heat_data.values():
            by_priority[heat.priority].append(heat.heat_score)
            total_heat += heat.heat_score
        
        return {
            'total_memories': len(self.heat_data),
            'avg_heat': total_heat / len(self.heat_data),
            'by_priority': {
                p: {
                    'count': len(heats),
                    'avg_heat': sum(heats) / len(heats) if heats else 0
                }
                for p, heats in by_priority.items()
            }
        }


# 便捷函數
def get_memory_heat(memory_id: str) -> float:
    """獲取記憶熱度的便捷函數"""
    manager = HeatDecayManager()
    if memory_id in manager.heat_data:
        return manager.heat_data[memory_id].heat_score
    return 0.0


# 模組測試
if __name__ == "__main__":
    print("=" * 60)
    print("Soul Memory Module E: 熱度衰減器測試")
    print("=" * 60)
    
    manager = HeatDecayManager()
    
    # 註冊測試記憶
    test_memories = [
        ("mem_001", "hash_abc", "C"),  # Critical
        ("mem_002", "hash_def", "I"),  # Important
        ("mem_003", "hash_ghi", "N"),  # Normal
    ]
    
    print("\n註冊測試記憶:")
    for mid, h, p in test_memories:
        manager.register_memory(mid, h, p)
        print(f"  {mid} (優先級 {p}) - 初始熱度: {manager.heat_data[mid].heat_score:.2f}")
    
    # 模擬訪問
    print("\n模擬訪問:")
    for _ in range(3):
        manager.record_access("mem_002")
    print(f"  mem_002 訪問 3 次後熱度: {manager.heat_data['mem_002'].heat_score:.2f}")
    
    # 應用衰減（模擬 10 天）
    print("\n模擬 10 天衰減:")
    for mid in ["mem_001", "mem_002", "mem_003"]:
        # 手動調整 last_accessed 模擬時間流逝
        manager.heat_data[mid].last_accessed = time.time() - (10 * 86400)
    
    decay_results = manager.apply_decay()
    for mid, heat in decay_results.items():
        print(f"  {mid} ({manager.heat_data[mid].priority}): {heat:.4f}")
    
    # 清理建議
    archive, delete = manager.get_cleanup_suggestions()
    print(f"\n清理建議:")
    print(f"  歸檔: {archive}")
    print(f"  刪除: {delete}")
    
    # 摘要
    summary = manager.get_summary()
    print(f"\n熱度摘要:")
    print(f"  總記憶數: {summary['total_memories']}")
    print(f"  平均熱度: {summary['avg_heat']:.2f}")
    
    print("\n" + "=" * 60)
    print("測試完成")
