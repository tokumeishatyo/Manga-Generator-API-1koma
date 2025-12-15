# -*- coding: utf-8 -*-
"""
背景生成設定ウィンドウ
背景のみの画像生成設定
"""

import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog
from typing import Callable, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.base_settings_window import BaseSettingsWindow


# 背景変形プリセット
TRANSFORM_PRESETS = {
    "アニメ調": "Convert to anime/illustration style, clean lines, vibrant colors",
    "水彩画風": "Transform to watercolor painting style, soft edges, artistic brush strokes",
    "夕暮れ": "Change to golden hour/sunset lighting, warm orange and pink tones",
    "夜景": "Transform to night scene, dark blue sky, artificial lighting",
    "冬景色": "Add winter elements, snow on surfaces, cold blue tones",
    "荒廃・廃墟": "Make it look abandoned and ruined, overgrown vegetation, decay",
    "ファンタジー": "Add fantasy elements, magical atmosphere, ethereal lighting",
    "サイバーパンク": "Cyberpunk style, neon lights, futuristic elements",
}


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
            width=650,
            height=750,
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

        # === 背景キャプチャ ===
        capture_frame = ctk.CTkFrame(self.content_frame)
        capture_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        capture_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            capture_frame,
            text="背景キャプチャ",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkLabel(
            capture_frame,
            text="参考画像から背景を生成（上記のテキスト記述より優先）",
            font=("Arial", 11),
            text_color="gray"
        ).grid(row=1, column=0, padx=10, pady=(0, 5), sticky="w")

        # キャプチャ有効チェックボックス
        self.bg_capture_var = tk.BooleanVar(value=False)
        self.bg_capture_checkbox = ctk.CTkCheckBox(
            capture_frame,
            text="参考画像から背景を生成",
            variable=self.bg_capture_var,
            command=self._on_bg_capture_toggle
        )
        self.bg_capture_checkbox.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        # 参考画像入力フレーム
        self.bg_ref_frame = ctk.CTkFrame(capture_frame, fg_color="transparent")
        self.bg_ref_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        self.bg_ref_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.bg_ref_frame, text="参考画像:").grid(row=0, column=0, padx=(0, 5), sticky="w")
        self.bg_ref_entry = ctk.CTkEntry(
            self.bg_ref_frame,
            placeholder_text="背景として取り込みたい画像のパス",
            state="disabled"
        )
        self.bg_ref_entry.grid(row=0, column=1, sticky="ew", padx=(0, 5))

        self.bg_ref_browse_btn = ctk.CTkButton(
            self.bg_ref_frame,
            text="参照",
            width=60,
            command=self._browse_bg_ref,
            state="disabled"
        )
        self.bg_ref_browse_btn.grid(row=0, column=2)

        # 著作権注意書き
        ctk.CTkLabel(
            self.bg_ref_frame,
            text="※ 参考画像の著作権はユーザー責任です",
            font=("Arial", 10),
            text_color="orange"
        ).grid(row=1, column=0, columnspan=3, pady=(2, 0), sticky="w")

        # 人物除去チェックボックス
        self.remove_people_var = tk.BooleanVar(value=True)
        self.remove_people_checkbox = ctk.CTkCheckBox(
            capture_frame,
            text="人物を自動的に除去（推奨）",
            variable=self.remove_people_var,
            state="disabled"
        )
        self.remove_people_checkbox.grid(row=4, column=0, padx=10, pady=5, sticky="w")

        # 変形指示
        ctk.CTkLabel(
            capture_frame,
            text="変形指示（オプション）:",
            font=("Arial", 12)
        ).grid(row=5, column=0, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkLabel(
            capture_frame,
            text="空欄の場合はアニメ調に変換されます",
            font=("Arial", 10),
            text_color="gray"
        ).grid(row=6, column=0, padx=10, pady=(0, 5), sticky="w")

        self.transform_entry = ctk.CTkEntry(
            capture_frame,
            placeholder_text="例：夕暮れ時の雰囲気に変える、雪景色にする",
            state="disabled"
        )
        self.transform_entry.grid(row=7, column=0, padx=10, pady=(0, 5), sticky="ew")

        # 変形プリセット
        ctk.CTkLabel(
            capture_frame,
            text="変形プリセット:",
            font=("Arial", 12)
        ).grid(row=8, column=0, padx=10, pady=(5, 5), sticky="w")

        transform_preset_frame = ctk.CTkFrame(capture_frame, fg_color="transparent")
        transform_preset_frame.grid(row=9, column=0, padx=10, pady=(0, 10), sticky="ew")

        # ボタンを保持するリストを初期化
        self.transform_preset_buttons = []
        preset_names = list(TRANSFORM_PRESETS.keys())
        for i, name in enumerate(preset_names):
            btn = ctk.CTkButton(
                transform_preset_frame,
                text=name,
                width=100,
                height=28,
                command=lambda n=name: self._apply_transform_preset(n),
                state="disabled"
            )
            btn.grid(row=i // 4, column=i % 4, padx=2, pady=2)
            self.transform_preset_buttons.append(btn)

    def _apply_preset(self, description: str):
        """プリセットを適用"""
        self.description_textbox.delete("1.0", tk.END)
        self.description_textbox.insert("1.0", description)

    def _browse_bg_ref(self):
        """背景参考画像参照ダイアログ"""
        filename = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]
        )
        if filename:
            self.bg_ref_entry.delete(0, tk.END)
            self.bg_ref_entry.insert(0, filename)

    def _on_bg_capture_toggle(self):
        """背景キャプチャのチェックボックス切り替え時の処理"""
        if self.bg_capture_var.get():
            # キャプチャモード有効
            self.bg_ref_entry.configure(state="normal")
            self.bg_ref_browse_btn.configure(state="normal")
            self.remove_people_checkbox.configure(state="normal")
            self.transform_entry.configure(state="normal")
            for btn in self.transform_preset_buttons:
                btn.configure(state="normal")
        else:
            # キャプチャモード無効
            self.bg_ref_entry.configure(state="disabled")
            self.bg_ref_browse_btn.configure(state="disabled")
            self.remove_people_checkbox.configure(state="disabled")
            self.transform_entry.configure(state="disabled")
            for btn in self.transform_preset_buttons:
                btn.configure(state="disabled")

    def _apply_transform_preset(self, preset_name: str):
        """変形プリセットを適用"""
        self.transform_entry.delete(0, tk.END)
        self.transform_entry.insert(0, preset_name)

    def collect_data(self) -> dict:
        """UIから設定データを収集"""
        # 変形プリセットが選択されている場合、その英語説明を取得
        transform_text = self.transform_entry.get().strip()
        transform_instruction = ""
        if transform_text:
            # プリセット名の場合は英語説明に変換
            if transform_text in TRANSFORM_PRESETS:
                transform_instruction = TRANSFORM_PRESETS[transform_text]
            else:
                # カスタム入力の場合はそのまま使用
                transform_instruction = transform_text

        return {
            'description': self.description_textbox.get("1.0", tk.END).strip(),
            # 背景キャプチャ設定
            'bg_capture_enabled': self.bg_capture_var.get(),
            'bg_reference_image': self.bg_ref_entry.get().strip() if self.bg_capture_var.get() else '',
            'remove_people': self.remove_people_var.get() if self.bg_capture_var.get() else True,
            'transform_instruction': transform_instruction if self.bg_capture_var.get() else ''
        }

    def validate(self) -> tuple[bool, str]:
        """入力検証"""
        # キャプチャモードの場合
        if self.bg_capture_var.get():
            if not self.bg_ref_entry.get().strip():
                return False, "背景キャプチャを使用する場合は、参考画像を指定してください。"
            return True, ""

        # テキスト記述モードの場合
        desc = self.description_textbox.get("1.0", tk.END).strip()
        if not desc:
            return False, "背景の説明を入力してください。"
        return True, ""
