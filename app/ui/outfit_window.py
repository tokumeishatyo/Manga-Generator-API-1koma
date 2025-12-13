# -*- coding: utf-8 -*-
"""
衣装着用（Step3）設定ウィンドウ
素体三面図に衣装を着せるための設定
"""

import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog
from typing import Callable, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.base_settings_window import BaseSettingsWindow
from constants import OUTFIT_DATA, CHARACTER_STYLES


class OutfitWindow(BaseSettingsWindow):
    """衣装着用設定ウィンドウ（Step3）"""

    def __init__(
        self,
        parent,
        callback: Optional[Callable] = None,
        initial_data: Optional[dict] = None,
        body_sheet_path: Optional[str] = None  # Step2の出力画像パス
    ):
        """
        Args:
            parent: 親ウィンドウ
            callback: 設定完了時のコールバック
            initial_data: 初期データ（編集時）
            body_sheet_path: Step2で生成した素体三面図のパス
        """
        self.initial_data = initial_data or {}
        self.body_sheet_path = body_sheet_path
        super().__init__(
            parent,
            title="Step3: 衣装着用設定",
            width=750,
            height=650,
            callback=callback
        )

    def build_content(self):
        """コンテンツを構築"""
        # === 入力画像（素体三面図） ===
        input_frame = ctk.CTkFrame(self.content_frame)
        input_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        input_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            input_frame,
            text="入力画像（素体三面図）",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkLabel(input_frame, text="素体三面図:").grid(row=1, column=0, padx=10, pady=5, sticky="w")

        img_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        img_frame.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        img_frame.grid_columnconfigure(0, weight=1)

        self.body_image_entry = ctk.CTkEntry(
            img_frame,
            placeholder_text="Step2で生成した素体三面図のパス"
        )
        self.body_image_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        if self.body_sheet_path:
            self.body_image_entry.insert(0, self.body_sheet_path)

        ctk.CTkButton(
            img_frame,
            text="参照",
            width=60,
            command=self._browse_body_image
        ).grid(row=0, column=1)

        # === 衣装選択 ===
        outfit_frame = ctk.CTkFrame(self.content_frame)
        outfit_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        outfit_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            outfit_frame,
            text="衣装設定",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        # カテゴリ
        ctk.CTkLabel(outfit_frame, text="カテゴリ:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.category_menu = ctk.CTkOptionMenu(
            outfit_frame,
            values=list(OUTFIT_DATA["カテゴリ"].keys()),
            width=180,
            command=self._on_category_change
        )
        self.category_menu.set("カジュアル")
        self.category_menu.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # 形状（カテゴリに応じて変化）
        ctk.CTkLabel(outfit_frame, text="形状:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.shape_menu = ctk.CTkOptionMenu(
            outfit_frame,
            values=["おまかせ"],
            width=180
        )
        self.shape_menu.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # 色
        ctk.CTkLabel(outfit_frame, text="色:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.color_menu = ctk.CTkOptionMenu(
            outfit_frame,
            values=list(OUTFIT_DATA["色"].keys()),
            width=180
        )
        self.color_menu.set("おまかせ")
        self.color_menu.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # 柄
        ctk.CTkLabel(outfit_frame, text="柄:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.pattern_menu = ctk.CTkOptionMenu(
            outfit_frame,
            values=list(OUTFIT_DATA["柄"].keys()),
            width=180
        )
        self.pattern_menu.set("おまかせ")
        self.pattern_menu.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        # スタイル
        ctk.CTkLabel(outfit_frame, text="印象:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.style_menu = ctk.CTkOptionMenu(
            outfit_frame,
            values=list(OUTFIT_DATA["スタイル"].keys()),
            width=180
        )
        self.style_menu.set("おまかせ")
        self.style_menu.grid(row=5, column=1, padx=5, pady=5, sticky="w")

        # 初期化（カテゴリ選択に応じて形状を更新）
        self._on_category_change("カジュアル")

        # === 描画スタイル（継承） ===
        style_frame = ctk.CTkFrame(self.content_frame)
        style_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        style_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            style_frame,
            text="描画スタイル",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkLabel(style_frame, text="スタイル:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.character_style_menu = ctk.CTkOptionMenu(
            style_frame,
            values=list(CHARACTER_STYLES.keys()),
            width=150
        )
        self.character_style_menu.set("標準アニメ")
        self.character_style_menu.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # === 追加説明 ===
        detail_frame = ctk.CTkFrame(self.content_frame)
        detail_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        detail_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            detail_frame,
            text="追加説明",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkLabel(detail_frame, text="詳細:").grid(row=1, column=0, padx=10, pady=5, sticky="nw")
        self.description_textbox = ctk.CTkTextbox(detail_frame, height=60, wrap="word")
        self.description_textbox.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.description_textbox.insert("1.0", "（任意）衣装の追加詳細を記述")

        # === 制約事項表示 ===
        constraint_frame = ctk.CTkFrame(self.content_frame)
        constraint_frame.grid(row=4, column=0, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(
            constraint_frame,
            text="生成時の制約",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        constraints_text = """• 素体三面図の顔・体型をそのまま使用（変更禁止）
• 指定された衣装を着用（素体の上に衣装を描画）
• 三面図形式を維持（正面/横/背面）
• 衣装のみを変更（髪型・顔は変更しない）"""

        ctk.CTkLabel(
            constraint_frame,
            text=constraints_text,
            font=("Arial", 11),
            justify="left"
        ).pack(anchor="w", padx=15, pady=(0, 10))

    def _browse_body_image(self):
        """素体三面図参照ダイアログ"""
        filename = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]
        )
        if filename:
            self.body_image_entry.delete(0, tk.END)
            self.body_image_entry.insert(0, filename)

    def _on_category_change(self, value):
        """カテゴリ変更時に形状オプションを更新"""
        shapes = OUTFIT_DATA["形状"].get(value, {"おまかせ": ""})
        self.shape_menu.configure(values=list(shapes.keys()))
        self.shape_menu.set("おまかせ")

    def collect_data(self) -> dict:
        """UIから設定データを収集"""
        desc = self.description_textbox.get("1.0", tk.END).strip()
        if desc == "（任意）衣装の追加詳細を記述":
            desc = ""

        return {
            'step_type': 'step3_outfit',
            'body_sheet_path': self.body_image_entry.get().strip(),
            'outfit': {
                'category': self.category_menu.get(),
                'shape': self.shape_menu.get(),
                'color': self.color_menu.get(),
                'pattern': self.pattern_menu.get(),
                'style': self.style_menu.get()
            },
            'character_style': self.character_style_menu.get(),
            'additional_description': desc
        }

    def validate(self) -> tuple[bool, str]:
        """入力検証"""
        body_path = self.body_image_entry.get().strip()
        if not body_path:
            return False, "素体三面図の画像パスを指定してください。\n（Step2の出力画像を選択）"
        return True, ""
