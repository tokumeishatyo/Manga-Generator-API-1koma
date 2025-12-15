# -*- coding: utf-8 -*-
"""
装飾テキスト配置ウィンドウ
複数の装飾テキストをシーンに配置するための設定
最大9箇所、位置の重複不可
"""

import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog
from typing import Callable, Optional, List, Dict
import os


# 位置のプリセット（参考用）
POSITION_PRESETS = [
    "Top Left", "Top Center", "Top Right",
    "Center Left", "Center", "Center Right",
    "Bottom Left", "Bottom Center", "Bottom Right"
]

# レイヤー設定
LAYER_OPTIONS = {
    "最前面": "Frontmost (Above Characters)",
    "キャラの後ろ": "Behind Characters",
    "背景の前": "Above Background Only"
}

LAYER_ORDER = ["最前面", "キャラの後ろ", "背景の前"]

MAX_OVERLAYS = 10


class TextOverlayPlacementWindow(ctk.CTkToplevel):
    """装飾テキスト配置ウィンドウ"""

    def __init__(
        self,
        parent,
        callback: Optional[Callable] = None,
        initial_data: Optional[List[Dict]] = None
    ):
        super().__init__(parent)

        self.callback = callback
        self.initial_data = initial_data or []
        self.entries: List[Dict] = []  # UIエントリを保持

        # ウィンドウ設定
        self.title("装飾テキスト配置設定")
        self.geometry("550x680")
        self.resizable(True, True)
        self.transient(parent)

        self._build_ui()
        self._load_initial_data()

    def _build_ui(self):
        """UIを構築"""
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # タイトル
        ctk.CTkLabel(
            main_frame,
            text="装飾テキスト配置",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", pady=(0, 5))

        ctk.CTkLabel(
            main_frame,
            text="位置は自由入力（例: Top Center, Bottom Right, Near Character 1）",
            font=("Arial", 11),
            text_color="gray"
        ).pack(anchor="w", pady=(0, 10))

        # 追加/削除ボタン
        button_row = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_row.pack(fill="x", pady=5)

        self.add_button = ctk.CTkButton(
            button_row,
            text="＋ 追加",
            width=80,
            command=self._add_entry
        )
        self.add_button.pack(side="left", padx=(0, 5))

        self.remove_button = ctk.CTkButton(
            button_row,
            text="－ 削除",
            width=80,
            command=self._remove_last_entry,
            fg_color="gray"
        )
        self.remove_button.pack(side="left")

        self.count_label = ctk.CTkLabel(
            button_row,
            text="0 / 11",
            font=("Arial", 12)
        )
        self.count_label.pack(side="right", padx=10)

        # エントリリスト用スクロールフレーム
        self.list_frame = ctk.CTkScrollableFrame(main_frame, height=450)
        self.list_frame.pack(fill="both", expand=True, pady=10)

        # OK/キャンセルボタン
        footer_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        footer_frame.pack(fill="x", pady=(10, 0))

        ctk.CTkButton(
            footer_frame,
            text="OK",
            width=100,
            command=self._on_ok
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            footer_frame,
            text="キャンセル",
            width=100,
            command=self.destroy,
            fg_color="gray"
        ).pack(side="right", padx=5)

    def _load_initial_data(self):
        """初期データを読み込み"""
        for item in self.initial_data:
            self._add_entry(
                image_path=item.get('image', ''),
                position=item.get('position', ''),
                layer=item.get('layer', '最前面')
            )

    def _add_entry(self, image_path: str = "", position: str = "", layer: str = "最前面"):
        """エントリを追加"""
        if len(self.entries) >= MAX_OVERLAYS:
            return

        entry_frame = ctk.CTkFrame(self.list_frame)
        entry_frame.pack(fill="x", pady=3)

        # 番号
        idx = len(self.entries) + 1
        ctk.CTkLabel(
            entry_frame,
            text=f"{idx}.",
            width=25
        ).pack(side="left", padx=(5, 2))

        # 画像パス
        img_entry = ctk.CTkEntry(
            entry_frame,
            placeholder_text="画像パス",
            width=180
        )
        img_entry.pack(side="left", padx=2)
        if image_path:
            img_entry.insert(0, image_path)

        # 参照ボタン
        ctk.CTkButton(
            entry_frame,
            text="参照",
            width=45,
            command=lambda e=img_entry: self._browse_image(e)
        ).pack(side="left", padx=2)

        # 位置入力（テキストボックス）
        position_entry = ctk.CTkEntry(
            entry_frame,
            placeholder_text="Center",
            width=100
        )
        position_entry.pack(side="left", padx=2)
        if position:
            position_entry.insert(0, position)
        else:
            position_entry.insert(0, "Center")

        # レイヤー選択
        layer_menu = ctk.CTkOptionMenu(
            entry_frame,
            values=LAYER_ORDER,
            width=110
        )
        layer_menu.set(layer if layer in LAYER_ORDER else "最前面")
        layer_menu.pack(side="left", padx=2)

        # エントリ情報を保存
        entry_data = {
            'frame': entry_frame,
            'image_entry': img_entry,
            'position_entry': position_entry,
            'layer_menu': layer_menu
        }
        self.entries.append(entry_data)

        self._update_ui_state()

    def _remove_last_entry(self):
        """最後のエントリを削除"""
        if not self.entries:
            return

        entry = self.entries.pop()
        entry['frame'].destroy()

        self._update_ui_state()

    def _update_ui_state(self):
        """UI状態を更新"""
        count = len(self.entries)
        self.count_label.configure(text=f"{count} / {MAX_OVERLAYS}")

        # 追加ボタンの有効/無効
        if count >= MAX_OVERLAYS:
            self.add_button.configure(state="disabled")
        else:
            self.add_button.configure(state="normal")

        # 削除ボタンの有効/無効
        if count == 0:
            self.remove_button.configure(state="disabled")
        else:
            self.remove_button.configure(state="normal")

    def _browse_image(self, entry):
        """画像参照"""
        filename = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]
        )
        if filename:
            entry.delete(0, tk.END)
            entry.insert(0, filename)

    def _on_ok(self):
        """OK押下時"""
        data = self.collect_data()
        if self.callback:
            self.callback(data)
        self.destroy()

    def collect_data(self) -> List[Dict]:
        """データを収集"""
        result = []
        for entry in self.entries:
            image_path = entry['image_entry'].get().strip()
            position = entry['position_entry'].get().strip()
            layer = entry['layer_menu'].get()

            if image_path and position:
                result.append({
                    'image': image_path,
                    'position': position,
                    'layer': layer,
                    'layer_en': LAYER_OPTIONS.get(layer, "Frontmost (Above Characters)")
                })

        return result
