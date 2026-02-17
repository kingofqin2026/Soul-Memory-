#!/usr/bin/env python3
"""
Soul Memory System v2.1 - 整合測試

測試所有 5 個模組的協同運作

Author: Soul Memory System
Date: 2026-02-17
"""

import sys
import os

# 添加模組路徑
sys.path.insert(0, '/root/.openclaw/workspace/memory-system')

from modules.priority_parser import PriorityParser, Priority, parse_priority
from modules.vector_search import VectorSearch, search_memory
from modules.dynamic_classifier import DynamicClassifier, classify_query
from modules.version_control import VersionControl, get_controller
from modules.memory_decay import MemoryDecay, get_decay_score


def test_priority_parser():
    """測試模組 A: 權重解析器"""
    print("\n" + "=" * 50)
    print("模組 A: 權重解析器測試")
    print("=" * 50)
    
    parser = PriorityParser()
    test_cases = [
        ("[C] QST 暗物質理論", Priority.CRITICAL),
        ("[I] OpenClaw 配置討論", Priority.IMPORTANT),
        ("今天天氣不錯", Priority.NORMAL),
        ("記住這個重要公式", Priority.CRITICAL),  # 自動檢測
        ("我們討論一下專案", Priority.IMPORTANT),  # 自動檢測
    ]
    
    passed = 0
    for text, expected in test_cases:
        result = parser.parse(text)
        status = "✓" if result.priority == expected else "✗"
        print(f"  {status} '{text[:30]}...' → {result.priority.name}")
        if result.priority == expected:
            passed += 1
    
    print(f"\n結果: {passed}/{len(test_cases)} 通過")
    return passed == len(test_cases)


def test_vector_search():
    """測試模組 B: 向量搜索"""
    print("\n" + "=" * 50)
    print("模組 B: 向量搜索引擎測試")
    print("=" * 50)
    
    engine = VectorSearch()
    count = engine.index_memory()
    print(f"  已索引 {count} 個記憶段")
    
    test_queries = [
        "QST 暗物質",
        "我是誰",
        "OpenClaw 配置",
    ]
    
    passed = 0
    for query in test_queries:
        results = engine.search(query, top_k=3)
        status = "✓" if results else "✗"
        print(f"  {status} 查詢 '{query}' → {len(results)} 結果")
        if results:
            print(f"      首個: [{results[0].priority}] {results[0].content[:40]}...")
            passed += 1
    
    print(f"\n結果: {passed}/{len(test_queries)} 通過")
    return passed == len(test_queries)


def test_dynamic_classifier():
    """測試模組 C: 動態分類樹"""
    print("\n" + "=" * 50)
    print("模組 C: 動態分類樹測試")
    print("=" * 50)
    
    classifier = DynamicClassifier()
    count = classifier.learn_from_memory()
    print(f"  已學習 {count} 個記憶條目")
    
    categories = classifier.get_categories()
    active_cats = [c for c in categories if c.count > 0]
    print(f"  活躍類別: {len(active_cats)}")
    
    test_queries = [
        ("QST 暗物質理論", "QST_Physics"),
        ("OpenClaw 系統", "Tech_Config"),
    ]
    
    passed = 0
    for query, expected_cat in test_queries:
        cats = classifier.select_for_query(query)
        status = "✓" if cats and expected_cat in cats else "○"
        print(f"  {status} '{query}' → {cats[:3]}")
        if cats:
            passed += 1
    
    print(f"\n結果: {passed}/{len(test_queries)} 通過")
    return passed == len(test_queries)


def test_version_control():
    """測試模組 D: 版本控制器"""
    print("\n" + "=" * 50)
    print("模組 D: 版本控制器測試")
    print("=" * 50)
    
    vc = get_controller()
    stats = vc.get_stats()
    
    print(f"  總版本數: {stats['total_versions']}")
    if stats['latest_version']:
        print(f"  最新版本: {stats['latest_version']}")
        print(f"  最後修改: {stats['latest_timestamp']}")
    
    # 測試列表功能
    versions = vc.list_versions(limit=3)
    print(f"  最近 3 個版本:")
    for v in versions:
        print(f"    - {v['id']}: {v['summary'][:40]}...")
    
    return True


def test_memory_decay():
    """測試模組 E: 熱度衰減"""
    print("\n" + "=" * 50)
    print("模組 E: 熱度衰減器測試")
    print("=" * 50)
    
    decay = MemoryDecay()
    
    # 註冊測試記憶
    test_memories = [
        ("test_001", "[C] 關鍵配置", "C"),
        ("test_002", "[I] 專案討論", "I"),
        ("test_003", "日常閒聊", "N"),
    ]
    
    for mid, content, priority in test_memories:
        decay.register_memory(mid, content, priority)
    
    print(f"  已註冊 {len(test_memories)} 個測試記憶")
    
    # 測試衰減計算
    for mid, _, priority in test_memories:
        score = decay.compute_decay(mid)
        print(f"  {mid} ({priority}): 衰減分數 = {score:.3f}")
    
    # 獲取統計
    stats = decay.get_stats()
    print(f"  統計: {stats['by_priority']}")
    
    return True


def test_integration():
    """整合測試：所有模組協同運作"""
    print("\n" + "=" * 50)
    print("整合測試：端到端流程")
    print("=" * 50)
    
    # 1. 解析優先級
    parser = PriorityParser()
    test_input = "[C] QST 暗物質核心公式驗證"
    parsed = parser.parse(test_input)
    print(f"  1. 優先級解析: '{test_input}' → {parsed.priority.name}")
    
    # 2. 分類查詢
    classifier = DynamicClassifier()
    classifier.learn_from_memory()
    categories = classifier.select_for_query(parsed.content)
    print(f"  2. 動態分類: → {categories}")
    
    # 3. 向量搜索
    engine = VectorSearch()
    engine.index_memory()
    results = engine.search(parsed.content, top_k=3)
    print(f"  3. 向量搜索: → {len(results)} 相關記憶")
    
    # 4. 註冊熱度
    decay = MemoryDecay()
    decay.register_memory("integration_test", parsed.content, parsed.priority.value)
    score = decay.compute_decay("integration_test")
    print(f"  4. 熱度註冊: → 初始分數 {score:.3f}")
    
    # 5. 版本控制
    vc = get_controller()
    stats = vc.get_stats()
    print(f"  5. 版本狀態: {stats['total_versions']} 個版本")
    
    print("\n  ✓ 整合測試完成")
    return True


def main():
    """主測試函數"""
    print("=" * 60)
    print("Soul Memory System v2.1 - 模組測試")
    print("=" * 60)
    
    results = {
        "A: 權重解析器": test_priority_parser(),
        "B: 向量搜索": test_vector_search(),
        "C: 動態分類樹": test_dynamic_classifier(),
        "D: 版本控制器": test_version_control(),
        "E: 熱度衰減": test_memory_decay(),
        "整合測試": test_integration(),
    }
    
    print("\n" + "=" * 60)
    print("測試結果摘要")
    print("=" * 60)
    
    passed = 0
    for name, result in results.items():
        status = "✓ 通過" if result else "✗ 失敗"
        print(f"  {name}: {status}")
        if result:
            passed += 1
    
    print(f"\n總計: {passed}/{len(results)} 模組通過")
    
    if passed == len(results):
        print("\n🎉 所有模組測試通過！Soul Memory v2.1 就緒。")
    else:
        print("\n⚠️ 部分模組測試未通過，請檢查。")
    
    return passed == len(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
