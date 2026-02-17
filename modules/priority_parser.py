#!/usr/bin/env python3
"""
Soul Memory Module A: 權重解析器 (Priority Parser)

實現 [C]/[I]/[N] 權重標籤的正確解析與自動識別

Author: Soul Memory System
Date: 2026-02-17
"""

import re
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Tuple


class Priority(Enum):
    """記憶優先級枚舉"""
    CRITICAL = "C"   # 關鍵：必須記住的核心資訊
    IMPORTANT = "I"  # 重要：需要關注的項目
    NORMAL = "N"     # 一般：日常閒聊、問候


@dataclass
class ParsedMemory:
    """解析後的記憶項目"""
    original: str           # 原始文本
    priority: Priority      # 優先級
    content: str           # 內容（不含標籤）
    has_explicit_tag: bool # 是否有明確標籤


class PriorityParser:
    """
    權重解析器
    
    功能：
    1. 解析 [C]/[I]/[N] 格式的明確標籤
    2. 基於關鍵詞自動識別優先級
    3. 支援混合模式（先檢查明確標籤，再進行語義識別）
    """
    
    # 明確標籤的正則表達式
    TAG_PATTERN = re.compile(r'^\[([CIN])\]\s*(.+)$', re.IGNORECASE)
    
    # Critical 關鍵詞 (必須記住)
    CRITICAL_KEYWORDS = frozenset([
        # 動作類
        '記住', '計算', '驗證', '確認', '決定', '設定',
        # 知識類
        '理論', '公式', '原理', '定律', '定理',
        # 決策類
        '決策', '決定', '選擇', '判斷',
        # 配置類
        '配置', '設置', '設定', '參數', '選項',
        # 重要標記
        '重要', '關鍵', '核心', '必要', '必須',
        # 安全類
        '密碼', '金鑰', '憑證', '權限',
    ])
    
    # Important 關鍵詞 (需要關注)
    IMPORTANT_KEYWORDS = frozenset([
        # 互動類
        '討論', '談論', '探討', '交流',
        # 分析類
        '分析', '比較', '對比', '評估',
        # 專案類
        '專案', '項目', '計畫', '規劃',
        # 約定類
        '約定', '約會', '會議', '安排',
        '期限', '截止', '到期',
        # 文檔類
        '文檔', '文獻', '論文', '報告',
    ])
    
    # Normal 模式指示詞
    NORMAL_INDICATORS = frozenset([
        '天氣', '怎麼樣', '你好', '早安', '晚安',
        '謝謝', '不客氣', '嗨', '哈囉', 'bye',
        '哈哈', '呵呵', '嘿嘿', 'lol', 'XD',
    ])
    
    def __init__(self, auto_detect: bool = True):
        """
        初始化解析器
        
        Args:
            auto_detect: 是否啟用自動檢自動檢測（預設啟用）
        """
        self.auto_detect = auto_detect
    
    def parse(self, text: str) -> ParsedMemory:
        """
        解析文本的優先級
        
        Args:
            text: 待解析的文本
            
        Returns:
            ParsedMemory 物件
        """
        # 去除首尾空白
        text = text.strip()
        
        # 1. 首先檢查明確標籤
        match = self.TAG_PATTERN.match(text)
        if match:
            tag_char = match.group(1).upper()
            content = match.group(2).strip()
            priority = self._tag_to_priority(tag_char)
            return ParsedMemory(
                original=text,
                priority=priority,
                content=content,
                has_explicit_tag=True
            )
        
        # 2. 如果沒有明確標籤且啟用自動檢測
        if self.auto_detect:
            priority = self._detect_priority(text)
            return ParsedMemory(
                original=text,
                priority=priority,
                content=text,
                has_explicit_tag=False
            )
        
        # 3. 預設為 Normal
        return ParsedMemory(
            original=text,
            priority=Priority.NORMAL,
            content=text,
            has_explicit_tag=False
        )
    
    def _tag_to_priority(self, tag: str) -> Priority:
        """將標籤字符轉換為 Priority 枚舉"""
        mapping = {
            'C': Priority.CRITICAL,
            'I': Priority.IMPORTANT,
            'N': Priority.NORMAL,
        }
        return mapping.get(tag, Priority.NORMAL)
    
    def _detect_priority(self, text: str) -> Priority:
        """
        基於關鍵詞檢測優先級
        
        檢測順序：Critical -> Important -> Normal
        """
        # 檢查 Critical 關鍵詞
        if self._contains_keywords(text, self.CRITICAL_KEYWORDS):
            return Priority.CRITICAL
        
        # 檢查 Important 關鍵詞
        if self._contains_keywords(text, self.IMPORTANT_KEYWORDS):
            return Priority.IMPORTANT
        
        # 檢查 Normal 指示詞
        if self._contains_keywords(text, self.NORMAL_INDICATORS):
            return Priority.NORMAL
        
        # 預設為 Normal
        return Priority.NORMAL
    
    def _contains_keywords(self, text: str, keywords: frozenset) -> bool:
        """檢查文本是否包含任一關鍵詞"""
        text_lower = text.lower()
        return any(kw in text_lower for kw in keywords)
    
    def add_tag(self, text: str, priority: Priority) -> str:
        """
        為文本添加優先級標籤
        
        Args:
            text: 原始文本
            priority: 要添加的優先級
            
        Returns:
            帶標籤的文本
        """
        text = text.strip()
        
        # 如果已有標籤，先移除
        match = self.TAG_PATTERN.match(text)
        if match:
            text = match.group(2).strip()
        
        return f"[{priority.value}] {text}"
    
    def change_priority(self, text: str, new_priority: Priority) -> str:
        """
        更改文本的優先級
        
        Args:
            text: 原始文本（可能含標籤）
            new_priority: 新的優先級
            
        Returns:
            更新後的文本
        """
        return self.add_tag(text, new_priority)
    
    def strip_tag(self, text: str) -> str:
        """
        移除文本中的優先級標籤
        
        Args:
            text: 可能含標籤的文本
            
        Returns:
            不含標籤的純文本
        """
        match = self.TAG_PATTERN.match(text.strip())
        if match:
            return match.group(2).strip()
        return text.strip()


