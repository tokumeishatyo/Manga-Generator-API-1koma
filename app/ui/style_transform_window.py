# -*- coding: utf-8 -*-
"""
スタイル変換ウィンドウ
リアルキャラ画像をちびキャラ化・ドットキャラ化する
- 任意の段階（素体/衣装/ポーズ）の画像を変換可能
"""

import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog
from typing import Callable, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.base_settings_window import BaseSettingsWindow

# スタイル変換タイプ
TRANSFORM_STYLES = {
    "ちびキャラ化": "chibi",
    "ドットキャラ化": "pixel"
}

# ちびキャラスタイル詳細
CHIBI_STYLES = {
    "スタンダード（2頭身）": {
        "prompt": "2-head-tall chibi style, super deformed, cute big head, small body",
        "head_ratio": "2:1"
    },
    "デフォルメ（1.5頭身）": {
        "prompt": "1.5-head-tall extreme chibi, very large head, tiny body, maximum cute",
        "head_ratio": "1.5:1"
    },
    "ミニキャラ（3頭身）": {
        "prompt": "3-head-tall mini character style, moderately deformed, cute proportions",
        "head_ratio": "3:1"
    },
    "ぷちキャラ（まるっこい）": {
        "prompt": "puchi chara style, round soft shapes, blob-like cute, simplified features",
        "head_ratio": "2:1"
    }
}

# ドットキャラスタイル詳細
PIXEL_STYLES = {
    "8bit風（ファミコン）": {
        "prompt": "8-bit pixel art style, NES/Famicom era, limited color palette, chunky pixels",
        "resolution": "low",
        "colors": "16"
    },
    "16bit風（スーファミ）": {
        "prompt": "16-bit pixel art style, SNES/Super Famicom era, vibrant colors, detailed sprites",
        "resolution": "medium",
        "colors": "256"
    },
    "32bit風（PS1/SS）": {
        "prompt": "32-bit pixel art style, PlayStation/Saturn era, high detail sprites, rich colors",
        "resolution": "high",
        "colors": "full"
    },
    "GBA風": {
        "prompt": "GBA pixel art style, Game Boy Advance era, portable game aesthetic",
        "resolution": "medium",
        "colors": "256"
    },
    "モダンピクセル": {
        "prompt": "modern pixel art style, indie game aesthetic, clean sharp pixels, contemporary",
        "resolution": "high",
        "colors": "full"
    }
}

# スプライトサイズ
SPRITE_SIZES = {
    "16x16": "16x16 pixel sprite, very small, icon-sized",
    "32x32": "32x32 pixel sprite, small game sprite size",
    "64x64": "64x64 pixel sprite, medium detailed sprite",
    "128x128": "128x128 pixel sprite, large detailed sprite",
    "256x256": "256x256 pixel sprite, high detail sprite art"
}


