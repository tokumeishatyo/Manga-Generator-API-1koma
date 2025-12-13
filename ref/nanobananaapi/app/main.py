import os
import json
import threading
import io
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import yaml
import pyperclip
from PIL import Image
from google import genai
from google.genai import types

# Set appearance mode and default color theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Constants
MAX_SPEECH_LENGTH = 15
MAX_RECENT_FILES = 5

# 服装データ定義
OUTFIT_DATA = {
    "カテゴリ": {
        "おまかせ": "",
        "スーツ": "business suit",
        "水着": "swimsuit",
        "カジュアル": "casual wear",
        "制服": "uniform",
        "ドレス/フォーマル": "formal wear",
        "スポーツ": "sportswear",
        "和服": "japanese traditional clothing",
        "作業着/職業服": "work uniform"
    },
    "形状": {
        "スーツ": {
            "おまかせ": "",
            "パンツスタイル": "pant suit, trousers",
            "タイトスカート": "pencil skirt",
            "プリーツスカート": "pleated skirt",
            "ミニスカート": "mini skirt suit",
            "スリーピース": "three-piece suit, vest",
            "ダブルスーツ": "double-breasted suit",
            "タキシード": "tuxedo, formal suit"
        },
        "水着": {
            "おまかせ": "",
            "三角ビキニ": "triangle bikini",
            "ホルターネック": "halter neck bikini",
            "バンドゥ": "bandeau bikini",
            "ワンピース": "one-piece swimsuit",
            "ハイレグ": "high-leg swimsuit",
            "パレオ付き": "bikini with pareo",
            "サーフパンツ": "surf shorts, board shorts",
            "競泳パンツ": "racing briefs, speedo"
        },
        "カジュアル": {
            "おまかせ": "",
            "Tシャツ+デニム": "t-shirt and denim jeans",
            "ワンピース": "casual dress",
            "ブラウス+スカート": "blouse and skirt",
            "パーカー": "hoodie",
            "カーディガン": "cardigan outfit",
            "シャツ+チノパン": "button-down shirt and chinos",
            "ポロシャツ": "polo shirt",
            "レザージャケット": "leather jacket"
        },
        "制服": {
            "おまかせ": "",
            "セーラー服": "sailor uniform",
            "ブレザー": "blazer uniform",
            "メイド服": "maid uniform",
            "ナース服": "nurse uniform",
            "OL制服": "office lady uniform",
            "学ラン": "gakuran, japanese male school uniform",
            "詰襟": "standing collar uniform",
            "警察官": "police uniform",
            "軍服": "military uniform"
        },
        "ドレス/フォーマル": {
            "おまかせ": "",
            "イブニングドレス": "evening gown",
            "カクテルドレス": "cocktail dress",
            "ウェディングドレス": "wedding dress",
            "チャイナドレス": "chinese dress, cheongsam",
            "サマードレス": "summer dress",
            "タキシード": "tuxedo",
            "モーニング": "morning coat, formal suit",
            "燕尾服": "tailcoat, white tie"
        },
        "スポーツ": {
            "おまかせ": "",
            "テニスウェア": "tennis wear",
            "体操服": "gym uniform",
            "レオタード": "leotard",
            "ヨガウェア": "yoga wear",
            "競泳水着": "racing swimsuit",
            "サッカーユニフォーム": "soccer jersey, football kit",
            "野球ユニフォーム": "baseball uniform",
            "バスケユニフォーム": "basketball jersey",
            "柔道着": "judo gi, martial arts uniform"
        },
        "和服": {
            "おまかせ": "",
            "着物": "kimono",
            "浴衣": "yukata",
            "振袖": "furisode",
            "巫女服": "miko outfit, shrine maiden",
            "袴": "hakama",
            "紋付袴": "montsuki hakama, formal male kimono",
            "羽織": "haori jacket",
            "甚平": "jinbei, japanese casual wear"
        },
        "作業着/職業服": {
            "おまかせ": "",
            "白衣": "white lab coat, doctor coat",
            "作業着": "work overalls, coveralls",
            "シェフコート": "chef coat, chef uniform",
            "消防服": "firefighter uniform",
            "建設作業員": "construction worker outfit, hard hat"
        }
    },
    "色": {
        "おまかせ": "",
        "黒": "black",
        "白": "white",
        "紺": "navy blue",
        "赤": "red",
        "ピンク": "pink",
        "青": "blue",
        "水色": "light blue",
        "緑": "green",
        "黄": "yellow",
        "オレンジ": "orange",
        "紫": "purple",
        "ベージュ": "beige",
        "グレー": "gray",
        "ゴールド": "gold",
        "シルバー": "silver"
    },
    "柄": {
        "おまかせ": "",
        "無地": "solid color, plain",
        "ストライプ": "striped",
        "チェック": "checkered, plaid",
        "花柄": "floral pattern",
        "ドット": "polka dot",
        "ボーダー": "horizontal stripes",
        "トロピカル": "tropical pattern, hibiscus",
        "レース": "lace",
        "迷彩": "camouflage",
        "アニマル柄": "animal print, leopard"
    },
    "スタイル": {
        "おまかせ": "",
        "大人っぽい": "mature, sophisticated",
        "可愛い": "cute, kawaii",
        "セクシー": "sexy, alluring",
        "クール": "cool, stylish",
        "清楚": "elegant, modest",
        "スポーティ": "sporty, athletic",
        "ゴージャス": "gorgeous, glamorous",
        "ワイルド": "wild, rugged",
        "知的": "intellectual, smart",
        "ダンディ": "dandy, gentlemanly",
        "カジュアル": "casual, relaxed"
    }
}

class MangaPromptApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window configuration
        self.title("4コマ漫画プロンプト作成ツール (API対応版)")
        self.geometry("1800x1000")

        # Layout configuration - Three column layout
        self.grid_columnconfigure(0, weight=1, minsize=400)  # Left column (basic info)
        self.grid_columnconfigure(1, weight=2, minsize=500)  # Center column (panels)
        self.grid_columnconfigure(2, weight=1, minsize=400)  # Right column (YAML + manga preview)
        self.grid_rowconfigure(0, weight=1)  # Main content row expands

        # Load template
        self.template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "template.yaml")
        self.template_data = self.load_template()

        # Recent files history
        self.recent_files_path = os.path.join(os.path.dirname(__file__), "recent_files.json")
        self.recent_files = self.load_recent_files()

        # ========== LEFT COLUMN (Basic Info & Characters) ==========
        self.left_column = ctk.CTkFrame(self)
        self.left_column.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")
        self.left_column.grid_columnconfigure(0, weight=1)
        self.left_column.grid_rowconfigure(4, weight=1)  # Character area expands

        # --- Output Mode Selection (API/YAML) ---
        self.output_mode_frame = ctk.CTkFrame(self.left_column)
        self.output_mode_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        self.output_mode_frame.grid_columnconfigure(1, weight=1)

        # Output mode radio buttons
        ctk.CTkLabel(self.output_mode_frame, text="出力モード:", font=("Arial", 11, "bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.output_mode_var = tk.StringVar(value="yaml")
        self.output_mode_var.trace_add("write", self.on_output_mode_change)

        output_radio_frame = ctk.CTkFrame(self.output_mode_frame, fg_color="transparent")
        output_radio_frame.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        self.api_output_radio = ctk.CTkRadioButton(output_radio_frame, text="画像出力(API使用)", variable=self.output_mode_var, value="api")
        self.api_output_radio.pack(side="left", padx=(0, 15))

        self.yaml_output_radio = ctk.CTkRadioButton(output_radio_frame, text="YAML出力", variable=self.output_mode_var, value="yaml")
        self.yaml_output_radio.pack(side="left")

        # API Sub-mode selection
        ctk.CTkLabel(self.output_mode_frame, text="APIモード:").grid(row=1, column=0, padx=10, pady=5, sticky="w")

        api_submode_frame = ctk.CTkFrame(self.output_mode_frame, fg_color="transparent")
        api_submode_frame.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        self.api_submode_var = tk.StringVar(value="generate")
        self.api_submode_var.trace_add("write", self.on_api_submode_change)

        self.api_generate_radio = ctk.CTkRadioButton(api_submode_frame, text="漫画生成", variable=self.api_submode_var, value="generate", state="disabled")
        self.api_generate_radio.pack(side="left", padx=(0, 15))

        self.api_redraw_radio = ctk.CTkRadioButton(api_submode_frame, text="参考漫画清書", variable=self.api_submode_var, value="redraw", state="disabled")
        self.api_redraw_radio.pack(side="left")

        # API Key input
        ctk.CTkLabel(self.output_mode_frame, text="API Key:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.api_key_entry = ctk.CTkEntry(self.output_mode_frame, placeholder_text="Google AI API Key", show="*", state="disabled")
        self.api_key_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        # --- Basic Info Area ---
        self.basic_frame = ctk.CTkFrame(self.left_column)
        self.basic_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.basic_frame.grid_columnconfigure(1, weight=1)

        # Title
        ctk.CTkLabel(self.basic_frame, text="タイトル:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.title_entry = ctk.CTkEntry(self.basic_frame, placeholder_text="シネマティック4コマ")
        self.title_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # Author
        ctk.CTkLabel(self.basic_frame, text="作者名:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.author_entry = ctk.CTkEntry(self.basic_frame, placeholder_text="Unknown")
        self.author_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # --- Color Mode Selection ---
        self.color_mode_frame = ctk.CTkFrame(self.left_column)
        self.color_mode_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.color_mode_frame, text="カラーモード:", font=("Arial", 11, "bold")).pack(side="left", padx=(10, 10), pady=5)

        self.color_mode_var = tk.StringVar(value="fullcolor")

        self.fullcolor_radio = ctk.CTkRadioButton(self.color_mode_frame, text="フルカラー", variable=self.color_mode_var, value="fullcolor")
        self.fullcolor_radio.pack(side="left", padx=5, pady=5)

        self.monochrome_radio = ctk.CTkRadioButton(self.color_mode_frame, text="モノクロ", variable=self.color_mode_var, value="monochrome")
        self.monochrome_radio.pack(side="left", padx=5, pady=5)

        # --- Resolution Selection (for API mode) ---
        self.resolution_frame = ctk.CTkFrame(self.left_column)
        self.resolution_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.resolution_frame, text="画質:", font=("Arial", 11, "bold")).pack(side="left", padx=(10, 10), pady=5)

        self.resolution_var = tk.StringVar(value="2k")

        self.resolution_1k_radio = ctk.CTkRadioButton(self.resolution_frame, text="1K", variable=self.resolution_var, value="1k", state="disabled")
        self.resolution_1k_radio.pack(side="left", padx=5, pady=5)

        self.resolution_2k_radio = ctk.CTkRadioButton(self.resolution_frame, text="2K", variable=self.resolution_var, value="2k", state="disabled")
        self.resolution_2k_radio.pack(side="left", padx=5, pady=5)

        self.resolution_4k_radio = ctk.CTkRadioButton(self.resolution_frame, text="4K", variable=self.resolution_var, value="4k", state="disabled")
        self.resolution_4k_radio.pack(side="left", padx=5, pady=5)

        # --- Character Area ---
        self.char_frame = ctk.CTkFrame(self.left_column)
        self.char_frame.grid(row=4, column=0, padx=10, pady=5, sticky="nsew")
        self.char_frame.grid_columnconfigure(1, weight=1)

        # Number of characters selection
        self.char_count_frame = ctk.CTkFrame(self.char_frame, fg_color="transparent")
        self.char_count_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        ctk.CTkLabel(self.char_count_frame, text="登場人物:", font=("Arial", 12, "bold")).pack(side="left", padx=(0, 10))

        self.char_count_var = tk.StringVar(value="1")
        self.char_count_var.trace_add("write", self.on_char_count_change)

        self.one_char_radio = ctk.CTkRadioButton(self.char_count_frame, text="1人", variable=self.char_count_var, value="1")
        self.one_char_radio.pack(side="left", padx=10)

        self.two_char_radio = ctk.CTkRadioButton(self.char_count_frame, text="2人", variable=self.char_count_var, value="2")
        self.two_char_radio.pack(side="left", padx=10)

        # Character 1
        ctk.CTkLabel(self.char_frame, text="キャラ1:", font=("Arial", 11, "bold")).grid(row=1, column=0, padx=10, pady=2, sticky="w")

        self.char1_frame = ctk.CTkFrame(self.char_frame, fg_color="transparent")
        self.char1_frame.grid(row=1, column=1, padx=10, pady=2, sticky="ew")
        self.char1_frame.grid_columnconfigure(0, weight=1)

        self.char1_name_entry = ctk.CTkEntry(self.char1_frame, placeholder_text="キャラ1の名前", width=150)
        self.char1_name_entry.grid(row=0, column=0, sticky="w")

        self.image_attach_var1 = tk.StringVar(value="with_image")
        self.with_image_radio1 = ctk.CTkRadioButton(self.char1_frame, text="画像あり", variable=self.image_attach_var1, value="with_image")
        self.with_image_radio1.grid(row=0, column=1, padx=(15, 5))
        self.without_image_radio1 = ctk.CTkRadioButton(self.char1_frame, text="画像なし", variable=self.image_attach_var1, value="without_image")
        self.without_image_radio1.grid(row=0, column=2, padx=5)

        ctk.CTkLabel(self.char_frame, text="説明:").grid(row=2, column=0, padx=10, pady=2, sticky="nw")
        self.char1_description_textbox = ctk.CTkTextbox(self.char_frame, height=40)
        self.char1_description_textbox.grid(row=2, column=1, padx=10, pady=2, sticky="ew")
        self.char1_description_textbox.insert("1.0", "顔、髪型を記述（服装は下の服装設定で指定可能）")
        self.char1_description_textbox.bind("<FocusIn>", lambda e: self.clear_placeholder(self.char1_description_textbox, "顔、髪型を記述（服装は下の服装設定で指定可能）"))

        # Character 1 Outfit Builder
        self.char1_outfit_frame = ctk.CTkFrame(self.char_frame)
        self.char1_outfit_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self.char1_outfit_frame.grid_columnconfigure((1, 2, 3, 4, 5), weight=1)

        ctk.CTkLabel(self.char1_outfit_frame, text="服装設定:", font=("Arial", 11, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # Category dropdown
        ctk.CTkLabel(self.char1_outfit_frame, text="カテゴリ", font=("Arial", 10)).grid(row=0, column=1, padx=2, pady=2)
        self.char1_outfit_category = ctk.CTkOptionMenu(
            self.char1_outfit_frame,
            values=list(OUTFIT_DATA["カテゴリ"].keys()),
            width=90,
            command=lambda v: self.on_outfit_category_change(1)
        )
        self.char1_outfit_category.set("おまかせ")
        self.char1_outfit_category.grid(row=1, column=1, padx=2, pady=2)

        # Shape dropdown
        ctk.CTkLabel(self.char1_outfit_frame, text="形状", font=("Arial", 10)).grid(row=0, column=2, padx=2, pady=2)
        self.char1_outfit_shape = ctk.CTkOptionMenu(
            self.char1_outfit_frame, values=["おまかせ"], width=100,
            command=lambda v: self.update_outfit_preview(1)
        )
        self.char1_outfit_shape.set("おまかせ")
        self.char1_outfit_shape.grid(row=1, column=2, padx=2, pady=2)

        # Color dropdown
        ctk.CTkLabel(self.char1_outfit_frame, text="色", font=("Arial", 10)).grid(row=0, column=3, padx=2, pady=2)
        self.char1_outfit_color = ctk.CTkOptionMenu(
            self.char1_outfit_frame, values=list(OUTFIT_DATA["色"].keys()), width=80,
            command=lambda v: self.update_outfit_preview(1)
        )
        self.char1_outfit_color.set("おまかせ")
        self.char1_outfit_color.grid(row=1, column=3, padx=2, pady=2)

        # Pattern dropdown
        ctk.CTkLabel(self.char1_outfit_frame, text="柄", font=("Arial", 10)).grid(row=0, column=4, padx=2, pady=2)
        self.char1_outfit_pattern = ctk.CTkOptionMenu(
            self.char1_outfit_frame, values=list(OUTFIT_DATA["柄"].keys()), width=90,
            command=lambda v: self.update_outfit_preview(1)
        )
        self.char1_outfit_pattern.set("おまかせ")
        self.char1_outfit_pattern.grid(row=1, column=4, padx=2, pady=2)

        # Style dropdown
        ctk.CTkLabel(self.char1_outfit_frame, text="スタイル", font=("Arial", 10)).grid(row=0, column=5, padx=2, pady=2)
        self.char1_outfit_style = ctk.CTkOptionMenu(
            self.char1_outfit_frame, values=list(OUTFIT_DATA["スタイル"].keys()), width=90,
            command=lambda v: self.update_outfit_preview(1)
        )
        self.char1_outfit_style.set("おまかせ")
        self.char1_outfit_style.grid(row=1, column=5, padx=2, pady=2)

        # Preview label for outfit prompt
        self.char1_outfit_preview = ctk.CTkLabel(self.char1_outfit_frame, text="", font=("Arial", 9), text_color="gray", wraplength=500)
        self.char1_outfit_preview.grid(row=2, column=1, columnspan=5, padx=5, pady=2, sticky="w")

        # Character 1 Image Path (for API mode)
        self.char1_image_path_label = ctk.CTkLabel(self.char_frame, text="画像パス:")
        self.char1_image_path_label.grid(row=4, column=0, padx=10, pady=2, sticky="w")
        self.char1_image_path_frame = ctk.CTkFrame(self.char_frame, fg_color="transparent")
        self.char1_image_path_frame.grid(row=4, column=1, padx=10, pady=2, sticky="ew")
        self.char1_image_path_frame.grid_columnconfigure(0, weight=1)
        self.char1_image_path_entry = ctk.CTkEntry(self.char1_image_path_frame, placeholder_text="キャラクター画像のパス（API使用時のみ）", state="disabled")
        self.char1_image_path_entry.grid(row=0, column=0, sticky="ew")
        self.char1_image_path_browse = ctk.CTkButton(self.char1_image_path_frame, text="参照", width=50, state="disabled", command=lambda: self.browse_image_path(1))
        self.char1_image_path_browse.grid(row=0, column=1, padx=(5, 0))

        # Character 2 (initially hidden)
        self.char2_label = ctk.CTkLabel(self.char_frame, text="キャラ2:", font=("Arial", 11, "bold"))
        self.char2_label.grid(row=5, column=0, padx=10, pady=2, sticky="w")

        self.char2_frame = ctk.CTkFrame(self.char_frame, fg_color="transparent")
        self.char2_frame.grid(row=5, column=1, padx=10, pady=2, sticky="ew")
        self.char2_frame.grid_columnconfigure(0, weight=1)

        self.char2_name_entry = ctk.CTkEntry(self.char2_frame, placeholder_text="キャラ2の名前", width=150)
        self.char2_name_entry.grid(row=0, column=0, sticky="w")

        self.image_attach_var2 = tk.StringVar(value="with_image")
        self.with_image_radio2 = ctk.CTkRadioButton(self.char2_frame, text="画像あり", variable=self.image_attach_var2, value="with_image")
        self.with_image_radio2.grid(row=0, column=1, padx=(15, 5))
        self.without_image_radio2 = ctk.CTkRadioButton(self.char2_frame, text="画像なし", variable=self.image_attach_var2, value="without_image")
        self.without_image_radio2.grid(row=0, column=2, padx=5)

        self.char2_desc_label = ctk.CTkLabel(self.char_frame, text="説明:")
        self.char2_desc_label.grid(row=6, column=0, padx=10, pady=2, sticky="nw")
        self.char2_description_textbox = ctk.CTkTextbox(self.char_frame, height=40)
        self.char2_description_textbox.grid(row=6, column=1, padx=10, pady=2, sticky="ew")
        self.char2_description_textbox.insert("1.0", "顔、髪型を記述（服装は下の服装設定で指定可能）")
        self.char2_description_textbox.bind("<FocusIn>", lambda e: self.clear_placeholder(self.char2_description_textbox, "顔、髪型を記述（服装は下の服装設定で指定可能）"))

        # Character 2 Outfit Builder
        self.char2_outfit_frame = ctk.CTkFrame(self.char_frame)
        self.char2_outfit_frame.grid(row=7, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self.char2_outfit_frame.grid_columnconfigure((1, 2, 3, 4, 5), weight=1)

        ctk.CTkLabel(self.char2_outfit_frame, text="服装設定:", font=("Arial", 11, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # Category dropdown
        ctk.CTkLabel(self.char2_outfit_frame, text="カテゴリ", font=("Arial", 10)).grid(row=0, column=1, padx=2, pady=2)
        self.char2_outfit_category = ctk.CTkOptionMenu(
            self.char2_outfit_frame,
            values=list(OUTFIT_DATA["カテゴリ"].keys()),
            width=90,
            command=lambda v: self.on_outfit_category_change(2)
        )
        self.char2_outfit_category.set("おまかせ")
        self.char2_outfit_category.grid(row=1, column=1, padx=2, pady=2)

        # Shape dropdown
        ctk.CTkLabel(self.char2_outfit_frame, text="形状", font=("Arial", 10)).grid(row=0, column=2, padx=2, pady=2)
        self.char2_outfit_shape = ctk.CTkOptionMenu(
            self.char2_outfit_frame, values=["おまかせ"], width=100,
            command=lambda v: self.update_outfit_preview(2)
        )
        self.char2_outfit_shape.set("おまかせ")
        self.char2_outfit_shape.grid(row=1, column=2, padx=2, pady=2)

        # Color dropdown
        ctk.CTkLabel(self.char2_outfit_frame, text="色", font=("Arial", 10)).grid(row=0, column=3, padx=2, pady=2)
        self.char2_outfit_color = ctk.CTkOptionMenu(
            self.char2_outfit_frame, values=list(OUTFIT_DATA["色"].keys()), width=80,
            command=lambda v: self.update_outfit_preview(2)
        )
        self.char2_outfit_color.set("おまかせ")
        self.char2_outfit_color.grid(row=1, column=3, padx=2, pady=2)

        # Pattern dropdown
        ctk.CTkLabel(self.char2_outfit_frame, text="柄", font=("Arial", 10)).grid(row=0, column=4, padx=2, pady=2)
        self.char2_outfit_pattern = ctk.CTkOptionMenu(
            self.char2_outfit_frame, values=list(OUTFIT_DATA["柄"].keys()), width=90,
            command=lambda v: self.update_outfit_preview(2)
        )
        self.char2_outfit_pattern.set("おまかせ")
        self.char2_outfit_pattern.grid(row=1, column=4, padx=2, pady=2)

        # Style dropdown
        ctk.CTkLabel(self.char2_outfit_frame, text="スタイル", font=("Arial", 10)).grid(row=0, column=5, padx=2, pady=2)
        self.char2_outfit_style = ctk.CTkOptionMenu(
            self.char2_outfit_frame, values=list(OUTFIT_DATA["スタイル"].keys()), width=90,
            command=lambda v: self.update_outfit_preview(2)
        )
        self.char2_outfit_style.set("おまかせ")
        self.char2_outfit_style.grid(row=1, column=5, padx=2, pady=2)

        # Preview label for outfit prompt
        self.char2_outfit_preview = ctk.CTkLabel(self.char2_outfit_frame, text="", font=("Arial", 9), text_color="gray", wraplength=500)
        self.char2_outfit_preview.grid(row=2, column=1, columnspan=5, padx=5, pady=2, sticky="w")

        # Character 2 Image Path (for API mode)
        self.char2_image_path_label = ctk.CTkLabel(self.char_frame, text="画像パス:")
        self.char2_image_path_label.grid(row=8, column=0, padx=10, pady=2, sticky="w")
        self.char2_image_path_frame = ctk.CTkFrame(self.char_frame, fg_color="transparent")
        self.char2_image_path_frame.grid(row=8, column=1, padx=10, pady=2, sticky="ew")
        self.char2_image_path_frame.grid_columnconfigure(0, weight=1)
        self.char2_image_path_entry = ctk.CTkEntry(self.char2_image_path_frame, placeholder_text="キャラクター画像のパス（API使用時のみ）", state="disabled")
        self.char2_image_path_entry.grid(row=0, column=0, sticky="ew")
        self.char2_image_path_browse = ctk.CTkButton(self.char2_image_path_frame, text="参照", width=50, state="disabled", command=lambda: self.browse_image_path(2))
        self.char2_image_path_browse.grid(row=0, column=1, padx=(5, 0))

        # Hide character 2 initially
        self.char2_widgets = [self.char2_label, self.char2_frame, self.char2_desc_label, self.char2_description_textbox, self.char2_outfit_frame, self.char2_image_path_label, self.char2_image_path_frame]
        self.toggle_char2_visibility(False)

        # --- Reference Manga Image (for API mode) ---
        self.ref_manga_frame = ctk.CTkFrame(self.char_frame)
        self.ref_manga_frame.grid(row=9, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="ew")
        self.ref_manga_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.ref_manga_frame, text="参考漫画画像:", font=("Arial", 11, "bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.ref_manga_path_frame = ctk.CTkFrame(self.ref_manga_frame, fg_color="transparent")
        self.ref_manga_path_frame.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.ref_manga_path_frame.grid_columnconfigure(0, weight=1)

        self.ref_manga_path_entry = ctk.CTkEntry(self.ref_manga_path_frame, placeholder_text="Geminiで生成した4コマ漫画画像のパス（API使用時のみ）", state="disabled")
        self.ref_manga_path_entry.grid(row=0, column=0, sticky="ew")
        self.ref_manga_path_browse = ctk.CTkButton(self.ref_manga_path_frame, text="参照", width=50, state="disabled", command=self.browse_ref_manga_path)
        self.ref_manga_path_browse.grid(row=0, column=1, padx=(5, 0))

        # ========== CENTER COLUMN (Panels) ==========
        self.center_column = ctk.CTkFrame(self)
        self.center_column.grid(row=0, column=1, padx=5, pady=10, sticky="nsew")
        self.center_column.grid_columnconfigure(0, weight=1)
        self.center_column.grid_rowconfigure(0, weight=1)  # Panels area expands

        # --- Panels Area ---
        self.panels_frame = ctk.CTkFrame(self.center_column)
        self.panels_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.panels_frame.grid_columnconfigure(0, weight=1)
        # Set equal weight for all 4 panel rows
        for row in range(4):
            self.panels_frame.grid_rowconfigure(row, weight=1)

        self.panel_prompts = []
        self.panel_speech1_speakers = []
        self.panel_speech1_positions = []
        self.panel_speech1_entries = []
        self.panel_speech2_speakers = []
        self.panel_speech2_positions = []
        self.panel_speech2_entries = []
        self.panel_speech2_widgets = []  # For hiding/showing
        self.panel_narrations = []
        self.panel_speech1_counters = []
        self.panel_speech2_counters = []
        self.panel_simultaneous_checkboxes = []  # 同時セリフ用チェックボックス
        self.panel_simultaneous_vars = []  # 同時セリフ用変数

        # Prompt clipboard for copy/paste between panels
        self.prompt_clipboard = ""

        panel_labels = ["1コマ目", "2コマ目", "3コマ目", "4コマ目（オチ）"]

        for i, label in enumerate(panel_labels):
            frame = ctk.CTkFrame(self.panels_frame)
            frame.grid(row=i, column=0, padx=5, pady=3, sticky="nsew")
            frame.grid_columnconfigure(1, weight=2)
            frame.grid_columnconfigure(2, weight=1)
            frame.grid_rowconfigure(1, weight=1)  # Allow prompt textbox to expand

            # Panel label with copy/paste buttons
            header_frame = ctk.CTkFrame(frame, fg_color="transparent")
            header_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=(5, 2), sticky="ew")

            ctk.CTkLabel(header_frame, text=f"【{label}】", font=("Arial", 14, "bold")).pack(side="left")

            # Copy prompt button
            copy_btn = ctk.CTkButton(header_frame, text="コピー", width=60, height=20, font=("Arial", 10),
                                     fg_color="gray", hover_color="darkgray",
                                     command=lambda idx=i: self.copy_prompt(idx))
            copy_btn.pack(side="left", padx=(10, 2))

            # Paste prompt button
            paste_btn = ctk.CTkButton(header_frame, text="ペースト", width=70, height=20, font=("Arial", 10),
                                      fg_color="gray", hover_color="darkgray",
                                      command=lambda idx=i: self.paste_prompt(idx))
            paste_btn.pack(side="left", padx=2)

            # Prompt
            ctk.CTkLabel(frame, text="プロンプト:").grid(row=1, column=0, padx=10, pady=2, sticky="nw")
            prompt_textbox = ctk.CTkTextbox(frame, height=50)
            prompt_textbox.grid(row=1, column=1, columnspan=2, padx=10, pady=2, sticky="nsew")
            self.panel_prompts.append(prompt_textbox)

            # Speech 1 row
            speech1_frame = ctk.CTkFrame(frame, fg_color="transparent")
            speech1_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=1, sticky="ew")
            speech1_frame.grid_columnconfigure(3, weight=1)

            ctk.CTkLabel(speech1_frame, text="セリフ1:").grid(row=0, column=0, padx=(0, 5), sticky="w")
            speech1_speaker = ctk.CTkOptionMenu(speech1_frame, values=["キャラ1"], width=80)
            speech1_speaker.grid(row=0, column=1, padx=2, sticky="w")
            self.panel_speech1_speakers.append(speech1_speaker)
            speech1_position = ctk.CTkOptionMenu(speech1_frame, values=["左", "右"], width=50)
            speech1_position.set("左")  # キャラ1は左がデフォルト
            speech1_position.grid(row=0, column=2, padx=2, sticky="w")
            self.panel_speech1_positions.append(speech1_position)
            speech1_entry = ctk.CTkEntry(speech1_frame, placeholder_text="セリフ内容")
            speech1_entry.grid(row=0, column=3, padx=5, sticky="ew")
            self.panel_speech1_entries.append(speech1_entry)
            speech1_counter = ctk.CTkLabel(speech1_frame, text=f"{MAX_SPEECH_LENGTH}", width=30, font=("Arial", 10))
            speech1_counter.grid(row=0, column=4, padx=2, sticky="w")
            self.panel_speech1_counters.append(speech1_counter)
            speech1_entry.bind("<KeyRelease>", lambda e, idx=i: self.update_speech_counter(idx, 1))

            # Speech 2 row (initially hidden)
            speech2_frame = ctk.CTkFrame(frame, fg_color="transparent")
            speech2_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=1, sticky="ew")
            speech2_frame.grid_columnconfigure(3, weight=1)

            speech2_label = ctk.CTkLabel(speech2_frame, text="セリフ2:")
            speech2_label.grid(row=0, column=0, padx=(0, 5), sticky="w")
            speech2_speaker = ctk.CTkOptionMenu(speech2_frame, values=["キャラ2"], width=80)
            speech2_speaker.grid(row=0, column=1, padx=2, sticky="w")
            self.panel_speech2_speakers.append(speech2_speaker)
            speech2_position = ctk.CTkOptionMenu(speech2_frame, values=["左", "右"], width=50)
            speech2_position.set("右")  # キャラ2は右がデフォルト
            speech2_position.grid(row=0, column=2, padx=2, sticky="w")
            self.panel_speech2_positions.append(speech2_position)
            speech2_entry = ctk.CTkEntry(speech2_frame, placeholder_text="セリフ内容")
            speech2_entry.grid(row=0, column=3, padx=5, sticky="ew")
            self.panel_speech2_entries.append(speech2_entry)
            speech2_counter = ctk.CTkLabel(speech2_frame, text=f"{MAX_SPEECH_LENGTH}", width=30, font=("Arial", 10))
            speech2_counter.grid(row=0, column=4, padx=2, sticky="w")
            self.panel_speech2_counters.append(speech2_counter)
            speech2_entry.bind("<KeyRelease>", lambda e, idx=i: self.update_speech_counter(idx, 2))

            self.panel_speech2_widgets.append(speech2_frame)

            # Simultaneous speech checkbox (同時セリフ)
            simultaneous_var = tk.BooleanVar(value=False)
            self.panel_simultaneous_vars.append(simultaneous_var)
            simultaneous_checkbox = ctk.CTkCheckBox(
                speech2_frame, text="同時セリフ", variable=simultaneous_var,
                command=lambda idx=i: self.on_simultaneous_change(idx),
                width=80
            )
            simultaneous_checkbox.grid(row=0, column=5, padx=(10, 0), sticky="w")
            self.panel_simultaneous_checkboxes.append(simultaneous_checkbox)

            # Narration and Clear button
            narration_frame = ctk.CTkFrame(frame, fg_color="transparent")
            narration_frame.grid(row=2, column=2, rowspan=2, padx=(5, 10), pady=1, sticky="nsew")
            narration_frame.grid_columnconfigure(0, weight=1)

            narration_entry = ctk.CTkEntry(narration_frame, placeholder_text="状況説明（ナレーション）")
            narration_entry.grid(row=0, column=0, sticky="ew")
            self.panel_narrations.append(narration_entry)

            panel_clear_btn = ctk.CTkButton(narration_frame, text="クリア", width=60, height=24, font=("Arial", 11), fg_color="gray", hover_color="darkgray", command=lambda idx=i: self.clear_panel(idx))
            panel_clear_btn.grid(row=1, column=0, pady=(2, 0), sticky="e")

        # Hide speech2 rows initially
        for widget in self.panel_speech2_widgets:
            widget.grid_remove()

        # --- Generate and Clear Buttons (Bottom of center column) ---
        self.button_frame = ctk.CTkFrame(self.center_column, fg_color="transparent")
        self.button_frame.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="ew")
        self.button_frame.grid_columnconfigure(0, weight=3)
        self.button_frame.grid_columnconfigure(1, weight=1)

        self.generate_btn = ctk.CTkButton(self.button_frame, text="Generate (YAML生成)", height=40, font=("Arial", 16, "bold"), command=self.generate_yaml)
        self.generate_btn.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self.clear_btn = ctk.CTkButton(self.button_frame, text="全てクリア", height=40, font=("Arial", 14), fg_color="gray", hover_color="darkgray", command=self.clear_all)
        self.clear_btn.grid(row=0, column=1, sticky="ew")

        # ========== RIGHT COLUMN (YAML Preview + Manga Preview) ==========
        self.right_column = ctk.CTkFrame(self)
        self.right_column.grid(row=0, column=2, padx=(5, 10), pady=10, sticky="nsew")
        self.right_column.grid_columnconfigure(0, weight=1)
        self.right_column.grid_rowconfigure(0, weight=0)  # YAML preview - fixed height
        self.right_column.grid_rowconfigure(1, weight=0)  # YAML action buttons
        self.right_column.grid_rowconfigure(2, weight=1)  # Manga preview - expands
        self.right_column.grid_rowconfigure(3, weight=0)  # Manga action buttons

        # --- YAML Preview Area (200px height) ---
        self.preview_frame = ctk.CTkFrame(self.right_column)
        self.preview_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="nsew")
        self.preview_frame.grid_columnconfigure(0, weight=1)
        self.preview_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.preview_frame, text="YAMLプレビュー", font=("Arial", 14, "bold")).grid(row=0, column=0, padx=10, pady=(5, 2), sticky="w")

        self.preview_textbox = ctk.CTkTextbox(self.preview_frame, height=180)
        self.preview_textbox.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        # --- YAML Action Buttons ---
        self.action_frame = ctk.CTkFrame(self.right_column)
        self.action_frame.grid(row=1, column=0, padx=10, pady=2, sticky="ew")

        self.load_btn = ctk.CTkButton(self.action_frame, text="読込", width=60, command=self.load_yaml)
        self.load_btn.pack(side="left", padx=2, pady=5)

        # Recent files dropdown
        self.recent_files_var = tk.StringVar(value="履歴")
        self.recent_files_menu = ctk.CTkOptionMenu(
            self.action_frame,
            values=["履歴なし"],
            variable=self.recent_files_var,
            command=self.on_recent_file_selected,
            width=60
        )
        self.recent_files_menu.pack(side="left", padx=2, pady=5)
        self.update_recent_files_menu()

        self.copy_btn = ctk.CTkButton(self.action_frame, text="コピー", width=60, state="disabled", command=self.copy_to_clipboard)
        self.copy_btn.pack(side="left", padx=2, pady=5)

        self.save_btn = ctk.CTkButton(self.action_frame, text="保存", width=60, state="disabled", command=self.save_yaml)
        self.save_btn.pack(side="left", padx=2, pady=5)

        self.generated_yaml = ""

        # --- Manga Preview Area (expands to fill remaining space) ---
        self.manga_preview_frame = ctk.CTkFrame(self.right_column)
        self.manga_preview_frame.grid(row=2, column=0, padx=10, pady=(10, 5), sticky="nsew")
        self.manga_preview_frame.grid_columnconfigure(0, weight=1)
        self.manga_preview_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.manga_preview_frame, text="漫画プレビュー", font=("Arial", 14, "bold")).grid(row=0, column=0, padx=10, pady=(5, 2), sticky="w")

        # Image display area (using a label to show image)
        self.manga_image_label = ctk.CTkLabel(self.manga_preview_frame, text="生成された漫画がここに表示されます\n\n(API出力モード時のみ)", font=("Arial", 12), text_color="gray")
        self.manga_image_label.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Store the generated image
        self.generated_manga_image = None
        self.manga_photo_image = None  # Keep reference to prevent garbage collection

        # --- Manga Action Buttons ---
        self.manga_action_frame = ctk.CTkFrame(self.right_column)
        self.manga_action_frame.grid(row=3, column=0, padx=10, pady=(2, 10), sticky="ew")

        self.save_manga_btn = ctk.CTkButton(self.manga_action_frame, text="画像を保存", state="disabled", command=self.save_manga_image)
        self.save_manga_btn.pack(side="left", expand=True, padx=5, pady=5)

    def load_template(self):
        """Load template.yaml file"""
        try:
            if os.path.exists(self.template_path):
                with open(self.template_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
        except Exception as e:
            print(f"Warning: Could not load template: {e}")
        return None

    def load_recent_files(self):
        """Load recent files history from JSON"""
        try:
            if os.path.exists(self.recent_files_path):
                with open(self.recent_files_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load recent files: {e}")
        return []

    def save_recent_files(self):
        """Save recent files history to JSON"""
        try:
            with open(self.recent_files_path, 'w', encoding='utf-8') as f:
                json.dump(self.recent_files, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Could not save recent files: {e}")

    def add_to_recent_files(self, filepath):
        """Add a file to recent files history"""
        # Remove if already exists
        if filepath in self.recent_files:
            self.recent_files.remove(filepath)
        # Add to front
        self.recent_files.insert(0, filepath)
        # Keep only MAX_RECENT_FILES
        self.recent_files = self.recent_files[:MAX_RECENT_FILES]
        self.save_recent_files()
        self.update_recent_files_menu()

    def update_recent_files_menu(self):
        """Update the recent files dropdown menu"""
        if self.recent_files:
            # Show only filenames in dropdown
            display_names = [os.path.basename(f) for f in self.recent_files]
            self.recent_files_menu.configure(values=display_names)
        else:
            self.recent_files_menu.configure(values=["履歴なし"])
        self.recent_files_var.set("履歴")

    def on_recent_file_selected(self, choice):
        """Handle selection from recent files dropdown"""
        if choice == "履歴なし" or choice == "履歴":
            return
        # Find full path from filename
        for filepath in self.recent_files:
            if os.path.basename(filepath) == choice:
                if os.path.exists(filepath):
                    self.load_yaml_file(filepath)
                else:
                    messagebox.showerror("エラー", f"ファイルが見つかりません: {filepath}")
                    # Remove from history
                    self.recent_files.remove(filepath)
                    self.save_recent_files()
                    self.update_recent_files_menu()
                break
        self.recent_files_var.set("履歴")

    def copy_prompt(self, panel_index):
        """Copy prompt from a panel to internal clipboard"""
        self.prompt_clipboard = self.panel_prompts[panel_index].get("1.0", tk.END).strip()

    def paste_prompt(self, panel_index):
        """Paste prompt from internal clipboard to a panel"""
        if self.prompt_clipboard:
            self.panel_prompts[panel_index].delete("1.0", tk.END)
            self.panel_prompts[panel_index].insert("1.0", self.prompt_clipboard)

    def update_speech_counter(self, panel_index, speech_num):
        """Update speech character counter and enforce limit"""
        if speech_num == 1:
            entry = self.panel_speech1_entries[panel_index]
            counter = self.panel_speech1_counters[panel_index]
        else:
            entry = self.panel_speech2_entries[panel_index]
            counter = self.panel_speech2_counters[panel_index]

        current_text = entry.get()
        current_len = len(current_text)

        # Enforce character limit
        if current_len > MAX_SPEECH_LENGTH:
            entry.delete(0, tk.END)
            entry.insert(0, current_text[:MAX_SPEECH_LENGTH])
            current_len = MAX_SPEECH_LENGTH

        # Update counter
        remaining = MAX_SPEECH_LENGTH - current_len
        counter.configure(text=f"{remaining}")

        # Change color when close to limit
        if remaining <= 3:
            counter.configure(text_color="red")
        elif remaining <= 5:
            counter.configure(text_color="orange")
        else:
            counter.configure(text_color=("gray50", "gray70"))

    def clear_placeholder(self, textbox, placeholder_text):
        """Clear placeholder text when textbox is focused"""
        current_text = textbox.get("1.0", tk.END).strip()
        if current_text == placeholder_text:
            textbox.delete("1.0", tk.END)

    def toggle_char2_visibility(self, visible):
        """Show or hide character 2 widgets"""
        for widget in self.char2_widgets:
            if visible:
                widget.grid()
            else:
                widget.grid_remove()

    def on_outfit_category_change(self, char_num):
        """Handle outfit category dropdown change - update shape options"""
        if char_num == 1:
            category = self.char1_outfit_category.get()
            shape_menu = self.char1_outfit_shape
        else:
            category = self.char2_outfit_category.get()
            shape_menu = self.char2_outfit_shape

        # Update shape options based on category
        if category == "おまかせ":
            shape_menu.configure(values=["おまかせ"])
            shape_menu.set("おまかせ")
        elif category in OUTFIT_DATA["形状"]:
            shapes = list(OUTFIT_DATA["形状"][category].keys())
            shape_menu.configure(values=shapes)
            shape_menu.set("おまかせ")
        else:
            shape_menu.configure(values=["おまかせ"])
            shape_menu.set("おまかせ")

        # Update preview
        self.update_outfit_preview(char_num)

    def update_outfit_preview(self, char_num):
        """Update the outfit prompt preview"""
        prompt = self.generate_outfit_prompt(char_num)
        if char_num == 1:
            self.char1_outfit_preview.configure(text=prompt if prompt else "(おまかせ)")
        else:
            self.char2_outfit_preview.configure(text=prompt if prompt else "(おまかせ)")

    def generate_outfit_prompt(self, char_num):
        """Generate English outfit prompt from selections"""
        if char_num == 1:
            category = self.char1_outfit_category.get()
            shape = self.char1_outfit_shape.get()
            color = self.char1_outfit_color.get()
            pattern = self.char1_outfit_pattern.get()
            style = self.char1_outfit_style.get()
        else:
            category = self.char2_outfit_category.get()
            shape = self.char2_outfit_shape.get()
            color = self.char2_outfit_color.get()
            pattern = self.char2_outfit_pattern.get()
            style = self.char2_outfit_style.get()

        # If category is おまかせ, return empty
        if category == "おまかせ":
            return ""

        parts = []

        # Color
        if color != "おまかせ" and color in OUTFIT_DATA["色"]:
            parts.append(OUTFIT_DATA["色"][color])

        # Pattern
        if pattern != "おまかせ" and pattern in OUTFIT_DATA["柄"]:
            parts.append(OUTFIT_DATA["柄"][pattern])

        # Shape (category-specific)
        if shape != "おまかせ" and category in OUTFIT_DATA["形状"] and shape in OUTFIT_DATA["形状"][category]:
            parts.append(OUTFIT_DATA["形状"][category][shape])
        elif category in OUTFIT_DATA["カテゴリ"]:
            # Use base category if no specific shape
            parts.append(OUTFIT_DATA["カテゴリ"][category])

        # Style
        if style != "おまかせ" and style in OUTFIT_DATA["スタイル"]:
            parts.append(OUTFIT_DATA["スタイル"][style])

        return ", ".join(parts) if parts else ""

    def on_simultaneous_change(self, panel_index):
        """Handle simultaneous speech checkbox change"""
        is_simultaneous = self.panel_simultaneous_vars[panel_index].get()
        if is_simultaneous:
            # Disable speech2 inputs
            self.panel_speech2_speakers[panel_index].configure(state="disabled")
            self.panel_speech2_positions[panel_index].configure(state="disabled")
            self.panel_speech2_entries[panel_index].configure(state="disabled")
            # Also disable speech1 speaker and position (will be centered)
            self.panel_speech1_speakers[panel_index].configure(state="disabled")
            self.panel_speech1_positions[panel_index].configure(state="disabled")
        else:
            # Enable speech2 inputs
            self.panel_speech2_speakers[panel_index].configure(state="normal")
            self.panel_speech2_positions[panel_index].configure(state="normal")
            self.panel_speech2_entries[panel_index].configure(state="normal")
            # Enable speech1 speaker and position
            self.panel_speech1_speakers[panel_index].configure(state="normal")
            self.panel_speech1_positions[panel_index].configure(state="normal")

    def clear_panel(self, panel_index):
        """Clear a single panel's input fields"""
        self.panel_prompts[panel_index].delete("1.0", tk.END)
        self.panel_speech1_entries[panel_index].delete(0, tk.END)
        self.panel_speech1_speakers[panel_index].set("キャラ1")
        self.panel_speech1_positions[panel_index].set("左")
        self.panel_speech2_entries[panel_index].delete(0, tk.END)
        if self.char_count_var.get() == "2":
            self.panel_speech2_speakers[panel_index].set("キャラ2")
            self.panel_speech2_positions[panel_index].set("右")
        self.panel_narrations[panel_index].delete(0, tk.END)
        # Reset simultaneous speech checkbox
        self.panel_simultaneous_vars[panel_index].set(False)
        self.on_simultaneous_change(panel_index)

    def on_output_mode_change(self, *args):
        """Handle output mode radio button change"""
        is_api_mode = self.output_mode_var.get() == "api"
        if is_api_mode:
            self.api_key_entry.configure(state="normal")
            # Enable API sub-mode selection
            self.api_generate_radio.configure(state="normal")
            self.api_redraw_radio.configure(state="normal")
            # Enable image path inputs
            self.char1_image_path_entry.configure(state="normal")
            self.char1_image_path_browse.configure(state="normal")
            self.char2_image_path_entry.configure(state="normal")
            self.char2_image_path_browse.configure(state="normal")
            # Enable reference manga image input
            self.ref_manga_path_entry.configure(state="normal")
            self.ref_manga_path_browse.configure(state="normal")
            # Enable resolution selection
            self.resolution_1k_radio.configure(state="normal")
            self.resolution_2k_radio.configure(state="normal")
            self.resolution_4k_radio.configure(state="normal")
        else:
            self.api_key_entry.configure(state="disabled")
            # Disable API sub-mode selection
            self.api_generate_radio.configure(state="disabled")
            self.api_redraw_radio.configure(state="disabled")
            # Disable image path inputs
            self.char1_image_path_entry.configure(state="disabled")
            self.char1_image_path_browse.configure(state="disabled")
            self.char2_image_path_entry.configure(state="disabled")
            self.char2_image_path_browse.configure(state="disabled")
            # Disable reference manga image input
            self.ref_manga_path_entry.configure(state="disabled")
            self.ref_manga_path_browse.configure(state="disabled")
            # Disable resolution selection
            self.resolution_1k_radio.configure(state="disabled")
            self.resolution_2k_radio.configure(state="disabled")
            self.resolution_4k_radio.configure(state="disabled")

        # Update generate button label
        self.update_generate_button_label()

    def on_api_submode_change(self, *args):
        """Handle API sub-mode radio button change"""
        self.update_generate_button_label()

    def update_generate_button_label(self):
        """Update generate button label based on current mode"""
        output_mode = self.output_mode_var.get()
        if output_mode == "yaml":
            self.generate_btn.configure(text="Generate (YAML生成)")
        elif output_mode == "api":
            api_submode = self.api_submode_var.get()
            if api_submode == "generate":
                self.generate_btn.configure(text="Generate (漫画生成)")
            else:  # redraw
                self.generate_btn.configure(text="Generate (清書)")

    def browse_image_path(self, char_num):
        """Open file dialog to select character image"""
        filename = filedialog.askopenfilename(
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.webp"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )
        if filename:
            if char_num == 1:
                self.char1_image_path_entry.delete(0, tk.END)
                self.char1_image_path_entry.insert(0, filename)
            else:
                self.char2_image_path_entry.delete(0, tk.END)
                self.char2_image_path_entry.insert(0, filename)

    def browse_ref_manga_path(self):
        """Open file dialog to select reference manga image"""
        filename = filedialog.askopenfilename(
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.webp"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.ref_manga_path_entry.delete(0, tk.END)
            self.ref_manga_path_entry.insert(0, filename)

    def on_char_count_change(self, *args):
        """Handle character count radio button change"""
        is_two_chars = self.char_count_var.get() == "2"
        self.toggle_char2_visibility(is_two_chars)

        # Update speaker dropdowns
        if is_two_chars:
            values = ["キャラ1", "キャラ2"]
            for speaker in self.panel_speech1_speakers:
                speaker.configure(values=values)
                speaker.set("キャラ1")
            for speaker in self.panel_speech2_speakers:
                speaker.configure(values=values)
                speaker.set("キャラ2")
            # Show speech2 rows
            for widget in self.panel_speech2_widgets:
                widget.grid()
        else:
            values = ["キャラ1"]
            for speaker in self.panel_speech1_speakers:
                speaker.configure(values=values)
                speaker.set("キャラ1")
            # Hide speech2 rows
            for widget in self.panel_speech2_widgets:
                widget.grid_remove()

    def clear_all(self):
        """Clear all input fields"""
        # Clear basic info
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)

        # Reset character count and clear character info
        self.char_count_var.set("1")
        self.char1_name_entry.delete(0, tk.END)
        self.char1_description_textbox.delete("1.0", tk.END)
        self.image_attach_var1.set("with_image")
        self.char2_name_entry.delete(0, tk.END)
        self.char2_description_textbox.delete("1.0", tk.END)
        self.image_attach_var2.set("with_image")

        # Reset outfit settings for character 1
        self.char1_outfit_category.set("おまかせ")
        self.char1_outfit_shape.configure(values=["おまかせ"])
        self.char1_outfit_shape.set("おまかせ")
        self.char1_outfit_color.set("おまかせ")
        self.char1_outfit_pattern.set("おまかせ")
        self.char1_outfit_style.set("おまかせ")
        self.char1_outfit_preview.configure(text="")

        # Reset outfit settings for character 2
        self.char2_outfit_category.set("おまかせ")
        self.char2_outfit_shape.configure(values=["おまかせ"])
        self.char2_outfit_shape.set("おまかせ")
        self.char2_outfit_color.set("おまかせ")
        self.char2_outfit_pattern.set("おまかせ")
        self.char2_outfit_style.set("おまかせ")
        self.char2_outfit_preview.configure(text="")

        # Clear panels
        for prompt in self.panel_prompts:
            prompt.delete("1.0", tk.END)
        for entry in self.panel_speech1_entries:
            entry.delete(0, tk.END)
        for entry in self.panel_speech2_entries:
            entry.delete(0, tk.END)
        for speaker in self.panel_speech1_speakers:
            speaker.set("キャラ1")
        for position in self.panel_speech1_positions:
            position.set("左")
        for speaker in self.panel_speech2_speakers:
            speaker.set("キャラ2")
        for position in self.panel_speech2_positions:
            position.set("右")
        for narration in self.panel_narrations:
            narration.delete(0, tk.END)

        # Reset simultaneous speech checkboxes
        for i, var in enumerate(self.panel_simultaneous_vars):
            var.set(False)
            self.on_simultaneous_change(i)

        # Reset color mode
        self.color_mode_var.set("fullcolor")

        # Clear preview
        self.preview_textbox.delete("1.0", tk.END)
        self.generated_yaml = ""

        # Disable action buttons
        self.copy_btn.configure(state="disabled")
        self.save_btn.configure(state="disabled")

    def generate_yaml(self):
        """Generate YAML from input values"""
        # Validate: at least one prompt required
        prompts = [p.get("1.0", tk.END).strip() for p in self.panel_prompts]
        if not any(prompts):
            messagebox.showerror("エラー", "少なくとも1つのプロンプトを入力してください。")
            return

        # Get values
        title = self.title_entry.get().strip() or "シネマティック4コマ"
        author = self.author_entry.get().strip() or "Unknown"
        is_two_chars = self.char_count_var.get() == "2"

        # Placeholder text to exclude
        placeholder_text = "顔、髪型を記述（服装は下の服装設定で指定可能）"

        # Get character 1 info
        char1_name = self.char1_name_entry.get().strip()
        char1_description_raw = self.char1_description_textbox.get("1.0", tk.END).strip()
        char1_description = "" if char1_description_raw == placeholder_text else char1_description_raw
        char1_outfit = self.generate_outfit_prompt(1)
        image_attach1 = self.image_attach_var1.get()

        # Get character 2 info (if 2 characters)
        char2_name = self.char2_name_entry.get().strip() if is_two_chars else ""
        char2_description_raw = self.char2_description_textbox.get("1.0", tk.END).strip() if is_two_chars else ""
        char2_description = "" if char2_description_raw == placeholder_text else char2_description_raw
        char2_outfit = self.generate_outfit_prompt(2) if is_two_chars else ""
        image_attach2 = self.image_attach_var2.get() if is_two_chars else ""

        # Get speeches with speakers and positions
        speech1_data = []
        for i in range(4):
            text = self.panel_speech1_entries[i].get().strip()
            speaker = self.panel_speech1_speakers[i].get()
            position = self.panel_speech1_positions[i].get()
            if text:
                speech1_data.append({"text": text, "speaker": speaker, "position": position})
            else:
                speech1_data.append(None)

        speech2_data = []
        if is_two_chars:
            for i in range(4):
                text = self.panel_speech2_entries[i].get().strip()
                speaker = self.panel_speech2_speakers[i].get()
                position = self.panel_speech2_positions[i].get()
                if text:
                    speech2_data.append({"text": text, "speaker": speaker, "position": position})
                else:
                    speech2_data.append(None)

        narrations = [n.get().strip() for n in self.panel_narrations]

        # Get color mode
        color_mode = self.color_mode_var.get()
        color_instruction = ""
        if color_mode == "monochrome":
            color_instruction = "モノクロ（白黒）で描画してください。"

        # Build YAML structure
        layout_instruction = "タイトルと作者名を画像上部に必ず表示してください。タイトルは左寄せで大きく、作者名は右寄せで小さく表示してください（「作:」などのラベルは不要、名前のみ表示）。4コマ漫画を縦1列に配置してください。横並びにせず、上から下へ1コマずつ縦に4つ並べてください。出力画像は縦長（9:16または2:5）で、4コマ漫画だけが画像全体を占めるようにしてください。"

        # Add character appearance instruction
        char_instruction = "各キャラクターの外見（顔、髪型、服装の色・デザイン・スタイル）は添付画像と説明を忠実に再現してください。複数キャラクターがいる場合は、それぞれの服装を明確に区別してください。"
        layout_instruction = layout_instruction + char_instruction

        if color_instruction:
            layout_instruction = color_instruction + layout_instruction

        yaml_data = {
            "title": title,
            "author": author,
            "width": 800,
            "height": 2000,
            "layout_instruction": layout_instruction
        }

        # Build character info
        def build_char_info(name, description, outfit_prompt, image_attach):
            char_info = {}
            if name:
                char_info["name"] = name

            # Combine description and outfit prompt
            full_description_parts = []
            if description:
                full_description_parts.append(description)
            if outfit_prompt:
                full_description_parts.append(f"服装: {outfit_prompt}")
            full_description = " ".join(full_description_parts)

            if image_attach == "with_image":
                char_info["reference"] = "添付画像を参照してください"
                if full_description:
                    char_info["description"] = full_description
            else:
                if full_description:
                    char_info["description"] = f"以下の説明に基づいてキャラクターを生成してください: {full_description}"
            return char_info if char_info else None

        if is_two_chars:
            characters = []
            char1_info = build_char_info(char1_name, char1_description, char1_outfit, image_attach1)
            char2_info = build_char_info(char2_name, char2_description, char2_outfit, image_attach2)
            if char1_info:
                characters.append(char1_info)
            if char2_info:
                characters.append(char2_info)
            if characters:
                yaml_data["characters"] = characters
        else:
            char1_info = build_char_info(char1_name, char1_description, char1_outfit, image_attach1)
            if char1_info:
                yaml_data["character"] = char1_info

        # Panel configurations with bubble positions (left, right, and center)
        panel_configs = [
            {"id": "panel_1", "box": [0, 0, 800, 450], "bubble_left": [50, 50, 250, 100], "bubble_right": [500, 50, 250, 100], "bubble_center": [275, 50, 250, 100], "narration_box": [50, 350, 300, 80]},
            {"id": "panel_2", "box": [0, 490, 800, 450], "bubble_left": [50, 550, 250, 100], "bubble_right": [500, 550, 250, 100], "bubble_center": [275, 550, 250, 100], "narration_box": [500, 850, 280, 80]},
            {"id": "panel_3", "box": [0, 980, 800, 450], "bubble_left": [50, 1050, 250, 100], "bubble_right": [500, 1050, 250, 100], "bubble_center": [275, 1050, 250, 100], "narration_box": [50, 1350, 300, 80]},
            {"id": "panel_4", "box": [0, 1470, 800, 450], "bubble_left": [50, 1550, 250, 100], "bubble_right": [500, 1550, 250, 100], "bubble_center": [275, 1550, 250, 100], "narration_box": [500, 1850, 280, 80]}
        ]

        # Get simultaneous speech settings
        simultaneous_flags = [var.get() for var in self.panel_simultaneous_vars]

        # Single character mode uses alternating positions
        single_char_positions = [
            [500, 50, 250, 100],   # Panel 1: right
            [50, 550, 250, 100],  # Panel 2: left
            [500, 1050, 250, 100], # Panel 3: right
            [50, 1550, 250, 100]  # Panel 4: left
        ]

        # Build panels
        panels = []
        for i, config in enumerate(panel_configs):
            panel = {
                "id": config["id"],
                "box": config["box"],
                "image": {
                    "prompt": prompts[i] if prompts[i] else f"ここに{i+1}コマ目の画像生成プロンプトを入力"
                }
            }

            # Add bubbles (speeches and/or narration)
            bubbles = []

            # Check if simultaneous speech mode
            is_simultaneous = simultaneous_flags[i] if i < len(simultaneous_flags) else False

            # Speech 1
            if speech1_data[i]:
                if is_two_chars:
                    if is_simultaneous:
                        # 同時セリフモード: 中央に配置、話者は「二人」
                        bubble = {
                            "text": speech1_data[i]["text"],
                            "box": config["bubble_center"],
                            "shape": "ellipse",
                            "speaker": "二人同時"
                        }
                    else:
                        # 2人モード: 位置選択に従う
                        position = speech1_data[i]["position"]
                        box = config["bubble_left"] if position == "左" else config["bubble_right"]
                        bubble = {
                            "text": speech1_data[i]["text"],
                            "box": box,
                            "shape": "ellipse",
                            "speaker": speech1_data[i]["speaker"]
                        }
                else:
                    # 1人モード: 臨機応変（交互配置）
                    bubble = {
                        "text": speech1_data[i]["text"],
                        "box": single_char_positions[i],
                        "shape": "ellipse"
                    }
                bubbles.append(bubble)

            # Speech 2 (only if 2 characters and not simultaneous)
            if is_two_chars and not is_simultaneous and i < len(speech2_data) and speech2_data[i]:
                position = speech2_data[i]["position"]
                box = config["bubble_left"] if position == "左" else config["bubble_right"]
                bubble = {
                    "text": speech2_data[i]["text"],
                    "box": box,
                    "shape": "ellipse",
                    "speaker": speech2_data[i]["speaker"]
                }
                bubbles.append(bubble)

            # Narration
            if narrations[i]:
                bubbles.append({
                    "text": narrations[i],
                    "box": config["narration_box"],
                    "shape": "rectangle"
                })

            if bubbles:
                panel["bubbles"] = bubbles

            panels.append(panel)

        yaml_data["pages"] = [{"index": 1, "panels": panels}]

        # Generate YAML string with instruction header
        yaml_content = yaml.dump(yaml_data, allow_unicode=True, default_flow_style=False, sort_keys=False)

        # Simple instruction that works with Gemini
        instruction = "以下のyamlの内容を忠実に再現してください。添付画像がある場合は添付画像もしっかり確認してください。\n\n"
        self.generated_yaml = instruction + yaml_content

        # Display in preview
        self.preview_textbox.delete("1.0", tk.END)
        self.preview_textbox.insert("1.0", self.generated_yaml)

        # Enable action buttons
        self.copy_btn.configure(state="normal")
        self.save_btn.configure(state="normal")

        # If API mode, start image generation
        if self.output_mode_var.get() == "api":
            if self.api_submode_var.get() == "generate":
                self.start_api_generation()
            elif self.api_submode_var.get() == "redraw":
                self.start_redraw_generation()

    def start_api_generation(self):
        """Start API image generation in a separate thread"""
        api_key = self.api_key_entry.get().strip()
        if not api_key:
            messagebox.showerror("エラー", "API Keyを入力してください。")
            return

        # Collect character images
        char_images = []
        char1_path = self.char1_image_path_entry.get().strip()
        if char1_path and os.path.exists(char1_path):
            char_images.append(char1_path)

        if self.char_count_var.get() == "2":
            char2_path = self.char2_image_path_entry.get().strip()
            if char2_path and os.path.exists(char2_path):
                char_images.append(char2_path)

        # Get resolution
        resolution = self.resolution_var.get().upper()

        # Update UI
        self.generate_btn.configure(state="disabled", text="生成中...")
        self.manga_image_label.configure(text="漫画を生成中...\nしばらくお待ちください", image=None)

        # Start thread
        thread = threading.Thread(
            target=self.generate_manga_api,
            args=(api_key, self.generated_yaml, char_images, resolution)
        )
        thread.start()

    def start_redraw_generation(self):
        """Start redraw generation in a separate thread"""
        api_key = self.api_key_entry.get().strip()
        if not api_key:
            messagebox.showerror("エラー", "API Keyを入力してください。")
            return

        # Check reference manga image
        ref_manga_path = self.ref_manga_path_entry.get().strip()
        if not ref_manga_path or not os.path.exists(ref_manga_path):
            messagebox.showerror("エラー", "参考漫画画像を指定してください。")
            return

        # Collect character images
        char_images = []
        char1_path = self.char1_image_path_entry.get().strip()
        if char1_path and os.path.exists(char1_path):
            char_images.append(char1_path)

        if self.char_count_var.get() == "2":
            char2_path = self.char2_image_path_entry.get().strip()
            if char2_path and os.path.exists(char2_path):
                char_images.append(char2_path)

        # Get resolution
        resolution = self.resolution_var.get().upper()

        # Update UI
        self.generate_btn.configure(state="disabled", text="清書中...")
        self.manga_image_label.configure(text="漫画を清書中...\nしばらくお待ちください", image=None)

        # Start thread (now includes YAML)
        thread = threading.Thread(
            target=self.redraw_manga_api,
            args=(api_key, self.generated_yaml, ref_manga_path, char_images, resolution)
        )
        thread.start()

    def generate_manga_api(self, api_key, yaml_prompt, char_images, resolution):
        """Generate manga using API (runs in separate thread)"""
        try:
            client = genai.Client(api_key=api_key)

            # Build contents
            contents = [yaml_prompt]

            # Add character reference images
            for img_path in char_images:
                try:
                    pil_img = Image.open(img_path)
                    contents.append(pil_img)
                except Exception as e:
                    print(f"Error loading image {img_path}: {e}")

            # Call API
            response = client.models.generate_content(
                model="gemini-3-pro-image-preview",
                contents=contents,
                config=types.GenerateContentConfig(
                    response_modalities=['TEXT', 'IMAGE']
                )
            )

            # Process response
            self.process_api_response(response)

        except Exception as e:
            err_msg = str(e)
            self.after(0, lambda: messagebox.showerror("APIエラー", f"エラーが発生しました:\n{err_msg}"))
            self.after(0, self.reset_generate_btn)

    def redraw_manga_api(self, api_key, yaml_prompt, ref_manga_path, char_images, resolution):
        """Redraw manga using API (runs in separate thread)"""
        try:
            client = genai.Client(api_key=api_key)

            # Build prompt for redraw (simple instruction + YAML)
            redraw_prompt = """添付の参考漫画画像を元に、高品質な4コマ漫画を新規に描き直してください。

- セリフ、タイトル、作者名は以下のYAMLの内容を正確に再現してください
- 構図やポーズは参考漫画画像を参考にしてください
- キャラクターの顔は添付のキャラクター参照画像を使用してください

""" + yaml_prompt

            contents = [redraw_prompt]

            # Add reference manga image
            try:
                ref_img = Image.open(ref_manga_path)
                contents.append(ref_img)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("エラー", f"参考漫画画像を読み込めません:\n{e}"))
                self.after(0, self.reset_generate_btn)
                return

            # Add character reference images
            for img_path in char_images:
                try:
                    pil_img = Image.open(img_path)
                    contents.append(pil_img)
                except Exception as e:
                    print(f"Error loading image {img_path}: {e}")

            # Call API
            response = client.models.generate_content(
                model="gemini-3-pro-image-preview",
                contents=contents,
                config=types.GenerateContentConfig(
                    response_modalities=['TEXT', 'IMAGE']
                )
            )

            # Process response
            self.process_api_response(response)

        except Exception as e:
            err_msg = str(e)
            self.after(0, lambda: messagebox.showerror("APIエラー", f"エラーが発生しました:\n{err_msg}"))
            self.after(0, self.reset_generate_btn)

    def process_api_response(self, response):
        """Process API response and extract image"""
        try:
            generated_img_data = None
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    generated_img_data = part.inline_data.data
                    break

            if generated_img_data:
                # Convert to PIL Image
                image_bytes = io.BytesIO(generated_img_data)
                self.generated_manga_image = Image.open(image_bytes)

                # Update UI in main thread
                self.after(0, self.update_manga_preview)
            else:
                self.after(0, lambda: messagebox.showerror("エラー", "APIから画像データが返されませんでした。"))
                self.after(0, self.reset_generate_btn)

        except Exception as e:
            err_msg = str(e)
            self.after(0, lambda: messagebox.showerror("エラー", f"レスポンス処理エラー:\n{err_msg}"))
            self.after(0, self.reset_generate_btn)

    def update_manga_preview(self):
        """Update manga preview with generated image"""
        if self.generated_manga_image:
            # Get the frame size for scaling
            frame_width = self.manga_preview_frame.winfo_width() - 40
            frame_height = self.manga_preview_frame.winfo_height() - 60

            # Use minimum reasonable size if frame not yet rendered
            if frame_width < 100:
                frame_width = 350
            if frame_height < 100:
                frame_height = 600

            # Resize for preview (keep aspect ratio)
            img_copy = self.generated_manga_image.copy()
            img_copy.thumbnail((frame_width, frame_height), Image.Resampling.LANCZOS)

            # Create CTkImage
            self.manga_photo_image = ctk.CTkImage(
                light_image=img_copy,
                dark_image=img_copy,
                size=img_copy.size
            )

            self.manga_image_label.configure(image=self.manga_photo_image, text="")
            self.save_manga_btn.configure(state="normal")

        self.reset_generate_btn()

    def reset_generate_btn(self):
        """Reset generate button state"""
        self.generate_btn.configure(state="normal")
        self.update_generate_button_label()

    def copy_to_clipboard(self):
        """Copy generated YAML to clipboard"""
        if self.generated_yaml:
            try:
                pyperclip.copy(self.generated_yaml)
                messagebox.showinfo("成功", "YAMLをクリップボードにコピーしました。")
            except Exception as e:
                messagebox.showerror("エラー", f"コピーに失敗しました: {e}")

    def save_yaml(self):
        """Save generated YAML to file"""
        if not self.generated_yaml:
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".yaml",
            filetypes=[("YAML file", "*.yaml"), ("YML file", "*.yml"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.generated_yaml)
                # Add to recent files
                self.add_to_recent_files(filename)
                messagebox.showinfo("成功", "YAMLファイルを保存しました。")
            except Exception as e:
                messagebox.showerror("エラー", f"保存に失敗しました: {e}")

    def save_manga_image(self):
        """Save generated manga image to file"""
        if not self.generated_manga_image:
            messagebox.showwarning("警告", "保存する画像がありません。")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG file", "*.png"), ("JPEG file", "*.jpg"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.generated_manga_image.save(filename)
                messagebox.showinfo("成功", "画像を保存しました。")
            except Exception as e:
                messagebox.showerror("エラー", f"保存に失敗しました: {e}")

    def load_yaml(self):
        """Open file dialog and load YAML file"""
        filename = filedialog.askopenfilename(
            filetypes=[("YAML file", "*.yaml"), ("YML file", "*.yml"), ("All files", "*.*")]
        )
        if filename:
            self.load_yaml_file(filename)

    def load_yaml_file(self, filename):
        """Load YAML file and populate input fields"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()

            # Remove instruction header if present
            if content.startswith("以下のyaml"):
                # Find the start of actual YAML content
                yaml_start = content.find("\n\n")
                if yaml_start != -1:
                    content = content[yaml_start + 2:]

            yaml_data = yaml.safe_load(content)
            if not yaml_data:
                messagebox.showerror("エラー", "YAMLファイルの解析に失敗しました。")
                return

            # Clear all fields first
            self.clear_all()

            # Restore basic info
            if "title" in yaml_data:
                self.title_entry.insert(0, yaml_data["title"])
            if "author" in yaml_data:
                self.author_entry.insert(0, yaml_data["author"])

            # Check color mode from layout_instruction
            layout_inst = yaml_data.get("layout_instruction", "")
            if "モノクロ" in layout_inst:
                self.color_mode_var.set("monochrome")

            # Restore character info
            if "characters" in yaml_data:
                # 2 characters mode
                self.char_count_var.set("2")
                characters = yaml_data["characters"]
                if len(characters) >= 1:
                    char1 = characters[0]
                    if "name" in char1:
                        self.char1_name_entry.insert(0, char1["name"])
                    if "reference" in char1:
                        self.image_attach_var1.set("with_image")
                    else:
                        self.image_attach_var1.set("without_image")
                    if "description" in char1:
                        desc = char1["description"]
                        if desc.startswith("以下の説明に基づいて"):
                            desc = desc.replace("以下の説明に基づいてキャラクターを生成してください: ", "")
                        self.char1_description_textbox.insert("1.0", desc)
                if len(characters) >= 2:
                    char2 = characters[1]
                    if "name" in char2:
                        self.char2_name_entry.insert(0, char2["name"])
                    if "reference" in char2:
                        self.image_attach_var2.set("with_image")
                    else:
                        self.image_attach_var2.set("without_image")
                    if "description" in char2:
                        desc = char2["description"]
                        if desc.startswith("以下の説明に基づいて"):
                            desc = desc.replace("以下の説明に基づいてキャラクターを生成してください: ", "")
                        self.char2_description_textbox.insert("1.0", desc)
            elif "character" in yaml_data:
                # 1 character mode
                self.char_count_var.set("1")
                char = yaml_data["character"]
                if "name" in char:
                    self.char1_name_entry.insert(0, char["name"])
                if "reference" in char:
                    self.image_attach_var1.set("with_image")
                else:
                    self.image_attach_var1.set("without_image")
                if "description" in char:
                    desc = char["description"]
                    if desc.startswith("以下の説明に基づいて"):
                        desc = desc.replace("以下の説明に基づいてキャラクターを生成してください: ", "")
                    self.char1_description_textbox.insert("1.0", desc)

            # Restore panels
            if "pages" in yaml_data and len(yaml_data["pages"]) > 0:
                panels = yaml_data["pages"][0].get("panels", [])
                is_two_chars = self.char_count_var.get() == "2"

                for i, panel in enumerate(panels):
                    if i >= 4:
                        break

                    # Restore prompt
                    if "image" in panel and "prompt" in panel["image"]:
                        prompt = panel["image"]["prompt"]
                        if not prompt.startswith("ここに"):
                            self.panel_prompts[i].insert("1.0", prompt)

                    # Restore bubbles
                    if "bubbles" in panel:
                        speech1_done = False
                        speech2_done = False
                        for bubble in panel["bubbles"]:
                            shape = bubble.get("shape", "")
                            text = bubble.get("text", "")
                            speaker = bubble.get("speaker", "キャラ1")
                            box = bubble.get("box", [0, 0, 0, 0])

                            if shape == "rectangle":
                                # Narration
                                self.panel_narrations[i].delete(0, tk.END)
                                self.panel_narrations[i].insert(0, text)
                            elif shape == "ellipse":
                                # Speech bubble
                                # Determine position from box x coordinate
                                position = "左" if box[0] < 300 else "右"

                                if not speech1_done:
                                    self.panel_speech1_entries[i].insert(0, text)
                                    if is_two_chars:
                                        self.panel_speech1_speakers[i].set(speaker)
                                        self.panel_speech1_positions[i].set(position)
                                    speech1_done = True
                                elif not speech2_done and is_two_chars:
                                    self.panel_speech2_entries[i].insert(0, text)
                                    self.panel_speech2_speakers[i].set(speaker)
                                    self.panel_speech2_positions[i].set(position)
                                    speech2_done = True

            # Display loaded content in preview
            self.preview_textbox.delete("1.0", tk.END)
            self.preview_textbox.insert("1.0", f"読み込み完了: {filename}\n\n内容を編集してGenerateボタンを押してください。")

            # Add to recent files
            self.add_to_recent_files(filename)

            messagebox.showinfo("成功", "YAMLファイルを読み込みました。")

        except Exception as e:
            messagebox.showerror("エラー", f"読み込みに失敗しました: {e}")


if __name__ == "__main__":
    app = MangaPromptApp()
    app.mainloop()
