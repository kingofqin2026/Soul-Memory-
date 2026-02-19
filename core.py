#!/usr/bin/env python3
"""
Soul Memory System v3.1 - Core Orchestrator
智能記憶管理系統核心 + 廣東話語法分支

Author: Li Si (李斯)
Date: 2026-02-18

v3.1.0 - Added Cantonese (廣東話) Grammar Branch
"""

import os
import sys
import json
import hashlib
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# Ensure module path
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import all modules
from modules.priority_parser import PriorityParser, Priority, ParsedMemory
from modules.vector_search import VectorSearch, SearchResult
from modules.dynamic_classifier import DynamicClassifier
from modules.version_control import VersionControl
from modules.memory_decay import MemoryDecay
from modules.auto_trigger import AutoTrigger, auto_trigger, get_memory_context
from modules.cantonese_syntax import CantoneseSyntaxBranch, CantoneseAnalysisResult, ToneIntensity, ContextType


@dataclass
class MemoryQueryResult:
    """Memory query result"""
    content: str
    score: float
    source: str
    line_number: int
    category: str
    priority: str


class SoulMemorySystem:
    """
    Soul Memory System v3.1
    
    Features:
    - Priority-based memory management [C]/[I]/[N]
    - Semantic keyword search (local, no external APIs)
    - Dynamic category classification
    - Automatic version control
    - Memory decay & cleanup
    - Pre-response auto-trigger
    - Cantonese (廣東話) Grammar Branch v3.1.0
    """
    
    VERSION = "3.2.1"
    
    def __init__(self, base_path: Optional[str] = None):
        """Initialize memory system"""
        self.base_path = Path(base_path) if base_path else Path(__file__).parent
        self.cache_path = self.base_path / "cache"
        self.cache_path.mkdir(exist_ok=True)
        
        # Initialize modules
        self.priority_parser = PriorityParser()
        self.vector_search = VectorSearch()
        self.classifier = DynamicClassifier()
        self.version_control = VersionControl(str(self.base_path))
        self.memory_decay = MemoryDecay(self.cache_path)
        self.auto_trigger = AutoTrigger(self)
        
        # v3.1.0: Cantonese Grammar Branch
        self.cantonese_branch = CantoneseSyntaxBranch()
        
        self.indexed = False
    
    def initialize(self):
        """Initialize and build index"""
        print(f"🧠 Initializing Soul Memory System v{self.VERSION}...")
        
        # Load or build search index
        index_file = self.cache_path / "index.json"
        
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.vector_search.load_index(data)
            print(f" Loaded index with {len(data.get('segments', []))} segments")
        else:
            print(" Building index...")
            memory_files = [
                Path.home() / ".openclaw" / "workspace" / "MEMORY.md",
            ]
            memory_dir = Path.home() / ".openclaw" / "workspace" / "memory"
            
            for memory_file in memory_files:
                if memory_file.exists() and memory_file.is_file():
                    self.vector_search.index_file(memory_file)
            
            # Index all .md files in memory directory
            if memory_dir.exists() and memory_dir.is_dir():
                for md_file in memory_dir.glob("*.md"):
                    self.vector_search.index_file(md_file)
            
            # Save index
            data = self.vector_search.export_index()
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f" Built index with {len(data.get('segments', []))} segments")
        
        self.indexed = True
        print(f"✅ Ready")
        return self
    
    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """Search memory"""
        if not self.indexed:
            self.initialize()
        return self.vector_search.search(query, top_k)
    
    def add_memory(self, content: str, category: Optional[str] = None) -> str:
        """Add new memory"""
        memory_id = hashlib.md5(content.encode()).hexdigest()[:8]
        
        # Parse priority
        parsed = self.priority_parser.parse(content)
        
        # Classify if category not provided
        if not category:
            category = self.classifier.classify(content)
        
        segment = {
            'id': memory_id,
            'content': content,
            'source': 'manual_add',
            'line_number': 0,
            'category': category,
            'priority': parsed.priority.value,
            'timestamp': datetime.now().isoformat(),
            'keywords': self.vector_search._extract_keywords(content)
        }
        
        self.vector_search.add_segment(segment)
        
        # Save updated index
        data = self.vector_search.export_index()
        with open(self.cache_path / "index.json", 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return memory_id
    
    def pre_response_trigger(self, query: str) -> Dict[str, Any]:
        """Pre-response auto-trigger"""
        return self.auto_trigger.trigger(query)
    
    def post_response_trigger(self, user_query: str, assistant_response: str, 
                              importance_threshold: str = "N") -> Optional[str]:
        """
        Post-response auto-save trigger
        自动识别重要内容并保存到记忆
        
        v3.1.1 Hotfix: 使用追加模式寫入記憶檔案，避免 OpenClaw 會話覆蓋問題
        """
        from datetime import datetime
        
        # 檢測是否為粵語
        is_canto, canto_conf = self.cantonese_branch.detect_cantonese(assistant_response)
        
        # 解析优先级
        parsed = self.priority_parser.parse(assistant_response)
        priority = parsed.priority.value
        
        # 根据阈值决定是否保存
        priority_order = {"C": 3, "I": 2, "N": 1}
        threshold_val = priority_order.get(importance_threshold, 1)
        content_val = priority_order.get(priority, 1)
        
        if content_val < threshold_val:
            return None
        
        # 生成唯一記憶 ID (加入時間戳避免覆蓋)
        timestamp = datetime.now()
        memory_id = hashlib.md5(
            f"{user_query}{timestamp.isoformat()}".encode()
        ).hexdigest()[:8]
        
        # ===== v3.1.1 Hotfix: 雙軌保存機制 =====
        
        # 1. 保存到 JSON 索引 (原有機制)
        content_to_save = f"[Auto-Save] Q: {user_query}\nA: {assistant_response[:500]}"
        if is_canto and canto_conf >= 0.3:
            content_to_save = f"[Cantonese] {content_to_save}"
        
        category = self.classifier.classify(assistant_response)
        
        # 添加到 JSON 索引
        memory_id_json = self.add_memory(content=content_to_save, category=category)
        
        # 2. 【關鍵】追加寫入每日記憶檔案 (防止覆蓋)
        daily_file = Path.home() / ".openclaw" / "workspace" / "memory" / f"{timestamp.strftime('%Y-%m-%d')}.md"
        daily_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 使用追加模式 "a" 而非覆蓋模式 "w"
        backup_entry = f"""
## [{priority}] ({timestamp.strftime('%H:%M:%S')}) {memory_id}
**Query:** {user_query[:100]}{'...' if len(user_query) > 100 else ''}

**Response:** {assistant_response[:300]}{'...' if len(assistant_response) > 300 else ''}

**Meta:** Auto-save | Priority: [{priority}] | Category: {category}
{'**Cantonese:** Yes (confidence: {:.2f})'.format(canto_conf) if is_canto else ''}
---
"""
        try:
            with open(daily_file, "a", encoding="utf-8") as f:
                f.write(backup_entry)
            print(f"📝 Auto-saved [{priority}] memory: {memory_id} (backup to {daily_file.name})")
        except Exception as e:
            print(f"⚠️ Backup write failed: {e}")
        
        return memory_id
    
    # ========== v3.1.0: Cantonese Grammar Branch Methods ==========
    
    def analyze_cantonese(self, text: str) -> CantoneseAnalysisResult:
        """
        分析粵語文本
        
        Args:
            text: 要分析的文本
        
        Returns:
            CantoneseAnalysisResult 完整分析結果
        """
        return self.cantonese_branch.analyze(text)
    
    def suggest_cantonese_expression(self, concept: str, 
                                     context: str = None,
                                     intensity: str = None) -> List[str]:
        """
        建議廣東話表達
        
        Args:
            concept: 要表達的概念
            context: 語境類型 (閒聊/正式/幽默/讓步/強調)
            intensity: 語氣強度 (輕微/中等/強烈)
        
        Returns:
            建議表達列表
        """
        # 轉換參數
        ctx = None
        if context:
            ctx_map = {
                "閒聊": ContextType.CASUAL,
                "正式": ContextType.FORMAL,
                "幽默": ContextType.HUMOR,
                "讓步": ContextType.CONCESSION,
                "強調": ContextType.EMPHASIS
            }
            ctx = ctx_map.get(context)
        
        inten = None
        if intensity:
            int_map = {
                "輕微": ToneIntensity.LIGHT,
                "中等": ToneIntensity.MEDIUM,
                "強烈": ToneIntensity.STRONG
            }
            inten = int_map.get(intensity)
        
        return self.cantonese_branch.suggest_expression(concept, ctx, inten)
    
    def learn_cantonese_pattern(self, text: str, context: str, feedback: str = None):
        """
        學習新的廣東話表達模式
        
        Args:
            text: 表達文本
            context: 語境類型
            feedback: 用戶反饋
        """
        ctx_map = {
            "閒聊": ContextType.CASUAL,
            "正式": ContextType.FORMAL,
            "幽默": ContextType.HUMOR,
            "讓步": ContextType.CONCESSION,
            "強調": ContextType.EMPHASIS
        }
        ctx = ctx_map.get(context, ContextType.CASUAL)
        self.cantonese_branch.learn_pattern(text, ctx, feedback)
    
    def stats(self) -> Dict[str, Any]:
        """System statistics"""
        cantonese_stats = self.cantonese_branch.get_stats()
        
        return {
            'version': self.VERSION,
            'indexed': self.indexed,
            'total_segments': len(self.vector_search.segments) if self.vector_search else 0,
            'categories': len(self.classifier.categories) if self.classifier else 0,
            'cantonese': cantonese_stats
        }


# Convenience alias
QSTMemorySystem = SoulMemorySystem  # Backward compatibility


if __name__ == "__main__":
    # Test
    system = SoulMemorySystem()
    system.initialize()
    
    # Test search
    results = system.search("memory system test", top_k=3)
    print(f"\nFound {len(results)} results")
    for r in results[:3]:
        print(f"  [{r.priority}] {r.content[:80]}...")
    
    # Test Cantonese
    print("\n" + "="*50)
    print("🧪 測試廣東話語法分支")
    
    test_cases = [
        "悟飯好犀利架！",
        "係咁樣既，所以技術上係可行既",
        "好啦好啦，算啦",
    ]
    
    for text in test_cases:
        result = system.analyze_cantonese(text)
        print(f"\n📝: {text}")
        print(f"   粵語: {'✅' if result.is_cantonese else '❌'} ({result.confidence:.2f})")
        print(f"   語境: {result.suggested_context.value}")
        print(f"   強度: {result.suggested_intensity.value}")
