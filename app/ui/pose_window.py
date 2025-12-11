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
from constants import CHARACTER_FACING, CHARACTER_POSES


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
    "上半身": "Upper Body",
    "バストアップ": "Bust Shot"
}


class PoseWindow(BaseSettingsWindow):
    """ポーズ付きキャラ設定ウィンドウ"""

    def __init__(
        self,
        parent,
        callback: Optional[Callable] = None,
        initial_data: Optional[dict] = None
    ):
        self.initial_data = initial_data or {}
        super().__init__(
            parent,
            title="ポーズ付きキャラ設定",
            width=700,
            height=600,
            callback=callback
        )

    def build_content(self):
        """コンテンツを構築"""
        # === 入力画像設定 ===
        input_frame = ctk.CTkFrame(self.content_frame)
        input_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        input_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            input_frame,
            text="入力画像（立ち絵）",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkLabel(
            input_frame,
            text="三面図やベースデザインから作成したキャラ画像を指定",
            font=("Arial", 11),
            text_color="gray"
        ).grid(row=1, column=0, columnspan=3, padx=10, pady=(0, 5), sticky="w")

        # 画像パス
        ctk.CTkLabel(input_frame, text="画像:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        img_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        img_frame.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        img_frame.grid_columnconfigure(0, weight=1)

        self.image_entry = ctk.CTkEntry(img_frame, placeholder_text="キャラクター画像パス")
        self.image_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
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

        # === 向き・配置設定 ===
        orient_frame = ctk.CTkFrame(self.content_frame)
        orient_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(
            orient_frame,
            text="向き・配置",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=4, padx=10, pady=(10, 5), sticky="w")

        # 向き
        ctk.CTkLabel(orient_frame, text="向き:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.facing_menu = ctk.CTkOptionMenu(
            orient_frame,
            values=list(CHARACTER_FACING.keys()),
            width=120
        )
        self.facing_menu.set("→右向き")
        self.facing_menu.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # 目線
        ctk.CTkLabel(orient_frame, text="目線:").grid(row=1, column=2, padx=10, pady=5, sticky="w")
        self.eye_line_menu = ctk.CTkOptionMenu(
            orient_frame,
            values=["相手を見る", "前を見る", "上を見る", "下を見る"],
            width=120
        )
        self.eye_line_menu.set("相手を見る")
        self.eye_line_menu.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        # === アクション設定 ===
        action_frame = ctk.CTkFrame(self.content_frame)
        action_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
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

        # === ビジュアル効果 ===
        visual_frame = ctk.CTkFrame(self.content_frame)
        visual_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)

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

        # 風の影響
        ctk.CTkLabel(visual_frame, text="風の影響:").grid(row=1, column=2, padx=10, pady=5, sticky="w")
        self.wind_menu = ctk.CTkOptionMenu(
            visual_frame,
            values=list(WIND_EFFECTS.keys()),
            width=130
        )
        self.wind_menu.set("前からの風")
        self.wind_menu.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        # === カメラワーク ===
        camera_frame = ctk.CTkFrame(self.content_frame)
        camera_frame.grid(row=4, column=0, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(
            camera_frame,
            text="カメラワーク",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=4, padx=10, pady=(10, 5), sticky="w")

        # カメラアングル
        ctk.CTkLabel(camera_frame, text="アングル:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.camera_angle_menu = ctk.CTkOptionMenu(
            camera_frame,
            values=list(CAMERA_ANGLES.keys()),
            width=150
        )
        self.camera_angle_menu.set("真横（格ゲー風）")
        self.camera_angle_menu.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # ズーム
        ctk.CTkLabel(camera_frame, text="ズーム:").grid(row=1, column=2, padx=10, pady=5, sticky="w")
        self.zoom_menu = ctk.CTkOptionMenu(
            camera_frame,
            values=list(ZOOM_LEVELS.keys()),
            width=120
        )
        self.zoom_menu.set("全身")
        self.zoom_menu.grid(row=1, column=3, padx=5, pady=5, sticky="w")

    def _browse_image(self):
        """画像参照ダイアログ"""
        filename = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]
        )
        if filename:
            self.image_entry.delete(0, tk.END)
            self.image_entry.insert(0, filename)

    def collect_data(self) -> dict:
        """UIから設定データを収集"""
        return {
            'image_path': self.image_entry.get().strip(),
            'identity_preservation': self.preservation_slider.get(),
            'facing': self.facing_menu.get(),
            'eye_line': self.eye_line_menu.get(),
            'action_category': self.category_menu.get(),
            'pose': self.pose_menu.get(),
            'action_description': self.action_desc_entry.get().strip(),
            'dynamism': self.dynamism_menu.get(),
            'include_effects': self.include_effects_var.get(),
            'wind_effect': self.wind_menu.get(),
            'camera_angle': self.camera_angle_menu.get(),
            'zoom': self.zoom_menu.get()
        }

    def validate(self) -> tuple[bool, str]:
        """入力検証"""
        if not self.image_entry.get().strip():
            return False, "キャラクター画像を指定してください。"
        return True, ""
