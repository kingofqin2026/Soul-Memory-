<div align="center">

# 🧠 Soul Memory System v3.1.0

### Intelligent Memory Management System

**Long-term memory framework for AI Agents**

**🆕 v3.1.0 - 廣東話語法分支 | Cantonese Grammar Branch**

[![Python 3.7+](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![CJK Support](https://img.shields.io/badge/CJK-%E4%B8%AD%E6%97%A5%E9%9F%93-red.svg)]()
[![Cantonese](https://img.shields.io/badge/粵語-支援-orange.svg)]()

</div>

---

## ✨ Features

Seven powerful modules for complete memory management - **Now with CJK & Cantonese support!**

| Module | Function | Description |
|:-------:|:---------:|:------------|
| **A** | Priority Parser | `[C]/[I]/[N]` tag parsing + semantic auto-detection |
| **B** | Vector Search | Keyword indexing + CJK segmentation + semantic expansion |
| **C** | Dynamic Classifier | Auto-learn categories from memory |
| **D** | Version Control | Git integration + version rollback |
| **E** | Memory Decay | Time-based decay + cleanup suggestions |
| **F** | Auto-Trigger | Pre-response search + Post-response auto-save |
| **G** | **Cantonese Branch** | 🆕 語氣詞分級 + 語境映射 + 粵語檢測 |
| **Web** | Web UI | FastAPI dashboard with real-time stats, search & task monitoring |

---

## 🆕 v3.1.0 - 廣東話語法分支

### 🎯 功能概覽

| 功能 | 說明 |
|------|------|
| **語氣詞分級** | 輕微/中等/強烈 三級語氣控制 |
| **語境映射** | 閒聊/正式/幽默/讓步/強調 五種語境 |
| **粵語檢測** | 自動檢測文本中的粵語元素 |
| **表達建議** | 根據語境和強度建議最佳廣東話表達 |
| **模式學習** | 從對話中學習新的表達模式 |

### 📊 語氣強度等級

```
程度 1：輕微 → 架、啦、囉、喎、嘅
程度 2：中等 → 真係...啦、都...架、好啦、算啦
程度 3：強烈 → 好犀利架！、係晒架！、犀利到爆！
```

### 🎭 語境類型

| 語境 | 適用場景 | 常用表達 |
|------|---------|---------|
| **閒聊** | 輕鬆對話 | 架、啦、囉、犀利 |
| **正式** | 技術討論 | 係咁、所以、咁樣 |
| **幽默** | 輕鬆幽默 | 衰鬼、犀利到爆、搞掂晒 |
| **讓步** | 讓步語氣 | 好啦、算啦、咁啦 |
| **強調** | 強調語氣 | 真係、確實、老實講 |

---

### One-Line Installation

```bash
curl -sSL https://raw.githubusercontent.com/kingofqin2026/Soul-Memory-/main/install.sh | bash
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/kingofqin2026/Soul-Memory-.git
cd Soul-Memory-

# Run tests to verify
python3 test_all_modules.py
```

### Basic Usage

```python
from core import SoulMemorySystem

# Initialize the system
system = SoulMemorySystem()
system.initialize()

# Search memory
results = system.search("user preferences", top_k=5)

# Add new memory
memory_id = system.add_memory("[C] User prefers dark mode")

# Pre-response: search before answering
context = system.pre_response_trigger("What are the user's preferences?")

# Post-response: auto-save after answering
def after_response(user_query, assistant_response):
    memory_id = system.post_response_trigger(
        user_query, 
        assistant_response,
        importance_threshold="I"  # Save [I] or above
    )
```

---

## 📋 Feature Details

### Priority System

Level tags determine memory importance:

| Tag | Level | Behavior |
|-----|-------|----------|
| `[C]` | **Critical** | Never decays, always retained |
| `[I]` | **Important** | Slow decay, 90-day retention |
| `[N]` | **Normal** | Fast decay, 30-day retention |

### Keyword Search

**Pure local implementation** - no external APIs:

- ✅ Full-text keyword indexing
- ✅ Semantic synonym expansion
- ✅ Similarity scoring with priority weighting
- ✅ Category-based filtering

### Classification System

Default categories (fully customizable):

> **User_Identity** | **Tech_Config** | **Project** | **Science** | **History** | **General**

---

## 🏗️ Architecture

```
soul-memory-v3.0/
│
├── core.py                    # Core system orchestrator
├── modules/                   # 6 functional modules
│   ├── priority_parser.py    # [A] Priority parser
│   ├── vector_search.py      # [B] Vector search engine
│   ├── dynamic_classifier.py # [C] Dynamic classifier
│   ├── version_control.py    # [D] Git integration
│   ├── memory_decay.py       # [E] Decay algorithm
│   └── auto_trigger.py       # [F] Auto-trigger
│
├── cache/                     # Auto-generated cache
├── test_all_modules.py       # Full test suite
└── README.md                 # You are here 📖
```

---

## 🔒 Privacy & Security

> **Your data stays under your control**

- ✅ **No external API calls** - 100% offline-compatible
- ✅ **No cloud services** - No third-party dependencies
- ✅ **Domain isolation** - Complete data separation
- ✅ **Open source** - Transparent MIT License

---

## 📐 Technical Details

| Specification | Details |
|---------------|---------|
| **Python Version** | 3.7+ |
| **Dependencies** | None (pure Python standard library) |
| **Storage** | Local JSON files |
| **Search Engine** | Keyword matching + semantic expansion |
| **Classification** | Dynamic learning + preset rules |
| **Memory Format** | Markdown with priority tags |

---

## 🧪 Testing

Run the complete test suite:

```bash
python3 test_all_modules.py
```

### Expected Output

```
==================================================
🧠 Soul Memory System v2.1 - Test Suite
==================================================

📦 Testing Module A: Priority Parser...
  ✅ Priority Parser: PASS

📦 Testing Module B: Vector Search...
  ✅ Vector Search: PASS

📦 Testing Module C: Dynamic Classifier...
  ✅ Dynamic Classifier: PASS

📦 Testing Module D: Version Control...
  ✅ Version Control: PASS

📦 Testing Module E: Memory Decay...
  ✅ Memory Decay: PASS

📦 Testing Module F: Auto-Trigger...
  ✅ Auto-Trigger: PASS

==================================================
📊 Results: 7 passed, 0 failed
==================================================
✅ All tests passed!
```

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| **v3.0.0** | 2026-02-18 | **Web UI v1.0**: FastAPI dashboard + real-time stats + task monitoring + CJK + Post-Response |
| **v2.2.0** | 2026-02-18 | **CJK Intelligent Segmentation** for Chinese/Japanese/Korean, **Post-Response Auto-Save**, bug fixes |
| **v2.1.0** | 2026-02-17 | Rebranded as Soul Memory, removed sensitive content, technical neutralization, English localization |
| **v2.0.0** | 2026-02-17 | Self-hosted version with complete independence |
| **v1.9.1** | 2026-02-17 | Auto-Trigger module added |

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

---

<div align="center">

## 🙏 Acknowledgments

**Soul Memory System v3.0** is a **personal AI assistant memory management tool**, designed for personal use.

---

made with ❤️ by **kingofqin2026**

[⬆ Back to Top](#-soul-memory-system-v21)

</div>
