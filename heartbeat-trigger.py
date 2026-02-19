#!/usr/bin/env python3
"""
Soul Memory Heartbeat Auto-Save Trigger
v3.2.0 - 主動提取對話 + 自動保存重要記憶
"""

import sys
import os
import json
import re
from pathlib import Path
from datetime import datetime, timedelta

SOUL_MEMORY_PATH = os.environ.get('SOUL_MEMORY_PATH', os.path.dirname(__file__))
sys.path.insert(0, SOUL_MEMORY_PATH)

from core import SoulMemorySystem

# OpenClaw session 路徑
SESSIONS_DIR = Path.home() / ".openclaw" / "agents" / "main" / "sessions"
SESSIONS_JSON = SESSIONS_DIR / "sessions.json"

def get_active_session_id():
    """獲取當前 active session 的 ID"""
    try:
        with open(SESSIONS_JSON, 'r', encoding='utf-8') as f:
            sessions = json.load(f)
        
        # 找到最近更新的 session
        best_session = None
        best_time = 0
        
        for key, data in sessions.items():
            if isinstance(data, dict) and 'updatedAt' in data:
                if data['updatedAt'] > best_time:
                    best_time = data['updatedAt']
                    best_session = data.get('sessionId', key)
        
        return best_session
    except Exception as e:
        print(f"⚠️ 無法讀取 sessions.json: {e}")
        return None

def read_session_messages(session_id, hours=2):
    """讀取 session 對話內容（最近 N 小時）"""
    session_file = SESSIONS_DIR / f"{session_id}.jsonl"
    
    if not session_file.exists():
        print(f"⚠️ Session 檔案不存在: {session_file}")
        return []
    
    messages = []
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    try:
        with open(session_file, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                
                try:
                    entry = json.loads(line)
                    
                    # 只處理消息類型
                    if entry.get('type') != 'message':
                        continue
                    
                    # 解析時間戳
                    timestamp_str = entry.get('timestamp', '')
                    if not timestamp_str:
                        continue
                    
                    try:
                        msg_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        msg_time = msg_time.replace(tzinfo=None)
                    except:
                        continue
                    
                    # 只處理最近的消息
                    if msg_time < cutoff_time:
                        continue
                    
                    # 提取消息內容
                    message = entry.get('message', {})
                    role = message.get('role', '')
                    content = message.get('content', [])
                    
                    # 提取文本內容
                    text_content = ''
                    if isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict) and item.get('type') == 'text':
                                text_content += item.get('text', '')
                    
                    if text_content.strip():
                        messages.append({
                            'time': msg_time,
                            'role': role,
                            'content': text_content.strip()
                        })
                        
                except json.JSONDecodeError:
                    continue
                    
    except Exception as e:
        print(f"⚠️ 讀取 session 檔案錯誤: {e}")
    
    return messages

def identify_important_content(messages):
    """識別重要內容"""
    important = []
    
    for msg in messages:
        content = msg['content']
        
        # 排除內容
        # 1. 太短
        if len(content) < 50:
            continue
        
        # 2. 系統指令
        if 'HEARTBEAT.md' in content or 'Read HEARTBEAT.md' in content:
            continue
        
        # 3. 標準指令模式
        if content.startswith('[') and ']' in content and len(content) < 200:
            continue
        
        # 識別重要內容（啟發式規則）
        importance_score = 0
        priority = 'N'  # 默認 Normal
        
        # 長文本內容 (> 200 字)
        if len(content) > 200:
            importance_score += 3
            priority = 'I'
        
        # 包含專有名詞或主題詞
        topic_keywords = [
            '劇情', '故事', '設定', '歷史', 'QST', '物理', '公式',
            '配置', '安裝', 'API', 'Token', '密鑰',
            '秦王', '陛下', '臣', '記住', '重要'
        ]
        
        for keyword in topic_keywords:
            if keyword in content:
                importance_score += 2
                if keyword in ['重要', 'QST', '物理', '公式', '配置', '安裝', 'Token', '密鑰']:
                    priority = 'C'
                break
        
        # 定義、說明模式
        if re.search(r'是.*的|定義|屬於|包括', content):
            importance_score += 1
        
        # 劇情/故事模式
        if re.search(r'第.\集|情節|角色|劇中', content):
            importance_score += 2
            priority = 'I'
        
        # AI 回應內容
        if msg['role'] == 'assistant' and importance_score >= 2:
            important.append({
                'time': msg['time'],
                'content': content,
                'priority': priority
            })
    
    return important

