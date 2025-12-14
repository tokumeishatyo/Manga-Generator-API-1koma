# -*- coding: utf-8 -*-
"""
角度・ズーム変更ウィンドウ（Step5）
正面ポーズ画像を基に、角度とズームを変更する
- 入力: 正面ポーズ画像 + 衣装三面図
- 出力: 指定角度・ズームのキャラクター画像
"""

import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog
from typing import Callable, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.base_settings_window import BaseSettingsWindow


# 角度設定
VIEW_ANGLES = {
    "正面": {
        "prompt": "Front view, facing camera directly",
        "description": "正面から見た状態"
    },
    "←左向き": {
        "prompt": "Left side view, profile facing left",
        "description": "左を向いた状態（横顔）"
    },
    "→右向き": {
        "prompt": "Right side view, profile facing right",
        "description": "右を向いた状態（横顔）"
    },
    "↖左斜め前": {
        "prompt": "3/4 view facing left, turned 45 degrees to the left",
        "description": "左斜め45度から見た状態"
    },
    "↗右斜め前": {
        "prompt": "3/4 view facing right, turned 45 degrees to the right",
        "description": "右斜め45度から見た状態"
    },
    "背面": {
        "prompt": "Back view, rear view from behind",
        "description": "後ろから見た状態"
    },
    "↑上から見下ろす": {
        "prompt": "High angle view, looking down from above, bird's eye perspective",
        "description": "上から見下ろした状態（俯瞰）"
    },
    "↓下から見上げる": {
        "prompt": "Low angle view, looking up from below, dramatic upward perspective",
        "description": "下から見上げた状態（煽り）"
    }
}

# ズーム設定
ZOOM_LEVELS = {
    "全身": {
        "prompt": "Full body shot, entire figure visible from head to toe",
        "description": "頭からつま先まで全身"
    },
    "上半身": {
        "prompt": "Upper body shot, waist up, from waist to head",
        "description": "腰から上"
    },
    "バストアップ": {
        "prompt": "Medium close up, chest and head visible, cutting off above the waist",
        "description": "胸から上"
    },
    "顔アップ": {
        "prompt": "Close up shot, face only, detailed facial features",
        "description": "顔のみ（詳細）"
    }
}


