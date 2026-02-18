#!/usr/bin/env python3
"""
Soul Memory Module B: Vector Search Engine
Local keyword-based semantic search (no external APIs)

Author: Soul Memory System
Date: 2026-02-17
"""

import json
import hashlib
import os
import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path


@dataclass
class SearchResult:
    """Search result"""
    content: str
    score: float
    source: str
    line_number: int
    category: str = ""
    priority: str = "N"


@dataclass
class MemorySegment:
    """Memory segment"""
    id: str
    content: str
    source: str
    line_number: int
    category: str = ""
    priority: str = "N"
    keywords: List[str] = field(default_factory=list)


class VectorSearch:
    """
    Vector Search Engine
    
    Local keyword-based semantic search.
    No external API dependencies.
    """
    
    # Generic semantic expansions (neutral)
    SEMANTIC_EXPANSIONS = {
        # User related
        "user": ["用戶", "user", "preferences"],
        "preferences": ["喜好", "偏好", "喜歡"],
        
        # Technical
        "config": ["配置", "設定", "settings", "configuration"],
        "api": ["API", "接口", "endpoint"],
        "memory": ["記憶", "memory", "context"],
        
        # Project
        "project": ["專案", "項目", "project"],
        "task": ["任務", "工作", "task"],
        "note": ["筆記", "記錄", "note"],
    }
    
    def __init__(self):
        self.segments: List[MemorySegment] = []
        self.keyword_index: Dict[str, List[str]] = {}
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text (支持中英文分词)"""
        # Remove markdown symbols
        text = re.sub(r"[#*_`\[\]()]", " ", text)
        # 在中文标点符号处添加空格，实现中文分词
        text = re.sub(r"([，。！？：；,《》【】（）])", r" \1 ", text)
        # Split by whitespace
        words = text.split()
        # Filter keywords (length >= 2)
        keywords = [w.lower() for w in words if len(w) >= 2]
        return list(set(keywords))
    
    def _expand_query(self, query: str) -> List[str]:
        """Expand query with semantic synonyms"""
        keywords = self._extract_keywords(query)
        expanded = set(keywords)
        
        for kw in keywords:
            if kw in self.SEMANTIC_EXPANSIONS:
                expanded.update(self.SEMANTIC_EXPANSIONS[kw])
        
        return list(expanded)
    
    def add_segment(self, segment: Dict[str, Any]):
        """Add a memory segment"""
        ms = MemorySegment(
            id=segment.get('id', hashlib.md5(segment['content'].encode()).hexdigest()[:8]),
            content=segment['content'],
            source=segment.get('source', 'unknown'),
            line_number=segment.get('line_number', 0),
            category=segment.get('category', ''),
            priority=segment.get('priority', 'N'),
            keywords=segment.get('keywords', self._extract_keywords(segment['content']))
        )
        self.segments.append(ms)
        
        # Update keyword index
        for kw in ms.keywords:
            if kw not in self.keyword_index:
                self.keyword_index[kw] = []
            self.keyword_index[kw].append(ms.id)
    
    def index_file(self, file_path: Path):
        """Index a memory file"""
        if not file_path.exists():
            return
        
        if file_path.is_dir():
            for f in file_path.glob("*.md"):
                self._index_single_file(f)
        else:
            self._index_single_file(file_path)
    
    def _index_single_file(self, file_path: Path):
        """Index a single file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            self.add_segment({
                'content': line,
                'source': str(file_path),
                'line_number': i + 1
            })
    
    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """Search memory"""
        query_keywords = self._expand_query(query)
        
        # Calculate scores
        scores: Dict[str, float] = {}
        for kw in query_keywords:
            if kw in self.keyword_index:
                for seg_id in self.keyword_index[kw]:
                    scores[seg_id] = scores.get(seg_id, 0) + 1
        
        # Normalize scores
        max_score = max(scores.values()) if scores else 1
        for seg_id in scores:
            scores[seg_id] /= max_score
        
        # Get top results
        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:top_k]
        
        results = []
        for seg_id in sorted_ids:
            for seg in self.segments:
                if seg.id == seg_id:
                    results.append(SearchResult(
                        content=seg.content,
                        score=scores[seg_id],
                        source=seg.source,
                        line_number=seg.line_number,
                        category=seg.category,
                        priority=seg.priority
                    ))
                    break
        
        return results
    
    def load_index(self, data: Dict[str, Any]):
        """Load index from data"""
        for seg in data.get('segments', []):
            self.add_segment(seg)
    
    def export_index(self) -> Dict[str, Any]:
        """Export index to data"""
        return {
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


if __name__ == "__main__":
    # Test
    vs = VectorSearch()
    vs.add_segment({'content': 'User prefers dark mode theme', 'category': 'preferences'})
    vs.add_segment({'content': 'API endpoint configured at localhost:8080', 'category': 'config'})
    
    results = vs.search('user preferences')
    for r in results:
        print(f"[{r.priority}] {r.score:.2f} {r.content}")
