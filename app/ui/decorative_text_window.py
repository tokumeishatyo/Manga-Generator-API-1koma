# -*- coding: utf-8 -*-
"""
装飾テキスト設定ウィンドウ
ui_text_overlay.yaml準拠
技名テロップ・決め台詞・キャラ名プレートの生成
"""

import tkinter as tk
import customtkinter as ctk
from typing import Callable, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.base_settings_window import BaseSettingsWindow


# テキストタイプ
TEXT_TYPES = {
    "技名テロップ": "special_move_title",
    "決め台詞": "impact_callout",
    "キャラ名プレート": "name_tag",
    "メッセージウィンドウ": "message_window"
}

# 技名テロップ用フォント
TITLE_FONTS = {
    "極太明朝": "Heavy Mincho",
    "筆文字": "Brush",
    "ゴシック": "Heavy Gothic"
}

# 技名テロップ用サイズ
TITLE_SIZES = {
    "特大": "Very Large",
    "大": "Large",
    "中": "Medium"
}

# グラデーション色
GRADIENT_COLORS = {
    "白→青": "White to Blue Gradient",
    "白→赤": "White to Red Gradient",
    "金→オレンジ": "Gold to Orange Gradient",
    "白→紫": "White to Purple Gradient",
    "単色白": "Solid White",
    "単色金": "Solid Gold"
}

# 縁取り色
OUTLINE_COLORS = {
    "金": "Gold",
    "黒": "Black",
    "赤": "Red",
    "青": "Blue",
    "なし": "None"
}

# 発光エフェクト
GLOW_EFFECTS = {
    "なし": "None",
    "青い稲妻": "Blue Lightning",
    "炎": "Fire Glow",
    "電撃": "Electric Spark",
    "オーラ": "Aura Glow"
}

# 決め台詞用タイプ
CALLOUT_TYPES = {
    "書き文字風": "Comic Sound Effect",
    "縦書き叫び": "Vertical Shout",
    "ポップ体": "Pop Style"
}

# 決め台詞用配色
CALLOUT_COLORS = {
    "赤＋黄縁": "Red with Yellow Border",
    "白＋黒縁": "White with Black Outline",
    "青＋白縁": "Blue with White Outline",
    "黄＋赤縁": "Yellow with Red Border"
}

# 回転角度
ROTATIONS = {
    "なし": "0 degrees",
    "少し左傾き": "-5 degrees",
    "左傾き": "-15 degrees",
    "少し右傾き": "5 degrees",
    "右傾き": "15 degrees"
}

# 変形効果
DISTORTIONS = {
    "なし": "None",
    "飛び出し": "Zoom In",
    "縮小": "Zoom Out",
    "波打ち": "Wave"
}

# キャラ名プレート用タイプ
NAMETAG_TYPES = {
    "ギザギザステッカー": "Jagged Sticker",
    "シンプル枠": "Simple Box",
    "リボン": "Ribbon Banner"
}

# メッセージウィンドウ用モード
MSGWIN_MODES = {
    "フルスペック（名前+顔+セリフ）": "full",
    "顔アイコンのみ": "face_only",
    "セリフのみ": "text_only"
}

# メッセージウィンドウ用スタイルプリセット
MSGWIN_STYLES = {
    "SF・ロボット風": "Sci-Fi Tech",
    "レトロRPG風": "Retro RPG",
    "ビジュアルノベル風": "Visual Novel"
}

# メッセージウィンドウ用フレームタイプ
MSGWIN_FRAME_TYPES = {
    "サイバネティック青": "Cybernetic Blue",
    "クラシック黒": "Classic Black",
    "半透明白": "Translucent White",
    "ゴールド装飾": "Gold Ornate"
}

# 顔アイコン位置
FACE_ICON_POSITIONS = {
    "左内側": "Left Inside",
    "右内側": "Right Inside",
    "左外側": "Left Outside",
    "なし": "None"
}