# 便捷函數
def parse_priority(text: str, auto_detect: bool = True) -> ParsedMemory:
    """
    解析文本優先級的便捷函數
    
    Args:
        text: 待解析的文本
        auto_detect: 是否啟用自動檢測
        
    Returns:
        ParsedMemory 物件
    """
    parser = PriorityParser(auto_detect=auto_detect)
    return parser.parse(text)


def get_priority(text: str) -> Priority:
    """
    獲取文本優先級的便捷函數
    
    Args:
        text: 待解析的文本
        
    Returns:
        Priority 枚舉值
    """
    return parse_priority(text).priority


# 模組測試
if __name__ == "__main__":
    # 測試案例
    test_cases = [
        "[C] QST 暗物質理論",
        "[I] OpenClaw 配置討論",
        "今天天氣不錯",
        "[c] 測試小寫標籤",  # 測試大小寫不敏感
        "記住這個重要公式",   # 測試自動檢測 Critical
        "我們討論一下專案",   # 測試自動檢測 Important
        "早安，今天好嗎",     # 測試自動檢測 Normal
    ]
    
    parser = PriorityParser()
    print("=" * 60)
    print("Soul Memory Module A: 權重解析器測試")
    print("=" * 60)
    
    for text in test_cases:
        result = parser.parse(text)
        print(f"\n輸入: {text}")
        print(f"  優先級: {result.priority.name}")
        print(f"  內容: {result.content}")
        print(f"  明確標籤: {'是' if result.has_explicit_tag else '否'}")
    
    print("\n" + "=" * 60)
    print("測試完成")
