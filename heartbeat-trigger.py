#!/usr/bin/env python3
"""
Soul Memory Heartbeat Auto-Save Trigger v3.1.1
自動檢查並保存重要記憶
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# 添加 soul-memory 到路徑
SOUL_MEMORY_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SOUL_MEMORY_PATH)

try:
    from core import SoulMemorySystem
except ImportError:
    print("❌ 無法導入 SoulMemorySystem")
    sys.exit(1)

def check_daily_memory():
    """檢查今日記憶檔案"""
    today = datetime.now().strftime('%Y-%m-%d')
    daily_file = Path.home() / ".openclaw" / "workspace" / "memory" / f"{today}.md"
    
    if daily_file.exists():
        with open(daily_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 計算 Auto-Save 條目數
        auto_save_count = content.count('[Auto-Save]')
        return auto_save_count, daily_file
    
    return 0, daily_file

def main():
    """Heartbeat 檢查點"""
    try:
        system = SoulMemorySystem()
        system.initialize()
        
        auto_save_count, daily_file = check_daily_memory()
        
        print(f"🩺 Heartbeat 記憶檢查 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC)")
        print(f"- 自動儲存條目：{auto_save_count} 條")
        print(f"- 記憶系統：v3.1.1 就緒")
        
        if auto_save_count > 0:
            print(f"↳ 已保存至 {daily_file.name}")
        else:
            print("HEARTBEAT_OK")
    
    except Exception as e:
        print(f"❌ Heartbeat 檢查失敗: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
