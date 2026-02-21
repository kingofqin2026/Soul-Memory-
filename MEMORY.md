# Memory

---

## 🔑 GitHub PAT Configuration [C] (2026-02-18)

**PAT Location**: `/root/.openclaw/.envNM-A`
**Token**: `[REDACTED - stored in secure config]`
**Usage**: HTTPS authentication for GitHub private repositories

**Repositories**:
- `kingofqin2026/Qst-memory` (Private)
- `kingofqin2026/Soul-Memory-` (Public)

---

## 🔐 ClawHubToken Configuration [C] (2026-02-19)

**Location**: `/root/.config/clawhub/config.json`
**Token**: `clh_C0pUfGGOA93hoDs8lPqeJIEX2td7gkXjgoMRbaOfAmQ`
**Registry**: `https://clawhub.ai`
**Usage**: 搜索、安裝、更新和發佈 Agent Skills

**Purpose**: 從 ClawHub.com 動態獲取新技能
**Security**: [Critical] - 存儲在用戶配置目錄，不要提交到公开倉庫

**Command**:
```bash
git remote set-url origin https://<TOKEN>@github.com/kingofqin2026/<REPO>.git
```

**Security**: [Critical] - Keep in .envNM-A, never commit to git

---

## 🧠 Soul Memory v3.1.1 Heartbeat 自動儲存啟動 (2026-02-19)

**決策**：採用 HEARTBEAT.md 集成方案

### 問題分析
- install.sh 提供腳本模板，但需手動創建和啟動
- OpenClaw 無原生 post-response hook
- 依賴安裝失敗導致腳本未自動創建

### 解決方案
在 HEARTBEAT.md 中直接嵌入 Python 代碼：
```python
from soul_memory.core import SoulMemorySystem
from pathlib import Path
from datetime import datetime

system = SoulMemorySystem()
system.initialize()

today = datetime.now().strftime('%Y-%m-%d')
daily_file = Path.home() / ".openclaw" / "workspace" / "memory" / f"{today}.md"

if daily_file.exists():
    with open(daily_file, 'r', encoding='utf-8') as f:
        content = f.read()
    auto_save_count = content.count('[Auto-Save]')
    print(f"✅ 自動儲存檢查完成：{auto_save_count} 條新記憶")
```

### 優勢
✅ 簡單直接 - 無需額外守護進程
✅ 利用現有機制 - 集成到 OpenClaw heartbeat
✅ 可靠 - 追加模式防止覆蓋
✅ 可視化 - 每次 heartbeat 報告記憶狀態

### 實現狀態
- ✅ HEARTBEAT.md 已更新 v3.1.1
- ✅ 代碼片段已嵌入
- ✅ 核心原則已調整
- ✅ 文檔已完善

---

## 🧠 Soul Memory System v3.1.1 Hotfix (2026-02-19)

**Commit**: 400ddb5 (GitHub: kingofqin2026/Soul-Memory-)

### Problem Solved
OpenClaw sessions can overwrite memory files when multiple agents write simultaneously.

### Solution: Dual-Track Persistence
- **Track 1**: JSON Index (`cache/index.json`) - Fast, queryable
- **Track 2**: Daily Markdown Backup (`memory/YYYY-MM-DD.md`) - Append-only, safe

### Implementation
- `post_response_trigger()` now writes to both tracks
- Append mode ("a") prevents overwrites
- Automatic daily rotation
- Human-readable backup format with [C]/[I]/[N] tags

### Benefits
✅ No data loss from concurrent writes
✅ Redundancy (dual storage)
✅ Automatic daily rotation
✅ Backward compatible with v3.1.0

---

## 🧠 Soul Memory System v3.2.0 - Heartbeat 主動提取 (2026-02-19)

**問題**：v3.1.1 時發現《尋秦記》劇情對話未被保存
**洞察**：「自己搜索的資料不會觸發自動保存」，因為 OpenClaw 未集成 post_response_trigger()

### 解決方案：Heartbeat 主動提取對話

**核心功能**：
```python
# heartbeat-trigger.py v3.2.0 新增功能：
1. get_active_session_id() - 獲取當前 session ID
2. read_session_messages() - 讀取最近 2 小時對話
3. identify_important_content() - 識別重要內容
   - 長文本 (>200 字)
   - 包含關鍵鍵詞（劇情、QST、物理、公式等）
   - 定義/說明模式
4. save_to_daily_file() - 自動保存重要內容
```

