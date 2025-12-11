# -*- coding: utf-8 -*-
"""
1コマ漫画生成アプリ
メインUIモジュール（簡素化版）
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
    COLOR_MODES, DUOTONE_COLORS, OUTPUT_TYPES, OUTPUT_STYLES, ASPECT_RATIOS
)

# Import logic modules
from logic.yaml_generator import (
    generate_decorative_yaml,
    generate_composite_yaml
)
from logic.api_client import generate_image_with_api
from logic.file_manager import (
    load_template, load_recent_files, save_recent_files,
    add_to_recent_files, save_yaml_file, load_yaml_file
)

# Import UI windows
from ui.scene_builder_window import SceneBuilderWindow
from ui.character_sheet_window import CharacterSheetWindow
from ui.background_window import BackgroundWindow
from ui.pose_window import PoseWindow
from ui.effect_window import EffectWindow
from ui.decorative_text_window import DecorativeTextWindow

# Set appearance mode and default color theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class MangaGeneratorApp(ctk.CTk):
    """簡素化されたメインアプリケーション"""

    def __init__(self):
        super().__init__()

        # Window configuration
        self.title("1コマ漫画生成アプリ")
        self.geometry("1200x800")

        # Layout configuration - Two column layout
        self.grid_columnconfigure(0, weight=1, minsize=400)  # Left column (settings)
        self.grid_columnconfigure(1, weight=2, minsize=600)  # Right column (preview)
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
        self._build_right_column()

        # Initial update
        self._on_output_type_change(None)

    def _build_left_column(self):
        """左列を構築（基本設定）"""
        self.left_column = ctk.CTkFrame(self)
        self.left_column.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")
        self.left_column.grid_columnconfigure(0, weight=1)
        self.left_column.grid_rowconfigure(6, weight=1)  # Spacer row

        # Create scrollable frame
        self.left_scroll = ctk.CTkScrollableFrame(self.left_column)
        self.left_scroll.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.left_scroll.grid_columnconfigure(0, weight=1)

        row = 0

        # === 出力タイプ選択 ===
        type_frame = ctk.CTkFrame(self.left_scroll)
        type_frame.grid(row=row, column=0, padx=5, pady=5, sticky="ew")
        type_frame.grid_columnconfigure(1, weight=1)
        row += 1

        ctk.CTkLabel(
            type_frame,
            text="出力タイプ",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkLabel(type_frame, text="タイプ:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.output_type_menu = ctk.CTkOptionMenu(
            type_frame,
            values=list(OUTPUT_TYPES.keys()),
            width=200,
            command=self._on_output_type_change
        )
        self.output_type_menu.set("キャラデザイン（全身）")
        self.output_type_menu.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # 詳細設定ボタン
        self.settings_button = ctk.CTkButton(
            type_frame,
            text="詳細設定...",
            width=150,
            command=self._open_settings_window
        )
        self.settings_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        # 設定状態表示
        self.settings_status_label = ctk.CTkLabel(
            type_frame,
            text="設定: 未設定",
            font=("Arial", 11),
            text_color="gray"
        )
        self.settings_status_label.grid(row=3, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="w")

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
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkLabel(info_frame, text="タイトル:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.title_entry = ctk.CTkEntry(info_frame, placeholder_text="作品タイトル")
        self.title_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(info_frame, text="作者名:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.author_entry = ctk.CTkEntry(info_frame, placeholder_text="Unknown")
        self.author_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        # === API設定 ===
        api_frame = ctk.CTkFrame(self.left_scroll)
        api_frame.grid(row=row, column=0, padx=5, pady=5, sticky="ew")
        api_frame.grid_columnconfigure(1, weight=1)
        row += 1

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
        self.api_key_entry = ctk.CTkEntry(api_frame, placeholder_text="Google AI API Key", show="*", state="disabled")
        self.api_key_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        # APIモード
        ctk.CTkLabel(api_frame, text="APIモード:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        api_submode_frame = ctk.CTkFrame(api_frame, fg_color="transparent")
        api_submode_frame.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        self.api_submode_var = tk.StringVar(value="normal")
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

        # === 生成ボタン ===
        button_frame = ctk.CTkFrame(self.left_scroll)
        button_frame.grid(row=row, column=0, padx=5, pady=10, sticky="ew")
        row += 1

        self.generate_button = ctk.CTkButton(
            button_frame,
            text="YAML生成",
            font=("Arial", 14, "bold"),
            height=40,
            command=self._generate_yaml
        )
        self.generate_button.pack(fill="x", padx=10, pady=10)

        # シーンビルダーボタン
        self.scene_builder_button = ctk.CTkButton(
            button_frame,
            text="シーンビルダーを開く",
            height=35,
            command=self._open_scene_builder
        )
        self.scene_builder_button.pack(fill="x", padx=10, pady=(0, 10))

    def _build_right_column(self):
        """右列を構築（YAML/画像プレビュー）"""
        self.right_column = ctk.CTkFrame(self)
        self.right_column.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="nsew")
        self.right_column.grid_columnconfigure(0, weight=1)
        self.right_column.grid_rowconfigure(1, weight=1)

        # === YAMLプレビュー ===
        yaml_frame = ctk.CTkFrame(self.right_column)
        yaml_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        yaml_frame.grid_columnconfigure(0, weight=1)
        yaml_frame.grid_rowconfigure(1, weight=1)
        self.right_column.grid_rowconfigure(0, weight=1)

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
        self.right_column.grid_rowconfigure(1, weight=1)

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

    # === Event Handlers ===

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
        """出力モード変更時"""
        mode = self.output_mode_var.get()
        if mode == "api":
            self.api_key_entry.configure(state="normal")
            self.api_normal_radio.configure(state="normal")
            self.api_redraw_radio.configure(state="normal")
            self.ref_image_entry.configure(state="normal")
            self.ref_image_browse.configure(state="normal")
            self.generate_button.configure(text="画像生成")
        else:
            self.api_key_entry.configure(state="disabled")
            self.api_normal_radio.configure(state="disabled")
            self.api_redraw_radio.configure(state="disabled")
            self.ref_image_entry.configure(state="disabled")
            self.ref_image_browse.configure(state="disabled")
            self.generate_button.configure(text="YAML生成")

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
        else:
            messagebox.showinfo("情報", f"'{output_type}'の設定ウィンドウは未実装です")

    def _on_settings_complete(self, data: dict):
        """設定完了時のコールバック"""
        self.current_settings = data
        self.settings_status_label.configure(text="設定: 設定済み ✓", text_color="green")

    # === YAML Generation ===

    def _generate_yaml(self):
        """YAML生成"""
        output_type = self.output_type_menu.get()

        # 設定チェック
        if not self.current_settings:
            messagebox.showwarning("警告", "詳細設定を行ってください")
            return

        # 共通パラメータ
        color_mode = self.color_mode_menu.get()
        duotone_color = self.duotone_color_menu.get() if color_mode == "2色刷り" else None
        output_style = self.output_style_menu.get()
        aspect_ratio = self.aspect_ratio_menu.get()
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip() or "Unknown"

        try:
            if output_type in ["キャラデザイン（全身）", "キャラデザイン（顔）"]:
                yaml_content = self._generate_character_sheet_yaml(
                    color_mode, duotone_color, output_style, aspect_ratio, title, author
                )
            elif output_type == "背景のみ生成":
                yaml_content = self._generate_background_yaml(
                    color_mode, duotone_color, output_style, aspect_ratio, title, author
                )
            elif output_type == "ポーズ付きキャラ":
                yaml_content = self._generate_pose_yaml(
                    color_mode, duotone_color, output_style, aspect_ratio, title, author
                )
            elif output_type == "エフェクト追加":
                yaml_content = self._generate_effect_yaml(
                    color_mode, duotone_color, output_style, aspect_ratio, title, author
                )
            elif output_type == "装飾テキスト":
                yaml_content = self._generate_decorative_yaml(
                    color_mode, duotone_color, output_style, aspect_ratio, title, author
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

    def _generate_character_sheet_yaml(self, color_mode, duotone_color, output_style, aspect_ratio, title, author):
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

        yaml_content = f"""# {sheet_label.title()} (character_basic.yaml準拠)
