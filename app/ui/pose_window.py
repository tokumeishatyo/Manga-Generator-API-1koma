# -*- coding: utf-8 -*-
"""
ポーズ付きキャラ設定ウィンドウ
character_pose.yaml準拠
"""

import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog
from typing import Callable, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.base_settings_window import BaseSettingsWindow


# ポーズプリセット（選択時に動作説明を自動入力）
POSE_PRESETS = {
    "（プリセットなし）": None,
    "波動拳（かめはめ波）": {
        "description": "Thrusting both palms forward at waist level, knees slightly bent, focusing energy between hands",
        "include_effects": False,
        "wind_effect": "前からの風",
        "additional_prompt": "energy blast stance, power stance"
    },
    "スペシウム光線": {
        "description": "Crossing arms in a plus sign shape (+) in front of chest, right hand vertical, left hand horizontal",
        "include_effects": False,
        "wind_effect": "前からの風",
        "additional_prompt": "cross beam pose, heroic stance"
    },
    "ライダーキック": {
        "description": "Mid-air dynamic flying kick, one leg extended forward, body angled downward, floating in the air",
        "include_effects": False,
        "wind_effect": "前からの風",
        "additional_prompt": "aerial attack, no shadow on ground to emphasize floating"
    },
    "指先ビーム": {
        "description": "Pointing index finger forward, arm fully extended, other fingers closed, cool and composed expression",
        "include_effects": False,
        "wind_effect": "なし",
        "additional_prompt": "precision attack, finger gun pose"
    },
    "坐禅（瞑想）": {
        "description": "Sitting cross-legged in lotus position, hands resting on knees, eyes closed, meditative posture",
        "include_effects": False,
        "wind_effect": "なし",
        "additional_prompt": "meditation, zazen, static still pose"
    }
}

WIND_EFFECTS = {
    "なし": "",
    "前からの風": "Strong Wind from Front",
    "後ろからの風": "Wind from Behind",
    "横からの風": "Side Wind"
}

EXPRESSIONS = {
    "無表情": "neutral expression, calm face, no emotion",
    "笑顔": "smiling, happy expression, cheerful face",
    "怒り": "angry expression, furious face, frowning",
    "泣き": "crying, tearful expression, sad face with tears",
    "恥じらい": "shy expression, blushing, embarrassed face"
}


