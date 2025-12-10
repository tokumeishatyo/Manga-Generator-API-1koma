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
    get_beam_colors,
    get_beam_types,
    get_beam_emissions,
    generate_scene_prompt,
    STYLE_NAMES,
    BEAM_COLORS,
    BEAM_TYPES,
    BEAM_EMISSIONS
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
        self.geometry("750x800")
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
            command=self._on_action_change,
            width=120
        )
        self.left_action_menu.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(action_row, text="右:").pack(side="left", padx=(0, 2))
        self.right_action_var = tk.StringVar(value="防御")
        self.right_action_menu = ctk.CTkOptionMenu(
            action_row,
            variable=self.right_action_var,
            values=action_display_names,
            command=self._on_action_change,
            width=120
        )
        self.right_action_menu.pack(side="left")

        # ズーム（1キャラモード用）
        ctk.CTkLabel(action_row, text="ズーム:").pack(side="left", padx=(20, 2))
        self.zoom_var = tk.StringVar(value="通常")
        self.zoom_menu = ctk.CTkOptionMenu(
            action_row,
            variable=self.zoom_var,
            values=["通常", "ドアップ"],
            command=lambda _: self._update_preview(),
            width=90
        )
        self.zoom_menu.pack(side="left")
        self.zoom_menu.configure(state="disabled")  # 初期状態は無効

        # 向き（1キャラモード用）
        ctk.CTkLabel(action_row, text="向き:").pack(side="left", padx=(10, 2))
        self.facing_var = tk.StringVar(value="指定なし")
        self.facing_menu = ctk.CTkOptionMenu(
            action_row,
            variable=self.facing_var,
            values=["指定なし", "右向き→", "←左向き"],
            command=lambda _: self._update_preview(),
            width=90
        )
        self.facing_menu.pack(side="left")
        self.facing_menu.configure(state="disabled")  # 初期状態は無効

        # 光線オプション - 左キャラ（攻撃時のみ有効）
        beam_row1 = ctk.CTkFrame(main_frame, fg_color="transparent")
        beam_row1.pack(fill="x", pady=5)

        ctk.CTkLabel(beam_row1, text="光線(左):", width=100).pack(side="left")

        ctk.CTkLabel(beam_row1, text="色:").pack(side="left", padx=(5, 2))
        self.left_beam_color_var = tk.StringVar(value="おまかせ")
        self.left_beam_color_menu = ctk.CTkOptionMenu(
            beam_row1,
            variable=self.left_beam_color_var,
            values=get_beam_colors(),
            command=lambda _: self._update_preview(),
            width=80
        )
        self.left_beam_color_menu.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(beam_row1, text="タイプ:").pack(side="left", padx=(0, 2))
        self.left_beam_type_var = tk.StringVar(value="おまかせ")
        self.left_beam_type_menu = ctk.CTkOptionMenu(
            beam_row1,
            variable=self.left_beam_type_var,
            values=get_beam_types(),
            command=lambda _: self._update_preview(),
            width=90
        )
        self.left_beam_type_menu.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(beam_row1, text="発射:").pack(side="left", padx=(0, 2))
        self.left_beam_emission_var = tk.StringVar(value="おまかせ")
        self.left_beam_emission_menu = ctk.CTkOptionMenu(
            beam_row1,
            variable=self.left_beam_emission_var,
            values=get_beam_emissions(),
            command=lambda _: self._update_preview(),
            width=100
        )
        self.left_beam_emission_menu.pack(side="left")

        # 光線オプション - 右キャラ（攻撃時のみ有効）
        beam_row2 = ctk.CTkFrame(main_frame, fg_color="transparent")
        beam_row2.pack(fill="x", pady=5)

        ctk.CTkLabel(beam_row2, text="光線(右):", width=100).pack(side="left")

        ctk.CTkLabel(beam_row2, text="色:").pack(side="left", padx=(5, 2))
        self.right_beam_color_var = tk.StringVar(value="おまかせ")
        self.right_beam_color_menu = ctk.CTkOptionMenu(
            beam_row2,
            variable=self.right_beam_color_var,
            values=get_beam_colors(),
            command=lambda _: self._update_preview(),
            width=80
        )
        self.right_beam_color_menu.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(beam_row2, text="タイプ:").pack(side="left", padx=(0, 2))
        self.right_beam_type_var = tk.StringVar(value="おまかせ")
        self.right_beam_type_menu = ctk.CTkOptionMenu(
            beam_row2,
            variable=self.right_beam_type_var,
            values=get_beam_types(),
            command=lambda _: self._update_preview(),
            width=90
        )
        self.right_beam_type_menu.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(beam_row2, text="発射:").pack(side="left", padx=(0, 2))
        self.right_beam_emission_var = tk.StringVar(value="おまかせ")
        self.right_beam_emission_menu = ctk.CTkOptionMenu(
            beam_row2,
            variable=self.right_beam_emission_var,
            values=get_beam_emissions(),
            command=lambda _: self._update_preview(),
            width=100
        )
        self.right_beam_emission_menu.pack(side="left")

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

        # UI要素トグル（7行目）
        ui_row = ctk.CTkFrame(main_frame, fg_color="transparent")
        ui_row.pack(fill="x", pady=5)

        ctk.CTkLabel(ui_row, text="UI要素:", width=100).pack(side="left")

        self.health_bars_var = tk.BooleanVar(value=True)
        self.health_bars_cb = ctk.CTkCheckBox(
            ui_row,
            text="ヘルスバー",
            variable=self.health_bars_var,
            command=self._update_preview,
            width=100
        )
        self.health_bars_cb.pack(side="left", padx=(5, 15))

        self.super_meter_var = tk.BooleanVar(value=True)
        self.super_meter_cb = ctk.CTkCheckBox(
            ui_row,
            text="SUPERゲージ",
            variable=self.super_meter_var,
            command=self._update_preview,
            width=120
        )
        self.super_meter_cb.pack(side="left", padx=(0, 15))

        self.dialogue_box_var = tk.BooleanVar(value=False)
        self.dialogue_box_cb = ctk.CTkCheckBox(
            ui_row,
            text="ダイアログボックス",
            variable=self.dialogue_box_var,
            command=self._update_preview,
            width=140
        )
        self.dialogue_box_cb.pack(side="left")

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

        # 1キャラモードかどうか
        single_character = type_info.get("single_character", False)

        # 構成を表示
        left_style = type_info.get("left_style", "")
        right_style = type_info.get("right_style")
        left_name = STYLE_NAMES.get(left_style, left_style)

        if single_character:
            composition = f"[{left_name}]"
            # 右側の入力を無効化、ズーム・向きを有効化
            self.right_action_menu.configure(state="disabled")
            self.right_name_entry.configure(state="disabled")
            self.right_speech_entry.configure(state="disabled")
            self.zoom_menu.configure(state="normal")
            self.facing_menu.configure(state="normal")
        else:
            right_name = STYLE_NAMES.get(right_style, right_style) if right_style else ""
            composition = f"[{left_name}] vs [{right_name}]"
            # 右側の入力を有効化、ズーム・向きを無効化
            self.right_action_menu.configure(state="normal")
            self.right_name_entry.configure(state="normal")
            self.right_speech_entry.configure(state="normal")
            self.zoom_menu.configure(state="disabled")
            self.facing_menu.configure(state="disabled")

        self.composition_label.configure(text=composition)

        self._update_beam_options_state()
        self._update_preview()

    def _on_action_change(self, _):
        """アクション変更時の処理"""
        self._update_beam_options_state()
        self._update_preview()

    def _update_beam_options_state(self):
        """光線オプションの有効/無効を更新"""
        # 左キャラの光線オプション
        left_action = self.left_action_var.get()
        left_beam_state = "normal" if left_action == "攻撃" else "disabled"
        self.left_beam_color_menu.configure(state=left_beam_state)
        self.left_beam_type_menu.configure(state=left_beam_state)
        self.left_beam_emission_menu.configure(state=left_beam_state)

        # 右キャラの光線オプション（2キャラモードかつ攻撃時のみ）
        right_action = self.right_action_var.get()
        scene_type = self.scene_type_var.get()
        type_info = get_scene_type_info(scene_type)
        single_character = type_info.get("single_character", False)

        if single_character:
            right_beam_state = "disabled"
        else:
            right_beam_state = "normal" if right_action == "攻撃" else "disabled"

        self.right_beam_color_menu.configure(state=right_beam_state)
        self.right_beam_type_menu.configure(state=right_beam_state)
        self.right_beam_emission_menu.configure(state=right_beam_state)

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

        # UIトグル
        show_health_bars = self.health_bars_var.get()
        show_super_meter = self.super_meter_var.get()
        show_dialogue_box = self.dialogue_box_var.get()

        # ズーム（1キャラモード用）
        zoom_jp = self.zoom_var.get()
        zoom = "extreme" if zoom_jp == "ドアップ" else "normal"

        # 向き（1キャラモード用）
        facing_jp = self.facing_var.get()
        if facing_jp == "右向き→":
            facing = "right"
        elif facing_jp == "←左向き":
            facing = "left"
        else:
            facing = ""

        # 光線オプション - 左キャラ（日本語 → 英語変換）
        left_beam_color = BEAM_COLORS.get(self.left_beam_color_var.get(), "")
        left_beam_type = BEAM_TYPES.get(self.left_beam_type_var.get(), "")
        left_beam_emission = BEAM_EMISSIONS.get(self.left_beam_emission_var.get(), "")

        # 光線オプション - 右キャラ（日本語 → 英語変換）
        right_beam_color = BEAM_COLORS.get(self.right_beam_color_var.get(), "")
        right_beam_type = BEAM_TYPES.get(self.right_beam_type_var.get(), "")
        right_beam_emission = BEAM_EMISSIONS.get(self.right_beam_emission_var.get(), "")

        prompt = generate_scene_prompt(
            scene_type=scene_type,
            left_action=left_action,
            right_action=right_action,
            background=background,
            left_name=left_name,
            right_name=right_name,
            left_speech=left_speech,
            right_speech=right_speech,
            move_name=move_name,
            show_health_bars=show_health_bars,
            show_super_meter=show_super_meter,
            show_dialogue_box=show_dialogue_box,
            zoom=zoom,
            facing=facing,
            left_beam_color=left_beam_color,
            left_beam_type=left_beam_type,
            left_beam_emission=left_beam_emission,
            right_beam_color=right_beam_color,
            right_beam_type=right_beam_type,
            right_beam_emission=right_beam_emission
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
