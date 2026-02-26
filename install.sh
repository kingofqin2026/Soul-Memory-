#!/bin/bash

################################################################################
# Soul Memory System v3.3 - Installation Script
#
# 功能：自動安裝 Soul Memory 系統 + OpenClaw Plugin + Heartbeat 自動儲存
# 用法：bash install.sh [--dev] [--path /custom/path] [--with-plugin] [--rebuild-index]
################################################################################

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置變數
INSTALL_PATH="${HOME}/.openclaw/workspace/soul-memory"
DEV_MODE=false
INSTALL_PLUGIN=true
REBUILD_INDEX=false
OPENCLAW_EXTENSIONS="${HOME}/.openclaw/extensions"
PYTHON_MIN_VERSION="3.7"

################################################################################
# 函數定義
################################################################################

print_header() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║   🧠 Soul Memory System v3.3 - Installation Script            ║${NC}"
    echo -e "${BLUE}║   CLI + Heartbeat v3.3 + OpenClaw Plugin Support            ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_step() {
    echo -e "${BLUE}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

check_python() {
    print_step "檢查 Python 環境..."

    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 未安裝"
        echo "請先安裝 Python 3.7 或更高版本"
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    print_success "Python 版本: $PYTHON_VERSION"
}

check_git() {
    print_step "檢查 Git 環境..."

    if ! command -v git &> /dev/null; then
        print_error "Git 未安裝"
        echo "請先安裝 Git"
        exit 1
    fi

    GIT_VERSION=$(git --version | awk '{print $3}')
    print_success "Git 版本: $GIT_VERSION"
}

check_openclaw() {
    print_step "檢查 OpenClaw 安裝..."

    if [ ! -d "${HOME}/.openclaw" ]; then
        print_warning "OpenClaw 未安裝，將跳過 Plugin 安裝"
        INSTALL_PLUGIN=false
        return
    fi

    print_success "OpenClaw 已安裝: ~/.openclaw"
}

parse_arguments() {
    CLEAN_INSTALL=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            --clean)
                CLEAN_INSTALL=true
                print_warning "清理模式：將先執行卸載"
                shift
                ;;
            --dev)
                DEV_MODE=true
                print_warning "開發模式已啟用"
                shift
                ;;
            --rebuild-index)
                REBUILD_INDEX=true
                print_warning "將重建記憶索引"
                shift
                ;;
            --path)
                INSTALL_PATH="$2"
                shift 2
                ;;
            --without-plugin)
                INSTALL_PLUGIN=false
                print_warning "將跳過 OpenClaw Plugin 安裝"
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                print_error "未知參數: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

show_help() {
    cat << EOF
用法: bash install.sh [選項]

選項:
    --dev                  啟用開發模式（包含測試套件）
    --rebuild-index        安裝後自動重建記憶索引（推薦升級時使用）
    --path PATH            自定義安裝路徑（默認: ~/.openclaw/workspace/soul-memory）
    --without-plugin       跳過 OpenClaw Plugin 安裝
    --help                 顯示此幫助信息

示例:
    bash install.sh
    bash install.sh --dev --rebuild-index
    bash install.sh --path /opt/soul-memory
    bash install.sh --without-plugin

v3.3 新功能:
    • 分層關鍵詞字典（三級權重系統）
    • 語意相似度去重（difflib, threshold=0.85）
    • 多標籤索引系統
    • 通用 Schema（無硬編碼特定字眼）
EOF
}