class DecorativeTextWindow(BaseSettingsWindow):
    """装飾テキスト設定ウィンドウ（ui_text_overlay.yaml準拠）"""

    def __init__(
        self,
        parent,
        callback: Optional[Callable] = None,
        initial_data: Optional[dict] = None
    ):
        self.initial_data = initial_data or {}
        super().__init__(
            parent,
            title="装飾テキスト設定",
            width=700,
            height=550,
            callback=callback
        )

    def build_content(self):
        """コンテンツを構築"""
        # === テキストタイプ選択 ===
        type_frame = ctk.CTkFrame(self.content_frame)
        type_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(
            type_frame,
            text="テキストタイプ",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        type_row = ctk.CTkFrame(type_frame, fg_color="transparent")
        type_row.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(type_row, text="タイプ:").pack(side="left", padx=(0, 5))
        self.type_menu = ctk.CTkOptionMenu(
            type_row,
            values=list(TEXT_TYPES.keys()),
            width=150,
            command=self._on_type_change
        )
        self.type_menu.set("技名テロップ")
        self.type_menu.pack(side="left")

        # 説明ラベル
        self.type_description = ctk.CTkLabel(
            type_frame,
            text="画面にドンと出る技名・必殺技名",
            font=("Arial", 11),
            text_color="gray"
        )
        self.type_description.pack(anchor="w", padx=10, pady=(0, 10))

        # === テキスト入力 ===
        text_frame = ctk.CTkFrame(self.content_frame)
        text_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        text_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            text_frame,
            text="テキスト内容",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkLabel(text_frame, text="テキスト:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.text_entry = ctk.CTkEntry(text_frame, placeholder_text="真空ビーム")
        self.text_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # === スタイル設定コンテナ（タイプ別に切り替え） ===
        self.style_container = ctk.CTkFrame(self.content_frame)
        self.style_container.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)

        # 各タイプ用のフレームを作成
        self._build_title_style_frame()
        self._build_callout_style_frame()
        self._build_nametag_style_frame()
        self._build_msgwin_style_frame()

        # 初期表示
        self._on_type_change("技名テロップ")

    def _build_title_style_frame(self):
        """技名テロップ用スタイルフレーム"""
        self.title_frame = ctk.CTkFrame(self.style_container)

        ctk.CTkLabel(
            self.title_frame,
            text="技名テロップスタイル",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        # フォントと文字サイズ
        row1 = ctk.CTkFrame(self.title_frame, fg_color="transparent")
        row1.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(row1, text="フォント:").pack(side="left", padx=(0, 5))
        self.title_font_menu = ctk.CTkOptionMenu(row1, values=list(TITLE_FONTS.keys()), width=120)
        self.title_font_menu.set("極太明朝")
        self.title_font_menu.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(row1, text="サイズ:").pack(side="left", padx=(0, 5))
        self.title_size_menu = ctk.CTkOptionMenu(row1, values=list(TITLE_SIZES.keys()), width=100)
        self.title_size_menu.set("特大")
        self.title_size_menu.pack(side="left")

        # 色設定
        row2 = ctk.CTkFrame(self.title_frame, fg_color="transparent")
        row2.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(row2, text="文字色:").pack(side="left", padx=(0, 5))
        self.title_color_menu = ctk.CTkOptionMenu(row2, values=list(GRADIENT_COLORS.keys()), width=140)
        self.title_color_menu.set("白→青")
        self.title_color_menu.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(row2, text="縁取り:").pack(side="left", padx=(0, 5))
        self.title_outline_menu = ctk.CTkOptionMenu(row2, values=list(OUTLINE_COLORS.keys()), width=80)
        self.title_outline_menu.set("金")
        self.title_outline_menu.pack(side="left")

        # エフェクト
        row3 = ctk.CTkFrame(self.title_frame, fg_color="transparent")
        row3.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(row3, text="発光効果:").pack(side="left", padx=(0, 5))
        self.title_glow_menu = ctk.CTkOptionMenu(row3, values=list(GLOW_EFFECTS.keys()), width=120)
        self.title_glow_menu.set("青い稲妻")
        self.title_glow_menu.pack(side="left", padx=(0, 15))

        self.title_shadow_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(row3, text="ドロップシャドウ", variable=self.title_shadow_var).pack(side="left")

    def _build_callout_style_frame(self):
        """決め台詞用スタイルフレーム"""
        self.callout_frame = ctk.CTkFrame(self.style_container)

        ctk.CTkLabel(
            self.callout_frame,
            text="決め台詞スタイル",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        # タイプと配色
        row1 = ctk.CTkFrame(self.callout_frame, fg_color="transparent")
        row1.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(row1, text="表現:").pack(side="left", padx=(0, 5))
        self.callout_type_menu = ctk.CTkOptionMenu(row1, values=list(CALLOUT_TYPES.keys()), width=120)
        self.callout_type_menu.set("書き文字風")
        self.callout_type_menu.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(row1, text="配色:").pack(side="left", padx=(0, 5))
        self.callout_color_menu = ctk.CTkOptionMenu(row1, values=list(CALLOUT_COLORS.keys()), width=130)
        self.callout_color_menu.set("赤＋黄縁")
        self.callout_color_menu.pack(side="left")

        # 変形効果
        row2 = ctk.CTkFrame(self.callout_frame, fg_color="transparent")
        row2.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(row2, text="回転:").pack(side="left", padx=(0, 5))
        self.callout_rotation_menu = ctk.CTkOptionMenu(row2, values=list(ROTATIONS.keys()), width=120)
        self.callout_rotation_menu.set("左傾き")
        self.callout_rotation_menu.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(row2, text="変形:").pack(side="left", padx=(0, 5))
        self.callout_distortion_menu = ctk.CTkOptionMenu(row2, values=list(DISTORTIONS.keys()), width=100)
        self.callout_distortion_menu.set("飛び出し")
        self.callout_distortion_menu.pack(side="left")

    def _build_nametag_style_frame(self):
        """キャラ名プレート用スタイルフレーム"""
        self.nametag_frame = ctk.CTkFrame(self.style_container)

        ctk.CTkLabel(
            self.nametag_frame,
            text="キャラ名プレートスタイル",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        # タイプと回転
        row1 = ctk.CTkFrame(self.nametag_frame, fg_color="transparent")
        row1.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(row1, text="デザイン:").pack(side="left", padx=(0, 5))
        self.nametag_type_menu = ctk.CTkOptionMenu(row1, values=list(NAMETAG_TYPES.keys()), width=150)
        self.nametag_type_menu.set("ギザギザステッカー")
        self.nametag_type_menu.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(row1, text="回転:").pack(side="left", padx=(0, 5))
        self.nametag_rotation_menu = ctk.CTkOptionMenu(row1, values=list(ROTATIONS.keys()), width=120)
        self.nametag_rotation_menu.set("少し左傾き")
        self.nametag_rotation_menu.pack(side="left")

    def _build_msgwin_style_frame(self):
        """メッセージウィンドウ用スタイルフレーム"""
        self.msgwin_frame = ctk.CTkFrame(self.style_container)

        ctk.CTkLabel(
            self.msgwin_frame,
            text="メッセージウィンドウスタイル",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        # モード選択
        mode_row = ctk.CTkFrame(self.msgwin_frame, fg_color="transparent")
        mode_row.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(mode_row, text="モード:").pack(side="left", padx=(0, 5))
        self.msgwin_mode_menu = ctk.CTkOptionMenu(
            mode_row,
            values=list(MSGWIN_MODES.keys()),
            width=220,
            command=self._on_msgwin_mode_change
        )
        self.msgwin_mode_menu.set("フルスペック（名前+顔+セリフ）")
        self.msgwin_mode_menu.pack(side="left")

        # 話者名入力（フルスペック時のみ）
        self.msgwin_name_row = ctk.CTkFrame(self.msgwin_frame, fg_color="transparent")
        self.msgwin_name_row.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(self.msgwin_name_row, text="話者名:").pack(side="left", padx=(0, 5))
        self.msgwin_speaker_entry = ctk.CTkEntry(self.msgwin_name_row, placeholder_text="彩瀬こよみ", width=150)
        self.msgwin_speaker_entry.pack(side="left", padx=(0, 15))

        # スタイルプリセット
        ctk.CTkLabel(self.msgwin_name_row, text="スタイル:").pack(side="left", padx=(0, 5))
        self.msgwin_style_menu = ctk.CTkOptionMenu(
            self.msgwin_name_row,
            values=list(MSGWIN_STYLES.keys()),
            width=150
        )
        self.msgwin_style_menu.set("SF・ロボット風")
        self.msgwin_style_menu.pack(side="left")

        # フレームデザイン（フルスペック・セリフのみ時）
        self.msgwin_design_row = ctk.CTkFrame(self.msgwin_frame, fg_color="transparent")
        self.msgwin_design_row.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(self.msgwin_design_row, text="枠デザイン:").pack(side="left", padx=(0, 5))
        self.msgwin_frame_menu = ctk.CTkOptionMenu(
            self.msgwin_design_row,
            values=list(MSGWIN_FRAME_TYPES.keys()),
            width=150
        )
        self.msgwin_frame_menu.set("サイバネティック青")
        self.msgwin_frame_menu.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(self.msgwin_design_row, text="透明度:").pack(side="left", padx=(0, 5))
        self.msgwin_opacity_slider = ctk.CTkSlider(self.msgwin_design_row, from_=0.3, to=1.0, width=100)
        self.msgwin_opacity_slider.set(0.8)
        self.msgwin_opacity_slider.pack(side="left")

        # 顔アイコン設定（フルスペック・顔のみ時）
        self.msgwin_face_row = ctk.CTkFrame(self.msgwin_frame, fg_color="transparent")
        self.msgwin_face_row.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(self.msgwin_face_row, text="顔アイコン位置:").pack(side="left", padx=(0, 5))
        self.msgwin_face_pos_menu = ctk.CTkOptionMenu(
            self.msgwin_face_row,
            values=list(FACE_ICON_POSITIONS.keys()),
            width=100
        )
        self.msgwin_face_pos_menu.set("左内側")
        self.msgwin_face_pos_menu.pack(side="left")

    def _on_msgwin_mode_change(self, value):
        """メッセージウィンドウモード変更時"""
        # 全行を一旦非表示
        self.msgwin_name_row.pack_forget()
        self.msgwin_design_row.pack_forget()
        self.msgwin_face_row.pack_forget()

        if value == "フルスペック（名前+顔+セリフ）":
            # 全て表示
            self.msgwin_name_row.pack(fill="x", padx=10, pady=5)
            self.msgwin_design_row.pack(fill="x", padx=10, pady=5)
            self.msgwin_face_row.pack(fill="x", padx=10, pady=5)
        elif value == "顔アイコンのみ":
            # 顔設定のみ
            self.msgwin_face_row.pack(fill="x", padx=10, pady=5)
        elif value == "セリフのみ":
            # デザイン設定のみ
            self.msgwin_design_row.pack(fill="x", padx=10, pady=5)

    def _on_type_change(self, value):
        """テキストタイプ変更時"""
        # 全フレームを非表示
        self.title_frame.pack_forget()
        self.callout_frame.pack_forget()
        self.nametag_frame.pack_forget()
        self.msgwin_frame.pack_forget()

        # 選択されたタイプのフレームを表示
        if value == "技名テロップ":
            self.title_frame.pack(fill="both", expand=True)
            self.type_description.configure(text="画面にドンと出る技名・必殺技名")
            self.text_entry.configure(placeholder_text="真空ビーム")
        elif value == "決め台詞":
            self.callout_frame.pack(fill="both", expand=True)
            self.type_description.configure(text="キャラの横に出る派手なセリフ・掛け声")
            self.text_entry.configure(placeholder_text="もらったー！")
        elif value == "キャラ名プレート":
            self.nametag_frame.pack(fill="both", expand=True)
            self.type_description.configure(text="キャラクターの名前表示プレート")
            self.text_entry.configure(placeholder_text="篠宮りん")
        elif value == "メッセージウィンドウ":
            self.msgwin_frame.pack(fill="both", expand=True)
            self.type_description.configure(text="画面下部のセリフウィンドウ（RPG/ADV風）")
            self.text_entry.configure(placeholder_text="「もらったー」")

    def collect_data(self) -> dict:
        """UIから設定データを収集"""
        text_type = self.type_menu.get()
        text_content = self.text_entry.get().strip()

        data = {
            'text_type': text_type,
            'text': text_content
        }

        if text_type == "技名テロップ":
            data['style'] = {
                'font': self.title_font_menu.get(),
                'size': self.title_size_menu.get(),
                'color': self.title_color_menu.get(),
                'outline': self.title_outline_menu.get(),
                'glow': self.title_glow_menu.get(),
                'shadow': self.title_shadow_var.get()
            }
        elif text_type == "決め台詞":
            data['style'] = {
                'type': self.callout_type_menu.get(),
                'color': self.callout_color_menu.get(),
                'rotation': self.callout_rotation_menu.get(),
                'distortion': self.callout_distortion_menu.get()
            }
        elif text_type == "キャラ名プレート":
            data['style'] = {
                'type': self.nametag_type_menu.get(),
                'rotation': self.nametag_rotation_menu.get()
            }
        elif text_type == "メッセージウィンドウ":
            mode = self.msgwin_mode_menu.get()
            data['mode'] = mode
            data['speaker_name'] = self.msgwin_speaker_entry.get().strip()
            data['style'] = {
                'preset': self.msgwin_style_menu.get(),
                'frame_type': self.msgwin_frame_menu.get(),
                'opacity': round(self.msgwin_opacity_slider.get(), 2),
                'face_icon_position': self.msgwin_face_pos_menu.get()
            }

        return data

    def validate(self) -> tuple[bool, str]:
        """入力検証"""
        if not self.text_entry.get().strip():
            return False, "テキストを入力してください。"
        return True, ""
