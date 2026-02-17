#!/usr/bin/env python3
"""
Soul Memory System v2.1 - Core Orchestrator

統一接口整合器，整合所有模組

Author: Soul Memory System
Date: 2026-02-17
"""

import os
import sys
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

# 確保模組路徑正確
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.priority_parser import PriorityParser, Priority, ParsedMemory
from modules.vector_search import VectorSearch, SearchResult
from modules.dynamic_classifier import DynamicClassifier
from modules.version_control import VersionControl
from modules.memory_decay import MemoryDecay
from modules.auto_trigger import AutoTrigger, auto_trigger, get_memory_context


@dataclass
class MemoryQueryResult:
    """記憶查詢結果"""
    content: str
    priority: str
    category: str
    score: float
    source: str
    line_number: int


class SoulMemorySystem:
    """
    Soul Memory System v2.1 統一接口
    
    整合所有模組，提供簡潔的記憶管理 API
    """
    
    def __init__(self, 
                 memory_path: str = "/root/.openclaw/workspace/MEMORY.md",
                 auto_git_commit: bool = True):
        """
        初始化記憶系統
        
        Args:
            memory_path: MEMORY.md 路徑
            auto_git_commit: 是否自動 git commit
        """
        self.memory_path = memory_path
        
        # 初始化各模組
        self.parser = PriorityParser()
        self.vector_search = VectorSearch(memory_path)
        self.classifier = DynamicClassifier(memory_path)
        self.version_control = VersionControl(memory_path, auto_git_commit=auto_git_commit)
        self.decay = MemoryDecay()
        self.auto_trigger = AutoTrigger(self)
        
        # 確保底層目錄存在
        os.makedirs(os.path.dirname(memory_path), exist_ok=True)
    
    def initialize(self) -> bool:
        """
        初始化系統（載入現有記憶）
        
        Returns:
            是否成功
        """
        try:
            # 索引記憶
            if os.path.exists(self.memory_path):
                self.vector_search.index_memory()
                self.classifier.learn_from_memory()
            return True
        except Exception as e:
            print(f"初始化失敗: {e}")
            return False
    
    def search(self, query: str, top_k: int = 5) -> List[MemoryQueryResult]:
        """
        搜索記憶
        
        Args:
            query: 搜索查詢
            top_k: 返回結果數量
            
        Returns:
            記憶查詢結果列表
        """
        # 記錄訪問（用於熱度衰減）
        results = self.vector_search.search(query, top_k)
        
        return [
            MemoryQueryResult(
                content=r.content,
                priority=r.priority,
                category=r.category,
                score=r.score,
                source=r.source,
                line_number=r.line_number
            )
            for r in results
        ]
    
    def pre_response_trigger(self, query: str) -> Dict[str, Any]:
        """
        回答前自動觸發（Pre-Response Auto-Trigger）
        
        每次回答用戶問題前調用，確保回答有記憶支持
        
        Args:
            query: 用戶問題
            
        Returns:
            包含搜索結果和上下文的字典
        """
        return self.auto_trigger.execute(query).results
    
    def add_memory(self, content: str, priority: Optional[str] = None) -> Dict[str, Any]:
        """
        添加新記憶
        
        Args:
            content: 記憶內容
            priority: 優先級（C/I/N），自動檢測
            
        Returns:
            操作結果
        """
        # 解析優先級
        parsed = self.parser.parse(content)
        if priority:
            priority = priority.upper()
        else:
            priority = parsed.priority.value
        
        # 格式化內容
        formatted = f"[{priority}] {parsed.content}"
        
        # 追加到 MEMORY.md
        try:
            with open(self.memory_path, 'a', encoding='utf-8') as f:
                f.write(f"\n{formatted}\n")
            
            # 重新索引
            self.vector_search.index_memory(force_rebuild=True)
            self.classifier.learn_from_memory(force_rebuild=True)
            
            # 註冊熱度
            memory_id = f"mem_{hash(content) % 10000:04d}"
            self.decay.register_memory(memory_id, formatted, priority)
            
            # 保存版本
            with open(self.memory_path, 'r', encoding='utf-8') as f:
                full_content = f.read()
            version_result = self.version_control.save_version(
                full_content, 
                f"Add memory: {parsed.content[:50]}..."
            )
            
            return {
                "success": True,
                "content": formatted,
                "priority": priority,
                "version_id": version_result.get("version_id"),
                "memory_id": memory_id
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_categories(self) -> List[str]:
        """獲取所有記憶類別"""
        cats = self.classifier.get_categories()
        return [c.name for c in cats if c.count > 0]
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取系統統計"""
        return {
            "total_segments": len(self.vector_search.segments),
            "categories": len(self.get_categories()),
            "versions": self.version_control.get_stats().get("total_versions", 0),
            "decay_stats": self.decay.get_stats()
        }
    
    def full_report(self) -> str:
        """生成完整系統報告"""
        stats = self.get_stats()
        return f"""
Soul Memory System v2.1 狀態報告
================================
記憶段數: {stats['total_segments']}
活躍類別: {stats['categories']}
版本數量: {stats['versions']}

熱度統計:
  - 總記憶數: {stats['decay_stats']['total_memories']}
  - 按優先級: {stats['decay_stats']['by_priority']}
  - 平均分數: {stats['decay_stats']['avg_decay_score']:.3f}

模組狀態:
  ✓ A: 權重解析器
  ✓ B: 向量搜索引擎  
  ✓ C: 動態分類樹
  ✓ D: 版本控制器
  ✓ E: 熱度衰減器

================================
        """


# 便捷函數
def get_system() -> SoulMemorySystem:
    """獲取系統實例的便捷函數"""
    return SoulMemorySystem()


# 測試
def test_system():
    """測試完整系統"""
    print("Soul Memory System v2.1 - 系統測試")
    print("=" * 50)
    
    system = get_system()
    system.initialize()
    
    # 測試搜索
    print("\n1. 搜索測試:")
    results = system.search("QST 暗物質", top_k=3)
    for r in results:
        print(f"   [{r.priority}] {r.content[:40]}... ({r.score:.2f})")
    
    # 測試類別
    print("\n2. 類別測試:")
    categories = system.get_categories()
    print(f"   活躍類別: {categories[:5]}")
    
    # 報告
    print("\n3. 系統報告:")
    print(system.full_report())


if __name__ == "__main__":
    test_system()
