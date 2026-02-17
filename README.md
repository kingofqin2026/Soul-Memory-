# Soul Memory System v2.1

🧠 **智能記憶管理系統** - 專為 AI Agent 設計的長期記憶框架

## 📦 一键安装

```bash
curl -sSL https://qsttheory.com/install-soul.sh | bash
```

或手动安装：

```bash
git clone https://github.com/kingofqin2026/Soul-Memory.git
cd Soul-Memory
python3 test_all_modules.py
```

## ✨ 核心功能

| 模組 | 功能 | 说明 |
|------|------|------|
| **A: 權重解析器** | Priority Parser | [C]/[I]/[N] 標籤解析 + 語義自動識別 |
| **B: 向量搜索** | Vector Search | 關鍵詞索引 + 語義擴展搜索 |
| **C: 動態分類** | Dynamic Classifier | 自動學習類別 + Selection Rule |
| **D: 版本控制** | Version Control | Git 整合 + 版本回滾 |
| **E: 熱度衰減** | Memory Decay | 時間衰減 + 訪問加權 |
| **F: 自動觸發** | Auto-Trigger | 回答前自動搜索記憶 |

## 🚀 快速开始

```python
from core import SoulMemorySystem

# 初始化系統
system = SoulMemorySystem()
system.initialize()

# 回答前自動觸發（Pre-Response Auto-Trigger）
context = system.pre_response_trigger("用戶問題")
# 返回相關記憶，確保回答有上下文支持

# 搜索記憶
results = system.search("灵魂理论", top_k=5)
for r in results:
    print(f"[{r.priority}] {r.content}")

# 添加記憶
system.add_memory("[C] 重要決策：記住這個配置", priority="C")

# 系統報告
print(system.full_report())
```

## 🔧 Auto-Trigger 使用方式

### 在 AGENTS.md 中加入（確保每次回答前執行）

```markdown
## 🧠 Pre-Response Auto-Trigger (回答前必執行)

**每次回答用戶問題前，執行以下流程：**

```python
from core import SoulMemorySystem
system = SoulMemorySystem()
results = system.pre_response_trigger("<用戶問題>")
```

### Selection Rule

| 用戶問題類型 | 優先搜索類別 |
|--------------|--------------|
| 灵魂理论/量子物理 | Soul_Physics, Soul_Computation |
| 用戶身份/偏好 | User_Identity |
| 系統配置 | Tech_Config |
| HKGBook 外交 | HK_Forum |
| 龍珠/動漫 | Dragon_Ball |
```

## 📁 專案結構

```
memory-system/
├── core.py                    # 統一接口
├── modules/
│   ├── priority_parser.py     # 模組 A: 權重解析
│   ├── vector_search.py       # 模組 B: 向量搜索
│   ├── dynamic_classifier.py  # 模組 C: 動態分類
│   ├── version_control.py     # 模組 D: 版本控制
│   ├── memory_decay.py        # 模組 E: 熱度衰減
│   └── auto_trigger.py        # 模組 F: 自動觸發
├── tests/                     # 單元測試
├── cache/                     # 索引快取
└── backups/                   # 版本備份
```

## 🎯 優先級系統

| 標籤 | 優先級 | 說明 | 衰減 |
|------|--------|------|------|
| `[C]` | Critical | 重要決策、核心配置 | 永不衰減 |
| `[I]` | Important | 專案進展、約定事項 | 慢衰減 (90天) |
| `[N]` | Normal | 日常閒聊、問候 | 快衰減 (30天) |

## 📊 測試結果

```
✅ A: 權重解析器 - 5/5 通過
✅ B: 向量搜索 - 3/3 通過
✅ C: 動態分類樹 - 2/2 通過
✅ D: 版本控制器 - 通過
✅ E: 熱度衰減 - 通過
✅ F: 自動觸發 - 通過
✅ 整合測試 - 通過
```

## 🔄 v2.0 → v2.1 更新内容

- ✅ 重命名为 Soul Memory System
- ✅ 更新核心类名为 SoulMemorySystem
- ✅ 优化 Selection Rule 分类
- ✅ 增强记忆搜索准确性
- ✅ 改进 Auto-Trigger 性能

## 🔧 CLI 使用

```bash
# 完整系統測試
python3 core.py

# Auto-Trigger 測試
python3 modules/auto_trigger.py

# 版本控制
python3 modules/version_control.py list 10
```

## 📜 License

MIT License - Soul Memory Project

## 👤 Author

界王 (King Kai) - Soul Memory Team

---

*为灵魂存储而生* 🧠
