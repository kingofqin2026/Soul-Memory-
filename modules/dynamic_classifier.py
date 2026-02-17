#!/usr/bin/env python3
"""
Soul Memory Module C: 動態分類樹 (Dynamic Classifier)

從 MEMORY.md 自動學習記憶類別，無需手動定義

Author: Soul Memory System
Date: 2026-02-17
"""

import json
import re
import os
from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple, Optional
from pathlib import Path
from collections import Counter


@dataclass
class Category:
    """記憶類別"""
    name: str                    # 類別名稱
    keywords: Set[str]           # 關鍵詞集合
    count: int = 0               # 出現次數
    parent: Optional[str] = None # 父類別
    children: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'keywords': list(self.keywords),
            'count': self.count,
            'parent': self.parent,
            'children': self.children
        }
    
    @classmethod
    def from_dict(cls, d: dict) -> 'Category':
        return cls(
            name=d['name'],
            keywords=set(d.get('keywords', [])),
            count=d.get('count', 0),
            parent=d.get('parent'),
            children=d.get('children', [])
        )


class DynamicClassifier:
    """
    動態分類樹
    
    功能：
    1. 從 MEMORY.md 自動學習類別
    2. 動態擴展分類樹
    3. 基於類別的 Selection Rule
    4. 相似類別自動合併建議
    """
    
    # 預設類別種子（初始類別）
    SEED_CATEGORIES = {
        "QST_Physics": ["暗物質", "FSCA", "E8", "理論", "物理", "公式", "時空", "宇宙"],
        "QST_Computation": ["軌道", "模擬", "數值", "計算", "HPC", "驗證"],
        "User_Identity": ["秦王", "陛下", "偏好", "身份", "喜歡", "用戶"],
        "User_Intent": ["想要", "需要", "我想", "請幫", "目標"],
        "Tech_Config": ["OpenClaw", "API", "配置", "金鑰", "key", "系統", "設置"],
        "Tech_Discussion": ["GPU", "CPU", "TPU", "性能", "比較", "硬件"],
        "HK_Forum": ["HKGBook", "論壇", "外交", "文宣", "巡邏", "帖子"],
        "Dragon_Ball": ["龍珠", "悟空", "界王", "Dragon Ball", "賽亞人"],
        "History": ["歷史", "朝代", "人物", "織田信長", "漢朝", "秦國"],
        "General_Chat": ["天氣", "早安", "晚安", "閒聊", "哈哈", "謝謝"],
    }
    
    # 類別關聯矩陣（哪些類別常一起出現）
    CATEGORY_RELATIONS = {
        ("QST_Physics", "QST_Computation"): 0.8,
        ("User_Identity", "User_Intent"): 0.7,
        ("Tech_Config", "Tech_Discussion"): 0.6,
        ("HK_Forum", "Tech_Config"): 0.5,
    }
    
    def __init__(self, 
                 memory_path: str = "/root/.openclaw/workspace/MEMORY.md",
                 config_path: str = "/root/.openclaw/workspace/memory-system/cache/categories.json"):
        """
        初始化動態分類器
        
        Args:
            memory_path: MEMORY.md 路徑
            config_path: 分類配置快取路徑
        """
        self.memory_path = memory_path
        self.config_path = config_path
        self.categories: Dict[str, Category] = {}
        
        # 確保目錄存在
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        # 初始化種子類別
        self._init_seed_categories()
    
    def _init_seed_categories(self):
        """初始化種子類別"""
        for name, keywords in self.SEED_CATEGORIES.items():
            self.categories[name] = Category(
                name=name,
                keywords=set(keywords),
                count=0
            )
    
    def learn_from_memory(self, force_rebuild: bool = False) -> int:
        """
        從 MEMORY.md 學習類別
        
        Args:
            force_rebuild: 是否強制重建
            
        Returns:
            學習到的記憶條目數
        """
        # 檢查快取
        if not force_rebuild and os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    cached = json.load(f)
                    self.categories = {
                        name: Category.from_dict(d) 
                        for name, d in cached.get('categories', {}).items()
                    }
                    if self.categories:
                        return sum(c.count for c in self.categories.values())
            except Exception:
                pass
        
        # 讀取 MEMORY.md
        if not os.path.exists(self.memory_path):
            return 0
        
        with open(self.memory_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析類別標籤 [Category_Name]
        tag_pattern = re.compile(r'\[([A-Za-z_]+)\]')
        
        lines = content.split('\n')
        item_count = 0
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('---'):
                continue
            
            # 提取類別標籤
            tags = tag_pattern.findall(line)
            
            # 更新類別計數
            for tag in tags:
                if tag in self.categories:
                    self.categories[tag].count += 1
                else:
                    # 新類別！動態創建
                    self.categories[tag] = Category(
                        name=tag,
                        keywords=self._extract_keywords_from_content(line),
                        count=1
                    )
            
            if tags:
                item_count += 1
        
        # 保存快取
        self._save_categories()
        
        return item_count
    
    def get_categories(self) -> List[Category]:
        """獲取所有類別"""
        return list(self.categories.values())
    
    def select_for_query(self, query: str) -> List[str]:
        """
        為查詢選擇相關類別（Selection Rule）
        
        Args:
            query: 用戶查詢
            
        Returns:
            相關類別列表（按相關度排序）
        """
        query_lower = query.lower()
        scores: List[Tuple[str, float]] = []
        
        for name, cat in self.categories.items():
            # 計算關鍵詞匹配
            match_count = sum(1 for kw in cat.keywords if kw.lower() in query_lower)
            if match_count == 0:
                continue
            
            # 歸一化分數
            score = match_count / max(len(cat.keywords), 1)
            
            # 考慮類別出現頻率
            frequency_bonus = min(cat.count / 10, 0.2)
            
            scores.append((name, score + frequency_bonus))
        
        # 排序
        scores.sort(key=lambda x: x[1], reverse=True)
        
        return [name for name, _ in scores[:5]]  # 返回 top 5
    
    def suggest_merge(self, threshold: float = 0.7) -> List[Tuple[str, str, float]]:
        """
        建議合併的相似類別
        
        Args:
            threshold: 相似度閾值
            
        Returns:
            [(類別A, 類別B, 相似度), ...]
        """
        suggestions = []
        cat_names = list(self.categories.keys())
        
        for i, name_a in enumerate(cat_names):
            for name_b in cat_names[i+1:]:
                # 計算關鍵詞重疊率
                cat_a = self.categories[name_a]
                cat_b = self.categories[name_b]
                
                if not cat_a.keywords or not cat_b.keywords:
                    continue
                
                intersection = len(cat_a.keywords & cat_b.keywords)
                union = len(cat_a.keywords | cat_b.keywords)
                similarity = intersection / union if union > 0 else 0
                
                if similarity >= threshold:
                    suggestions.append((name_a, name_b, similarity))
        
        # 按相似度排序
        suggestions.sort(key=lambda x: x[2], reverse=True)
        return suggestions
    
    def add_category(self, name: str, keywords: List[str], parent: Optional[str] = None):
        """添加新類別"""
        if name not in self.categories:
            self.categories[name] = Category(
                name=name,
                keywords=set(keywords),
                parent=parent
            )
            if parent and parent in self.categories:
                self.categories[parent].children.append(name)
            self._save_categories()
    
    def merge_categories(self, source: str, target: str):
        """合併兩個類別"""
        if source not in self.categories or target not in self.categories:
            return
        
        src = self.categories[source]
        tgt = self.categories[target]
        
        # 合併關鍵詞
        tgt.keywords.update(src.keywords)
        tgt.count += src.count
        
        # 移動子類別
        for child in src.children:
            if child in self.categories:
                self.categories[child].parent = target
                tgt.children.append(child)
        
        # 刪除源類別
        del self.categories[source]
        
        self._save_categories()
    
    def _extract_keywords_from_content(self, content: str) -> Set[str]:
        """從內容提取關鍵詞"""
        # 提取中文詞和英文詞
        words = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', content)
        stop_words = {'的', '是', '在', '有', '和', '了', '與', '對', '到', '為', 'the', 'a', 'is', 'of', 'to', 'and'}
        return {w for w in words if w not in stop_words and len(w) > 1}
    
    def _save_categories(self):
        """保存類別配置"""
        data = {
            'categories': {
                name: cat.to_dict() 
                for name, cat in self.categories.items()
            }
        }
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


# 便捷函數
def classify_query(query: str) -> List[str]:
    """
    分類查詢的便捷函數
    
    Args:
        query: 用戶查詢
        
    Returns:
        相關類別列表
    """
    classifier = DynamicClassifier()
    classifier.learn_from_memory()
    return classifier.select_for_query(query)


# 模組測試
if __name__ == "__main__":
    print("=" * 60)
    print("Soul Memory Module C: 動態分類樹測試")
    print("=" * 60)
    
    classifier = DynamicClassifier()
    count = classifier.learn_from_memory()
    print(f"\n已學習 {count} 個記憶條目")
    
    # 顯示類別
    print("\n類別列表:")
    for cat in classifier.get_categories():
        if cat.count > 0:
            print(f"  {cat.name}: {cat.count} 次, 關鍵詞: {list(cat.keywords)[:5]}...")
    
    # 測試 Selection Rule
    test_queries = [
        "QST 暗物質理論",
        "我是誰",
        "OpenClaw 系統配置",
    ]
    
    print("\nSelection Rule 測試:")
    for query in test_queries:
        categories = classifier.select_for_query(query)
        print(f"  查詢: {query} → 類別: {categories}")
    
    # 測試合併建議
    suggestions = classifier.suggest_merge(threshold=0.3)
    if suggestions:
        print("\n建議合併的類別:")
        for a, b, sim in suggestions[:3]:
            print(f"  {a} ↔ {b} (相似度: {sim:.2f})")
    
    print("\n" + "=" * 60)
    print("測試完成")
