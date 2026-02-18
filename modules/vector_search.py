#!/usr/bin/env python3
"""
Soul Memory Module B: Vector Search Engine (v2.2)
Local keyword-based semantic search with CJK support
Author: Soul Memory System
Date: 2026-02-18
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
    Vector Search Engine v2.2
    - CJK intelligent segmentation (无需外部依赖)
    - Local keyword-based semantic search
    """
    
    VERSION = "2.2.0"
    
    # CJK Unicode ranges
    CJK_RANGES = [
        (0x4E00, 0x9FFF),
        (0x3400, 0x4DBF),
        (0x3040, 0x309F),
        (0x30A0, 0x30FF),
    ]
    
    SEMANTIC_EXPANSIONS = {
        "user": ["用戶", "user", "preferences"],
        "preferences": ["喜好", "偏好", "喜歡"],
        "config": ["配置", "設定", "settings"],
        "api": ["API", "接口", "endpoint"],
        "memory": ["記憶", "memory", "context"],
        "project": ["專案", "項目", "project"],
        "task": ["任務", "工作", "task"],
    }

    def __init__(self):
        self.segments: List[MemorySegment] = []
        self.keyword_index: Dict[str, List[str]] = {}

    def _is_cjk(self, char: str) -> bool:
        """Check if character is CJK"""
        code = ord(char)
        for start, end in self.CJK_RANGES:
            if start <= code <= end:
                return True
        return False

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords (v2.2 CJK智能分词)"""
        text = re.sub(r"[#*_`\[\](){}]", " ", text)
        
        result = []
        current_word = ""
        
        for char in text:
            if self._is_cjk(char):
                if current_word:
                    result.append(current_word)
                    current_word = ""
                result.append(char)
            elif char.isalnum():
                current_word += char
            else:
                if current_word:
                    result.append(current_word)
                    current_word = ""
        
        if current_word:
            result.append(current_word)
        
        keywords = []
        i = 0
        while i < len(result):
            word = result[i]
            if len(word) >= 1:
                keywords.append(word.lower())
            # Create bigram for adjacent CJK characters (single chars only)
            if i + 1 < len(result) and len(word) == 1 and len(result[i+1]) == 1:
                if self._is_cjk(word) and self._is_cjk(result[i+1]):
                    bigram = word + result[i+1]
                    keywords.append(bigram.lower())
            i += 1
        
        seen = set()
        filtered = []
        for k in keywords:
            if k not in seen and len(k) >= 1:
                seen.add(k)
                filtered.append(k)
        
        return filtered

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
        
        for kw in ms.keywords:
            if kw not in self.keyword_index:
                self.keyword_index[kw] = []
            self.keyword_index[kw].append(ms.id)

    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """Search memory with CJK support"""
        query_keywords = self._expand_query(query)
        scores = {}
        
        for kw in query_keywords:
            if kw in self.keyword_index:
                for seg_id in self.keyword_index[kw]:
                    scores[seg_id] = scores.get(seg_id, 0) + 1
        
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        results = []
        
        for seg_id, score in sorted_scores[:top_k]:
            seg = next((s for s in self.segments if s.id == seg_id), None)
            if seg:
                results.append(SearchResult(
                    content=seg.content,
                    score=score,
                    source=seg.source,
                    line_number=seg.line_number,
                    category=seg.category,
                    priority=seg.priority
                ))
        
        return results

    def index_file(self, file_path: Path):
        """Index a markdown file"""
        if not file_path.exists():
            return
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        current_category = ""
        current_priority = "N"
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('#'):
                current_category = line.lstrip('#').strip()
                continue
            
            if '[C]' in line:
                current_priority = 'C'
            elif '[I]' in line:
                current_priority = 'I'
            elif '[N]' in line:
                current_priority = 'N'
            
            segment = {
                'content': line,
                'source': str(file_path),
                'line_number': i,
                'category': current_category,
                'priority': current_priority
            }
            self.add_segment(segment)

    def export_index(self) -> Dict[str, Any]:
        """Export index to dict"""
        return {
            'version': self.VERSION,
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

    def load_index(self, data: Dict[str, Any]):
        """Load index from dict"""
        self.segments = []
        self.keyword_index = {}
        for seg_data in data.get('segments', []):
            ms = MemorySegment(
                id=seg_data.get('id', ''),
                content=seg_data.get('content', ''),
                source=seg_data.get('source', ''),
                line_number=seg_data.get('line_number', 0),
                category=seg_data.get('category', ''),
                priority=seg_data.get('priority', 'N'),
                keywords=seg_data.get('keywords', [])
            )
            self.segments.append(ms)
            for kw in ms.keywords:
                if kw not in self.keyword_index:
                    self.keyword_index[kw] = []
                self.keyword_index[kw].append(ms.id)