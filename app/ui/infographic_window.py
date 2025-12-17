# -*- coding: utf-8 -*-
"""
インフォグラフィック設定ウィンドウ
グラレコ風・ノート風などのインフォグラフィック画像を生成するための設定
"""

import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog
from typing import Callable, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.base_settings_window import BaseSettingsWindow
from constants import INFOGRAPHIC_STYLES, INFOGRAPHIC_POSITIONS, INFOGRAPHIC_LANGUAGES


class InfographicWindow(BaseSettingsWindow):
    """インフォグラフィック設定ウィンドウ"""

    MAX_SECTIONS = 8  # 最大項目数

    def __init__(
        self,
        parent,
        callback: Optional[Callable] = None,
        initial_data: Optional[dict] = None
    ):
        """
        Args:
            parent: 親ウィンドウ
            callback: 設定完了時のコールバック
            initial_data: 初期データ（編集時）
        """
        self.initial_data = initial_data or {}
        self.section_frames = []  # 項目フレームのリスト
        super().__init__(
            parent,
            title="インフォグラフィック設定",
            width=850,
            height=700,
            callback=callback
        )

    def build_content(self):
        """コンテンツを構築"""
        # スクロール可能なフレームを作成
        self.content_frame.grid_columnconfigure(0, weight=1)

        # === スタイル選択 ===
        style_frame = ctk.CTkFrame(self.content_frame)
        style_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        style_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            style_frame,
            text="スタイル設定",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkLabel(style_frame, text="スタイル:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.style_menu = ctk.CTkOptionMenu(
            style_frame,
            values=list(INFOGRAPHIC_STYLES.keys()),
            width=200,
            command=self._on_style_change
        )
        self.style_menu.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        self.style_menu.set("グラレコ風")

        # スタイル説明
        self.style_desc_label = ctk.CTkLabel(
            style_frame,
            text=INFOGRAPHIC_STYLES["グラレコ風"]["description"],
            text_color="gray"
        )
        self.style_desc_label.grid(row=2, column=0, columnspan=2, padx=10, pady=(0, 5), sticky="w")

        # アスペクト比
        ctk.CTkLabel(style_frame, text="アスペクト比:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.aspect_var = tk.StringVar(value="16:9")
        aspect_frame = ctk.CTkFrame(style_frame, fg_color="transparent")
        aspect_frame.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkRadioButton(aspect_frame, text="16:9（横長）", variable=self.aspect_var, value="16:9").pack(side="left", padx=(0, 20))
        ctk.CTkRadioButton(aspect_frame, text="9:16（縦長）", variable=self.aspect_var, value="9:16").pack(side="left")

        # 出力言語
        ctk.CTkLabel(style_frame, text="出力言語:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.language_menu = ctk.CTkOptionMenu(
            style_frame,
            values=list(INFOGRAPHIC_LANGUAGES.keys()),
            width=200
        )
        self.language_menu.grid(row=4, column=1, padx=10, pady=5, sticky="w")
        self.language_menu.set("日本語")

        # === タイトル・副題 ===
        title_frame = ctk.CTkFrame(self.content_frame)
        title_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        title_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            title_frame,
            text="タイトル設定",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkLabel(title_frame, text="タイトル:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.main_title_entry = ctk.CTkEntry(title_frame, placeholder_text="例: けいすけ解体新書（必須）", width=400)
        self.main_title_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(title_frame, text="副題:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.subtitle_entry = ctk.CTkEntry(title_frame, placeholder_text="例: KEISUKE ANATOMY（任意）", width=400)
        self.subtitle_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        # === キャラクター画像 ===
        char_frame = ctk.CTkFrame(self.content_frame)
        char_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        char_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            char_frame,
            text="キャラクター画像",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 5), sticky="w")

        # メインキャラクター
        ctk.CTkLabel(char_frame, text="メイン画像:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        img_frame = ctk.CTkFrame(char_frame, fg_color="transparent")
        img_frame.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        img_frame.grid_columnconfigure(0, weight=1)

        self.main_image_entry = ctk.CTkEntry(img_frame, placeholder_text="中央に配置するキャラクター画像（必須）")
        self.main_image_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkButton(img_frame, text="参照", width=60, command=self._browse_main_image).grid(row=0, column=1)

        # おまけ画像
        ctk.CTkLabel(char_frame, text="おまけ画像:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        bonus_frame = ctk.CTkFrame(char_frame, fg_color="transparent")
        bonus_frame.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        bonus_frame.grid_columnconfigure(0, weight=1)

        self.bonus_image_entry = ctk.CTkEntry(bonus_frame, placeholder_text="ちびキャラなど（任意・配置はAIおまかせ）")
        self.bonus_image_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkButton(bonus_frame, text="参照", width=60, command=self._browse_bonus_image).grid(row=0, column=1)

        # === 項目セクション ===
        sections_label_frame = ctk.CTkFrame(self.content_frame)
        sections_label_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=(10, 0))
        sections_label_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            sections_label_frame,
            text=f"項目（最大{self.MAX_SECTIONS}つ）",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkButton(
            sections_label_frame,
            text="+ 項目を追加",
            width=120,
            command=self._add_section
        ).grid(row=0, column=1, padx=10, pady=(10, 5), sticky="e")

        # 項目コンテナ（スクロール可能）
        self.sections_container = ctk.CTkScrollableFrame(
            self.content_frame,
            height=250
        )
        self.sections_container.grid(row=4, column=0, sticky="nsew", padx=5, pady=5)
        self.sections_container.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(4, weight=1)

        # 初期項目を2つ追加
        self._add_section()
        self._add_section()

        # 初期データがあれば反映
        if self.initial_data:
            self._load_initial_data()

    def _on_style_change(self, value):
        """スタイル変更時"""
        style_info = INFOGRAPHIC_STYLES.get(value, {})
        self.style_desc_label.configure(text=style_info.get("description", ""))

    def _browse_main_image(self):
        """メイン画像参照"""
        filename = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]
        )
        if filename:
            self.main_image_entry.delete(0, tk.END)
            self.main_image_entry.insert(0, filename)

    def _browse_bonus_image(self):
        """おまけ画像参照"""
        filename = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]
        )
        if filename:
            self.bonus_image_entry.delete(0, tk.END)
            self.bonus_image_entry.insert(0, filename)

    def _add_section(self):
        """項目を追加"""
        if len(self.section_frames) >= self.MAX_SECTIONS:
            return

        section_idx = len(self.section_frames)
        frame = ctk.CTkFrame(self.sections_container)
        frame.grid(row=section_idx, column=0, sticky="ew", padx=5, pady=5)
        frame.grid_columnconfigure(1, weight=1)

        # ヘッダー（項目番号と削除ボタン）
        header_frame = ctk.CTkFrame(frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=5, pady=(5, 0))
        header_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header_frame,
            text=f"項目 {section_idx + 1}",
            font=("Arial", 12, "bold")
        ).grid(row=0, column=0, sticky="w")

        delete_btn = ctk.CTkButton(
            header_frame,
            text="×",
            width=30,
            height=24,
            fg_color="red",
            hover_color="darkred",
            command=lambda f=frame: self._remove_section(f)
        )
        delete_btn.grid(row=0, column=1, sticky="e")

        # タイトル
        ctk.CTkLabel(frame, text="タイトル:").grid(row=1, column=0, padx=10, pady=2, sticky="w")
        title_entry = ctk.CTkEntry(frame, placeholder_text="例: 仕事と活動の顔", width=300)
        title_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        # 位置指定
        ctk.CTkLabel(frame, text="位置:").grid(row=1, column=2, padx=(10, 5), pady=2, sticky="w")
        position_menu = ctk.CTkOptionMenu(
            frame,
            values=list(INFOGRAPHIC_POSITIONS.keys()),
            width=120
        )
        position_menu.grid(row=1, column=3, padx=5, pady=2, sticky="w")
        position_menu.set("おまかせ")

        # 説明（複数行）
        ctk.CTkLabel(frame, text="説明:").grid(row=2, column=0, padx=10, pady=2, sticky="nw")
        desc_textbox = ctk.CTkTextbox(frame, height=60, width=400)
        desc_textbox.grid(row=2, column=1, columnspan=3, padx=5, pady=2, sticky="ew")
        desc_textbox.insert("1.0", "AIマンガ家\n教材クリエイター")

        # フレーム情報を保存
        frame.title_entry = title_entry
        frame.position_menu = position_menu
        frame.desc_textbox = desc_textbox
        self.section_frames.append(frame)

        # 項目番号を更新
        self._update_section_numbers()

    def _remove_section(self, frame):
        """項目を削除"""
        if len(self.section_frames) <= 1:
            return  # 最低1つは残す

        frame.destroy()
        self.section_frames.remove(frame)
        self._update_section_numbers()

    def _update_section_numbers(self):
        """項目番号を更新"""
        for idx, frame in enumerate(self.section_frames):
            # ヘッダーのラベルを更新（最初の子要素のラベル）
            for widget in frame.winfo_children():
                if isinstance(widget, ctk.CTkFrame):
                    for child in widget.winfo_children():
                        if isinstance(child, ctk.CTkLabel):
                            child.configure(text=f"項目 {idx + 1}")
                            break
                    break
            frame.grid(row=idx, column=0, sticky="ew", padx=5, pady=5)

    def _load_initial_data(self):
        """初期データを読み込み"""
        data = self.initial_data

        if data.get('style'):
            self.style_menu.set(data['style'])
            self._on_style_change(data['style'])

        if data.get('aspect_ratio'):
            self.aspect_var.set(data['aspect_ratio'])

        if data.get('language'):
            self.language_menu.set(data['language'])

        if data.get('main_title'):
            self.main_title_entry.delete(0, tk.END)
            self.main_title_entry.insert(0, data['main_title'])

        if data.get('subtitle'):
            self.subtitle_entry.delete(0, tk.END)
            self.subtitle_entry.insert(0, data['subtitle'])

        if data.get('main_image_path'):
            self.main_image_entry.delete(0, tk.END)
            self.main_image_entry.insert(0, data['main_image_path'])

        if data.get('bonus_image_path'):
            self.bonus_image_entry.delete(0, tk.END)
            self.bonus_image_entry.insert(0, data['bonus_image_path'])

        # 項目を読み込み
        sections = data.get('sections', [])
        # 既存の項目をクリア
        for frame in self.section_frames[:]:
            self._remove_section(frame)

        for section in sections:
            self._add_section()
            frame = self.section_frames[-1]
            frame.title_entry.delete(0, tk.END)
            frame.title_entry.insert(0, section.get('title', ''))
            frame.position_menu.set(section.get('position', 'おまかせ'))
            frame.desc_textbox.delete("1.0", tk.END)
            frame.desc_textbox.insert("1.0", section.get('description', ''))

    def collect_data(self) -> dict:
        """UIから設定データを収集"""
        sections = []
        for frame in self.section_frames:
            title = frame.title_entry.get().strip()
            position = frame.position_menu.get()
            description = frame.desc_textbox.get("1.0", tk.END).strip()

            if title or description:  # タイトルか説明があれば追加
                sections.append({
                    'title': title,
                    'position': position,
                    'position_value': INFOGRAPHIC_POSITIONS.get(position, 'auto'),
                    'description': description
                })

        return {
            'step_type': 'infographic',
            'style': self.style_menu.get(),
            'style_info': INFOGRAPHIC_STYLES.get(self.style_menu.get(), {}),
            'aspect_ratio': self.aspect_var.get(),
            'language': self.language_menu.get(),
            'language_value': INFOGRAPHIC_LANGUAGES.get(self.language_menu.get(), 'Japanese'),
            'main_title': self.main_title_entry.get().strip(),
            'subtitle': self.subtitle_entry.get().strip(),
            'main_image_path': self.main_image_entry.get().strip(),
            'bonus_image_path': self.bonus_image_entry.get().strip(),
            'sections': sections
        }

    def validate(self) -> tuple[bool, str]:
        """入力検証"""
        if not self.main_title_entry.get().strip():
            return False, "タイトルを入力してください。"

        if not self.main_image_entry.get().strip():
            return False, "メインキャラクター画像を選択してください。"

        main_image = self.main_image_entry.get().strip()
        if not os.path.exists(main_image):
            return False, "メインキャラクター画像が見つかりません。"

        bonus_image = self.bonus_image_entry.get().strip()
        if bonus_image and not os.path.exists(bonus_image):
            return False, "おまけ画像が見つかりません。"

        # 少なくとも1つの項目が必要
        has_section = False
        for frame in self.section_frames:
            title = frame.title_entry.get().strip()
            description = frame.desc_textbox.get("1.0", tk.END).strip()
            if title or description:
                has_section = True
                break

        if not has_section:
            return False, "少なくとも1つの項目を入力してください。"

        return True, ""