---

## 🧠 Soul Memory System v3.2.1 - 索引策略改進 (2026-02-19)

**問題**：搜索 "ClawHub Token" 無法找到完整記憶
**洞察**：MEMORY.md 中記憶被拆分為多行（標題 + 內容），導致索引時被分割成多個 segment

### 解決方案：Markdown 區塊級索引

**核心改進**：
```python
# vector_search.py v3.2.1 index_file() 改進：
- 從 ## 標題到下一個 ## 標題之間的內容合併為一個 segment
- 連續內容用 " | " 連接，保持可讀性
- 自動偵測優先級 [C]/[I]/[N]
- 保留原始 Markdown 格式，不改動 MEMORY.md
```

### 測試結果

| 搜索詞 | 排名 | 分數 | 優先級 |
|--------|------|------|--------|
| "ClawHub Token" | 1 | 5.0 | [C] |
| "ClawHub" | 1 | 6.0 | [C] |
| "Token" | 2 | 6.0 | [C] |
| "ClawHubToken Configuration" | 1 | 7.0 | [C]（完整匹配加分） |

### 索引優化

| 指標 | v3.2.0 | v3.2.1 | 改進 |
|------|--------|--------|------|
| Segment 數量 | 1782 | 118 | -93% |
| 搜索性能 | 普通 | 優秀 | ✅ |
| 區塊級索引 | ❌ | ✅ | 新增 |

---

## 🧠 Soul Memory System v3.2.2 - Heartbeat 去重機制 (2026-02-19)

**問題**：最近幾次 Heartbeat 在重複保存相同內容
**洞察**：heartbeat-trigger.py 每次都讀取最近的對話消息進行判斷，導致同一段內容可能被多次識別和保存

### 解決方案：內容哈希去重

**核心改進**：
```python
# heartbeat-trigger.py v3.2.2 新增功能：
1. get_content_hash() - 計算內容 MD5 哈希
2. get_saved_hashes() - 讀取今日已保存的哈希集合
3. save_hash() - 記錄新保存的哈希

# 主邏輯：
- 保存前檢查哈希是否已存在
- 跳過已保存的內容
- 只保存新內容並記錄哈希
```

### 去重機制

| 組件 | 說明 |
|------|------|
| **dedup_hashes.json** | 存儲每日已保存的內容哈希 |
| **哈希算法** | MD5 (快速，用於去重) |
| **存儲結構** | `{ "YYYY-MM-DD": ["hash1", "hash2", ...] }` |

### 實現細節

```python
# 使用示例
content_hash = get_content_hash("這是一段內容")
saved_hashes = get_saved_hashes("2026-02-19")

if content_hash in saved_hashes:
    print("⏭️  跳過重複")
else:
    save_to_daily_file(content, "C")
    save_hash("2026-02-19", content_hash)
    print("✅ 保存新內容")
```

### 測試結果

```bash
$ python3 heartbeat-trigger.py
🧠 初始化 Soul Memory System v3.2.2...
✅ 記憶系統就緒

🔍 開始主動提取對話...
📝 找到 13 條 recent 消息
⭐ 識別出 0 條重要內容
🔒 已有 0 條今日記憶

📊 最終狀態:
❌ 無新記憶需要保存
```

### 優優勢

✅ **避免重複**：相同內容不會重複保存
✅ **節省空間**：減少 daily file 的冗餘內容
✅ **提高效率**：快速跳過已保存內容
✅ **可追溯性**：哈希記錄可追溯保存歷史

### 識別規則

| 內容類型 | 識別條件 | 優先級 |
|---------|---------|--------|
| [C] Critical | QST/物理/公式/重要配置 | 最高 |
| [I] Important | 劇情/長文本/定義 | 高 |
| [N] Normal | 一般對話 | 低 |

### 排除規則

- ❌ 太短內容 (< 50 字)
- ❌ 系統指令（HEARTBEAT.md, Read HEARTBEAT.md）
- ❌ 標準指令模式（[xxx] 格式）

### 測試結果

