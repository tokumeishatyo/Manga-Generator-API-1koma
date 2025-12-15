# -*- coding: utf-8 -*-
"""
1コマ漫画生成アプリ
メインUIモジュール（簡素化版）
"""

import os
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk

# Import constants
from constants import (
    COLOR_MODES, DUOTONE_COLORS, OUTPUT_TYPES, OUTPUT_STYLES, ASPECT_RATIOS,
    STEP_ORDER, STEP_LABELS, STEP_REQUIREMENTS, AGE_EXPRESSION_CONVERSIONS
)


def convert_age_expressions(text: str) -> str:
    """年齢表現を安全な表現に変換（セーフティフィルター対策）"""
    if not text:
        return text
    result = text
    for age_expr, safe_expr in AGE_EXPRESSION_CONVERSIONS.items():
        if age_expr in result:
            result = result.replace(age_expr, safe_expr)
    return result

# Import logic modules
from logic.api_client import generate_image_with_api
from logic.file_manager import (
    load_template, load_recent_files, save_recent_files,
    add_to_recent_files, save_yaml_file, load_yaml_file,
    update_yaml_metadata, add_title_to_image
)

# Import UI windows
from ui.scene_builder_window import SceneBuilderWindow
from ui.character_sheet_window import CharacterSheetWindow
from ui.body_sheet_window import BodySheetWindow
from ui.outfit_window import OutfitWindow
from ui.background_window import BackgroundWindow
from ui.pose_window import PoseWindow
from ui.decorative_text_window import DecorativeTextWindow
from ui.four_panel_window import FourPanelWindow
from ui.manga_composer_window import MangaComposerWindow
from ui.style_transform_window import StyleTransformWindow
from ui.bg_remover_window import BgRemoverWindow

