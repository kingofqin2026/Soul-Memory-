#!/usr/bin/env python3
"""
Soul Memory Module B: 向量搜索引擎 (Vector Search Engine)

替換失效的 Gemini Embedding API，實現本地向量搜索

Author: Soul Memory System
Date: 2026-02-17
"""

import json
import hashlib
import os
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path
import re


@dataclass
class SearchResult:
    """搜索結果"""
    content: str           # 記憶內容
    score: float          # 相似度分數 (0-1)
    source: str           # 來源檔案
    line_number: int      # 行號
    category: str = ""    # 記憶類別
    priority: str = "N"   # 優先級


@dataclass
class MemorySegment:
    """記憶分段"""
    id: str
    content: str
    source: str
    line_number: int
    category: str = ""
    priority: str = "N"
    keywords: List[str] = field(default_factory=list)


class VectorSearch:
    """
    向量搜索引擎
    
    由於外部 API 可能不可用，實現基於關鍵詞的語義搜索
    作為 fallback 方案，同時預留 embedding API 接口
    """
    
    # 語義關鍵詞映射（同義詞擴展）
    SEMANTIC_EXPANSIONS = {
        # QST 物理
        "暗物質": ["dark matter", "FSCA", "幾何扭量", "M_geo"],
        "FSCA": ["暗物質", "幾何扭量", "rho"],
        "E8": ["E8 bundle", "標準模型", "粒子"],
        "QST": ["量子時空", "分形時空", "quantum spacetime"],
        
        # 用戶相關
        "秦王": ["陛下", "King", "Eddy"],
        "我": ["用戶", "秦王", "陛下"],
        
        # 系統相關
        "記憶": ["memory", "MEMORY.md", "記住"],
        "系統": ["OpenClaw", "配置", "config"],
        
        # 外交
        "HKGBook": ["論壇", "外交", "Zhuangzi001"],
        "外交": ["HKGBook", "文宣", "巡邏"],
        
        # 龍珠
        "龍珠": ["dragon ball", "悟空", "界王"],
        "界王": ["King Kai", "龍珠", "悟空"],
    }
    
    # 分類關鍵詞
    CATEGORY_KEYWORDS = {
        "QST_Physics": ["暗物質", "FSCA", "E8", "理論", "物理", "公式", "計算"],
        "QST_Computation": ["軌道", "模擬", "數值", "HPC"],
        "User_Identity": ["秦王", "陛下", "偏好", "身份"],
        "Tech_Config": ["OpenClaw", "API", "配置", "金鑰", "key"],
        "HK_Forum": ["HKGBook", "論壇", "外交", "文宣", "巡邏"],
        "Dragon_Ball": ["龍珠", "悟空", "界王", "Dragon Ball"],
        "History": ["歷史", "朝代", "人物", "織田信長"],
        "General_Chat": ["天氣", "早安", "晚安", "閒聊"],
    }
    
    def __init__(self, 
                 memory_path: str = "/root/.openclaw/workspace/MEMORY.md",
                 index_path: str = "/root/.openclaw/workspace/memory-system/cache/index.json"):
        """
        初始化向量搜索引擎
        
        Args:
            memory_path: MEMORY.md 檔案路徑
            index_path: 索引快取路徑
        """
        self.memory_path = memory_path
        self.index_path = index_path
        self.segments: List[MemorySegment] = []
        self._embedding_client = None
        
        # 確保快取目錄存在
        os.makedirs(os.path.dirname(index_path), exist_ok=True)
    
    def index_memory(self, force_rebuild: bool = False) -> int:
        """
        索引 MEMORY.md
        
        Args:
            force_rebuild: 是否強制重建索引
            
        Returns:
            索引的記憶段數量
        """
        # 檢查快取
        if not force_rebuild and os.path.exists(self.index_path):
            try:
                with open(self.index_path, 'r', encoding='utf-8') as f:
                    cached = json.load(f)
                    self.segments = [MemorySegment(**s) for s in cached.get('segments', [])]
                    if self.segments:
                        return len(self.segments)
            except Exception:
                pass  # 快取損壞，重新索引
        
        # 讀取 MEMORY.md
        if not os.path.exists(self.memory_path):
            return 0
        
        with open(self.memory_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 解析記憶段
        self.segments = []
        current_category = ""
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith('#'):
                # 檢查是否是分類標題
                if line.startswith('##'):
                    current_category = line.lstrip('#').strip()
                continue
            
            # 跳過分隔線
            if line.startswith('---'):
                continue
            
            # 提取優先級標籤
            priority = "N"
            content = line
            match = re.match(r'^\[([CIN])\]\s*(.+)$', line, re.IGNORECASE)
            if match:
                priority = match.group(1).upper()
                content = match.group(2)
            
            # 生成唯一 ID
            seg_id = hashlib.md5(f"{line}_{i}".encode()).hexdigest()[:8]
            
            # 提取關鍵詞
            keywords = self._extract_keywords(content)
            
            # 檢測類別
            detected_category = self._detect_category(content)
            
            segment = MemorySegment(
                id=seg_id,
                content=content,
                source=self.memory_path,
                line_number=i + 1,
                category=detected_category or current_category,
                priority=priority,
                keywords=keywords
            )
            self.segments.append(segment)
        
        # 保存快取
        self._save_index()
        
        return len(self.segments)
    
    def search(self, query: str, top_k: int = 5, 
               category_filter: Optional[str] = None,
               priority_boost: bool = True) -> List[SearchResult]:
        """
        搜索相關記憶
        
        Args:
            query: 搜索查詢
            top_k: 返回結果數量
            category_filter: 類別過濾
            priority_boost: 是否對高優先級記憶加分
            
        Returns:
            搜索結果列表
        """
        if not self.segments:
            self.index_memory()
        
        # 擴展查詢關鍵詞
        query_keywords = self._extract_keywords(query)
        
        # 中文 n-gram 和語義擴展
        expanded_keywords = set(query_keywords)
        
        # 檢查中文單字/詞組的語義擴展
        query_lower = query.lower()
        for key, expansions in self.SEMANTIC_EXPANSIONS.items():
            if key in query_lower:
                expanded_keywords.update(expansions)
                expanded_keywords.add(key)
            # 反向檢查：如果擴展詞在查詢中
            for exp in expansions:
                if exp.lower() in query_lower:
                    expanded_keywords.add(key)
                    expanded_keywords.update(expansions)
        
        # 原擴展邏輯
        for kw in query_keywords:
            if kw in self.SEMANTIC_EXPANSIONS:
                expanded_keywords.update(self.SEMANTIC_EXPANSIONS[kw])
        
        # 計算每個段落的相似度
        results = []
        for seg in self.segments:
            # 類別過濾
            if category_filter and category_filter not in seg.category:
                continue
            
            # 計算關鍵詞匹配分數
            match_count = sum(1 for kw in expanded_keywords if kw in seg.content.lower())
            keyword_score = match_count / max(len(expanded_keywords), 1)
            
            # 計算原始關鍵詞匹配
            original_match = sum(1 for kw in query_keywords if kw in seg.content.lower())
            original_score = original_match / max(len(query_keywords), 1) if query_keywords else 0
            
            # 綜合分數（原始關鍵詞權重更高）
            score = original_score * 0.7 + keyword_score * 0.3
            
            # 優先級加分
            if priority_boost:
                if seg.priority == "C":
                    score *= 1.3
                elif seg.priority == "I":
                    score *= 1.1
            
            if score > 0:
                results.append(SearchResult(
                    content=seg.content,
                    score=min(score, 1.0),
                    source=seg.source,
                    line_number=seg.line_number,
                    category=seg.category,
                    priority=seg.priority
                ))
        
        # 排序並返回 top_k
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取關鍵詞"""
        # 簡單分詞（以空格和標點分隔）
        words = re.findall(r'[\w\u4e00-\u9fff]+', text.lower())
        # 過濾停用詞
        stop_words = {'的', '是', '在', '有', '和', '了', '與', '對', '到', '為', 'the', 'a', 'is', 'of', 'to', 'and'}
        return [w for w in words if w not in stop_words and len(w) > 1]
    
    def _detect_category(self, text: str) -> str:
        """檢測記憶類別"""
        text_lower = text.lower()
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in text_lower:
                    return category
        return ""
    
    def _save_index(self):
        """保存索引到快取"""
        data = {
            'segments': [
                {
                    'id': s.id,
                    'content': s.content,
                    'source': s.source,
                    'line_number': s.line_number,
                    'category': s.category,
                    'priority': s.priority,
                    'keywords': s.keywords
                }
                for s in self.segments
            ]
        }
        with open(self.index_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def clear_cache(self):
        """清除索引快取"""
        if os.path.exists(self.index_path):
            os.remove(self.index_path)
        self.segments = []


# 便捷函數
def search_memory(query: str, top_k: int = 5) -> List[SearchResult]:
    """
    搜索記憶的便捷函數
    
    Args:
        query: 搜索查詢
        top_k: 返回結果數量
        
    Returns:
        搜索結果列表
    """
    engine = VectorSearch()
    return engine.search(query, top_k)


# 模組測試
if __name__ == "__main__":
    print("=" * 60)
    print("Soul Memory Module B: 向量搜索引擎測試")
    print("=" * 60)
    
    engine = VectorSearch()
    count = engine.index_memory()
    print(f"\n已索引 {count} 個記憶段")
    
    # 測試搜索
    test_queries = [
        "QST 暗物質",
        "我是誰",
        "OpenClaw 配置",
        "HKGBook 外交",
    ]
    
    for query in test_queries:
        print(f"\n查詢: {query}")
        results = engine.search(query, top_k=3)
        for i, r in enumerate(results, 1):
            print(f"  {i}. [{r.priority}] {r.content[:50]}... (分數: {r.score:.2f})")
    
    print("\n" + "=" * 60)
    print("測試完成")
