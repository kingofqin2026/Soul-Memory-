#!/usr/bin/env python3
"""
Soul Memory Module D: 版本控制器
追蹤 MEMORY.md 的修改歷史
"""

import json
import os
import subprocess
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple


class VersionControl:
    """MEMORY.md 版本控制器"""
    
    def __init__(
        self,
        memory_file: str = "/root/.openclaw/workspace/MEMORY.md",
        versions_file: str = "/root/.openclaw/workspace/memory-system/versions.json",
        auto_git_commit: bool = True
    ):
        self.memory_file = Path(memory_file)
        self.versions_file = Path(versions_file)
        self.auto_git_commit = auto_git_commit
        self.workspace_root = Path("/root/.openclaw/workspace")
        
        # 確保版本檔案存在
        self._init_versions_file()
    
    def _init_versions_file(self):
        """初始化版本記錄檔案"""
        if not self.versions_file.exists():
            self.versions_file.parent.mkdir(parents=True, exist_ok=True)
            self._save_versions({
                "versions": [],
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "memory_file": str(self.memory_file)
                }
            })
    
    def _load_versions(self) -> Dict[str, Any]:
        """載入版本記錄"""
        with open(self.versions_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_versions(self, data: Dict[str, Any]):
        """保存版本記錄"""
        with open(self.versions_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _generate_version_id(self, timestamp: str, content_hash: str) -> str:
        """生成版本 ID"""
        short_hash = hashlib.md5(content_hash.encode()).hexdigest()[:8]
        ts = datetime.fromisoformat(timestamp).strftime("%Y%m%d_%H%M%S")
        return f"v_{ts}_{short_hash}"
    
    def _compute_content_hash(self, content: str) -> str:
        """計算內容哈希"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _git_commit(self, summary: str) -> Tuple[bool, str]:
        """執行 git commit，返回 (成功與否, commit_hash 或錯誤訊息)"""
        try:
            # 檢查是否在 git repo 中
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return False, "Not a git repository"
            
            # 取得當前 timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            commit_message = f"[{timestamp}] {summary}"
            
            # git add
            subprocess.run(
                ["git", "add", self.memory_file.name],
                cwd=self.workspace_root,
                capture_output=True,
                timeout=30
            )
            
            # git commit
            result = subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # 取得 commit hash
                hash_result = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=self.workspace_root,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                commit_hash = hash_result.stdout.strip()[:12] if hash_result.returncode == 0 else "unknown"
                return True, commit_hash
            else:
                # 可能是沒有變更
                return False, result.stderr.strip() or "No changes to commit"
                
        except subprocess.TimeoutExpired:
            return False, "Git operation timed out"
        except Exception as e:
            return False, str(e)
    
    def save_version(self, content: str, summary: str) -> Dict[str, Any]:
        """
        保存新版本
        
        Args:
            content: MEMORY.md 內容
            summary: 修改摘要
            
        Returns:
            版本資訊字典
        """
        timestamp = datetime.now().isoformat()
        content_hash = self._compute_content_hash(content)
        version_id = self._generate_version_id(timestamp, content_hash)
        
        # 載入現有版本記錄
        data = self._load_versions()
        
        # 檢查是否有實質變更
        if data["versions"]:
            last_version = data["versions"][-1]
            if last_version["content_hash"] == content_hash:
                return {
                    "success": False,
                    "message": "No changes detected (content hash identical)",
                    "version_id": last_version["id"]
                }
        
        # 執行 git commit
        git_commit_hash = None
        git_success = False
        if self.auto_git_commit:
            git_success, git_result = self._git_commit(summary)
            if git_success:
                git_commit_hash = git_result
        
        # 創建版本記錄
        version_entry = {
            "id": version_id,
            "timestamp": timestamp,
            "summary": summary,
            "content_hash": content_hash,
            "git_commit": git_commit_hash,
            "git_committed": git_success,
            "size_bytes": len(content.encode('utf-8')),
            "line_count": len(content.splitlines())
        }
        
        # 保存內容備份
        backup_dir = self.versions_file.parent / "backups"
        backup_dir.mkdir(exist_ok=True)
        backup_file = backup_dir / f"{version_id}.md"
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        version_entry["backup_path"] = str(backup_file)
        
        # 更新版本記錄
        data["versions"].append(version_entry)
        data["metadata"]["updated_at"] = timestamp
        self._save_versions(data)
        
        return {
            "success": True,
            "version_id": version_id,
            "timestamp": timestamp,
            "git_commit": git_commit_hash,
            "git_committed": git_success
        }
    
    def list_versions(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        列出最近版本
        
        Args:
            limit: 最多返回的版本數量，None 表示全部
            
        Returns:
            版本列表
        """
        data = self._load_versions()
        versions = data["versions"]
        
        # 按時間倒序排列（最新的在前面）
        versions = sorted(versions, key=lambda x: x["timestamp"], reverse=True)
        
        if limit is not None:
            versions = versions[:limit]
        
        return versions
    
    def get_version(self, version_id: str) -> Optional[Dict[str, Any]]:
        """
        取得特定版本資訊
        
        Args:
            version_id: 版本 ID
            
        Returns:
            版本資訊，不存在則返回 None
        """
        data = self._load_versions()
        for version in data["versions"]:
            if version["id"] == version_id:
                return version
        return None
    
    def get_version_content(self, version_id: str) -> Optional[str]:
        """
        取得特定版本的內容
        
        Args:
            version_id: 版本 ID
            
        Returns:
            內容字串，不存在則返回 None
        """
        version = self.get_version(version_id)
        if not version:
            return None
        
        backup_path = version.get("backup_path")
        if backup_path and os.path.exists(backup_path):
            with open(backup_path, 'r', encoding='utf-8') as f:
                return f.read()
        return None
    
    def get_diff(self, version_a: str, version_b: str) -> Dict[str, Any]:
        """
        比較兩個版本的差異
        
        Args:
            version_a: 第一個版本 ID
            version_b: 第二個版本 ID
            
        Returns:
            差異資訊字典
        """
        # 取得兩個版本的內容
        content_a = self.get_version_content(version_a) if version_a else None
        content_b = self.get_version_content(version_b) if version_b else None
        
        # 處理 special case
        if version_a == "HEAD":
            if self.memory_file.exists():
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    content_a = f.read()
            else:
                content_a = ""
        
        # 檢查版本是否存在
        info_a = self.get_version(version_a) if version_a != "HEAD" else None
        info_b = self.get_version(version_b) if version_b != "HEAD" else None
        
        if version_a != "HEAD" and content_a is None:
            return {
                "success": False,
                "error": f"Version {version_a} not found"
            }
        
        if version_b != "HEAD" and content_b is None:
            return {
                "success": False,
                "error": f"Version {version_b} not found"
            }
        
        if content_a is None:
            content_a = ""
        if content_b is None:
            content_b = ""
        
        # 計算差異
        lines_a = content_a.splitlines()
        lines_b = content_b.splitlines()
        
        # 簡單的行級差異比較
        diff_result = self._compute_line_diff(lines_a, lines_b)
        
        return {
            "success": True,
            "version_a": {
                "id": version_a,
                "timestamp": info_a["timestamp"] if info_a else "current",
                "summary": info_a["summary"] if info_a else "current state"
            },
            "version_b": {
                "id": version_b,
                "timestamp": info_b["timestamp"] if info_b else "current",
                "summary": info_b["summary"] if info_b else "current state"
            },
            "stats": {
                "lines_added": diff_result["added"],
                "lines_removed": diff_result["removed"],
                "lines_unchanged": diff_result["unchanged"],
                "total_lines_a": len(lines_a),
                "total_lines_b": len(lines_b)
            },
            "diff_text": diff_result["diff_text"]
        }
    
    def _compute_line_diff(self, lines_a: List[str], lines_b: List[str]) -> Dict[str, Any]:
        """計算行級差異（簡化版）"""
        # 使用簡單的 LCS-like 方法
        unmatched_a = []
        unmatched_b = []
        matched = []
        
        lines_b_remaining = list(enumerate(lines_b))
        
        for i, line_a in enumerate(lines_a):
            found = False
            for j, (idx_b, line_b) in enumerate(lines_b_remaining):
                if line_a == line_b:
                    matched.append((i, idx_b, line_a))
                    lines_b_remaining.pop(j)
                    found = True
                    break
            if not found:
                unmatched_a.append((i, line_a))
        
        unmatched_b = lines_b_remaining
        
        # 生成 diff 文本
        diff_lines = []
        diff_lines.append("--- Version A")
        diff_lines.append("+++ Version B")
        diff_lines.append("@@ Diff @@")
        
        for idx, line in unmatched_a:
            diff_lines.append(f"-{line}")
        for idx, line in unmatched_b:
            diff_lines.append(f"+{line}")
        
        return {
            "added": len(unmatched_b),
            "removed": len(unmatched_a),
            "unchanged": len(matched),
            "diff_text": "\n".join(diff_lines)
        }
    
    def rollback(self, version_id: str, create_backup: bool = True) -> Dict[str, Any]:
        """
        回滾到指定版本
        
        Args:
            version_id: 目標版本 ID
            create_backup: 是否先備份當前狀態
            
        Returns:
            回滾結果字典
        """
        # 取得目標版本內容
        target_content = self.get_version_content(version_id)
        if target_content is None:
            return {
                "success": False,
                "error": f"Version {version_id} not found"
            }
        
        # 若存在 MEMORY.md，先備份當前狀態
        rollback_backup_id = None
        if create_backup and self.memory_file.exists():
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                current_content = f.read()
            
            rollback_backup = self.save_version(
                current_content,
                f"AUTO-BACKUP before rollback to {version_id}"
            )
            if rollback_backup["success"]:
                rollback_backup_id = rollback_backup["version_id"]
        
        # 寫入目標版本內容
        try:
            self.memory_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                f.write(target_content)
            
            # 執行 git commit
            git_commit_hash = None
            if self.auto_git_commit:
                git_success, git_hash = self._git_commit(f"Rollback to {version_id}")
                if git_success:
                    git_commit_hash = git_hash
            
            return {
                "success": True,
                "rolled_to": version_id,
                "rollback_backup_id": rollback_backup_id,
                "git_commit": git_commit_hash
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """取得版本統計資訊"""
        data = self._load_versions()
        versions = data["versions"]
        
        if not versions:
            return {
                "total_versions": 0,
                "first_version": None,
                "latest_version": None
            }
        
        total_size = sum(v.get("size_bytes", 0) for v in versions)
        
        return {
            "total_versions": len(versions),
            "first_version": versions[0]["id"],
            "first_timestamp": versions[0]["timestamp"],
            "latest_version": versions[-1]["id"],
            "latest_timestamp": versions[-1]["timestamp"],
            "latest_summary": versions[-1]["summary"],
            "total_size_bytes": total_size,
            "avg_size_bytes": total_size // len(versions) if versions else 0
        }


# 便捷函數，用於直接操作
def get_controller(
    memory_file: str = "/root/.openclaw/workspace/MEMORY.md",
    auto_git_commit: bool = True
) -> VersionControl:
    """取得版本控制器實例"""
    return VersionControl(
        memory_file=memory_file,
        auto_git_commit=auto_git_commit
    )


# 如果直接執行此檔案，執行簡單測試
if __name__ == "__main__":
    import sys
    
    vc = get_controller()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            versions = vc.list_versions(limit=limit)
            print(f"Recent {len(versions)} versions:")
            for v in versions:
                print(f"  - {v['id']}: {v['summary'][:50]}... ({v['timestamp']})")
        
        elif command == "stats":
            stats = vc.get_stats()
            print("Version Control Stats:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
        
        elif command == "diff":
            if len(sys.argv) < 4:
                print("Usage: version_control.py diff <version_a> <version_b>")
                sys.exit(1)
            diff = vc.get_diff(sys.argv[2], sys.argv[3])
            if diff["success"]:
                print(f"Diff: {sys.argv[2]} -> {sys.argv[3]}")
                print(f"  +{diff['stats']['lines_added']} -{diff['stats']['lines_removed']}")
                print(diff["diff_text"])
            else:
                print(f"Error: {diff.get('error')}")
        
        elif command == "rollback":
            if len(sys.argv) < 3:
                print("Usage: version_control.py rollback <version_id>")
                sys.exit(1)
            result = vc.rollback(sys.argv[2])
            if result["success"]:
                print(f"Rolled back to {result['rolled_to']}")
                if result.get("rollback_backup_id"):
                    print(f"Backup created: {result['rollback_backup_id']}")
            else:
                print(f"Error: {result.get('error')}")
        
        else:
            print(f"Unknown command: {command}")
            print("Commands: list, stats, diff, rollback")
    
    else:
        stats = vc.get_stats()
        print("Soul Memory Version Controller")
        print(f"  Total versions: {stats['total_versions']}")
        if stats['latest_version']:
            print(f"  Latest: {stats['latest_version']}")
            print(f"  Last modified: {stats['latest_timestamp']}")
