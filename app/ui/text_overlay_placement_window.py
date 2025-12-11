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


# 配置位置（絶対位置 9箇所 + キャラクター相対位置 2箇所）
TEXT_POSITIONS_ABSOLUTE = {
    "上部左": "Top Left",
    "上部中央": "Top Center",
    "上部右": "Top Right",
    "中央左": "Center Left",
    "中央": "Center",
    "中央右": "Center Right",
    "下部左": "Bottom Left",
    "下部中央": "Bottom Center",
    "下部右": "Bottom Right"
}

TEXT_POSITIONS_RELATIVE = {
    "左キャラ付近（自動）": "Near Left Character",
    "右キャラ付近（自動）": "Near Right Character"
}

# 全位置（UIで使用）
TEXT_POSITIONS = {**TEXT_POSITIONS_ABSOLUTE, **TEXT_POSITIONS_RELATIVE}

# ドロップダウン表示順（絶対位置→キャラ相対位置）
POSITION_ORDER = [
    # 絶対位置
    "上部左", "上部中央", "上部右",
    "中央左", "中央", "中央右",
    "下部左", "下部中央", "下部右",
    # キャラ相対位置
    "左キャラ付近（自動）", "右キャラ付近（自動）"
]

MAX_OVERLAYS = 11  # 9 + 2


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
            text="最大11箇所（絶対位置9 + キャラ付近2）。同じ位置には配置できません。",
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
                position=item.get('position', '')
            )

    def _add_entry(self, image_path: str = "", position: str = ""):
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
            width=200
        )
        img_entry.pack(side="left", padx=2)
        if image_path:
            img_entry.insert(0, image_path)

        # 参照ボタン
        ctk.CTkButton(
            entry_frame,
            text="参照",
            width=50,
            command=lambda e=img_entry: self._browse_image(e)
        ).pack(side="left", padx=2)

        # 位置選択
        available_positions = self._get_available_positions(exclude_current=None)
        position_menu = ctk.CTkOptionMenu(
            entry_frame,
            values=available_positions if available_positions else ["（空きなし）"],
            width=120,
            command=lambda v: self._on_position_change()
        )
        if position and position in TEXT_POSITIONS:
            position_menu.set(position)
        elif available_positions:
            position_menu.set(available_positions[0])
        position_menu.pack(side="left", padx=5)

        # エントリ情報を保存
        entry_data = {
            'frame': entry_frame,
            'image_entry': img_entry,
            'position_menu': position_menu
        }
        self.entries.append(entry_data)

        self._update_ui_state()
        self._on_position_change()

    def _remove_last_entry(self):
        """最後のエントリを削除"""
        if not self.entries:
            return

        entry = self.entries.pop()
        entry['frame'].destroy()

        self._update_ui_state()
        self._on_position_change()

    def _get_available_positions(self, exclude_current: Optional[str] = None) -> List[str]:
        """利用可能な位置のリストを取得（POSITION_ORDER順）"""
        used_positions = set()
        for entry in self.entries:
            pos = entry['position_menu'].get()
            if pos and pos != "（空きなし）" and pos != exclude_current:
                used_positions.add(pos)

        available = [p for p in POSITION_ORDER if p not in used_positions]
        return available

    def _on_position_change(self):
        """位置選択が変更された時、他のドロップダウンを更新"""
        # 各エントリの現在の選択を取得
        current_selections = {}
        for i, entry in enumerate(self.entries):
            pos = entry['position_menu'].get()
            if pos and pos != "（空きなし）":
                current_selections[i] = pos

        # 各エントリのドロップダウンを更新
        for i, entry in enumerate(self.entries):
            current_pos = current_selections.get(i, "")

            # この項目以外で使われている位置を取得
            other_used = set()
            for j, pos in current_selections.items():
                if j != i:
                    other_used.add(pos)

            # 利用可能な位置（自分の現在選択 + 他で使われていない位置）
            available = [p for p in POSITION_ORDER if p not in other_used]

            # ドロップダウンの値を更新
            if available:
                entry['position_menu'].configure(values=available)
                # 現在の選択が有効なら維持、無効なら最初の利用可能な位置を選択
                if current_pos in available:
                    entry['position_menu'].set(current_pos)
                else:
                    entry['position_menu'].set(available[0])
            else:
                entry['position_menu'].configure(values=["（空きなし）"])
                entry['position_menu'].set("（空きなし）")

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
            position = entry['position_menu'].get()

            if image_path and position and position != "（空きなし）":
                result.append({
                    'image': image_path,
                    'position': position,
                    'position_en': TEXT_POSITIONS.get(position, position)
                })

        return result
