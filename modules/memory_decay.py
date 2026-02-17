#!/usr/bin/env python3
"""
Soul Memory Module E: 熱度衰減器 (Memory Decay)

時間衰減 + 訪問頻率算法，優化記憶清理策略

Author: Soul Memory System
Date: 2026-02-17
"""

import json
import time
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import math


@dataclass
class MemoryHeat:
    """記憶熱度數據"""
    memory_id: str           # 記憶 ID
    content_hash: str        # 內容 hash
    priority: str = "N"      # 優先級 (C/I/N)
    created_at: float = 0    # 創建時間戳
    last_accessed: float = 0 # 最後訪問時間
    access_count: int = 0    # 訪問次數
    decay_score: float = 1.0 # 衰減分數 (0-1)
    
    def to_dict(self) -> dict:
        return {
            'memory_id': self.memory_id,
            'content_hash': self.content_hash,
            'priority': self.priority,
            'created_at': self.created_at,
            'last_accessed': self.last_accessed,
            'access_count': self.access_count,
            'decay_score': self.decay_score
        }
    
    @classmethod
    def from_dict(cls, d: dict) -> 'MemoryHeat':
        return cls(
            memory_id=d['memory_id'],
            content_hash=d['content_hash'],
            priority=d.get('priority', 'N'),
            created_at=d.get('created_at', 0),
            last_accessed=d.get('last_accessed', 0),
            access_count=d.get('access_count', 0),
            decay_score=d.get('decay_score', 1.0)
        )


