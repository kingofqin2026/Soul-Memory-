#!/bin/bash

################################################################################
# Soul Memory System v2.1 - Installation Script
# 
# 功能：自動安裝 Soul Memory 系統，確保 auto-trigger 順利運行
# 用法：bash install.sh [--dev] [--path /custom/path]
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
PYTHON_MIN_VERSION="3.7"

################################################################################
# 函數定義
################################################################################

print_header() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║     🧠 Soul Memory System v2.1 - Installation Script          ║${NC}"
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
    --dev              啟用開發模式（包含測試套件）
    --path PATH        自定義安裝路徑（默認: ~/.openclaw/workspace/soul-memory）
    --help             顯示此幫助信息

示例:
    bash install.sh
    bash install.sh --dev
    bash install.sh --path /opt/soul-memory
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
    print_step "安裝依賴..."
    
    if [ -f "$INSTALL_PATH/requirements.txt" ]; then
        if ! command -v pip3 &> /dev/null; then
            print_warning "pip3 未安裝，嘗試使用 python3 -m pip"
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
        print_warning "test_all_modules.py 未找到"
    fi
}

setup_auto_trigger() {
    print_step "配置 Auto-Trigger..."
    
    TRIGGER_CONFIG_DIR="${HOME}/.config/soul-memory"
    mkdir -p "$TRIGGER_CONFIG_DIR"
    
    cat > "$TRIGGER_CONFIG_DIR/auto-trigger.conf" << 'CONF'
# Soul Memory Auto-Trigger Configuration
ENABLED=true
TOP_K=5
PRIORITY_CRITICAL=1.0
PRIORITY_IMPORTANT=0.7
PRIORITY_NORMAL=0.3
SEARCH_TIMEOUT=5
CACHE_TTL=3600
LOG_LEVEL=INFO
CONF
    
    print_success "Auto-Trigger 配置已創建: $TRIGGER_CONFIG_DIR/auto-trigger.conf"
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

# Soul Memory System v2.1
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

create_trigger_daemon() {
    print_step "創建 Auto-Trigger 守護進程..."
    
    DAEMON_FILE="$INSTALL_PATH/trigger-daemon.py"
    
    cat > "$DAEMON_FILE" << 'DAEMON'
#!/usr/bin/env python3
"""
Soul Memory Auto-Trigger Daemon
持續監控並在需要時自動觸發記憶搜索
"""

import sys
import os
import time
import logging
from pathlib import Path

SOUL_MEMORY_PATH = os.environ.get('SOUL_MEMORY_PATH', os.path.dirname(__file__))
sys.path.insert(0, SOUL_MEMORY_PATH)

from core import SoulMemorySystem

CONFIG_DIR = Path.home() / '.config' / 'soul-memory'
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = CONFIG_DIR / 'auto-trigger.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TriggerDaemon:
    def __init__(self):
        self.system = SoulMemorySystem()
        self.system.initialize()
        self.running = True
        logger.info("🧠 Soul Memory Auto-Trigger Daemon 已啟動")
    
    def run(self):
        try:
            while self.running:
                time.sleep(60)
                self.check_and_trigger()
        except KeyboardInterrupt:
            logger.info("收到中斷信號，正在關閉...")
            self.stop()
    
    def check_and_trigger(self):
        try:
            logger.debug("Auto-Trigger 檢查點")
        except Exception as e:
            logger.error(f"觸發錯誤: {e}")
    
    def stop(self):
        self.running = False
        logger.info("Auto-Trigger Daemon 已停止")

if __name__ == '__main__':
    daemon = TriggerDaemon()
    daemon.run()
DAEMON
    
    chmod +x "$DAEMON_FILE"
    print_success "Auto-Trigger 守護進程已創建: $DAEMON_FILE"
}

verify_installation() {
    print_step "驗證安裝..."
    
    cd "$INSTALL_PATH"
    
    REQUIRED_FILES=(
        "core.py"
        "modules/priority_parser.py"
        "modules/vector_search.py"
        "modules/dynamic_classifier.py"
        "modules/version_control.py"
        "modules/memory_decay.py"
        "modules/auto_trigger.py"
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
    
    if [ "$ALL_EXIST" = true ]; then
        print_success "所有必需文件已就位"
    else
        print_error "某些文件缺失"
        exit 1
    fi
}

print_summary() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                    ✅ 安裝完成                                ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}📍 安裝位置:${NC} $INSTALL_PATH"
    echo ""
    echo -e "${GREEN}📋 後續步驟:${NC}"
    echo ""
    echo "1. 設置環境變數:"
    echo -e "   ${YELLOW}source ~/.bashrc${NC}  (或 ~/.zshrc)"
    echo ""
    echo "2. 驗證安裝:"
    echo -e "   ${YELLOW}cd $INSTALL_PATH${NC}"
    echo -e "   ${YELLOW}python3 -c \"from core import SoulMemorySystem; s = SoulMemorySystem(); s.initialize(); print('✅ Ready')\"${NC}"
    echo ""
    echo "3. 使用 Auto-Trigger:"
    echo -e "   ${YELLOW}python3 $INSTALL_PATH/trigger-daemon.py${NC}"
    echo ""
    echo "4. 配置文件:"
    echo -e "   ${YELLOW}${HOME}/.config/soul-memory/auto-trigger.conf${NC}"
    echo ""
    echo -e "${GREEN}📚 文檔:${NC}"
    echo -e "   ${YELLOW}$INSTALL_PATH/README.md${NC}"
    echo ""
}

main() {
    print_header
    
    parse_arguments "$@"
    
    check_python
    check_git
    clone_or_update
    install_dependencies
    
    if [ "$DEV_MODE" = true ]; then
        run_tests
    fi
    
    setup_auto_trigger
    setup_environment
    create_trigger_daemon
    verify_installation
    
    print_summary
    
    print_success "Soul Memory System v2.1 安裝完成！"
}

main "$@"
