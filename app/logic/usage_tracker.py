# -*- coding: utf-8 -*-
"""
API使用量トラッキングモジュール
"""

import json
import os
from datetime import datetime, date
from typing import Dict, Any, Optional


class UsageTracker:
    """API使用量を記録・管理するクラス"""

    def __init__(self, storage_path: str = None):
        """
        Args:
            storage_path: 使用量データの保存パス
        """
        if storage_path is None:
            # デフォルトはappディレクトリ内
            app_dir = os.path.dirname(os.path.dirname(__file__))
            storage_path = os.path.join(app_dir, "api_usage.json")

        self.storage_path = storage_path
        self.data = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        """保存されたデータを読み込む"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        # 初期データ構造
        return {
            "total_count": 0,
            "daily_records": {},
            "mode_counts": {
                "normal": 0,
                "redraw": 0,
                "simple": 0,
                "refine": 0
            },
            "resolution_counts": {
                "1K": 0,
                "2K": 0,
                "4K": 0
            }
        }

    def _save_data(self):
        """データを保存"""
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Error saving usage data: {e}")

    def record_usage(self, mode: str, resolution: str, success: bool):
        """
        API使用を記録

        Args:
            mode: 生成モード ("normal", "redraw", "simple", "refine")
            resolution: 解像度 ("1K", "2K", "4K")
            success: 成功したかどうか
        """
        today = date.today().isoformat()
        now = datetime.now().strftime("%H:%M:%S")

        # 日別レコードの初期化
        if today not in self.data["daily_records"]:
            self.data["daily_records"][today] = {
                "count": 0,
                "success_count": 0,
                "details": []
            }

        # 記録を追加
        record = {
            "time": now,
            "mode": mode,
            "resolution": resolution,
            "success": success
        }
        self.data["daily_records"][today]["details"].append(record)
        self.data["daily_records"][today]["count"] += 1
        if success:
            self.data["daily_records"][today]["success_count"] += 1

        # 累計カウント
        self.data["total_count"] += 1

        # モード別カウント
        if mode in self.data["mode_counts"]:
            self.data["mode_counts"][mode] += 1

        # 解像度別カウント
        if resolution in self.data["resolution_counts"]:
            self.data["resolution_counts"][resolution] += 1

        # 保存
        self._save_data()

    def get_today_count(self) -> int:
        """本日の使用回数を取得"""
        today = date.today().isoformat()
        if today in self.data["daily_records"]:
            return self.data["daily_records"][today]["count"]
        return 0

    def get_month_count(self) -> int:
        """今月の使用回数を取得"""
        current_month = date.today().strftime("%Y-%m")
        count = 0
        for day, record in self.data["daily_records"].items():
            if day.startswith(current_month):
                count += record["count"]
        return count

    def get_total_count(self) -> int:
        """累計使用回数を取得"""
        return self.data["total_count"]

    def get_mode_counts(self) -> Dict[str, int]:
        """モード別使用回数を取得"""
        return self.data["mode_counts"].copy()

    def get_resolution_counts(self) -> Dict[str, int]:
        """解像度別使用回数を取得"""
        return self.data["resolution_counts"].copy()

    def get_today_success_rate(self) -> Optional[float]:
        """本日の成功率を取得"""
        today = date.today().isoformat()
        if today in self.data["daily_records"]:
            record = self.data["daily_records"][today]
            if record["count"] > 0:
                return record["success_count"] / record["count"] * 100
        return None

    def get_statistics(self) -> Dict[str, Any]:
        """統計情報を取得"""
        today_rate = self.get_today_success_rate()
        return {
            "today": self.get_today_count(),
            "month": self.get_month_count(),
            "total": self.get_total_count(),
            "mode_counts": self.get_mode_counts(),
            "resolution_counts": self.get_resolution_counts(),
            "today_success_rate": today_rate
        }

    def get_recent_records(self, limit: int = 10) -> list:
        """最近の記録を取得"""
        today = date.today().isoformat()
        if today in self.data["daily_records"]:
            details = self.data["daily_records"][today]["details"]
            return details[-limit:][::-1]  # 新しい順
        return []


# シングルトンインスタンス
_tracker_instance = None


def get_tracker() -> UsageTracker:
    """トラッカーのシングルトンインスタンスを取得"""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = UsageTracker()
    return _tracker_instance