rebuild_memory_index() {
    print_step "重建記憶索引 (v3.3)..."
    print_warning "這可能需要幾秒鐘...

    INDEX_SCRIPT="$INSTALL_PATH/rebuild_index.py"

    # 創建索引自動重建腳本
    cat > "$INDEX_SCRIPT" << 'REBUILD_SCRIPT'
#!/usr/bin/env python3
"""
Soul Memory Index Rebuilder v3.3
自動重建記憶搜尋索引
"""

import sys
import os
from pathlib import Path

# 添加模組路徑
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

try:
    from core import SoulMemorySystem

    # 初始化系統
    sms = SoulMemorySystem()
    sms.initialize()

    # 刪除舊索引
    cache_dir = script_dir / "cache"
    cache_index = cache_dir / "index.json"
    
    if cache_index.exists():
        cache_index.unlink()
        print("  已刪除舊索引")
    
    # 重建索引
    print("  重建中...")
    sms.initialize()

    # 獲取索引統計
    if cache_index.exists():
        import json
        with open(cache_index, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        segments = len(data.get('segments', []))
        print(f"  索引重建成功: {segments} 個分段")
        print("  ✅ 記憶索引已自動更新")
    else:
        print("  ⚠️  索引文件未生成（可能沒有記憶文件）")
        
except Exception as e:
    print(f"  ❌ 索引重建失敗: {e}")
    sys.exit(1)
REBUILD_SCRIPT

    chmod +x "$INDEX_SCRIPT"

    # 執行重建
    python3 "$INDEX_SCRIPT"
    
    if [ $? -eq 0 ]; then
        print_success "記憶索引重建完成"
    else
        print_error "記憶索引重建失敗"
        print_warning "您可以稍後手動執行: python3 $INDEX_SCRIPT"
    fi
}

clone_or_update() {
    print_step "克隆/更新 Soul Memory 倉庫..."

    if [ -d "$INSTALL_PATH" ]; then
        print_warning "目錄已存在: $INSTALL_PATH"
        echo "正在更新..."
        cd "$INSTALL_PATH"
        git pull origin main
    else
        mkdir -p "$(dirname "$INSTALL_PATH")"
        git clone https://github.com/kingofqin2026/Soul-Memory-.git "$INSTALL_PATH"
        cd "$INSTALL_PATH"
    fi

    print_success "倉庫已同步"
}

install_dependencies() {
    print_step "安裝 Python 依賴..."

    if [ -f "$INSTALL_PATH/requirements.txt" ]; then
        if ! command -v pip3 &> /dev/null; then
            print_warning "pip3 未安安裝，嘗試使用 python3 -m pip"
            python3 -m pip install --upgrade pip
        fi

        pip3 install -r "$INSTALL_PATH/requirements.txt" || true
        print_success "依賴安裝完成"
    else
        print_warning "requirements.txt 未找到，跳過依賴安裝"
    fi
}

run_tests() {
    print_step "運行測試套件..."

    if [ -f "$INSTALL_PATH/test_all_modules.py" ]; then
        cd "$INSTALL_PATH"
        python3 test_all_modules.py

        if [ $? -eq 0 ]; then
            print_success "所有測試通過"
        else
            print_error "測試失敗"
            exit 1
        fi
    else
        print_warning "test_all_modules.py 未找到，跳過測試"
    fi
}

setup_heartbeat_v33() {
    print_step "配置 Heartbeat v3.3（分層關鍵詞 + 語意去重）..."

    HEARTBEAT_FILE="${HOME}/.openclaw/workspace/HEARTBEAT.md"

    # 檢查 HEARTBEAT.md 是否已包含 v3.3 配置
    if [ -f "$HEARTBEAT_FILE" ] && grep -q "v3.3" "$HEARTBEAT_FILE"; then
        print_success "Heartbeat v3.3 配置已存在"
    else
        print_step "自動更新 HEARTBEAT.md..."
        cat > "$HEARTBEAT_FILE" << 'HEARTBEAT'
# Heartbeat Tasks (丞相職責) v3.3

## 🤖 自動執行：Soul Memory v3.3 Heartbeat 檢查

**每次 Heartbeat 時自動執行以下命令**：

```bash
python3 /root/.openclaw/workspace/soul-memory/heartbeat-trigger.py
```

如果輸出 `HEARTBEAT_OK`，則無新記憶需要處理。

---

## Soul Memory 自動記憶系統 v3.3

### 🎯 系統架構（Heartbeat + 三層保護機制）

| 機制 | 觸發條件 | 版本 |
|------|----------|------|
| **OpenClaw Plugin** | 每次回答前（before_prompt_build） | ✅ v0.1.0 beta |
| **Heartbeat 主動提取** | 每 30 分鐘左右 | ✅ v3.3 |
| **CLI 接口** | 手動調用 / 測試 | ✅ v3.3 |
| **手動即時保存** | 重要對話後立即 | ✅ 可用 |

### 📋 Heartbeat 職責 (v3.3)

- [ ] 最近對話回顧（識別定義/資料/配置/搜索結果）
- [ ] 主動提取重要內容（寬鬆模式：降低閾值）
- [ ] 分層關鍵詞分類（primary/secondary/tertiary 權重）
- [ ] 語意相似度去重（difflib threshold=0.85）
- [ ] 多標籤索引支持
- [ ] 關鍵記憶保存（[C] 定義 / [I] 資料+配置 / ❌ 指令+問候）
- [ ] 每日檔案檢查（memory/YYYY-MM-DD.md）
- [ ] ~~X (Twitter) 新聞監控~~ - 已停止

### 🎯 v3.3 核心改進

| 項目 | v3.2.2 | v3.3 |
|------|--------|------|
| **關鍵詞映射** | 單層 | **三層分級**（權重 10/7/3） |
| **去重機制** | MD5 哈希 | **MD5 + 語意相似度**（雙層） |
| **標籤系統** | 單標籤 | **多標籤索引** |
| **用戶定制** | 硬編碼 | **通用 Schema** |

### 🔧 三層關鍵詞字典示例

```
Primary (權重 10): framework, core, theory
Secondary (權重 7): document, export, version
Tertiary (權重 3): analysis, discussion, review
```

### 💾 v3.3 數據結構

| 文件 | 用途 |
|------|------|
| `dedup_hashes.json` | MD5 哈希去重記錄 |
| `data/dedup.json` | 語意去重相似度記錄 |
| `data/tag_index.json` | 多標籤反向索引 |

If nothing needs attention, reply HEARTBEAT_OK.
HEARTBEAT
        print_success "HEARTBEAT.md 已自動更新為 v3.3"
    fi
}

setup_openclaw_plugin() {
    if [ "$INSTALL_PLUGIN" != true ]; then
        return
    fi

    print_step "配置 OpenClaw v0.1.1 Plugin (v3.3 update)..."

    # 創建 Plugin 目錄
    PLUGIN_DIR="${OPENCLAW_EXTENSIONS}/soul-memory"
    mkdir -p "$PLUGIN_DIR"

    # 檢查 Plugin 文件是否已存在
    if [ -f "$PLUGIN_DIR/openclaw.plugin.json" ] && [ -f "$PLUGIN_DIR/index.ts" ]; then
        print_warning "Plugin 文件已存在，跳過創建"
    else
        print_step "創建 Plugin 檔案..."

        # 創建 openclaw.plugin.json
        cat > "$PLUGIN_DIR/openclaw.plugin.json" << 'PLUGIN_JSON'
{
  "id": "soul-memory",
  "name": "Soul Memory Context Injector",
  "version": "0.1.1",
  "description": "Automatically injects Soul Memory v3.3 search results before each response using before_prompt_build Hook with multi-tag support",
  "main": "index.ts",
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "enabled": {
        "type": "boolean",
        "default": true,
        "description": "Enable Soul Memory injection"
      },
      "topK": {
        "type": "number",
        "default": 5,
        "minimum": 1,
        "maximum": 10,
        "description": "Number of memory results to retrieve"
      },
      "minScore": {
        "type": "number",
        "default": 0.0,
        "minimum": 0.0,
        "maximum": 10.0,
        "description": "Minimum similarity score threshold"
      },
      "multiTagSearch": {
        "type": "boolean",
        "default": true,
        "description": "Enable multi-tag search (v3.3 feature)"
      }
    }
  },
  "uiHints": {
    "enabled": {
      "label": "Enable Soul Memory Injection",
      "description": "Automatically search and inject memory before responses"
    },
    "topK": {
      "label": "Memory Results Count",
      "placeholder": "5",
      "description": "How many relevant memories to retrieve"
    },
    "minScore": {
      "label": "Minimum Score",
      "placeholder": "0.0",
      "description": "Only show memories above this similarity score"
    },
    "multiTagSearch": {
      "label": "Multi-Tag Search",
      "description": "Enable multi-tag search support (v3.3)"
    }
  }
}
PLUGIN_JSON
        print_success "已創成: $PLUGIN_DIR/openclaw.plugin.json"

        # 創建 index.ts (保持不變，兼容 v3.3)
        cat > "$PLUGIN_DIR/index.ts" << 'PLUGIN_TS'
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

