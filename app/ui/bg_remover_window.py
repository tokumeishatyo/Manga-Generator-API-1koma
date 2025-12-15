# -*- coding: utf-8 -*-
"""
背景透過ユーティリティウィンドウ
AIを使わずにローカルで背景を透過処理
"""

import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import Optional
from PIL import Image
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class BgRemoverWindow(ctk.CTkToplevel):
    """背景透過ユーティリティウィンドウ"""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("背景透過ツール")
        self.geometry("550x450")
        self.resizable(False, False)

        # モーダル風に
        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self._center_window()

    def _center_window(self):
        """ウィンドウを中央に配置"""
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_width()) // 2
        y = (self.winfo_screenheight() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def _build_ui(self):
        """UIを構築"""
        # === 入力ファイル ===
        input_frame = ctk.CTkFrame(self)
        input_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            input_frame,
            text="入力画像",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        file_row = ctk.CTkFrame(input_frame, fg_color="transparent")
        file_row.pack(fill="x", padx=10, pady=5)
        file_row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(file_row, text="ファイル:").grid(row=0, column=0, padx=(0, 5), sticky="w")
        self.input_entry = ctk.CTkEntry(file_row, placeholder_text="画像ファイルを選択")
        self.input_entry.grid(row=0, column=1, sticky="ew", padx=(0, 5))
        ctk.CTkButton(file_row, text="参照", width=60, command=self._browse_input).grid(row=0, column=2)

        # === 処理方法選択 ===
        method_frame = ctk.CTkFrame(self)
        method_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            method_frame,
            text="処理方法",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        self.method_var = tk.StringVar(value="color")

        # 方法1: 単色背景除去
        method1_frame = ctk.CTkFrame(method_frame, fg_color="transparent")
        method1_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkRadioButton(
            method1_frame,
            text="単色背景を透過",
            variable=self.method_var,
            value="color",
            command=self._on_method_change
        ).pack(side="left")

        ctk.CTkLabel(
            method1_frame,
            text="（白背景など単色の場合に最適）",
            font=("Arial", 10),
            text_color="gray"
        ).pack(side="left", padx=10)

        # 色選択
        self.color_options_frame = ctk.CTkFrame(method_frame, fg_color="transparent")
        self.color_options_frame.pack(fill="x", padx=30, pady=5)

        ctk.CTkLabel(self.color_options_frame, text="除去する色:").pack(side="left", padx=(0, 5))
        self.color_menu = ctk.CTkOptionMenu(
            self.color_options_frame,
            values=["白", "黒", "緑（グリーンバック）", "青（ブルーバック）"],
            width=160
        )
        self.color_menu.set("白")
        self.color_menu.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(self.color_options_frame, text="許容値:").pack(side="left", padx=(0, 5))
        self.tolerance_slider = ctk.CTkSlider(self.color_options_frame, from_=0, to=100, width=100)
        self.tolerance_slider.set(30)
        self.tolerance_slider.pack(side="left")

        # 方法2: 自動背景除去
        method2_frame = ctk.CTkFrame(method_frame, fg_color="transparent")
        method2_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkRadioButton(
            method2_frame,
            text="自動背景除去（rembg）",
            variable=self.method_var,
            value="rembg",
            command=self._on_method_change
        ).pack(side="left")

        ctk.CTkLabel(
            method2_frame,
            text="（複雑な背景も対応、初回モデルDL要）",
            font=("Arial", 10),
            text_color="gray"
        ).pack(side="left", padx=10)

        # === 出力設定 ===
        output_frame = ctk.CTkFrame(self)
        output_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            output_frame,
            text="出力設定",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        output_row = ctk.CTkFrame(output_frame, fg_color="transparent")
        output_row.pack(fill="x", padx=10, pady=5)
        output_row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(output_row, text="保存先:").grid(row=0, column=0, padx=(0, 5), sticky="w")
        self.output_entry = ctk.CTkEntry(output_row, placeholder_text="自動（入力ファイル名_transparent.png）")
        self.output_entry.grid(row=0, column=1, sticky="ew", padx=(0, 5))
        ctk.CTkButton(output_row, text="参照", width=60, command=self._browse_output).grid(row=0, column=2)

        # === 実行ボタン ===
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=20)

        ctk.CTkButton(
            button_frame,
            text="背景を透過",
            width=200,
            height=40,
            command=self._execute
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            button_frame,
            text="閉じる",
            width=100,
            height=40,
            fg_color="gray",
            command=self.destroy
        ).pack(side="right", padx=10)

        # ステータス表示
        self.status_label = ctk.CTkLabel(
            self,
            text="",
            font=("Arial", 11),
            text_color="gray"
        )
        self.status_label.pack(anchor="w", padx=20, pady=(0, 10))

    def _on_method_change(self):
        """処理方法変更時"""
        if self.method_var.get() == "color":
            self.color_options_frame.pack(fill="x", padx=30, pady=5)
        else:
            self.color_options_frame.pack_forget()

    def _browse_input(self):
        """入力ファイル選択"""
        filename = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]
        )
        if filename:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, filename)

    def _browse_output(self):
        """出力ファイル選択"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")]
        )
        if filename:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, filename)

    def _execute(self):
        """背景透過処理を実行"""
        input_path = self.input_entry.get().strip()
        if not input_path:
            messagebox.showerror("エラー", "入力画像を選択してください。")
            return

        if not os.path.exists(input_path):
            messagebox.showerror("エラー", "入力ファイルが見つかりません。")
            return

        # 出力パスを決定
        output_path = self.output_entry.get().strip()
        if not output_path:
            base, _ = os.path.splitext(input_path)
            output_path = f"{base}_transparent.png"

        self.status_label.configure(text="処理中...")
        self.update()

        try:
            if self.method_var.get() == "color":
                self._remove_color_background(input_path, output_path)
            else:
                self._remove_background_rembg(input_path, output_path)

            self.status_label.configure(text=f"完了: {os.path.basename(output_path)}")
            messagebox.showinfo("完了", f"背景透過が完了しました。\n\n保存先: {output_path}")

        except ImportError as e:
            self.status_label.configure(text="エラー: ライブラリが見つかりません")
            messagebox.showerror("エラー", f"必要なライブラリがインストールされていません。\n\n{str(e)}\n\npip install rembg でインストールしてください。")
        except Exception as e:
            self.status_label.configure(text="エラー")
            messagebox.showerror("エラー", f"処理中にエラーが発生しました。\n\n{str(e)}")

    def _remove_color_background(self, input_path: str, output_path: str):
        """単色背景を透過に変換"""
        img = Image.open(input_path).convert("RGBA")
        data = img.getdata()

        # 除去する色を決定
        color_name = self.color_menu.get()
        if color_name == "白":
            target_color = (255, 255, 255)
        elif color_name == "黒":
            target_color = (0, 0, 0)
        elif color_name == "緑（グリーンバック）":
            target_color = (0, 255, 0)
        elif color_name == "青（ブルーバック）":
            target_color = (0, 0, 255)
        else:
            target_color = (255, 255, 255)

        tolerance = int(self.tolerance_slider.get())

        new_data = []
        for item in data:
            r, g, b, a = item
            # 色の距離を計算
            distance = abs(r - target_color[0]) + abs(g - target_color[1]) + abs(b - target_color[2])
            if distance <= tolerance * 3:  # 許容値を3倍（RGB各チャンネル分）
                new_data.append((r, g, b, 0))  # 透明に
            else:
                new_data.append(item)

        img.putdata(new_data)
        img.save(output_path, "PNG")

    def _remove_background_rembg(self, input_path: str, output_path: str):
        """rembgを使って自動背景除去"""
        from rembg import remove

        with open(input_path, "rb") as f:
            input_data = f.read()

        output_data = remove(input_data)

        with open(output_path, "wb") as f:
            f.write(output_data)