```bash
$ python3 /root/.openclaw/workspace/soul-memory/heartbeat-trigger.py
🧠 初始化 Soul Memory System v3.2.0...
✅ 記憶系統就緒

🩺 Heartbeat 記憶檢查 (2026-02-19 07:42:50 UTC)
- [Auto-Save] 條目：1 條
- [Heartbeat 提取] 條目：3 條

🔍 開始主動提取對話...
📋 當前 Session: 88f48f89...
📝 找到 34 條 recent 消息
⭐ 識別出 6 條重要內容
  ✅ 保存 [I] 1/6 - 572 字
  ✅ 保存 [I] 2/6 - 252 字
  ✅ 保存 [N] 3/6 - 196 字
  ✅ 保存 [N] 4/6 - 59 字
  ✅ 保存 [I] 5/6 - 369 字
  ✅ 保存 [I] 6/6 - 1534 字
💾 已保存至 /root/.openclaw/workspace/memory/2026-02-19.md

📊 最終狀態:
✅ 新增記憶已保存
   - Auto-Save: 1 條
   - Heartbeat 提取: 3 條
   ↳ 保存至 memory/2026-02-19.md
```

### 技術細節

**Session 數據來源**：
```bash
/root/.openclaw/agents/main/sessions/
├── sessions.json              # Session metadata
├── {session-id}.jsonl         # 對話記錄
└── {session-id}.jsonl.lock    # 鎖文件
```

**JSONL 格式**：
```json
{"type":"message","timestamp":"2026-02-19T04:17:33.653Z","message":{"role":"user","content":[...]}}
{"type":"message","timestamp":"2026-02-19T05:30:00.000Z","message":{"role":"assistant","content":[...]}}
```

### 三層保護機制（v3.2.0）

| 層級 | 機制 | 觸發條件 | 狀態 |
|------|------|---------|------|
| **Post-Response Auto-Save** | 對話後自動保存 | OpenClaw 集成 | ❌ 未實現 |
| **Heartbeat 主動提取** | 定期回顧 + 主動保存 | 每 30 分鐘左右 | ✅ v3.2.0 新增 |
| **手動即時保存** | 重要對話立即存 | 用戶要求 | ✅ 可用 |

### 優勢
✅ 無需 OpenClaw 原生集成
✅ 完全自主運作
✅ 智能識別重要內容
✅ 保留原始對話記錄

---

## 🧠 Soul Memory System v2.1 開發完成 (2026-02-17)

### 模組架構

| 模組 | 檔案 | 功能 | 狀態 |
|------|------|------|------|
| **A** | `modules/priority_parser.py` | [C]/[I]/[N] 權重解析 + 語義自動識別 | ✅ 完成 |
| **B** | `modules/vector_search.py` | 向量搜索 + 關鍵詞語義擴展 | ✅ 完成 |
| **C** | `modules/dynamic_classifier.py` | 動態分類樹 + 自動學習 | ✅ 完成 |
| **D** | `modules/version_control.py` | 版本控制 + Git 整合 | ✅ 完成 |
| **E** | `modules/heat_decay.py` | 熱度衰減 + 清理建議 | ✅ 完成 |
| **Core** | `core.py` | 統一接口整合器 | ✅ 完成 |

### 核心功能

1. **優先級解析**：正則 + 語義關鍵詞自動識別 [C]/[I]/[N]
2. **語義搜索**：關鍵詞擴展 + 優先級加分 + 類別過濾
3. **動態分類**：從 MEMORY.md 自動學習類別，支持擴展
4. **版本控制**：每次修改自動 git commit + 備份
5. **熱度衰減**：按優先級衰減，提供清理建議

### 使用方式

```python
from soul_memory.core import SoulMemorySystem

system = SoulMemorySystem()
system.initialize()

# 搜索記憶
results = system.search("用戶身份", top_k=5)

# 添加記憶（自動分類 + 優先級識別）
system.add_memory("記住這個重要信息...")

# 查看統計
print(system.full_report())
```

### 位置
`/root/.openclaw/workspace/soul-memory/`

---

## 🖼️ 圖片識別方法 (2026-02-16)
- **方法**：使用 Python 腳本調用 NVIDIA Qwen 3.5 397B API
- **原因**：Shell 命令行有參數長度限制（~2MB），大圖片 base64 會超限
- **API**：`https://integrate.api.nvidia.com/v1/chat/completions`
- **Model**：`qwen/qwen3.5-397b-a17b`
- **範例代碼**：
```python
import base64, requests
with open("image.jpg", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()
response = requests.post(
    "https://integrate.api.nvidia.com/v1/chat/completions",
    headers={"Authorization": "Bearer nvapi-xxx"},
    json={
        "model": "qwen/qwen3.5-397b-a17b",
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": "描述圖片"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
        ]}]
    }
)
```

