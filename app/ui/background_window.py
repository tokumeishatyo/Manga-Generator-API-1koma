# -*- coding: utf-8 -*-
"""
背景生成設定ウィンドウ
背景のみの画像生成設定
"""

import tkinter as tk
import customtkinter as ctk
from typing import Callable, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.base_settings_window import BaseSettingsWindow


class BackgroundWindow(BaseSettingsWindow):
    """背景生成設定ウィンドウ"""

    def __init__(
        self,
        parent,
        callback: Optional[Callable] = None,
        initial_data: Optional[dict] = None
    ):
        """
        Args:
            parent: 親ウィンドウ
            callback: 設定完了時のコールバック
            initial_data: 初期データ（編集時）
        """
        self.initial_data = initial_data or {}
        super().__init__(
            parent,
            title="背景生成設定",
            width=600,
            height=400,
            callback=callback
        )

    def build_content(self):
        """コンテンツを構築"""
        # === 背景説明 ===
        desc_frame = ctk.CTkFrame(self.content_frame)
        desc_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        desc_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            desc_frame,
            text="背景説明",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkLabel(
            desc_frame,
            text="場所、時間帯、天候、雰囲気などを詳しく記述してください",
            font=("Arial", 11),
            text_color="gray"
        ).grid(row=1, column=0, padx=10, pady=(0, 5), sticky="w")

        self.description_textbox = ctk.CTkTextbox(desc_frame, height=150, wrap="word")
        self.description_textbox.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        self.description_textbox.insert("1.0", "例：夜の学校の教室、月明かりが窓から差し込む、静かで少し不気味な雰囲気")

        # === プリセット ===
        preset_frame = ctk.CTkFrame(self.content_frame)
        preset_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(
            preset_frame,
            text="プリセット",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        presets = [
            ("学校 - 教室（昼）", "明るい昼間の学校の教室、窓から日差し、机と椅子が並ぶ"),
            ("学校 - 教室（夜）", "夜の学校の教室、月明かりが窓から差し込む、静かな雰囲気"),
            ("学校 - 廊下", "学校の廊下、ロッカーが並ぶ、窓から光が差し込む"),
            ("公園", "緑豊かな公園、ベンチ、木々、青空"),
            ("街中", "都会の街並み、ビル、歩道、人通り"),
            ("海辺", "海岸、砂浜、波、青い空と海"),
            ("部屋 - 自室", "一般的な部屋、ベッド、机、本棚"),
            ("ファンタジー - 森", "幻想的な森、大きな木々、木漏れ日"),
            ("ファンタジー - 城", "壮大な城、塔、旗がなびく"),
        ]

        preset_buttons_frame = ctk.CTkFrame(preset_frame, fg_color="transparent")
        preset_buttons_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        for i, (name, desc) in enumerate(presets):
            btn = ctk.CTkButton(
                preset_buttons_frame,
                text=name,
                width=150,
                height=30,
                command=lambda d=desc: self._apply_preset(d)
            )
            btn.grid(row=i // 3, column=i % 3, padx=3, pady=3)

    def _apply_preset(self, description: str):
        """プリセットを適用"""
        self.description_textbox.delete("1.0", tk.END)
        self.description_textbox.insert("1.0", description)

    def collect_data(self) -> dict:
        """UIから設定データを収集"""
        return {
            'description': self.description_textbox.get("1.0", tk.END).strip()
        }

    def validate(self) -> tuple[bool, str]:
        """入力検証"""
        desc = self.description_textbox.get("1.0", tk.END).strip()
        if not desc:
            return False, "背景の説明を入力してください。"
        return True, ""