interface SoulMemoryConfig {
  enabled: boolean;
  topK: number;
  minScore: number;
  multiTagSearch: boolean;
}

interface MemoryResult {
  path: string;
  content: string;
  score: number;
  priority?: string;
}

async function searchMemories(query: string, config: SoulMemoryConfig): Promise<MemoryResult[]> {
  try {
    const { stdout } = await execAsync(
      `python3 /root/.openclaw/workspace/soul-memory/cli.py search "${query}" --top_k ${config.topK} --min_score ${config.minScore}`,
      { timeout: 5000 }
    );

    const results = JSON.parse(stdout || '[]');
    return Array.isArray(results) ? results : [];
  } catch (error) {
    console.error('[Soul Memory] Search failed:', error instanceof Error ? error.message : String(error));
    return [];
  }
}

function buildMemoryContext(results: MemoryResult[]): string {
  if (results.length === 0) return '';

  let context = '\\n## 🧠 Memory Context\\n\\n';

  results.forEach((result, index) => {
    const scoreBadge = result.score > 5 ? '🔥' : result.score > 3 ? '⭐' : '';
    const priorityBadge = result.priority === 'C' ? '[🔴 Critical]'
                        : result.priority === 'I' ? '[🟡 Important]'
                        : '';

    context += `${index + 1}. ${scoreBadge} ${priorityBadge} ${result.content}\\n`;

    if (result.path && result.score > 3) {
      context += `   *Source: ${result.path}*\\n`;
    }
    context += '\\n';
  });

  return context;
}

