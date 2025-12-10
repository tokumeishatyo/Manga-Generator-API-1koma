# -*- coding: utf-8 -*-
"""
YAML生成ロジック
イラスト生成用YAMLの構築
"""

import yaml
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import (
    COLOR_MODES, DUOTONE_COLORS, OUTPUT_TYPES, OUTPUT_STYLES,
    TEXT_POSITIONS, DECORATIVE_TEXT_STYLES,
    CHARACTER_SHEET_PROMPTS, CHARACTER_SHEET_DEFAULT_SCENES, BACKGROUND_PROMPT
)


def build_characters_list(
    char_data: list,
    generate_outfit_func: callable
) -> list:
    """
    キャラクターリストを構築

    Args:
        char_data: キャラクターデータのリスト
            各要素は dict: {
                'enabled': bool,
                'name': str,
                'description': str,
                'image_attach': str ('with_image' or 'without_image'),
                'outfit': dict (category, shape, color, pattern, style)
            }
        generate_outfit_func: 服装プロンプト生成関数

    Returns:
        YAML用キャラクターリスト
    """
    characters = []

    for i, char in enumerate(char_data):
        if not char.get('enabled', False):
            continue

        char_name = char.get('name', '').strip() or f"キャラ{i+1}"
        description = char.get('description', '').strip()

        # 服装プロンプト生成
        outfit = char.get('outfit', {})
        outfit_prompt = generate_outfit_func(
            outfit.get('category', 'おまかせ'),
            outfit.get('shape', 'おまかせ'),
            outfit.get('color', 'おまかせ'),
            outfit.get('pattern', 'おまかせ'),
            outfit.get('style', 'おまかせ')
        )

        image_attach = char.get('image_attach', 'with_image')

        char_info = {"name": char_name}

        # Combine description and outfit
        full_description_parts = []
        if description:
            full_description_parts.append(description)
        if outfit_prompt:
            full_description_parts.append(f"outfit: {outfit_prompt}")
        full_description = " ".join(full_description_parts)

        if image_attach == "with_image":
            char_info["reference"] = "see attached image"
            if full_description:
                char_info["description"] = full_description
        else:
            if full_description:
                char_info["description"] = f"generate character based on description: {full_description}"

        characters.append(char_info)

    return characters


def build_speeches_list(speech_data: list, char_names: list) -> list:
    """
    セリフリストを構築

    Args:
        speech_data: セリフデータのリスト
            各要素は dict: {
                'enabled': bool,
                'text': str,
                'position': str ('左' or '右')
            }
        char_names: キャラクター名のリスト

    Returns:
        YAML用セリフリスト
    """
    speeches = []

    for i, speech in enumerate(speech_data):
        if not speech.get('enabled', False):
            continue

        speech_text = speech.get('text', '').strip()
        if speech_text:
            char_name = char_names[i] if i < len(char_names) else f"キャラ{i+1}"
            position = speech.get('position', '左')
            speeches.append({
                "character": char_name,
                "content": speech_text,
                "position": "left" if position == "左" else "right"
            })

    return speeches


def build_texts_list(narration_data: list) -> list:
    """
    テキスト（ナレーション）リストを構築

    Args:
        narration_data: ナレーションデータのリスト
            各要素は dict: {
                'content': str,
                'position': str (日本語位置名)
            }

    Returns:
        YAML用テキストリスト
    """
    texts = []

    for narration in narration_data:
        content = narration.get('content', '').strip()
        if content:
            position_name = narration.get('position', '左上')
            texts.append({
                "content": content,
                "position": TEXT_POSITIONS.get(position_name, "top-left")
            })

    return texts


def build_layout_instruction(
    color_mode_prompt: str,
    output_style_prompt: str,
    output_type: str
) -> str:
    """
    レイアウト指示文を構築

    Args:
        color_mode_prompt: カラーモードプロンプト
        output_style_prompt: 出力スタイルプロンプト
        output_type: 出力タイプ

    Returns:
        レイアウト指示文字列
    """
    layout_parts = []

    if color_mode_prompt:
        layout_parts.append(f"color tone: {color_mode_prompt}")
    if output_style_prompt:
        layout_parts.append(f"style: {output_style_prompt}")

    if output_type == "background":
        layout_parts.append(BACKGROUND_PROMPT)
        layout_parts.append("Generate background only. Do not include people or characters.")
    elif output_type == "fullbody_sheet":
        sheet_prompt = CHARACTER_SHEET_PROMPTS.get(output_type, "")
        layout_parts.append(sheet_prompt)
        layout_parts.append("Faithfully reproduce character appearance from attached image and description.")
        layout_parts.append("Draw character only on plain white background.")
    elif output_type == "face_sheet":
        sheet_prompt = CHARACTER_SHEET_PROMPTS.get(output_type, "")
        layout_parts.append(sheet_prompt)
        layout_parts.append("Reference only facial features from attached image.")
        layout_parts.append("Draw face and neck only. Never draw body or full figure.")
        layout_parts.append("Use plain white background.")
    else:
        layout_parts.append("Generate single panel illustration.")
        layout_parts.append("Faithfully reproduce each character's appearance from attached images and descriptions.")
        layout_parts.append("Display dialogue in speech bubbles.")

    return " ".join(layout_parts)


