# Soul Memory System v2.1

🧠 **智能記憶管理系統** - AI Agent長期記憶框架

## ✨ 特性

| 模組 | 功能 | 說明 |
|------|------|------|
| **A: 優先級解析器** | Priority Parser | [C]/[I]/[N] 標籤解析 + 語義自動識別 |
| **B: 向量搜索** | Vector Search | 關鍵詞索引 + 語義擴展搜索（本地） |
| **C: 動態分類** | Dynamic Classifier | 自動學習類別 |
| **D: 版本控制** | Version Control | Git 整合 + 版本回滾 |
| **E: 記憶衰減** | Memory Decay | 時間衰減 + 清理建議 |
| **F: 自動觸發** | Auto-Trigger | 回答前自動搜索記憶 |

## 🚀 快速開始

### 安裝

```bash
curl -sSL https://qsttheory.com/install-soul-v21.sh | bash
```

### 手動安裝

```bash
# 下載
wget -r -np -nH --cut-dirs=1 https://qsttheory.com/soul-memory-v2.1/
cd soul-memory-v2.1

# 測試
python3 test_all_modules.py
```

### 使用

```python
from core import SoulMemorySystem

# 初始化系統
system = SoulMemorySystem()
system.initialize()

# 搜索記憶
results = system.search("user preferences", top_k=5)

# 添加記憶
memory_id = system.add_memory("[C] User likes dark mode")

# 自動觸發（回答前）
context = system.pre_response_trigger("What are user preferences?")
```

## 📋 功能詳解

### 優先級系統

- **[C] Critical**: 關鍵信息，必須記住
- **[I] Important**: 重要項目，需要關注
- **[N] Normal**: 日常閒聊，可衰減

### 關鍵詞搜索

本地化實現，無需外部 API：
- 關鍵詞索引
- 同義詞擴展
- 相似度評分

### 分類系統

默認分類（可自定義）：
- User_Identity（用戶身份）
- Tech_Config（技術配置）
- Project（專案）
- Science（科學）
- History（歷史）
- General（一般）

## 🏗️ 架構

```
soul-memory-v2.1/
├── core.py           # 核心系統
├── modules/          # 6大功能模組
│   ├── priority_parser.py
│   ├── vector_search.py
│   ├── dynamic_classifier.py
│   ├── version_control.py
│   ├── memory_decay.py
│   └── auto_trigger.py
├── cache/            # 快取目錄（自動生成）
├── test_all_modules.py  # 測試套件
└── README.md         # 文檔
```

## 🔒 隱私與安全

- ✅ 無外部 API 調用
- ✅ 無雲服務依賴
- ✅ 跨域隔離，不共享數據
- ✅ 開源 MIT License

## 📐 技術細節

- **Python 版本**: 3.7+
- **依賴**: 無外部依賴（純 Python 標準庫）
- **存儲**: 本地 JSON 文件
- **搜索**: 關鍵詞匹配 + 語義擴展
- **分類**: 動態學習 + 預設規則

## 🧪 測試

```bash
python3 test_all_modules.py
```

預期輸出：
```
==================================================
🧠 Soul Memory System v2.1 - Test Suite
==================================================

📦 Testing Module A: Priority Parser...
  ✅ Priority Parser: PASS

📦 Testing Module B: Vector Search...
  ✅ Vector Search: PASS

...
==================================================
📊 Results: 7 passed, 0 failed
==================================================
✅ All tests passed!
```

## 📝 版本歷史

- **v2.1.0** (2026-02-17): 重命名為 Soul Memory，移除敏感內容，技術中性化
- **v2.0.0** (2026-02-17): 自托管版本
- **v1.9.1**: Auto-Trigger 模組

## 📄 授權

MIT License - 詳見 LICENSE

## 🙏 鳴謝

Soul Memory System v2.1 是一個**個人 AI 助手記憶管理工具**，專為個人使用而設計，非社交媒體操作工具。

---

© 2026 Soul Memory System