class MemoryDecay:
    """
    記憶熱度衰減器
    
    衰減算法：
    - Critical: 永不衰減 (decay_rate = 0)
    - Important: 慢衰減 (半衰期 90 天)
    - Normal: 快衰減 (半衰期 30 天)
    
    訪問加分：
    - 每次訪問增加 decay_score
    - 加分幅度與優先級相關
    """
    
    # 衰減參數
    DECAY_RATES = {
        "C": 0.0,        # Critical: 永不衰減
        "I": 0.0077,     # Important: 半衰期 ~90 天 (ln(2)/90)
        "N": 0.0231,     # Normal: 半衰期 ~30 天 (ln(2)/30)
    }
    
    # 訪問加分
    ACCESS_BONUS = {
        "C": 0.1,   # Critical 每次訪問 +0.1
        "I": 0.15,  # Important 每次訪問 +0.15
        "N": 0.2,   # Normal 每次訪問 +0.2
    }
    
    # 分數上限
    MAX_SCORE = 1.5
    MIN_SCORE = 0.0
    
    def __init__(self, 
                 cache_path: str = "/root/.openclaw/workspace/memory-system/cache/heat_map.json"):
        """
        初始化熱度衰減器
        
        Args:
            cache_path: 熱度快取路徑
        """
        self.cache_path = cache_path
        self.heat_map: Dict[str, MemoryHeat] = {}
        
        # 確保目錄存在
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        
        # 載入快取
        self._load_cache()
    
    def _load_cache(self):
        """載入熱度快取"""
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, 'r', encoding='utf-8') as f:
                    cached = json.load(f)
                    self.heat_map = {
                        k: MemoryHeat.from_dict(v) 
                        for k, v in cached.get('heat_map', {}).items()
                    }
            except Exception:
                pass
    
    def _save_cache(self):
        """保存熱度快取"""
        data = {
            'last_updated': time.time(),
            'heat_map': {
                k: v.to_dict() 
                for k, v in self.heat_map.items()
            }
        }
        with open(self.cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def register_memory(self, memory_id: str, content: str, priority: str = "N"):
        """
        註冊新記憶
        
        Args:
            memory_id: 記憶 ID
            content: 記憶內容
            priority: 優先級
        """
        content_hash = self._hash_content(content)
        
        # 檢查是否已存在（基於內容 hash）
        for heat in self.heat_map.values():
            if heat.content_hash == content_hash:
                # 更新訪問時間
                self.record_access(heat.memory_id)
                return
        
        # 創建新熱度記錄
        now = time.time()
        self.heat_map[memory_id] = MemoryHeat(
            memory_id=memory_id,
            content_hash=content_hash,
            priority=priority.upper(),
            created_at=now,
            last_accessed=now,
            access_count=1,
            decay_score=1.0
        )
        
        self._save_cache()
    
    def record_access(self, memory_id: str):
        """
        記錄記憶訪問
        
        Args:
            memory_id: 記憶 ID
        """
        if memory_id not in self.heat_map:
            return
        
        heat = self.heat_map[memory_id]
        heat.last_accessed = time.time()
        heat.access_count += 1
        
        # 訪問加分
        bonus = self.ACCESS_BONUS.get(heat.priority, 0.1)
        heat.decay_score = min(heat.decay_score + bonus, self.MAX_SCORE)
        
        self._save_cache()
    
    def compute_decay(self, memory_id: str) -> float:
        """
        計算記憶衰減分數
        
        Args:
            memory_id: 記憶 ID
            
        Returns:
            衰減後的分數 (0-1)
        """
        if memory_id not in self.heat_map:
            return 1.0
        
        heat = self.heat_map[memory_id]
        decay_rate = self.DECAY_RATES.get(heat.priority, 0.0231)
        
        # Critical 不衰減
        if decay_rate == 0:
            return heat.decay_score
        
        # 計算時間差（天）
        days_since_access = (time.time() - heat.last_accessed) / 86400
        
        # 指數衰減
        decayed = heat.decay_score * math.exp(-decay_rate * days_since_access)
        
        return max(decayed, self.MIN_SCORE)
    
    def update_all_decay(self):
        """更新所有記憶的衰減分數"""
        for memory_id in self.heat_map:
            self.heat_map[memory_id].decay_score = self.compute_decay(memory_id)
        self._save_cache()
    
    def get_memories_to_archive(self, threshold: float = 0.3) -> List[Tuple[str, float]]:
        """
        獲取建議歸檔的記憶
        
        Args:
            threshold: 衰減閾值
            
        Returns:
            [(memory_id, decay_score), ...]
        """
        to_archive = []
        
        for memory_id, heat in self.heat_map.items():
            # Critical 永不歸檔
            if heat.priority == "C":
                continue
            
            decay_score = self.compute_decay(memory_id)
            if decay_score < threshold:
                to_archive.append((memory_id, decay_score))
        
        # 按衰減分數排序（最低優先）
        to_archive.sort(key=lambda x: x[1])
        return to_archive
    
    def get_hot_memories(self, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        獲取熱門記憶
        
        Args:
            top_k: 返回數量
            
        Returns:
            [(memory_id, decay_score), ...]
        """
        scored = [
            (mid, self.compute_decay(mid))
            for mid in self.heat_map
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]
    
    def get_stats(self) -> dict:
        """獲取熱度統計"""
        stats = {
            'total_memories': len(self.heat_map),
            'by_priority': {'C': 0, 'I': 0, 'N': 0},
            'avg_decay_score': 0,
            'avg_access_count': 0,
        }
        
        if not self.heat_map:
            return stats
        
        total_decay = 0
        total_access = 0
        
        for heat in self.heat_map.values():
            stats['by_priority'][heat.priority] = stats['by_priority'].get(heat.priority, 0) + 1
            total_decay += self.compute_decay(heat.memory_id)
            total_access += heat.access_count
        
        stats['avg_decay_score'] = total_decay / len(self.heat_map)
        stats['avg_access_count'] = total_access / len(self.heat_map)
        
        return stats
    
    def _hash_content(self, content: str) -> str:
        """計算內容 hash"""
        import hashlib
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def clear_cache(self):
        """清除快取"""
        self.heat_map = {}
        if os.path.exists(self.cache_path):
            os.remove(self.cache_path)


# 便捷函數
def get_decay_score(memory_id: str) -> float:
    """獲取記憶衰減分數"""
    decay = MemoryDecay()
    return decay.compute_decay(memory_id)


def get_archive_candidates(threshold: float = 0.3) -> List[Tuple[str, float]]:
    """獲取建議歸檔的記憶"""
    decay = MemoryDecay()
    return decay.get_memories_to_archive(threshold)


# 模組測試
if __name__ == "__main__":
    print("=" * 60)
    print("Soul Memory Module E: 熱度衰減器測試")
    print("=" * 60)
    
    decay = MemoryDecay()
    
    # 測試註冊記憶
    test_memories = [
        ("mem_001", "[C] QST 暗物質理論核心公式", "C"),
        ("mem_002", "[I] OpenClaw 配置討論", "I"),
        ("mem_003", "今天天氣不錯", "N"),
    ]
    
    print("\n註冊測試記憶:")
    for mid, content, priority in test_memories:
        decay.register_memory(mid, content, priority)
        print(f"  {mid}: {content} (優先級: {priority})")
    
    # 模擬時間流逝
    print("\n模擬 30 天後的衰減:")
    for mid, _, _ in test_memories:
        # 模擬時間流逝（修改 last_accessed）
        if mid in decay.heat_map:
            heat = decay.heat_map[mid]
            heat.last_accessed -= 30 * 86400  # 往前推 30 天
            score = decay.compute_decay(mid)
            print(f"  {mid} ({heat.priority}): 衰減分數 = {score:.3f}")
    
    # 顯示統計
    stats = decay.get_stats()
    print(f"\n統計:")
    print(f"  總記憶數: {stats['total_memories']}")
    print(f"  按優先級: {stats['by_priority']}")
    
    print("\n" + "=" * 60)
    print("測試完成")
