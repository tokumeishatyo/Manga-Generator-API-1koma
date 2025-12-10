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
        self.geometry("750x650")
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

        # シーンタイプ選択（1行目）
        type_row = ctk.CTkFrame(main_frame, fg_color="transparent")
        type_row.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(type_row, text="シーンタイプ:", width=100).pack(side="left")
        self.scene_type_var = tk.StringVar(value="同一キャラ: カットイン/ドット絵")
        scene_types = get_scene_types()

        self.scene_type_menu = ctk.CTkOptionMenu(
            type_row,
            variable=self.scene_type_var,
            values=scene_types,
            command=self._on_scene_type_change,
            width=280
        )
        self.scene_type_menu.pack(side="left", padx=(5, 10))

        # 構成表示（シーンタイプの横）
        self.composition_label = ctk.CTkLabel(
            type_row,
            text="",
            font=("", 11),
            text_color="gray"
        )
        self.composition_label.pack(side="left")

        # アクション選択（2行目）- 左右を1行に
        action_row = ctk.CTkFrame(main_frame, fg_color="transparent")
        action_row.pack(fill="x", pady=5)

        ctk.CTkLabel(action_row, text="アクション:", width=100).pack(side="left")

        action_display_names = get_action_display_names()

        ctk.CTkLabel(action_row, text="左:").pack(side="left", padx=(5, 2))
        self.left_action_var = tk.StringVar(value="攻撃")
        self.left_action_menu = ctk.CTkOptionMenu(
            action_row,
            variable=self.left_action_var,
            values=action_display_names,
            command=lambda _: self._update_preview(),
            width=120
        )
        self.left_action_menu.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(action_row, text="右:").pack(side="left", padx=(0, 2))
        self.right_action_var = tk.StringVar(value="防御")
        self.right_action_menu = ctk.CTkOptionMenu(
            action_row,
            variable=self.right_action_var,
            values=action_display_names,
            command=lambda _: self._update_preview(),
            width=120
        )
        self.right_action_menu.pack(side="left")

        # 背景選択（3行目）
        bg_row = ctk.CTkFrame(main_frame, fg_color="transparent")
        bg_row.pack(fill="x", pady=5)

        ctk.CTkLabel(bg_row, text="背景:", width=100).pack(side="left")

        self.background_var = tk.StringVar(value="教室")
        background_names = get_background_names()

        self.background_menu = ctk.CTkOptionMenu(
            bg_row,
            variable=self.background_var,
            values=background_names,
            command=lambda _: self._update_preview(),
            width=150
        )
        self.background_menu.pack(side="left", padx=(5, 0))

        # キャラ名入力（4行目）- 左右を1行に
        name_row = ctk.CTkFrame(main_frame, fg_color="transparent")
        name_row.pack(fill="x", pady=5)

        ctk.CTkLabel(name_row, text="キャラ名:", width=100).pack(side="left")

        ctk.CTkLabel(name_row, text="左:").pack(side="left", padx=(5, 2))
        self.left_name_var = tk.StringVar(value="")
        self.left_name_entry = ctk.CTkEntry(
            name_row,
            textvariable=self.left_name_var,
            width=150,
            placeholder_text="AYASE KOYOMI"
        )
        self.left_name_entry.pack(side="left", padx=(0, 15))
        self.left_name_entry.bind("<KeyRelease>", lambda _: self._update_preview())

        ctk.CTkLabel(name_row, text="右:").pack(side="left", padx=(0, 2))
        self.right_name_var = tk.StringVar(value="")
        self.right_name_entry = ctk.CTkEntry(
            name_row,
            textvariable=self.right_name_var,
            width=150,
            placeholder_text="SHINOMIYA RIN"
        )
        self.right_name_entry.pack(side="left")
        self.right_name_entry.bind("<KeyRelease>", lambda _: self._update_preview())

        # セリフ入力（5行目）- 左右を1行に
        speech_row = ctk.CTkFrame(main_frame, fg_color="transparent")
        speech_row.pack(fill="x", pady=5)

        ctk.CTkLabel(speech_row, text="セリフ:", width=100).pack(side="left")

        ctk.CTkLabel(speech_row, text="左:").pack(side="left", padx=(5, 2))
        self.left_speech_var = tk.StringVar(value="")
        self.left_speech_entry = ctk.CTkEntry(
            speech_row,
            textvariable=self.left_speech_var,
            width=150,
            placeholder_text="くらえ〜"
        )
        self.left_speech_entry.pack(side="left", padx=(0, 15))
        self.left_speech_entry.bind("<KeyRelease>", lambda _: self._update_preview())

        ctk.CTkLabel(speech_row, text="右:").pack(side="left", padx=(0, 2))
        self.right_speech_var = tk.StringVar(value="")
        self.right_speech_entry = ctk.CTkEntry(
            speech_row,
            textvariable=self.right_speech_var,
            width=150,
            placeholder_text="うおお"
        )
        self.right_speech_entry.pack(side="left")
        self.right_speech_entry.bind("<KeyRelease>", lambda _: self._update_preview())

        # 技名入力（6行目）
        move_row = ctk.CTkFrame(main_frame, fg_color="transparent")
        move_row.pack(fill="x", pady=5)

        ctk.CTkLabel(move_row, text="技名:", width=100).pack(side="left")

        self.move_name_var = tk.StringVar(value="")
        self.move_name_entry = ctk.CTkEntry(
            move_row,
            textvariable=self.move_name_var,
            width=250,
            placeholder_text="必殺ビーム"
        )
        self.move_name_entry.pack(side="left", padx=(5, 0))
        self.move_name_entry.bind("<KeyRelease>", lambda _: self._update_preview())

        # プレビュー
        preview_frame = ctk.CTkFrame(main_frame)
        preview_frame.pack(fill="both", expand=True, pady=(10, 5))

        ctk.CTkLabel(preview_frame, text="プレビュー", font=("", 12, "bold")).pack(anchor="w", padx=10, pady=(5, 0))

        self.preview_text = ctk.CTkTextbox(preview_frame, height=200, wrap="word")
        self.preview_text.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        # ボタン
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(5, 0))

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

        # 構成を表示
        left_style = type_info.get("left_style", "")
        right_style = type_info.get("right_style", "")
        left_name = STYLE_NAMES.get(left_style, left_style)
        right_name = STYLE_NAMES.get(right_style, right_style)

        composition = f"[{left_name}] vs [{right_name}]"
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
