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
from constants import CHARACTER_POSES  # CHARACTER_FACING は正面固定のため不要


# ポーズプリセット（選択時に各設定を自動入力）
# ※description はGoogle Gemini謹製のプロンプト（character_pose.yaml準拠）
POSE_PRESETS = {
    "（プリセットなし）": None,
    "波動拳（かめはめ波）": {
        "category": "攻撃（魔法）",
        "pose": "攻撃",
        "description": "Thrusting both palms forward at waist level, knees slightly bent, focusing energy between hands",
        "dynamism": "誇張",
        "include_effects": False,  # 合成用にキャラだけ欲しい場合はFalse推奨
        "wind_effect": "前からの風",
        "camera_angle": "真横（格ゲー風）",
        "additional_prompt": "energy blast stance, power stance"
    },
    "スペシウム光線": {
        "category": "攻撃（魔法）",
        "pose": "攻撃",
        "description": "Crossing arms in a plus sign shape (+) in front of chest, right hand vertical, left hand horizontal",
        "dynamism": "標準",
        "include_effects": False,
        "wind_effect": "前からの風",
        "camera_angle": "ダイナミック（煽り）",
        "additional_prompt": "cross beam pose, heroic stance"
    },
    "ライダーキック": {
        "category": "攻撃（打撃）",
        "pose": "ジャンプ",
        "description": "Mid-air dynamic flying kick, one leg extended forward, body angled downward, floating in the air",
        "dynamism": "誇張",
        "include_effects": False,
        "wind_effect": "前からの風",
        "camera_angle": "ダイナミック（煽り）",
        "additional_prompt": "aerial attack, no shadow on ground to emphasize floating"
    },
    "指先ビーム": {
        "category": "攻撃（魔法）",
        "pose": "攻撃",
        "description": "Pointing index finger forward, arm fully extended, other fingers closed, cool and composed expression",
        "dynamism": "標準",
        "include_effects": False,
        "wind_effect": "なし",
        "camera_angle": "斜め前",
        "additional_prompt": "precision attack, finger gun pose"
    },
    "坐禅（瞑想）": {
        "category": "待機",
        "pose": "瞑想",
        "description": "Sitting cross-legged in lotus position, hands resting on knees, eyes closed, meditative posture",
        "dynamism": "控えめ",
        "include_effects": False,
        "wind_effect": "なし",
        "camera_angle": "正面",
        "additional_prompt": "meditation, zazen, static still pose"
    }
}

# ポーズ用追加定数
ACTION_CATEGORIES = {
    "攻撃（打撃）": "Melee Attack",
    "攻撃（魔法）": "Magic Attack",
    "攻撃（射撃）": "Ranged Attack",
    "防御": "Defensive",
    "移動": "Movement",
    "待機": "Idle/Ready"
}

DYNAMISM_LEVELS = {
    "控えめ": "Low (Subtle)",
    "標準": "Medium (Normal)",
    "誇張": "High (Exaggerated)"
}

WIND_EFFECTS = {
    "なし": "",
    "前からの風": "Strong Wind from Front",
    "後ろからの風": "Wind from Behind",
    "横からの風": "Side Wind"
}

CAMERA_ANGLES = {
    "真横（格ゲー風）": "Side View (Fighting Game)",
    "斜め前": "3/4 View",
    "正面": "Front View",
    "ダイナミック（煽り）": "Low Angle / Dynamic"
}

ZOOM_LEVELS = {
    "全身": "Full Body",
    "上半身": "Upper Body, waist up",
    "バストアップ": "Medium Close Up, chest and head visible, cutting off above the waist",
    "胸から上": "Chest up shot, head and chest visible",
    "胴体中ほどから上": "Shot from mid-torso up, framing from navel area to head",
    "みぞおちから上": "Shot from solar plexus up, framing from solar plexus to top of head",
    "顔アップ": "Close Up, face only, facial features detail"
}

EXPRESSIONS = {
    "無表情": "neutral expression, calm face, no emotion",
    "笑顔": "smiling, happy expression, cheerful face",
    "怒り": "angry expression, furious face, frowning",
    "泣き": "crying, tearful expression, sad face with tears",
    "恥じらい": "shy expression, blushing, embarrassed face"
}

# 使用する手足
LIMB_HAND = {
    "指定なし": "",
    "右手": "using right hand",
    "左手": "using left hand",
    "両手": "using both hands"
}