function getLastUserMessage(messages: any[]): string {
  if (!messages || messages.length === 0) return '';

  for (let i = messages.length - 1; i >= 0; i--) {
    const msg = messages[i];
    if (msg.role === 'user' && msg.content) {
      if (Array.isArray(msg.content)) {
        return msg.content
          .filter((item: any) => item.type === 'text')
          .map((item: any) => item.text)
          .join(' ');
      } else if (typeof msg.content === 'string') {
        return msg.content;
      }
    }
  }

  return '';
}

export default function register(api: any) {
  const logger = api.logger || console;

  logger.info('[Soul Memory v3.3] Plugin registered via api.register()');

  api.on('before_prompt_build', async (event: any, ctx: any) => {
    const config: SoulMemoryConfig = {
      enabled: true,
      topK: 5,
      minScore: 0.0,
      multiTagSearch: true,
      ...api.config.plugins?.entries?.['soul-memory']?.config
    };

    logger.info('[Soul Memory v3.3] ✓ BEFORE_PROMPT_BUILD HOOK CALLED');
    logger.debug(`[Soul Memory v3.3] Config: enabled=${config.enabled}, topK=${config.topK}, minScore=${config.minScore}`);
    logger.debug(`[Soul Memory v3.3] Event: prompt=${event.prompt?.substring(0, 50)}..., messages=${event.messages?.length || 0}`);
    logger.debug(`[Soul Memory v3.3] Context: agentId=${ctx.agentId}, sessionKey=${ctx.sessionKey}`);

    if (!config.enabled) {
      logger.info('[Soul Memory v3.3] Plugin disabled, skipping');
      return {};
    }

    const messages = event.messages || [];
    const lastUserMessage = getLastUserMessage(messages);

    logger.debug(`[Soul Memory v3.3] Last user message length: ${lastUserMessage.length}`);

    if (!lastUserMessage || lastUserMessage.trim().length === 0) {
      logger.debug('[Soul Memory v3.3] No user message found, skipping');
      return {};
    }

    const query = lastUserMessage
      .split(/[。!！?？\\n]/)[0]
      .trim()
      .substring(0, 200);

    if (query.length < 5) {
      logger.debug(`[Soul Memory v3.3] Query too short (${query.length} chars): "${query}", skipping`);
      return {};
    }

    logger.info(`[Soul Memory v3.3] Searching for: "${query}"`);

    const results = await searchMemories(query, config);

    logger.info(`[Soul Memory v3.3] Found ${results.length} results`);

    if (results.length === 0) {
      logger.info('[Soul Memory v3.3] No memories found');
      return {};
    }

    const memoryContext = buildMemoryContext(results);

    logger.info(`[Soul Memory v3.3] Injected ${results.length} memories into prompt (${memoryContext.length} chars)`);

    return {
      prependContext: memoryContext
    };
  });

  logger.info('[Soul Memory v3.3] Hook registered: before_prompt_build');
}
PLUGIN_TS
        print_success "已創成: $PLUGIN_DIR/index.ts"

        # 創建 package.json
        cat > "$PLUGIN_DIR/package.json" << 'PACKAGE_JSON'
{
  "name": "soul-memory-plugin",
  "version": "0.1.1",
  "description": "Soul Memory Context Injector v3.3 for OpenClaw",
  "type": "module",
  "main": "index.ts"
}
PACKAGE_JSON
        print_success "已創成: $PLUGIN_DIR/package.json"
    fi

    print_success "OpenClaw Plugin v0.1.1 配置完成"
}

