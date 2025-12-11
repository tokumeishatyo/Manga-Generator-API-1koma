# -*- coding: utf-8 -*-
"""
設定ウィンドウの共通ベースクラス
各機能の設定ウィンドウはこのクラスを継承する
"""

import customtkinter as ctk
from typing import Callable, Optional


class BaseSettingsWindow(ctk.CTkToplevel):
    """設定ウィンドウの共通ベースクラス"""

    def __init__(
        self,
        parent,
        title: str,
        width: int = 800,
        height: int = 600,
        callback: Optional[Callable] = None
    ):
        """
        Args:
            parent: 親ウィンドウ
            title: ウィンドウタイトル
            width: ウィンドウ幅
            height: ウィンドウ高さ
            callback: 設定完了時のコールバック関数
        """
        super().__init__(parent)
        self.parent = parent
        self.callback = callback
        self.result_data = {}

        # ウィンドウ設定
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.transient(parent)  # 親ウィンドウに関連付け

        # グリッド設定
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # メインフレーム
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # コンテンツエリア（サブクラスでオーバーライド）
        self.content_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.content_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # ボタンエリア
        self.button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.button_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=(10, 5))
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)

        self.apply_btn = ctk.CTkButton(
            self.button_frame,
            text="適用",
            command=self.on_apply,
            width=120,
            height=35
        )
        self.apply_btn.grid(row=0, column=0, padx=5, sticky="e")

        self.cancel_btn = ctk.CTkButton(
            self.button_frame,
            text="キャンセル",
            command=self.on_cancel,
            width=120,
            height=35,
            fg_color="gray",
            hover_color="darkgray"
        )
        self.cancel_btn.grid(row=0, column=1, padx=5, sticky="w")

        # コンテンツを構築（サブクラスで実装）
        self.build_content()

        # フォーカス
        self.focus()

    def build_content(self):
        """コンテンツを構築（サブクラスでオーバーライド）"""
        pass

    def collect_data(self) -> dict:
        """UIから設定データを収集（サブクラスでオーバーライド）"""
        return {}

    def validate(self) -> tuple[bool, str]:
        """入力検証（サブクラスでオーバーライド）"""
        return True, ""

    def on_apply(self):
        """適用ボタンのハンドラ"""
        is_valid, error_msg = self.validate()
        if not is_valid:
            self.show_error(error_msg)
            return

        self.result_data = self.collect_data()
        if self.callback:
            self.callback(self.result_data)
        self.destroy()

    def on_cancel(self):
        """キャンセルボタンのハンドラ"""
        self.destroy()

    def show_error(self, message: str):
        """エラーメッセージを表示"""
        from tkinter import messagebox
        messagebox.showerror("エラー", message)

    def show_info(self, message: str):
        """情報メッセージを表示"""
        from tkinter import messagebox
        messagebox.showinfo("情報", message)
