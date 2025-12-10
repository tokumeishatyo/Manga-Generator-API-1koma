# -*- coding: utf-8 -*-
"""
キャラクター関連ロジック
服装プロンプト生成など
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import OUTFIT_DATA


def generate_outfit_prompt(category: str, shape: str, color: str, pattern: str, style: str) -> str:
    """
    服装選択から英語プロンプトを生成

    Args:
        category: カテゴリ選択値
        shape: 形状選択値
        color: 色選択値
        pattern: 柄選択値
        style: スタイル選択値

    Returns:
        英語の服装プロンプト文字列
    """
    if category == "おまかせ":
        return ""

    parts = []

    # Color
    if color != "おまかせ" and color in OUTFIT_DATA["色"]:
        parts.append(OUTFIT_DATA["色"][color])

    # Pattern
    if pattern != "おまかせ" and pattern in OUTFIT_DATA["柄"]:
        parts.append(OUTFIT_DATA["柄"][pattern])

    # Shape
    if shape != "おまかせ" and category in OUTFIT_DATA["形状"] and shape in OUTFIT_DATA["形状"][category]:
        parts.append(OUTFIT_DATA["形状"][category][shape])
    elif category in OUTFIT_DATA["カテゴリ"]:
        parts.append(OUTFIT_DATA["カテゴリ"][category])

    # Style
    if style != "おまかせ" and style in OUTFIT_DATA["スタイル"]:
        parts.append(OUTFIT_DATA["スタイル"][style])

    return ", ".join(parts) if parts else ""


def get_shape_options(category: str) -> list:
    """
    カテゴリに対応する形状オプションのリストを取得

    Args:
        category: カテゴリ選択値

    Returns:
        形状オプションのリスト
    """
    if category == "おまかせ":
        return ["おまかせ"]
    elif category in OUTFIT_DATA["形状"]:
        return list(OUTFIT_DATA["形状"][category].keys())
    else:
        return ["おまかせ"]