class StyleTransformWindow(BaseSettingsWindow):
    """スタイル変換設定ウィンドウ"""

    def __init__(
        self,
        parent,
        callback: Optional[Callable] = None,
        initial_data: Optional[dict] = None,
        source_image_path: Optional[str] = None
    ):
        """
        Args:
            parent: 親ウィンドウ
            callback: 設定完了時のコールバック
            initial_data: 初期データ（編集時）
            source_image_path: 変換元画像のパス
        """
        self.initial_data = initial_data or {}
        self.source_image_path = source_image_path
        super().__init__(
            parent,
            title="スタイル変換（ちびキャラ化・ドットキャラ化）",
            width=700,
            height=650,
            callback=callback
        )

    def build_content(self):
        """コンテンツを構築"""
        # === 入力画像 ===
        input_frame = ctk.CTkFrame(self.content_frame)
        input_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        input_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            input_frame,
            text="入力画像（変換元）",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkLabel(input_frame, text="画像:").grid(row=1, column=0, padx=10, pady=5, sticky="w")

        img_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        img_frame.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        img_frame.grid_columnconfigure(0, weight=1)

        self.source_image_entry = ctk.CTkEntry(
            img_frame,
            placeholder_text="変換したいキャラクター画像を選択"
        )
        self.source_image_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        if self.source_image_path:
            self.source_image_entry.insert(0, self.source_image_path)

        ctk.CTkButton(
            img_frame,
            text="参照",
            width=60,
            command=self._browse_source_image
        ).grid(row=0, column=1)

        # 説明
        ctk.CTkLabel(
            input_frame,
            text="※ 素体/衣装/ポーズなど、どの段階の画像でも変換可能",
            font=("Arial", 10),
            text_color="gray"
        ).grid(row=2, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="w")

        # === 変換タイプ選択 ===
        type_frame = ctk.CTkFrame(self.content_frame)
        type_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(
            type_frame,
            text="変換タイプ",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        self.transform_type_var = tk.StringVar(value="ちびキャラ化")

        ctk.CTkRadioButton(
            type_frame,
            text="ちびキャラ化",
            variable=self.transform_type_var,
            value="ちびキャラ化",
            command=self._on_type_change
        ).grid(row=1, column=0, padx=20, pady=5, sticky="w")

        ctk.CTkRadioButton(
            type_frame,
            text="ドットキャラ化",
            variable=self.transform_type_var,
            value="ドットキャラ化",
            command=self._on_type_change
        ).grid(row=1, column=1, padx=20, pady=5, sticky="w")

        # === ちびキャラ設定フレーム ===
        self.chibi_frame = ctk.CTkFrame(self.content_frame)
        self.chibi_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.chibi_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            self.chibi_frame,
            text="ちびキャラ設定",
            font=("Arial", 14, "bold")
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkLabel(self.chibi_frame, text="スタイル:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.chibi_style_menu = ctk.CTkOptionMenu(
            self.chibi_frame,
            values=list(CHIBI_STYLES.keys()),
            width=250
        )
        self.chibi_style_menu.set("スタンダード（2頭身）")
        self.chibi_style_menu.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # ちびキャラオプション
        self.chibi_preserve_outfit_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            self.chibi_frame,
            text="衣装を保持",
            variable=self.chibi_preserve_outfit_var
        ).grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        self.chibi_preserve_pose_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            self.chibi_frame,
            text="ポーズを保持",
            variable=self.chibi_preserve_pose_var
        ).grid(row=3, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="w")

        # === ドットキャラ設定フレーム ===
        self.pixel_frame = ctk.CTkFrame(self.content_frame)
        self.pixel_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        self.pixel_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            self.pixel_frame,
            text="ドットキャラ設定",
            font=("Arial", 14, "bold")
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkLabel(self.pixel_frame, text="スタイル:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.pixel_style_menu = ctk.CTkOptionMenu(
            self.pixel_frame,
            values=list(PIXEL_STYLES.keys()),
            width=250
        )
        self.pixel_style_menu.set("16bit風（スーファミ）")
        self.pixel_style_menu.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(self.pixel_frame, text="サイズ:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.sprite_size_menu = ctk.CTkOptionMenu(
            self.pixel_frame,
            values=list(SPRITE_SIZES.keys()),
            width=250
        )
        self.sprite_size_menu.set("64x64")
        self.sprite_size_menu.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # ドットキャラオプション
        self.pixel_preserve_colors_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            self.pixel_frame,
            text="元のカラーパレットを参照",
            variable=self.pixel_preserve_colors_var
        ).grid(row=3, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="w")

        # 初期状態でドットキャラフレームを無効化
        self._set_frame_state(self.pixel_frame, "disabled")

        # === 出力設定（全タイプ共通） ===
        output_frame = ctk.CTkFrame(self.content_frame)
        output_frame.grid(row=4, column=0, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(
            output_frame,
            text="出力設定",
            font=("Arial", 14, "bold")
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        # 背景透過（デフォルトON）
        self.transparent_bg_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            output_frame,
            text="背景透過（合成用素材として出力）",
            variable=self.transparent_bg_var
        ).grid(row=1, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="w")

        # === 追加説明 ===
        detail_frame = ctk.CTkFrame(self.content_frame)
        detail_frame.grid(row=5, column=0, sticky="ew", padx=5, pady=5)
        detail_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            detail_frame,
            text="追加説明",
            font=("Arial", 14, "bold")
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkLabel(detail_frame, text="詳細:").grid(row=1, column=0, padx=10, pady=5, sticky="nw")
        self.description_textbox = ctk.CTkTextbox(detail_frame, height=60, wrap="word")
        self.description_textbox.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.description_textbox.insert("1.0", "（任意）変換時の追加指示")

        # === 説明 ===
        info_frame = ctk.CTkFrame(self.content_frame)
        info_frame.grid(row=6, column=0, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(
            info_frame,
            text="変換について",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        info_text = """• キャラクターの顔・衣装・ポーズは可能な限り保持されます
• ちびキャラ化: 頭身が低くなり、かわいいデフォルメになります
• ドットキャラ化: ピクセルアート風に変換されます
• 背景透過ONで合成用素材として出力できます"""

        ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=("Arial", 11),
            justify="left"
        ).pack(anchor="w", padx=15, pady=(0, 10))

    def _browse_source_image(self):
        """変換元画像参照ダイアログ"""
        filename = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]
        )
        if filename:
            self.source_image_entry.delete(0, tk.END)
            self.source_image_entry.insert(0, filename)

    def _on_type_change(self):
        """変換タイプ変更時"""
        transform_type = self.transform_type_var.get()
        if transform_type == "ちびキャラ化":
            self._set_frame_state(self.chibi_frame, "normal")
            self._set_frame_state(self.pixel_frame, "disabled")
        else:
            self._set_frame_state(self.chibi_frame, "disabled")
            self._set_frame_state(self.pixel_frame, "normal")

    def _set_frame_state(self, frame, state):
        """フレーム内のウィジェットの状態を変更"""
        for child in frame.winfo_children():
            try:
                if isinstance(child, (ctk.CTkEntry, ctk.CTkOptionMenu, ctk.CTkTextbox,
                                      ctk.CTkButton, ctk.CTkCheckBox)):
                    child.configure(state=state)
                elif isinstance(child, ctk.CTkFrame):
                    self._set_frame_state(child, state)
            except Exception:
                pass

    def collect_data(self) -> dict:
        """UIから設定データを収集"""
        desc = self.description_textbox.get("1.0", tk.END).strip()
        if desc == "（任意）変換時の追加指示":
            desc = ""

        transform_type = self.transform_type_var.get()

        data = {
            'step_type': 'style_transform',
            'source_image_path': self.source_image_entry.get().strip(),
            'transform_type': transform_type,
            'transform_type_en': TRANSFORM_STYLES.get(transform_type, 'chibi'),
            'additional_description': desc,
            'transparent_bg': self.transparent_bg_var.get()  # 全タイプ共通
        }

        if transform_type == "ちびキャラ化":
            chibi_style = self.chibi_style_menu.get()
            data['chibi_settings'] = {
                'style': chibi_style,
                'style_info': CHIBI_STYLES.get(chibi_style, {}),
                'preserve_outfit': self.chibi_preserve_outfit_var.get(),
                'preserve_pose': self.chibi_preserve_pose_var.get()
            }
        else:
            pixel_style = self.pixel_style_menu.get()
            sprite_size = self.sprite_size_menu.get()
            data['pixel_settings'] = {
                'style': pixel_style,
                'style_info': PIXEL_STYLES.get(pixel_style, {}),
                'sprite_size': sprite_size,
                'sprite_size_prompt': SPRITE_SIZES.get(sprite_size, ''),
                'preserve_colors': self.pixel_preserve_colors_var.get()
            }

        return data

    def validate(self) -> tuple[bool, str]:
        """入力検証"""
        source_path = self.source_image_entry.get().strip()
        if not source_path:
            return False, "変換元の画像を選択してください。"

        return True, ""
