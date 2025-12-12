# -*- coding: utf-8 -*-
"""
4コマ漫画設定ウィンドウ
four_panel_manga.yaml準拠
"""

import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog
from typing import Callable, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.base_settings_window import BaseSettingsWindow


# セリフ位置
SPEECH_POSITIONS = {
    "左": "left",
    "右": "right"
}


class FourPanelWindow(BaseSettingsWindow):
    """4コマ漫画設定ウィンドウ"""

    def __init__(
        self,
        parent,
        callback: Optional[Callable] = None,
        initial_data: Optional[dict] = None
    ):
        self.initial_data = initial_data or {}
        # 各コマのUI要素を保持
        self.panel_widgets = []
        super().__init__(
            parent,
            title="4コマ漫画設定",
            width=900,
            height=900,
            callback=callback
        )

    def build_content(self):
        """コンテンツを構築"""
        # === 登場人物設定 ===
        char_frame = ctk.CTkFrame(self.content_frame)
        char_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        char_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            char_frame,
            text="登場人物",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=4, padx=10, pady=(10, 5), sticky="w")

        # キャラ1
        ctk.CTkLabel(char_frame, text="キャラ1名:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.char1_name_entry = ctk.CTkEntry(char_frame, placeholder_text="キャラクター名", width=150)
        self.char1_name_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(char_frame, text="説明:").grid(row=1, column=2, padx=10, pady=5, sticky="w")
        self.char1_desc_entry = ctk.CTkEntry(char_frame, placeholder_text="外見の説明", width=200)
        self.char1_desc_entry.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

        # キャラ1画像
        ctk.CTkLabel(char_frame, text="画像1:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        img1_frame = ctk.CTkFrame(char_frame, fg_color="transparent")
        img1_frame.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="ew")
        img1_frame.grid_columnconfigure(0, weight=1)

        self.char1_image_entry = ctk.CTkEntry(img1_frame, placeholder_text="キャラクター参照画像パス")
        self.char1_image_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkButton(
            img1_frame,
            text="参照",
            width=60,
            command=lambda: self._browse_image(self.char1_image_entry)
        ).grid(row=0, column=1)

        # キャラ2
        ctk.CTkLabel(char_frame, text="キャラ2名:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.char2_name_entry = ctk.CTkEntry(char_frame, placeholder_text="キャラクター名（任意）", width=150)
        self.char2_name_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(char_frame, text="説明:").grid(row=3, column=2, padx=10, pady=5, sticky="w")
        self.char2_desc_entry = ctk.CTkEntry(char_frame, placeholder_text="外見の説明", width=200)
        self.char2_desc_entry.grid(row=3, column=3, padx=5, pady=5, sticky="ew")

        # キャラ2画像
        ctk.CTkLabel(char_frame, text="画像2:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        img2_frame = ctk.CTkFrame(char_frame, fg_color="transparent")
        img2_frame.grid(row=4, column=1, columnspan=3, padx=5, pady=5, sticky="ew")
        img2_frame.grid_columnconfigure(0, weight=1)

        self.char2_image_entry = ctk.CTkEntry(img2_frame, placeholder_text="キャラクター参照画像パス（任意）")
        self.char2_image_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkButton(
            img2_frame,
            text="参照",
            width=60,
            command=lambda: self._browse_image(self.char2_image_entry)
        ).grid(row=0, column=1)

        # === 4コマ入力 ===
        panels_label_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        panels_label_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=(15, 0))

        ctk.CTkLabel(
            panels_label_frame,
            text="4コマ内容",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, padx=10, pady=5, sticky="w")

        ctk.CTkLabel(
            panels_label_frame,
            text="起承転結の流れで4コマを設定してください",
            font=("Arial", 11),
            text_color="gray"
        ).grid(row=0, column=1, padx=10, pady=5, sticky="w")

        # 4コマそれぞれのUI
        panel_labels = ["1コマ目（起）", "2コマ目（承）", "3コマ目（転）", "4コマ目（結）"]
        for i, label in enumerate(panel_labels):
            panel_widgets = self._create_panel_ui(i + 1, label, row=i + 2)
            self.panel_widgets.append(panel_widgets)

    def _create_panel_ui(self, panel_num: int, label: str, row: int) -> dict:
        """1コマ分のUI要素を作成"""
        frame = ctk.CTkFrame(self.content_frame)
        frame.grid(row=row, column=0, sticky="ew", padx=5, pady=5)
        frame.grid_columnconfigure(1, weight=1)

        # ヘッダー
        ctk.CTkLabel(
            frame,
            text=label,
            font=("Arial", 14, "bold")
        ).grid(row=0, column=0, columnspan=4, padx=10, pady=(10, 5), sticky="w")

        # シーン説明
        ctk.CTkLabel(frame, text="シーン:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        prompt_entry = ctk.CTkEntry(
            frame,
            placeholder_text="背景、キャラクターの配置、表情、アクションなど"
        )
        prompt_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        # セリフ1
        ctk.CTkLabel(frame, text="セリフ1:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        speech1_frame = ctk.CTkFrame(frame, fg_color="transparent")
        speech1_frame.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="ew")
        speech1_frame.grid_columnconfigure(1, weight=1)

        speech1_char_menu = ctk.CTkOptionMenu(
            speech1_frame,
            values=["キャラ1", "キャラ2", "（なし）"],
            width=100
        )
        speech1_char_menu.set("キャラ1")
        speech1_char_menu.grid(row=0, column=0, padx=(0, 5))

        speech1_entry = ctk.CTkEntry(speech1_frame, placeholder_text="セリフ内容")
        speech1_entry.grid(row=0, column=1, sticky="ew", padx=(0, 5))

        speech1_pos_menu = ctk.CTkOptionMenu(
            speech1_frame,
            values=list(SPEECH_POSITIONS.keys()),
            width=60
        )
        speech1_pos_menu.set("左")
        speech1_pos_menu.grid(row=0, column=2)

        # セリフ2（同時セリフ対応）
        ctk.CTkLabel(frame, text="セリフ2:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        speech2_frame = ctk.CTkFrame(frame, fg_color="transparent")
        speech2_frame.grid(row=3, column=1, columnspan=3, padx=5, pady=5, sticky="ew")
        speech2_frame.grid_columnconfigure(1, weight=1)

        speech2_char_menu = ctk.CTkOptionMenu(
            speech2_frame,
            values=["キャラ1", "キャラ2", "（なし）"],
            width=100
        )
        speech2_char_menu.set("（なし）")
        speech2_char_menu.grid(row=0, column=0, padx=(0, 5))

        speech2_entry = ctk.CTkEntry(speech2_frame, placeholder_text="セリフ内容（任意）")
        speech2_entry.grid(row=0, column=1, sticky="ew", padx=(0, 5))

        speech2_pos_menu = ctk.CTkOptionMenu(
            speech2_frame,
            values=list(SPEECH_POSITIONS.keys()),
            width=60
        )
        speech2_pos_menu.set("右")
        speech2_pos_menu.grid(row=0, column=2)

        # ナレーション
        ctk.CTkLabel(frame, text="ナレーション:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        narration_entry = ctk.CTkEntry(frame, placeholder_text="ナレーション（任意）")
        narration_entry.grid(row=4, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        return {
            'prompt': prompt_entry,
            'speech1_char': speech1_char_menu,
            'speech1_text': speech1_entry,
            'speech1_pos': speech1_pos_menu,
            'speech2_char': speech2_char_menu,
            'speech2_text': speech2_entry,
            'speech2_pos': speech2_pos_menu,
            'narration': narration_entry
        }

    def _browse_image(self, entry):
        """画像参照ダイアログ"""
        filename = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]
        )
        if filename:
            entry.delete(0, tk.END)
            entry.insert(0, filename)

    def collect_data(self) -> dict:
        """UIから設定データを収集"""
        # キャラクター情報
        characters = []
        char1_name = self.char1_name_entry.get().strip()
        if char1_name:
            characters.append({
                'name': char1_name,
                'description': self.char1_desc_entry.get().strip(),
                'image_path': self.char1_image_entry.get().strip()
            })

        char2_name = self.char2_name_entry.get().strip()
        if char2_name:
            characters.append({
                'name': char2_name,
                'description': self.char2_desc_entry.get().strip(),
                'image_path': self.char2_image_entry.get().strip()
            })

        # パネル情報
        panels = []
        for i, widgets in enumerate(self.panel_widgets):
            panel_data = {
                'panel_number': i + 1,
                'prompt': widgets['prompt'].get().strip(),
                'speeches': [],
                'narration': widgets['narration'].get().strip()
            }

            # セリフ1
            speech1_char = widgets['speech1_char'].get()
            speech1_text = widgets['speech1_text'].get().strip()
            if speech1_char != "（なし）" and speech1_text:
                # キャラ名に変換
                if speech1_char == "キャラ1" and char1_name:
                    speech1_char_name = char1_name
                elif speech1_char == "キャラ2" and char2_name:
                    speech1_char_name = char2_name
                else:
                    speech1_char_name = speech1_char

                panel_data['speeches'].append({
                    'character': speech1_char_name,
                    'content': speech1_text,
                    'position': SPEECH_POSITIONS[widgets['speech1_pos'].get()]
                })

            # セリフ2
            speech2_char = widgets['speech2_char'].get()
            speech2_text = widgets['speech2_text'].get().strip()
            if speech2_char != "（なし）" and speech2_text:
                if speech2_char == "キャラ1" and char1_name:
                    speech2_char_name = char1_name
                elif speech2_char == "キャラ2" and char2_name:
                    speech2_char_name = char2_name
                else:
                    speech2_char_name = speech2_char

                panel_data['speeches'].append({
                    'character': speech2_char_name,
                    'content': speech2_text,
                    'position': SPEECH_POSITIONS[widgets['speech2_pos'].get()]
                })

            panels.append(panel_data)

        return {
            'characters': characters,
            'panels': panels
        }

    def validate(self) -> tuple[bool, str]:
        """入力検証"""
        # キャラ1は必須
        if not self.char1_name_entry.get().strip():
            return False, "キャラクター1の名前を入力してください。"

        # 各コマのシーン説明は必須
        for i, widgets in enumerate(self.panel_widgets):
            if not widgets['prompt'].get().strip():
                return False, f"{i + 1}コマ目のシーン説明を入力してください。"

        return True, ""
