#!/usr/bin/env python3
"""
Soul Memory System v2.1 - Core Orchestrator
智能記憶管理系統核心
Author: Personal AI Assistant
Date: 2026-02-17

A lightweight, self-hosted memory system for AI assistants.
No external dependencies. No cloud services required.
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
    Soul Memory System v2.1
    
    Features:
    - Priority-based memory management [C]/[I]/[N]
    - Semantic keyword search (local, no external APIs)
    - Dynamic category classification
    - Automatic version control
    - Memory decay & cleanup
    - Pre-response auto-trigger
    """
    
    VERSION = "2.1.0"
    
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
            print(f"   Loaded index with {len(data.get('segments', []))} segments")
        else:
            print("   Building index...")
            memory_files = [
                Path.home() / ".openclaw" / "workspace" / "MEMORY.md",
                Path.home() / ".openclaw" / "workspace" / "memory"
            ]
            for memory_file in memory_files:
                if memory_file.exists():
                    self.vector_search.index_file(memory_file)
            
            # Save index
            data = self.vector_search.export_index()
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"   Built index with {len(data.get('segments', []))} segments")
        
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
            'priority': parsed.priority_tag,
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
    
    def stats(self) -> Dict[str, Any]:
        """System statistics"""
        return {
            'version': self.VERSION,
            'indexed': self.indexed,
            'total_segments': len(self.vector_search.segments) if self.vector_search else 0,
            'categories': len(self.classifier.categories) if self.classifier else 0
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
