# -*- coding: utf-8 -*-
"""
衣装着用（Step3）設定ウィンドウ
素体三面図に衣装を着せるための設定
- プリセットから選択
- 参考画像から着せる
"""

import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog
from typing import Callable, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.base_settings_window import BaseSettingsWindow
from constants import OUTFIT_DATA, CHARACTER_STYLES


class OutfitWindow(BaseSettingsWindow):
    """衣装着用設定ウィンドウ（Step3）"""

    def __init__(
        self,
        parent,
        callback: Optional[Callable] = None,
        initial_data: Optional[dict] = None,
        body_sheet_path: Optional[str] = None  # Step2の出力画像パス
    ):
        """
        Args:
            parent: 親ウィンドウ
            callback: 設定完了時のコールバック
            initial_data: 初期データ（編集時）
            body_sheet_path: Step2で生成した素体三面図のパス
        """
        self.initial_data = initial_data or {}
        self.body_sheet_path = body_sheet_path
        super().__init__(
            parent,
            title="衣装着用設定",
            width=780,
            height=750,
            callback=callback
        )

    def build_content(self):
        """コンテンツを構築"""
        # === 入力画像（素体三面図） ===
        input_frame = ctk.CTkFrame(self.content_frame)
        input_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        input_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            input_frame,
            text="入力画像（素体三面図）",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkLabel(input_frame, text="素体三面図:").grid(row=1, column=0, padx=10, pady=5, sticky="w")

        img_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        img_frame.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        img_frame.grid_columnconfigure(0, weight=1)

        self.body_image_entry = ctk.CTkEntry(
            img_frame,
            placeholder_text="Step2で生成した素体三面図のパス"
        )
        self.body_image_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        if self.body_sheet_path:
            self.body_image_entry.insert(0, self.body_sheet_path)

        ctk.CTkButton(
            img_frame,
            text="参照",
            width=60,
            command=self._browse_body_image
        ).grid(row=0, column=1)

        # === 衣装選択方法 ===
        method_frame = ctk.CTkFrame(self.content_frame)
        method_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        method_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            method_frame,
            text="衣装選択方法",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        # ラジオボタン用変数
        self.outfit_source_var = tk.StringVar(value="preset")

        # プリセット選択
        self.preset_radio = ctk.CTkRadioButton(
            method_frame,
            text="プリセットから選ぶ",
            variable=self.outfit_source_var,
            value="preset",
            command=self._on_source_change
        )
        self.preset_radio.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # 参考画像選択
        self.reference_radio = ctk.CTkRadioButton(
            method_frame,
            text="参考画像から着せる",
            variable=self.outfit_source_var,
            value="reference",
            command=self._on_source_change
        )
        self.reference_radio.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # === プリセット衣装選択フレーム ===
        self.preset_frame = ctk.CTkFrame(self.content_frame)
        self.preset_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.preset_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            self.preset_frame,
            text="プリセット衣装",
            font=("Arial", 14, "bold")
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        # カテゴリ
        ctk.CTkLabel(self.preset_frame, text="カテゴリ:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.category_menu = ctk.CTkOptionMenu(
            self.preset_frame,
            values=list(OUTFIT_DATA["カテゴリ"].keys()),
            width=180,
            command=self._on_category_change
        )
        self.category_menu.set("カジュアル")
        self.category_menu.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # 形状
        ctk.CTkLabel(self.preset_frame, text="形状:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.shape_menu = ctk.CTkOptionMenu(
            self.preset_frame,
            values=["おまかせ"],
            width=180
        )
        self.shape_menu.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # 色
        ctk.CTkLabel(self.preset_frame, text="色:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.color_menu = ctk.CTkOptionMenu(
            self.preset_frame,
            values=list(OUTFIT_DATA["色"].keys()),
            width=180
        )
        self.color_menu.set("おまかせ")
        self.color_menu.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # 柄
        ctk.CTkLabel(self.preset_frame, text="柄:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.pattern_menu = ctk.CTkOptionMenu(
            self.preset_frame,
            values=list(OUTFIT_DATA["柄"].keys()),
            width=180
        )
        self.pattern_menu.set("おまかせ")
        self.pattern_menu.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        # スタイル
        ctk.CTkLabel(self.preset_frame, text="印象:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.style_menu = ctk.CTkOptionMenu(
            self.preset_frame,
            values=list(OUTFIT_DATA["スタイル"].keys()),
            width=180
        )
        self.style_menu.set("おまかせ")
        self.style_menu.grid(row=5, column=1, padx=5, pady=5, sticky="w")

        self._on_category_change("カジュアル")

        # === 参考画像フレーム ===
        self.reference_frame = ctk.CTkFrame(self.content_frame)
        self.reference_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        self.reference_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            self.reference_frame,
            text="参考画像から衣装を着せる",
            font=("Arial", 14, "bold")
        ).grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkLabel(self.reference_frame, text="衣装参考画像:").grid(row=1, column=0, padx=10, pady=5, sticky="w")

        ref_img_frame = ctk.CTkFrame(self.reference_frame, fg_color="transparent")
        ref_img_frame.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ref_img_frame.grid_columnconfigure(0, weight=1)

        self.reference_image_entry = ctk.CTkEntry(
            ref_img_frame,
            placeholder_text="着せたい衣装の参考画像を選択"
        )
        self.reference_image_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        ctk.CTkButton(
            ref_img_frame,
            text="参照",
            width=60,
            command=self._browse_reference_image
        ).grid(row=0, column=1)

        # 参考画像の説明
        ctk.CTkLabel(
            self.reference_frame,
            text="衣装説明:",
        ).grid(row=2, column=0, padx=10, pady=5, sticky="nw")

        self.reference_desc_textbox = ctk.CTkTextbox(self.reference_frame, height=50, wrap="word")
        self.reference_desc_textbox.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # === 衣装フィットモード ===
        ctk.CTkLabel(
            self.reference_frame,
            text="フィットモード:",
        ).grid(row=3, column=0, padx=10, pady=5, sticky="nw")

        fit_mode_frame = ctk.CTkFrame(self.reference_frame, fg_color="transparent")
        fit_mode_frame.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        self.fit_mode_var = tk.StringVar(value="base_priority")

        ctk.CTkRadioButton(
            fit_mode_frame,
            text="素体優先",
            variable=self.fit_mode_var,
            value="base_priority",
            command=self._on_fit_mode_change
        ).pack(side="left", padx=(0, 15))

        ctk.CTkRadioButton(
            fit_mode_frame,
            text="衣装優先",
            variable=self.fit_mode_var,
            value="outfit_priority",
            command=self._on_fit_mode_change
        ).pack(side="left", padx=(0, 15))

        ctk.CTkRadioButton(
            fit_mode_frame,
            text="ハイブリッド",
            variable=self.fit_mode_var,
            value="hybrid",
            command=self._on_fit_mode_change
        ).pack(side="left")

        # フィットモード説明
        fit_mode_desc = ctk.CTkLabel(
            self.reference_frame,
            text="素体優先: 衣装を素体にフィット / 衣装優先: 体型を衣装に合わせる / ハイブリッド: 顔は素体、体型は衣装",
            font=("Arial", 10),
            text_color="gray"
        )
        fit_mode_desc.grid(row=4, column=0, columnspan=2, padx=10, pady=(0, 5), sticky="w")

        # === 頭部装飾オプション ===
        self.include_headwear_var = tk.BooleanVar(value=True)
        self.headwear_checkbox = ctk.CTkCheckBox(
            self.reference_frame,
            text="頭部装飾（帽子・ヘルメット等）を含める",
            variable=self.include_headwear_var
        )
        self.headwear_checkbox.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # 頭部装飾オプション説明
        self.headwear_desc = ctk.CTkLabel(
            self.reference_frame,
            text="※ ハイブリッドモードでは頭部全体（髪型含む）が素体から取られるため、このオプションは無効です",
            font=("Arial", 10),
            text_color="gray"
        )
        self.headwear_desc.grid(row=6, column=0, columnspan=2, padx=10, pady=(0, 5), sticky="w")

        # 注意書き
        ctk.CTkLabel(
            self.reference_frame,
            text="※ 参考画像の著作権はユーザー責任です",
            font=("Arial", 10),
            text_color="orange"
        ).grid(row=7, column=0, columnspan=2, padx=10, pady=(0, 5), sticky="w")

        # 初期状態では参考画像フレームを無効化
        self._set_frame_state(self.reference_frame, "disabled")

        # === 描画スタイル ===
        style_frame = ctk.CTkFrame(self.content_frame)
        style_frame.grid(row=4, column=0, sticky="ew", padx=5, pady=5)
        style_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            style_frame,
            text="描画スタイル",
            font=("Arial", 14, "bold")
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkLabel(style_frame, text="スタイル:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.character_style_menu = ctk.CTkOptionMenu(
            style_frame,
            values=list(CHARACTER_STYLES.keys()),
            width=150
        )
        self.character_style_menu.set("標準アニメ")
        self.character_style_menu.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # === 追加説明 ===
        detail_frame = ctk.CTkFrame(self.content_frame)
        detail_frame.grid(row=5, column=0, sticky="ew", padx=5, pady=5)
        detail_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            detail_frame,
            text="追加説明",
            font=("Arial", 14, "bold")
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkLabel(detail_frame, text="詳細:").grid(row=1, column=0, padx=10, pady=5, sticky="nw")
        self.description_textbox = ctk.CTkTextbox(detail_frame, height=50, wrap="word")
        self.description_textbox.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # === 制約事項表示 ===
        constraint_frame = ctk.CTkFrame(self.content_frame)
        constraint_frame.grid(row=6, column=0, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(
            constraint_frame,
            text="生成時の制約",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        constraints_text = """• 素体三面図の顔・体型をそのまま使用（変更禁止）
• 指定された衣装を着用（素体の上に衣装を描画）
• 三面図形式を維持（正面/横/背面）
• 衣装のみを変更（髪型・顔は変更しない）"""

        ctk.CTkLabel(
            constraint_frame,
            text=constraints_text,
            font=("Arial", 11),
            justify="left"
        ).pack(anchor="w", padx=15, pady=(0, 10))

    def _browse_body_image(self):
        """素体三面図参照ダイアログ"""
        filename = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]
        )
        if filename:
            self.body_image_entry.delete(0, tk.END)
            self.body_image_entry.insert(0, filename)

    def _browse_reference_image(self):
        """衣装参考画像参照ダイアログ"""
        filename = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]
        )
        if filename:
            self.reference_image_entry.delete(0, tk.END)
            self.reference_image_entry.insert(0, filename)

    def _on_source_change(self):
        """衣装選択方法変更時"""
        source = self.outfit_source_var.get()
        if source == "preset":
            self._set_frame_state(self.preset_frame, "normal")
            self._set_frame_state(self.reference_frame, "disabled")
        else:
            self._set_frame_state(self.preset_frame, "disabled")
            self._set_frame_state(self.reference_frame, "normal")

    def _set_frame_state(self, frame, state):
        """フレーム内のウィジェットの状態を変更"""
        for child in frame.winfo_children():
            try:
                if isinstance(child, (ctk.CTkEntry, ctk.CTkOptionMenu, ctk.CTkTextbox, ctk.CTkButton)):
                    child.configure(state=state)
                elif isinstance(child, ctk.CTkFrame):
                    self._set_frame_state(child, state)
            except Exception:
                pass

    def _on_category_change(self, value):
        """カテゴリ変更時に形状オプションを更新"""
        shapes = OUTFIT_DATA["形状"].get(value, {"おまかせ": ""})
        self.shape_menu.configure(values=list(shapes.keys()))
        self.shape_menu.set("おまかせ")

    def _on_fit_mode_change(self):
        """フィットモード変更時の処理"""
        fit_mode = self.fit_mode_var.get()
        if fit_mode == "hybrid":
            # ハイブリッドモードでは頭部全体が素体から取られるため、頭部装飾オプションは無効
            self.headwear_checkbox.configure(state="disabled")
            self.include_headwear_var.set(False)
        else:
            # 素体優先/衣装優先では頭部装飾オプションを有効化
            self.headwear_checkbox.configure(state="normal")

    def collect_data(self) -> dict:
        """UIから設定データを収集"""
        desc = self.description_textbox.get("1.0", tk.END).strip()
        if desc == "（任意）衣装の追加詳細を記述":
            desc = ""

        ref_desc = self.reference_desc_textbox.get("1.0", tk.END).strip()
        if ref_desc == "（任意）参考画像の衣装について補足説明":
            ref_desc = ""

        outfit_source = self.outfit_source_var.get()

        data = {
            'step_type': 'step3_outfit',
            'body_sheet_path': self.body_image_entry.get().strip(),
            'outfit_source': outfit_source,  # "preset" or "reference"
            'character_style': self.character_style_menu.get(),
            'additional_description': desc
        }

        if outfit_source == "preset":
            data['outfit'] = {
                'category': self.category_menu.get(),
                'shape': self.shape_menu.get(),
                'color': self.color_menu.get(),
                'pattern': self.pattern_menu.get(),
                'style': self.style_menu.get()
            }
        else:
            data['reference_image_path'] = self.reference_image_entry.get().strip()
            data['reference_description'] = ref_desc
            data['fit_mode'] = self.fit_mode_var.get()  # base_priority / outfit_priority / hybrid
            data['include_headwear'] = self.include_headwear_var.get()  # 頭部装飾を含めるか

        return data

    def validate(self) -> tuple[bool, str]:
        """入力検証"""
        body_path = self.body_image_entry.get().strip()
        if not body_path:
            return False, "素体三面図の画像パスを指定してください。\n（Step2の出力画像を選択）"

        outfit_source = self.outfit_source_var.get()
        if outfit_source == "reference":
            ref_path = self.reference_image_entry.get().strip()
            if not ref_path:
                return False, "衣装参考画像を選択してください。"

        return True, ""
