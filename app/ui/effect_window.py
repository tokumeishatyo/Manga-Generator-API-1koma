# -*- coding: utf-8 -*-
"""
エフェクト追加設定ウィンドウ
character_effect.yaml準拠
ポーズ付きキャラ画像にVFXを追加する
"""

import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog
from typing import Callable, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.base_settings_window import BaseSettingsWindow


# エフェクト用定数（character_effect.yaml準拠）
PRESERVATION_LEVELS = {
    "厳密（1ピクセルも変えない）": "Strict",
    "緩め（光の影響を許容）": "Loose"
}

ATTACK_EFFECT_TYPES = {
    "なし": "",
    "エネルギービーム": "Energy Beam",
    "飛び道具": "Projectile",
    "斬撃": "Slash",
    "爆発": "Explosion"
}

STATE_EFFECT_TYPES = {
    "なし": "",
    "オーラ": "Aura",
    "バリア": "Shield",
    "強化発光": "Buff"
}

EFFECT_LAYERS = {
    "キャラの背面": "Behind",
    "キャラの前面": "Front/Over"
}

TARGET_AREAS = {
    "全身": "Full Body",
    "足元": "Feet",
    "武器のみ": "Weapon Only",
    "手のみ": "Hands Only"
}

BACKGROUND_EFFECT_STYLES = {
    "なし": "",
    "必殺技カットイン": "Super Move Cut-in",
    "集中線": "Speed Lines",
    "インパクト瞬間": "Impact Frames"
}

COMPOSITE_MODES = {
    "背景を置き換え": "Replace Background",
    "背景に重ねる": "Overlay"
}

VFX_STYLES = {
    "アニメ/格ゲー風": "Anime/Fighting Game, Cel Shaded VFX",
    "リアル調": "Realistic VFX",
    "レトロゲーム風": "Retro Game Style"
}

INTENSITY_LEVELS = {
    "控えめ": "Low (Subtle)",
    "標準": "Medium",
    "派手": "High (Hype)"
}