class PoseWindow(BaseSettingsWindow):
    """ポーズ設定ウィンドウ（Step4）- ポーズ付きキャラクター画像を1枚生成"""

    def __init__(
        self,
        parent,
        callback: Optional[Callable] = None,
        initial_data: Optional[dict] = None,
        outfit_sheet_path: Optional[str] = None  # Step3の出力画像パス
    ):
        """
        Args:
            parent: 親ウィンドウ
            callback: 設定完了時のコールバック
            initial_data: 初期データ（編集時）
            outfit_sheet_path: Step3で生成した衣装着用三面図のパス
        """
        self.initial_data = initial_data or {}
        self.outfit_sheet_path = outfit_sheet_path
        super().__init__(
            parent,
            title="Step4: ポーズ",
            width=700,
            height=550,
            callback=callback
        )

    def build_content(self):
        """コンテンツを構築"""
        # === プリセット選択 ===
        preset_frame = ctk.CTkFrame(self.content_frame)
        preset_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(
            preset_frame,
            text="ポーズプリセット",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkLabel(
            preset_frame,
            text="よく使うポーズを選択すると動作説明が自動入力されます",
            font=("Arial", 11),
            text_color="gray"
        ).grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 5), sticky="w")

        # プリセットとキャプチャの選択行
        preset_row_frame = ctk.CTkFrame(preset_frame, fg_color="transparent")
        preset_row_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=(0, 5), sticky="w")

        self.preset_menu = ctk.CTkOptionMenu(
            preset_row_frame,
            values=list(POSE_PRESETS.keys()),
            width=200,
            command=self._on_preset_change
        )
        self.preset_menu.set("（プリセットなし）")
        self.preset_menu.grid(row=0, column=0, padx=(0, 20), sticky="w")

        # ポーズキャプチャチェックボックス
        self.pose_capture_var = tk.BooleanVar(value=False)
        self.pose_capture_checkbox = ctk.CTkCheckBox(
            preset_row_frame,
            text="参考画像のポーズをキャプチャ",
            variable=self.pose_capture_var,
            command=self._on_pose_capture_toggle
        )
        self.pose_capture_checkbox.grid(row=0, column=1, sticky="w")

        # ポーズ参考画像パス入力
        capture_frame = ctk.CTkFrame(preset_frame, fg_color="transparent")
        capture_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")
        capture_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(capture_frame, text="ポーズ参考画像:").grid(row=0, column=0, padx=(0, 5), sticky="w")
        self.pose_ref_entry = ctk.CTkEntry(
            capture_frame,
            placeholder_text="ポーズを取り込みたい画像のパス",
            state="disabled"
        )
        self.pose_ref_entry.grid(row=0, column=1, sticky="ew", padx=(0, 5))

        self.pose_ref_browse_btn = ctk.CTkButton(
            capture_frame,
            text="参照",
            width=60,
            command=self._browse_pose_ref,
            state="disabled"
        )
        self.pose_ref_browse_btn.grid(row=0, column=2)

        # 著作権注意書き
        self.pose_ref_warning = ctk.CTkLabel(
            capture_frame,
            text="※ 参考画像の著作権はユーザー責任です",
            font=("Arial", 10),
            text_color="orange"
        )
        self.pose_ref_warning.grid(row=1, column=0, columnspan=3, padx=0, pady=(2, 0), sticky="w")

        # プリセットの追加プロンプト保持用
        self.current_additional_prompt = ""

        # === 入力画像設定 ===
        input_frame = ctk.CTkFrame(self.content_frame)
        input_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        input_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            input_frame,
            text="入力画像（衣装着用三面図）",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkLabel(
            input_frame,
            text="Step3で生成した衣装着用三面図、または任意のキャラ画像を指定",
            font=("Arial", 11),
            text_color="gray"
        ).grid(row=1, column=0, columnspan=3, padx=10, pady=(0, 5), sticky="w")

        # 画像パス
        ctk.CTkLabel(input_frame, text="画像:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        img_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        img_frame.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        img_frame.grid_columnconfigure(0, weight=1)

        self.image_entry = ctk.CTkEntry(img_frame, placeholder_text="Step3の出力画像パス")
        self.image_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        # Step3の出力パスがあれば自動入力
        if self.outfit_sheet_path:
            self.image_entry.insert(0, self.outfit_sheet_path)

        ctk.CTkButton(
            img_frame,
            text="参照",
            width=60,
            command=self._browse_image
        ).grid(row=0, column=1)

        # 同一性保持
        ctk.CTkLabel(input_frame, text="同一性保持:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.preservation_slider = ctk.CTkSlider(input_frame, from_=0.5, to=1.0, number_of_steps=10)
        self.preservation_slider.set(0.85)
        self.preservation_slider.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        # === 向き・表情設定 ===
        orient_frame = ctk.CTkFrame(self.content_frame)
        orient_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(
            orient_frame,
            text="向き・表情",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=4, padx=10, pady=(10, 5), sticky="w")

        # 目線
        ctk.CTkLabel(orient_frame, text="目線:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.eye_line_menu = ctk.CTkOptionMenu(
            orient_frame,
            values=["前を見る", "上を見る", "下を見る"],
            width=120
        )
        self.eye_line_menu.set("前を見る")
        self.eye_line_menu.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # 表情
        ctk.CTkLabel(orient_frame, text="表情:").grid(row=1, column=2, padx=10, pady=5, sticky="w")
        self.expression_menu = ctk.CTkOptionMenu(
            orient_frame,
            values=list(EXPRESSIONS.keys()),
            width=120
        )
        self.expression_menu.set("無表情")
        self.expression_menu.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        # 表情補足（テキストボックス）
        ctk.CTkLabel(orient_frame, text="表情補足:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.expression_detail_entry = ctk.CTkEntry(
            orient_frame,
            placeholder_text="例：苦笑い、泣き笑い、ニヤリ",
            width=280
        )
        self.expression_detail_entry.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="w")

        # === 動作説明 ===
        action_frame = ctk.CTkFrame(self.content_frame)
        action_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        action_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            action_frame,
            text="動作説明",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkLabel(
            action_frame,
            text="ポーズや動作を自由に記述してください（日本語/英語どちらでも可）",
            font=("Arial", 11),
            text_color="gray"
        ).grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 5), sticky="w")

        self.action_desc_entry = ctk.CTkEntry(
            action_frame,
            placeholder_text="例：椅子に座ってコーヒーを飲む、手を振る、考え込むポーズ"
        )
        self.action_desc_entry.grid(row=2, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")

        # === ビジュアル効果 ===
        visual_frame = ctk.CTkFrame(self.content_frame)
        visual_frame.grid(row=4, column=0, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(
            visual_frame,
            text="ビジュアル効果",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=4, padx=10, pady=(10, 5), sticky="w")

        # エフェクト描画
        self.include_effects_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            visual_frame,
            text="エフェクトを描画する（合成用はOFF推奨）",
            variable=self.include_effects_var
        ).grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # 背景透過（デフォルトON）
        self.transparent_bg_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            visual_frame,
            text="背景を透過にする（合成用）",
            variable=self.transparent_bg_var
        ).grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # 風の影響
        ctk.CTkLabel(visual_frame, text="風の影響:").grid(row=1, column=2, padx=10, pady=5, sticky="w")
        self.wind_menu = ctk.CTkOptionMenu(
            visual_frame,
            values=list(WIND_EFFECTS.keys()),
            width=130
        )
        self.wind_menu.set("なし")
        self.wind_menu.grid(row=1, column=3, padx=5, pady=5, sticky="w")

    def _browse_image(self):
        """画像参照ダイアログ"""
        filename = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]
        )
        if filename:
            self.image_entry.delete(0, tk.END)
            self.image_entry.insert(0, filename)

    def _browse_pose_ref(self):
        """ポーズ参考画像参照ダイアログ"""
        filename = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]
        )
        if filename:
            self.pose_ref_entry.delete(0, tk.END)
            self.pose_ref_entry.insert(0, filename)

    def _on_pose_capture_toggle(self):
        """ポーズキャプチャのチェックボックス切り替え時の処理"""
        if self.pose_capture_var.get():
            # キャプチャモード: プリセット無効、参考画像入力有効
            self.preset_menu.configure(state="disabled")
            self.pose_ref_entry.configure(state="normal")
            self.pose_ref_browse_btn.configure(state="normal")
            # 動作説明をクリア（キャプチャモードでは参考画像がポーズを決める）
            self.action_desc_entry.delete(0, tk.END)
            self.current_additional_prompt = ""
        else:
            # プリセットモード: プリセット有効、参考画像入力無効
            self.preset_menu.configure(state="normal")
            self.pose_ref_entry.configure(state="disabled")
            self.pose_ref_browse_btn.configure(state="disabled")

    def _on_preset_change(self, value):
        """プリセット選択時の処理"""
        preset = POSE_PRESETS.get(value)
        if preset is None:
            self.current_additional_prompt = ""
            return

        # 動作説明を自動入力
        if "description" in preset:
            self.action_desc_entry.delete(0, tk.END)
            self.action_desc_entry.insert(0, preset["description"])
        if "include_effects" in preset:
            self.include_effects_var.set(preset["include_effects"])
        if "wind_effect" in preset:
            self.wind_menu.set(preset["wind_effect"])

        # 追加プロンプトを保持
        self.current_additional_prompt = preset.get("additional_prompt", "")

    def collect_data(self) -> dict:
        """UIから設定データを収集"""
        return {
            'preset': self.preset_menu.get(),
            'image_path': self.image_entry.get().strip(),
            'identity_preservation': self.preservation_slider.get(),
            'output_format': 'single',  # 1枚出力
            'eye_line': self.eye_line_menu.get(),
            'expression': self.expression_menu.get(),
            'expression_detail': self.expression_detail_entry.get().strip(),
            'action_description': self.action_desc_entry.get().strip(),
            'include_effects': self.include_effects_var.get(),
            'transparent_bg': self.transparent_bg_var.get(),
            'wind_effect': self.wind_menu.get(),
            'additional_prompt': self.current_additional_prompt,
            # ポーズキャプチャ設定
            'pose_capture_enabled': self.pose_capture_var.get(),
            'pose_reference_image': self.pose_ref_entry.get().strip() if self.pose_capture_var.get() else ''
        }

    def validate(self) -> tuple[bool, str]:
        """入力検証"""
        if not self.image_entry.get().strip():
            return False, "キャラクター画像を指定してください。"
        # ポーズキャプチャが有効な場合、参考画像が必須
        if self.pose_capture_var.get() and not self.pose_ref_entry.get().strip():
            return False, "ポーズキャプチャを使用する場合は、ポーズ参考画像を指定してください。"
        return True, ""
