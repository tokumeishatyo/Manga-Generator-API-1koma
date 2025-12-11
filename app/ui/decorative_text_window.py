# -*- coding: utf-8 -*-
"""
装飾テキスト設定ウィンドウ
装飾テキストの設定
"""

import tkinter as tk
import customtkinter as ctk
from typing import Callable, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.base_settings_window import BaseSettingsWindow
from constants import TEXT_POSITIONS, DECORATIVE_TEXT_STYLES


class DecorativeTextWindow(BaseSettingsWindow):
    """装飾テキスト設定ウィンドウ"""

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
            title="装飾テキスト設定",
            width=650,
            height=500,
            callback=callback
        )

    def build_content(self):
        """コンテンツを構築"""
        # === テキスト入力セクション ===
        text_frame = ctk.CTkFrame(self.content_frame)
        text_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        text_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            text_frame,
            text="装飾テキスト",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=4, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkLabel(
            text_frame,
            text="画像内に配置するテキストを設定します",
            font=("Arial", 11),
            text_color="gray"
        ).grid(row=1, column=0, columnspan=4, padx=10, pady=(0, 10), sticky="w")

        # テキスト入力（3スロット）
        self.text_entries = []
        self.position_menus = []
        self.style_menus = []

        default_positions = ["中央上", "中央", "右下"]
        default_styles = ["タイトル", "サブタイトル", "クレジット"]

        for i in range(3):
            # ラベル
            ctk.CTkLabel(
                text_frame,
                text=f"テキスト{i + 1}:"
            ).grid(row=i + 2, column=0, padx=10, pady=5, sticky="w")

            # テキスト入力
            entry = ctk.CTkEntry(
                text_frame,
                placeholder_text="テキストを入力"
            )
            entry.grid(row=i + 2, column=1, padx=5, pady=5, sticky="ew")
            self.text_entries.append(entry)

            # 位置
            pos_menu = ctk.CTkOptionMenu(
                text_frame,
                values=list(TEXT_POSITIONS.keys()),
                width=90
            )
            pos_menu.set(default_positions[i])
            pos_menu.grid(row=i + 2, column=2, padx=5, pady=5)
            self.position_menus.append(pos_menu)

            # スタイル
            style_menu = ctk.CTkOptionMenu(
                text_frame,
                values=list(DECORATIVE_TEXT_STYLES.keys()),
                width=100
            )
            style_menu.set(default_styles[i])
            style_menu.grid(row=i + 2, column=3, padx=5, pady=5)
            self.style_menus.append(style_menu)

        # ヘルプテキスト
        help_frame = ctk.CTkFrame(self.content_frame)
        help_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(
            help_frame,
            text="配置位置の説明",
            font=("Arial", 14, "bold")
        ).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        positions_text = """
左上    中央上    右上
左中    中央      右中
左下    中央下    右下
"""
        ctk.CTkLabel(
            help_frame,
            text=positions_text,
            font=("Courier", 12),
            justify="left"
        ).grid(row=1, column=0, padx=10, pady=5, sticky="w")

    def collect_data(self) -> dict:
        """UIから設定データを収集"""
        texts = []
        for i in range(3):
            content = self.text_entries[i].get().strip()
            if content:
                texts.append({
                    'content': content,
                    'position': self.position_menus[i].get(),
                    'style': self.style_menus[i].get()
                })
        return {'texts': texts}

    def validate(self) -> tuple[bool, str]:
        """入力検証"""
        # 少なくとも1つのテキストが必要
        any_text = any(entry.get().strip() for entry in self.text_entries)
        if not any_text:
            return False, "少なくとも1つのテキストを入力してください。"
        return True, ""
