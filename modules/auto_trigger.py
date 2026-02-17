#!/usr/bin/env python3
"""
Soul Memory Module F: Auto-Trigger (自動觸發器)

每次回答前自動執行記憶搜索，確保回答有記憶支持

Author: Soul Memory System v2.1
Date: 2026-02-17
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class TriggerResult:
    """Auto-Trigger 結果"""
    query: str
    results: List[dict]
    categories: List[str]
    context_summary: str


class AutoTrigger:
    """
    自動觸發器
    
    功能：
    1. 理解用戶意圖
    2. 識別問題類型
    3. 調用 memory-system 搜索
    4. 應用 Selection Rule
    5. 返回整合上下文
    """
    
    # Selection Rule 分類映射
    SELECTION_RULES = {
        # QST 相關
        "暗物質": ["QST_Physics", "QST_Computation"],
        "FSCA": ["QST_Physics", "QST_Computation"],
        "E8": ["QST_Physics"],
        "理論": ["QST_Physics"],
        "公式": ["QST_Computation", "QST_Physics"],
        "計算": ["QST_Computation"],
        "驗證": ["QST_Computation"],
        
        # 用戶相關
        "我是誰": ["User_Identity"],
        "我喜歡": ["User_Identity"],
        "我的": ["User_Identity", "Tech_Config"],
        "秦王": ["User_Identity"],
        "陛下": ["User_Identity"],
        
        # 系統相關
        "SSH": ["Tech_Config"],
        "API": ["Tech_Config"],
        "配置": ["Tech_Config"],
        "OpenClaw": ["Tech_Config"],
        "key": ["Tech_Config"],
        
        # 外交相關
        "HKGBook": ["HK_Forum"],
        "論壇": ["HK_Forum"],
        "外交": ["HK_Forum"],
        "帖子": ["HK_Forum"],
        
        # 動漫相關
        "龍珠": ["Dragon_Ball"],
        "悟空": ["Dragon_Ball"],
        "界王": ["Dragon_Ball"],
        
        # 歷史相關
        "歷史": ["History"],
        "朝代": ["History"],
    }
    
    def __init__(self, memory_system=None):
        """
        初始化 Auto-Trigger
        
        Args:
            memory_system: QSTMemorySystem 實例（可選）
        """
        self.memory_system = memory_system
    
    def execute(self, query: str, top_k: int = 5) -> TriggerResult:
        """
        執行 Auto-Trigger 流程
        
        Args:
            query: 用戶問題
            top_k: 返回結果數量
            
        Returns:
            TriggerResult 物件
        """
        # 1. 識別問題類型
        categories = self._identify_categories(query)
        
        # 2. 搜索記憶
        results = self._search_memory(query, categories, top_k)
        
        # 3. 生成上下文摘要
        context_summary = self._generate_context_summary(results)
        
        return TriggerResult(
            query=query,
            results=results,
            categories=categories,
            context_summary=context_summary
        )
    
    def _identify_categories(self, query: str) -> List[str]:
        """識別問題類型，返回相關類別"""
        categories = set()
        query_lower = query.lower()
        
        for keyword, cats in self.SELECTION_RULES.items():
            if keyword.lower() in query_lower:
                categories.update(cats)
        
        return list(categories) if categories else ["General"]
    
    def _search_memory(self, query: str, categories: List[str], top_k: int) -> List[dict]:
        """搜索記憶"""
        if self.memory_system is None:
            # 延遲導入避免循環依賴
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from core import QSTMemorySystem
            self.memory_system = QSTMemorySystem()
            self.memory_system.initialize()
        
        results = self.memory_system.search(query, top_k=top_k)
        
        # 轉換為字典格式
        return [
            {
                "content": r.content,
                "priority": r.priority,
                "category": r.category,
                "score": r.score,
                "source": r.source,
                "line_number": r.line_number
            }
            for r in results
        ]
    
    def _generate_context_summary(self, results: List[dict]) -> str:
        """生成上下文摘要"""
        if not results:
            return "無相關記憶"
        
        summary_parts = []
        for r in results[:3]:
            priority = r.get("priority", "N")
            content = r.get("content", "")[:50]
            summary_parts.append(f"[{priority}] {content}...")
        
        return " | ".join(summary_parts)
    
    def get_context_for_response(self, query: str) -> str:
        """
        獲取用於回答的上下文字串
        
        Args:
            query: 用戶問題
            
        Returns:
            格式化的上下文字串
        """
        result = self.execute(query)
        
        if not result.results:
            return ""
        
        context_lines = ["📌 相關記憶:"]
        for i, r in enumerate(result.results[:3], 1):
            context_lines.append(f"  {i}. [{r['priority']}] {r['content'][:60]}...")
        
        return "\n".join(context_lines)


# 便捷函數
_auto_trigger = None

def auto_trigger(query: str, top_k: int = 5) -> TriggerResult:
    """
    Auto-Trigger 便捷函數
    
    Args:
        query: 用戶問題
        top_k: 返回結果數量
        
    Returns:
        TriggerResult 物件
    """
    global _auto_trigger
    if _auto_trigger is None:
        _auto_trigger = AutoTrigger()
    return _auto_trigger.execute(query, top_k)


def get_memory_context(query: str) -> str:
    """
    獲取記憶上下文（用於回答前調用）
    
    Args:
        query: 用戶問題
        
    Returns:
        格式化的上下文字串
    """
    trigger = AutoTrigger()
    return trigger.get_context_for_response(query)


# 模組測試
if __name__ == "__main__":
    print("=" * 60)
    print("Soul Memory Module F: Auto-Trigger 測試")
    print("=" * 60)
    
    test_queries = [
        "QST 暗物質理論",
        "我是誰",
        "我的 SSH key",
        "HKGBook 最近有什麼討論",
    ]
    
    for query in test_queries:
        print(f"\n📝 用戶問題: {query}")
        
        # 執行 Auto-Trigger
        result = auto_trigger(query, top_k=3)
        
        print(f"🏷️ 識別類別: {result.categories}")
        print(f"🔍 搜索結果:")
        for i, r in enumerate(result.results, 1):
            print(f"   {i}. [{r['priority']}] {r['content'][:40]}...")
        print(f"📋 上下文摘要: {result.context_summary[:80]}...")
    
    print("\n" + "=" * 60)
    print("測試完成")