def save_to_daily_file(content, priority):
    """保存到 daily file"""
    today = datetime.now().strftime('%Y-%m-%d')
    daily_dir = Path.home() / ".openclaw" / "workspace" / "memory"
    daily_file = daily_dir / f"{today}.md"
    
    # 確保目錄存在
    daily_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成內容
    timestamp = datetime.now().strftime('%H:%M')
    header = "\n\n" + "-" * 50 + "\n"
    header += f"## [{priority}] {timestamp} - Heartbeat 自動提取\n"
    header += f"**來源**：Session 對話回顧\n"
    header += f"**時區**：UTC\n\n"
    
    # 追加到檔案
    with open(daily_file, 'a', encoding='utf-8') as f:
        f.write(header)
        f.write(content)
        f.write('\n')
    
    return str(daily_file)

def check_daily_memory():
    """檢查今日記憶檔案"""
    today = datetime.now().strftime('%Y-%m-%d')
    daily_file = Path.home() / ".openclaw" / "workspace" / "memory" / f"{today}.md"
    
    if daily_file.exists():
        with open(daily_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 計算各類標記數量
        auto_save_count = content.count('[Auto-Save]')
        heartbeat_extract_count = content.count('## [I]') + content.count('## [C]') - content.count('[Auto-Save]')
        
        return auto_save_count, heartbeat_extract_count
    
    return 0, 0

def main():
    """Heartbeat 檢查點"""
    print(f"🧠 初始化 Soul Memory System v3.2.0...")
    system = SoulMemorySystem()
    system.initialize()
    print(f"✅ 記憶系統就緒")
    
    # 步驟 1：檢查現有記憶
    auto_save_count, heartbeat_extract_count = check_daily_memory()
    
    print(f"\n🩺 Heartbeat 記憶檢查 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC)")
    print(f"- [Auto-Save] 條目：{auto_save_count} 條")
    print(f"- [Heartbeat 提取] 條目：{heartbeat_extract_count} 條")
    
    # 步驟 2：主動提取對話（新功能 v3.2.0）
    print(f"\n🔍 開始主動提取對話...")
    
    session_id = get_active_session_id()
    if not session_id:
        print("⚠️ 無法獲取 session ID，跳過對話提取")
    else:
        print(f"📋 當前 Session: {session_id[:8]}...")
        
        # 讀取最近 2 小時的對話
        messages = read_session_messages(session_id, hours=2)
        print(f"📝 找到 {len(messages)} 條 recent 消息")
        
        # 識別重要內容
        important = identify_important_content(messages)
        print(f"⭐ 識別出 {len(important)} 條重要內容")
        
        # 保存重要內容
        saved_count = 0
        for item in important:
            daily_file = save_to_daily_file(item['content'], item['priority'])
            saved_count += 1
            print(f"  ✅ 保存 [{item['priority']}] {saved_count}/{len(important)} - {len(item['content'])} 字")
        
        if saved_count > 0:
            print(f"💾 已保存至 {daily_file}")
    
    # 最終報告
    print(f"\n📊 最終狀態:")
    new_auto_save, new_heartbeat = check_daily_memory()
    
    if new_auto_save > auto_save_count or new_heartbeat > heartbeat_extract_count:
        print(f"✅ 新增記憶已保存")
        print(f"   - Auto-Save: {new_auto_save - auto_save_count} 條")
        print(f"   - Heartbeat 提取: {new_heartbeat - heartbeat_extract_count} 條")
        print(f"   ↳ 保存至 memory/{datetime.now().strftime('%Y-%m-%d')}.md")
    else:
        print("❌ 無新記憶需要保存")

if __name__ == '__main__':
    main()
