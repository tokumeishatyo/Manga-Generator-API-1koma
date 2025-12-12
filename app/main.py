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
    COLOR_MODES, DUOTONE_COLORS, OUTPUT_TYPES, OUTPUT_STYLES, ASPECT_RATIOS
)

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
from ui.background_window import BackgroundWindow
from ui.pose_window import PoseWindow
from ui.effect_window import EffectWindow
from ui.decorative_text_window import DecorativeTextWindow
from ui.four_panel_window import FourPanelWindow
from ui.manga_composer_window import MangaComposerWindow

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
            width=180,
            command=self._on_output_type_change
        )
        self.output_type_menu.set("キャラデザイン（全身）")
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
        self.manga_composer_button.pack(fill="x", padx=10, pady=(0, 10))

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
        self.settings_status_label.configure(text="設定: 未設定")

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
            # 清書モード：詳細設定不要、設定ボタンを無効化
            self.settings_button.configure(state="disabled")
            self.settings_status_label.configure(
                text="清書モード: 詳細設定不要",
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

        if output_type == "キャラデザイン（全身）":
            CharacterSheetWindow(
                self,
                sheet_type="fullbody",
                callback=self._on_settings_complete,
                initial_data=self.current_settings
            )
        elif output_type == "キャラデザイン（顔）":
            CharacterSheetWindow(
                self,
                sheet_type="face",
                callback=self._on_settings_complete,
                initial_data=self.current_settings
            )
        elif output_type == "ポーズ付きキャラ":
            PoseWindow(
                self,
                callback=self._on_settings_complete,
                initial_data=self.current_settings
            )
        elif output_type == "エフェクト追加":
            EffectWindow(
                self,
                callback=self._on_settings_complete,
                initial_data=self.current_settings
            )
        elif output_type == "背景のみ生成":
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
        else:
            messagebox.showinfo("情報", f"'{output_type}'の設定ウィンドウは未実装です")

    def _on_settings_complete(self, data: dict):
        """設定完了時のコールバック"""
        self.current_settings = data
        self.settings_status_label.configure(text="設定: 設定済み ✓", text_color="green")

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
            if output_type in ["キャラデザイン（全身）", "キャラデザイン（顔）"]:
                yaml_content = self._generate_character_sheet_yaml(
                    color_mode, duotone_color, output_style, aspect_ratio, title, author, include_title_in_image
                )
            elif output_type == "背景のみ生成":
                yaml_content = self._generate_background_yaml(
                    color_mode, duotone_color, output_style, aspect_ratio, title, author, include_title_in_image
                )
            elif output_type == "ポーズ付きキャラ":
                yaml_content = self._generate_pose_yaml(
                    color_mode, duotone_color, output_style, aspect_ratio, title, author, include_title_in_image
                )
            elif output_type == "エフェクト追加":
                yaml_content = self._generate_effect_yaml(
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
        description = settings.get('description', '')
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
        views = "front view, side view, back view" if sheet_type == "fullbody" else "front view, side view, 3/4 view"

        # 顔三面図専用の指示（素体ヘッドショット）
        face_headshot_instruction = ""
        if sheet_type == "face":
            face_headshot_instruction = """
# IMPORTANT: Face Reference Sheet Instructions
headshot_specification:
  type: "Character design base body (sotai) headshot for reference sheet"
  coverage: "From top of head to base of neck (around collarbone level)"
  clothing: "NONE - Do not include any clothing or accessories"
  accessories: "NONE - No jewelry, headwear, or decorations"
  state: "Clean base body state only"
  background: "Pure white background"
  purpose: "This is professional character design reference material"
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

views: "{views}"

constraints:
  - Maintain consistent design across all views
  - White or simple background for clarity
  - Clean linework suitable for reference
{'''  - This is a HEAD/FACE ONLY reference - show from top of head to neck/collarbone
  - Do NOT draw any clothing, accessories, or decorations
  - Keep the character in clean base body state''' if sheet_type == 'face' else ''}

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

        if image_path:
            yaml_content += f'\nreference_image: "{os.path.basename(image_path)}"'

        return yaml_content

    def _generate_background_yaml(self, color_mode, duotone_color, output_style, aspect_ratio, title, author, include_title_in_image):
        """背景生成用YAML生成"""
        settings = self.current_settings
        description = settings.get('description', '')

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
        """ポーズ付きキャラ用YAML生成（character_pose.yaml準拠）"""
        settings = self.current_settings
        from ui.pose_window import (
            ACTION_CATEGORIES, DYNAMISM_LEVELS, WIND_EFFECTS, CAMERA_ANGLES, ZOOM_LEVELS
        )
        from constants import CHARACTER_FACING, CHARACTER_POSES

        preset = settings.get('preset', '（プリセットなし）')
        image_path = settings.get('image_path', '')
        identity = settings.get('identity_preservation', 0.85)
        facing = CHARACTER_FACING.get(settings.get('facing', '→右向き'), 'Facing Right')
        eye_line = settings.get('eye_line', '相手を見る')
        category = ACTION_CATEGORIES.get(settings.get('action_category', '攻撃（魔法）'), 'Magic Attack')
        pose = CHARACTER_POSES.get(settings.get('pose', '攻撃'), 'attacking')
        action_desc = settings.get('action_description', '')
        dynamism = DYNAMISM_LEVELS.get(settings.get('dynamism', '誇張'), 'High (Exaggerated)')
        include_effects = settings.get('include_effects', False)
        wind = WIND_EFFECTS.get(settings.get('wind_effect', '前からの風'), 'Strong Wind from Front')
        camera = CAMERA_ANGLES.get(settings.get('camera_angle', '真横（格ゲー風）'), 'Side View (Fighting Game)')
        zoom = ZOOM_LEVELS.get(settings.get('zoom', '全身'), 'Full Body')
        additional_prompt = settings.get('additional_prompt', '')

        # プリセットコメント
        preset_comment = f"# Preset: {preset}\n" if preset != "（プリセットなし）" else ""

        # 追加プロンプトセクション
        additional_section = ""
        if additional_prompt:
            additional_section = f"""
additional_details:
  - {additional_prompt}
"""

        yaml_content = f"""# Character Pose Generation (character_pose.yaml準拠)
{preset_comment}type: character_pose
title: "{title or 'Character Pose'}"
author: "{author}"

input:
  character_image: "{os.path.basename(image_path) if image_path else ''}"
  identity_preservation: {identity}

settings:
  orientation:
    body_direction: "{facing}"
    eye_line: "{eye_line}"
  action:
    category: "{category}"
    pose_type: "{pose}"
    description: "{action_desc}"
    dynamism: "{dynamism}"
  visuals:
    include_effects: {str(include_effects).lower()}
    wind_effect: "{wind}"
  camera:
    angle: "{camera}"
    zoom: "{zoom}"
{additional_section}
constraints:
  - Preserve character design and colors from input image
  - No background (transparent or simple backdrop)
  - Clean silhouette for compositing

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

    def _generate_effect_yaml(self, color_mode, duotone_color, output_style, aspect_ratio, title, author, include_title_in_image):
        """エフェクト追加用YAML生成（character_effect.yaml準拠）"""
        settings = self.current_settings
        from ui.effect_window import (
            PRESERVATION_LEVELS, ATTACK_EFFECT_TYPES, STATE_EFFECT_TYPES,
            EFFECT_LAYERS, TARGET_AREAS, BACKGROUND_EFFECT_STYLES,
            COMPOSITE_MODES, VFX_STYLES, INTENSITY_LEVELS
        )

        image_path = settings.get('image_path', '')
        preservation = PRESERVATION_LEVELS.get(
            settings.get('preservation_level', '厳密（1ピクセルも変えない）'), 'Strict'
        )

        # 攻撃エフェクト
        attack = settings.get('attack_effect', {})
        attack_type = ATTACK_EFFECT_TYPES.get(attack.get('type', 'エネルギービーム'), 'Energy Beam')
        attack_origin = attack.get('origin', '')
        attack_direction = attack.get('direction', '')
        attack_color = attack.get('color', '')
        attack_texture = attack.get('texture', '')

        # 状態エフェクト
        state = settings.get('state_effect', {})
        state_type = STATE_EFFECT_TYPES.get(state.get('type', 'オーラ'), 'Aura')
        state_area = TARGET_AREAS.get(state.get('area', '全身'), 'Full Body')
        state_layer = EFFECT_LAYERS.get(state.get('layer', 'キャラの背面'), 'Behind')
        state_visual = state.get('visual', '')

        # 背景エフェクト
        bg = settings.get('background_effect', {})
        bg_style = BACKGROUND_EFFECT_STYLES.get(bg.get('style', '必殺技カットイン'), 'Super Move Cut-in')
        bg_composite = COMPOSITE_MODES.get(bg.get('composite_mode', '背景を置き換え'), 'Replace Background')

        # グローバルスタイル
        global_style = settings.get('global_style', {})
        vfx_style = VFX_STYLES.get(global_style.get('vfx_style', 'アニメ/格ゲー風'), 'Anime/Fighting Game, Cel Shaded VFX')
        intensity = INTENSITY_LEVELS.get(global_style.get('intensity', '派手'), 'High (Hype)')

        yaml_content = f"""# VFX Effect Addition (character_effect.yaml準拠)
type: character_effect
title: "{title or 'Character VFX'}"
author: "{author}"

input:
  posed_character_image: "{os.path.basename(image_path) if image_path else ''}"
  character_preservation: "{preservation}"

settings:
  attack_effect:
    type: "{attack_type}"
    origin: "{attack_origin}"
    direction: "{attack_direction}"
    color: "{attack_color}"
    texture: "{attack_texture}"
  state_effect:
    type: "{state_type}"
    target_area: "{state_area}"
    layer: "{state_layer}"
    visual: "{state_visual}"
  background_effect:
    style: "{bg_style}"
    composite_mode: "{bg_composite}"
  global_style:
    vfx_style: "{vfx_style}"
    intensity: "{intensity}"

constraints:
  - DO NOT modify the character at all - preserve every pixel
  - Effects should enhance the character action
  - Maintain visual coherence with character style

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

        type_key = TEXT_TYPES.get(text_type, 'special_move_title')

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
  background: "Transparent"

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
  background: "Transparent"

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
  background: "Transparent"

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
  background: "Transparent"

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
  background: "Transparent"

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
  background: "Transparent"

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

        yaml_content = f"""# 4コマ漫画生成 (four_panel_manga.yaml準拠)
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

    # === API Image Generation ===

    def _generate_redraw_image(self):
        """清書モード専用：参考画像を高画質化"""
        # APIキーチェック
        api_key = self.api_key_entry.get().strip()
        if not api_key:
            messagebox.showwarning("警告", "API Keyを入力してください")
            return

        # 参考画像チェック
        ref_image_path = self.ref_image_entry.get().strip()
        if not ref_image_path or not os.path.exists(ref_image_path):
            messagebox.showwarning("警告", "参考画像を選択してください")
            return

        # タイトル必須チェック（ファイル名用）
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning("警告", "タイトルを入力してください（ファイル名に使用します）")
            self.title_entry.focus_set()
            return

        # 確認ダイアログ
        confirm_msg = (
            "【清書モード】画像の高画質化を実行します\n\n"
            f"参考画像: {os.path.basename(ref_image_path)}\n"
            f"解像度: {self.resolution_var.get()}\n"
            "\n※ 詳細設定・YAMLは不要です\n"
            "※ API呼び出しには料金がかかります\n\n"
            "実行しますか？"
        )
        if not messagebox.askyesno("生成確認", confirm_msg):
            return

        # 生成中表示
        self.generate_button.configure(state="disabled", text="清書中...")
        self.preview_label.configure(text="画像を高画質化中...\n経過時間: 0秒", image=None)

        # 経過時間タイマー開始
        self._generation_start_time = time.time()
        self._start_progress_timer()

        # 解像度を取得
        resolution = self.resolution_var.get()

        # YAMLプレビューに清書モード情報を表示
        redraw_info = f"""# 清書モード（High-Fidelity Redraw）
# YAML設定は使用されません

mode: redraw
source_image: "{os.path.basename(ref_image_path)}"
resolution: "{resolution}"
title: "{title or '(未設定)'}"

# 処理内容:
# - 元画像の構図・キャラクター・色彩を100%保持
# - 解像度・線の鮮明さ・ディテールのみ向上
"""
        self.yaml_textbox.delete("1.0", tk.END)
        self.yaml_textbox.insert("1.0", redraw_info)

        def generate():
            try:
                result = generate_image_with_api(
                    api_key=api_key,
                    yaml_prompt="",  # 清書モードでは空（api_client側で専用プロンプト使用）
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
        default_filename = self._get_safe_filename(title) if title else "output"

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


def main():
    app = MangaGeneratorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
