#!/usr/bin/env python3
"""
Soul Memory Module A: 權重解析器單元測試

Author: Soul Memory System
Date: 2026-02-17
"""

import unittest
import sys
import os

# 添加模組路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.priority_parser import (
    Priority,
    ParsedMemory,
    PriorityParser,
    parse_priority,
    get_priority,
)


class TestPriorityEnum(unittest.TestCase):
    """測試 Priority 枚舉"""
    
    def test_priority_values(self):
        """測試枚舉值"""
        self.assertEqual(Priority.CRITICAL.value, "C")
        self.assertEqual(Priority.IMPORTANT.value, "I")
        self.assertEqual(Priority.NORMAL.value, "N")
    
    def test_priority_count(self):
        """測試枚舉數量"""
        self.assertEqual(len(Priority), 3)


class TestPriorityParser(unittest.TestCase):
    """測試 PriorityParser 類"""
    
    def setUp(self):
        """測試前設置"""
        self.parser = PriorityParser()
    
    # ==================== 明確標籤解析 ====================
    
    def test_parse_critical_tag(self):
        """測試 [C] 標籤解析"""
        result = self.parser.parse("[C] QST 暗物質理論")
        self.assertEqual(result.priority, Priority.CRITICAL)
        self.assertEqual(result.content, "QST 暗物質理論")
        self.assertTrue(result.has_explicit_tag)
    
    def test_parse_important_tag(self):
        """測試 [I] 標籤解析"""
        result = self.parser.parse("[I] OpenClaw 配置討論")
        self.assertEqual(result.priority, Priority.IMPORTANT)
        self.assertEqual(result.content, "OpenClaw 配置討論")
        self.assertTrue(result.has_explicit_tag)
    
    def test_parse_normal_tag(self):
        """測試 [N] 標籤解析"""
        result = self.parser.parse("[N] 一般閒聊內容")
        self.assertEqual(result.priority, Priority.NORMAL)
        self.assertEqual(result.content, "一般閒聊內容")
        self.assertTrue(result.has_explicit_tag)
    
    def test_parse_tag_case_insensitive(self):
        """測試標籤大小寫不敏感"""
        # 小寫
        result = self.parser.parse("[c] 小寫 critical")
        self.assertEqual(result.priority, Priority.CRITICAL)
        
        result = self.parser.parse("[i] 小寫 important")
        self.assertEqual(result.priority, Priority.IMPORTANT)
        
        result = self.parser.parse("[n] 小寫 normal")
        self.assertEqual(result.priority, Priority.NORMAL)
    
    def test_parse_tag_with_extra_spaces(self):
        """測試標籤後多空格"""
        result = self.parser.parse("[C]   多餘空格測試")
        self.assertEqual(result.priority, Priority.CRITICAL)
        self.assertEqual(result.content, "多餘空格測試")
    
    # ==================== 自動檢測 ====================
    
    def test_auto_detect_critical(self):
        """測試 Critical 關鍵詞自動檢測"""
        critical_texts = [
            "記住這個重要資訊",
            "計算結果需要保存",
            "這是暗物質理論的核心",
            "重要決策會議紀錄",
            "系統配置參數",
            "公式推導過程",
        ]
        for text in critical_texts:
            result = self.parser.parse(text)
            self.assertEqual(result.priority, Priority.CRITICAL, 
                           f"Expected CRITICAL for: {text}")
            self.assertFalse(result.has_explicit_tag)
    
    def test_auto_detect_important(self):
        """測試 Important 關鍵詞自動檢測"""
        important_texts = [
            "我們討論一下這個問題",
            "比較兩種方案的優劣",
            "專案進度分析",
            "明天有個約定",
            "會議安排在下午",
            "項目評估報告",
        ]
        for text in important_texts:
            result = self.parser.parse(text)
            self.assertEqual(result.priority, Priority.IMPORTANT,
                           f"Expected IMPORTANT for: {text}")
            self.assertFalse(result.has_explicit_tag)
    
    def test_auto_detect_normal(self):
        """測試 Normal 模式自動檢測"""
        normal_texts = [
            "今天天氣不錯",
            "早安，你好",
            "晚安，明天見",
            "哈哈，真有趣",
            "謝謝你的幫忙",
        ]
        for text in normal_texts:
            result = self.parser.parse(text)
            self.assertEqual(result.priority, Priority.NORMAL,
                           f"Expected NORMAL for: {text}")
            self.assertFalse(result.has_explicit_tag)
    
    def test_auto_detect_default_normal(self):
        """測試無關鍵詞時預設為 Normal"""
        result = self.parser.parse("這是一段普通文字")
        self.assertEqual(result.priority, Priority.NORMAL)
    
    # ==================== 優先級層級 ====================
    
    def test_priority_critical_over_important(self):
        """測試 Critical 優先於 Important"""
        # 包含 Critical 關鍵詞 "記住" 和 Important 關鍵詞 "討論"
        result = self.parser.parse("記住我們討論的內容")
        self.assertEqual(result.priority, Priority.CRITICAL)
    
    def test_priority_important_over_normal(self):
        """測試 Important 優先於 Normal"""
        # 包含 Important 關鍵詞 "討論" 和 Normal 指示詞
        result = self.parser.parse("討論一下天氣")  # "討論" 在 IMPORTANT_KEYWORDS
        self.assertEqual(result.priority, Priority.IMPORTANT)
    
    # ==================== 標籤操作 ====================
    
    def test_add_tag(self):
        """測試添加標籤"""
        text = "需要記住的內容"
        tagged = self.parser.add_tag(text, Priority.CRITICAL)
        self.assertEqual(tagged, "[C] 需要記住的內容")
    
    def test_add_tag_to_already_tagged(self):
        """測試為已標籤文本添加新標籤（應替換）"""
        text = "[I] 原有標籤"
        tagged = self.parser.add_tag(text, Priority.CRITICAL)
        self.assertEqual(tagged, "[C] 原有標籤")
    
    def test_change_priority(self):
        """測試更改優先級"""
        text = "[N] 原本是 normal"
        changed = self.parser.change_priority(text, Priority.CRITICAL)
        self.assertEqual(changed, "[C] 原本是 normal")
    
    def test_strip_tag(self):
        """測試移除標籤"""
        text = "[C] 需要移除標籤的內容"
        stripped = self.parser.strip_tag(text)
        self.assertEqual(stripped, "需要移除標籤的內容")
    
    def test_strip_tag_no_tag(self):
        """測試移除不存在標籤"""
        text = "沒有標籤的內容"
        stripped = self.parser.strip_tag(text)
        self.assertEqual(stripped, text)
    
    # ==================== 便捷函數 ====================
    
    def test_parse_priority_function(self):
        """測試 parse_priority 便捷函數"""
        result = parse_priority("[C] 測試")
        self.assertIsInstance(result, ParsedMemory)
        self.assertEqual(result.priority, Priority.CRITICAL)
    
    def test_get_priority_function(self):
        """測試 get_priority 便捷函數"""
        priority = get_priority("[I] 測試")
        self.assertEqual(priority, Priority.IMPORTANT)
    
    # ==================== 邊界條件 ====================
    
    def test_empty_string(self):
        """測試空字符串"""
        result = self.parser.parse("")
        self.assertEqual(result.priority, Priority.NORMAL)
        self.assertEqual(result.content, "")
    
    def test_whitespace_only(self):
        """測試僅空白字符"""
        result = self.parser.parse("   ")
        self.assertEqual(result.priority, Priority.NORMAL)
    
    def test_tag_only(self):
        """測試僅標籤"""
        result = self.parser.parse("[C]")
        # 正則不匹配，因為需要有內容
        self.assertEqual(result.priority, Priority.NORMAL)  # 無內容，無關鍵詞
    
    def test_invalid_tag(self):
        """測試無效標籤"""
        result = self.parser.parse("[X] 無效標籤")
        # 無效標籤不匹配，走自動檢測
        self.assertEqual(result.priority, Priority.NORMAL)
    
    def test_tag_in_middle(self):
        """測試標籤在中間（不應匹配）"""
        result = self.parser.parse("文本 [C] 在中間")
        # 標籤不在開頭，走自動檢測
        self.assertFalse(result.has_explicit_tag)
    
    # ==================== 自動檢測開關 ====================
    
    def test_auto_detect_disabled(self):
        """測試關閉自動檢測"""
        parser = PriorityParser(auto_detect=False)
        result = parser.parse("記住這個重要資訊")
        # 自動檢測關閉，即使有 Critical 關鍵詞也返回 Normal
        self.assertEqual(result.priority, Priority.NORMAL)


class TestParsedMemory(unittest.TestCase):
    """測試 ParsedMemory 數據類"""
    
    def test_dataclass_creation(self):
        """測試數據類創建"""
        memory = ParsedMemory(
            original="[C] 測試",
            priority=Priority.CRITICAL,
            content="測試",
            has_explicit_tag=True
        )
        self.assertEqual(memory.original, "[C] 測試")
        self.assertEqual(memory.priority, Priority.CRITICAL)
        self.assertEqual(memory.content, "測試")
        self.assertTrue(memory.has_explicit_tag)


# 測試運行器
def run_tests():
    """運行所有測試"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加測試類
    suite.addTests(loader.loadTestsFromTestCase(TestPriorityEnum))
    suite.addTests(loader.loadTestsFromTestCase(TestPriorityParser))
    suite.addTests(loader.loadTestsFromTestCase(TestParsedMemory))
    
    # 運行測試
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