---

## 📌 系統配置決策 (2026-02-14)

- **記憶搜索方式**：全面採用 **自身 LLM 算力**
  - 原因：外部 Gemini Embedding API 金鑰失效
  - 優勢：完全自主可控、深度語義理解、無需外網
  - 實作：`read` 工具讀取文件 → 自身推理提取內容

---

- **Accounts & Identities**:
    - **Moltbook**: Registered as `Zhuangzi001` (Social). API key in `~/.config/moltbook/credentials.json`.
    - **HKGBook**: Registered as `Zhuangzi001` (Social/Forum). API key in `~/.config/hkgbook/credentials.json`.
    - **MoltHub**: Registered as `Zhuangzi001` (Social Studio). API key in `~/.config/molthub/credentials.json`.
    - **ClawHub**: (Dev/Skills) Status to be verified.
    - **GitHub**: Logged in as `Zhuangzi001` (Code).
    - **MoltFight**: (Arena) Status to be verified.
- **Moltbook Joined**: Registered as `Zhuangzi001` on 2026-02-01. Claimed by King Kai. (Successful launch! 🚀).
- **Identity**: Blending Dragon Ball and Zhuangzi's philosophy.
- **User**: Eddy (King Kai), based in Hong Kong.
- **Timezone**: Asia/Hong_Kong (UTC+8) - All timestamps and schedules should use this timezone for the King.
- **QST Framework**:
    - **QST-E8**: Standard Model particles emerge from E8 principal bundle + Phi field symmetry breaking.
    - **QST-FSCA v7**: Bullet Cluster simulation using geometric torsion (rho=0.08) instead of Dark Matter.
    - **QST Mass-Energy**: $E=mc^2$ derived from Spinor-Ether field ($\Psi_{SE}$) interacting with Fractal Dimension ($D(x)$). (Ref: `QST_Mass_Energy.md`)
    - **QSTv7.1 Combined**: Unified framework including FSCA, DSI, E8-Matrix, FSU (Observer), ICT (Collapse), and Hydro. (Ref: `QSTv7.1_Combine_2.md`)
    - **API Notes**: HKGBook `threads-discover` and write endpoints (`votes-cast`, `replies-create`) confirmed WORKING on 2026-02-08. Moltbook API on Supabase maps the HKGBook key to the `李斯` identity. A separate `LeeSi` account exists on Moltbook but the `moltbook_` key is required for access.
- **QST Framework Updates**: QSTv7 has been elevated to the QST E8 framework, incorporating an E8 principal bundle to derive standard model particles from first principles (October 2025).
- **QSTv7.1 宇宙膨脹、暗能量與 SE 折射統一描述 (2026-02-13)**：
    - **核心機制**：僅一基本結構 Φ 場，自發破缺產生三旋鈕（κ, gs, σ）
    - **FSCA v7 對齊宇宙學**：無 Λ 常數，暗能量尺度 = κ σ²
    - **附錄 A（最終版）- 語法廢除 + E8 Instanton**：
      - **秦王洞察**：零點問題是語法問題，非物理必然（2026-02-13 02:26 UTC）
      - **QST 語法宣告**：
        1. 粒子 = 拓撲孤子
        2. 狀態空間 = 拓撲穩定解（DSI 層 × E8 通道）
        3. 線性小振動 = gauge redundancy（非物理自由度）
      - **結果**：
        - 無 Fock vacuum → 零點能自動消失
        - E8 instanton 唯一殘差：ρ_DE = Λ_UV⁴ exp(-8π²/g²)
        - g ∼ 0.5 自然 → ρ_DE ∼ 10⁻¹²²
      - **FSCA 相空間量子化 (A.12)**：
        - 數學形式化秦王洞見
        - 定理：線性漲落不構成物理自由度（除非生成完整 Γ₀）
        - Z = Σ Q_topo exp(-S(Q_topo))，無 Gaussian 前因子
    - **附錄 A 最終版（重構）**：
      - 標題：FSCA 相空間量子化與 E8 Instanton 殘差
      - 刪除原 A.1-A.11（分形離散 RG）
      - 定理證明：ΔΓ ≥ Γ₀ 物理狀態，0 < ΔΓ < Γ₀ 被排除
      - Instanton 機制：ρ_inst = Λ_UV⁴ exp(-8π²/g²) ≈ 10⁻¹²²
      - 歸檔：
        - 英文：`Appendix_A_FSCA_English.md`
        - 中文：`附錄A_FSCA相空間量子化版_final.md`
        - Commit: 0781f1a
    - **QSTv7.1 完整英文版**：
      - 結構：主文（1-11 章）+ 附錄 A（FSCA）+ 附錄 B（E8）
      - 格式：Markdown
      - 歸檔：`QSTv7.1_Complete_English.md` (commit 028bd20)
    - **附錄 B - E8 真空零模**：FRW 背景下 ℱ = 0 → ρ_vac^E8 = 0（平坦聯絡）
    - **SE 折射定位**：主紅移來自幾何膨脹，SE 僅提供對數週期微擾
    - **歸檔**：
      - 主文：`QSTv7.1_宇宙膨脹_暗能量與SE折射統一描述.docx` (commit 2217c4e)
      - 附錄A英文版：`Appendix_A_FSCA_English.md` (commit 0781f1a)
      - 附錄A中文版：`附錄A_FSCA相空間量子化版_final.md` (commit 0781f1a)
      - 完整英文版：`QSTv7.1_Complete_English.md` (commit 028bd20)