type: character_design
title: "{title or name + ' Reference Sheet'}"
author: "{author}"

output_type: "{sheet_label}"

character:
  name: "{name}"
  description: "{description}"
  outfit: "{outfit_prompt}"
  expression: "neutral expression, standing at attention"

character_style:
  style: "{style_prompt}"
  proportions: "{proportions}"
  style_description: "{style_description}"

views: "{views}"

constraints:
  - Maintain consistent design across all views
  - White or simple background for clarity
  - Clean linework suitable for reference

style:
  color_mode: "{COLOR_MODES.get(color_mode, 'full_color')}"
  output_style: "{OUTPUT_STYLES.get(output_style, 'anime')}"
  aspect_ratio: "{ASPECT_RATIOS.get(aspect_ratio, '1:1')}"
"""

        if image_path:
            yaml_content += f'\nreference_image: "{image_path}"'

        return yaml_content

    def _generate_background_yaml(self, color_mode, duotone_color, output_style, aspect_ratio, title, author):
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
        return yaml_content

    def _generate_pose_yaml(self, color_mode, duotone_color, output_style, aspect_ratio, title, author):
        """ポーズ付きキャラ用YAML生成（character_pose.yaml準拠）"""
        settings = self.current_settings
        from ui.pose_window import (
            ACTION_CATEGORIES, DYNAMISM_LEVELS, WIND_EFFECTS, CAMERA_ANGLES, ZOOM_LEVELS
        )
        from constants import CHARACTER_FACING, CHARACTER_POSES

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

        yaml_content = f"""# Character Pose Generation (character_pose.yaml準拠)