class EffectWindow(BaseSettingsWindow):
    """エフェクト追加設定ウィンドウ"""

    def __init__(
        self,
        parent,
        callback: Optional[Callable] = None,
        initial_data: Optional[dict] = None
    ):
        self.initial_data = initial_data or {}
        super().__init__(
            parent,
            title="エフェクト追加設定",
            width=750,
            height=850,
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
            text="ベース画像",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkLabel(
            input_frame,
            text="ポーズ付きキャラ画像を指定（キャラ自体は再描画しません）",
            font=("Arial", 11),
            text_color="gray"
        ).grid(row=1, column=0, columnspan=3, padx=10, pady=(0, 5), sticky="w")

        # 画像パス
        ctk.CTkLabel(input_frame, text="画像:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        img_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        img_frame.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        img_frame.grid_columnconfigure(0, weight=1)

        self.image_entry = ctk.CTkEntry(img_frame, placeholder_text="ポーズ付きキャラ画像")
        self.image_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkButton(
            img_frame,
            text="参照",
            width=60,
            command=self._browse_image
        ).grid(row=0, column=1)

        # キャラ保護レベル
        ctk.CTkLabel(input_frame, text="キャラ保護:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.preservation_menu = ctk.CTkOptionMenu(
            input_frame,
            values=list(PRESERVATION_LEVELS.keys()),
            width=200
        )
        self.preservation_menu.set("厳密（1ピクセルも変えない）")
        self.preservation_menu.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # === 攻撃エフェクト ===
        attack_frame = ctk.CTkFrame(self.content_frame)
        attack_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        attack_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            attack_frame,
            text="攻撃エフェクト（ビーム、弾など）",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=4, padx=10, pady=(10, 5), sticky="w")

        # タイプ
        ctk.CTkLabel(attack_frame, text="タイプ:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.attack_type_menu = ctk.CTkOptionMenu(
            attack_frame,
            values=list(ATTACK_EFFECT_TYPES.keys()),
            width=130
        )
        self.attack_type_menu.set("エネルギービーム")
        self.attack_type_menu.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # 発生源
        ctk.CTkLabel(attack_frame, text="発生源:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.attack_origin_entry = ctk.CTkEntry(
            attack_frame,
            placeholder_text="例：魔法の杖の先端、両手から"
        )
        self.attack_origin_entry.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        # 方向
        ctk.CTkLabel(attack_frame, text="方向:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.attack_direction_entry = ctk.CTkEntry(
            attack_frame,
            placeholder_text="例：右方向へ発射、前方へ放出"
        )
        self.attack_direction_entry.grid(row=3, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        # 色と質感
        ctk.CTkLabel(attack_frame, text="色:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.attack_color_entry = ctk.CTkEntry(
            attack_frame,
            placeholder_text="例：赤とオレンジの混合、青白い光"
        )
        self.attack_color_entry.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(attack_frame, text="質感:").grid(row=4, column=2, padx=10, pady=5, sticky="w")
        self.attack_texture_entry = ctk.CTkEntry(
            attack_frame,
            placeholder_text="例：渦を巻く、パーティクル"
        )
        self.attack_texture_entry.grid(row=4, column=3, padx=5, pady=5, sticky="ew")

        # === 状態変化エフェクト ===
        state_frame = ctk.CTkFrame(self.content_frame)
        state_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        state_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            state_frame,
            text="状態変化エフェクト（オーラ、バリアなど）",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=4, padx=10, pady=(10, 5), sticky="w")

        # タイプ
        ctk.CTkLabel(state_frame, text="タイプ:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.state_type_menu = ctk.CTkOptionMenu(
            state_frame,
            values=list(STATE_EFFECT_TYPES.keys()),
            width=100
        )
        self.state_type_menu.set("オーラ")
        self.state_type_menu.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # 範囲
        ctk.CTkLabel(state_frame, text="範囲:").grid(row=1, column=2, padx=10, pady=5, sticky="w")
        self.state_area_menu = ctk.CTkOptionMenu(
            state_frame,
            values=list(TARGET_AREAS.keys()),
            width=100
        )
        self.state_area_menu.set("全身")
        self.state_area_menu.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        # レイヤー
        ctk.CTkLabel(state_frame, text="レイヤー:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.state_layer_menu = ctk.CTkOptionMenu(
            state_frame,
            values=list(EFFECT_LAYERS.keys()),
            width=130
        )
        self.state_layer_menu.set("キャラの背面")
        self.state_layer_menu.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # 色と質感
        ctk.CTkLabel(state_frame, text="色/質感:").grid(row=2, column=2, padx=10, pady=5, sticky="w")
        self.state_visual_entry = ctk.CTkEntry(
            state_frame,
            placeholder_text="例：金色の電気、上に立ち昇る炎"
        )
        self.state_visual_entry.grid(row=2, column=3, padx=5, pady=5, sticky="ew")

        # === 背景演出エフェクト ===
        bg_frame = ctk.CTkFrame(self.content_frame)
        bg_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(
            bg_frame,
            text="背景演出エフェクト",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=4, padx=10, pady=(10, 5), sticky="w")

        # スタイル
        ctk.CTkLabel(bg_frame, text="スタイル:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.bg_style_menu = ctk.CTkOptionMenu(
            bg_frame,
            values=list(BACKGROUND_EFFECT_STYLES.keys()),
            width=150
        )
        self.bg_style_menu.set("必殺技カットイン")
        self.bg_style_menu.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # 合成モード
        ctk.CTkLabel(bg_frame, text="合成:").grid(row=1, column=2, padx=10, pady=5, sticky="w")
        self.bg_composite_menu = ctk.CTkOptionMenu(
            bg_frame,
            values=list(COMPOSITE_MODES.keys()),
            width=130
        )
        self.bg_composite_menu.set("背景を置き換え")
        self.bg_composite_menu.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        # === 全体スタイル ===
        global_frame = ctk.CTkFrame(self.content_frame)
        global_frame.grid(row=4, column=0, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(
            global_frame,
            text="全体スタイル",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=4, padx=10, pady=(10, 5), sticky="w")

        # VFXスタイル
        ctk.CTkLabel(global_frame, text="VFXスタイル:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.vfx_style_menu = ctk.CTkOptionMenu(
            global_frame,
            values=list(VFX_STYLES.keys()),
            width=180
        )
        self.vfx_style_menu.set("アニメ/格ゲー風")
        self.vfx_style_menu.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # 強度
        ctk.CTkLabel(global_frame, text="強度:").grid(row=1, column=2, padx=10, pady=5, sticky="w")
        self.intensity_menu = ctk.CTkOptionMenu(
            global_frame,
            values=list(INTENSITY_LEVELS.keys()),
            width=100
        )
        self.intensity_menu.set("派手")
        self.intensity_menu.grid(row=1, column=3, padx=5, pady=5, sticky="w")

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
            'preservation_level': self.preservation_menu.get(),
            'attack_effect': {
                'type': self.attack_type_menu.get(),
                'origin': self.attack_origin_entry.get().strip(),
                'direction': self.attack_direction_entry.get().strip(),
                'color': self.attack_color_entry.get().strip(),
                'texture': self.attack_texture_entry.get().strip()
            },
            'state_effect': {
                'type': self.state_type_menu.get(),
                'area': self.state_area_menu.get(),
                'layer': self.state_layer_menu.get(),
                'visual': self.state_visual_entry.get().strip()
            },
            'background_effect': {
                'style': self.bg_style_menu.get(),
                'composite_mode': self.bg_composite_menu.get()
            },
            'global_style': {
                'vfx_style': self.vfx_style_menu.get(),
                'intensity': self.intensity_menu.get()
            }
        }

    def validate(self) -> tuple[bool, str]:
        """入力検証"""
        if not self.image_entry.get().strip():
            return False, "ベース画像を指定してください。"
        return True, ""
