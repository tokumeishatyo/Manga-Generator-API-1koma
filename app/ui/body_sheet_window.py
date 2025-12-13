# -*- coding: utf-8 -*-
"""
素体三面図（Step2）設定ウィンドウ
顔三面図から素体三面図を生成するための設定
"""

import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog
from typing import Callable, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.base_settings_window import BaseSettingsWindow
from constants import BODY_TYPE_PRESETS, BODY_RENDER_TYPES, CHARACTER_STYLES


class BodySheetWindow(BaseSettingsWindow):
    """素体三面図設定ウィンドウ（Step2）"""

    def __init__(
        self,
        parent,
        callback: Optional[Callable] = None,
        initial_data: Optional[dict] = None,
        face_sheet_path: Optional[str] = None  # Step1の出力画像パス
    ):
        """
        Args:
            parent: 親ウィンドウ
            callback: 設定完了時のコールバック
            initial_data: 初期データ（編集時）
            face_sheet_path: Step1で生成した顔三面図のパス
        """
        self.initial_data = initial_data or {}
        self.face_sheet_path = face_sheet_path
        super().__init__(
            parent,
            title="Step2: 素体三面図設定",
            width=700,
            height=550,
            callback=callback
        )

    def build_content(self):
        """コンテンツを構築"""
        # === 入力画像（顔三面図） ===
        input_frame = ctk.CTkFrame(self.content_frame)
        input_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        input_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            input_frame,
            text="入力画像（顔三面図）",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkLabel(input_frame, text="顔三面図:").grid(row=1, column=0, padx=10, pady=5, sticky="w")

        img_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        img_frame.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        img_frame.grid_columnconfigure(0, weight=1)

        self.face_image_entry = ctk.CTkEntry(
            img_frame,
            placeholder_text="Step1で生成した顔三面図のパス"
        )
        self.face_image_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        if self.face_sheet_path:
            self.face_image_entry.insert(0, self.face_sheet_path)

        ctk.CTkButton(
            img_frame,
            text="参照",
            width=60,
            command=self._browse_face_image
        ).grid(row=0, column=1)

        # === 体型設定 ===
        body_frame = ctk.CTkFrame(self.content_frame)
        body_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        body_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            body_frame,
            text="体型設定",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        # 体型プリセット
        ctk.CTkLabel(body_frame, text="体型:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.body_type_menu = ctk.CTkOptionMenu(
            body_frame,
            values=list(BODY_TYPE_PRESETS.keys()),
            width=180,
            command=self._on_body_type_change
        )
        self.body_type_menu.set("標準体型（女性）")
        self.body_type_menu.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # 体型説明
        self.body_type_desc = ctk.CTkLabel(
            body_frame,
            text="",
            font=("Arial", 10),
            text_color="gray"
        )
        self.body_type_desc.grid(row=2, column=0, columnspan=2, padx=15, pady=(0, 5), sticky="w")
        self._on_body_type_change("標準体型（女性）")

        # 素体表現タイプ
        ctk.CTkLabel(body_frame, text="表現:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.render_type_menu = ctk.CTkOptionMenu(
            body_frame,
            values=list(BODY_RENDER_TYPES.keys()),
            width=180
        )
        self.render_type_menu.set("素体（白レオタード）")
        self.render_type_menu.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # スタイル（継承）
        ctk.CTkLabel(body_frame, text="スタイル:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.style_menu = ctk.CTkOptionMenu(
            body_frame,
            values=list(CHARACTER_STYLES.keys()),
            width=150
        )
        self.style_menu.set("標準アニメ")
        self.style_menu.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        # === 詳細設定 ===
        detail_frame = ctk.CTkFrame(self.content_frame)
        detail_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        detail_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            detail_frame,
            text="詳細設定",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        # 追加説明
        ctk.CTkLabel(detail_frame, text="追加説明:").grid(row=1, column=0, padx=10, pady=5, sticky="nw")
        self.description_textbox = ctk.CTkTextbox(detail_frame, height=80, wrap="word")
        self.description_textbox.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.description_textbox.insert("1.0", "（任意）体型の追加詳細を記述")

        # === 制約事項表示 ===
        constraint_frame = ctk.CTkFrame(self.content_frame)
        constraint_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(
            constraint_frame,
            text="生成時の制約",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        constraints_text = """• 顔三面図の顔をそのまま使用（変更禁止）
• 体型は指定されたプリセットに従う
• 服装は追加しない（素体のみ）
• 三面図形式を維持（正面/横/背面）"""

        ctk.CTkLabel(
            constraint_frame,
            text=constraints_text,
            font=("Arial", 11),
            justify="left"
        ).pack(anchor="w", padx=15, pady=(0, 10))

    def _browse_face_image(self):
        """顔三面図参照ダイアログ"""
        filename = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]
        )
        if filename:
            self.face_image_entry.delete(0, tk.END)
            self.face_image_entry.insert(0, filename)

    def _on_body_type_change(self, value):
        """体型プリセット変更時"""
        preset = BODY_TYPE_PRESETS.get(value, {})
        desc = preset.get("description", "")
        self.body_type_desc.configure(text=f"→ {desc}")

    def collect_data(self) -> dict:
        """UIから設定データを収集"""
        desc = self.description_textbox.get("1.0", tk.END).strip()
        if desc == "（任意）体型の追加詳細を記述":
            desc = ""

        return {
            'step_type': 'step2_body',
            'face_sheet_path': self.face_image_entry.get().strip(),
            'body_type': self.body_type_menu.get(),
            'render_type': self.render_type_menu.get(),
            'character_style': self.style_menu.get(),
            'additional_description': desc
        }

    def validate(self) -> tuple[bool, str]:
        """入力検証"""
        face_path = self.face_image_entry.get().strip()
        if not face_path:
            return False, "顔三面図の画像パスを指定してください。\n（Step1の出力画像を選択）"
        return True, ""
