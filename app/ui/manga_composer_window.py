# -*- coding: utf-8 -*-
"""
漫画ページコンポーザーウィンドウ
生成した画像を組み合わせて漫画ページを作成
"""

import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import Optional, Callable
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os


# テンプレート定義
TEMPLATES = {
    "4コマ（16:9縦並び）": {
        "cols": 1,
        "rows": 4,
        "panel_ratio": (16, 9),  # 各コマのアスペクト比
        "description": "各コマ16:9を縦に4枚並べ"
    },
    "8コマ（4:3 2列）": {
        "cols": 2,
        "rows": 4,
        "panel_ratio": (4, 3),  # 各コマのアスペクト比
        "description": "4:3を縦4枚×2列"
    }
}

# 出力サイズ（Web向け）
OUTPUT_WIDTHS = {
    "標準（720px）": 720,
    "高解像度（1080px）": 1080,
    "大（1440px）": 1440
}

# 吹き出しスタイル
BUBBLE_STYLES = {
    "丸（通常）": "oval",
    "角丸四角": "rounded_rect",
    "ギザギザ（叫び）": "burst",
    "思考（雲）": "cloud"
}


class MangaComposerWindow(ctk.CTkToplevel):
    """漫画ページコンポーザーウィンドウ"""

    def __init__(self, parent, callback: Optional[Callable] = None):
        super().__init__(parent)
        self.parent = parent
        self.callback = callback

        # ウィンドウ設定
        self.title("漫画ページコンポーザー")
        self.geometry("1200x800")
        self.transient(parent)

        # データ
        self.panel_images = {}  # {panel_index: PIL.Image}
        self.panel_bubbles = {}  # {panel_index: [{'text': str, 'position': (x,y), 'style': str}]}
        self.current_template = "4コマ（16:9縦並び）"
        self.composed_image = None

        # グリッド設定
        self.grid_columnconfigure(0, weight=1, minsize=400)
        self.grid_columnconfigure(1, weight=2, minsize=500)
        self.grid_rowconfigure(0, weight=1)

        # UI構築
        self._build_left_panel()
        self._build_right_panel()

        # フォーカス
        self.focus()

    def _build_left_panel(self):
        """左パネル（設定エリア）を構築"""
        left_frame = ctk.CTkFrame(self)
        left_frame.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(2, weight=1)

        # === テンプレート選択 ===
        template_frame = ctk.CTkFrame(left_frame)
        template_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        template_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            template_frame,
            text="テンプレート",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkLabel(template_frame, text="レイアウト:").grid(
            row=1, column=0, padx=10, pady=5, sticky="w"
        )
        self.template_menu = ctk.CTkOptionMenu(
            template_frame,
            values=list(TEMPLATES.keys()),
            width=200,
            command=self._on_template_change
        )
        self.template_menu.set(self.current_template)
        self.template_menu.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # テンプレート説明
        self.template_desc_label = ctk.CTkLabel(
            template_frame,
            text=TEMPLATES[self.current_template]["description"],
            font=("Arial", 11),
            text_color="gray"
        )
        self.template_desc_label.grid(row=2, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="w")

        # 出力サイズ
        ctk.CTkLabel(template_frame, text="出力幅:").grid(
            row=3, column=0, padx=10, pady=5, sticky="w"
        )
        self.output_width_menu = ctk.CTkOptionMenu(
            template_frame,
            values=list(OUTPUT_WIDTHS.keys()),
            width=200
        )
        self.output_width_menu.set("標準（720px）")
        self.output_width_menu.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        # === コマ画像選択エリア ===
        panels_frame = ctk.CTkFrame(left_frame)
        panels_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        panels_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            panels_frame,
            text="コマ画像",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        # スクロール可能なコマ選択エリア
        self.panels_scroll = ctk.CTkScrollableFrame(panels_frame, height=300)
        self.panels_scroll.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.panels_scroll.grid_columnconfigure(0, weight=1)

        self.panel_widgets = []
        self._create_panel_selectors()

        # === 吹き出し追加エリア ===
        bubble_frame = ctk.CTkFrame(left_frame)
        bubble_frame.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
        bubble_frame.grid_columnconfigure(1, weight=1)
        bubble_frame.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(
            bubble_frame,
            text="吹き出し追加",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkLabel(bubble_frame, text="対象コマ:").grid(
            row=1, column=0, padx=10, pady=5, sticky="w"
        )
        self.bubble_panel_menu = ctk.CTkOptionMenu(
            bubble_frame,
            values=["1", "2", "3", "4"],
            width=80
        )
        self.bubble_panel_menu.set("1")
        self.bubble_panel_menu.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(bubble_frame, text="スタイル:").grid(
            row=1, column=2, padx=10, pady=5, sticky="w"
        )
        self.bubble_style_menu = ctk.CTkOptionMenu(
            bubble_frame,
            values=list(BUBBLE_STYLES.keys()),
            width=120
        )
        self.bubble_style_menu.set("丸（通常）")
        self.bubble_style_menu.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(bubble_frame, text="セリフ:").grid(
            row=2, column=0, padx=10, pady=5, sticky="w"
        )
        self.bubble_text_entry = ctk.CTkEntry(
            bubble_frame,
            placeholder_text="吹き出し内のテキスト"
        )
        self.bubble_text_entry.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

        self.add_bubble_btn = ctk.CTkButton(
            bubble_frame,
            text="追加",
            width=60,
            command=self._add_bubble
        )
        self.add_bubble_btn.grid(row=2, column=3, padx=5, pady=5)

        # 吹き出しリスト
        ctk.CTkLabel(bubble_frame, text="追加済み:").grid(
            row=3, column=0, padx=10, pady=5, sticky="nw"
        )
        self.bubble_list = ctk.CTkTextbox(bubble_frame, height=80, state="disabled")
        self.bubble_list.grid(row=3, column=1, columnspan=3, padx=5, pady=5, sticky="nsew")

        # === 出力ボタン ===
        button_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        button_frame.grid(row=3, column=0, padx=5, pady=10, sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        self.preview_btn = ctk.CTkButton(
            button_frame,
            text="プレビュー更新",
            command=self._update_preview,
            height=40
        )
        self.preview_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.export_btn = ctk.CTkButton(
            button_frame,
            text="画像を出力",
            command=self._export_image,
            height=40,
            fg_color="green",
            hover_color="darkgreen"
        )
        self.export_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    def _build_right_panel(self):
        """右パネル（プレビューエリア）を構築"""
        right_frame = ctk.CTkFrame(self)
        right_frame.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="nsew")
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            right_frame,
            text="プレビュー",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        # プレビューエリア（スクロール対応）
        self.preview_scroll = ctk.CTkScrollableFrame(right_frame)
        self.preview_scroll.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.preview_scroll.grid_columnconfigure(0, weight=1)

        self.preview_label = ctk.CTkLabel(
            self.preview_scroll,
            text="画像を選択してプレビューを更新してください",
            font=("Arial", 12),
            text_color="gray"
        )
        self.preview_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    def _create_panel_selectors(self):
        """コマ選択UIを作成"""
        # 既存のウィジェットをクリア
        for widget in self.panel_widgets:
            for w in widget.values():
                if hasattr(w, 'destroy'):
                    w.destroy()
        self.panel_widgets = []

        template = TEMPLATES[self.current_template]
        num_panels = template["cols"] * template["rows"]

        for i in range(num_panels):
            panel_frame = ctk.CTkFrame(self.panels_scroll)
            panel_frame.grid(row=i, column=0, padx=5, pady=3, sticky="ew")
            panel_frame.grid_columnconfigure(1, weight=1)

            label = ctk.CTkLabel(panel_frame, text=f"コマ{i + 1}:", width=60)
            label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

            entry = ctk.CTkEntry(panel_frame, placeholder_text="画像ファイルパス")
            entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

            browse_btn = ctk.CTkButton(
                panel_frame,
                text="参照",
                width=60,
                command=lambda idx=i, e=entry: self._browse_panel_image(idx, e)
            )
            browse_btn.grid(row=0, column=2, padx=5, pady=5)

            clear_btn = ctk.CTkButton(
                panel_frame,
                text="×",
                width=30,
                fg_color="gray",
                hover_color="darkgray",
                command=lambda idx=i, e=entry: self._clear_panel_image(idx, e)
            )
            clear_btn.grid(row=0, column=3, padx=5, pady=5)

            self.panel_widgets.append({
                'frame': panel_frame,
                'entry': entry,
                'browse': browse_btn,
                'clear': clear_btn
            })

        # 吹き出し対象コマのドロップダウンを更新
        panel_options = [str(i + 1) for i in range(num_panels)]
        self.bubble_panel_menu.configure(values=panel_options)
        self.bubble_panel_menu.set("1")

    def _on_template_change(self, value):
        """テンプレート変更時"""
        self.current_template = value
        self.template_desc_label.configure(
            text=TEMPLATES[value]["description"]
        )
        # コマ選択UIを再構築
        self._create_panel_selectors()
        # 画像とバブルをクリア
        self.panel_images = {}
        self.panel_bubbles = {}
        self._update_bubble_list()
        # プレビューをクリア
        self.preview_label.configure(
            text="画像を選択してプレビューを更新してください",
            image=None
        )
        self.composed_image = None

    def _browse_panel_image(self, panel_index: int, entry: ctk.CTkEntry):
        """コマ画像を参照"""
        filename = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]
        )
        if filename:
            entry.delete(0, tk.END)
            entry.insert(0, filename)
            # 画像を読み込み
            try:
                img = Image.open(filename)
                self.panel_images[panel_index] = img
            except Exception as e:
                messagebox.showerror("エラー", f"画像の読み込みに失敗しました:\n{e}")

    def _clear_panel_image(self, panel_index: int, entry: ctk.CTkEntry):
        """コマ画像をクリア"""
        entry.delete(0, tk.END)
        if panel_index in self.panel_images:
            del self.panel_images[panel_index]

    def _add_bubble(self):
        """吹き出しを追加"""
        text = self.bubble_text_entry.get().strip()
        if not text:
            messagebox.showwarning("警告", "セリフを入力してください")
            return

        panel_idx = int(self.bubble_panel_menu.get()) - 1
        style = BUBBLE_STYLES[self.bubble_style_menu.get()]

        if panel_idx not in self.panel_bubbles:
            self.panel_bubbles[panel_idx] = []

        self.panel_bubbles[panel_idx].append({
            'text': text,
            'style': style,
            'position': (0.5, 0.2)  # デフォルト位置（コマ中央上部）
        })

        # 入力欄をクリア
        self.bubble_text_entry.delete(0, tk.END)

        # リスト更新
        self._update_bubble_list()

    def _update_bubble_list(self):
        """吹き出しリストを更新"""
        self.bubble_list.configure(state="normal")
        self.bubble_list.delete("1.0", tk.END)

        for panel_idx, bubbles in sorted(self.panel_bubbles.items()):
            for bubble in bubbles:
                self.bubble_list.insert(
                    tk.END,
                    f"コマ{panel_idx + 1}: {bubble['text'][:20]}...\n"
                    if len(bubble['text']) > 20
                    else f"コマ{panel_idx + 1}: {bubble['text']}\n"
                )

        self.bubble_list.configure(state="disabled")

    def _compose_image(self) -> Optional[Image.Image]:
        """画像を合成"""
        template = TEMPLATES[self.current_template]
        cols = template["cols"]
        rows = template["rows"]
        panel_ratio = template["panel_ratio"]

        output_width = OUTPUT_WIDTHS[self.output_width_menu.get()]

        # 各コマのサイズを計算
        panel_w = output_width // cols
        panel_h = int(panel_w * panel_ratio[1] / panel_ratio[0])

        # キャンバスサイズ
        canvas_w = output_width
        canvas_h = panel_h * rows

        # 白背景のキャンバスを作成
        canvas = Image.new("RGB", (canvas_w, canvas_h), "white")

        # 各コマを配置
        num_panels = cols * rows
        for i in range(num_panels):
            col = i % cols
            row = i // cols
            x = col * panel_w
            y = row * panel_h

            if i in self.panel_images:
                img = self.panel_images[i].copy()
                # コマサイズにフィット（アスペクト比を維持してクロップ）
                img = self._fit_image_to_panel(img, panel_w, panel_h)
                canvas.paste(img, (x, y))

                # 吹き出しを描画
                if i in self.panel_bubbles:
                    for bubble in self.panel_bubbles[i]:
                        self._draw_bubble(canvas, x, y, panel_w, panel_h, bubble)
            else:
                # 空のコマ（グレー）
                draw = ImageDraw.Draw(canvas)
                draw.rectangle([x, y, x + panel_w - 1, y + panel_h - 1], fill="#EEEEEE", outline="#CCCCCC", width=2)
                # コマ番号を表示
                try:
                    font = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", 24)
                except:
                    font = ImageFont.load_default()
                text = f"コマ{i + 1}"
                bbox = draw.textbbox((0, 0), text, font=font)
                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1]
                draw.text(
                    (x + panel_w // 2 - text_w // 2, y + panel_h // 2 - text_h // 2),
                    text,
                    fill="#999999",
                    font=font
                )

        # コマ枠を描画
        draw = ImageDraw.Draw(canvas)
        for i in range(num_panels):
            col = i % cols
            row = i // cols
            x = col * panel_w
            y = row * panel_h
            draw.rectangle([x, y, x + panel_w - 1, y + panel_h - 1], outline="black", width=2)

        return canvas

    def _fit_image_to_panel(self, img: Image.Image, panel_w: int, panel_h: int) -> Image.Image:
        """画像をコマサイズにフィット（アスペクト比維持、中央クロップ）"""
        img_w, img_h = img.size
        img_ratio = img_w / img_h
        panel_ratio = panel_w / panel_h

        if img_ratio > panel_ratio:
            # 画像が横長 → 上下に合わせて左右をクロップ
            new_h = img_h
            new_w = int(img_h * panel_ratio)
            left = (img_w - new_w) // 2
            img = img.crop((left, 0, left + new_w, new_h))
        else:
            # 画像が縦長 → 左右に合わせて上下をクロップ
            new_w = img_w
            new_h = int(img_w / panel_ratio)
            top = (img_h - new_h) // 2
            img = img.crop((0, top, new_w, top + new_h))

        # リサイズ
        img = img.resize((panel_w, panel_h), Image.Resampling.LANCZOS)
        return img

    def _draw_bubble(self, canvas: Image.Image, panel_x: int, panel_y: int,
                     panel_w: int, panel_h: int, bubble: dict):
        """吹き出しを描画"""
        draw = ImageDraw.Draw(canvas)
        text = bubble['text']
        style = bubble['style']
        pos = bubble['position']

        # フォント
        try:
            font = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", 16)
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
            except:
                font = ImageFont.load_default()

        # テキストサイズを計算
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        # 吹き出しのサイズとパディング
        padding = 10
        bubble_w = text_w + padding * 2
        bubble_h = text_h + padding * 2

        # 位置を計算（コマ内の相対位置）
        bubble_x = panel_x + int(pos[0] * panel_w) - bubble_w // 2
        bubble_y = panel_y + int(pos[1] * panel_h) - bubble_h // 2

        # コマ内に収まるように調整
        bubble_x = max(panel_x + 5, min(bubble_x, panel_x + panel_w - bubble_w - 5))
        bubble_y = max(panel_y + 5, min(bubble_y, panel_y + panel_h - bubble_h - 5))

        # 吹き出し形状を描画
        if style == "oval":
            draw.ellipse(
                [bubble_x, bubble_y, bubble_x + bubble_w, bubble_y + bubble_h],
                fill="white",
                outline="black",
                width=2
            )
        elif style == "rounded_rect":
            self._draw_rounded_rectangle(
                draw, bubble_x, bubble_y, bubble_w, bubble_h,
                radius=10, fill="white", outline="black", width=2
            )
        elif style == "burst":
            # ギザギザ（簡易版）
            draw.ellipse(
                [bubble_x, bubble_y, bubble_x + bubble_w, bubble_y + bubble_h],
                fill="white",
                outline="black",
                width=3
            )
        else:  # cloud
            draw.ellipse(
                [bubble_x, bubble_y, bubble_x + bubble_w, bubble_y + bubble_h],
                fill="white",
                outline="black",
                width=2
            )

        # テキストを描画
        draw.text(
            (bubble_x + padding, bubble_y + padding),
            text,
            fill="black",
            font=font
        )

    def _draw_rounded_rectangle(self, draw, x, y, w, h, radius, fill, outline, width):
        """角丸四角形を描画"""
        draw.rounded_rectangle(
            [x, y, x + w, y + h],
            radius=radius,
            fill=fill,
            outline=outline,
            width=width
        )

    def _update_preview(self):
        """プレビューを更新"""
        self.composed_image = self._compose_image()
        if self.composed_image:
            # プレビュー用にリサイズ
            preview = self.composed_image.copy()
            max_preview_width = 500
            if preview.width > max_preview_width:
                ratio = max_preview_width / preview.width
                new_size = (max_preview_width, int(preview.height * ratio))
                preview = preview.resize(new_size, Image.Resampling.LANCZOS)

            photo = ImageTk.PhotoImage(preview)
            self.preview_label.configure(image=photo, text="")
            self.preview_label.image = photo

    def _export_image(self):
        """画像を出力"""
        if not self.composed_image:
            self._update_preview()

        if not self.composed_image:
            messagebox.showwarning("警告", "出力する画像がありません")
            return

        filename = filedialog.asksaveasfilename(
            initialfile="manga_page",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        if filename:
            self.composed_image.save(filename)
            messagebox.showinfo("保存完了", f"画像を保存しました:\n{filename}")