LIMB_FOOT = {
    "指定なし": "",
    "右足": "using right foot, right leg extended",
    "左足": "using left foot, left leg extended",
    "両足": "using both feet"
}


class PoseWindow(BaseSettingsWindow):
    """ポーズ三面図設定ウィンドウ（Step4）- 正面/横/背面の三面図を生成"""

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
            title="Step4: ポーズ三面図",
            width=750,
            height=750,
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
            text="よく使うポーズを選択すると設定が自動入力されます",
            font=("Arial", 11),
            text_color="gray"
        ).grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 5), sticky="w")

        self.preset_menu = ctk.CTkOptionMenu(
            preset_frame,
            values=list(POSE_PRESETS.keys()),
            width=200,
            command=self._on_preset_change
        )
        self.preset_menu.set("（プリセットなし）")
        self.preset_menu.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="w")

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

        # 三面図の説明
        ctk.CTkLabel(
            orient_frame,
            text="※ 正面・横・背面の三面図を生成します。Step5で任意の角度に変換できます。",
            font=("Arial", 11),
            text_color="gray"
        ).grid(row=1, column=0, columnspan=4, padx=10, pady=(0, 5), sticky="w")

        # 左右整合性の制限警告
        ctk.CTkLabel(
            orient_frame,
            text="⚠ 三面図の左右整合性（右手が全ビューで右手として描かれる等）は保証されません。",
            font=("Arial", 11),
            text_color="orange"
        ).grid(row=2, column=0, columnspan=4, padx=10, pady=(0, 5), sticky="w")

        # 目線
        ctk.CTkLabel(orient_frame, text="目線:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.eye_line_menu = ctk.CTkOptionMenu(
            orient_frame,
            values=["前を見る", "上を見る", "下を見る"],
            width=120
        )
        self.eye_line_menu.set("前を見る")
        self.eye_line_menu.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # 表情
        ctk.CTkLabel(orient_frame, text="表情:").grid(row=3, column=2, padx=10, pady=5, sticky="w")
        self.expression_menu = ctk.CTkOptionMenu(
            orient_frame,
            values=list(EXPRESSIONS.keys()),
            width=120
        )
        self.expression_menu.set("無表情")
        self.expression_menu.grid(row=3, column=3, padx=5, pady=5, sticky="w")

        # 表情補足（テキストボックス）
        ctk.CTkLabel(orient_frame, text="表情補足:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.expression_detail_entry = ctk.CTkEntry(
            orient_frame,
            placeholder_text="例：苦笑い、泣き笑い、ニヤリ",
            width=280
        )
        self.expression_detail_entry.grid(row=4, column=1, columnspan=3, padx=5, pady=5, sticky="w")

        # === アクション設定 ===
        action_frame = ctk.CTkFrame(self.content_frame)
        action_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        action_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            action_frame,
            text="アクション設定",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=4, padx=10, pady=(10, 5), sticky="w")

        # カテゴリ
        ctk.CTkLabel(action_frame, text="カテゴリ:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.category_menu = ctk.CTkOptionMenu(
            action_frame,
            values=list(ACTION_CATEGORIES.keys()),
            width=130
        )
        self.category_menu.set("攻撃（魔法）")
        self.category_menu.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # ポーズ
        ctk.CTkLabel(action_frame, text="ポーズ:").grid(row=1, column=2, padx=10, pady=5, sticky="w")
        self.pose_menu = ctk.CTkOptionMenu(
            action_frame,
            values=list(CHARACTER_POSES.keys()),
            width=130
        )
        self.pose_menu.set("攻撃")
        self.pose_menu.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        # 動作の詳細説明
        ctk.CTkLabel(action_frame, text="動作説明:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.action_desc_entry = ctk.CTkEntry(
            action_frame,
            placeholder_text="例：魔法の杖を前方に突き出す、詠唱ポーズ"
        )
        self.action_desc_entry.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        # 躍動感
        ctk.CTkLabel(action_frame, text="躍動感:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.dynamism_menu = ctk.CTkOptionMenu(
            action_frame,
            values=list(DYNAMISM_LEVELS.keys()),
            width=120
        )
        self.dynamism_menu.set("誇張")
        self.dynamism_menu.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # 使用する手
        ctk.CTkLabel(action_frame, text="使用する手:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.hand_menu = ctk.CTkOptionMenu(
            action_frame,
            values=list(LIMB_HAND.keys()),
            width=100
        )
        self.hand_menu.set("指定なし")
        self.hand_menu.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        # 手の詳細
        ctk.CTkLabel(action_frame, text="手の詳細:").grid(row=4, column=2, padx=10, pady=5, sticky="w")
        self.hand_detail_entry = ctk.CTkEntry(
            action_frame,
            placeholder_text="例：右手が上 / right hand on top",
            width=200
        )
        self.hand_detail_entry.grid(row=4, column=3, padx=5, pady=5, sticky="w")

        # 使用する足
        ctk.CTkLabel(action_frame, text="使用する足:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.foot_menu = ctk.CTkOptionMenu(
            action_frame,
            values=list(LIMB_FOOT.keys()),
            width=100
        )
        self.foot_menu.set("指定なし")
        self.foot_menu.grid(row=5, column=1, padx=5, pady=5, sticky="w")

        # 足の詳細
        ctk.CTkLabel(action_frame, text="足の詳細:").grid(row=5, column=2, padx=10, pady=5, sticky="w")
        self.foot_detail_entry = ctk.CTkEntry(
            action_frame,
            placeholder_text="例：左足が前 / left foot forward",
            width=200
        )
        self.foot_detail_entry.grid(row=5, column=3, padx=5, pady=5, sticky="w")

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

        # 背景透過
        self.transparent_bg_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            visual_frame,
            text="背景を透過にする（合成用）",
            variable=self.transparent_bg_var
        ).grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # 風の影響
        ctk.CTkLabel(visual_frame, text="風の影響:").grid(row=2, column=2, padx=10, pady=5, sticky="w")
        self.wind_menu = ctk.CTkOptionMenu(
            visual_frame,
            values=list(WIND_EFFECTS.keys()),
            width=130
        )
        self.wind_menu.set("前からの風")
        self.wind_menu.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        # カメラワーク（任意角度）はStep5（角度変更）で設定
        # このステップでは三面図（正面/横/背面）を生成

    def _browse_image(self):
        """画像参照ダイアログ"""
        filename = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]
        )
        if filename:
            self.image_entry.delete(0, tk.END)
            self.image_entry.insert(0, filename)

    def _on_preset_change(self, value):
        """プリセット選択時の処理"""
        preset = POSE_PRESETS.get(value)
        if preset is None:
            self.current_additional_prompt = ""
            return

        # 各設定を自動入力
        if "category" in preset:
            self.category_menu.set(preset["category"])
        if "pose" in preset:
            self.pose_menu.set(preset["pose"])
        if "description" in preset:
            self.action_desc_entry.delete(0, tk.END)
            self.action_desc_entry.insert(0, preset["description"])
        if "dynamism" in preset:
            self.dynamism_menu.set(preset["dynamism"])
        if "include_effects" in preset:
            self.include_effects_var.set(preset["include_effects"])
        if "wind_effect" in preset:
            self.wind_menu.set(preset["wind_effect"])
        # camera_angle は正面固定のためスキップ（Step5で角度変更）

        # 追加プロンプトを保持
        self.current_additional_prompt = preset.get("additional_prompt", "")

    def collect_data(self) -> dict:
        """UIから設定データを収集"""
        return {
            'preset': self.preset_menu.get(),
            'image_path': self.image_entry.get().strip(),
            'identity_preservation': self.preservation_slider.get(),
            'output_format': 'three_view',  # 三面図形式
            'eye_line': self.eye_line_menu.get(),
            'expression': self.expression_menu.get(),
            'expression_detail': self.expression_detail_entry.get().strip(),
            'action_category': self.category_menu.get(),
            'pose': self.pose_menu.get(),
            'action_description': self.action_desc_entry.get().strip(),
            'dynamism': self.dynamism_menu.get(),
            'hand': self.hand_menu.get(),
            'hand_detail': self.hand_detail_entry.get().strip(),
            'foot': self.foot_menu.get(),
            'foot_detail': self.foot_detail_entry.get().strip(),
            'include_effects': self.include_effects_var.get(),
            'transparent_bg': self.transparent_bg_var.get(),
            'wind_effect': self.wind_menu.get(),
            'additional_prompt': self.current_additional_prompt
        }

    def validate(self) -> tuple[bool, str]:
        """入力検証"""
        if not self.image_entry.get().strip():
            return False, "キャラクター画像を指定してください。"
        return True, ""
