# -*- coding: utf-8 -*-
"""
1コマ漫画生成アプリ
メインUIモジュール
"""

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import pyperclip
from PIL import Image, ImageTk

# Import constants
from constants import (
    MAX_CHARACTERS,
    COLOR_MODES, DUOTONE_COLORS, OUTPUT_TYPES, OUTPUT_STYLES,
    TEXT_POSITIONS, DECORATIVE_TEXT_STYLES, ASPECT_RATIOS, OUTFIT_DATA,
    SCENE_PLACEHOLDERS, CHARACTER_DESCRIPTION_PLACEHOLDER
)

# Import logic modules
from logic.character import generate_outfit_prompt, get_shape_options
from logic.yaml_generator import (
    generate_illustration_yaml,
    generate_decorative_yaml,
    build_characters_list,
    build_speeches_list,
    build_texts_list
)
from logic.api_client import generate_image_with_api
from logic.file_manager import (
    load_template, load_recent_files, save_recent_files,
    add_to_recent_files, save_yaml_file, load_yaml_file,
    parse_yaml_to_ui_data
)
from ui.scene_builder_window import SceneBuilderWindow

# Set appearance mode and default color theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class SinglePanelApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window configuration
        self.title("1コマ漫画生成アプリ")
        self.geometry("1800x1000")

        # Layout configuration - Three column layout
        self.grid_columnconfigure(0, weight=1, minsize=350)  # Left column (settings + scene/speeches)
        self.grid_columnconfigure(1, weight=2, minsize=550)  # Center column (characters only)
        self.grid_columnconfigure(2, weight=1, minsize=380)  # Right column (preview)
        self.grid_rowconfigure(0, weight=1)

        # Load template
        self.template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "template.yaml")
        self.template_data = load_template(self.template_path)

        # Recent files history
        self.recent_files_path = os.path.join(os.path.dirname(__file__), "recent_files.json")
        self.recent_files = load_recent_files(self.recent_files_path)

        # Character data storage
        self.char_enabled_vars = []
        self.char_enabled_checkboxes = []
        self.char_name_entries = []
        self.char_description_textboxes = []
        self.char_image_attach_vars = []
        self.char_image_path_entries = []
        self.char_image_path_browses = []
        self.char_outfit_frames = []
        self.char_outfit_categories = []
        self.char_outfit_shapes = []
        self.char_outfit_colors = []
        self.char_outfit_patterns = []
        self.char_outfit_styles = []
        self.char_outfit_previews = []
        self.char_widgets = []  # For hiding/showing

        # Speech data storage
        self.speech_entries = []
        self.speech_position_menus = []
        self.speech_frames = []

        # Build UI
        self._build_left_column()
        self._build_center_column()
        self._build_right_column()

        # Update speech visibility based on initial character states
        self.update_speech_visibility()

    def _build_left_column(self):
        """左列を構築（設定 + シーン/セリフ）"""
        # ========== LEFT COLUMN (Settings + Scene/Speeches - Scrollable) ==========
        self.left_column = ctk.CTkFrame(self)
        self.left_column.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")
        self.left_column.grid_columnconfigure(0, weight=1)
        self.left_column.grid_rowconfigure(0, weight=1)

        # Create scrollable frame for left column
        self.left_scroll = ctk.CTkScrollableFrame(self.left_column)
        self.left_scroll.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.left_scroll.grid_columnconfigure(0, weight=1)

        # --- Output Mode Selection (API/YAML) ---
        self.output_mode_frame = ctk.CTkFrame(self.left_scroll)
        self.output_mode_frame.grid(row=0, column=0, padx=5, pady=(5, 5), sticky="ew")
        self.output_mode_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.output_mode_frame, text="出力モード:", font=("Arial", 11, "bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.output_mode_var = tk.StringVar(value="yaml")
        self.output_mode_var.trace_add("write", self.on_output_mode_change)

        output_radio_frame = ctk.CTkFrame(self.output_mode_frame, fg_color="transparent")
        output_radio_frame.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        self.api_output_radio = ctk.CTkRadioButton(output_radio_frame, text="画像出力(API)", variable=self.output_mode_var, value="api")
        self.api_output_radio.pack(side="left", padx=(0, 10))

        self.yaml_output_radio = ctk.CTkRadioButton(output_radio_frame, text="YAML出力", variable=self.output_mode_var, value="yaml")
        self.yaml_output_radio.pack(side="left")

        # API Key input
        ctk.CTkLabel(self.output_mode_frame, text="API Key:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.api_key_entry = ctk.CTkEntry(self.output_mode_frame, placeholder_text="Google AI API Key", show="*", state="disabled")
        self.api_key_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # API Submode (通常 / 参考画像清書)
        ctk.CTkLabel(self.output_mode_frame, text="APIモード:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        api_submode_frame = ctk.CTkFrame(self.output_mode_frame, fg_color="transparent")
        api_submode_frame.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        self.api_submode_var = tk.StringVar(value="normal")
        self.api_normal_radio = ctk.CTkRadioButton(api_submode_frame, text="通常", variable=self.api_submode_var, value="normal", state="disabled")
        self.api_normal_radio.pack(side="left", padx=(0, 10))
        self.api_redraw_radio = ctk.CTkRadioButton(api_submode_frame, text="参考画像清書", variable=self.api_submode_var, value="redraw", state="disabled")
        self.api_redraw_radio.pack(side="left")

        # Reference image for redraw mode
        ctk.CTkLabel(self.output_mode_frame, text="参考画像:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        ref_image_frame = ctk.CTkFrame(self.output_mode_frame, fg_color="transparent")
        ref_image_frame.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        ref_image_frame.grid_columnconfigure(0, weight=1)

        self.ref_image_entry = ctk.CTkEntry(ref_image_frame, placeholder_text="ブラウザ版で生成した下書き画像", state="disabled")
        self.ref_image_entry.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        self.ref_image_browse = ctk.CTkButton(ref_image_frame, text="参照", width=50, state="disabled", command=self.browse_ref_image)
        self.ref_image_browse.grid(row=0, column=1)

        # --- Basic Info Area ---
        self.basic_frame = ctk.CTkFrame(self.left_scroll)
        self.basic_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.basic_frame.grid_columnconfigure(1, weight=1)

        # Title
        ctk.CTkLabel(self.basic_frame, text="タイトル:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.title_entry = ctk.CTkEntry(self.basic_frame, placeholder_text="作品タイトル")
        self.title_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # Author
        ctk.CTkLabel(self.basic_frame, text="作者名:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.author_entry = ctk.CTkEntry(self.basic_frame, placeholder_text="Unknown")
        self.author_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # --- Style & Color Mode ---
        self.style_frame = ctk.CTkFrame(self.left_scroll)
        self.style_frame.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        self.style_frame.grid_columnconfigure(1, weight=1)

        # Color Mode
        ctk.CTkLabel(self.style_frame, text="カラーモード:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        color_mode_frame = ctk.CTkFrame(self.style_frame, fg_color="transparent")
        color_mode_frame.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        self.color_mode_var = tk.StringVar(value="フルカラー")
        self.color_mode_menu = ctk.CTkOptionMenu(
            color_mode_frame,
            values=list(COLOR_MODES.keys()),
            width=120,
            command=self.on_color_mode_change
        )
        self.color_mode_menu.set("フルカラー")
        self.color_mode_menu.pack(side="left", padx=(0, 10))

        # Duotone color selection (initially hidden)
        self.duotone_color_menu = ctk.CTkOptionMenu(
            color_mode_frame,
            values=list(DUOTONE_COLORS.keys()),
            width=100
        )
        self.duotone_color_menu.set("赤×黒")
        # Don't pack yet - will be shown when duotone is selected

        # Output Type (Illustration / Character Sheet)
        ctk.CTkLabel(self.style_frame, text="出力タイプ:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        output_type_frame = ctk.CTkFrame(self.style_frame, fg_color="transparent")
        output_type_frame.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        self.output_type_var = tk.StringVar(value="イラスト生成")
        self.output_type_menu = ctk.CTkOptionMenu(
            output_type_frame,
            values=list(OUTPUT_TYPES.keys()),
            width=120,
            command=self.on_output_type_change
        )
        self.output_type_menu.set("イラスト生成")
        self.output_type_menu.pack(side="left")

        # Output Style
        ctk.CTkLabel(self.style_frame, text="出力スタイル:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.output_style_menu = ctk.CTkOptionMenu(self.style_frame, values=list(OUTPUT_STYLES.keys()), width=180)
        self.output_style_menu.set("おまかせ")
        self.output_style_menu.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        # Resolution (for API mode)
        ctk.CTkLabel(self.style_frame, text="画質:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        resolution_frame = ctk.CTkFrame(self.style_frame, fg_color="transparent")
        resolution_frame.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        self.resolution_var = tk.StringVar(value="2k")
        self.resolution_1k_radio = ctk.CTkRadioButton(resolution_frame, text="1K", variable=self.resolution_var, value="1k", state="disabled")
        self.resolution_1k_radio.pack(side="left", padx=(0, 10))
        self.resolution_2k_radio = ctk.CTkRadioButton(resolution_frame, text="2K", variable=self.resolution_var, value="2k", state="disabled")
        self.resolution_2k_radio.pack(side="left", padx=(0, 10))
        self.resolution_4k_radio = ctk.CTkRadioButton(resolution_frame, text="4K", variable=self.resolution_var, value="4k", state="disabled")
        self.resolution_4k_radio.pack(side="left")

        # Aspect Ratio
        ctk.CTkLabel(self.style_frame, text="アスペクト比:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        aspect_ratio_frame = ctk.CTkFrame(self.style_frame, fg_color="transparent")
        aspect_ratio_frame.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        self.aspect_ratio_var = tk.StringVar(value="1:1")
        self.aspect_ratio_radios = []
        for i, (label, value) in enumerate(ASPECT_RATIOS.items()):
            radio = ctk.CTkRadioButton(aspect_ratio_frame, text=label, variable=self.aspect_ratio_var, value=value, width=60)
            radio.pack(side="left", padx=(0, 8))
            self.aspect_ratio_radios.append(radio)

        # --- Scene Description (in left column) ---
        self.scene_frame = ctk.CTkFrame(self.left_scroll)
        self.scene_frame.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        self.scene_frame.grid_columnconfigure(0, weight=1)

        scene_header_frame = ctk.CTkFrame(self.scene_frame, fg_color="transparent")
        scene_header_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")

        ctk.CTkLabel(scene_header_frame, text="シーン説明", font=("Arial", 14, "bold")).pack(side="left")

        self.scene_builder_button = ctk.CTkButton(
            scene_header_frame,
            text="シーンビルダー",
            width=120,
            height=25,
            command=self.open_scene_builder
        )
        self.scene_builder_button.pack(side="right")

        self.scene_textbox = ctk.CTkTextbox(self.scene_frame, height=100)
        self.scene_textbox.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.scene_textbox.insert("1.0", SCENE_PLACEHOLDERS[0])
        self.scene_textbox.bind("<FocusIn>", lambda e: self.clear_placeholder(self.scene_textbox, SCENE_PLACEHOLDERS[0]))

        # --- Speeches Section (in left column) ---
        self.speech_section_frame = ctk.CTkFrame(self.left_scroll)
        self.speech_section_frame.grid(row=4, column=0, padx=5, pady=5, sticky="ew")
        self.speech_section_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.speech_section_frame, text="セリフ", font=("Arial", 14, "bold")).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        # Speech entries container (will be populated based on enabled characters)
        self.speeches_container = ctk.CTkFrame(self.speech_section_frame, fg_color="transparent")
        self.speeches_container.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.speeches_container.grid_columnconfigure(1, weight=1)

        # Create speech entries for each character
        for i in range(MAX_CHARACTERS):
            self.create_speech_ui(i)

        # --- Text Placement Section (in left column) ---
        self.text_section_frame = ctk.CTkFrame(self.left_scroll)
        self.text_section_frame.grid(row=5, column=0, padx=5, pady=5, sticky="ew")
        self.text_section_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.text_section_frame, text="テキスト配置", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 5), sticky="w")

        # Narration inputs (3 slots)
        self.narration_entries = []
        self.narration_position_menus = []
        for i in range(3):
            ctk.CTkLabel(self.text_section_frame, text=f"ナレーション{i+1}:").grid(row=i+1, column=0, padx=10, pady=3, sticky="w")
            entry = ctk.CTkEntry(self.text_section_frame, placeholder_text="状況説明やナレーション")
            entry.grid(row=i+1, column=1, padx=5, pady=3, sticky="ew")
            self.narration_entries.append(entry)

            position_menu = ctk.CTkOptionMenu(self.text_section_frame, values=list(TEXT_POSITIONS.keys()), width=80)
            position_menu.set(["左上", "中央上", "右上"][i])  # Default positions
            position_menu.grid(row=i+1, column=2, padx=(5, 10), pady=3)
            self.narration_position_menus.append(position_menu)

        # --- Decorative Text Section (for decorative_text mode, in left column) ---
        self.decorative_section_frame = ctk.CTkFrame(self.left_scroll)
        self.decorative_section_frame.grid(row=6, column=0, padx=5, pady=5, sticky="ew")
        self.decorative_section_frame.grid_columnconfigure(1, weight=1)
        self.decorative_section_frame.grid_forget()  # Hidden by default

        ctk.CTkLabel(self.decorative_section_frame, text="装飾テキスト", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=4, padx=10, pady=(10, 5), sticky="w")

        # Decorative text inputs (3 slots)
        self.decorative_entries = []
        self.decorative_position_menus = []
        self.decorative_style_menus = []
        for i in range(3):
            ctk.CTkLabel(self.decorative_section_frame, text=f"テキスト{i+1}:").grid(row=i+1, column=0, padx=10, pady=3, sticky="w")
            entry = ctk.CTkEntry(self.decorative_section_frame, placeholder_text="装飾テキストを入力")
            entry.grid(row=i+1, column=1, padx=5, pady=3, sticky="ew")
            self.decorative_entries.append(entry)

            position_menu = ctk.CTkOptionMenu(self.decorative_section_frame, values=list(TEXT_POSITIONS.keys()), width=80)
            position_menu.set(["中央上", "中央", "右下"][i])  # Default positions
            position_menu.grid(row=i+1, column=2, padx=5, pady=3)
            self.decorative_position_menus.append(position_menu)

            style_menu = ctk.CTkOptionMenu(self.decorative_section_frame, values=list(DECORATIVE_TEXT_STYLES.keys()), width=100)
            style_menu.set(["タイトル", "サブタイトル", "クレジット"][i])  # Default styles
            style_menu.grid(row=i+1, column=3, padx=(5, 10), pady=3)
            self.decorative_style_menus.append(style_menu)

        # --- Generate and Clear Buttons (in left column) ---
        self.button_frame = ctk.CTkFrame(self.left_scroll, fg_color="transparent")
        self.button_frame.grid(row=7, column=0, padx=5, pady=(10, 10), sticky="ew")
        self.button_frame.grid_columnconfigure(0, weight=3)
        self.button_frame.grid_columnconfigure(1, weight=1)

        self.generate_btn = ctk.CTkButton(self.button_frame, text="Generate (YAML生成)", height=40, font=("Arial", 16, "bold"), command=self.generate_yaml)
        self.generate_btn.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self.clear_btn = ctk.CTkButton(self.button_frame, text="全てクリア", height=40, font=("Arial", 14), fg_color="gray", hover_color="darkgray", command=self.clear_all)
        self.clear_btn.grid(row=0, column=1, sticky="ew")

    def _build_center_column(self):
        """中央列を構築（キャラクターのみ）"""
        # ========== CENTER COLUMN (Characters only - Scrollable) ==========
        self.center_column = ctk.CTkFrame(self)
        self.center_column.grid(row=0, column=1, padx=5, pady=10, sticky="nsew")
        self.center_column.grid_columnconfigure(0, weight=1)
        self.center_column.grid_rowconfigure(0, weight=1)

        # Create scrollable frame for center column
        self.center_scroll = ctk.CTkScrollableFrame(self.center_column)
        self.center_scroll.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.center_scroll.grid_columnconfigure(0, weight=1)

        # --- Characters Section ---
        self.char_section_frame = ctk.CTkFrame(self.center_scroll)
        self.char_section_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.char_section_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.char_section_frame, text="登場人物", font=("Arial", 14, "bold")).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        # Create 5 character input sections
        for i in range(MAX_CHARACTERS):
            self.create_character_ui(i)

    def _build_right_column(self):
        """右列を構築（プレビュー）"""
        # ========== RIGHT COLUMN (Preview) ==========
        self.right_column = ctk.CTkFrame(self)
        self.right_column.grid(row=0, column=2, padx=(5, 10), pady=10, sticky="nsew")
        self.right_column.grid_columnconfigure(0, weight=1)
        self.right_column.grid_rowconfigure(0, weight=0)  # YAML preview - fixed height
        self.right_column.grid_rowconfigure(1, weight=0)  # YAML action buttons
        self.right_column.grid_rowconfigure(2, weight=1)  # Image preview - expands
        self.right_column.grid_rowconfigure(3, weight=0)  # Image action buttons

        # --- YAML Preview Area ---
        self.preview_frame = ctk.CTkFrame(self.right_column)
        self.preview_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="nsew")
        self.preview_frame.grid_columnconfigure(0, weight=1)
        self.preview_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.preview_frame, text="YAMLプレビュー", font=("Arial", 14, "bold")).grid(row=0, column=0, padx=10, pady=(5, 2), sticky="w")

        self.preview_textbox = ctk.CTkTextbox(self.preview_frame, height=180)
        self.preview_textbox.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        # --- YAML Action Buttons ---
        self.action_frame = ctk.CTkFrame(self.right_column)
        self.action_frame.grid(row=1, column=0, padx=10, pady=2, sticky="ew")

        self.load_btn = ctk.CTkButton(self.action_frame, text="読込", width=60, command=self.load_yaml)
        self.load_btn.pack(side="left", padx=2, pady=5)

        # Recent files dropdown
        self.recent_files_var = tk.StringVar(value="履歴")
        self.recent_files_menu = ctk.CTkOptionMenu(
            self.action_frame,
            values=["履歴なし"],
            variable=self.recent_files_var,
            command=self.on_recent_file_selected,
            width=60
        )
        self.recent_files_menu.pack(side="left", padx=2, pady=5)
        self.update_recent_files_menu()

        self.copy_btn = ctk.CTkButton(self.action_frame, text="コピー", width=60, state="disabled", command=self.copy_to_clipboard)
        self.copy_btn.pack(side="left", padx=2, pady=5)

        self.save_btn = ctk.CTkButton(self.action_frame, text="保存", width=60, state="disabled", command=self.save_yaml)
        self.save_btn.pack(side="left", padx=2, pady=5)

        self.generated_yaml = ""

        # --- Image Preview Area ---
        self.image_preview_frame = ctk.CTkFrame(self.right_column)
        self.image_preview_frame.grid(row=2, column=0, padx=10, pady=(10, 5), sticky="nsew")
        self.image_preview_frame.grid_columnconfigure(0, weight=1)
        self.image_preview_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.image_preview_frame, text="画像プレビュー", font=("Arial", 14, "bold")).grid(row=0, column=0, padx=10, pady=(5, 2), sticky="w")

        self.image_label = ctk.CTkLabel(self.image_preview_frame, text="生成された画像がここに表示されます\n\n(API出力モード時のみ)", font=("Arial", 12), text_color="gray")
        self.image_label.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.generated_image = None
        self.photo_image = None

        # --- Image Action Buttons ---
        self.image_action_frame = ctk.CTkFrame(self.right_column)
        self.image_action_frame.grid(row=3, column=0, padx=10, pady=(2, 10), sticky="ew")

        self.save_image_btn = ctk.CTkButton(self.image_action_frame, text="画像を保存", state="disabled", command=self.save_image)
        self.save_image_btn.pack(side="left", expand=True, padx=5, pady=5)

    def create_character_ui(self, index):
        """Create UI for a single character"""
        char_num = index + 1
        is_default_enabled = index < 2  # First 2 characters enabled by default

        # Main character frame
        char_frame = ctk.CTkFrame(self.char_section_frame)
        char_frame.grid(row=index + 1, column=0, padx=5, pady=2, sticky="ew")
        char_frame.grid_columnconfigure(1, weight=1)

        # Enable checkbox and name
        header_frame = ctk.CTkFrame(char_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=2, sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)

        enabled_var = tk.BooleanVar(value=is_default_enabled)
        enabled_var.trace_add("write", lambda *args, idx=index: self.on_char_enabled_change(idx))
        self.char_enabled_vars.append(enabled_var)

        enabled_checkbox = ctk.CTkCheckBox(header_frame, text=f"キャラ{char_num}", variable=enabled_var, font=("Arial", 12, "bold"))
        enabled_checkbox.grid(row=0, column=0, padx=5, sticky="w")
        self.char_enabled_checkboxes.append(enabled_checkbox)

        name_entry = ctk.CTkEntry(header_frame, placeholder_text=f"キャラ{char_num}の名前", width=150)
        name_entry.grid(row=0, column=1, padx=5, sticky="w")
        self.char_name_entries.append(name_entry)

        # Image attach radio buttons
        image_attach_var = tk.StringVar(value="with_image")
        self.char_image_attach_vars.append(image_attach_var)

        with_image_radio = ctk.CTkRadioButton(header_frame, text="画像あり", variable=image_attach_var, value="with_image")
        with_image_radio.grid(row=0, column=2, padx=5)
        without_image_radio = ctk.CTkRadioButton(header_frame, text="画像なし", variable=image_attach_var, value="without_image")
        without_image_radio.grid(row=0, column=3, padx=5)

        # Description
        ctk.CTkLabel(char_frame, text="説明:").grid(row=1, column=0, padx=10, pady=2, sticky="nw")
        description_textbox = ctk.CTkTextbox(char_frame, height=40)
        description_textbox.grid(row=1, column=1, padx=10, pady=2, sticky="ew")
        description_textbox.insert("1.0", CHARACTER_DESCRIPTION_PLACEHOLDER)
        description_textbox.bind("<FocusIn>", lambda e, tb=description_textbox: self.clear_placeholder(tb, CHARACTER_DESCRIPTION_PLACEHOLDER))
        self.char_description_textboxes.append(description_textbox)

        # Outfit Builder
        outfit_frame = ctk.CTkFrame(char_frame, fg_color="transparent")
        outfit_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=(0, 2), sticky="ew")
        outfit_frame.grid_columnconfigure((1, 2, 3, 4, 5), weight=1)
        self.char_outfit_frames.append(outfit_frame)

        ctk.CTkLabel(outfit_frame, text="服装:", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=0, sticky="w")

        # Category
        outfit_category = ctk.CTkOptionMenu(
            outfit_frame, values=list(OUTFIT_DATA["カテゴリ"].keys()), width=85,
            command=lambda v, idx=index: self.on_outfit_category_change(idx)
        )
        outfit_category.set("おまかせ")
        outfit_category.grid(row=0, column=1, padx=2, pady=0)
        self.char_outfit_categories.append(outfit_category)

        # Shape
        outfit_shape = ctk.CTkOptionMenu(outfit_frame, values=["おまかせ"], width=95, command=lambda v, idx=index: self.update_outfit_preview(idx))
        outfit_shape.set("おまかせ")
        outfit_shape.grid(row=0, column=2, padx=2, pady=0)
        self.char_outfit_shapes.append(outfit_shape)

        # Color
        outfit_color = ctk.CTkOptionMenu(outfit_frame, values=list(OUTFIT_DATA["色"].keys()), width=75, command=lambda v, idx=index: self.update_outfit_preview(idx))
        outfit_color.set("おまかせ")
        outfit_color.grid(row=0, column=3, padx=2, pady=0)
        self.char_outfit_colors.append(outfit_color)

        # Pattern
        outfit_pattern = ctk.CTkOptionMenu(outfit_frame, values=list(OUTFIT_DATA["柄"].keys()), width=85, command=lambda v, idx=index: self.update_outfit_preview(idx))
        outfit_pattern.set("おまかせ")
        outfit_pattern.grid(row=0, column=4, padx=2, pady=0)
        self.char_outfit_patterns.append(outfit_pattern)

        # Style
        outfit_style = ctk.CTkOptionMenu(outfit_frame, values=list(OUTFIT_DATA["スタイル"].keys()), width=85, command=lambda v, idx=index: self.update_outfit_preview(idx))
        outfit_style.set("おまかせ")
        outfit_style.grid(row=0, column=5, padx=2, pady=0)
        self.char_outfit_styles.append(outfit_style)

        # Outfit preview (hidden - placeholder for compatibility)
        outfit_preview = ctk.CTkLabel(outfit_frame, text="")
        self.char_outfit_previews.append(outfit_preview)

        # Image path (for API mode)
        image_path_frame = ctk.CTkFrame(char_frame, fg_color="transparent")
        image_path_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=2, sticky="ew")
        image_path_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(image_path_frame, text="画像パス:").grid(row=0, column=0, padx=5, sticky="w")
        image_path_entry = ctk.CTkEntry(image_path_frame, placeholder_text="キャラクター画像のパス", state="disabled")
        image_path_entry.grid(row=0, column=1, padx=5, sticky="ew")
        self.char_image_path_entries.append(image_path_entry)

        image_path_browse = ctk.CTkButton(image_path_frame, text="参照", width=50, state="disabled", command=lambda idx=index: self.browse_image_path(idx))
        image_path_browse.grid(row=0, column=2, padx=(5, 0))
        self.char_image_path_browses.append(image_path_browse)

        # Store widgets for visibility toggle
        self.char_widgets.append({
            'frame': char_frame,
            'content_widgets': [description_textbox, outfit_frame, image_path_frame]
        })

        # Initially hide content if not enabled
        if not is_default_enabled:
            for widget in self.char_widgets[index]['content_widgets']:
                widget.grid_remove()

    def create_speech_ui(self, index):
        """Create speech input UI for a character"""
        char_num = index + 1

        speech_frame = ctk.CTkFrame(self.speeches_container, fg_color="transparent")
        speech_frame.grid(row=index, column=0, columnspan=3, padx=5, pady=2, sticky="ew")
        speech_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(speech_frame, text=f"キャラ{char_num}:", width=70).grid(row=0, column=0, padx=5, sticky="w")

        speech_entry = ctk.CTkEntry(speech_frame, placeholder_text="セリフを入力")
        speech_entry.grid(row=0, column=1, padx=5, sticky="ew")
        self.speech_entries.append(speech_entry)

        position_menu = ctk.CTkOptionMenu(speech_frame, values=["左", "右"], width=50)
        position_menu.set("左" if index % 2 == 0 else "右")
        position_menu.grid(row=0, column=2, padx=5)
        self.speech_position_menus.append(position_menu)

        self.speech_frames.append(speech_frame)

        # Initially hide if character not enabled
        if index >= 2:
            speech_frame.grid_remove()

    def on_char_enabled_change(self, index):
        """Handle character enabled/disabled checkbox change"""
        is_enabled = self.char_enabled_vars[index].get()

        # Show/hide character content
        for widget in self.char_widgets[index]['content_widgets']:
            if is_enabled:
                widget.grid()
            else:
                widget.grid_remove()

        # Update speech visibility
        self.update_speech_visibility()

    def update_speech_visibility(self):
        """Update speech input visibility based on enabled characters"""
        for i in range(MAX_CHARACTERS):
            is_enabled = self.char_enabled_vars[i].get()
            if is_enabled:
                self.speech_frames[i].grid()
            else:
                self.speech_frames[i].grid_remove()

    def on_outfit_category_change(self, index):
        """Handle outfit category change"""
        category = self.char_outfit_categories[index].get()
        shape_menu = self.char_outfit_shapes[index]

        shapes = get_shape_options(category)
        shape_menu.configure(values=shapes)
        shape_menu.set("おまかせ")

        self.update_outfit_preview(index)

    def update_outfit_preview(self, index):
        """Update outfit prompt preview"""
        prompt = generate_outfit_prompt(
            self.char_outfit_categories[index].get(),
            self.char_outfit_shapes[index].get(),
            self.char_outfit_colors[index].get(),
            self.char_outfit_patterns[index].get(),
            self.char_outfit_styles[index].get()
        )
        self.char_outfit_previews[index].configure(text=prompt if prompt else "(おまかせ)")

    def on_color_mode_change(self, choice):
        """Handle color mode dropdown change"""
        if choice == "二色刷り":
            self.duotone_color_menu.pack(side="left")
        else:
            self.duotone_color_menu.pack_forget()

    def on_output_type_change(self, choice):
        """Handle output type change (Illustration, Character Sheet, Background, Decorative Text)"""
        is_character_sheet = choice in ["全身三面図", "顔三面図"]
        is_face_sheet = choice == "顔三面図"
        is_background = choice == "背景生成"
        is_decorative_text = choice == "装飾テキスト"

        # Show/hide decorative text section (in left_scroll)
        if is_decorative_text:
            self.decorative_section_frame.grid(row=6, column=0, padx=5, pady=5, sticky="ew")
            self.text_section_frame.grid_forget()
        else:
            self.decorative_section_frame.grid_forget()
            self.text_section_frame.grid(row=5, column=0, padx=5, pady=5, sticky="ew")

        if is_decorative_text:
            # For decorative text, disable all character-related inputs, scene, speeches, narrations
            for i in range(MAX_CHARACTERS):
                self.char_enabled_vars[i].set(False)
                self.char_enabled_checkboxes[i].configure(state="disabled")
                self.char_outfit_categories[i].configure(state="disabled")
                self.char_outfit_shapes[i].configure(state="disabled")
                self.char_outfit_colors[i].configure(state="disabled")
                self.char_outfit_patterns[i].configure(state="disabled")
                self.char_outfit_styles[i].configure(state="disabled")

            # Disable speech/narration inputs
            for entry in self.speech_entries:
                entry.configure(state="disabled", placeholder_text="装飾テキストでは使用しません")
            for entry in self.narration_entries:
                entry.configure(state="disabled", placeholder_text="装飾テキストでは使用しません")

            # Disable scene textbox
            self.scene_textbox.delete("1.0", tk.END)
            self.scene_textbox.insert("1.0", "装飾テキストモードではシーン説明は不要です")
            self.scene_textbox.configure(state="disabled")

        elif is_background:
            # Re-enable scene textbox if coming from decorative mode
            self.scene_textbox.configure(state="normal")

            # For background generation, disable all character-related inputs
            for i in range(MAX_CHARACTERS):
                self.char_enabled_vars[i].set(False)
                self.char_enabled_checkboxes[i].configure(state="disabled")
                self.char_outfit_categories[i].configure(state="disabled")
                self.char_outfit_shapes[i].configure(state="disabled")
                self.char_outfit_colors[i].configure(state="disabled")
                self.char_outfit_patterns[i].configure(state="disabled")
                self.char_outfit_styles[i].configure(state="disabled")

            # Disable speech inputs
            for entry in self.speech_entries:
                entry.configure(state="disabled", placeholder_text="背景生成では使用しません")
            for entry in self.narration_entries:
                entry.configure(state="disabled", placeholder_text="背景生成では使用しません")

            # Update scene textbox placeholder for background
            self.scene_textbox.delete("1.0", tk.END)
            self.scene_textbox.insert("1.0", "背景の詳細を記述（場所、時間帯、天候、雰囲気など）")

        elif is_character_sheet:
            # Re-enable scene textbox if coming from decorative mode
            self.scene_textbox.configure(state="normal")

            # For character sheets, only allow 1 character
            # Disable checkboxes for characters 2-5 and uncheck them
            for i in range(1, MAX_CHARACTERS):
                self.char_enabled_vars[i].set(False)
                self.char_enabled_checkboxes[i].configure(state="disabled")
            # Ensure character 1 is enabled
            self.char_enabled_vars[0].set(True)
            self.char_enabled_checkboxes[0].configure(state="disabled")  # Keep checked but disabled

            # Disable speech/narration inputs as they're not needed for character sheets
            for entry in self.speech_entries:
                entry.configure(state="disabled", placeholder_text="三面図では使用しません")
            for entry in self.narration_entries:
                entry.configure(state="disabled", placeholder_text="三面図では使用しません")

            # For face sheet, disable outfit selection (not needed for face only)
            if is_face_sheet:
                self.char_outfit_categories[0].configure(state="disabled")
                self.char_outfit_shapes[0].configure(state="disabled")
                self.char_outfit_colors[0].configure(state="disabled")
                self.char_outfit_patterns[0].configure(state="disabled")
                self.char_outfit_styles[0].configure(state="disabled")
                # Update scene placeholder for face sheet (optional - default: 無表情)
                self.scene_textbox.delete("1.0", tk.END)
                self.scene_textbox.insert("1.0", "（任意）表情などを指定。空欄の場合は無表情")
            else:
                # Re-enable outfit for full body sheet
                self.char_outfit_categories[0].configure(state="normal")
                self.char_outfit_shapes[0].configure(state="normal")
                self.char_outfit_colors[0].configure(state="normal")
                self.char_outfit_patterns[0].configure(state="normal")
                self.char_outfit_styles[0].configure(state="normal")
                # Update scene placeholder for full body sheet (optional - default: 無表情、気をつけ)
                self.scene_textbox.delete("1.0", tk.END)
                self.scene_textbox.insert("1.0", "（任意）表情やポーズを指定。空欄の場合は無表情・気をつけの姿勢")
        else:
            # Illustration mode - re-enable all inputs
            self.scene_textbox.configure(state="normal")

            for i in range(MAX_CHARACTERS):
                self.char_enabled_checkboxes[i].configure(state="normal")
                self.char_outfit_categories[i].configure(state="normal")
                self.char_outfit_shapes[i].configure(state="normal")
                self.char_outfit_colors[i].configure(state="normal")
                self.char_outfit_patterns[i].configure(state="normal")
                self.char_outfit_styles[i].configure(state="normal")
            # Re-enable default characters
            self.char_enabled_vars[0].set(True)
            self.char_enabled_vars[1].set(True)

            # Re-enable speech/narration inputs
            for entry in self.speech_entries:
                entry.configure(state="normal", placeholder_text="セリフを入力")
            for entry in self.narration_entries:
                entry.configure(state="normal", placeholder_text="状況説明やナレーション")

            # Reset scene textbox placeholder
            self.scene_textbox.delete("1.0", tk.END)
            self.scene_textbox.insert("1.0", SCENE_PLACEHOLDERS[0])

        self.update_speech_visibility()

    def on_output_mode_change(self, *args):
        """Handle output mode change (API/YAML)"""
        mode = self.output_mode_var.get()
        if mode == "api":
            self.api_key_entry.configure(state="normal")
            self.api_normal_radio.configure(state="normal")
            self.api_redraw_radio.configure(state="normal")
            self.ref_image_entry.configure(state="normal")
            self.ref_image_browse.configure(state="normal")
            self.resolution_1k_radio.configure(state="normal")
            self.resolution_2k_radio.configure(state="normal")
            self.resolution_4k_radio.configure(state="normal")
            for entry in self.char_image_path_entries:
                entry.configure(state="normal")
            for browse in self.char_image_path_browses:
                browse.configure(state="normal")
            self.generate_btn.configure(text="Generate (画像生成)")
        else:
            self.api_key_entry.configure(state="disabled")
            self.api_normal_radio.configure(state="disabled")
            self.api_redraw_radio.configure(state="disabled")
            self.ref_image_entry.configure(state="disabled")
            self.ref_image_browse.configure(state="disabled")
            self.resolution_1k_radio.configure(state="disabled")
            self.resolution_2k_radio.configure(state="disabled")
            self.resolution_4k_radio.configure(state="disabled")
            for entry in self.char_image_path_entries:
                entry.configure(state="disabled")
            for browse in self.char_image_path_browses:
                browse.configure(state="disabled")
            self.generate_btn.configure(text="Generate (YAML生成)")

    def browse_image_path(self, index):
        """Browse for character image"""
        filename = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]
        )
        if filename:
            self.char_image_path_entries[index].delete(0, tk.END)
            self.char_image_path_entries[index].insert(0, filename)

    def browse_ref_image(self):
        """Browse for reference image (draft from browser version)"""
        filename = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]
        )
        if filename:
            self.ref_image_entry.delete(0, tk.END)
            self.ref_image_entry.insert(0, filename)

    def clear_placeholder(self, textbox, placeholder_text):
        """Clear placeholder text on focus"""
        content = textbox.get("1.0", tk.END).strip()
        if content == placeholder_text:
            textbox.delete("1.0", tk.END)

    def update_recent_files_menu(self):
        """Update recent files dropdown"""
        if self.recent_files:
            display_names = [os.path.basename(f) for f in self.recent_files]
            self.recent_files_menu.configure(values=display_names)
        else:
            self.recent_files_menu.configure(values=["履歴なし"])
        self.recent_files_var.set("履歴")

    def on_recent_file_selected(self, choice):
        """Handle recent file selection"""
        if choice == "履歴なし" or choice == "履歴":
            return
        for filepath in self.recent_files:
            if os.path.basename(filepath) == choice:
                if os.path.exists(filepath):
                    self.load_yaml_file(filepath)
                else:
                    messagebox.showerror("エラー", f"ファイルが見つかりません: {filepath}")
                    self.recent_files.remove(filepath)
                    save_recent_files(self.recent_files_path, self.recent_files)
                    self.update_recent_files_menu()
                break

    def open_scene_builder(self):
        """シーンビルダーウィンドウを開く"""
        SceneBuilderWindow(self, callback=self.set_scene_from_builder)

    def set_scene_from_builder(self, scene_prompt: str):
        """シーンビルダーからのプロンプトをシーン説明に設定"""
        self.scene_textbox.delete("1.0", tk.END)
        self.scene_textbox.insert("1.0", scene_prompt)

    def clear_all(self):
        """Clear all input fields"""
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.color_mode_menu.set("フルカラー")
        self.on_color_mode_change("フルカラー")
        self.output_style_menu.set("おまかせ")

        for i in range(MAX_CHARACTERS):
            self.char_enabled_vars[i].set(i < 2)
            self.char_name_entries[i].delete(0, tk.END)
            self.char_description_textboxes[i].delete("1.0", tk.END)
            self.char_description_textboxes[i].insert("1.0", CHARACTER_DESCRIPTION_PLACEHOLDER)
            self.char_image_attach_vars[i].set("with_image")
            self.char_image_path_entries[i].delete(0, tk.END)
            self.char_outfit_categories[i].set("おまかせ")
            self.on_outfit_category_change(i)

        self.scene_textbox.delete("1.0", tk.END)
        self.scene_textbox.insert("1.0", SCENE_PLACEHOLDERS[0])

        for entry in self.speech_entries:
            entry.delete(0, tk.END)

        for entry in self.narration_entries:
            entry.delete(0, tk.END)

        for entry in self.decorative_entries:
            entry.delete(0, tk.END)

        self.preview_textbox.delete("1.0", tk.END)
        self.generated_yaml = ""
        self.copy_btn.configure(state="disabled")
        self.save_btn.configure(state="disabled")

        self.update_speech_visibility()

    def _collect_character_data(self) -> list:
        """UIからキャラクターデータを収集"""
        char_data = []
        for i in range(MAX_CHARACTERS):
            desc = self.char_description_textboxes[i].get("1.0", tk.END).strip()
            if desc == CHARACTER_DESCRIPTION_PLACEHOLDER:
                desc = ""

            char_data.append({
                'enabled': self.char_enabled_vars[i].get(),
                'name': self.char_name_entries[i].get().strip(),
                'description': desc,
                'image_attach': self.char_image_attach_vars[i].get(),
                'outfit': {
                    'category': self.char_outfit_categories[i].get(),
                    'shape': self.char_outfit_shapes[i].get(),
                    'color': self.char_outfit_colors[i].get(),
                    'pattern': self.char_outfit_patterns[i].get(),
                    'style': self.char_outfit_styles[i].get()
                }
            })
        return char_data

    def _collect_speech_data(self) -> list:
        """UIからセリフデータを収集"""
        speech_data = []
        for i in range(MAX_CHARACTERS):
            speech_data.append({
                'enabled': self.char_enabled_vars[i].get(),
                'text': self.speech_entries[i].get().strip(),
                'position': self.speech_position_menus[i].get()
            })
        return speech_data

    def _collect_narration_data(self) -> list:
        """UIからナレーションデータを収集"""
        narration_data = []
        for i in range(3):
            narration_data.append({
                'content': self.narration_entries[i].get().strip(),
                'position': self.narration_position_menus[i].get()
            })
        return narration_data

    def _collect_decorative_data(self) -> list:
        """UIから装飾テキストデータを収集"""
        decorative_data = []
        for i in range(3):
            decorative_data.append({
                'content': self.decorative_entries[i].get().strip(),
                'position': self.decorative_position_menus[i].get(),
                'style': self.decorative_style_menus[i].get()
            })
        return decorative_data

    def generate_yaml(self):
        """Generate YAML from input values"""
        # Get output type first to determine validation
        output_type_name = self.output_type_menu.get()
        output_type = OUTPUT_TYPES.get(output_type_name, "illustration")
        is_character_sheet = output_type in ["fullbody_sheet", "face_sheet"]
        is_background = output_type == "background"
        is_decorative_text = output_type == "decorative_text"

        # For decorative text mode, generate different YAML
        if is_decorative_text:
            decorative_data = self._collect_decorative_data()
            result, instruction = generate_decorative_yaml(decorative_data)
            if result is None:
                messagebox.showerror("エラー", instruction)
                return
            self.generated_yaml = result
            self._update_preview_and_buttons()
            return

        # Get scene prompt
        scene_prompt = self.scene_textbox.get("1.0", tk.END).strip()
        if scene_prompt in SCENE_PLACEHOLDERS:
            scene_prompt = ""

        # 三面図以外の場合はシーン説明が必須
        if not scene_prompt and not is_character_sheet:
            messagebox.showerror("エラー", "シーン説明を入力してください。")
            return

        # Collect data from UI
        char_data = self._collect_character_data()
        speech_data = self._collect_speech_data()
        narration_data = self._collect_narration_data()

        # Build lists using logic module
        characters = []
        if not is_background:
            characters = build_characters_list(char_data, generate_outfit_prompt)

        # Get character names for speeches
        char_names = []
        for i, char in enumerate(char_data):
            if char.get('enabled', False):
                char_names.append(char.get('name', '').strip() or f"キャラ{i+1}")

        speeches = []
        texts = []
        if not is_character_sheet and not is_background:
            speeches = build_speeches_list(speech_data, char_names)
            texts = build_texts_list(narration_data)

        # Generate YAML
        self.generated_yaml, _ = generate_illustration_yaml(
            scene_prompt=scene_prompt,
            title=self.title_entry.get().strip(),
            author=self.author_entry.get().strip(),
            color_mode_name=self.color_mode_menu.get(),
            duotone_color=self.duotone_color_menu.get(),
            output_style_name=self.output_style_menu.get(),
            output_type_name=output_type_name,
            aspect_ratio=self.aspect_ratio_var.get(),
            characters=characters,
            speeches=speeches,
            texts=texts
        )

        self._update_preview_and_buttons()

        # If API mode, start image generation
        if self.output_mode_var.get() == "api":
            self.start_api_generation()

    def _update_preview_and_buttons(self):
        """プレビューとボタン状態を更新"""
        self.preview_textbox.delete("1.0", tk.END)
        self.preview_textbox.insert("1.0", self.generated_yaml)
        self.copy_btn.configure(state="normal")
        self.save_btn.configure(state="normal")

    def start_api_generation(self):
        """Start API image generation"""
        api_key = self.api_key_entry.get().strip()
        if not api_key:
            messagebox.showerror("エラー", "API Keyを入力してください。")
            return

        # Check API submode
        is_redraw_mode = self.api_submode_var.get() == "redraw"
        ref_image_path = self.ref_image_entry.get().strip() if is_redraw_mode else None

        if is_redraw_mode:
            if not ref_image_path:
                messagebox.showerror("エラー", "参考画像清書モードでは参考画像を指定してください。")
                return
            if not os.path.exists(ref_image_path):
                messagebox.showerror("エラー", f"参考画像が見つかりません:\n{ref_image_path}")
                return

        # Collect character images
        char_images = []
        for i in range(MAX_CHARACTERS):
            if self.char_enabled_vars[i].get():
                path = self.char_image_path_entries[i].get().strip()
                if path and os.path.exists(path):
                    char_images.append(path)

        # Get resolution
        resolution = self.resolution_var.get().upper()

        # Update UI
        self.generate_btn.configure(state="disabled", text="生成中...")
        self.image_label.configure(text="画像を生成中...\nしばらくお待ちください", image=None)

        # Start thread
        thread = threading.Thread(
            target=self._api_generation_thread,
            args=(api_key, self.generated_yaml, char_images, resolution, ref_image_path)
        )
        thread.start()

    def _api_generation_thread(self, api_key, yaml_prompt, char_images, resolution, ref_image_path=None):
        """API generation thread"""
        result = generate_image_with_api(api_key, yaml_prompt, char_images, resolution, ref_image_path)

        if result['success']:
            self.generated_image = result['image']
            self.after(0, self.update_image_preview)
        else:
            error_msg = result['error']
            self.after(0, lambda: messagebox.showerror("APIエラー", f"エラーが発生しました:\n{error_msg}"))
            self.after(0, self.reset_generate_btn)

    def update_image_preview(self):
        """Update image preview display"""
        if self.generated_image:
            try:
                # Resize for preview
                display_size = (380, 500)
                img_copy = self.generated_image.copy()
                img_copy.thumbnail(display_size, Image.Resampling.LANCZOS)

                # Try CTkImage first, fall back to ImageTk.PhotoImage
                try:
                    self.photo_image = ctk.CTkImage(light_image=img_copy, dark_image=img_copy, size=img_copy.size)
                    self.image_label.configure(text="")
                    self.image_label.configure(image=self.photo_image)
                except Exception:
                    # Fallback to standard Tkinter PhotoImage
                    self.photo_image = ImageTk.PhotoImage(img_copy)
                    self.image_label.configure(text="")
                    self.image_label.configure(image=self.photo_image)

                self.save_image_btn.configure(state="normal")
            except Exception as e:
                print(f"Warning: Could not display image preview: {e}")
                self.image_label.configure(text="画像生成完了\n（プレビュー表示エラー）\n\n画像を保存ボタンで保存できます", image=None)
                self.save_image_btn.configure(state="normal")

        self.reset_generate_btn()

    def reset_generate_btn(self):
        """Reset generate button state"""
        self.generate_btn.configure(state="normal")
        if self.output_mode_var.get() == "api":
            self.generate_btn.configure(text="Generate (画像生成)")
        else:
            self.generate_btn.configure(text="Generate (YAML生成)")

    def save_image(self):
        """Save generated image"""
        if not self.generated_image:
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.generated_image.save(filename)
                messagebox.showinfo("成功", "画像を保存しました。")
            except Exception as e:
                messagebox.showerror("エラー", f"保存に失敗しました: {e}")

    def copy_to_clipboard(self):
        """Copy YAML to clipboard"""
        if self.generated_yaml:
            pyperclip.copy(self.generated_yaml)
            messagebox.showinfo("コピー完了", "YAMLをクリップボードにコピーしました。")

    def save_yaml(self):
        """Save YAML to file"""
        if not self.generated_yaml:
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".yaml",
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")]
        )
        if filename:
            success, error = save_yaml_file(filename, self.generated_yaml)
            if success:
                self.recent_files = add_to_recent_files(self.recent_files, filename)
                save_recent_files(self.recent_files_path, self.recent_files)
                self.update_recent_files_menu()
                messagebox.showinfo("成功", "YAMLを保存しました。")
            else:
                messagebox.showerror("エラー", f"保存に失敗しました: {error}")

    def load_yaml(self):
        """Load YAML from file"""
        filename = filedialog.askopenfilename(
            filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")]
        )
        if filename:
            self.load_yaml_file(filename)

    def load_yaml_file(self, filepath):
        """Load and parse YAML file"""
        success, data, raw_content, error = load_yaml_file(filepath)

        if not success:
            messagebox.showerror("エラー", f"ファイル読み込みエラー:\n{error}")
            return

        # Parse YAML to UI data
        ui_data = parse_yaml_to_ui_data(data)

        # Clear current inputs
        self.clear_all()

        # Restore basic info
        if ui_data['title']:
            self.title_entry.insert(0, ui_data['title'])
        if ui_data['author']:
            self.author_entry.insert(0, ui_data['author'])

        # Restore color mode
        self.color_mode_menu.set(ui_data['color_mode'])
        self.on_color_mode_change(ui_data['color_mode'])
        if ui_data['duotone_color']:
            self.duotone_color_menu.set(ui_data['duotone_color'])

        # Restore output style
        if ui_data['output_style']:
            self.output_style_menu.set(ui_data['output_style'])

        # Restore aspect ratio
        if ui_data.get('aspect_ratio'):
            self.aspect_ratio_var.set(ui_data['aspect_ratio'])

        # Restore characters
        for i, char in enumerate(ui_data['characters'][:MAX_CHARACTERS]):
            self.char_enabled_vars[i].set(True)
            if char['name']:
                self.char_name_entries[i].insert(0, char['name'])
            if char['description']:
                self.char_description_textboxes[i].delete("1.0", tk.END)
                self.char_description_textboxes[i].insert("1.0", char['description'])
            if char['has_reference']:
                self.char_image_attach_vars[i].set("with_image")
            else:
                self.char_image_attach_vars[i].set("without_image")

            # Restore outfit selections
            if 'outfit' in char:
                outfit = char['outfit']
                # カテゴリを設定（形状オプションを更新するためon_outfit_category_changeを呼ぶ）
                self.char_outfit_categories[i].set(outfit.get('category', 'おまかせ'))
                self.on_outfit_category_change(i)  # 形状の選択肢を更新
                # 形状を設定
                self.char_outfit_shapes[i].set(outfit.get('shape', 'おまかせ'))
                # 色、柄、スタイルを設定
                self.char_outfit_colors[i].set(outfit.get('color', 'おまかせ'))
                self.char_outfit_patterns[i].set(outfit.get('pattern', 'おまかせ'))
                self.char_outfit_styles[i].set(outfit.get('style', 'おまかせ'))

        # Restore scene
        if ui_data['scene_prompt']:
            self.scene_textbox.delete("1.0", tk.END)
            self.scene_textbox.insert("1.0", ui_data['scene_prompt'])

        # Restore speeches
        for speech in ui_data['speeches']:
            char_name = speech['character']
            for i in range(MAX_CHARACTERS):
                name = self.char_name_entries[i].get().strip()
                if name == char_name:
                    self.speech_entries[i].insert(0, speech['content'])
                    self.speech_position_menus[i].set(speech['position'])
                    break

        # Restore narrations
        for i, narration in enumerate(ui_data['narrations'][:3]):
            self.narration_entries[i].insert(0, narration['content'])
            self.narration_position_menus[i].set(narration['position'])

        # Update visibility
        self.update_speech_visibility()

        # Add to recent files
        self.recent_files = add_to_recent_files(self.recent_files, filepath)
        save_recent_files(self.recent_files_path, self.recent_files)
        self.update_recent_files_menu()

        # Display in preview
        self.preview_textbox.delete("1.0", tk.END)
        self.preview_textbox.insert("1.0", raw_content)
        self.generated_yaml = raw_content
        self.copy_btn.configure(state="normal")
        self.save_btn.configure(state="normal")


if __name__ == "__main__":
    app = SinglePanelApp()
    app.mainloop()
