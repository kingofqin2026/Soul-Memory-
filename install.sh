#!/bin/bash
# Soul Memory System - 一鍵安裝腳本
# Author: 界王 (King Kai)
# Repo: https://github.com/kingofqin2026/Soul-Memory

set -e

echo "🧠 Soul Memory System v2.1 安裝程序"
echo "======================================"
echo ""

# 檢查 Python 版本
if ! command -v python3 &> /dev/null; then
    echo "❌ 錯誤：未找到 python3"
    echo "請先安裝 Python 3.7+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python 版本: $PYTHON_VERSION"

# 克隆倉庫
echo ""
echo "📥 克隆 Soul-Memory 倉庫..."
if [ -d "Soul-Memory" ]; then
    echo "⚠️  目錄 Soul-Memory 已存在，跳過克隆"
    cd Soul-Memory
    git pull origin main
else
    git clone https://github.com/kingofqin2026/Soul-Memory.git
    cd Soul-Memory
fi

# 安裝依賴（如果有 requirements.txt）
if [ -f "requirements.txt" ]; then
    echo ""
    echo "📦 安裝依賴..."
    pip3 install -r requirements.txt
else
    echo ""
    echo "ℹ️  無 requirements.txt，跳過依賴安裝"
fi

# 測試安裝
echo ""
echo "🧪 測試安裝..."
python3 -c "
import sys
sys.path.insert(0, '.')
from core import SoulMemorySystem
print('✅ Soul Memory System 導入成功')
"

# 運行測試
echo ""
echo "🧪 運行模組測試..."
python3 test_all_modules.py

echo ""
echo "======================================"
echo "✅ 安裝完成！"
echo ""
echo "📚 使用方式："
echo "  cd Soul-Memory"
echo "  python3 -c 'from core import SoulMemorySystem; s=SoulMemorySystem(); s.initialize()'"
echo ""
echo "📖 文檔: https://github.com/kingofqin2026/Soul-Memory"
echo "🧠 为灵魂存储而生"