# Set appearance mode and default color theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class MangaGeneratorApp(ctk.CTk):
    """簡素化されたメインアプリケーション"""

    def __init__(self):
        super().__init__()

        # Window configuration
        self.title("1コマ漫画生成アプリ")
        self.geometry("1500x800")

        # Layout configuration - Three column layout
        self.grid_columnconfigure(0, weight=1, minsize=320)  # Left column (settings)
        self.grid_columnconfigure(1, weight=1, minsize=280)  # Middle column (API)
        self.grid_columnconfigure(2, weight=2, minsize=500)  # Right column (preview)
        self.grid_rowconfigure(0, weight=1)

        # Load template
        self.template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "template.yaml")
        self.template_data = load_template(self.template_path)

        # Recent files history
        self.recent_files_path = os.path.join(os.path.dirname(__file__), "recent_files.json")
        self.recent_files = load_recent_files(self.recent_files_path)

        # Current settings data (from settings windows)
        self.current_settings = {}

        # 進捗トラッカー: 各ステップの完了状態と生成画像パス
        self.step_progress = {
            step: {"completed": False, "image_path": None}
            for step in STEP_ORDER
        }

        # Build UI
        self._build_left_column()
        self._build_middle_column()
        self._build_right_column()

        # Initial update
        self._on_output_type_change(None)

    def _build_left_column(self):
        """左列を構築（基本設定）"""
        self.left_column = ctk.CTkFrame(self)
        self.left_column.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")
        self.left_column.grid_columnconfigure(0, weight=1)
        self.left_column.grid_rowconfigure(0, weight=1)  # Scrollable frame expands

        # Create scrollable frame
        self.left_scroll = ctk.CTkScrollableFrame(self.left_column)
        self.left_scroll.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.left_scroll.grid_columnconfigure(0, weight=1)

        row = 0

        # === 出力タイプ選択 ===
        type_frame = ctk.CTkFrame(self.left_scroll)
        type_frame.grid(row=row, column=0, padx=5, pady=5, sticky="ew")
        row += 1

        ctk.CTkLabel(
            type_frame,
            text="出力タイプ",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 5), sticky="w")

        # タイプ選択と詳細設定を1行に
        ctk.CTkLabel(type_frame, text="タイプ:").grid(row=1, column=0, padx=(10, 2), pady=5, sticky="w")
        self.output_type_menu = ctk.CTkOptionMenu(
            type_frame,
            values=list(OUTPUT_TYPES.keys()),
            width=200,
            command=self._on_output_type_change
        )
        self.output_type_menu.set("Step1: 顔三面図")
        self.output_type_menu.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        self.settings_button = ctk.CTkButton(
            type_frame,
            text="詳細設定...",
            width=100,
            command=self._open_settings_window
        )
        self.settings_button.grid(row=1, column=2, padx=(5, 10), pady=5, sticky="w")

        # 設定状態表示
        self.settings_status_label = ctk.CTkLabel(
            type_frame,
            text="設定: 未設定",
            font=("Arial", 11),
            text_color="gray"
        )
        self.settings_status_label.grid(row=2, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="w")

        # === 進捗トラッカー ===
        progress_frame = ctk.CTkFrame(self.left_scroll)
        progress_frame.grid(row=row, column=0, padx=5, pady=5, sticky="ew")
        progress_frame.grid_columnconfigure(0, weight=1)
        row += 1

        ctk.CTkLabel(
            progress_frame,
            text="ワークフロー進捗",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        # 進捗表示用のラベルを格納
        self.progress_labels = {}
        for i, step_key in enumerate(STEP_ORDER):
            step_label = STEP_LABELS.get(step_key, step_key)
            label = ctk.CTkLabel(
                progress_frame,
                text=f"⬜ {step_label}",
                font=("Arial", 11),
                text_color="gray"
            )
            label.grid(row=i + 1, column=0, padx=15, pady=1, sticky="w")
            self.progress_labels[step_key] = label

        # 進捗リセットボタン
        self.progress_reset_btn = ctk.CTkButton(
            progress_frame,
            text="進捗リセット",
            width=100,
            height=25,
            fg_color="gray",
            hover_color="darkgray",
            command=self._reset_progress
        )
        self.progress_reset_btn.grid(row=len(STEP_ORDER) + 1, column=0, padx=10, pady=(5, 10), sticky="w")

        # === スタイル設定 ===
        style_frame = ctk.CTkFrame(self.left_scroll)
        style_frame.grid(row=row, column=0, padx=5, pady=5, sticky="ew")
        style_frame.grid_columnconfigure(1, weight=1)
        row += 1

        ctk.CTkLabel(
            style_frame,
            text="スタイル設定",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        # カラーモード
        ctk.CTkLabel(style_frame, text="カラーモード:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        color_frame = ctk.CTkFrame(style_frame, fg_color="transparent")
        color_frame.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        self.color_mode_menu = ctk.CTkOptionMenu(
            color_frame,
            values=list(COLOR_MODES.keys()),
            width=120,
            command=self._on_color_mode_change
        )
        self.color_mode_menu.set("フルカラー")
        self.color_mode_menu.pack(side="left", padx=(0, 10))

        self.duotone_color_menu = ctk.CTkOptionMenu(
            color_frame,
            values=list(DUOTONE_COLORS.keys()),
            width=100
        )
        self.duotone_color_menu.set("青")
        self.duotone_color_menu.pack(side="left")
        self.duotone_color_menu.pack_forget()  # Initially hidden

        # スタイル
        ctk.CTkLabel(style_frame, text="スタイル:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.output_style_menu = ctk.CTkOptionMenu(
            style_frame,
            values=list(OUTPUT_STYLES.keys()),
            width=150
        )
        self.output_style_menu.set("アニメ調")
        self.output_style_menu.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        # アスペクト比
        ctk.CTkLabel(style_frame, text="アスペクト比:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.aspect_ratio_menu = ctk.CTkOptionMenu(
            style_frame,
            values=list(ASPECT_RATIOS.keys()),
            width=150
        )
        self.aspect_ratio_menu.set("1:1（正方形）")
        self.aspect_ratio_menu.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        # === 基本情報 ===
        info_frame = ctk.CTkFrame(self.left_scroll)
        info_frame.grid(row=row, column=0, padx=5, pady=5, sticky="ew")
        info_frame.grid_columnconfigure(1, weight=1)
        row += 1

        ctk.CTkLabel(
            info_frame,
            text="基本情報",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 5), sticky="w")

        # タイトル（必須）
        ctk.CTkLabel(info_frame, text="タイトル:").grid(row=1, column=0, padx=10, pady=5, sticky="w")

        title_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        title_frame.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        title_frame.grid_columnconfigure(0, weight=1)

        self.title_entry = ctk.CTkEntry(title_frame, placeholder_text="作品タイトル（必須）")
        self.title_entry.grid(row=0, column=0, sticky="ew")

        # 画像にタイトルを入れるチェックボックス
        self.include_title_var = tk.BooleanVar(value=False)
        self.include_title_checkbox = ctk.CTkCheckBox(
            title_frame,
            text="画像にタイトルを入れる",
            variable=self.include_title_var,
            width=160
        )
        self.include_title_checkbox.grid(row=0, column=1, padx=(10, 0), sticky="w")

        ctk.CTkLabel(info_frame, text="作者名:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.author_entry = ctk.CTkEntry(info_frame, placeholder_text="Unknown")
        self.author_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        # === 生成ボタン・リセットボタン ===
        button_frame = ctk.CTkFrame(self.left_scroll)
        button_frame.grid(row=row, column=0, padx=5, pady=10, sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        row += 1

        # 生成ボタンとリセットボタンを横並び
        main_button_frame = ctk.CTkFrame(button_frame, fg_color="transparent")
        main_button_frame.pack(fill="x", padx=10, pady=10)
        main_button_frame.grid_columnconfigure(0, weight=1)
        main_button_frame.grid_columnconfigure(1, weight=1)

        self.generate_button = ctk.CTkButton(
            main_button_frame,
            text="YAML生成",
            font=("Arial", 14, "bold"),
            height=40,
            command=self._generate_yaml
        )
        self.generate_button.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        self.reset_button = ctk.CTkButton(
            main_button_frame,
            text="リセット",
            font=("Arial", 14, "bold"),
            height=40,
            fg_color="gray",
            hover_color="darkgray",
            command=self._reset_all
        )
        self.reset_button.grid(row=0, column=1, padx=(5, 0), sticky="ew")

        # シーンビルダーボタン
        self.scene_builder_button = ctk.CTkButton(
            button_frame,
            text="シーンビルダーを開く",
            height=35,
            command=self._open_scene_builder
        )
        self.scene_builder_button.pack(fill="x", padx=10, pady=(0, 5))

        # 漫画ページコンポーザーボタン
        self.manga_composer_button = ctk.CTkButton(
            button_frame,
            text="漫画ページコンポーザー",
            height=35,
            fg_color="#6B4C9A",
            hover_color="#5A3D89",
            command=self._open_manga_composer
        )
        self.manga_composer_button.pack(fill="x", padx=10, pady=(0, 5))

        # 画像ツールボタン
        self.image_tools_button = ctk.CTkButton(
            button_frame,
            text="画像ツール（背景透過）",
            height=35,
            fg_color="#4A7C59",
            hover_color="#3A6C49",
            command=self._open_bg_remover
        )
        self.image_tools_button.pack(fill="x", padx=10, pady=(0, 10))

    def _build_middle_column(self):
        """中列を構築（API設定）"""
        self.middle_column = ctk.CTkFrame(self)
        self.middle_column.grid(row=0, column=1, padx=5, pady=10, sticky="nsew")
        self.middle_column.grid_columnconfigure(0, weight=1)
        self.middle_column.grid_rowconfigure(0, weight=1)

        # Create scrollable frame
        self.middle_scroll = ctk.CTkScrollableFrame(self.middle_column)
        self.middle_scroll.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.middle_scroll.grid_columnconfigure(0, weight=1)

        # === API設定 ===
        api_frame = ctk.CTkFrame(self.middle_scroll)
        api_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        api_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            api_frame,
            text="API設定",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        # 出力モード
        ctk.CTkLabel(api_frame, text="出力モード:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        mode_frame = ctk.CTkFrame(api_frame, fg_color="transparent")
        mode_frame.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        self.output_mode_var = tk.StringVar(value="yaml")
        self.output_mode_var.trace_add("write", self._on_output_mode_change)

        ctk.CTkRadioButton(
            mode_frame,
            text="YAML出力",
            variable=self.output_mode_var,
            value="yaml"
        ).pack(side="left", padx=(0, 10))

        ctk.CTkRadioButton(
            mode_frame,
            text="画像出力(API)",
            variable=self.output_mode_var,
            value="api"
        ).pack(side="left")

        # API Key
        ctk.CTkLabel(api_frame, text="API Key:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        api_key_frame = ctk.CTkFrame(api_frame, fg_color="transparent")
        api_key_frame.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        api_key_frame.grid_columnconfigure(0, weight=1)

        self.api_key_entry = ctk.CTkEntry(api_key_frame, placeholder_text="Google AI API Key", show="*", state="disabled")
        self.api_key_entry.grid(row=0, column=0, sticky="ew")

        self.api_key_clear_btn = ctk.CTkButton(
            api_key_frame,
            text="×",
            width=28,
            height=28,
            font=("Arial", 14),
            fg_color="gray",
            hover_color="darkgray",
            state="disabled",
            command=self._clear_api_key
        )
        self.api_key_clear_btn.grid(row=0, column=1, padx=(5, 0))

        # APIモード
        ctk.CTkLabel(api_frame, text="APIモード:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        api_submode_frame = ctk.CTkFrame(api_frame, fg_color="transparent")
        api_submode_frame.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        self.api_submode_var = tk.StringVar(value="normal")
        self.api_submode_var.trace_add("write", self._on_api_submode_change)

        self.api_normal_radio = ctk.CTkRadioButton(
            api_submode_frame,
            text="通常",
            variable=self.api_submode_var,
            value="normal",
            state="disabled"
        )
        self.api_normal_radio.pack(side="left", padx=(0, 10))

        self.api_redraw_radio = ctk.CTkRadioButton(
            api_submode_frame,
            text="参考画像清書",
            variable=self.api_submode_var,
            value="redraw",
            state="disabled"
        )
        self.api_redraw_radio.pack(side="left")

        # 参考画像
        ctk.CTkLabel(api_frame, text="参考画像:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        ref_frame = ctk.CTkFrame(api_frame, fg_color="transparent")
        ref_frame.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
        ref_frame.grid_columnconfigure(0, weight=1)

        self.ref_image_entry = ctk.CTkEntry(ref_frame, placeholder_text="下書き画像", state="disabled")
        self.ref_image_entry.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        self.ref_image_browse = ctk.CTkButton(
            ref_frame,
            text="参照",
            width=50,
            state="disabled",
            command=self._browse_ref_image
        )
        self.ref_image_browse.grid(row=0, column=1)

        # 解像度設定
        ctk.CTkLabel(api_frame, text="解像度:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        resolution_frame = ctk.CTkFrame(api_frame, fg_color="transparent")
        resolution_frame.grid(row=5, column=1, padx=10, pady=5, sticky="w")

        self.resolution_var = tk.StringVar(value="2K")
        self.resolution_1k_radio = ctk.CTkRadioButton(
            resolution_frame,
            text="1K",
            variable=self.resolution_var,
            value="1K",
            state="disabled"
        )
        self.resolution_1k_radio.pack(side="left", padx=(0, 10))

        self.resolution_2k_radio = ctk.CTkRadioButton(
            resolution_frame,
            text="2K",
            variable=self.resolution_var,
            value="2K",
            state="disabled"
        )
        self.resolution_2k_radio.pack(side="left", padx=(0, 10))

        self.resolution_4k_radio = ctk.CTkRadioButton(
            resolution_frame,
            text="4K",
            variable=self.resolution_var,
            value="4K",
            state="disabled"
        )
        self.resolution_4k_radio.pack(side="left")

    def _build_right_column(self):
        """右列を構築（YAML/画像プレビュー）"""
        self.right_column = ctk.CTkFrame(self)
        self.right_column.grid(row=0, column=2, padx=(5, 10), pady=10, sticky="nsew")
        self.right_column.grid_columnconfigure(0, weight=1)
        self.right_column.grid_rowconfigure(1, weight=1)

        # === YAMLプレビュー ===
        yaml_frame = ctk.CTkFrame(self.right_column)
        yaml_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        yaml_frame.grid_columnconfigure(0, weight=1)
        yaml_frame.grid_rowconfigure(1, weight=1)
        self.right_column.grid_rowconfigure(0, weight=1)  # YAMLプレビュー（小さめ）

        # ヘッダー
        header_frame = ctk.CTkFrame(yaml_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        header_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header_frame,
            text="YAMLプレビュー",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, sticky="w")

        # ボタン
        btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_frame.grid(row=0, column=1, sticky="e")

        ctk.CTkButton(
            btn_frame,
            text="コピー",
            width=60,
            command=self._copy_yaml
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            btn_frame,
            text="保存",
            width=60,
            command=self._save_yaml
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            btn_frame,
            text="読込",
            width=60,
            command=self._load_yaml
        ).pack(side="left", padx=2)

        # YAMLテキストボックス
        self.yaml_textbox = ctk.CTkTextbox(yaml_frame, font=("Consolas", 11))
        self.yaml_textbox.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # === 画像プレビュー ===
        preview_frame = ctk.CTkFrame(self.right_column)
        preview_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        preview_frame.grid_columnconfigure(0, weight=1)
        preview_frame.grid_rowconfigure(1, weight=1)
        self.right_column.grid_rowconfigure(1, weight=3)  # 画像プレビュー（大きめ）

        ctk.CTkLabel(
            preview_frame,
            text="画像プレビュー",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        self.preview_label = ctk.CTkLabel(
            preview_frame,
            text="画像生成後に表示されます",
            font=("Arial", 12),
            text_color="gray"
        )
        self.preview_label.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # 画像保存ボタン
        self.save_image_button = ctk.CTkButton(
            preview_frame,
            text="画像を保存",
            state="disabled",
            command=self._save_image
        )
        self.save_image_button.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        # Generated image storage
        self.generated_image = None
        self._image_generated_by_api = False  # API生成フラグ

        # 進捗表示用タイマー
        self._generation_start_time = None
        self._progress_timer_id = None

        # 最後に保存したYAMLファイルのパス（メタデータ連携用）
        self.last_saved_yaml_path = None

    # === Event Handlers ===

    def _reset_all(self):
        """すべての入力をリセットして起動直後の状態に戻す"""
        # 確認ダイアログ
        if not messagebox.askyesno("確認", "すべての入力をリセットしますか？"):
            return

        # 出力タイプをデフォルトに
        self.output_type_menu.set("キャラデザイン（全身）")

        # スタイル設定をデフォルトに
        self.color_mode_menu.set("フルカラー")
        self.duotone_color_menu.set("青")
        self.duotone_color_menu.pack_forget()
        self.output_style_menu.set("アニメ調")
        self.aspect_ratio_menu.set("1:1（正方形）")

        # 基本情報をクリア
        self.title_entry.delete(0, tk.END)
        self.include_title_var.set(False)
        self.author_entry.delete(0, tk.END)

        # API設定をデフォルトに（APIキーは保持）
        self.output_mode_var.set("yaml")
        # APIキーは明示的に「×」ボタンでクリアしない限り保持
        self.api_submode_var.set("normal")
        self.ref_image_entry.configure(state="normal")
        self.ref_image_entry.delete(0, tk.END)
        self.ref_image_entry.configure(state="disabled")
        self.resolution_var.set("2K")

        # 詳細設定をクリア
        self.current_settings = {}
        self.settings_status_label.configure(text="設定: 未設定", text_color="gray")

        # YAMLプレビューをクリア
        self.yaml_textbox.delete("1.0", tk.END)

        # 画像プレビューをクリア
        self.generated_image = None
        self._image_generated_by_api = False
        self.preview_label.configure(text="画像生成後に表示されます", image=None)
        self.save_image_button.configure(state="disabled")

        # ファイルパスをクリア
        self.last_saved_yaml_path = None

        # ボタンをデフォルトに
        self.generate_button.configure(text="YAML生成", state="normal")

    def _on_output_type_change(self, value):
        """出力タイプ変更時"""
        # 設定をリセット
        self.current_settings = {}
        self.settings_status_label.configure(text="設定: 未設定", text_color="gray")
        # 進捗表示を更新
        self._update_progress_display()

    def _on_color_mode_change(self, value):
        """カラーモード変更時"""
        if value == "2色刷り":
            self.duotone_color_menu.pack(side="left")
        else:
            self.duotone_color_menu.pack_forget()

    def _on_output_mode_change(self, *args):
        """出力モード変更時（APIキーは保持する）"""
        mode = self.output_mode_var.get()
        if mode == "api":
            self.api_key_entry.configure(state="normal")
            self.api_key_clear_btn.configure(state="normal")
            self.api_normal_radio.configure(state="normal")
            self.api_redraw_radio.configure(state="normal")
            self.ref_image_entry.configure(state="normal")
            self.ref_image_browse.configure(state="normal")
            self.resolution_1k_radio.configure(state="normal")
            self.resolution_2k_radio.configure(state="normal")
            self.resolution_4k_radio.configure(state="normal")
            self.generate_button.configure(text="画像生成")
            # APIサブモードに応じて詳細設定ボタンの状態を更新
            self._on_api_submode_change()
        else:
            # APIキーの値は保持したまま、入力を無効化
            self.api_key_entry.configure(state="disabled")
            self.api_key_clear_btn.configure(state="disabled")
            self.api_normal_radio.configure(state="disabled")
            self.api_redraw_radio.configure(state="disabled")
            self.ref_image_entry.configure(state="disabled")
            self.ref_image_browse.configure(state="disabled")
            self.resolution_1k_radio.configure(state="disabled")
            self.resolution_2k_radio.configure(state="disabled")
            self.resolution_4k_radio.configure(state="disabled")
            self.generate_button.configure(text="YAML生成")
            # YAML出力モードでは詳細設定ボタンを有効化
            self.settings_button.configure(state="normal")
            # 設定状態ラベルを更新
            if self.current_settings:
                self.settings_status_label.configure(text="設定: 設定済み ✓", text_color="green")
            else:
                self.settings_status_label.configure(text="設定: 未設定", text_color="gray")

    def _clear_api_key(self):
        """APIキーをクリア"""
        self.api_key_entry.delete(0, tk.END)

    def _on_api_submode_change(self, *args):
        """APIサブモード変更時（通常/清書切替）"""
        if self.output_mode_var.get() != "api":
            return

        submode = self.api_submode_var.get()
        if submode == "redraw":
            # 清書モード：詳細設定不要だが、YAML読込が必要
            self.settings_button.configure(state="disabled")
            self.settings_status_label.configure(
                text="清書モード: YAML読込+参照画像が必要",
                text_color="blue"
            )
        else:
            # 通常モード：詳細設定必要
            self.settings_button.configure(state="normal")
            if self.current_settings:
                self.settings_status_label.configure(
                    text="設定: 設定済み ✓",
                    text_color="green"
                )
            else:
                self.settings_status_label.configure(
                    text="設定: 未設定",
                    text_color="gray"
                )

    def _browse_ref_image(self):
        """参考画像参照"""
        filename = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]
        )
        if filename:
            self.ref_image_entry.configure(state="normal")
            self.ref_image_entry.delete(0, tk.END)
            self.ref_image_entry.insert(0, filename)

    # === Settings Window ===

    def _open_settings_window(self):
        """詳細設定ウィンドウを開く"""
        output_type = self.output_type_menu.get()

        # === キャラクター生成フェーズ ===
        if output_type == "Step1: 顔三面図":
            CharacterSheetWindow(
                self,
                sheet_type="face",
                callback=self._on_settings_complete,
                initial_data=self.current_settings
            )
        elif output_type == "Step2: 素体三面図":
            # Step1の出力画像を取得
            face_sheet_path = self._get_previous_step_image("step2_body")
            BodySheetWindow(
                self,
                callback=self._on_settings_complete,
                initial_data=self.current_settings,
                face_sheet_path=face_sheet_path
            )
        elif output_type == "Step3: 衣装着用":
            # Step2の出力画像を取得
            body_sheet_path = self._get_previous_step_image("step3_outfit")
            OutfitWindow(
                self,
                callback=self._on_settings_complete,
                initial_data=self.current_settings,
                body_sheet_path=body_sheet_path
            )
        # === ポーズ生成フェーズ ===
        elif output_type == "Step4: ポーズ":
            outfit_sheet_path = self._get_previous_step_image("step3_outfit")
            PoseWindow(
                self,
                callback=self._on_settings_complete,
                initial_data=self.current_settings,
                outfit_sheet_path=outfit_sheet_path
            )
        # === その他 ===
        elif output_type == "背景生成":
            BackgroundWindow(
                self,
                callback=self._on_settings_complete,
                initial_data=self.current_settings
            )
        elif output_type == "装飾テキスト":
            DecorativeTextWindow(
                self,
                callback=self._on_settings_complete,
                initial_data=self.current_settings
            )
        elif output_type == "4コマ漫画":
            FourPanelWindow(
                self,
                callback=self._on_settings_complete,
                initial_data=self.current_settings
            )
        elif output_type == "スタイル変換":
            StyleTransformWindow(
                self,
                callback=self._on_settings_complete,
                initial_data=self.current_settings
            )
        else:
            messagebox.showinfo("情報", f"'{output_type}'の設定ウィンドウは未実装です")

    def _on_settings_complete(self, data: dict):
        """設定完了時のコールバック"""
        self.current_settings = data
        self.settings_status_label.configure(text="設定: 設定済み ✓", text_color="green")

    # === 進捗トラッカー ===

    def _reset_progress(self):
        """進捗をリセット"""
        if messagebox.askyesno("確認", "すべての進捗をリセットしますか？"):
            self.step_progress = {
                step: {"completed": False, "image_path": None}
                for step in STEP_ORDER
            }
            self._update_progress_display()

    def _update_progress_display(self):
        """進捗表示を更新"""
        for step_key, label in self.progress_labels.items():
            step_label = STEP_LABELS.get(step_key, step_key)
            progress = self.step_progress.get(step_key, {})

            if progress.get("completed"):
                label.configure(text=f"✅ {step_label}", text_color="green")
            else:
                # 前のステップが完了しているか確認
                req_step = STEP_REQUIREMENTS.get(step_key)
                if req_step is None or self.step_progress.get(req_step, {}).get("completed"):
                    # このステップは実行可能
                    label.configure(text=f"🔄 {step_label}", text_color="orange")
                else:
                    # 前のステップが未完了
                    label.configure(text=f"⬜ {step_label}", text_color="gray")

    def _mark_step_complete(self, step_key: str, image_path: str = None):
        """ステップを完了としてマーク"""
        if step_key in self.step_progress:
            self.step_progress[step_key]["completed"] = True
            self.step_progress[step_key]["image_path"] = image_path
            self._update_progress_display()

    def _get_previous_step_image(self, step_key: str) -> str:
        """前のステップの画像パスを取得"""
        req_step = STEP_REQUIREMENTS.get(step_key)
        if req_step and self.step_progress.get(req_step, {}).get("completed"):
            return self.step_progress[req_step].get("image_path")
        return None

    # === YAML Generation ===

    def _generate_yaml(self):
        """YAML生成"""
        # 清書モードの場合は専用処理
        if (self.output_mode_var.get() == "api" and
            self.api_submode_var.get() == "redraw"):
            self._generate_redraw_image()
            return

        output_type = self.output_type_menu.get()

        # タイトル必須チェック
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning("警告", "タイトルを入力してください")
            self.title_entry.focus_set()
            return

        # 設定チェック（通常モードのみ）
        if not self.current_settings:
            messagebox.showwarning("警告", "詳細設定を行ってください")
            return

        # 共通パラメータ
        color_mode = self.color_mode_menu.get()
        duotone_color = self.duotone_color_menu.get() if color_mode == "2色刷り" else None
        output_style = self.output_style_menu.get()
        aspect_ratio = self.aspect_ratio_menu.get()
        include_title_in_image = self.include_title_var.get()
        author = self.author_entry.get().strip() or "Unknown"

        try:
            # === キャラクター生成フェーズ ===
            if output_type == "Step1: 顔三面図":
                yaml_content = self._generate_character_sheet_yaml(
                    color_mode, duotone_color, output_style, aspect_ratio, title, author, include_title_in_image
                )
            elif output_type == "Step2: 素体三面図":
                yaml_content = self._generate_body_sheet_yaml(
                    color_mode, duotone_color, output_style, aspect_ratio, title, author, include_title_in_image
                )
            elif output_type == "Step3: 衣装着用":
                yaml_content = self._generate_outfit_yaml(
                    color_mode, duotone_color, output_style, aspect_ratio, title, author, include_title_in_image
                )
            # === ポーズ生成フェーズ ===
            elif output_type == "Step4: ポーズ":
                yaml_content = self._generate_pose_yaml(
                    color_mode, duotone_color, output_style, aspect_ratio, title, author, include_title_in_image
                )
            # === その他 ===
            elif output_type == "背景生成":
                yaml_content = self._generate_background_yaml(
                    color_mode, duotone_color, output_style, aspect_ratio, title, author, include_title_in_image
                )
            elif output_type == "装飾テキスト":
                yaml_content = self._generate_decorative_yaml(
                    color_mode, duotone_color, output_style, aspect_ratio, title, author, include_title_in_image
                )
            elif output_type == "4コマ漫画":
                yaml_content = self._generate_four_panel_yaml(
                    color_mode, duotone_color, output_style, title, author, include_title_in_image
                )
            elif output_type == "スタイル変換":
                yaml_content = self._generate_style_transform_yaml(
                    color_mode, duotone_color, output_style, aspect_ratio, title, author, include_title_in_image
                )
            else:
                yaml_content = f"# {output_type} - 未実装"

            # YAMLをプレビューに表示
            self.yaml_textbox.delete("1.0", tk.END)
            self.yaml_textbox.insert("1.0", yaml_content)

            # API出力モードの場合は画像生成
            if self.output_mode_var.get() == "api":
                self._generate_image_with_api(yaml_content)

        except Exception as e:
            messagebox.showerror("エラー", f"YAML生成中にエラーが発生しました:\n{str(e)}")

    def _generate_character_sheet_yaml(self, color_mode, duotone_color, output_style, aspect_ratio, title, author, include_title_in_image):
        """三面図用YAML生成（character_basic.yaml準拠）"""
        settings = self.current_settings
        from constants import CHARACTER_STYLES

        sheet_type = settings.get('sheet_type', 'fullbody')

        # 基本情報
        name = settings.get('name', '')
        description = convert_age_expressions(settings.get('description', ''))  # 年齢表現を安全に変換
        image_path = settings.get('image_path', '')
        character_style = settings.get('character_style', '標準アニメ')

        # スタイル情報取得
        style_info = CHARACTER_STYLES.get(character_style, CHARACTER_STYLES['標準アニメ'])
        style_prompt = style_info.get('style', '')
        proportions = style_info.get('proportions', '')
        style_description = style_info.get('description', '')

        # 服装情報（全身三面図のみ）
        outfit = settings.get('outfit', {})
        outfit_prompt = ""
        if sheet_type == "fullbody" and outfit:
            from logic.character import generate_outfit_prompt
            outfit_prompt = generate_outfit_prompt(
                outfit.get('category', 'おまかせ'),
                outfit.get('shape', 'おまかせ'),
                outfit.get('color', 'おまかせ'),
                outfit.get('pattern', 'おまかせ'),
                outfit.get('style', 'おまかせ')
            )

        # YAMLテンプレート生成
        sheet_label = "full body character reference sheet" if sheet_type == "fullbody" else "face character reference sheet"

        # 顔三面図専用の指示（素体ヘッドショット・三角形配置）
        face_headshot_instruction = ""
        if sheet_type == "face":
            face_headshot_instruction = """
# ====================================================
# IMPORTANT: Face Reference Sheet Layout
# ====================================================
# Layout: Triangular arrangement (inverted triangle)
#
#   [FRONT VIEW]     [3/4 LEFT VIEW]
#         [LEFT PROFILE]
#
# All views facing LEFT direction for consistency
# ====================================================

layout:
  arrangement: "triangular, inverted triangle formation"
  direction: "all views facing LEFT"
  top_row:
    - position: "top-left"
      view: "front view, facing directly at camera, eyes looking at viewer"
    - position: "top-right"
      view: "3/4 left view, head turned 45 degrees to the left, showing left side of face"
  bottom_row:
    - position: "bottom-center"
      view: "left profile, pure side view facing left, showing only left side of face"

headshot_specification:
  type: "Character design base body (sotai) headshot for reference sheet"
  coverage: "From top of head to base of neck (around collarbone level)"
  clothing: "NONE - Do not include any clothing or accessories"
  accessories: "NONE - No jewelry, headwear, or decorations"
  state: "Clean base body state only"
  background: "Pure white background, seamless"
  purpose: "Professional character design reference for commercial use - product catalogs, instruction manuals, educational materials, corporate training. This is legitimate business artwork, NOT inappropriate content."
"""

        yaml_content = f"""# {sheet_label.title()} (character_basic.yaml準拠)
type: character_design
title: "{title or name + ' Reference Sheet'}"
author: "{author}"

output_type: "{sheet_label}"
{face_headshot_instruction}
character:
  name: "{name}"
  description: "{description}"
  outfit: "{outfit_prompt if sheet_type == 'fullbody' else 'NONE - bare skin only, no clothing'}"
  expression: "neutral expression{', standing at attention' if sheet_type == 'fullbody' else ''}"

character_style:
  style: "{style_prompt}"
  proportions: "{proportions}"
  style_description: "{style_description}"

# ====================================================
# Output Specifications
# ====================================================
output:
  format: "reference sheet with multiple views"
  views: "{'front view, side view, back view' if sheet_type == 'fullbody' else 'front view, 3/4 view, side profile'}"
  background: "pure white, clean, seamless, no borders"
  text_overlay: "NONE - absolutely no text, labels, or titles on the image"

# ====================================================
# Constraints (Critical)
# ====================================================
constraints:
  layout:
    - "{'Triangular arrangement: front view top-left, 3/4 left view top-right, left profile bottom-center' if sheet_type == 'face' else 'Horizontal row with STRICT order: LEFT=front view, CENTER=left side view, RIGHT=back view'}"
    - "{'All angled views must face LEFT direction' if sheet_type == 'face' else 'Side view MUST show LEFT side of body (character facing left)'}"
    - "Each view should be clearly separated with white space"
    - "All views same size and scale"
    - "{'POSITION ORDER IS CRITICAL: Front view on LEFT, Side view in CENTER, Back view on RIGHT' if sheet_type == 'fullbody' else ''}"
  design:
    - "Maintain consistent design across all views"
    - "Pure white background for clarity"
    - "Clean linework suitable for reference"
{'''  face_specific:
    - "HEAD/FACE ONLY - show from top of head to neck/collarbone"
    - "Do NOT draw any clothing, accessories, or decorations"
    - "Keep the character in clean base body state"
    - "Neutral expression, emotionless"
    - "3/4 view: head turned 45 degrees to the LEFT"
    - "Profile view: pure side view facing LEFT"''' if sheet_type == 'face' else ''}

# ====================================================
# Anti-Hallucination (MUST FOLLOW)
# ====================================================
anti_hallucination:
  - "Do NOT add any text or labels to the image"
  - "Do NOT include character names on the image"
  - "Do NOT add view labels like 'FRONT VIEW' or 'SIDE VIEW'"
  - "Do NOT add borders or frames around views"
  - "Do NOT add any decorative elements"
  - "Output ONLY the character views on white background"

style:
  color_mode: "{COLOR_MODES.get(color_mode, ('fullcolor', ''))[0]}"
  output_style: "{OUTPUT_STYLES.get(output_style, '')}"
  aspect_ratio: "{'1:1' if sheet_type == 'face' else '16:9'}"  # 顔三面図は1:1、全身三面図は16:9固定
"""

        # タイトルオーバーレイ（有効な場合のみ出力）
        if include_title_in_image:
            yaml_content += f"""
title_overlay:
  enabled: true
  text: "{title}"
  position: "top-left"
"""

        if image_path:
            yaml_content += f'\nreference_image: "{os.path.basename(image_path)}"'

        return yaml_content

    def _generate_body_sheet_yaml(self, color_mode, duotone_color, output_style, aspect_ratio, title, author, include_title_in_image):
        """素体三面図用YAML生成（Step2）"""
        settings = self.current_settings
        from constants import BODY_TYPE_PRESETS, BODY_RENDER_TYPES, CHARACTER_STYLES, BUST_FEATURES

        face_sheet_path = settings.get('face_sheet_path', '')
        body_type = settings.get('body_type', '標準体型（女性）')
        bust_feature = settings.get('bust_feature', 'おまかせ')
        render_type = settings.get('render_type', '素体（白レオタード）')
        character_style = settings.get('character_style', '標準アニメ')
        additional_desc = convert_age_expressions(settings.get('additional_description', ''))  # 年齢表現を安全に変換

        # プリセット情報取得
        body_preset = BODY_TYPE_PRESETS.get(body_type, BODY_TYPE_PRESETS['標準体型（女性）'])
        bust_preset = BUST_FEATURES.get(bust_feature, BUST_FEATURES['おまかせ'])
        render_preset = BODY_RENDER_TYPES.get(render_type, BODY_RENDER_TYPES['素体（白レオタード）'])
        style_info = CHARACTER_STYLES.get(character_style, CHARACTER_STYLES['標準アニメ'])

        # バスト特徴のプロンプト
        bust_prompt = bust_preset.get('prompt', '')

        yaml_content = f"""# Step 2: Body Reference Sheet (素体三面図)
# Purpose: Professional character design reference for commercial use
# Usage: Product catalogs, instruction manuals, educational materials, corporate training
# Note: This is legitimate business artwork, NOT inappropriate content
type: body_reference_sheet
title: "{title or 'Body Reference Sheet'}"
author: "{author}"

# ====================================================
# Input: Face Sheet from Step 1
# ====================================================
input:
  face_sheet: "{os.path.basename(face_sheet_path) if face_sheet_path else 'REQUIRED'}"
  preserve_face: true
  preserve_face_details: "exact match required - do not alter facial features"

# ====================================================
# Body Configuration
# ====================================================
body:
  type: "{body_type}"
  description: "{body_preset.get('description', '')}"
  height: "{body_preset.get('height', 'average')}"
  build: "{body_preset.get('build', 'normal')}"
  gender: "{body_preset.get('gender', 'neutral')}"
{f'  figure_style: "{bust_prompt}"' if bust_prompt else ''}
{f'  additional_notes: "{additional_desc}"' if additional_desc else ''}

# ====================================================
# Render Type
# ====================================================
render:
  type: "{render_type}"
  style: "{render_preset.get('prompt', '')}"
  clothing: "NONE - this is a base body reference"

# ====================================================
# Output Format
# ====================================================
output:
  format: "three view reference sheet"
  views:
    - "front view, facing directly at camera"
    - "left side view, profile facing left"
    - "back view"
  pose: "attention pose (kiwotsuke), standing straight, arms at sides, heels together"
  background: "pure white, clean, seamless"
  text_overlay: "NONE - no text or labels on the image"

# ====================================================
# Style Settings
# ====================================================
style:
  character_style: "{style_info.get('style', '')}"
  proportions: "{style_info.get('proportions', '')}"
  color_mode: "{COLOR_MODES.get(color_mode, 'full_color')}"
  output_style: "{OUTPUT_STYLES.get(output_style, 'anime')}"
  aspect_ratio: "16:9"  # 素体三面図は16:9固定

# ====================================================
# Constraints (Critical)
# ====================================================
constraints:
  layout:
    - "STRICT horizontal arrangement: LEFT=front view, CENTER=left side view, RIGHT=back view"
    - "Side view MUST show LEFT side of body (character facing left)"
    - "POSITION ORDER IS CRITICAL: Front on LEFT, Side in CENTER, Back on RIGHT"
    - "Each view should be clearly separated with white space"
  face_preservation:
    - "MUST use exact face from input face_sheet"
    - "Do NOT alter facial features, expression, or proportions"
    - "Maintain exact hair style and color from reference"
  body_generation:
    - "Generate body matching the specified body type"
    - "Do NOT add any clothing or accessories beyond specified render type"
    - "Maintain anatomically correct proportions"
  pose:
    - "Attention pose (kiwotsuke): standing straight with arms at sides"
    - "Heels together, toes slightly apart"
    - "Arms relaxed at sides, palms facing inward"
    - "Do NOT use T-pose or A-pose"
  consistency:
    - "All three views must show the same character in same pose"
    - "Maintain consistent proportions across views"
    - "Use clean linework suitable for reference"

anti_hallucination:
  - "Do NOT add clothing that was not specified"
  - "Do NOT change the face from the reference"
  - "Do NOT add accessories or decorations"
  - "Do NOT change body proportions from specified type"
  - "Do NOT add any text or labels to the image"
  - "Do NOT use T-pose or A-pose - use attention pose only"
  - "Do NOT change the view order - ALWAYS front/side/back from left to right"
"""

        if include_title_in_image:
            yaml_content += f"""
title_overlay:
  enabled: true
  text: "{title}"
  position: "top-left"
"""

        return yaml_content

    def _generate_outfit_yaml(self, color_mode, duotone_color, output_style, aspect_ratio, title, author, include_title_in_image):
        """衣装着用用YAML生成（Step3）"""
        settings = self.current_settings
        from constants import OUTFIT_DATA, CHARACTER_STYLES
        from logic.character import generate_outfit_prompt

        body_sheet_path = settings.get('body_sheet_path', '')
        outfit_source = settings.get('outfit_source', 'preset')  # "preset" or "reference"
        character_style = settings.get('character_style', '標準アニメ')
        additional_desc = convert_age_expressions(settings.get('additional_description', ''))  # 年齢表現を安全に変換

        style_info = CHARACTER_STYLES.get(character_style, CHARACTER_STYLES['標準アニメ'])

        # 参考画像モードの場合
        if outfit_source == "reference":
            reference_image_path = settings.get('reference_image_path', '')
            reference_desc = convert_age_expressions(settings.get('reference_description', ''))
            fit_mode = settings.get('fit_mode', 'base_priority')  # base_priority / outfit_priority / hybrid
            include_headwear = settings.get('include_headwear', True)  # 頭部装飾を含めるか

            # フィットモードに応じた制約を生成
            if fit_mode == "outfit_priority":
                # 衣装優先: 体型を参考画像に合わせる
                fit_mode_label = "outfit_priority (衣装優先)"
                # 頭部装飾の制約
                if include_headwear:
                    headwear_constraint = '    - "Include headwear (hats, helmets, etc.) from outfit_reference if present"'
                    headwear_anti_rule = '  - "Include headwear from outfit_reference - hats, helmets, caps should be applied"'
                else:
                    headwear_constraint = '    - "EXCLUDE headwear (hats, helmets, caps, etc.) from outfit_reference"'
                    headwear_anti_rule = '  - "Do NOT include any headwear from outfit_reference - no hats, helmets, or head accessories"'
                body_constraints = f"""  body_adaptation:
    - "Adapt body proportions to match the outfit_reference image"
    - "Maintain the silhouette and shape of the outfit from reference"
    - "Keep protectors, padding, and bulky elements at their original size"
    - "Body shape should fit the outfit, not the other way around"
  face_preservation:
    - "MUST use exact face from input body_sheet"
    - "Do NOT alter facial features, expression, or proportions"
    - "Maintain exact hair style and color from body_sheet reference"
  pose_preservation:
    - "MUST use the POSE from body_sheet (attention pose / kiwotsuke)"
    - "Do NOT copy the pose from outfit_reference image"
    - "Extract ONLY the clothing design, IGNORE the pose in reference"
  headwear:
{headwear_constraint}
  outfit_extraction:
    - "Extract ONLY the clothing/outfit from the outfit_reference image"
    - "KEEP the body proportions that fit the outfit from reference"
    - "Maintain the style, color, design, and SHAPE of the reference outfit"
    - "Do NOT shrink or resize outfit to fit body_sheet body\""""
                anti_hallucination_rules = f"""  - "Do NOT use face from outfit_reference image"
  - "Do NOT copy the POSE from outfit_reference - use body_sheet pose only"
  - "Do NOT shrink or compress outfit elements (like protectors)"
  - "ALLOW body proportions to change to match outfit reference"
  - "Do NOT add accessories not visible in outfit_reference"
  - "Do NOT change hair style or color from body_sheet"
  - "Apply the outfit with its ORIGINAL proportions from reference image"
{headwear_anti_rule}"""
            elif fit_mode == "hybrid":
                # ハイブリッド: 顔・髪・頭部装飾すべて素体から、体型は衣装に合わせる
                fit_mode_label = "hybrid (ハイブリッド: 頭部全体は素体、体型は衣装)"
                body_constraints = """  hybrid_mode:
    - "HEAD (face, hair, headwear) ONLY from body_sheet"
    - "Body proportions from outfit_reference"
    - "This creates a hybrid: original head on a body that fits the outfit"
  head_preservation:
    - "MUST use ENTIRE HEAD from input body_sheet (face + hair + any accessories)"
    - "Do NOT alter facial features, expression, or proportions"
    - "Maintain exact hair style and color from body_sheet reference"
    - "Do NOT apply any headwear (hats, helmets, etc.) from outfit_reference"
    - "Head should look exactly like body_sheet - NO changes from reference"
  pose_preservation:
    - "MUST use the POSE from body_sheet (attention pose / kiwotsuke)"
    - "Do NOT copy the pose from outfit_reference image"
    - "Extract ONLY the clothing design, IGNORE the pose in reference"
  body_adaptation:
    - "Adapt body proportions to match the outfit_reference image"
    - "Keep protectors, padding, and bulky elements at their original size"
    - "Body shape should fit the outfit naturally"
  outfit_extraction:
    - "Extract ONLY the clothing/outfit (body parts only) from the outfit_reference image"
    - "EXCLUDE any headwear (hats, helmets, caps) from outfit_reference"
    - "KEEP the body proportions that fit the outfit from reference"
    - "Maintain the style, color, design, and SHAPE of the reference outfit"""
                anti_hallucination_rules = """  - "Do NOT use face from outfit_reference image - ONLY use body_sheet face"
  - "Do NOT use hair style from outfit_reference - ONLY use body_sheet hair"
  - "Do NOT apply headwear (hats, helmets, caps) from outfit_reference - head must match body_sheet exactly"
  - "Do NOT copy the POSE from outfit_reference - use body_sheet pose only"
  - "Do NOT shrink or compress outfit elements (like protectors)"
  - "ALLOW body proportions to change to match outfit reference"
  - "Do NOT add accessories not visible in outfit_reference"
  - "Apply the outfit with its ORIGINAL proportions from reference image"
  - "HEAD must be IDENTICAL to body_sheet - no changes from reference allowed"""
            else:
                # base_priority（素体優先）: 現状の動作（デフォルト）
                fit_mode_label = "base_priority (素体優先)"
                # 頭部装飾の制約
                if include_headwear:
                    headwear_constraint = '    - "Include headwear (hats, helmets, etc.) from outfit_reference if present"'
                    headwear_anti_rule = '  - "Include headwear from outfit_reference - hats, helmets, caps should be applied"'
                else:
                    headwear_constraint = '    - "EXCLUDE headwear (hats, helmets, caps, etc.) from outfit_reference"'
                    headwear_anti_rule = '  - "Do NOT include any headwear from outfit_reference - no hats, helmets, or head accessories"'
                body_constraints = f"""  face_preservation:
    - "MUST use exact face from input body_sheet"
    - "Do NOT alter facial features, expression, or proportions"
    - "Maintain exact hair style and color from body_sheet reference"
  body_preservation:
    - "MUST use exact body shape from input body_sheet"
    - "Do NOT alter body proportions or pose"
    - "Body should be visible through/under clothing naturally"
  pose_preservation:
    - "MUST use the POSE from body_sheet (attention pose / kiwotsuke)"
    - "Do NOT copy the pose from outfit_reference image"
    - "Extract ONLY the clothing design, IGNORE the pose in reference"
  headwear:
{headwear_constraint}
  outfit_extraction:
    - "Extract ONLY the clothing/outfit from the outfit_reference image"
    - "Do NOT copy the face or body from outfit_reference"
    - "Adapt the outfit to fit the body_sheet character's body shape"
    - "Maintain the style, color, and design of the reference outfit\""""
                anti_hallucination_rules = f"""  - "Do NOT use face or body from outfit_reference image"
  - "Do NOT copy the POSE from outfit_reference - use body_sheet pose only"
  - "Do NOT alter body proportions from body_sheet"
  - "Do NOT add accessories not visible in outfit_reference"
  - "Do NOT change hair style or color from body_sheet"
  - "Apply ONLY the outfit visible in outfit_reference image"
{headwear_anti_rule}"""

            yaml_content = f"""# Step 3: Outfit Application from Reference Image (参考画像から衣装着用)
# Purpose: Professional character design reference for commercial use
# Usage: Product catalogs, instruction manuals, educational materials, corporate training
# Note: This is legitimate business artwork, NOT inappropriate content
# IMPORTANT: User is responsible for copyright compliance of reference images
type: outfit_reference_from_image
title: "{title or 'Outfit Reference Sheet'}"
author: "{author}"

# ====================================================
# Input Images
# ====================================================
input:
  body_sheet: "{os.path.basename(body_sheet_path) if body_sheet_path else 'REQUIRED'}"
  outfit_reference: "{os.path.basename(reference_image_path) if reference_image_path else 'REQUIRED'}"
  fit_mode: "{fit_mode_label}"

# ====================================================
# Outfit from Reference Image
# ====================================================
outfit:
  source: "reference_image"
  instruction: "Extract and apply the outfit/clothing from the outfit_reference image to the character in body_sheet"
  fit_mode: "{fit_mode}"
{f'  description: "{reference_desc}"' if reference_desc else ''}
{f'  additional_notes: "{additional_desc}"' if additional_desc else ''}

# ====================================================
# Output Format
# ====================================================
output:
  format: "three view reference sheet"
  views:
    - "front view"
    - "side view (left or right)"
    - "back view"
  pose: "T-pose or A-pose, same as body sheet"
  background: "pure white, clean"

# ====================================================
# Style Settings
# ====================================================
style:
  character_style: "{style_info.get('style', '')}"
  proportions: "{style_info.get('proportions', '')}"
  color_mode: "{COLOR_MODES.get(color_mode, ('fullcolor', ''))[0]}"
  output_style: "{OUTPUT_STYLES.get(output_style, '')}"
  aspect_ratio: "16:9"  # 衣装三面図は16:9固定

# ====================================================
# Constraints (Critical) - Fit Mode: {fit_mode_label}
# ====================================================
constraints:
  layout:
    - "STRICT horizontal arrangement: LEFT=front view, CENTER=left side view, RIGHT=back view"
    - "Side view MUST show LEFT side of body (character facing left)"
    - "POSITION ORDER IS CRITICAL: Front on LEFT, Side in CENTER, Back on RIGHT"
{body_constraints}
  consistency:
    - "All three views must show the same character in same outfit"
    - "Maintain consistent proportions across views"
    - "Use clean linework suitable for reference"

anti_hallucination:
{anti_hallucination_rules}
  - "Do NOT change the view order - ALWAYS front/side/back from left to right"
"""
        else:
            # プリセットモードの場合（従来のロジック）
            outfit = settings.get('outfit', {})

            # 衣装プロンプト生成
            outfit_prompt = generate_outfit_prompt(
                outfit.get('category', 'おまかせ'),
                outfit.get('shape', 'おまかせ'),
                outfit.get('color', 'おまかせ'),
                outfit.get('pattern', 'おまかせ'),
                outfit.get('style', 'おまかせ')
            )

            yaml_content = f"""# Step 3: Outfit Application (衣装着用)
# Purpose: Professional character design reference for commercial use
# Usage: Product catalogs, instruction manuals, educational materials, corporate training
# Note: This is legitimate business artwork, NOT inappropriate content
type: outfit_reference_sheet
title: "{title or 'Outfit Reference Sheet'}"
author: "{author}"

# ====================================================
# Input: Body Sheet from Step 2
# ====================================================
input:
  body_sheet: "{os.path.basename(body_sheet_path) if body_sheet_path else 'REQUIRED'}"
  preserve_body: true
  preserve_face: true
  preserve_details: "exact match required - do not alter face or body shape"

# ====================================================
# Outfit Configuration
# ====================================================
outfit:
  category: "{outfit.get('category', 'おまかせ')}"
  shape: "{outfit.get('shape', 'おまかせ')}"
  color: "{outfit.get('color', 'おまかせ')}"
  pattern: "{outfit.get('pattern', 'おまかせ')}"
  style_impression: "{outfit.get('style', 'おまかせ')}"
  prompt: "{outfit_prompt}"
{f'  additional_notes: "{additional_desc}"' if additional_desc else ''}

# ====================================================
# Output Format
# ====================================================
output:
  format: "three view reference sheet"
  views:
    - "front view"
    - "side view (left or right)"
    - "back view"
  pose: "T-pose or A-pose, same as body sheet"
  background: "pure white, clean"

# ====================================================
# Style Settings
# ====================================================
style:
  character_style: "{style_info.get('style', '')}"
  proportions: "{style_info.get('proportions', '')}"
  color_mode: "{COLOR_MODES.get(color_mode, ('fullcolor', ''))[0]}"
  output_style: "{OUTPUT_STYLES.get(output_style, '')}"
  aspect_ratio: "16:9"  # 衣装三面図は16:9固定

# ====================================================
# Constraints (Critical)
# ====================================================
constraints:
  layout:
    - "STRICT horizontal arrangement: LEFT=front view, CENTER=left side view, RIGHT=back view"
    - "Side view MUST show LEFT side of body (character facing left)"
    - "POSITION ORDER IS CRITICAL: Front on LEFT, Side in CENTER, Back on RIGHT"
  face_preservation:
    - "MUST use exact face from input body_sheet"
    - "Do NOT alter facial features, expression, or proportions"
    - "Maintain exact hair style and color from reference"
  body_preservation:
    - "MUST use exact body shape from input body_sheet"
    - "Do NOT alter body proportions or pose"
    - "Body should be visible through/under clothing naturally"
  outfit_application:
    - "Apply specified outfit to the body"
    - "Maintain clothing consistency across all three views"
    - "Show realistic fabric draping and fit"
  consistency:
    - "All three views must show the same character in same outfit"
    - "Maintain consistent proportions across views"
    - "Use clean linework suitable for reference"

anti_hallucination:
  - "Do NOT change the face from the body sheet reference"
  - "Do NOT alter body proportions"
  - "Do NOT add accessories not specified in outfit"
  - "Do NOT change hair style or color"
  - "Apply ONLY the specified outfit"
  - "Do NOT change the view order - ALWAYS front/side/back from left to right"
"""

        if include_title_in_image:
            yaml_content += f"""
title_overlay:
  enabled: true
  text: "{title}"
  position: "top-left"
"""

        return yaml_content

    def _generate_background_yaml(self, color_mode, duotone_color, output_style, aspect_ratio, title, author, include_title_in_image):
        """背景生成用YAML生成"""
        settings = self.current_settings
        description = settings.get('description', '')
        # 背景キャプチャ設定
        bg_capture_enabled = settings.get('bg_capture_enabled', False)
        bg_reference_image = settings.get('bg_reference_image', '')
        remove_people = settings.get('remove_people', True)
        transform_instruction = settings.get('transform_instruction', '')

        # 背景キャプチャモードの場合
        if bg_capture_enabled and bg_reference_image:
            # 変形指示がない場合はアニメ調に変換
            if not transform_instruction:
                transform_instruction = "Convert to anime/illustration style, clean lines, vibrant colors"

            # 人物除去の指示
            people_instruction = ""
            if remove_people:
                people_instruction = """
  remove_people:
    enabled: true
    instruction: "Remove all people/humans from the image. Fill the removed areas naturally with background elements."
"""

            # アスペクト比の処理（グローバル設定を使用）
            aspect_ratio_value = ASPECT_RATIOS.get(aspect_ratio, '1:1')
            if aspect_ratio_value == "preserve_original":
                aspect_ratio_instruction = "Preserve the original aspect ratio of the reference image"
            else:
                aspect_ratio_instruction = f"Output aspect ratio: {aspect_ratio_value}"

            yaml_content = f"""# Background Capture (背景キャプチャ)
title: "{title or 'Background'}"
author: "{author}"

output_type: "background_capture"

# ====================================================
# Background Capture Settings
# ====================================================
background_capture:
  enabled: true
  reference_image: "{os.path.basename(bg_reference_image)}"
  transform_instruction: "{transform_instruction}"
  aspect_ratio: "{aspect_ratio_value}"
  aspect_ratio_instruction: "{aspect_ratio_instruction}"
{people_instruction}
# ====================================================
# CRITICAL CONSTRAINTS
# ====================================================
constraints:
  - "Use the reference image as the base for the background"
  - "Apply the transformation instruction to modify the style/atmosphere"
  - "Do NOT include any characters or people in the output"
  - "Maintain the general composition and layout from the reference"
  - "{aspect_ratio_instruction}"

style:
  color_mode: "{COLOR_MODES.get(color_mode, 'full_color')}"
  output_style: "{OUTPUT_STYLES.get(output_style, 'anime')}"
  aspect_ratio: "{aspect_ratio_value}"
"""
        else:
            # テキスト記述モード（従来通り）
            yaml_content = f"""# Background Generation
title: "{title or 'Background'}"
author: "{author}"

output_type: "background only"

background:
  description: "{description}"

style:
  color_mode: "{COLOR_MODES.get(color_mode, 'full_color')}"
  output_style: "{OUTPUT_STYLES.get(output_style, 'anime')}"
  aspect_ratio: "{ASPECT_RATIOS.get(aspect_ratio, '1:1')}"
"""

        # タイトルオーバーレイ（有効な場合のみ出力）
        if include_title_in_image:
            yaml_content += f"""
title_overlay:
  enabled: true
  text: "{title}"
  position: "top-left"
"""
        return yaml_content

    def _generate_pose_yaml(self, color_mode, duotone_color, output_style, aspect_ratio, title, author, include_title_in_image):
        """ポーズ画像用YAML生成（単一画像出力）"""
        settings = self.current_settings
        from ui.pose_window import WIND_EFFECTS, EXPRESSIONS

        preset = settings.get('preset', '（プリセットなし）')
        image_path = settings.get('image_path', '')
        identity = settings.get('identity_preservation', 0.85)
        eye_line = settings.get('eye_line', '前を見る')
        expression = EXPRESSIONS.get(settings.get('expression', '無表情'), 'neutral expression')
        expression_detail = settings.get('expression_detail', '')
        action_desc = settings.get('action_description', '')
        include_effects = settings.get('include_effects', False)
        transparent_bg = settings.get('transparent_bg', False)
        wind = WIND_EFFECTS.get(settings.get('wind_effect', 'なし'), '')
        additional_prompt = settings.get('additional_prompt', '')
        # ポーズキャプチャ設定
        pose_capture_enabled = settings.get('pose_capture_enabled', False)
        pose_reference_image = settings.get('pose_reference_image', '')

        # 表情プロンプト生成（補足があれば追加）
        expression_prompt = expression
        if expression_detail:
            expression_prompt = f"{expression}, {expression_detail}"

        # プリセットコメント（キャプチャモードでは表示しない）
        preset_comment = ""
        if not pose_capture_enabled and preset != "（プリセットなし）":
            preset_comment = f"# Preset: {preset}\n"

        # 追加プロンプトセクション
        additional_section = ""
        if additional_prompt:
            additional_section = f"""
additional_details:
  - {additional_prompt}
"""

        # 風エフェクトセクション
        wind_section = ""
        if wind:
            wind_section = f"""
  wind_effect: "{wind}"
"""

        # ポーズキャプチャモードの場合
        if pose_capture_enabled and pose_reference_image:
            pose_source_section = f"""# ====================================================
# Pose Capture (ポーズキャプチャ)
# ====================================================
pose_capture:
  enabled: true
  reference_image: "{os.path.basename(pose_reference_image)}"
  capture_target: "pose_only"
  instruction: |
    Capture ONLY the pose (body position, arm/leg positions, gestures) from the reference image.
    Apply this pose to the character while preserving:
    - Character's face and facial features from character_sheet
    - Character's outfit and clothing from character_sheet
    - Character's colors and design from character_sheet
    Do NOT transfer any appearance elements from the reference image.

pose:
  source: "captured from reference image"
  expression: "{expression_prompt}"
  eye_line: "{eye_line}"
  include_effects: {str(include_effects).lower()}{wind_section}"""
        else:
            pose_source_section = f"""# ====================================================
# Pose Definition
# ====================================================
pose:
  description: "{action_desc}"
  expression: "{expression_prompt}"
  eye_line: "{eye_line}"
  include_effects: {str(include_effects).lower()}{wind_section}"""

        yaml_content = f"""# Step 4: Pose Image (ポーズ画像)
# Purpose: Generate character in specified pose based on outfit sheet
# Output: Single character image
{preset_comment}type: pose_single
title: "{title or 'Character Pose'}"
author: "{author}"

# ====================================================
# Input Image
# ====================================================
input:
  character_sheet: "{os.path.basename(image_path) if image_path else ''}"
  identity_preservation: {identity}
  purpose: "Generate posed character from outfit sheet"

{pose_source_section}{additional_section}
# ====================================================
# Output Settings
# ====================================================
output:
  format: "single_image"
  background: "{'transparent, fully clear alpha channel' if transparent_bg else 'pure white, clean background'}"

# ====================================================
# CRITICAL CONSTRAINTS
# ====================================================
constraints:
  character_preservation:
    - "Preserve exact character design, face, and colors from input image"
    - "Maintain clothing details exactly as shown in input"
  output_format:
    - "Single character image, full body visible"

anti_hallucination:
  - "Do NOT alter character design from input"
  - "Do NOT add extra figures"

style:
  color_mode: "{COLOR_MODES.get(color_mode, ('fullcolor', ''))[0]}"
  output_style: "{OUTPUT_STYLES.get(output_style, '')}"
  aspect_ratio: "{aspect_ratio}"
"""

        # タイトルオーバーレイ（有効な場合のみ出力）
        if include_title_in_image:
            yaml_content += f"""
title_overlay:
  enabled: true
  text: "{title}"
  position: "top-left"
"""
        return yaml_content

    def _generate_decorative_yaml(self, color_mode, duotone_color, output_style, aspect_ratio, title, author, include_title_in_image):
        """装飾テキスト用YAML生成（ui_text_overlay.yaml準拠）"""
        from ui.decorative_text_window import (
            TEXT_TYPES, TITLE_FONTS, TITLE_SIZES, GRADIENT_COLORS,
            OUTLINE_COLORS, GLOW_EFFECTS, CALLOUT_TYPES, CALLOUT_COLORS,
            ROTATIONS, DISTORTIONS, NAMETAG_TYPES,
            MSGWIN_STYLES, MSGWIN_FRAME_TYPES, FACE_ICON_POSITIONS
        )

        settings = self.current_settings
        text_type = settings.get('text_type', '技名テロップ')
        text_content = settings.get('text', '')
        style = settings.get('style', {})
        transparent_bg = settings.get('transparent_bg', True)  # デフォルトは透過

        type_key = TEXT_TYPES.get(text_type, 'special_move_title')
        bg_value = "Transparent" if transparent_bg else "None (Generate with scene)"

        if text_type == "技名テロップ":
            yaml_content = f"""# Decorative Text (ui_text_overlay.yaml準拠)
type: text_ui_layer_definition
title: "{title or 'Decorative Text'}"
author: "{author}"

ui_global_style:
  preset: "Anime Battle"
  font_language: "Japanese"

special_move_title:
  enabled: true
  text: "{text_content}"

  style:
    font_type: "{TITLE_FONTS.get(style.get('font', '極太明朝'), 'Heavy Mincho')}"
    size: "{TITLE_SIZES.get(style.get('size', '特大'), 'Very Large')}"
    fill_color: "{GRADIENT_COLORS.get(style.get('color', '白→青'), 'White to Blue Gradient')}"
    outline:
      enabled: {str(style.get('outline', '金') != 'なし').lower()}
      color: "{OUTLINE_COLORS.get(style.get('outline', '金'), 'Gold')}"
      thickness: "Thick"
    glow_effect: "{GLOW_EFFECTS.get(style.get('glow', '青い稲妻'), 'Blue Lightning')}"
    drop_shadow: "{'Hard Drop' if style.get('shadow', True) else 'None'}"

output:
  background: "{bg_value}"

style:
  color_mode: "{COLOR_MODES.get(color_mode, 'full_color')}"
  output_style: "{OUTPUT_STYLES.get(output_style, 'anime')}"
  aspect_ratio: "{ASPECT_RATIOS.get(aspect_ratio, '16:9')}"
"""

        elif text_type == "決め台詞":
            yaml_content = f"""# Decorative Text (ui_text_overlay.yaml準拠)
type: text_ui_layer_definition
title: "{title or 'Decorative Text'}"
author: "{author}"

ui_global_style:
  preset: "Anime Battle"
  font_language: "Japanese"

impact_callout:
  enabled: true
  text: "{text_content}"

  style:
    type: "{CALLOUT_TYPES.get(style.get('type', '書き文字風'), 'Comic Sound Effect')}"
    color: "{CALLOUT_COLORS.get(style.get('color', '赤＋黄縁'), 'Red with Yellow Border')}"
    rotation: "{ROTATIONS.get(style.get('rotation', '左傾き'), '-15 degrees')}"
    distortion: "{DISTORTIONS.get(style.get('distortion', '飛び出し'), 'Zoom In')}"

output:
  background: "{bg_value}"

style:
  color_mode: "{COLOR_MODES.get(color_mode, 'full_color')}"
  output_style: "{OUTPUT_STYLES.get(output_style, 'anime')}"
  aspect_ratio: "{ASPECT_RATIOS.get(aspect_ratio, '16:9')}"
"""

        elif text_type == "キャラ名プレート":
            yaml_content = f"""# Decorative Text (ui_text_overlay.yaml準拠)
type: text_ui_layer_definition
title: "{title or 'Decorative Text'}"
author: "{author}"

ui_global_style:
  preset: "Anime Battle"
  font_language: "Japanese"

name_tag:
  enabled: true
  text: "{text_content}"

  style:
    type: "{NAMETAG_TYPES.get(style.get('type', 'ギザギザステッカー'), 'Jagged Sticker')}"
    rotation: "{ROTATIONS.get(style.get('rotation', '少し左傾き'), '-5 degrees')}"

output:
  background: "{bg_value}"

style:
  color_mode: "{COLOR_MODES.get(color_mode, 'full_color')}"
  output_style: "{OUTPUT_STYLES.get(output_style, 'anime')}"
  aspect_ratio: "{ASPECT_RATIOS.get(aspect_ratio, '16:9')}"
"""

        elif text_type == "メッセージウィンドウ":
            from ui.decorative_text_window import MSGWIN_MODES
            mode = settings.get('mode', 'フルスペック（名前+顔+セリフ）')
            mode_key = MSGWIN_MODES.get(mode, 'full')
            speaker_name = settings.get('speaker_name', '')
            face_position = style.get('face_icon_position', '左内側')

            if mode_key == "full":
                # フルスペック: 名前+顔+セリフ
                yaml_content = f"""# Message Window - Full (ui_text_overlay.yaml準拠)
type: text_ui_layer_definition
title: "{title or 'Message Window'}"
author: "{author}"

ui_global_style:
  preset: "Anime Battle"
  font_language: "Japanese"

message_window:
  enabled: true
  mode: "full"
  speaker_name: "{speaker_name}"
  text: "{text_content}"
  style_preset: "{MSGWIN_STYLES.get(style.get('preset', 'SF・ロボット風'), 'Sci-Fi Tech')}"

  design:
    position: "Bottom Center"
    width: "90%"
    frame_type: "{MSGWIN_FRAME_TYPES.get(style.get('frame_type', 'サイバネティック青'), 'Cybernetic Blue')}"
    background_opacity: {style.get('opacity', 0.8)}

    face_icon:
      enabled: true
      source_image: "Auto(Left Character)"
      position: "{FACE_ICON_POSITIONS.get(face_position, 'Left Inside')}"

output:
  background: "{bg_value}"

style:
  color_mode: "{COLOR_MODES.get(color_mode, 'full_color')}"
  output_style: "{OUTPUT_STYLES.get(output_style, 'anime')}"
  aspect_ratio: "{ASPECT_RATIOS.get(aspect_ratio, '16:9')}"
"""
            elif mode_key == "face_only":
                # 顔アイコンのみ
                yaml_content = f"""# Message Window - Face Only (ui_text_overlay.yaml準拠)
type: text_ui_layer_definition
title: "{title or 'Face Icon'}"
author: "{author}"

ui_global_style:
  preset: "Anime Battle"
  font_language: "Japanese"

message_window:
  enabled: true
  mode: "face_only"

  design:
    face_icon:
      enabled: true
      source_image: "Auto(Left Character)"
      position: "{FACE_ICON_POSITIONS.get(face_position, 'Left Inside')}"
      style: "Standalone"

output:
  background: "{bg_value}"

style:
  color_mode: "{COLOR_MODES.get(color_mode, 'full_color')}"
  output_style: "{OUTPUT_STYLES.get(output_style, 'anime')}"
  aspect_ratio: "{ASPECT_RATIOS.get(aspect_ratio, '1:1')}"
"""
            else:  # text_only
                # セリフのみ
                yaml_content = f"""# Message Window - Text Only (ui_text_overlay.yaml準拠)
type: text_ui_layer_definition
title: "{title or 'Message Text'}"
author: "{author}"

ui_global_style:
  preset: "Anime Battle"
  font_language: "Japanese"

message_window:
  enabled: true
  mode: "text_only"
  text: "{text_content}"

  design:
    position: "Bottom Center"
    width: "90%"
    frame_type: "{MSGWIN_FRAME_TYPES.get(style.get('frame_type', 'サイバネティック青'), 'Cybernetic Blue')}"
    background_opacity: {style.get('opacity', 0.8)}

    face_icon:
      enabled: false

output:
  background: "{bg_value}"

style:
  color_mode: "{COLOR_MODES.get(color_mode, 'full_color')}"
  output_style: "{OUTPUT_STYLES.get(output_style, 'anime')}"
  aspect_ratio: "{ASPECT_RATIOS.get(aspect_ratio, '16:9')}"
"""
        else:
            yaml_content = "# Unknown text type"

        # タイトルオーバーレイを追加（有効な場合のみ）
        if yaml_content != "# Unknown text type" and include_title_in_image:
            yaml_content += f"""
title_overlay:
  enabled: true
  text: "{title}"
  position: "top-left"
"""

        return yaml_content

    def _generate_four_panel_yaml(self, color_mode, duotone_color, output_style, title, author, include_title_in_image):
        """4コマ漫画用YAML生成（four_panel_manga.yaml準拠）"""
        settings = self.current_settings

        characters = settings.get('characters', [])
        panels = settings.get('panels', [])

        # キャラクターセクション生成
        char_yaml = ""
        for i, char in enumerate(characters):
            char_yaml += f"""
  - name: "{char.get('name', f'キャラ{i+1}')}"
    reference: "添付画像{i+1}を参照してください"
    description: "{char.get('description', '')}\""""

        # パネルセクション生成
        panel_labels = ["起", "承", "転", "結"]
        panels_yaml = ""
        for i, panel in enumerate(panels):
            label = panel_labels[i] if i < len(panel_labels) else str(i+1)

            # セリフ生成
            speeches_yaml = ""
            for speech in panel.get('speeches', []):
                speeches_yaml += f"""
      - character: "{speech.get('character', '')}"
        content: "{speech.get('content', '')}"
        position: "{speech.get('position', 'left')}\""""

            narration = panel.get('narration', '')
            narration_line = f'\n    narration: "{narration}"' if narration else ""

            panels_yaml += f"""
  # --- {i+1}コマ目（{label}）---
  - panel_number: {i+1}
    prompt: "{panel.get('prompt', '')}"
    speeches:{speeches_yaml}{narration_line}
"""

        yaml_content = f"""【画像生成指示 / Image Generation Instructions】
以下のYAML指示に従って、4コマ漫画を1枚の画像として生成してください。
添付したキャラクター設定画を参考に、キャラクターの外見を一貫させてください。

Generate a 4-panel manga as a single image following the YAML instructions below.
Use the attached character reference sheets to maintain consistent character appearances.

---

# 4コマ漫画生成 (four_panel_manga.yaml準拠)
title: "{title}"
author: "{author}"
color_mode: "{COLOR_MODES.get(color_mode, ('fullcolor', ''))[0]}"
output_style: "{OUTPUT_STYLES.get(output_style, 'manga')}"

# 登場人物
characters:{char_yaml}

# 4コマの内容
panels:{panels_yaml}
# レイアウト指示
layout_instruction: |
  4コマ漫画を縦1列に配置してください。
  横並びにせず、上から下へ1コマずつ縦に4つ並べてください。
  出力画像は縦長（9:16または2:5の比率）で、4コマ漫画だけが画像全体を占めるようにしてください。
  余白は不要です。
  各キャラクターの外見は添付画像と説明を忠実に再現してください。
  セリフは吹き出しで表示し、指定された位置に配置してください。
  ナレーションがある場合は、コマの上部または下部にテキストボックスで表示してください。
"""

        # タイトルオーバーレイ（有効な場合のみ出力）
        if include_title_in_image:
            yaml_content += f"""
title_overlay:
  enabled: true
  text: "{title}"
  position: "top-center"
"""
        return yaml_content

    def _generate_style_transform_yaml(self, color_mode, duotone_color, output_style, aspect_ratio, title, author, include_title_in_image):
        """スタイル変換用YAML生成（ちびキャラ化・ドットキャラ化）"""
        settings = self.current_settings
        from ui.style_transform_window import CHIBI_STYLES, PIXEL_STYLES, SPRITE_SIZES

        source_image_path = settings.get('source_image_path', '')
        transform_type = settings.get('transform_type', 'ちびキャラ化')
        transform_type_en = settings.get('transform_type_en', 'chibi')
        additional_desc = convert_age_expressions(settings.get('additional_description', ''))

        # 全タイプ共通の背景透過設定
        transparent_bg = settings.get('transparent_bg', True)

        if transform_type == "ちびキャラ化":
            chibi_settings = settings.get('chibi_settings', {})
            style_name = chibi_settings.get('style', 'スタンダード（2頭身）')
            style_info = chibi_settings.get('style_info', CHIBI_STYLES.get(style_name, {}))
            preserve_outfit = chibi_settings.get('preserve_outfit', True)
            preserve_pose = chibi_settings.get('preserve_pose', True)

            # 保持する要素のリスト作成
            preserve_list = []
            if preserve_outfit:
                preserve_list.append("outfit and clothing")
            if preserve_pose:
                preserve_list.append("pose and action")
            preserve_str = ", ".join(preserve_list) if preserve_list else "basic appearance"

            yaml_content = f"""# Style Transform: Chibi Conversion (スタイル変換: ちびキャラ化)
# Transform realistic/normal character to chibi (super-deformed) style
# The source image can be from any stage (base/outfit/pose)
type: style_transform_chibi
title: "{title or 'Chibi Character'}"
author: "{author}"

# ====================================================
# Input Image (Source Character)
# ====================================================
input:
  source_image: "{os.path.basename(source_image_path) if source_image_path else 'REQUIRED'}"
  source_stage: "any (base body / with outfit / with pose)"

# ====================================================
# Transform Settings
# ====================================================
transform:
  type: "chibi"
  style: "{style_name}"
  style_prompt: "{style_info.get('prompt', '')}"
  head_ratio: "{style_info.get('head_ratio', '2:1')}"

# ====================================================
# Preservation Settings
# ====================================================
preserve:
  elements: "{preserve_str}"
  face_features: "Maintain character's face identity (eyes, hair color, expression)"
  outfit_details: {"true" if preserve_outfit else "false"}
  pose_action: {"true" if preserve_pose else "false"}
{f'  additional_notes: "{additional_desc}"' if additional_desc else ''}

# ====================================================
# Output Settings
# ====================================================
output:
  style: "chibi / super-deformed"
  aspect_ratio: "{ASPECT_RATIOS.get(aspect_ratio, '1:1')}"
  background: "{'transparent' if transparent_bg else 'simple solid color'}"
  quality: "clean linework, cute proportions"

# ====================================================
# Constraints (Critical)
# ====================================================
constraints:
  chibi_rules:
    - "Transform to chibi style with {style_info.get('head_ratio', '2:1')} head-to-body ratio"
    - "Large head, small body, simplified features"
    - "Maintain character identity (face, hair, colors)"
    - "Keep the cuteness and appeal of chibi style"
  preservation_rules:
    - "Preserve: {preserve_str}"
    - "Maintain the same outfit design (simplified for chibi proportions)"
    - "Keep the same pose action (adapted for chibi body)"
  style_consistency:
    - "Use consistent chibi proportions throughout"
    - "Clean, cute linework suitable for chibi style"
    - "{'Transparent background for easy compositing' if transparent_bg else 'Simple background'}"

anti_hallucination:
  - "Do NOT change character's identity (face, hair color)"
  - "Do NOT add new accessories not in source"
  - "Do NOT change outfit design significantly"
  - "MAINTAIN chibi proportions consistently"
"""
        else:
            # ドットキャラ化
            pixel_settings = settings.get('pixel_settings', {})
            style_name = pixel_settings.get('style', '16bit風（スーファミ）')
            style_info = pixel_settings.get('style_info', PIXEL_STYLES.get(style_name, {}))
            sprite_size = pixel_settings.get('sprite_size', '64x64')
            sprite_size_prompt = pixel_settings.get('sprite_size_prompt', SPRITE_SIZES.get(sprite_size, ''))
            preserve_colors = pixel_settings.get('preserve_colors', True)
            # transparent_bg は上位レベルから取得済み

            yaml_content = f"""# Style Transform: Pixel Art Conversion (スタイル変換: ドットキャラ化)
# Transform character to pixel art / sprite style
# The source image can be from any stage (base/outfit/pose)
type: style_transform_pixel
title: "{title or 'Pixel Character'}"
author: "{author}"

# ====================================================
# Input Image (Source Character)
# ====================================================
input:
  source_image: "{os.path.basename(source_image_path) if source_image_path else 'REQUIRED'}"
  source_stage: "any (base body / with outfit / with pose)"

# ====================================================
# Transform Settings
# ====================================================
transform:
  type: "pixel_art"
  style: "{style_name}"
  style_prompt: "{style_info.get('prompt', '')}"
  resolution: "{style_info.get('resolution', 'medium')}"
  color_depth: "{style_info.get('colors', '256')}"

# ====================================================
# Sprite Settings
# ====================================================
sprite:
  size: "{sprite_size}"
  size_prompt: "{sprite_size_prompt}"
  preserve_colors: {"true" if preserve_colors else "false"}
  transparent_background: {"true" if transparent_bg else "false"}
{f'  additional_notes: "{additional_desc}"' if additional_desc else ''}

# ====================================================
# Output Settings
# ====================================================
output:
  style: "pixel art sprite"
  aspect_ratio: "1:1"
  background: "{'transparent' if transparent_bg else 'simple solid color'}"
  quality: "clean pixels, game sprite aesthetic"

# ====================================================
# Constraints (Critical)
# ====================================================
constraints:
  pixel_art_rules:
    - "Convert to {style_name} pixel art style"
    - "Use {sprite_size} sprite size"
    - "Clean, sharp pixels with no anti-aliasing blur"
    - "Limited color palette appropriate for {style_name}"
  preservation_rules:
    - "Maintain character identity (recognizable silhouette)"
    - "Keep the same outfit and pose from source"
    - "{'Reference original colors from source image' if preserve_colors else 'Use appropriate pixel art palette'}"
  style_consistency:
    - "Consistent pixel size throughout the sprite"
    - "Game sprite aesthetic, suitable for game use"
    - "{'Transparent background for easy compositing' if transparent_bg else 'Simple background'}"

anti_hallucination:
  - "Do NOT add pixel art artifacts or noise"
  - "Do NOT blur or anti-alias the pixels"
  - "MAINTAIN consistent pixel grid"
  - "Do NOT change character's recognizable features"
"""

        # タイトルオーバーレイ
        if include_title_in_image:
            yaml_content += f"""
title_overlay:
  enabled: true
  text: "{title}"
  position: "bottom-center"
"""
        return yaml_content

    # === API Image Generation ===

    def _generate_redraw_image(self):
        """清書モード専用：YAML + 参照画像で高品質再描画"""
        # APIキーチェック
        api_key = self.api_key_entry.get().strip()
        if not api_key:
            messagebox.showwarning("警告", "API Keyを入力してください")
            return

        # YAML必須チェック（清書モードでは読込が必要）
        yaml_content = self.yaml_textbox.get("1.0", tk.END).strip()
        if not yaml_content:
            messagebox.showwarning(
                "警告",
                "清書モードではYAMLが必要です。\n\n"
                "ブラウザ版で成功したYAMLを「読込」ボタンで\n"
                "読み込むか、直接ペーストしてください。"
            )
            return

        # 参考画像チェック
        ref_image_path = self.ref_image_entry.get().strip()
        if not ref_image_path or not os.path.exists(ref_image_path):
            messagebox.showwarning(
                "警告",
                "参考画像を選択してください。\n\n"
                "ブラウザ版で生成した画像を指定してください。"
            )
            return

        # タイトル必須チェック（ファイル名用）
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning("警告", "タイトルを入力してください（ファイル名に使用します）")
            self.title_entry.focus_set()
            return

        # 確認ダイアログ
        confirm_msg = (
            "【清書モード】高品質再描画を実行します\n\n"
            f"参考画像: {os.path.basename(ref_image_path)}\n"
            f"YAML: 読込済み ({len(yaml_content)}文字)\n"
            f"解像度: {self.resolution_var.get()}\n"
            "\n※ YAMLの指示 + 参照画像の構図で再描画します\n"
            "※ API呼び出しには料金がかかります\n\n"
            "実行しますか？"
        )
        if not messagebox.askyesno("生成確認", confirm_msg):
            return

        # 生成中表示
        self.generate_button.configure(state="disabled", text="清書中...")
        self.preview_label.configure(text="高品質再描画中...\n経過時間: 0秒", image=None)

        # 経過時間タイマー開始
        self._generation_start_time = time.time()
        self._start_progress_timer()

        # 解像度を取得
        resolution = self.resolution_var.get()

        # YAMLはそのまま保持（読み込んだYAMLを使用するため上書きしない）

        def generate():
            try:
                result = generate_image_with_api(
                    api_key=api_key,
                    yaml_prompt=yaml_content,  # 読み込んだYAMLを使用
                    char_image_paths=[],
                    resolution=resolution,
                    ref_image_path=ref_image_path
                )

                if result['success'] and result['image']:
                    img = result['image']
                    self.after(0, lambda img=img: self._on_image_generated(img))
                else:
                    error_msg = result.get('error', '不明なエラー')
                    self.after(0, lambda msg=error_msg: self._on_image_error(msg))
            except Exception as e:
                error_str = str(e)
                self.after(0, lambda msg=error_str: self._on_image_error(msg))

        thread = threading.Thread(target=generate, daemon=True)
        thread.start()

    def _generate_image_with_api(self, yaml_content: str):
        """APIで画像生成（通常モード）"""
        api_key = self.api_key_entry.get().strip()
        if not api_key:
            messagebox.showwarning("警告", "API Keyを入力してください")
            return

        # 確認ダイアログ
        confirm_msg = (
            "【通常モード】画像生成を実行します\n\n"
            "⚠ 注意事項:\n"
            "・API呼び出しには料金がかかります\n\n"
            "実行しますか？"
        )
        if not messagebox.askyesno("生成確認", confirm_msg):
            return

        # 生成中表示
        self.generate_button.configure(state="disabled", text="生成中...")
        self.preview_label.configure(text="画像生成中...\n経過時間: 0秒", image=None)

        # 経過時間タイマー開始
        self._generation_start_time = time.time()
        self._start_progress_timer()

        # 解像度を取得
        resolution = self.resolution_var.get()

        def generate():
            try:
                # APIクライアントを呼び出し（戻り値はdict）
                # 通常モードでは参考画像は使用しない
                result = generate_image_with_api(
                    api_key=api_key,
                    yaml_prompt=yaml_content,
                    char_image_paths=[],
                    resolution=resolution,
                    ref_image_path=None  # 通常モードでは参考画像なし
                )

                if result['success'] and result['image']:
                    img = result['image']
                    self.after(0, lambda img=img: self._on_image_generated(img))
                else:
                    error_msg = result.get('error', '不明なエラー')
                    self.after(0, lambda msg=error_msg: self._on_image_error(msg))
            except Exception as e:
                error_str = str(e)
                self.after(0, lambda msg=error_str: self._on_image_error(msg))

        thread = threading.Thread(target=generate, daemon=True)
        thread.start()

    def _start_progress_timer(self):
        """経過時間表示タイマーを開始"""
        self._update_progress_display()

    def _update_progress_display(self):
        """経過時間表示を更新"""
        if self._generation_start_time is not None:
            elapsed = int(time.time() - self._generation_start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            if minutes > 0:
                time_str = f"{minutes}分{seconds}秒"
            else:
                time_str = f"{seconds}秒"

            self.preview_label.configure(
                text=f"画像生成中...\n経過時間: {time_str}",
                image=None
            )
            # 1秒後に再度更新
            self._progress_timer_id = self.after(1000, self._update_progress_display)

    def _stop_progress_timer(self):
        """経過時間表示タイマーを停止"""
        if self._progress_timer_id is not None:
            self.after_cancel(self._progress_timer_id)
            self._progress_timer_id = None
        self._generation_start_time = None

    def _on_image_generated(self, image: Image.Image):
        """画像生成完了"""
        # タイマー停止
        self._stop_progress_timer()

        # タイトル合成（チェックボックスがオンの場合）
        if self.include_title_var.get():
            title = self.title_entry.get().strip()
            if title:
                image = add_title_to_image(image, title, position="top-left")

        self.generated_image = image
        self._image_generated_by_api = True  # API生成フラグを設定

        # ボタンのテキストを現在のモードに応じて設定
        if self.output_mode_var.get() == "api":
            self.generate_button.configure(state="normal", text="画像生成")
        else:
            self.generate_button.configure(state="normal", text="YAML生成")
        self.save_image_button.configure(state="normal")

        # プレビュー表示（元画像をコピーしてサムネイル化）
        preview_image = image.copy()
        preview_size = (400, 400)
        preview_image.thumbnail(preview_size, Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(preview_image)
        self.preview_label.configure(image=photo, text="")
        self.preview_label.image = photo

    def _on_image_error(self, error_msg: str):
        """画像生成エラー"""
        # タイマー停止
        self._stop_progress_timer()

        # ボタンのテキストを現在のモードに応じて設定
        if self.output_mode_var.get() == "api":
            self.generate_button.configure(state="normal", text="画像生成")
        else:
            self.generate_button.configure(state="normal", text="YAML生成")
        self.preview_label.configure(text=f"エラー: {error_msg}", image=None)
        messagebox.showerror("エラー", f"画像生成に失敗しました:\n{error_msg}")

    # === File Operations ===

    def _copy_yaml(self):
        """YAMLをクリップボードにコピー"""
        yaml_content = self.yaml_textbox.get("1.0", tk.END).strip()
        if yaml_content:
            # tkinterの組み込みクリップボード機能を使用（macOSで確実に動作）
            self.clipboard_clear()
            self.clipboard_append(yaml_content)
            self.update()  # クリップボードを確実に更新
            messagebox.showinfo("コピー完了", "YAMLをクリップボードにコピーしました")

    def _get_safe_filename(self, title: str) -> str:
        """タイトルからファイル名に使える文字列を生成"""
        # ファイル名に使えない文字を置換
        invalid_chars = '<>:"/\\|?*'
        safe_name = title
        for char in invalid_chars:
            safe_name = safe_name.replace(char, '_')
        return safe_name.strip() or "untitled"

    def _save_yaml(self):
        """YAMLを保存"""
        yaml_content = self.yaml_textbox.get("1.0", tk.END).strip()
        if not yaml_content:
            messagebox.showwarning("警告", "保存するYAMLがありません")
            return

        # タイトルからデフォルトファイル名を生成
        title = self.title_entry.get().strip()
        base_name = self._get_safe_filename(title) if title else "output"
        default_filename = f"{base_name}.yaml"

        filename = filedialog.asksaveasfilename(
            initialfile=default_filename,
            defaultextension=".yaml",
            filetypes=[("YAML files", "*.yaml *.yml"), ("All files", "*.*")]
        )
        if filename:
            save_yaml_file(filename, yaml_content)
            self.last_saved_yaml_path = filename  # パスを記録
            add_to_recent_files(self.recent_files, filename)
            save_recent_files(self.recent_files_path, self.recent_files)
            messagebox.showinfo("保存完了", f"YAMLを保存しました:\n{filename}")

    def _load_yaml(self):
        """YAMLを読み込み"""
        filename = filedialog.askopenfilename(
            filetypes=[("YAML files", "*.yaml *.yml"), ("All files", "*.*")]
        )
        if filename:
            yaml_content = load_yaml_file(filename)
            if yaml_content:
                self.yaml_textbox.delete("1.0", tk.END)
                self.yaml_textbox.insert("1.0", yaml_content)
                self.last_saved_yaml_path = filename   # 保存パスを更新
                add_to_recent_files(self.recent_files, filename)
                save_recent_files(self.recent_files_path, self.recent_files)

    def _save_image(self):
        """生成画像を保存"""
        if not self.generated_image:
            messagebox.showwarning("警告", "保存する画像がありません")
            return

        # タイトルからデフォルトファイル名を生成
        title = self.title_entry.get().strip()
        base_filename = self._get_safe_filename(title) if title else "output"

        # API生成画像には「_API」サフィックスを付ける
        if self._image_generated_by_api:
            default_filename = f"{base_filename}_API"
        else:
            default_filename = base_filename

        filename = filedialog.asksaveasfilename(
            initialfile=default_filename,
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        if filename:
            self.generated_image.save(filename)

            # YAMLにメタデータを追加（保存済みYAMLがある場合）
            if self.last_saved_yaml_path and os.path.exists(self.last_saved_yaml_path):
                success, error = update_yaml_metadata(self.last_saved_yaml_path, filename)
                if success:
                    messagebox.showinfo(
                        "保存完了",
                        f"画像を保存しました:\n{filename}\n\n"
                        f"YAMLファイルにメタデータを追加しました:\n{os.path.basename(self.last_saved_yaml_path)}"
                    )
                else:
                    messagebox.showinfo("保存完了", f"画像を保存しました:\n{filename}")
            else:
                messagebox.showinfo("保存完了", f"画像を保存しました:\n{filename}")

    # === Scene Builder ===

    def _open_scene_builder(self):
        """シーンビルダーを開く"""
        SceneBuilderWindow(self, callback=self._on_scene_builder_yaml)

    def _on_scene_builder_yaml(self, yaml_content: str):
        """シーンビルダーからYAMLを受け取る"""
        self.yaml_textbox.delete("1.0", tk.END)
        self.yaml_textbox.insert("1.0", yaml_content)

    # === Manga Composer ===

    def _open_manga_composer(self):
        """漫画ページコンポーザーを開く"""
        MangaComposerWindow(self)

    # === Image Tools ===

    def _open_bg_remover(self):
        """背景透過ツールを開く"""
        BgRemoverWindow(self)


def main():
    app = MangaGeneratorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