def get_color_mode_info(color_mode_name: str, duotone_color: str = None) -> tuple:
    """
    カラーモード情報を取得

    Args:
        color_mode_name: カラーモード名
        duotone_color: 二色刷りの色選択（二色刷り選択時のみ）

    Returns:
        (color_mode_value, color_mode_prompt) のタプル
    """
    color_mode_value, color_mode_prompt = COLOR_MODES.get(color_mode_name, ("fullcolor", ""))

    if color_mode_name == "二色刷り" and duotone_color:
        color_mode_prompt, duotone_value = DUOTONE_COLORS.get(duotone_color, ("", "red_black"))
        color_mode_value = f"duotone_{duotone_value}"

    return color_mode_value, color_mode_prompt


def generate_illustration_yaml(
    scene_prompt: str,
    title: str,
    author: str,
    color_mode_name: str,
    duotone_color: str,
    output_style_name: str,
    output_type_name: str,
    aspect_ratio: str,
    characters: list,
    speeches: list,
    texts: list
) -> tuple:
    """
    イラスト生成用YAMLを生成

    Args:
        scene_prompt: シーン説明
        title: タイトル
        author: 作者名
        color_mode_name: カラーモード名
        duotone_color: 二色刷りの色
        output_style_name: 出力スタイル名
        output_type_name: 出力タイプ名
        aspect_ratio: アスペクト比
        characters: キャラクターリスト
        speeches: セリフリスト
        texts: テキストリスト

    Returns:
        (yaml_string, instruction) のタプル
    """
    output_type = OUTPUT_TYPES.get(output_type_name, "illustration")
    is_character_sheet = output_type in ["fullbody_sheet", "face_sheet"]
    is_background = output_type == "background"

    # 三面図の場合、シーン説明が空ならデフォルト値を使用
    if is_character_sheet and not scene_prompt.strip():
        scene_prompt = CHARACTER_SHEET_DEFAULT_SCENES.get(output_type, "")

    # Get color mode info
    color_mode_value, color_mode_prompt = get_color_mode_info(color_mode_name, duotone_color)

    # Get output style prompt
    output_style_prompt = OUTPUT_STYLES.get(output_style_name, "")

    # Build layout instruction
    layout_instruction = build_layout_instruction(
        color_mode_prompt, output_style_prompt, output_type
    )

    # Build YAML structure
    yaml_data = {
        "color_mode": color_mode_value,
        "aspect_ratio": aspect_ratio,
        "output_type": output_type,
        "output_style": output_style_prompt if output_style_prompt else "auto",
        "scene": {
            "prompt": scene_prompt
        },
        "layout_instruction": layout_instruction
    }

    # Add characters only if not background mode
    if not is_background and characters:
        yaml_data["characters"] = characters

    # Add title/author only if specified
    if title:
        yaml_data["title"] = title
    if author:
        yaml_data["author"] = author

    if texts:
        yaml_data["scene"]["texts"] = texts
    if speeches:
        yaml_data["scene"]["speeches"] = speeches

    # Generate YAML string
    yaml_content = yaml.dump(yaml_data, allow_unicode=True, default_flow_style=False, sort_keys=False)

    # Set instruction based on output type
    if is_background:
        instruction = "Generate background image based on the YAML below. Draw background only, no people or characters.\n\n"
    elif is_character_sheet:
        if output_type == "fullbody_sheet":
            instruction = "Generate character full body reference sheet (front, side, back views) based on the YAML below. Reference attached images if available.\n\n"
        else:  # face_sheet
            instruction = "Generate character face reference sheet (front, 3/4, profile views) based on the YAML below. [IMPORTANT] Draw face and neck only, never include body or full figure. Reference only facial features from attached images even if they show full body.\n\n"
    else:
        instruction = "Generate single panel illustration faithfully based on the YAML below. Reference attached images if available.\n\n"

    return instruction + yaml_content, instruction


def generate_decorative_yaml(decorative_data: list) -> tuple:
    """
    装飾テキスト用YAMLを生成

    Args:
        decorative_data: 装飾テキストデータのリスト
            各要素は dict: {
                'content': str,
                'position': str (日本語位置名),
                'style': str (日本語スタイル名)
            }

    Returns:
        (yaml_string, instruction) のタプル、またはエラー時は (None, error_message)
    """
    decorative_texts = []

    for item in decorative_data:
        content = item.get('content', '').strip()
        if content:
            position_name = item.get('position', '中央')
            style_name = item.get('style', 'タイトル')
            decorative_texts.append({
                "content": content,
                "position": TEXT_POSITIONS.get(position_name, "center"),
                "style": DECORATIVE_TEXT_STYLES.get(style_name, "title")
            })

    if not decorative_texts:
        return None, "少なくとも1つの装飾テキストを入力してください。"

    yaml_data = {
        "output_type": "decorative_text",
        "decorative_texts": decorative_texts
    }

    yaml_content = yaml.dump(yaml_data, allow_unicode=True, default_flow_style=False, sort_keys=False)
    instruction = "The YAML below defines decorative text. Used for post-processing image composition.\n\n"

    return instruction + yaml_content, instruction
