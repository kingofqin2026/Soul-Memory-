#!/bin/bash

################################################################################
# Soul Memory System v3.2.2 - Installation Script
#
# 功能：自動安裝 Soul Memory 系統 + OpenClaw Plugin + Heartbeat 自動儲存
# 用法：bash install.sh [--dev] [--path /custom/path] [--with-plugin]
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
OPENCLAW_EXTENSIONS="${HOME}/.openclaw/extensions"
PYTHON_MIN_VERSION="3.7"

################################################################################
# 函數定義
################################################################################

print_header() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║   🧠 Soul Memory System v3.2.2 - Installation Script          ║${NC}"
    echo -e "${BLUE}║   CLI + Heartbeat v3.2.2 + OpenClaw Plugin Support          ║${NC}"
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
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dev)
                DEV_MODE=true
                print_warning "開發模式已啟用"
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
    --path PATH            自定義安裝路徑（默認: ~/.openclaw/workspace/soul-memory）
    --without-plugin       跳過 OpenClaw Plugin 安裝
    --help                 顯示此幫助信息

示例:
    bash install.sh
    bash install.sh --dev
    bash install.sh --path /opt/soul-memory
    bash install.sh --without-plugin
EOF
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
            print_warning "pip3 未安未安裝，嘗試使用 python3 -m pip"
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

setup_heartbeat_v32() {
    print_step "配置 Heartbeat v3.2.2 去重機制..."

    HEARTBEAT_FILE="${HOME}/.openclaw/workspace/HEARTBEAT.md"

    # 檢查 HEARTBEAT.md 是否已包含 v3.2.2 配置
    if [ -f "$HEARTBEAT_FILE" ] && grep -q "v3.2.2" "$HEARTBEAT_FILE"; then
        print_success "Heartbeat v3.2.2 配置已存在"
    else
        print_step "自動更新 HEARTBEAT.md..."
        cat > "$HEARTBEAT_FILE" << 'HEARTBEAT'
# Heartbeat Tasks (丞相職責) v3.2.2

## 🤖 自動執行：Soul Memory v3.2.2 Heartbeat 檢查

**每次 Heartbeat 時自動執行以下命令**：

```bash
python3 /root/.openclaw/workspace/soul-memory/heartbeat-trigger.py
```

如果輸出 `HEARTBEAT_OK`，則無新記憶需要處理。

---

## Soul Memory 自動記憶系統 v3.2.2

### 🎯 系統架構（Heartbeat 寬鬆模式 + 去重機制）

| 機制 | 觸發條件 | 版本 |
|------|----------|------|
| **OpenClaw Plugin** | 每次回答前（before_prompt_build） | ✅ v0.1.0 beta |
| **Heartbeat 寬鬆模式** | 每 30 分鐘左右 | ✅ v3.2.2 |
| **CLI 接口** | 手動調用 / 測試 | ✅ v3.2.2 |
| **手動即時保存** | 重要對話後立即 | ✅ 可用 |

### 📋 Heartbeat 職責 (v3.2.2)

- [ ] 最近對話回顧（識別定義/資料/配置/搜索結果）
- [ ] 主動提取重要內容（寬鬆模式：降低閾值）
- [ ] 關鍵記憶保存（[C] 定義 / [I] 資料+配置 / ❌ 指令+問候）
- [ ] 每日檔案檢查（memory/YYYY-MM-DD.md）
- [ ] ~~X (Twitter) 新聞監控~~ - 已停止

### 🎯 v3.2.2 寬鬆模式改進

| 項目 | 修改前（嚴格） | 修改後（寬鬆） |
|------|--------------|--------------|
| **最小長度** | 50 字 | **30 字** ↓ |
| **長文本閾值** | > 200 字 | **> 100 字** ↓ |
| **最低 importance_score** | >= 2 | **>= 1** ↓ |
| **排除規則** | HEARTBEAT.md + Read HEARTBEAT.md + [xxx] | **僅 HEARTBEAT.md** ✅ |

### 🔄 v3.2.2 去重機制

- **MD5 哈希追蹤**：已保存內容不重複
- **數據結構**：dedup_hashes.json（每日哈希集合）
- **效率提升**：避免重複保存，節省空間

If nothing needs attention, reply HEARTBEAT_OK.
HEARTBEAT
        print_success "HEARTBEAT.md 已自動更新為 v3.2.2"
    fi
}

setup_openclaw_plugin() {
    if [ "$INSTALL_PLUGIN" != true ]; then
        return
    fi

    print_step "配置 OpenClaw v0.1.0 Plugin..."

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
  "version": "0.1.0-beta",
  "description": "Automatically injects Soul Memory search results before each response using before_prompt_build Hook",
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
    }
  }
}
PLUGIN_JSON
        print_success "已創成: $PLUGIN_DIR/openclaw.plugin.json"

        # 創建 index.ts
        cat > "$PLUGIN_DIR/index.ts" << 'PLUGIN_TS'
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

interface SoulMemoryConfig {
  enabled: boolean;
  topK: number;
  minScore: number;
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

  logger.info('[Soul Memory] Plugin registered via api.register()');