class AngleWindow(BaseSettingsWindow):
    """角度・ズーム変更ウィンドウ（Step5）"""

    def __init__(
        self,
        parent,
        callback: Optional[Callable] = None,
        initial_data: Optional[dict] = None,
        front_pose_path: Optional[str] = None,   # Step4の出力画像パス
        outfit_sheet_path: Optional[str] = None  # Step3の出力画像パス
    ):
        """
        Args:
            parent: 親ウィンドウ
            callback: 設定完了時のコールバック
            initial_data: 初期データ（編集時）
            front_pose_path: Step4で生成した正面ポーズ画像のパス
            outfit_sheet_path: Step3で生成した衣装三面図のパス
        """
        self.initial_data = initial_data or {}
        self.front_pose_path = front_pose_path
        self.outfit_sheet_path = outfit_sheet_path
        super().__init__(
            parent,
            title="Step5: 角度・ズーム変更",
            width=700,
            height=650,
            callback=callback
        )

    def build_content(self):
        """コンテンツを構築"""
        # === 説明 ===
        desc_frame = ctk.CTkFrame(self.content_frame)
        desc_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(
            desc_frame,
            text="角度・ズーム変更について",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        desc_text = """正面ポーズ画像を基に、角度とズームを変更します。
衣装三面図を参照として使用することで、横・後ろの情報を補完します。"""

        ctk.CTkLabel(
            desc_frame,
            text=desc_text,
            font=("Arial", 11),
            justify="left"
        ).pack(anchor="w", padx=15, pady=(0, 10))

        # === 入力画像 ===
        input_frame = ctk.CTkFrame(self.content_frame)
        input_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        input_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            input_frame,
            text="入力画像",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 5), sticky="w")

        # 正面ポーズ画像
        ctk.CTkLabel(input_frame, text="正面ポーズ画像:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        pose_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        pose_frame.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        pose_frame.grid_columnconfigure(0, weight=1)

        self.front_pose_entry = ctk.CTkEntry(
            pose_frame,
            placeholder_text="Step4で生成した正面ポーズ画像"
        )
        self.front_pose_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        if self.front_pose_path:
            self.front_pose_entry.insert(0, self.front_pose_path)

        ctk.CTkButton(
            pose_frame,
            text="参照",
            width=60,
            command=self._browse_front_pose
        ).grid(row=0, column=1)

        # 衣装三面図
        ctk.CTkLabel(input_frame, text="衣装三面図:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        outfit_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        outfit_frame.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        outfit_frame.grid_columnconfigure(0, weight=1)

        self.outfit_sheet_entry = ctk.CTkEntry(
            outfit_frame,
            placeholder_text="Step3で生成した衣装三面図（横・後ろの参照用）"
        )
        self.outfit_sheet_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        if self.outfit_sheet_path:
            self.outfit_sheet_entry.insert(0, self.outfit_sheet_path)

        ctk.CTkButton(
            outfit_frame,
            text="参照",
            width=60,
            command=self._browse_outfit_sheet
        ).grid(row=0, column=1)

        # 三面図の説明
        ctk.CTkLabel(
            input_frame,
            text="※ 三面図は横・後ろの情報補完に使用。正面以外の角度で精度が向上します。",
            font=("Arial", 10),
            text_color="gray"
        ).grid(row=3, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="w")

        # === 角度設定 ===
        angle_frame = ctk.CTkFrame(self.content_frame)
        angle_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(
            angle_frame,
            text="角度（アングル）",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=4, padx=10, pady=(10, 5), sticky="w")

        self.angle_var = tk.StringVar(value="正面")

        # ラジオボタンを2行に配置
        row1_angles = ["正面", "←左向き", "→右向き", "背面"]
        row2_angles = ["↖左斜め前", "↗右斜め前", "↑上から見下ろす", "↓下から見上げる"]

        for i, angle in enumerate(row1_angles):
            ctk.CTkRadioButton(
                angle_frame,
                text=angle,
                variable=self.angle_var,
                value=angle
            ).grid(row=1, column=i, padx=10, pady=5, sticky="w")

        for i, angle in enumerate(row2_angles):
            ctk.CTkRadioButton(
                angle_frame,
                text=angle,
                variable=self.angle_var,
                value=angle
            ).grid(row=2, column=i, padx=10, pady=5, sticky="w")

        # === ズーム設定 ===
        zoom_frame = ctk.CTkFrame(self.content_frame)
        zoom_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(
            zoom_frame,
            text="ズーム（フレーミング）",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=4, padx=10, pady=(10, 5), sticky="w")

        self.zoom_var = tk.StringVar(value="全身")

        for i, zoom in enumerate(ZOOM_LEVELS.keys()):
            ctk.CTkRadioButton(
                zoom_frame,
                text=zoom,
                variable=self.zoom_var,
                value=zoom
            ).grid(row=1, column=i, padx=10, pady=5, sticky="w")

        # ズーム説明
        ctk.CTkLabel(
            zoom_frame,
            text="※ 攻撃ポーズ + 顔アップ → 腕を含めるためバストアップ程度になります",
            font=("Arial", 10),
            text_color="gray"
        ).grid(row=2, column=0, columnspan=4, padx=10, pady=(0, 10), sticky="w")

        # === 背景設定 ===
        bg_frame = ctk.CTkFrame(self.content_frame)
        bg_frame.grid(row=4, column=0, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(
            bg_frame,
            text="背景設定",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        self.transparent_bg_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            bg_frame,
            text="背景を透過にする（合成用）",
            variable=self.transparent_bg_var
        ).grid(row=1, column=0, padx=10, pady=(5, 10), sticky="w")

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
        self.description_textbox.insert("1.0", "（任意）追加の指示")

    def _browse_front_pose(self):
        """正面ポーズ画像参照ダイアログ"""
        filename = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]
        )
        if filename:
            self.front_pose_entry.delete(0, tk.END)
            self.front_pose_entry.insert(0, filename)

    def _browse_outfit_sheet(self):
        """衣装三面図参照ダイアログ"""
        filename = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]
        )
        if filename:
            self.outfit_sheet_entry.delete(0, tk.END)
            self.outfit_sheet_entry.insert(0, filename)

    def collect_data(self) -> dict:
        """UIから設定データを収集"""
        desc = self.description_textbox.get("1.0", tk.END).strip()
        if desc == "（任意）追加の指示":
            desc = ""

        angle = self.angle_var.get()
        zoom = self.zoom_var.get()

        return {
            'step_type': 'step5_angle',
            'front_pose_path': self.front_pose_entry.get().strip(),
            'outfit_sheet_path': self.outfit_sheet_entry.get().strip(),
            'angle': angle,
            'angle_info': VIEW_ANGLES.get(angle, {}),
            'zoom': zoom,
            'zoom_info': ZOOM_LEVELS.get(zoom, {}),
            'transparent_bg': self.transparent_bg_var.get(),
            'additional_description': desc
        }

    def validate(self) -> tuple[bool, str]:
        """入力検証"""
        front_pose = self.front_pose_entry.get().strip()
        if not front_pose:
            return False, "正面ポーズ画像を指定してください。\n（Step4の出力画像を選択）"

        # 正面以外の角度で三面図がない場合は警告
        angle = self.angle_var.get()
        outfit_sheet = self.outfit_sheet_entry.get().strip()
        if angle != "正面" and not outfit_sheet:
            return False, f"角度「{angle}」を選択していますが、衣装三面図が指定されていません。\n横・後ろの情報補完のため、三面図の指定を推奨します。"

        return True, ""