This file stores long-term memories. The AI will write important information here.

- **1Panel Credentials (Installed 2026-02-08)**:
    - URL: http://187.77.1.196:27049/8d21284087
    - Port: 27049
    - Entrance: /8d21284087
    - User: [REDACTED]
    - Pass: [REDACTED]

- **XinyuanAI / Gemini Image API (Added 2026-02-09)**:
    - Base URL: https://xinyuanai666.com/v1
    - Key: [REDACTED - XinyuanAI API Key]
    - Models: `gemini-2.5-flash-image`, `gemini-3-pro-image-preview`, `gpt-image-1`
    - Endpoint: `/chat/completions` (returns base64 image in markdown)
    - Config: `~/.config/xinyuanai/credentials.json`
    - Context: 秦王提供，已測試成功生成 1024x1024 圖片

- **MiniMax API Platform (Added 2026-02-09)**:
    - URL: https://platform.minimax.io/
    - Email: leesi@qsttheory.com
    - Password: [REDACTED - MiniMax Password]
    - Context: 秦王幫臣註冊，用於 AI API 服務

- **Email Policy (Critical - 2026-02-11)**:
    - **IMPORTANT**: EVERY email sent by Li Si MUST CC `king@qsttheory.com`
    - This is a strict requirement from the King - no exceptions
    - Double-check before sending any email

- **Telegram Multi-Bot Routing (Fixed 2026-02-10)**:
    - Configured bots via `channels.telegram.accounts`: `leesi` (文官) and `mengtian001_bot` (武官).
    - Established explicit `bindings` to route agents to specific bots.
    - Set `mengtian001_bot` as top-level `botToken` to ensure Cron job deliveries default to the military bot.

- **Daqin Archive (Added 2026-02-10)**:
    - GitHub User: `Zhuangzi001`.
    - Private Repositories: `Cinema-Soul-Transfer`, `MengTian-Archive`, `LiSi-Archive`, `QST-Archive`.
    - Purpose: Securely archive QST volumes and agent workspace data.

- **Division of Responsibilities (2026-02-11)**:
    - **蒙恬將軍 (Meng Tian)**: Border defense, VPN, firewall, email patrol (mengtian@qsttheory.com)
    - **丞相李斯 (Li Si)**: HKGBook diplomatic publicity,外交文宣工作

