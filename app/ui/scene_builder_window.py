# -*- coding: utf-8 -*-
"""
シーンビルダーウィンドウ
Google YAML準拠のシーン合成機能
- バトルシーン合成 (scene_composite.yaml)
- ストーリーシーン合成 (story_scene_composite.yaml)
- ボスレイド合成 (boss_raid_composition.yaml)
"""

import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import (
    COMPOSITE_POSITIONS, COMPOSITE_SIZES, COMPOSITE_LAYOUTS, COMPOSITE_BATTLE_MODES
)
from ui.text_overlay_placement_window import TextOverlayPlacementWindow, TEXT_POSITIONS


# シーン合成タイプ
COMPOSITION_TYPES = {
    "バトルシーン": "battle",
    "ストーリーシーン": "story",
    "ボスレイド": "boss_raid"
}

# バトル用: 衝突タイプ
COLLISION_TYPES = {
    "中央衝突": "Center Clash",
    "画面分割": "Split Screen",
    "グラデーション融合": "Merge/Blend"
}

# バトル用: 優勢側
DOMINANT_SIDES = {
    "互角": "None (Even)",
    "左側有利": "Left",
    "右側有利": "Right"
}

# バトル用: 境界エフェクト
BORDER_VFX = {
    "火花と稲妻": "Intense Sparks & Lightning",
    "シンプル": "Simple Glow",
    "なし": "None"
}

# バトル用: 画面揺れ
SCREEN_SHAKE = {
    "なし": "None",
    "軽め": "Mild",
    "普通": "Moderate",
    "激しい": "Heavy"
}

# ストーリー用: 配置パターン
STORY_LAYOUTS = {
    "並んで歩く": "Side by Side (Walking)",
    "向かい合う（テーブル）": "Face to Face (Table)",
    "中央で話す": "Center & Listener"
}

# ストーリー用: 距離感
STORY_DISTANCE = {
    "親しい": "Close Friends",
    "普通": "Normal",
    "遠い": "Distant"
}

# ストーリー用: 雰囲気
LIGHTING_MOODS = {
    "朝の光": "Morning Sunlight",
    "夕焼け": "Sunset",
    "夏の正午": "Summer Noon",
    "夜": "Night"
}

# 共通: 合成モード
BLEND_MODES = {
    "発光（加算）": "Add",
    "スクリーン": "Screen",
    "通常": "Normal"
}