setup_environment() {
    print_step "設置環境變數..."

    SHELL_RC=""
    if [ -f "$HOME/.bashrc" ]; then
        SHELL_RC="$HOME/.bashrc"
    elif [ -f "$HOME/.zshrc" ]; then
        SHELL_RC="$HOME/.zshrc"
    fi

    if [ -n "$SHELL_RC" ]; then
        if ! grep -q "SOUL_MEMORY_PATH" "$SHELL_RC"; then
            cat >> "$SHELL_RC" << EOF

# Soul Memory System v3.3
export SOUL_MEMORY_PATH="$INSTALL_PATH"
export PYTHONPATH="\${SOUL_MEMORY_PATH}:\${PYTHONPATH}"
EOF
            print_success "環境變數已添加到 $SHELL_RC"
            print_warning "請運行: source $SHELL_RC"
        else
            print_success "環境變數已存在"
        fi
    fi
}

verify_installation() {
    print_step "驗證安裝..."

    cd "$INSTALL_PATH"

    # 檢查 v3.3 核心文件
    REQUIRED_FILES=(
        "core.py"
        "cli.py"
        "heartbeat-trigger.py"
        "dedup_hashes.json"
        "README.md"
        "V3_3_UPGRADE.md"
    )

    ALL_EXIST=true
    for file in "${REQUIRED_FILES[@]}"; do
        if [ -f "$file" ]; then
            echo -e "${GREEN}  ✓${NC} $file"
        else
            echo -e "${RED}  ✗${NC} $file"
            ALL_EXIST=false
        fi
    done

    # 檢查 v3.3 新模組
    echo ""
    echo "v3.3 新模組:"
    V33_MODULES=(
        "modules/keyword_mapping.py"
        "modules/semantic_dedup.py"
        "modules/tag_index.py"
    )

    for file in "${V33_MODULES[@]}"; do
        if [ -f "$file" ] || [ -f "$file"_v3_3.py ]; then
            echo -e "${GREEN}  ✓${NC} $(basename $file)"
        else
            echo -e "${YELLOW}  ⚠️ ${NC} $(basename $file) (可選)"
        fi
    done

    # 檢查模組
    echo ""
    echo "核心模組:"
    MODULE_FILES=(
        "modules/priority_parser.py"
        "modules/vector_search.py"
        "modules/dynamic_classifier.py"
        "modules/auto_trigger.py"
        "modules/cantonese_syntax.py"
    )

    for file in "${MODULE_FILES[@]}"; do
        if [ -f "$file" ]; then
            echo -e "${GREEN}  ✓${NC} $file"
        else
            echo -e "${RED}  ✗${NC} $file"
        fi
    done

    # 測試 CLI
    echo ""
    print_step "測試 CLI 接口..."
    python3 "$INSTALL_PATH/cli.py" search "test" --top_k 1 &> /dev/null
    if [ $? -eq 0 ]; then
        print_success "CLI 接口正常"
    else
        print_warning "CLI 接口測試失敗（可能需要初始化系統）"
    fi

    if [ "$ALL_EXIST" = true ]; then
        print_success "所有必需文件已就位"
    else
        print_error "某些文件缺失"
    fi
}