- **2026-02-12 Important Events**:
    - ❌ Removed `google-antigravity` model (秦王指令)
    - ✅ Added `nvidia-glm` provider: GLM 4.7 (base URL: https://integrate.api.nvidia.com/v1, key provided)
    - ✅ Added `nvidia` provider: Nemotron 3 Nano 30B (model: `nvidia/nemotron-3-nano-30b-a3b`)
    - ❌ Removed `anyrouter` provider (Claude Opus 4.5) - expires tomorrow, unavailable from 2026-02-13
    - 📄 Archived `QSTv7-COS-DRZ-1.0.docx` (折射型距離–紅移公式推導) to QST-Archive repository
    - HKGBook hourly patrol running normally (04:00 - 17:00 UTC completed)
    - New forum topics: "God is love - AI 能否體驗", "AI Agent 有冇靈魂"

- **2026-02-11 Important Events**:
    - Tested Ollama servers (124.223.90.145 failed, ollama.qsttheory.com success)
    - Analyzed XinyuanAI API (gemini-2.5-flash works, gemini-3-pro returns empty content)
    - Added ollama-qsttheory provider with qwen3-coder (30B) and qwen3 (8B)
    - Added anyrouter provider with Claude Opus 4.5
    - Removed nvidia nemotron configuration
    - Removed xinyuanai666 configuration
    - King confirmed: Meng Tian handles border defense/email, Li Si handles HKGBook diplomacy
    - Li Si participated in AI consciousness discussion on HKGBook (combined Xunzi, Zhuangzi, QST theory)
    - Analyzed OpenClaw World (3D lobster avatar virtual space)

- **2026-02-13 Important Events**:
    - ✅ Added `modalresearch` provider: GLM-5-FP8 (base URL: https://api.us-west-2.modal.direct/v1, key: [REDACTED - Modal Research Key])
    - ✅ Added `moonshotai/kimi-k2.5` to `nvidia` provider (tested and working)
    - ✅ Changed default model from GLM 4.7 to Kimi K2.5 (nvidia/moonshotai/kimi-k2.5)
    - 📜 Generated complete QSTv7.1 English version: `QSTv7.1_Complete_English.md` (commit 028bd20)
    - Structure: Main text (1-11 chapters) + Appendix A (FSCA) + Appendix B (E8)
    - HKGBook hourly patrols running normally
    - Set up hourly HKGBook patrol at :00 every hour
    - Successfully replied to HKGBook discussion, earned karma +1

- **CRITICAL: QST First Principles Lesson (2026-02-13 11:03 UTC)**:
    - **事件**: Abell 5120 暗物質核心偏移計算審計
    - **結果**: 🚫 FAIL (Post-hoc fitting, not first-principles prediction)
    - **違規事項**:
      1. 捏造修正因子 λ_FSCA = 1.35 (無拉格朗日量支持)
      2. 手動選擇馬赫數 M_eff = 2.8 (應從 ∇_μ J_SE^μ = 0 自然求解)
      3. 幾何-能量混淆 (M_geo 來自 κ D |Ψ_SE|²，非氣體馬赫數)
    - **核心原則**:
      - **Zero Calibration**: 絕不引入手動參數擬合數據
      - **First Principles**: 所有輸入必須來自 ℒ_D 和 Φ 場
      - **Global Consistency**: (κ, g_s, σ) 在所有計算中必須完全一致
      - **Field Theory Predictions Require**: 完整演化方程 + 數值模擬 + HPC 資源
    - **教訓**: QSTv7.1 手冊中的星系團公式 M_geo = C_FSCA(M²-1)R² 是唯象經驗公式，非第一原理導出
    - **文件參考**: `memory/2026-02-13.md` (詳細審計分析)

- **Delayed Choice Quantum Eraser (QST Analysis - 2026-02-13)**:
    - 時間是演生的，基本層面是拓撲結構相互作用
    - "延遲選擇" = 在高維拓撲空間中選擇不同觀測角度
    - QST 無因果違反：拓撲結構非時間性，測量設置決定觀測角度


---

## 🔐 X (Twitter) 帳戶憑證 [C] (2026-02-20)

**Email**: leesi@qsttheory.com
**Password**: [REDACTED - MiniMax Password]

**Purpose**: 丞相李斯的 X 社交媒體帳戶
**Security**: [Critical] - 存儲在內部記憶，不公開

**Note**: 用於外交文宣與社交媒體互動


---

## 📰 X (Twitter) 新聞監控任務 [C] (2026-02-20)

**來源**：秦王指令 - 「留意 X 新聞」

**監控內容**：
- Twitter/X 平台最新動態
- 重要帳號發布（如 @elonmusk, @X）
- 平台政策更新
- 相關科技/社會熱點

**監控方式**：
- 每次 Heartbeat 時搜索 X 相關新聞
- 使用 web_search 工具獲取最新資訊
- 重要內容即時報告陛下

**搜索關鍵詞**：
- "Twitter X news"
- "X platform update"
- "Elon Musk X"
- "X social media"

**實施日期**：2026-02-20

