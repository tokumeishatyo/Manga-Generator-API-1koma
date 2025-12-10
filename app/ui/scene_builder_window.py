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
    get_template_names,
    get_template,
    get_actions,
    get_backgrounds,
    generate_scene_prompt
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

        # ウィンドウ設定
        self.title("シーンビルダー")
        self.geometry("600x550")
        self.resizable(True, True)

        # モーダル風に設定（親ウィンドウの前面に表示）
        self.transient(parent)
        self.grab_set()

        # UI構築
        self._build_ui()

        # 初期プレビュー生成
        self._update_preview()

    def _build_ui(self):
        """UIを構築"""
        # メインフレーム
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # テンプレート選択
        template_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        template_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(template_frame, text="テンプレート:", font=("", 14, "bold")).pack(side="left")

        self.template_var = tk.StringVar(value="格闘ゲーム風")
        template_names = get_template_names()
        self.template_menu = ctk.CTkOptionMenu(
            template_frame,
            variable=self.template_var,
            values=template_names if template_names else ["(なし)"],
            command=self._on_template_change,
            width=200
        )
        self.template_menu.pack(side="left", padx=(10, 0))

        # 配置選択（左右入れ替え）
        layout_frame = ctk.CTkFrame(main_frame)
        layout_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(layout_frame, text="配置:", font=("", 13, "bold")).pack(anchor="w", padx=10, pady=(10, 5))

        self.layout_var = tk.StringVar(value="left_real")

        layout_options_frame = ctk.CTkFrame(layout_frame, fg_color="transparent")
        layout_options_frame.pack(fill="x", padx=20)

        self.layout_radio1 = ctk.CTkRadioButton(
            layout_options_frame,
            text="左: リアル（カットイン） / 右: ドット絵（2頭身）",
            variable=self.layout_var,
            value="left_real",
            command=self._update_preview
        )
        self.layout_radio1.pack(anchor="w", pady=2)

        self.layout_radio2 = ctk.CTkRadioButton(
            layout_options_frame,
            text="左: ドット絵（2頭身） / 右: リアル（カットイン）",
            variable=self.layout_var,
            value="left_deformed",
            command=self._update_preview
        )
        self.layout_radio2.pack(anchor="w", pady=2)

        # アクション選択
        action_frame = ctk.CTkFrame(main_frame)
        action_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(action_frame, text="アクション:", font=("", 13, "bold")).pack(anchor="w", padx=10, pady=(10, 5))

        action_options_frame = ctk.CTkFrame(action_frame, fg_color="transparent")
        action_options_frame.pack(fill="x", padx=20)

        # 左キャラアクション
        left_action_frame = ctk.CTkFrame(action_options_frame, fg_color="transparent")
        left_action_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(left_action_frame, text="左キャラ:", width=80).pack(side="left")

        self.left_action_var = tk.StringVar(value="attacking")
        actions = get_actions("格闘ゲーム風")
        action_keys = list(actions.keys()) if actions else ["attacking"]
        self.left_action_menu = ctk.CTkOptionMenu(
            left_action_frame,
            variable=self.left_action_var,
            values=action_keys,
            command=lambda _: self._update_preview(),
            width=150
        )
        self.left_action_menu.pack(side="left", padx=(10, 0))

        # 右キャラアクション
        right_action_frame = ctk.CTkFrame(action_options_frame, fg_color="transparent")
        right_action_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(right_action_frame, text="右キャラ:", width=80).pack(side="left")

        self.right_action_var = tk.StringVar(value="defending")
        self.right_action_menu = ctk.CTkOptionMenu(
            right_action_frame,
            variable=self.right_action_var,
            values=action_keys,
            command=lambda _: self._update_preview(),
            width=150
        )
        self.right_action_menu.pack(side="left", padx=(10, 0))

        # 背景選択
        bg_frame = ctk.CTkFrame(action_options_frame, fg_color="transparent")
        bg_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(bg_frame, text="背景:", width=80).pack(side="left")

        self.background_var = tk.StringVar(value="教室")
        backgrounds = get_backgrounds("格闘ゲーム風")
        bg_keys = list(backgrounds.keys()) if backgrounds else ["教室"]
        self.background_menu = ctk.CTkOptionMenu(
            bg_frame,
            variable=self.background_var,
            values=bg_keys,
            command=lambda _: self._update_preview(),
            width=150
        )
        self.background_menu.pack(side="left", padx=(10, 0))

        # 同一キャラオプション
        option_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        option_frame.pack(fill="x", pady=10)

        self.same_char_var = tk.BooleanVar(value=True)
        self.same_char_check = ctk.CTkCheckBox(
            option_frame,
            text="左右は同一キャラ（服装・髪型を統一）",
            variable=self.same_char_var,
            command=self._update_preview
        )
        self.same_char_check.pack(anchor="w")

        # プレビュー
        preview_frame = ctk.CTkFrame(main_frame)
        preview_frame.pack(fill="both", expand=True, pady=10)

        ctk.CTkLabel(preview_frame, text="プレビュー:", font=("", 13, "bold")).pack(anchor="w", padx=10, pady=(10, 5))

        self.preview_text = ctk.CTkTextbox(preview_frame, height=150, wrap="word")
        self.preview_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # ボタン
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))

        self.copy_button = ctk.CTkButton(
            button_frame,
            text="シーン説明にコピー",
            command=self._copy_to_scene,
            width=150
        )
        self.copy_button.pack(side="left", padx=(0, 10))

        self.close_button = ctk.CTkButton(
            button_frame,
            text="閉じる",
            command=self.destroy,
            width=100,
            fg_color="gray"
        )
        self.close_button.pack(side="left")

    def _on_template_change(self, template_name: str):
        """テンプレート変更時の処理"""
        # アクションと背景の選択肢を更新
        actions = get_actions(template_name)
        action_keys = list(actions.keys()) if actions else ["attacking"]

        self.left_action_menu.configure(values=action_keys)
        self.right_action_menu.configure(values=action_keys)

        if action_keys:
            self.left_action_var.set(action_keys[0])
            self.right_action_var.set(action_keys[1] if len(action_keys) > 1 else action_keys[0])

        backgrounds = get_backgrounds(template_name)
        bg_keys = list(backgrounds.keys()) if backgrounds else ["教室"]

        self.background_menu.configure(values=bg_keys)
        if bg_keys:
            self.background_var.set(bg_keys[0])

        self._update_preview()

    def _update_preview(self):
        """プレビューを更新"""
        template_name = self.template_var.get()
        left_is_real = self.layout_var.get() == "left_real"
        same_character = self.same_char_var.get()
        left_action = self.left_action_var.get()
        right_action = self.right_action_var.get()
        background = self.background_var.get()

        prompt = generate_scene_prompt(
            template_name=template_name,
            left_is_real=left_is_real,
            same_character=same_character,
            left_action=left_action,
            right_action=right_action,
            background=background
        )

        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert("1.0", prompt)

    def _copy_to_scene(self):
        """シーン説明にコピー"""
        prompt = self.preview_text.get("1.0", tk.END).strip()

        if self.callback:
            self.callback(prompt)

        self.destroy()