print_summary() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                    ✅ 安裝完成                                ║${NC}"
    echo -e "${BLUE}║              Soul Memory System v3.3                         ║${NC}"
    echo -e "${BLUE}║           + OpenClaw Plugin v0.1.1                           ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}📍 安裝位置:${NC} $INSTALL_PATH"
    echo -e "${GREEN}📦 OpenClaw Plugin:${NC} ~/.openclaw/extensions/soul-memory"
    echo ""
    echo -e "${GREEN}🎯 v3.3 新功能:${NC}"
    echo "  • 分層關鍵詞字典（三級權重系統：10/7/3）"
    echo "  • 語意相似度去重（difflib, threshold=0.85）"
    echo "  • 多標籤索引系統"
    echo "  • 通用 Schema（無硬編碼特定字眼）"
    echo ""
    echo -e "${GREEN}📋 後續步驟:${NC}"
    echo ""
    echo "1. 設置環境變數:"
    echo -e "   ${YELLOW}source ~/.bashrc${NC}  (或 ~/.zshrc)"
    echo ""
    echo "2. 驗證安裝:"
    echo -e "   ${YELLOW}cd $INSTALL_PATH${NC}"
    echo -e "   ${YELLOW}python3 cli.py search 'test' --top_k 1${NC}"
    echo ""
    echo "3. 測試 Heartbeat:"
    echo -e "   ${YELLOW}python3 $INSTALL_PATH/heartbeat-trigger.py${NC}"
    echo ""
    echo "4. 重建記憶索引（如果升級後舊索引不準確）:"
    echo -e "   ${YELLOW}python3 $INSTALL_PATH/rebuild_index.py${NC}"
    echo ""
    if [ "$INSTALL_PLUGIN" = true ]; then
        echo "5. 配置 OpenClaw（如果尚未配置）:"
        echo "   在 ~/.openclaw/openclaw.json 的 plugins.entries 中添加:"
        echo "   "
        echo '   "soul-memory": {'
        echo '     "enabled": true,'
        echo '     "config": {'
        echo '       "enabled": true,'
        echo '       "topK": 5,'
        echo '       "minScore": 0.0,'
        echo '       "multiTagSearch": true'
        echo '     }'
        echo '   }'
        echo ""
        echo "6. 重啟 OpenClaw Gateway:"
        echo -e "   ${YELLOW}openclaw gateway restart${NC}"
        echo ""
    fi
    echo -e "${GREEN}📚 文檔:${NC}"
    echo -e "   ${YELLOW}$INSTALL_PATH/README.md${NC}"
    echo -e "   ${YELLOW}$INSTALL_PATH/V3_3_UPGRADE.md${NC}"
    echo ""
}

main() {
    print_header

    parse_arguments "$@"

    # 清理模式：先卸載再安裝
    if [ "$CLEAN_INSTALL" = true ]; then
        print_warning "執行清理安裝..."
        if [ -f "${INSTALL_PATH}/uninstall.sh" ]; then
            bash "${INSTALL_PATH}/uninstall.sh" --backup --confirm || {
                print_warning "卸載失敗，繼續安裝..."
            }
        else
            print_warning "未找到 uninstall.sh，跳過卸載"
        fi
        echo ""
    fi

    check_python
    check_git
    check_openclaw
    clone_or_update
    install_dependencies

    if [ "$DEV_MODE" = true ]; then
        run_tests
    fi

    setup_heartbeat_v33
    setup_openclaw_plugin
    setup_environment

    # 索引自動重建
    if [ "$REBUILD_INDEX" = true ]; then
        rebuild_memory_index
    fi

    verify_installation

    print_summary

    print_success "Soul Memory System v3.3 安裝完成！"
}

main "$@"