  api.on('before_prompt_build', async (event: any, ctx: any) => {
    const config: SoulMemoryConfig = {
      enabled: true,
      topK: 5,
      minScore: 0.0,
      ...api.config.plugins?.entries?.['soul-memory']?.config
    };

    logger.info('[Soul Memory] ✓ BEFORE_PROMPT_BUILD HOOK CALLED via api.on()');
    logger.debug(`[Soul Memory] Config: enabled=${config.enabled}, topK=${config.topK}, minScore=${config.minScore}`);
    logger.debug(`[Soul Memory] Event: prompt=${event.prompt?.substring(0, 50)}..., messages=${event.messages?.length || 0}`);
    logger.debug(`[Soul Memory] Context: agentId=${ctx.agentId}, sessionKey=${ctx.sessionKey}`);

    if (!config.enabled) {
      logger.info('[Soul Memory] Plugin disabled, skipping');
      return {};
    }

    const messages = event.messages || [];
    const lastUserMessage = getLastUserMessage(messages);

    logger.debug(`[Soul Memory] Last user message length: ${lastUserMessage.length}`);

    if (!lastUserMessage || lastUserMessage.trim().length === 0) {
      logger.debug('[Soul Memory] No user message found, skipping');
      return {};
    }

    const query = lastUserMessage
      .split(/[。!！?？\\n]/)[0]
      .trim()
      .substring(0, 200);

    if (query.length < 5) {
      logger.debug(`[Soul Memory] Query too short (${query.length} chars): "${query}", skipping`);
      return {};
    }

    logger.info(`[Soul Memory] Searching for: "${query}"`);

    const results = await searchMemories(query, config);

    logger.info(`[Soul Memory] Found ${results.length} results`);

    if (results.length === 0) {
      logger.info('[Soul Memory] No memories found');
      return {};
    }

    const memoryContext = buildMemoryContext(results);

    logger.info(`[Soul Memory] Injected ${results.length} memories into prompt (${memoryContext.length} chars)`);

    return {
      prependContext: memoryContext
    };
  });

  logger.info('[Soul Memory] Hook registered via api.on(): before_prompt_build');
}
PLUGIN_TS
        print_success "已創成: $PLUGIN_DIR/index.ts"

        # 創建 package.json
        cat > "$PLUGIN_DIR/package.json" << 'PACKAGE_JSON'
{
  "name": "soul-memory-plugin",
  "version": "0.1.0-beta",
  "description": "Soul Memory Context Injector for OpenClaw",
  "type": "module",
  "main": "index.ts"
}
PACKAGE_JSON
        print_success "已創成: $PLUGIN_DIR/package.json"
    fi

    # 配置 OpenClaw
    OPENCLAW_CONFIG="${HOME}/.openclaw/openclaw.json"

    if [ -f "$OPENCLAW_CONFIG" ]; then
        print_step "配置 OpenClaw..."

        # 檢查是否已配置
        if grep -q '"soul-memory"' "$OPENCLAW_CONFIG"; then
            print_success "OpenClaw 已配置 soul-memory"
        else
            print_warning "需要手動配置 OpenClaw（以下命令）:"
            echo ""
            echo -e "${YELLOW}在 ~/.openclaw/openclaw.json 的 plugins.entries 中添加：${NC}"
            echo ""
            echo '  "soul-memory": {'
            echo '    "enabled": true,'
            echo '    "config": {'
            echo '      "enabled": true,'
            echo '      "topK": 5,'
            echo '      "minScore": 0.0'
            echo '    }'
            echo '  }'
            echo ""
            echo -e "${YELLOW}然後重啟 Gateway：${NC}"
            echo '  openclaw gateway restart'
            echo ""
        fi
    fi

    print_success "OpenClaw Plugin 配置完成"
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

# Soul Memory System v3.2.2
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

    # 檢查 v3.2.2 核心文件
    REQUIRED_FILES=(
        "core.py"
        "cli.py"
        "heartbeat-trigger.py"
        "dedup_hashes.json"
        "README.md"
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

    # 檢查 modules
    echo ""
    echo "Check modules:"
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
    echo -e "${BLUE}║              Soul Memory System v3.2.2                       ║${NC}"
    echo -e "${BLUE}║           + OpenClaw Plugin v0.1.0 beta                     ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}📍 安裝位置:${NC} $INSTALL_PATH"
    echo -e "${GREEN}📦 OpenClaw Plugin:${NC} ~/.openclaw/extensions/soul-memory"
    echo ""
    echo -e "${GREEN}🎯 v3.2.2 新功能:${NC}"
    echo "  • CLI 接口（純 JSON 輸出）"
    echo "  • Heartbeat v3.2.2 寬鬆模式（降低識別閾值）"
    echo "  • MD5 哈希去重機制（防止重複保存）"
    echo "  • OpenClaw Plugin（before_prompt_build Hook）"
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
    if [ "$INSTALL_PLUGIN" = true ]; then
        echo "4. 配置 OpenClaw（如果尚未配置）:"
        echo "   在 ~/.openclaw/openclaw.json 的 plugins.entries 中添加:"
        echo "   "
        echo '   "soul-memory": {'
        echo '     "enabled": true,'
        echo '     "config": {'
        echo '       "enabled": true,'
        echo '       "topK": 5,'
        echo '       "minScore": 0.0'
        echo '     }'
        echo '   }'
        echo ""
        echo "5. 重啟 OpenClaw Gateway:"
        echo -e "   ${YELLOW}openclaw gateway restart${NC}"
        echo ""
    fi
    echo -e "${GREEN}📚 文檔:${NC}"
    echo -e "   ${YELLOW}$INSTALL_PATH/README.md${NC}"
    echo ""
}

main() {
    print_header

    parse_arguments "$@"

    check_python
    check_git
    check_openclaw
    clone_or_update
    install_dependencies

    if [ "$DEV_MODE" = true ]; then
        run_tests
    fi

    setup_heartbeat_v32
    setup_openclaw_plugin
    setup_environment
    verify_installation

    print_summary

    print_success "Soul Memory System v3.2.2 安裝完成！"
}

main "$@"
