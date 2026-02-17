"""
Soul Memory System v2.1

智能記憶管理系統
"""

from .core import QSTMemorySystem
from .modules.priority_parser import PriorityParser, Priority
from .modules.vector_search import VectorSearch
from .modules.dynamic_classifier import DynamicClassifier
from .modules.version_control import VersionControl
from .modules.memory_decay import MemoryDecay
from .modules.auto_trigger import AutoTrigger, auto_trigger, get_memory_context

__version__ = "1.9.1"
__all__ = [
    "QSTMemorySystem",
    "PriorityParser", 
    "Priority",
    "VectorSearch",
    "DynamicClassifier",
    "VersionControl",
    "MemoryDecay",
    "AutoTrigger",
    "auto_trigger",
    "get_memory_context",
]
