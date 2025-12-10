# -*- coding: utf-8 -*-
"""
ファイル操作ロジック
YAML読み書き、履歴管理、テンプレート読み込み
"""

import os
import json
import yaml

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import (
    MAX_RECENT_FILES, MAX_CHARACTERS,
    COLOR_MODES, DUOTONE_COLORS, OUTPUT_STYLES, TEXT_POSITIONS,
    ASPECT_RATIOS, OUTFIT_DATA
)


def load_template(template_path: str) -> dict:
    """
    テンプレートYAMLファイルを読み込み

    Args:
        template_path: テンプレートファイルのパス

    Returns:
        テンプレートデータの辞書、失敗時はNone
    """
    try:
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
    except Exception as e:
        print(f"Warning: Could not load template: {e}")
    return None


def load_recent_files(recent_files_path: str) -> list:
    """
    最近使用したファイルの履歴を読み込み

    Args:
        recent_files_path: 履歴ファイルのパス

    Returns:
        ファイルパスのリスト
    """
    try:
        if os.path.exists(recent_files_path):
            with open(recent_files_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load recent files: {e}")
    return []


def save_recent_files(recent_files_path: str, recent_files: list) -> bool:
    """
    最近使用したファイルの履歴を保存

    Args:
        recent_files_path: 履歴ファイルのパス
        recent_files: ファイルパスのリスト

    Returns:
        成功したかどうか
    """
    try:
        with open(recent_files_path, 'w', encoding='utf-8') as f:
            json.dump(recent_files, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Warning: Could not save recent files: {e}")
        return False


def add_to_recent_files(recent_files: list, filepath: str) -> list:
    """
    ファイルを履歴に追加

    Args:
        recent_files: 現在の履歴リスト
        filepath: 追加するファイルパス

    Returns:
        更新された履歴リスト
    """
    if filepath in recent_files:
        recent_files.remove(filepath)
    recent_files.insert(0, filepath)
    return recent_files[:MAX_RECENT_FILES]


def save_yaml_file(filepath: str, content: str) -> tuple:
    """
    YAMLファイルを保存

    Args:
        filepath: 保存先パス
        content: YAML内容

    Returns:
        (success: bool, error_message: str or None)
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, None
    except Exception as e:
        return False, str(e)


def load_yaml_file(filepath: str) -> tuple:
    """
    YAMLファイルを読み込んで解析

    Args:
        filepath: ファイルパス

    Returns:
        (success: bool, data: dict or None, raw_content: str, error_message: str or None)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Skip instruction header if present (Japanese or English)
        instruction_prefixes = [
            "以下の",
            "Generate ",
            "The YAML below",
        ]
        yaml_content = content
        for prefix in instruction_prefixes:
            if content.startswith(prefix):
                parts = content.split("\n\n", 1)
                if len(parts) > 1:
                    yaml_content = parts[1]
                break

        data = yaml.safe_load(yaml_content)
        if not data:
            return False, None, content, "YAMLファイルを解析できませんでした。"

        return True, data, content, None

    except Exception as e:
        return False, None, "", str(e)


def parse_outfit_from_prompt(outfit_prompt: str) -> dict:
    """
    英語の服装プロンプトから日本語の選択肢に逆変換

    Args:
        outfit_prompt: 英語の服装プロンプト文字列

    Returns:
        服装選択肢の辞書:
        {
            'category': str,
            'shape': str,
            'color': str,
            'pattern': str,
            'style': str
        }
    """
    result = {
        'category': 'おまかせ',
        'shape': 'おまかせ',
        'color': 'おまかせ',
        'pattern': 'おまかせ',
        'style': 'おまかせ'
    }

    if not outfit_prompt:
        return result

    prompt_lower = outfit_prompt.lower()

    # 色を検索
    for jp_name, en_name in OUTFIT_DATA["色"].items():
        if en_name and en_name.lower() in prompt_lower:
            result['color'] = jp_name
            break

    # 柄を検索
    for jp_name, en_name in OUTFIT_DATA["柄"].items():
        if en_name and en_name.lower() in prompt_lower:
            result['pattern'] = jp_name
            break

    # スタイルを検索
    for jp_name, en_name in OUTFIT_DATA["スタイル"].items():
        if en_name and en_name.lower() in prompt_lower:
            result['style'] = jp_name
            break

    # カテゴリと形状を検索（形状の方が具体的なので先にチェック）
    found_category = None
    found_shape = None

    for category, shapes in OUTFIT_DATA["形状"].items():
        for jp_shape, en_shape in shapes.items():
            if en_shape and en_shape.lower() in prompt_lower:
                found_category = category
                found_shape = jp_shape
                break
        if found_shape:
            break

    # 形状が見つからなかった場合はカテゴリのみ検索
    if not found_category:
        for jp_name, en_name in OUTFIT_DATA["カテゴリ"].items():
            if en_name and en_name.lower() in prompt_lower:
                found_category = jp_name
                break

    if found_category:
        result['category'] = found_category
    if found_shape:
        result['shape'] = found_shape

    return result


def extract_outfit_from_description(description: str) -> tuple:
    """
    キャラクター説明から服装部分を分離

    Args:
        description: キャラクター説明文字列

    Returns:
        (description_without_outfit: str, outfit_prompt: str)
        服装部分がない場合は (description, '')
    """
    if not description:
        return '', ''

    # 「outfit:」「服装:」または「服装：」で分割
    for separator in ['outfit: ', 'outfit:', '服装: ', '服装:', '服装： ', '服装：']:
        if separator in description:
            parts = description.split(separator, 1)
            desc_part = parts[0].strip()
            outfit_part = parts[1].strip() if len(parts) > 1 else ''
            return desc_part, outfit_part

    return description, ''


def parse_yaml_to_ui_data(data: dict) -> dict:
    """
    YAMLデータをUI用データに変換

    Args:
        data: 解析済みYAMLデータ

    Returns:
        UI設定用の辞書:
        {
            'title': str,
            'author': str,
            'color_mode': str,
            'duotone_color': str or None,
            'output_style': str,
            'characters': list,
            'scene_prompt': str,
            'speeches': list,
            'narrations': list
        }
    """
    ui_data = {
        'title': data.get('title', ''),
        'author': data.get('author', ''),
        'color_mode': 'フルカラー',
        'duotone_color': None,
        'output_style': 'おまかせ',
        'aspect_ratio': '1:1',
        'characters': [],
        'scene_prompt': '',
        'speeches': [],
        'narrations': []
    }

    # Parse color mode
    if 'color_mode' in data:
        color_mode_value = data['color_mode']
        if color_mode_value.startswith("duotone_"):
            ui_data['color_mode'] = '二色刷り'
            duotone_suffix = color_mode_value.replace("duotone_", "")
            for name, (_, suffix) in DUOTONE_COLORS.items():
                if suffix == duotone_suffix:
                    ui_data['duotone_color'] = name
                    break
        else:
            for name, (value, _) in COLOR_MODES.items():
                if value == color_mode_value:
                    ui_data['color_mode'] = name
                    break

    # Parse output style
    if 'output_style' in data:
        style_prompt = data['output_style']
        for name, prompt in OUTPUT_STYLES.items():
            if prompt == style_prompt:
                ui_data['output_style'] = name
                break

    # Parse aspect ratio
    if 'aspect_ratio' in data:
        aspect_ratio = data['aspect_ratio']
        if aspect_ratio in ASPECT_RATIOS.values():
            ui_data['aspect_ratio'] = aspect_ratio

    # Parse characters
    if 'characters' in data:
        for char in data['characters'][:MAX_CHARACTERS]:
            raw_description = char.get('description', '')

            # プレフィックスを除去（日本語・英語両対応）
            prefixes_to_remove = [
                '以下の説明に基づいてキャラクターを生成:',
                'generate character based on description:'
            ]
            for prefix in prefixes_to_remove:
                if raw_description.lower().startswith(prefix.lower()):
                    raw_description = raw_description[len(prefix):].strip()
                    break

            # 説明から服装部分を分離
            description, outfit_prompt = extract_outfit_from_description(raw_description)

            # 服装プロンプトをUI選択肢に変換
            outfit = parse_outfit_from_prompt(outfit_prompt)

            char_data = {
                'name': char.get('name', ''),
                'description': description,
                'has_reference': 'reference' in char,
                'outfit': outfit
            }
            ui_data['characters'].append(char_data)

    # Parse scene
    if 'scene' in data:
        scene = data['scene']
        ui_data['scene_prompt'] = scene.get('prompt', '')

        # Parse speeches
        if 'speeches' in scene:
            for speech in scene['speeches']:
                ui_data['speeches'].append({
                    'character': speech.get('character', ''),
                    'content': speech.get('content', ''),
                    'position': '左' if speech.get('position', 'left') == 'left' else '右'
                })

        # Parse narrations
        if 'texts' in scene:
            for text in scene['texts'][:3]:
                pos_value = text.get('position', 'top-left')
                pos_name = '左上'
                for name, val in TEXT_POSITIONS.items():
                    if val == pos_value:
                        pos_name = name
                        break
                ui_data['narrations'].append({
                    'content': text.get('content', ''),
                    'position': pos_name
                })

    return ui_data
