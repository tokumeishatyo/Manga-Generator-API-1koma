# -*- coding: utf-8 -*-
"""
三面図（キャラクターシート）設定ウィンドウ
全身三面図・顔三面図の設定
"""

import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog
from typing import Callable, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.base_settings_window import BaseSettingsWindow
from constants import OUTFIT_DATA, CHARACTER_DESCRIPTION_PLACEHOLDER, CHARACTER_STYLES
from logic.character import get_shape_options


class CharacterSheetWindow(BaseSettingsWindow):
    """三面図設定ウィンドウ"""

    def __init__(
        self,
        parent,
        sheet_type: str = "fullbody",  # "fullbody" or "face"
        callback: Optional[Callable] = None,
        initial_data: Optional[dict] = None
    ):
        """
        Args:
            parent: 親ウィンドウ
            sheet_type: "fullbody"（全身三面図）または "face"（顔三面図）
            callback: 設定完了時のコールバック
            initial_data: 初期データ（編集時）
        """
        self.sheet_type = sheet_type
        self.initial_data = initial_data or {}
        title = "全身三面図設定" if sheet_type == "fullbody" else "顔三面図設定"
        super().__init__(
            parent,
            title=title,
            width=850,
            height=380,
            callback=callback
        )

    def build_content(self):
        """コンテンツを構築"""
        # === キャラクター基本情報 ===
        basic_frame = ctk.CTkFrame(self.content_frame)
        basic_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        basic_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            basic_frame,
            text="キャラクター情報",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 5), sticky="w")

        # 名前
        ctk.CTkLabel(basic_frame, text="名前:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.name_entry = ctk.CTkEntry(basic_frame, placeholder_text="キャラクター名")
        self.name_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # スタイル選択（標準アニメ/ドット絵/ちびキャラ）
        ctk.CTkLabel(basic_frame, text="スタイル:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.style_menu = ctk.CTkOptionMenu(
            basic_frame,
            values=list(CHARACTER_STYLES.keys()),
            width=150
        )
        self.style_menu.set("標準アニメ")
        self.style_menu.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # 参照画像
        ctk.CTkLabel(basic_frame, text="参照画像:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        img_frame = ctk.CTkFrame(basic_frame, fg_color="transparent")
        img_frame.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        img_frame.grid_columnconfigure(0, weight=1)

        self.image_entry = ctk.CTkEntry(img_frame, placeholder_text="参照画像パス（任意）")
        self.image_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkButton(
            img_frame,
            text="参照",
            width=60,
            command=self._browse_image
        ).grid(row=0, column=1)

        # キャラクター説明
        ctk.CTkLabel(basic_frame, text="外見説明:").grid(row=4, column=0, padx=10, pady=5, sticky="nw")
        self.description_textbox = ctk.CTkTextbox(basic_frame, height=100, wrap="word")
        self.description_textbox.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        self.description_textbox.insert("1.0", CHARACTER_DESCRIPTION_PLACEHOLDER)

        # === 服装設定（全身三面図のみ） ===
        if self.sheet_type == "fullbody":
            self._build_outfit_section()

    def _build_outfit_section(self):
        """服装セクションを構築（全身三面図のみ）"""
        outfit_frame = ctk.CTkFrame(self.content_frame)
        outfit_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(
            outfit_frame,
            text="服装設定",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        # 全ドロップダウンを横一列に配置
        row_frame = ctk.CTkFrame(outfit_frame, fg_color="transparent")
        row_frame.pack(fill="x", padx=10, pady=5)

        # カテゴリ（OUTFIT_DATA["カテゴリ"]から取得）
        ctk.CTkLabel(row_frame, text="カテゴリ:").pack(side="left", padx=(0, 2))
        categories = list(OUTFIT_DATA["カテゴリ"].keys())
        self.outfit_category = ctk.CTkOptionMenu(
            row_frame,
            values=categories,
            width=120,
            command=self._on_category_change
        )
        self.outfit_category.set("おまかせ")
        self.outfit_category.pack(side="left", padx=(0, 8))

        # 形状（カテゴリに応じて動的に変更）
        ctk.CTkLabel(row_frame, text="形状:").pack(side="left", padx=(0, 2))
        self.outfit_shape = ctk.CTkOptionMenu(row_frame, values=["おまかせ"], width=120)
        self.outfit_shape.pack(side="left", padx=(0, 8))

        # 色（OUTFIT_DATA["色"]から取得）
        ctk.CTkLabel(row_frame, text="色:").pack(side="left", padx=(0, 2))
        self.outfit_color = ctk.CTkOptionMenu(
            row_frame,
            values=list(OUTFIT_DATA["色"].keys()),
            width=90
        )
        self.outfit_color.set("おまかせ")
        self.outfit_color.pack(side="left", padx=(0, 8))

        # 柄（OUTFIT_DATA["柄"]から取得）
        ctk.CTkLabel(row_frame, text="柄:").pack(side="left", padx=(0, 2))
        self.outfit_pattern = ctk.CTkOptionMenu(
            row_frame,
            values=list(OUTFIT_DATA["柄"].keys()),
            width=100
        )
        self.outfit_pattern.set("おまかせ")
        self.outfit_pattern.pack(side="left", padx=(0, 8))

        # スタイル（OUTFIT_DATA["スタイル"]から取得）
        ctk.CTkLabel(row_frame, text="スタイル:").pack(side="left", padx=(0, 2))
        self.outfit_style = ctk.CTkOptionMenu(
            row_frame,
            values=list(OUTFIT_DATA["スタイル"].keys()),
            width=100
        )
        self.outfit_style.set("おまかせ")
        self.outfit_style.pack(side="left")

    def _browse_image(self):
        """画像参照ダイアログ"""
        filename = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]
        )
        if filename:
            self.image_entry.delete(0, tk.END)
            self.image_entry.insert(0, filename)

    def _on_category_change(self, value):
        """服装カテゴリ変更時"""
        shapes = get_shape_options(value)
        self.outfit_shape.configure(values=shapes)
        self.outfit_shape.set(shapes[0] if shapes else "おまかせ")

    def collect_data(self) -> dict:
        """UIから設定データを収集"""
        desc = self.description_textbox.get("1.0", tk.END).strip()
        if desc == CHARACTER_DESCRIPTION_PLACEHOLDER:
            desc = ""

        data = {
            'sheet_type': self.sheet_type,
            'name': self.name_entry.get().strip(),
            'character_style': self.style_menu.get(),
            'description': desc,
            'image_path': self.image_entry.get().strip()
        }

        if self.sheet_type == "fullbody":
            data['outfit'] = {
                'category': self.outfit_category.get(),
                'shape': self.outfit_shape.get(),
                'color': self.outfit_color.get(),
                'pattern': self.outfit_pattern.get(),
                'style': self.outfit_style.get()
            }

        return data

    def validate(self) -> tuple[bool, str]:
        """入力検証"""
        desc = self.description_textbox.get("1.0", tk.END).strip()
        if not desc or desc == CHARACTER_DESCRIPTION_PLACEHOLDER:
            return False, "キャラクターの外見説明を入力してください。"
        return True, ""