type: character_pose
title: "{title or 'Character Pose'}"
author: "{author}"

input:
  character_image: "{image_path}"
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

constraints:
  - Preserve character design and colors from input image
  - No background (transparent or simple backdrop)
  - Clean silhouette for compositing

style:
  color_mode: "{COLOR_MODES.get(color_mode, 'full_color')}"
  output_style: "{OUTPUT_STYLES.get(output_style, 'anime')}"
  aspect_ratio: "{ASPECT_RATIOS.get(aspect_ratio, '1:1')}"
"""
        return yaml_content

    def _generate_effect_yaml(self, color_mode, duotone_color, output_style, aspect_ratio, title, author):
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
  posed_character_image: "{image_path}"
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
        return yaml_content

    def _generate_decorative_yaml(self, color_mode, duotone_color, output_style, aspect_ratio, title, author):
        """装飾テキスト用YAML生成"""
        settings = self.current_settings
        texts = settings.get('texts', [])

        return generate_decorative_yaml(
            template_data=self.template_data,
            title=title,
            author=author,
            texts=texts,
            color_mode_name=color_mode,
            duotone_color_name=duotone_color,
            output_style_name=output_style,
            aspect_ratio_name=aspect_ratio
        )

    # === API Image Generation ===

    def _generate_image_with_api(self, yaml_content: str):
        """APIで画像生成"""
        api_key = self.api_key_entry.get().strip()
        if not api_key:
            messagebox.showwarning("警告", "API Keyを入力してください")
            return

        # 参考画像（清書モードの場合）
        ref_image_path = None
        if self.api_submode_var.get() == "redraw":
            ref_image_path = self.ref_image_entry.get().strip()
            if not ref_image_path or not os.path.exists(ref_image_path):
                messagebox.showwarning("警告", "参考画像清書モードでは参考画像が必要です")
                return

        # 生成中表示
        self.generate_button.configure(state="disabled", text="生成中...")
        self.preview_label.configure(text="画像生成中...", image=None)

        def generate():
            try:
                image = generate_image_with_api(api_key, yaml_content, ref_image_path)
                self.after(0, lambda: self._on_image_generated(image))
            except Exception as e:
                self.after(0, lambda: self._on_image_error(str(e)))

        thread = threading.Thread(target=generate, daemon=True)
        thread.start()

    def _on_image_generated(self, image: Image.Image):
        """画像生成完了"""
        self.generated_image = image
        self.generate_button.configure(state="normal", text="画像生成")
        self.save_image_button.configure(state="normal")

        # プレビュー表示
        preview_size = (400, 400)
        image.thumbnail(preview_size, Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        self.preview_label.configure(image=photo, text="")
        self.preview_label.image = photo

    def _on_image_error(self, error_msg: str):
        """画像生成エラー"""
        self.generate_button.configure(state="normal", text="画像生成")
        self.preview_label.configure(text=f"エラー: {error_msg}", image=None)
        messagebox.showerror("エラー", f"画像生成に失敗しました:\n{error_msg}")

    # === File Operations ===

    def _copy_yaml(self):
        """YAMLをクリップボードにコピー"""
        yaml_content = self.yaml_textbox.get("1.0", tk.END).strip()
        if yaml_content:
            pyperclip.copy(yaml_content)
            messagebox.showinfo("コピー完了", "YAMLをクリップボードにコピーしました")

    def _save_yaml(self):
        """YAMLを保存"""
        yaml_content = self.yaml_textbox.get("1.0", tk.END).strip()
        if not yaml_content:
            messagebox.showwarning("警告", "保存するYAMLがありません")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".yaml",
            filetypes=[("YAML files", "*.yaml *.yml"), ("All files", "*.*")]
        )
        if filename:
            save_yaml_file(filename, yaml_content)
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
                add_to_recent_files(self.recent_files, filename)
                save_recent_files(self.recent_files_path, self.recent_files)

    def _save_image(self):
        """生成画像を保存"""
        if not self.generated_image:
            messagebox.showwarning("警告", "保存する画像がありません")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        if filename:
            self.generated_image.save(filename)
            messagebox.showinfo("保存完了", f"画像を保存しました:\n{filename}")

    # === Scene Builder ===

    def _open_scene_builder(self):
        """シーンビルダーを開く"""
        SceneBuilderWindow(self)


def main():
    app = MangaGeneratorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