class SceneBuilderWindow(ctk.CTkToplevel):
    """シーンビルダーウィンドウ"""

    def __init__(self, parent, callback=None):
        super().__init__(parent)

        self.callback = callback
        self.text_overlay_data = []  # 装飾テキスト配置データ

        # ウィンドウ設定
        self.title("シーンビルダー")
        self.geometry("850x850")
        self.resizable(True, True)

        # 非モーダル
        self.transient(parent)

        # UI構築
        self._build_ui()

    def _build_ui(self):
        """UIを構築"""
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # タイトル
        ctk.CTkLabel(
            main_frame,
            text="シーン合成",
            font=("Arial", 18, "bold")
        ).pack(anchor="w", padx=10, pady=(0, 10))

        # 合成タイプ選択
        type_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        type_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(type_frame, text="合成タイプ:", width=100).pack(side="left")
        self.composition_type_var = tk.StringVar(value="バトルシーン")
        self.composition_type_menu = ctk.CTkOptionMenu(
            type_frame,
            variable=self.composition_type_var,
            values=list(COMPOSITION_TYPES.keys()),
            command=self._on_composition_type_change,
            width=200
        )
        self.composition_type_menu.pack(side="left", padx=5)

        # 設定コンテナ（タイプ別に切り替え）
        self.settings_container = ctk.CTkFrame(main_frame)
        self.settings_container.pack(fill="both", expand=True, pady=10)

        # 各タイプ用フレームを作成
        self.battle_frame = ctk.CTkFrame(self.settings_container)
        self.story_frame = ctk.CTkFrame(self.settings_container)
        self.boss_frame = ctk.CTkFrame(self.settings_container)

        self._build_battle_settings(self.battle_frame)
        self._build_story_settings(self.story_frame)
        self._build_boss_settings(self.boss_frame)

        # 初期表示
        self._on_composition_type_change("バトルシーン")

        # 装飾テキストオーバーレイセクション（共通）
        self._build_text_overlay_section(main_frame)

        # プレビューとボタン
        self._build_preview_section(main_frame)

    def _on_composition_type_change(self, value):
        """合成タイプ変更"""
        # 全フレームを非表示
        for frame in [self.battle_frame, self.story_frame, self.boss_frame]:
            frame.pack_forget()

        # 選択されたタイプのフレームを表示
        if value == "バトルシーン":
            self.battle_frame.pack(fill="both", expand=True)
        elif value == "ストーリーシーン":
            self.story_frame.pack(fill="both", expand=True)
        elif value == "ボスレイド":
            self.boss_frame.pack(fill="both", expand=True)

    def _on_story_bg_type_change(self):
        """ストーリー背景タイプ変更"""
        bg_type = self.story_bg_type_var.get()
        if bg_type == "file":
            self.story_bg_prompt_frame.pack_forget()
            self.story_bg_file_frame.pack(fill="x", padx=10, pady=5)
        else:
            self.story_bg_file_frame.pack_forget()
            self.story_bg_prompt_frame.pack(fill="x", padx=10, pady=5)

    def _on_battle_bg_type_change(self):
        """バトル背景タイプ変更"""
        bg_type = self.battle_bg_type_var.get()
        if bg_type == "file":
            self.battle_bg_prompt_frame.pack_forget()
            self.battle_bg_file_frame.pack(fill="x", padx=10, pady=5)
        else:
            self.battle_bg_file_frame.pack_forget()
            self.battle_bg_prompt_frame.pack(fill="x", padx=10, pady=5)

    # ========== バトルシーン設定 ==========

    def _build_battle_settings(self, parent):
        """バトルシーン設定を構築"""
        canvas = ctk.CTkScrollableFrame(parent)
        canvas.pack(fill="both", expand=True)

        # === 背景設定 ===
        bg_frame = ctk.CTkFrame(canvas)
        bg_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(bg_frame, text="背景設定", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=5)

        # 背景タイプ選択（ファイル指定 / 情景説明）
        bg_type_row = ctk.CTkFrame(bg_frame, fg_color="transparent")
        bg_type_row.pack(fill="x", padx=10, pady=5)

        self.battle_bg_type_var = tk.StringVar(value="file")
        ctk.CTkRadioButton(
            bg_type_row, text="ファイル指定", variable=self.battle_bg_type_var,
            value="file", command=self._on_battle_bg_type_change
        ).pack(side="left", padx=(0, 15))
        ctk.CTkRadioButton(
            bg_type_row, text="情景説明で生成", variable=self.battle_bg_type_var,
            value="prompt", command=self._on_battle_bg_type_change
        ).pack(side="left")

        # ファイル指定用フレーム
        self.battle_bg_file_frame = ctk.CTkFrame(bg_frame, fg_color="transparent")
        self.battle_bg_file_frame.pack(fill="x", padx=10, pady=5)
        self.battle_bg_file_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.battle_bg_file_frame, text="背景画像:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.battle_bg_entry = ctk.CTkEntry(self.battle_bg_file_frame, placeholder_text="背景画像パス")
        self.battle_bg_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(self.battle_bg_file_frame, text="参照", width=60, command=lambda: self._browse_image(self.battle_bg_entry)).grid(row=0, column=2, padx=5)

        # 情景説明用フレーム（初期非表示）
        self.battle_bg_prompt_frame = ctk.CTkFrame(bg_frame, fg_color="transparent")
        self.battle_bg_prompt_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.battle_bg_prompt_frame, text="情景説明:").grid(row=0, column=0, padx=5, pady=5, sticky="nw")
        self.battle_bg_prompt_entry = ctk.CTkTextbox(self.battle_bg_prompt_frame, height=60)
        self.battle_bg_prompt_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.battle_bg_prompt_entry.insert("1.0", "荒廃した都市の廃墟、炎が燃え盛る背景")

        # 共通設定（暗さ）
        bg_common_row = ctk.CTkFrame(bg_frame, fg_color="transparent")
        bg_common_row.pack(fill="x", padx=10, pady=5)
        bg_common_row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(bg_common_row, text="暗さ:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.battle_dimming_slider = ctk.CTkSlider(bg_common_row, from_=0, to=1, number_of_steps=10)
        self.battle_dimming_slider.set(0.5)
        self.battle_dimming_slider.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # === カットイン演出設定（左右横並び） ===
        cutin_frame = ctk.CTkFrame(canvas)
        cutin_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(cutin_frame, text="カットイン演出", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=5)

        # 左右横並びコンテナ
        cutin_row = ctk.CTkFrame(cutin_frame, fg_color="transparent")
        cutin_row.pack(fill="x", padx=10, pady=5)
        cutin_row.grid_columnconfigure(0, weight=1)
        cutin_row.grid_columnconfigure(1, weight=1)

        # 左側演出
        left_cutin = ctk.CTkFrame(cutin_row)
        left_cutin.grid(row=0, column=0, padx=(0, 5), sticky="nsew")

        self.battle_left_cutin_var = tk.BooleanVar(value=True)
        left_row = ctk.CTkFrame(left_cutin, fg_color="transparent")
        left_row.pack(fill="x", padx=5, pady=3)
        ctk.CTkCheckBox(left_row, text="左", variable=self.battle_left_cutin_var, width=40).pack(side="left")
        self.battle_left_cutin_entry = ctk.CTkEntry(left_row, placeholder_text="画像", width=100)
        self.battle_left_cutin_entry.pack(side="left", padx=2)
        ctk.CTkButton(left_row, text="参照", width=40, command=lambda: self._browse_image(self.battle_left_cutin_entry)).pack(side="left")
        self.battle_left_blend_menu = ctk.CTkOptionMenu(left_row, values=list(BLEND_MODES.keys()), width=100)
        self.battle_left_blend_menu.set("発光（加算）")
        self.battle_left_blend_menu.pack(side="left", padx=2)

        # 右側演出
        right_cutin = ctk.CTkFrame(cutin_row)
        right_cutin.grid(row=0, column=1, padx=(5, 0), sticky="nsew")

        self.battle_right_cutin_var = tk.BooleanVar(value=True)
        right_row = ctk.CTkFrame(right_cutin, fg_color="transparent")
        right_row.pack(fill="x", padx=5, pady=3)
        ctk.CTkCheckBox(right_row, text="右", variable=self.battle_right_cutin_var, width=40).pack(side="left")
        self.battle_right_cutin_entry = ctk.CTkEntry(right_row, placeholder_text="画像", width=100)
        self.battle_right_cutin_entry.pack(side="left", padx=2)
        ctk.CTkButton(right_row, text="参照", width=40, command=lambda: self._browse_image(self.battle_right_cutin_entry)).pack(side="left")
        self.battle_right_blend_menu = ctk.CTkOptionMenu(right_row, values=list(BLEND_MODES.keys()), width=100)
        self.battle_right_blend_menu.set("発光（加算）")
        self.battle_right_blend_menu.pack(side="left", padx=2)

        # === 衝突設定 ===
        collision_frame = ctk.CTkFrame(canvas)
        collision_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(collision_frame, text="衝突設定", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=5)

        collision_row = ctk.CTkFrame(collision_frame, fg_color="transparent")
        collision_row.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(collision_row, text="衝突タイプ:").pack(side="left", padx=5)
        self.battle_collision_menu = ctk.CTkOptionMenu(collision_row, values=list(COLLISION_TYPES.keys()), width=140)
        self.battle_collision_menu.set("中央衝突")
        self.battle_collision_menu.pack(side="left", padx=5)

        ctk.CTkLabel(collision_row, text="優勢:").pack(side="left", padx=(20, 5))
        self.battle_dominant_menu = ctk.CTkOptionMenu(collision_row, values=list(DOMINANT_SIDES.keys()), width=100)
        self.battle_dominant_menu.set("互角")
        self.battle_dominant_menu.pack(side="left", padx=5)

        ctk.CTkLabel(collision_row, text="境界エフェクト:").pack(side="left", padx=(20, 5))
        self.battle_border_menu = ctk.CTkOptionMenu(collision_row, values=list(BORDER_VFX.keys()), width=120)
        self.battle_border_menu.set("火花と稲妻")
        self.battle_border_menu.pack(side="left", padx=5)

        # === キャラクター配置 ===
        char_frame = ctk.CTkFrame(canvas)
        char_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(char_frame, text="キャラクター配置", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=5)

        # 左キャラ
        left_char = ctk.CTkFrame(char_frame, fg_color="transparent")
        left_char.pack(fill="x", padx=10, pady=5)
        left_char.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(left_char, text="左キャラ画像:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.battle_left_char_entry = ctk.CTkEntry(left_char, placeholder_text="ポーズ付きキャラ画像")
        self.battle_left_char_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(left_char, text="参照", width=60, command=lambda: self._browse_image(self.battle_left_char_entry)).grid(row=0, column=2, padx=5)

        ctk.CTkLabel(left_char, text="スケール:").grid(row=0, column=3, padx=5, sticky="w")
        self.battle_left_scale_entry = ctk.CTkEntry(left_char, width=60, placeholder_text="1.0")
        self.battle_left_scale_entry.insert(0, "1.2")
        self.battle_left_scale_entry.grid(row=0, column=4, padx=5)

        ctk.CTkLabel(left_char, text="名前:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.battle_left_name_entry = ctk.CTkEntry(left_char, placeholder_text="AYASE KOYOMI")
        self.battle_left_name_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(left_char, text="特徴:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.battle_left_traits_entry = ctk.CTkEntry(left_char, placeholder_text="長い黒髪、身長高め")
        self.battle_left_traits_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # 右キャラ
        right_char = ctk.CTkFrame(char_frame, fg_color="transparent")
        right_char.pack(fill="x", padx=10, pady=5)
        right_char.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(right_char, text="右キャラ画像:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.battle_right_char_entry = ctk.CTkEntry(right_char, placeholder_text="ポーズ付きキャラ画像")
        self.battle_right_char_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(right_char, text="参照", width=60, command=lambda: self._browse_image(self.battle_right_char_entry)).grid(row=0, column=2, padx=5)

        ctk.CTkLabel(right_char, text="スケール:").grid(row=0, column=3, padx=5, sticky="w")
        self.battle_right_scale_entry = ctk.CTkEntry(right_char, width=60, placeholder_text="1.0")
        self.battle_right_scale_entry.insert(0, "1.2")
        self.battle_right_scale_entry.grid(row=0, column=4, padx=5)

        ctk.CTkLabel(right_char, text="名前:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.battle_right_name_entry = ctk.CTkEntry(right_char, placeholder_text="SHINOMIYA RIN")
        self.battle_right_name_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(right_char, text="特徴:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.battle_right_traits_entry = ctk.CTkEntry(right_char, placeholder_text="ツインテール金髪")
        self.battle_right_traits_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # === 画面効果 ===
        effect_frame = ctk.CTkFrame(canvas)
        effect_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(effect_frame, text="画面効果", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=5)

        effect_row = ctk.CTkFrame(effect_frame, fg_color="transparent")
        effect_row.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(effect_row, text="画面揺れ:").pack(side="left", padx=5)
        self.battle_shake_menu = ctk.CTkOptionMenu(effect_row, values=list(SCREEN_SHAKE.keys()), width=100)
        self.battle_shake_menu.set("激しい")
        self.battle_shake_menu.pack(side="left", padx=5)

        self.battle_ui_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(effect_row, text="UI表示", variable=self.battle_ui_var).pack(side="left", padx=20)

    # ========== ストーリーシーン設定 ==========

    def _build_story_settings(self, parent):
        """ストーリーシーン設定を構築"""
        canvas = ctk.CTkScrollableFrame(parent)
        canvas.pack(fill="both", expand=True)

        # === 背景設定 ===
        bg_frame = ctk.CTkFrame(canvas)
        bg_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(bg_frame, text="背景設定", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=5)

        # 背景タイプ選択（ファイル指定 / 情景説明）
        bg_type_row = ctk.CTkFrame(bg_frame, fg_color="transparent")
        bg_type_row.pack(fill="x", padx=10, pady=5)

        self.story_bg_type_var = tk.StringVar(value="file")
        ctk.CTkRadioButton(
            bg_type_row, text="ファイル指定", variable=self.story_bg_type_var,
            value="file", command=self._on_story_bg_type_change
        ).pack(side="left", padx=(0, 15))
        ctk.CTkRadioButton(
            bg_type_row, text="情景説明で生成", variable=self.story_bg_type_var,
            value="prompt", command=self._on_story_bg_type_change
        ).pack(side="left")

        # ファイル指定用フレーム
        self.story_bg_file_frame = ctk.CTkFrame(bg_frame, fg_color="transparent")
        self.story_bg_file_frame.pack(fill="x", padx=10, pady=5)
        self.story_bg_file_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.story_bg_file_frame, text="背景画像:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.story_bg_entry = ctk.CTkEntry(self.story_bg_file_frame, placeholder_text="背景画像パス")
        self.story_bg_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(self.story_bg_file_frame, text="参照", width=60, command=lambda: self._browse_image(self.story_bg_entry)).grid(row=0, column=2, padx=5)

        # 情景説明用フレーム（初期非表示）
        self.story_bg_prompt_frame = ctk.CTkFrame(bg_frame, fg_color="transparent")
        self.story_bg_prompt_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.story_bg_prompt_frame, text="情景説明:").grid(row=0, column=0, padx=5, pady=5, sticky="nw")
        self.story_bg_prompt_entry = ctk.CTkTextbox(self.story_bg_prompt_frame, height=60)
        self.story_bg_prompt_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.story_bg_prompt_entry.insert("1.0", "ゴージャスなパーティ会場、シャンデリアが輝く広いホール")

        # 共通設定（ぼかし・雰囲気）
        bg_common_row = ctk.CTkFrame(bg_frame, fg_color="transparent")
        bg_common_row.pack(fill="x", padx=10, pady=5)
        bg_common_row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(bg_common_row, text="ぼかし:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.story_blur_slider = ctk.CTkSlider(bg_common_row, from_=0, to=100, number_of_steps=20)
        self.story_blur_slider.set(10)
        self.story_blur_slider.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(bg_common_row, text="雰囲気:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.story_mood_menu = ctk.CTkOptionMenu(bg_common_row, values=list(LIGHTING_MOODS.keys()), width=150)
        self.story_mood_menu.set("朝の光")
        self.story_mood_menu.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # === 配置設定 ===
        layout_frame = ctk.CTkFrame(canvas)
        layout_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(layout_frame, text="配置設定", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=5)

        layout_row = ctk.CTkFrame(layout_frame, fg_color="transparent")
        layout_row.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(layout_row, text="配置パターン:").pack(side="left", padx=5)
        self.story_layout_menu = ctk.CTkOptionMenu(layout_row, values=list(STORY_LAYOUTS.keys()), width=180)
        self.story_layout_menu.set("並んで歩く")
        self.story_layout_menu.pack(side="left", padx=5)

        ctk.CTkLabel(layout_row, text="距離感:").pack(side="left", padx=(20, 5))
        self.story_distance_menu = ctk.CTkOptionMenu(layout_row, values=list(STORY_DISTANCE.keys()), width=100)
        self.story_distance_menu.set("親しい")
        self.story_distance_menu.pack(side="left", padx=5)

        # === キャラクター配置（3人まで対応） ===
        char_frame = ctk.CTkFrame(canvas)
        char_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(char_frame, text="キャラクター配置（最大3人）", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=5)

        # 3人のキャラを横並びに
        char_row = ctk.CTkFrame(char_frame, fg_color="transparent")
        char_row.pack(fill="x", padx=10, pady=5)
        char_row.grid_columnconfigure(0, weight=1)
        char_row.grid_columnconfigure(1, weight=1)
        char_row.grid_columnconfigure(2, weight=1)

        # 左キャラ
        left_char = ctk.CTkFrame(char_row)
        left_char.grid(row=0, column=0, padx=2, sticky="nsew")

        ctk.CTkLabel(left_char, text="キャラ1（左）", font=("Arial", 11, "bold")).pack(anchor="w", padx=5, pady=2)
        left_img_row = ctk.CTkFrame(left_char, fg_color="transparent")
        left_img_row.pack(fill="x", padx=5, pady=2)
        self.story_left_char_entry = ctk.CTkEntry(left_img_row, placeholder_text="画像", width=120)
        self.story_left_char_entry.pack(side="left", padx=(0, 3))
        ctk.CTkButton(left_img_row, text="参照", width=40, command=lambda: self._browse_image(self.story_left_char_entry)).pack(side="left")

        left_expr_row = ctk.CTkFrame(left_char, fg_color="transparent")
        left_expr_row.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(left_expr_row, text="表情:").pack(side="left")
        self.story_left_expr_entry = ctk.CTkEntry(left_expr_row, placeholder_text="笑顔", width=80)
        self.story_left_expr_entry.pack(side="left", padx=3)

        left_traits_row = ctk.CTkFrame(left_char, fg_color="transparent")
        left_traits_row.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(left_traits_row, text="特徴:").pack(side="left")
        self.story_left_traits_entry = ctk.CTkEntry(left_traits_row, placeholder_text="長い黒髪、身長高め", width=130)
        self.story_left_traits_entry.pack(side="left", padx=3)

        # 中央キャラ（任意）
        center_char = ctk.CTkFrame(char_row)
        center_char.grid(row=0, column=1, padx=2, sticky="nsew")

        ctk.CTkLabel(center_char, text="キャラ2（中央・任意）", font=("Arial", 11, "bold")).pack(anchor="w", padx=5, pady=2)
        center_img_row = ctk.CTkFrame(center_char, fg_color="transparent")
        center_img_row.pack(fill="x", padx=5, pady=2)
        self.story_center_char_entry = ctk.CTkEntry(center_img_row, placeholder_text="画像", width=120)
        self.story_center_char_entry.pack(side="left", padx=(0, 3))
        ctk.CTkButton(center_img_row, text="参照", width=40, command=lambda: self._browse_image(self.story_center_char_entry)).pack(side="left")

        center_expr_row = ctk.CTkFrame(center_char, fg_color="transparent")
        center_expr_row.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(center_expr_row, text="表情:").pack(side="left")
        self.story_center_expr_entry = ctk.CTkEntry(center_expr_row, placeholder_text="笑顔", width=80)
        self.story_center_expr_entry.pack(side="left", padx=3)

        center_traits_row = ctk.CTkFrame(center_char, fg_color="transparent")
        center_traits_row.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(center_traits_row, text="特徴:").pack(side="left")
        self.story_center_traits_entry = ctk.CTkEntry(center_traits_row, placeholder_text="セミロング茶髪", width=130)
        self.story_center_traits_entry.pack(side="left", padx=3)

        # 右キャラ
        right_char = ctk.CTkFrame(char_row)
        right_char.grid(row=0, column=2, padx=2, sticky="nsew")

        ctk.CTkLabel(right_char, text="キャラ3（右）", font=("Arial", 11, "bold")).pack(anchor="w", padx=5, pady=2)
        right_img_row = ctk.CTkFrame(right_char, fg_color="transparent")
        right_img_row.pack(fill="x", padx=5, pady=2)
        self.story_right_char_entry = ctk.CTkEntry(right_img_row, placeholder_text="画像", width=120)
        self.story_right_char_entry.pack(side="left", padx=(0, 3))
        ctk.CTkButton(right_img_row, text="参照", width=40, command=lambda: self._browse_image(self.story_right_char_entry)).pack(side="left")

        right_expr_row = ctk.CTkFrame(right_char, fg_color="transparent")
        right_expr_row.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(right_expr_row, text="表情:").pack(side="left")
        self.story_right_expr_entry = ctk.CTkEntry(right_expr_row, placeholder_text="笑顔", width=80)
        self.story_right_expr_entry.pack(side="left", padx=5)

        right_traits_row = ctk.CTkFrame(right_char, fg_color="transparent")
        right_traits_row.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(right_traits_row, text="特徴:").pack(side="left")
        self.story_right_traits_entry = ctk.CTkEntry(right_traits_row, placeholder_text="ショート、小柄", width=130)
        self.story_right_traits_entry.pack(side="left", padx=3)

        # === ダイアログ設定 ===
        dialog_frame = ctk.CTkFrame(canvas)
        dialog_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(dialog_frame, text="ダイアログ設定", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=5)

        # ナレーション（1行）
        narr_row = ctk.CTkFrame(dialog_frame, fg_color="transparent")
        narr_row.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(narr_row, text="ナレーション:").pack(side="left", padx=(0, 5))
        self.story_narration_entry = ctk.CTkEntry(narr_row, placeholder_text="今日から新学期が始まる", width=300)
        self.story_narration_entry.pack(side="left", fill="x", expand=True)

        # セリフ（3人分）
        speech_row = ctk.CTkFrame(dialog_frame, fg_color="transparent")
        speech_row.pack(fill="x", padx=10, pady=2)
        speech_row.grid_columnconfigure(0, weight=1)
        speech_row.grid_columnconfigure(1, weight=1)
        speech_row.grid_columnconfigure(2, weight=1)

        # キャラ1セリフ
        speech1_frame = ctk.CTkFrame(speech_row, fg_color="transparent")
        speech1_frame.grid(row=0, column=0, padx=2, sticky="ew")
        ctk.CTkLabel(speech1_frame, text="キャラ1:").pack(side="left")
        self.story_left_speech_entry = ctk.CTkEntry(speech1_frame, placeholder_text="おはよう！", width=100)
        self.story_left_speech_entry.pack(side="left", padx=2)

        # キャラ2セリフ
        speech2_frame = ctk.CTkFrame(speech_row, fg_color="transparent")
        speech2_frame.grid(row=0, column=1, padx=2, sticky="ew")
        ctk.CTkLabel(speech2_frame, text="キャラ2:").pack(side="left")
        self.story_center_speech_entry = ctk.CTkEntry(speech2_frame, placeholder_text="（任意）", width=100)
        self.story_center_speech_entry.pack(side="left", padx=2)

        # キャラ3セリフ
        speech3_frame = ctk.CTkFrame(speech_row, fg_color="transparent")
        speech3_frame.grid(row=0, column=2, padx=2, sticky="ew")
        ctk.CTkLabel(speech3_frame, text="キャラ3:").pack(side="left")
        self.story_right_speech_entry = ctk.CTkEntry(speech3_frame, placeholder_text="おはよう", width=100)
        self.story_right_speech_entry.pack(side="left", padx=2)

    # ========== ボスレイド設定 ==========

    def _build_boss_settings(self, parent):
        """ボスレイド設定を構築"""
        canvas = ctk.CTkScrollableFrame(parent)
        canvas.pack(fill="both", expand=True)

        # === ボス設定 ===
        boss_frame = ctk.CTkFrame(canvas)
        boss_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(boss_frame, text="巨大ボス設定", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=5)

        boss_row = ctk.CTkFrame(boss_frame, fg_color="transparent")
        boss_row.pack(fill="x", padx=10, pady=5)
        boss_row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(boss_row, text="ボス画像:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.boss_image_entry = ctk.CTkEntry(boss_row, placeholder_text="巨大ボス画像")
        self.boss_image_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(boss_row, text="参照", width=60, command=lambda: self._browse_image(self.boss_image_entry)).grid(row=0, column=2, padx=5)

        ctk.CTkLabel(boss_row, text="スケール:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.boss_scale_entry = ctk.CTkEntry(boss_row, width=60, placeholder_text="2.5")
        self.boss_scale_entry.insert(0, "2.5")
        self.boss_scale_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        self.boss_crop_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(boss_row, text="画面からはみ出し許可", variable=self.boss_crop_var).grid(row=1, column=2, padx=10)

        # === パーティメンバー設定 ===
        party_frame = ctk.CTkFrame(canvas)
        party_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(party_frame, text="攻撃部隊（パーティ）", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=5)

        # 3人分のパーティメンバー
        self.boss_party_entries = []
        for i in range(3):
            member_row = ctk.CTkFrame(party_frame, fg_color="transparent")
            member_row.pack(fill="x", padx=10, pady=3)
            member_row.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(member_row, text=f"メンバー{i + 1}:").grid(row=0, column=0, padx=5, pady=3, sticky="w")
            img_entry = ctk.CTkEntry(member_row, placeholder_text="ちびキャラ画像")
            img_entry.grid(row=0, column=1, padx=5, pady=3, sticky="ew")
            ctk.CTkButton(member_row, text="参照", width=60, command=lambda e=img_entry: self._browse_image(e)).grid(row=0, column=2, padx=5)

            action_entry = ctk.CTkEntry(member_row, placeholder_text="Jumping Slash", width=120)
            action_entry.grid(row=0, column=3, padx=5)

            self.boss_party_entries.append({
                'image': img_entry,
                'action': action_entry
            })

        # パーティ基本スケール
        scale_row = ctk.CTkFrame(party_frame, fg_color="transparent")
        scale_row.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(scale_row, text="パーティ基本スケール:").pack(side="left", padx=5)
        self.boss_party_scale_entry = ctk.CTkEntry(scale_row, width=60, placeholder_text="0.6")
        self.boss_party_scale_entry.insert(0, "0.6")
        self.boss_party_scale_entry.pack(side="left", padx=5)

        # === 攻撃エフェクト ===
        attack_frame = ctk.CTkFrame(canvas)
        attack_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(attack_frame, text="集中砲火エフェクト", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=5)

        attack_row = ctk.CTkFrame(attack_frame, fg_color="transparent")
        attack_row.pack(fill="x", padx=10, pady=5)

        self.boss_convergence_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(attack_row, text="集中砲火有効", variable=self.boss_convergence_var).pack(side="left", padx=5)

        ctk.CTkLabel(attack_row, text="ビーム色:").pack(side="left", padx=(20, 5))
        self.boss_beam_color_entry = ctk.CTkEntry(attack_row, placeholder_text="Blue & Pink Lasers", width=150)
        self.boss_beam_color_entry.pack(side="left", padx=5)

    # ========== 装飾テキストオーバーレイ ==========

    def _build_text_overlay_section(self, parent):
        """装飾テキストオーバーレイセクションを構築"""
        overlay_frame = ctk.CTkFrame(parent)
        overlay_frame.pack(fill="x", pady=5)

        row = ctk.CTkFrame(overlay_frame, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=8)

        ctk.CTkLabel(
            row,
            text="装飾テキスト:",
            font=("Arial", 12)
        ).pack(side="left")

        ctk.CTkButton(
            row,
            text="配置設定...",
            width=100,
            command=self._open_text_overlay_window
        ).pack(side="left", padx=10)

        # 配置数表示ラベル
        self.text_overlay_count_label = ctk.CTkLabel(
            row,
            text="0個配置",
            font=("Arial", 11),
            text_color="gray"
        )
        self.text_overlay_count_label.pack(side="left")

    def _open_text_overlay_window(self):
        """装飾テキスト配置ウィンドウを開く"""
        TextOverlayPlacementWindow(
            self,
            callback=self._on_text_overlay_data,
            initial_data=self.text_overlay_data
        )

    def _on_text_overlay_data(self, data):
        """装飾テキスト配置データを受け取る"""
        self.text_overlay_data = data
        count = len(data)
        self.text_overlay_count_label.configure(
            text=f"{count}個配置" if count > 0 else "0個配置",
            text_color="white" if count > 0 else "gray"
        )

    # ========== プレビューとボタン ==========

    def _build_preview_section(self, parent):
        """ボタンセクションを構築"""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", pady=10)

        ctk.CTkButton(
            button_frame,
            text="YAML生成 → メインへ",
            command=self._generate_yaml,
            width=160
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="閉じる",
            command=self.destroy,
            width=80,
            fg_color="gray"
        ).pack(side="right", padx=5)

    # ========== ヘルパーメソッド ==========

    def _browse_image(self, entry):
        """画像参照"""
        filename = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]
        )
        if filename:
            entry.delete(0, tk.END)
            entry.insert(0, filename)

    def _get_filename(self, path: str) -> str:
        """パスからファイル名のみを取得"""
        if not path:
            return ""
        return os.path.basename(path)

    def _generate_text_overlay_yaml(self) -> str:
        """装飾テキストオーバーレイのYAMLセクションを生成（複数対応）"""
        if not self.text_overlay_data:
            return ""

        items_yaml = ""
        for i, item in enumerate(self.text_overlay_data):
            image_path = self._get_filename(item.get('image', ''))
            position_en = item.get('position_en', 'Top Center')

            # キャラ相対位置の場合はplacement_hintを追加
            if "Near" in position_en and "Character" in position_en:
                items_yaml += f"""
    - source_image: "{image_path}"
      position: "{position_en}"
      placement_hint: "Auto-adjust to avoid overlaps"
      blend_mode: "Normal\""""
            else:
                items_yaml += f"""
    - source_image: "{image_path}"
      position: "{position_en}"
      blend_mode: "Normal\""""

        return f"""
decorative_text_overlays:
  enabled: true
  items:{items_yaml}
"""

    def _generate_yaml(self):
        """YAML生成してメインウィンドウに送信"""
        comp_type = self.composition_type_var.get()

        if comp_type == "バトルシーン":
            yaml_content = self._generate_battle_yaml()
        elif comp_type == "ストーリーシーン":
            yaml_content = self._generate_story_yaml()
        elif comp_type == "ボスレイド":
            yaml_content = self._generate_boss_yaml()
        else:
            yaml_content = "# Unknown composition type"

        # コールバックでメインウィンドウに送信
        if self.callback:
            self.callback(yaml_content)
            self.destroy()

    def _generate_battle_yaml(self):
        """バトルシーンYAML生成"""
        # 背景設定
        if self.battle_bg_type_var.get() == "file":
            bg_section = f"""background:
  source_image: "{self._get_filename(self.battle_bg_entry.get().strip())}"
  dimming: {self.battle_dimming_slider.get():.1f}"""
        else:
            bg_prompt = self.battle_bg_prompt_entry.get("1.0", "end-1c").strip()
            bg_section = f"""background:
  generate_from_prompt: true
  scene_description: "{bg_prompt}"
  dimming: {self.battle_dimming_slider.get():.1f}"""

        return f"""# Battle Scene Composition (scene_composite.yaml準拠)
type: final_scene_composition_dual_cutin

{bg_section}

cutin_effects:
  left_effect:
    enabled: {str(self.battle_left_cutin_var.get()).lower()}
    source_image: "{self._get_filename(self.battle_left_cutin_entry.get().strip())}"
    blend_mode: "{BLEND_MODES.get(self.battle_left_blend_menu.get(), 'Add')}"
    opacity: 1.0
  right_effect:
    enabled: {str(self.battle_right_cutin_var.get()).lower()}
    source_image: "{self._get_filename(self.battle_right_cutin_entry.get().strip())}"
    blend_mode: "{BLEND_MODES.get(self.battle_right_blend_menu.get(), 'Add')}"
    opacity: 1.0

collision_settings:
  collision_type: "{COLLISION_TYPES.get(self.battle_collision_menu.get(), 'Center Clash')}"
  border_vfx: "{BORDER_VFX.get(self.battle_border_menu.get(), 'Intense Sparks & Lightning')}"
  dominant_side: "{DOMINANT_SIDES.get(self.battle_dominant_menu.get(), 'None (Even)')}"

left_character:
  source_image: "{self._get_filename(self.battle_left_char_entry.get().strip())}"
  scale: {self.battle_left_scale_entry.get().strip() or '1.0'}
  force_facing: "Right"{f'''
  physical_traits: "{self.battle_left_traits_entry.get().strip()}"''' if self.battle_left_traits_entry.get().strip() else ""}

right_character:
  source_image: "{self._get_filename(self.battle_right_char_entry.get().strip())}"
  scale: {self.battle_right_scale_entry.get().strip() or '1.0'}
  force_facing: "Left"
  flip_image: true{f'''
  physical_traits: "{self.battle_right_traits_entry.get().strip()}"''' if self.battle_right_traits_entry.get().strip() else ""}

ui_overlay:
  enabled: {str(self.battle_ui_var.get()).lower()}
  left_bar_name: "{self.battle_left_name_entry.get().strip()}"
  right_bar_name: "{self.battle_right_name_entry.get().strip()}"

scene_settings:
  interaction_focus: "Maximum Impact"
  screen_shake: "{SCREEN_SHAKE.get(self.battle_shake_menu.get(), 'Heavy')}"
  color_grading: "Dramatic Clash"
{self._generate_text_overlay_yaml()}"""

    def _generate_story_yaml(self):
        """ストーリーシーンYAML生成"""
        # 背景設定
        if self.story_bg_type_var.get() == "file":
            bg_section = f"""background:
  source_image: "{self._get_filename(self.story_bg_entry.get().strip())}"
  blur_amount: {int(self.story_blur_slider.get())}
  lighting_mood: "{LIGHTING_MOODS.get(self.story_mood_menu.get(), 'Morning Sunlight')}\""""
        else:
            bg_prompt = self.story_bg_prompt_entry.get("1.0", "end-1c").strip()
            bg_section = f"""background:
  generate_from_prompt: true
  scene_description: "{bg_prompt}"
  blur_amount: {int(self.story_blur_slider.get())}
  lighting_mood: "{LIGHTING_MOODS.get(self.story_mood_menu.get(), 'Morning Sunlight')}\""""

        # キャラクターセクション（3人対応）
        characters_yaml = ""

        # キャラ1（左）
        left_img = self.story_left_char_entry.get().strip()
        if left_img:
            left_traits = self.story_left_traits_entry.get().strip()
            left_traits_line = f'\n  physical_traits: "{left_traits}"' if left_traits else ""
            characters_yaml += f"""
character_1:
  source_image: "{self._get_filename(left_img)}"
  position: "Left"
  scale: 1.0
  expression_override: "{self.story_left_expr_entry.get().strip() or 'Smiling'}"{left_traits_line}
"""

        # キャラ2（中央）- 任意
        center_img = self.story_center_char_entry.get().strip()
        if center_img:
            center_traits = self.story_center_traits_entry.get().strip()
            center_traits_line = f'\n  physical_traits: "{center_traits}"' if center_traits else ""
            characters_yaml += f"""
character_2:
  source_image: "{self._get_filename(center_img)}"
  position: "Center"
  scale: 1.0
  expression_override: "{self.story_center_expr_entry.get().strip() or 'Smiling'}"{center_traits_line}
"""

        # キャラ3（右）
        right_img = self.story_right_char_entry.get().strip()
        if right_img:
            right_traits = self.story_right_traits_entry.get().strip()
            right_traits_line = f'\n  physical_traits: "{right_traits}"' if right_traits else ""
            characters_yaml += f"""
character_3:
  source_image: "{self._get_filename(right_img)}"
  position: "Right"
  scale: 1.0
  expression_override: "{self.story_right_expr_entry.get().strip() or 'Smiling'}"{right_traits_line}
"""

        # ダイアログセクション（3人対応）
        dialogues_yaml = ""
        left_speech = self.story_left_speech_entry.get().strip()
        center_speech = self.story_center_speech_entry.get().strip()
        right_speech = self.story_right_speech_entry.get().strip()

        if left_speech:
            dialogues_yaml += f"""
    - speaker: "Character 1 (Left)"
      text: "{left_speech}"
      shape: "Round (Normal)\""""
        if center_speech:
            dialogues_yaml += f"""
    - speaker: "Character 2 (Center)"
      text: "{center_speech}"
      shape: "Round (Normal)\""""
        if right_speech:
            dialogues_yaml += f"""
    - speaker: "Character 3 (Right)"
      text: "{right_speech}"
      shape: "Round (Normal)\""""

        return f"""# Story Scene Composition (story_scene_composite.yaml準拠)
type: story_scene_composition

{bg_section}

scene_interaction:
  layout_type: "{STORY_LAYOUTS.get(self.story_layout_menu.get(), 'Side by Side (Walking)')}"
  distance: "{STORY_DISTANCE.get(self.story_distance_menu.get(), 'Close Friends')}"
{characters_yaml}
comic_overlay:
  enabled: true
  style: "Slice of Life / Visual Novel"
  narration_box:
    text: "{self.story_narration_entry.get().strip()}"
    position: "Top Left"
  dialogues:{dialogues_yaml}

post_processing:
  filter: "Soft Anime Look"
  bloom_effect: "Low"
{self._generate_text_overlay_yaml()}"""

    def _generate_boss_yaml(self):
        """ボスレイドYAML生成"""
        # パーティメンバーを収集
        members_yaml = ""
        for i, member in enumerate(self.boss_party_entries):
            img = member['image'].get().strip()
            action = member['action'].get().strip() or "Standing"
            if img:
                members_yaml += f"""
    - id: "member_{i + 1}"
      source_image: "{self._get_filename(img)}"
      action: "{action}"
"""

        return f"""# Boss Raid Composition (boss_raid_composition.yaml準拠)
type: boss_raid_composition

boss_character:
  source_image: "{self._get_filename(self.boss_image_entry.get().strip())}"
  placement:
    position_x: "Right Edge (90%)"
    position_y: "Center"
    scale: {self.boss_scale_entry.get().strip() or '2.5'}
    crop_mode: "{'Allow Cropping' if self.boss_crop_var.get() else 'No Crop'}"
  orientation:
    facing: "Down-Left"

party_members:
  base_scale: {self.boss_party_scale_entry.get().strip() or '0.6'}
  members:{members_yaml}

attack_convergence:
  enabled: {str(self.boss_convergence_var.get()).lower()}
  target_point: "Boss Chest/Head"
  beam_effects:
    color: "{self.boss_beam_color_entry.get().strip() or 'Blue & Pink Lasers'}"
    style: "Concentrated Fire"

camera:
  angle: "Low Angle / Dynamic"
{self._generate_text_overlay_yaml()}"""
