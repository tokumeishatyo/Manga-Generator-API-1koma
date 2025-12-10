# -*- coding: utf-8 -*-
"""
シーンビルダーウィンドウ
シーンテンプレートを選択・カスタマイズするための別ウィンドウ
"""

import tkinter as tk
import customtkinter as ctk

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logic.scene_builder import (
    get_scene_types,
    get_scene_type_info,
    get_action_names,
    get_action_display_names,
    get_background_names,
    generate_scene_prompt,
    STYLE_NAMES
)


class SceneBuilderWindow(ctk.CTkToplevel):
    """シーンビルダーウィンドウ"""

    def __init__(self, parent, callback=None):
        """
        Args:
            parent: 親ウィンドウ
            callback: シーン説明をコピーする際に呼び出すコールバック関数
                      callback(scene_prompt: str) の形式
        """
        super().__init__(parent)

        self.callback = callback
        self.action_name_map = get_action_names()  # 日本語 -> 英語キー

        # ウィンドウ設定
        self.title("シーンビルダー")
        self.geometry("650x950")
        self.resizable(True, True)

        # 非モーダル（親ウィンドウも操作可能）
        self.transient(parent)

        # UI構築
        self._build_ui()

        # 初期プレビュー生成
        self._update_preview()

    def _build_ui(self):
        """UIを構築"""
        # メインフレーム
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # シーンタイプ選択
        type_frame = ctk.CTkFrame(main_frame)
        type_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(type_frame, text="シーンタイプ", font=("", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 5))

        self.scene_type_var = tk.StringVar(value="同一キャラ: カットイン/ドット絵")
        scene_types = get_scene_types()

        self.scene_type_menu = ctk.CTkOptionMenu(
            type_frame,
            variable=self.scene_type_var,
            values=scene_types,
            command=self._on_scene_type_change,
            width=300
        )
        self.scene_type_menu.pack(anchor="w", padx=20, pady=(0, 5))

        # シーンタイプ説明
        self.type_description_label = ctk.CTkLabel(
            type_frame,
            text="",
            font=("", 11),
            text_color="gray"
        )
        self.type_description_label.pack(anchor="w", padx=20, pady=(0, 10))

        # 構成表示
        self.composition_label = ctk.CTkLabel(
            type_frame,
            text="",
            font=("", 12)
        )
        self.composition_label.pack(anchor="w", padx=20, pady=(0, 10))

        # アクション選択フレーム
        action_frame = ctk.CTkFrame(main_frame)
        action_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(action_frame, text="アクション", font=("", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 5))

        action_options_frame = ctk.CTkFrame(action_frame, fg_color="transparent")
        action_options_frame.pack(fill="x", padx=20, pady=(0, 10))

        action_display_names = get_action_display_names()

        # 左キャラアクション
        left_frame = ctk.CTkFrame(action_options_frame, fg_color="transparent")
        left_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(left_frame, text="左キャラ:", width=80).pack(side="left")
        self.left_action_var = tk.StringVar(value="攻撃")
        self.left_action_menu = ctk.CTkOptionMenu(
            left_frame,
            variable=self.left_action_var,
            values=action_display_names,
            command=lambda _: self._update_preview(),
            width=180
        )
        self.left_action_menu.pack(side="left", padx=(10, 0))

        # 右キャラアクション
        right_frame = ctk.CTkFrame(action_options_frame, fg_color="transparent")
        right_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(right_frame, text="右キャラ:", width=80).pack(side="left")
        self.right_action_var = tk.StringVar(value="防御")
        self.right_action_menu = ctk.CTkOptionMenu(
            right_frame,
            variable=self.right_action_var,
            values=action_display_names,
            command=lambda _: self._update_preview(),
            width=180
        )
        self.right_action_menu.pack(side="left", padx=(10, 0))

        # 背景選択
        bg_frame = ctk.CTkFrame(main_frame)
        bg_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(bg_frame, text="背景", font=("", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 5))

        bg_options_frame = ctk.CTkFrame(bg_frame, fg_color="transparent")
        bg_options_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.background_var = tk.StringVar(value="教室")
        background_names = get_background_names()

        self.background_menu = ctk.CTkOptionMenu(
            bg_options_frame,
            variable=self.background_var,
            values=background_names,
            command=lambda _: self._update_preview(),
            width=180
        )
        self.background_menu.pack(anchor="w")

        # キャラ名入力
        name_frame = ctk.CTkFrame(main_frame)
        name_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(name_frame, text="キャラ名（任意）", font=("", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 5))

        name_options_frame = ctk.CTkFrame(name_frame, fg_color="transparent")
        name_options_frame.pack(fill="x", padx=20, pady=(0, 10))

        # 左キャラ名
        left_name_frame = ctk.CTkFrame(name_options_frame, fg_color="transparent")
        left_name_frame.pack(fill="x", pady=2)

        ctk.CTkLabel(left_name_frame, text="左キャラ:", width=80).pack(side="left")
        self.left_name_var = tk.StringVar(value="")
        self.left_name_entry = ctk.CTkEntry(
            left_name_frame,
            textvariable=self.left_name_var,
            width=200,
            placeholder_text="例: AYASE KOYOMI"
        )
        self.left_name_entry.pack(side="left", padx=(10, 0))
        self.left_name_entry.bind("<KeyRelease>", lambda _: self._update_preview())

        # 右キャラ名
        right_name_frame = ctk.CTkFrame(name_options_frame, fg_color="transparent")
        right_name_frame.pack(fill="x", pady=2)

        ctk.CTkLabel(right_name_frame, text="右キャラ:", width=80).pack(side="left")
        self.right_name_var = tk.StringVar(value="")
        self.right_name_entry = ctk.CTkEntry(
            right_name_frame,
            textvariable=self.right_name_var,
            width=200,
            placeholder_text="例: SHINOMIYA RIN"
        )
        self.right_name_entry.pack(side="left", padx=(10, 0))
        self.right_name_entry.bind("<KeyRelease>", lambda _: self._update_preview())

        # セリフ入力
        speech_frame = ctk.CTkFrame(main_frame)
        speech_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(speech_frame, text="セリフ（任意）", font=("", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 5))

        speech_options_frame = ctk.CTkFrame(speech_frame, fg_color="transparent")
        speech_options_frame.pack(fill="x", padx=20, pady=(0, 10))

        # 左キャラセリフ
        left_speech_frame = ctk.CTkFrame(speech_options_frame, fg_color="transparent")
        left_speech_frame.pack(fill="x", pady=2)

        ctk.CTkLabel(left_speech_frame, text="左キャラ:", width=80).pack(side="left")
        self.left_speech_var = tk.StringVar(value="")
        self.left_speech_entry = ctk.CTkEntry(
            left_speech_frame,
            textvariable=self.left_speech_var,
            width=200,
            placeholder_text="例: くらえ〜"
        )
        self.left_speech_entry.pack(side="left", padx=(10, 0))
        self.left_speech_entry.bind("<KeyRelease>", lambda _: self._update_preview())

        # 右キャラセリフ
        right_speech_frame = ctk.CTkFrame(speech_options_frame, fg_color="transparent")
        right_speech_frame.pack(fill="x", pady=2)

        ctk.CTkLabel(right_speech_frame, text="右キャラ:", width=80).pack(side="left")
        self.right_speech_var = tk.StringVar(value="")
        self.right_speech_entry = ctk.CTkEntry(
            right_speech_frame,
            textvariable=self.right_speech_var,
            width=200,
            placeholder_text="例: うおお"
        )
        self.right_speech_entry.pack(side="left", padx=(10, 0))
        self.right_speech_entry.bind("<KeyRelease>", lambda _: self._update_preview())

        # 技名入力
        move_frame = ctk.CTkFrame(main_frame)
        move_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(move_frame, text="技名（任意）", font=("", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 5))

        move_options_frame = ctk.CTkFrame(move_frame, fg_color="transparent")
        move_options_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.move_name_var = tk.StringVar(value="")
        self.move_name_entry = ctk.CTkEntry(
            move_options_frame,
            textvariable=self.move_name_var,
            width=250,
            placeholder_text="例: 必殺ビーム"
        )
        self.move_name_entry.pack(anchor="w")
        self.move_name_entry.bind("<KeyRelease>", lambda _: self._update_preview())

        # プレビュー
        preview_frame = ctk.CTkFrame(main_frame)
        preview_frame.pack(fill="both", expand=True, pady=10)

        ctk.CTkLabel(preview_frame, text="プレビュー", font=("", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 5))

        self.preview_text = ctk.CTkTextbox(preview_frame, height=180, wrap="word")
        self.preview_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # ボタン
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))

        self.clipboard_button = ctk.CTkButton(
            button_frame,
            text="クリップボードにコピー",
            command=self._copy_to_clipboard,
            width=160
        )
        self.clipboard_button.pack(side="left", padx=(0, 10))

        self.apply_button = ctk.CTkButton(
            button_frame,
            text="シーン説明に書き込み",
            command=self._apply_to_scene,
            width=160
        )
        self.apply_button.pack(side="left", padx=(0, 10))

        self.close_button = ctk.CTkButton(
            button_frame,
            text="閉じる",
            command=self.destroy,
            width=80,
            fg_color="gray"
        )
        self.close_button.pack(side="left")

        # 初期表示更新
        self._on_scene_type_change(self.scene_type_var.get())

    def _on_scene_type_change(self, scene_type: str):
        """シーンタイプ変更時の処理"""
        type_info = get_scene_type_info(scene_type)

        # 説明を更新
        description = type_info.get("description", "")
        self.type_description_label.configure(text=description)

        # 構成を表示
        left_style = type_info.get("left_style", "")
        right_style = type_info.get("right_style", "")
        left_name = STYLE_NAMES.get(left_style, left_style)
        right_name = STYLE_NAMES.get(right_style, right_style)

        composition = f"構成: 左[{left_name}] vs 右[{right_name}]"
        self.composition_label.configure(text=composition)

        self._update_preview()

    def _update_preview(self):
        """プレビューを更新"""
        scene_type = self.scene_type_var.get()

        # 日本語アクション名を英語キーに変換
        left_action_jp = self.left_action_var.get()
        right_action_jp = self.right_action_var.get()
        left_action = self.action_name_map.get(left_action_jp, "attacking")
        right_action = self.action_name_map.get(right_action_jp, "defending")

        background = self.background_var.get()

        # 追加パラメータ
        left_name = self.left_name_var.get().strip()
        right_name = self.right_name_var.get().strip()
        left_speech = self.left_speech_var.get().strip()
        right_speech = self.right_speech_var.get().strip()
        move_name = self.move_name_var.get().strip()

        prompt = generate_scene_prompt(
            scene_type=scene_type,
            left_action=left_action,
            right_action=right_action,
            background=background,
            left_name=left_name,
            right_name=right_name,
            left_speech=left_speech,
            right_speech=right_speech,
            move_name=move_name
        )

        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert("1.0", prompt)

    def _copy_to_clipboard(self):
        """クリップボードにコピー"""
        import pyperclip
        prompt = self.preview_text.get("1.0", tk.END).strip()
        pyperclip.copy(prompt)
        # ボタンテキストを一時的に変更してフィードバック
        self.clipboard_button.configure(text="コピーしました！")
        self.after(1500, lambda: self.clipboard_button.configure(text="クリップボードにコピー"))

    def _apply_to_scene(self):
        """シーン説明に書き込み（ウィンドウは閉じない）"""
        prompt = self.preview_text.get("1.0", tk.END).strip()

        if self.callback:
            self.callback(prompt)

        # ボタンテキストを一時的に変更してフィードバック
        self.apply_button.configure(text="書き込みました！")
        self.after(1500, lambda: self.apply_button.configure(text="シーン説明に書き込み"))
