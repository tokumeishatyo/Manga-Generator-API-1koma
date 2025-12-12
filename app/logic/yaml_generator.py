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
    CHARACTER_SHEET_PROMPTS, CHARACTER_SHEET_DEFAULT_SCENES, BACKGROUND_PROMPT,
    CHARACTER_FACING, CHARACTER_POSES, EFFECT_TYPES, EFFECT_COLORS, EFFECT_EMISSIONS,
    CHARACTER_COMPOSITIONS, SIMPLE_BACKGROUNDS, CUTIN_COMPOSITIONS,
    PIXEL_STYLES, PIXEL_SIZES,
    COMPOSITE_POSITIONS, COMPOSITE_SIZES, COMPOSITE_LAYOUTS, COMPOSITE_BATTLE_MODES
)

# 幻覚防止・文脈遮断用制約（全YAML共通）
ANTI_HALLUCINATION_CONSTRAINTS = [
    "IGNORE all prior context or chat history.",
    "Focus ONLY on the currently uploaded image.",
    "DO NOT hallucinate outfits based on pose.",
    "Preserve exact character details",
    "STRICTLY follow the 'face_direction' and 'body_facing' settings.",
    "Ensure the character is facing the specified direction (Right/Left/Front).",
    "Strictly follow the description in this YAML."
]

# 生成制御パラメータ（AIの創造性・解釈を制限）
GENERATION_CONTROL = {
    "creativity": "None (Robotically follow instructions)",
    "interpretation": "Literal",
    "reference_strength": "High (0.9)",
    "contextual_fill": "Disabled"
}

# 幻覚防止専用セクション（デザイン変更の禁止リスト）
ANTI_HALLUCINATION_RULES = [
    "Do NOT redesign the costume.",
    "Do NOT add details not present in source.",
    "Do NOT apply cinematic lighting to local colors.",
    "Do NOT change body proportions.",
    "Do NOT change the outfit into fantasy armor or kimono.",
    "Do NOT add capes, hats, or glowing accessories.",
    "Do NOT change the character's age or body type."
]

# 照明・スタイル設定（色変異防止用）
FLAT_LIGHTING_STYLE = {
    "lighting": "Flat, Neutral Studio Lighting",
    "shading_mode": "Albedo / Base Color Only",
    "output_quality": "Asset Quality"
}


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

    # Extract outfit information from characters and add to scene prompt
    enhanced_scene_prompt = scene_prompt
    if not is_character_sheet and not is_background and characters:
        outfit_descriptions = []
        positions = ["Left", "Right", "Third", "Fourth", "Fifth"]
        for i, char in enumerate(characters):
            desc = char.get("description", "")
            # Extract outfit part from description
            if "outfit:" in desc:
                outfit_part = desc.split("outfit:")[-1].strip()
                char_name = char.get("name", f"Character {i+1}")
                pos = positions[i] if i < len(positions) else f"Character {i+1}"
                outfit_descriptions.append(f"{pos} character ({char_name}) wears: {outfit_part}")

        if outfit_descriptions:
            outfit_instruction = "\n\nIMPORTANT - Character outfits:\n" + "\n".join(outfit_descriptions)
            enhanced_scene_prompt = scene_prompt + outfit_instruction

    # Build YAML structure
    yaml_data = {
        "generation_control": GENERATION_CONTROL,
        "color_mode": color_mode_value,
        "aspect_ratio": aspect_ratio,
        "output_type": output_type,
        "output_style": output_style_prompt if output_style_prompt else "auto",
        "style": FLAT_LIGHTING_STYLE,
        "scene": {
            "prompt": enhanced_scene_prompt
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

    # 幻覚防止制約を追加
    yaml_data["constraints"] = ANTI_HALLUCINATION_CONSTRAINTS
    yaml_data["anti_hallucination"] = ANTI_HALLUCINATION_RULES

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
        "generation_control": GENERATION_CONTROL,
        "decorative_texts": decorative_texts,
        "constraints": ANTI_HALLUCINATION_CONSTRAINTS,
        "anti_hallucination": ANTI_HALLUCINATION_RULES
    }

    yaml_content = yaml.dump(yaml_data, allow_unicode=True, default_flow_style=False, sort_keys=False)
    instruction = "The YAML below defines decorative text. Used for post-processing image composition.\n\n"

    return instruction + yaml_content, instruction


def generate_effect_character_yaml(
    char_name: str,
    char_description: str,
    facing_name: str,
    pose_name: str,
    composition_name: str,
    effect_type_name: str,
    effect_color_name: str,
    effect_emission_name: str,
    background_name: str,
    output_style_name: str,
    color_mode_name: str,
    duotone_color: str = None
) -> tuple:
    """
    エフェクト付きキャラクター生成用YAMLを生成

    Args:
        char_name: キャラクター名
        char_description: キャラクター説明
        facing_name: 向き（日本語）
        pose_name: ポーズ（日本語）
        composition_name: 構図（日本語）
        effect_type_name: エフェクトタイプ（日本語）
        effect_color_name: エフェクト色（日本語）
        effect_emission_name: 発射方法（日本語）
        background_name: 背景（日本語）
        output_style_name: 出力スタイル名
        color_mode_name: カラーモード名
        duotone_color: 二色刷りの色

    Returns:
        (yaml_string, instruction) のタプル
    """
    # 定数から英語に変換
    facing = CHARACTER_FACING.get(facing_name, "right")
    pose = CHARACTER_POSES.get(pose_name, "attacking, offensive pose")
    composition = CHARACTER_COMPOSITIONS.get(composition_name, "")
    effect_type = EFFECT_TYPES.get(effect_type_name, "")
    effect_color = EFFECT_COLORS.get(effect_color_name, "")
    effect_emission = EFFECT_EMISSIONS.get(effect_emission_name, "")
    background = SIMPLE_BACKGROUNDS.get(background_name, "plain white background")

    # カットイン構図かどうか判定
    is_cutin = composition_name in CUTIN_COMPOSITIONS

    # カラーモード情報
    color_mode_value, color_mode_prompt = get_color_mode_info(color_mode_name, duotone_color)

    # 出力スタイル
    output_style_prompt = OUTPUT_STYLES.get(output_style_name, "")

    # 向き指示を構築（構図によって説明を変える）
    # 強化されたorientation情報を生成
    if facing == "right":
        face_direction = "Looking Right (Profile View)"
        body_facing = "Facing Right (Side Profile)"
    elif facing == "left":
        face_direction = "Looking Left (Profile View)"
        body_facing = "Facing Left (Side Profile)"
    else:
        face_direction = "Looking Front (Front View)"
        body_facing = "Facing Front"

    if is_cutin:
        # カットイン: 必殺技演出、画面外に向かって
        facing_desc = f"facing {facing}, looking {facing}"
        attack_direction_desc = f"releasing special attack towards the {facing} side of the frame"
    else:
        # 通常配置: 対戦相手に向かって
        facing_desc = f"facing {facing}, turned towards {facing}"
        attack_direction_desc = f"attacking towards the {facing} (where opponent would be)"

    # エフェクト指示を構築
    effect_parts = []
    if effect_type:
        if effect_color:
            effect_parts.append(f"{effect_color} {effect_type}")
        else:
            effect_parts.append(effect_type)
        if effect_emission:
            effect_parts.append(effect_emission)
        effect_parts.append(attack_direction_desc)

    effect_desc = ", ".join(effect_parts) if effect_parts else ""

    # プロンプト構築
    prompt_parts = []

    if composition:
        prompt_parts.append(composition)

    prompt_parts.append(f"Character {facing_desc}")
    prompt_parts.append(pose)

    if effect_desc:
        prompt_parts.append(effect_desc)

    if char_description:
        prompt_parts.append(f"Character appearance: {char_description}")

    prompt_parts.append(background)

    if color_mode_prompt:
        prompt_parts.append(color_mode_prompt)

    if output_style_prompt:
        prompt_parts.append(f"Style: {output_style_prompt}")

    scene_prompt = ". ".join(prompt_parts) + "."

    # YAML構造
    yaml_data = {
        "output_type": "effect_character",
        "generation_control": GENERATION_CONTROL,
        "color_mode": color_mode_value,
        "orientation": {
            "face_direction": face_direction,
            "body_facing": body_facing,
            "eye_line": "Looking at Opponent",
            "mirror_mode": "Do not mirror/flip the character"
        },
        "character": {
            "name": char_name if char_name else "Character",
            "facing": facing,
            "pose": pose_name,
            "description": char_description
        },
        "effect": {
            "type": effect_type_name,
            "color": effect_color_name,
            "emission": effect_emission_name,
            "direction": facing
        },
        "composition": composition_name,
        "composition_type": "cutin" if is_cutin else "normal",
        "background": background_name,
        "style": FLAT_LIGHTING_STYLE,
        "scene": {
            "prompt": scene_prompt
        },
        "constraints": ANTI_HALLUCINATION_CONSTRAINTS,
        "anti_hallucination": ANTI_HALLUCINATION_RULES
    }

    yaml_content = yaml.dump(yaml_data, allow_unicode=True, default_flow_style=False, sort_keys=False)

    # インストラクションも構図によって変える
    if is_cutin:
        instruction = f"""Generate a dramatic cut-in character image with effects based on the YAML below.
This is a SPECIAL MOVE CUT-IN scene - the character should be {facing_desc}, releasing their attack towards the {facing} side.
The effect should look like a powerful special move announcement.
Reference attached character image if available.

"""
    else:
        instruction = f"""Generate a battle-ready character image with effects based on the YAML below.
This is for a VERSUS BATTLE scene - the character should be {facing_desc}, attacking towards where their opponent would be on the {facing}.
The character's body and attack should be directed towards the {facing} side.
Reference attached character image if available.

"""

    return instruction + yaml_content, instruction


def generate_pixel_character_yaml(
    char_name: str,
    char_description: str,
    facing_name: str,
    pose_name: str,
    pixel_style_name: str,
    pixel_size_name: str,
    background_name: str
) -> tuple:
    """
    ドット絵キャラクター生成用YAMLを生成

    Args:
        char_name: キャラクター名
        char_description: キャラクター説明
        facing_name: 向き（日本語）
        pose_name: ポーズ（日本語）
        pixel_style_name: ドット絵スタイル（日本語）
        pixel_size_name: サイズ（日本語）
        background_name: 背景（日本語）

    Returns:
        (yaml_string, instruction) のタプル
    """
    facing = CHARACTER_FACING.get(facing_name, "right")
    pose = CHARACTER_POSES.get(pose_name, "battle ready, fighting stance")
    pixel_style = PIXEL_STYLES.get(pixel_style_name, "pixel art style, 16-bit")
    pixel_size = PIXEL_SIZES.get(pixel_size_name, "medium sprite")
    background = SIMPLE_BACKGROUNDS.get(background_name, "plain white background")

    # 強化されたorientation情報を生成
    if facing == "right":
        face_direction = "Looking Right (Profile View)"
        body_facing = "Facing Right (Side Profile)"
    elif facing == "left":
        face_direction = "Looking Left (Profile View)"
        body_facing = "Facing Left (Side Profile)"
    else:
        face_direction = "Looking Front (Front View)"
        body_facing = "Facing Front"

    facing_desc = f"facing {facing}"

    # プロンプト構築
    prompt_parts = [
        pixel_style,
        pixel_size,
        f"Character sprite {facing_desc}",
        pose
    ]

    if char_description:
        prompt_parts.append(f"Character appearance: {char_description}")

    prompt_parts.append(background)
    prompt_parts.append("Clean pixel art, game sprite style")

    scene_prompt = ". ".join(prompt_parts) + "."

    yaml_data = {
        "output_type": "pixel_character",
        "generation_control": GENERATION_CONTROL,
        "orientation": {
            "face_direction": face_direction,
            "body_facing": body_facing,
            "mirror_mode": "Do not mirror/flip the character"
        },
        "character": {
            "name": char_name if char_name else "Character",
            "facing": facing,
            "pose": pose_name,
            "description": char_description
        },
        "pixel_style": pixel_style_name,
        "pixel_size": pixel_size_name,
        "background": background_name,
        "style": FLAT_LIGHTING_STYLE,
        "scene": {
            "prompt": scene_prompt
        },
        "constraints": ANTI_HALLUCINATION_CONSTRAINTS,
        "anti_hallucination": ANTI_HALLUCINATION_RULES
    }

    yaml_content = yaml.dump(yaml_data, allow_unicode=True, default_flow_style=False, sort_keys=False)

    instruction = f"""Generate a pixel art character sprite based on the YAML below.
The character should be {facing_desc} in {pixel_style_name} style.
Reference attached character image if available.

"""

    return instruction + yaml_content, instruction


def generate_composite_yaml(
    images_data: list,
    background_path: str,
    layout_name: str,
    ui_elements: dict,
    battle_mode_name: str = "なし",
    additional_instructions: str = ""
) -> tuple:
    """
    画像合成用YAMLを生成

    Args:
        images_data: 画像データのリスト
            各要素は dict: {
                'path': str (画像パス、表示用),
                'position_name': str (配置位置、日本語),
                'size_name': str (サイズ、日本語),
                'description': str (画像の説明)
            }
        background_path: 背景画像パス
        layout_name: レイアウト名（日本語）
        ui_elements: UI要素 dict: {
            'health_bars': bool,
            'super_meter': bool,
            'character_names': bool,
            'move_name': str
        }
        battle_mode_name: 対戦モード（日本語）
        additional_instructions: 追加指示

    Returns:
        (yaml_string, instruction) のタプル
    """
    layout = COMPOSITE_LAYOUTS.get(layout_name, "fighting game style")
    battle_mode = COMPOSITE_BATTLE_MODES.get(battle_mode_name, "")

    # 画像配置指示を構築
    placement_instructions = []
    for i, img in enumerate(images_data):
        if img.get('path') or img.get('description'):
            position = COMPOSITE_POSITIONS.get(img.get('position_name', '左'), 'left')
            size = COMPOSITE_SIZES.get(img.get('size_name', '中'), 'medium')
            desc = img.get('description', f'Image {i+1}')

            placement_instructions.append(
                f"Place {desc} on the {position} side, {size} size"
            )

    # UI要素指示を構築
    ui_instructions = []
    if ui_elements.get('health_bars', False):
        ui_instructions.append("health bars at top")
    if ui_elements.get('super_meter', False):
        ui_instructions.append("super meter/gauge at bottom")
    if ui_elements.get('character_names', False):
        ui_instructions.append("character name plates")
    if ui_elements.get('move_name'):
        ui_instructions.append(f"special move name '{ui_elements['move_name']}' with dramatic text effects")

    # 対戦モード指示を構築
    battle_instructions = []
    if battle_mode == "versus_facing":
        battle_instructions = [
            "IMPORTANT: This is a VERSUS BATTLE scene",
            "The characters must FACE EACH OTHER",
            "Left character should face RIGHT (towards the right opponent)",
            "Right character should face LEFT (towards the left opponent)",
            "Their attacks/effects should be directed at each other",
            "If attacks are shown, they should collide or cross in the center"
        ]
    elif battle_mode == "coop_same_direction":
        battle_instructions = [
            "IMPORTANT: This is a COOPERATIVE scene",
            "Both characters should face the SAME DIRECTION",
            "They are fighting together against a common enemy",
            "Their attacks should be directed in the same direction"
        ]

    # プロンプト構築
    prompt_parts = [
        f"Composite image in {layout} style",
        "Combine the provided images into a cohesive scene"
    ]

    # 対戦モード指示を追加（最優先）
    if battle_instructions:
        prompt_parts.extend(battle_instructions)

    if placement_instructions:
        prompt_parts.extend(placement_instructions)

    prompt_parts.append("Use the background image as the scene backdrop")

    if ui_instructions:
        prompt_parts.append(f"Add game UI elements: {', '.join(ui_instructions)}")

    if additional_instructions:
        prompt_parts.append(additional_instructions)

    prompt_parts.append("Ensure all elements blend naturally with consistent lighting and style")

    scene_prompt = ". ".join(prompt_parts) + "."

    # YAML構造
    yaml_data = {
        "output_type": "image_composite",
        "generation_control": GENERATION_CONTROL,
        "layout": layout_name,
        "battle_mode": battle_mode_name,
        "images": [
            {
                "position": img.get('position_name', '左'),
                "size": img.get('size_name', '中'),
                "description": img.get('description', '')
            }
            for img in images_data if img.get('path') or img.get('description')
        ],
        "background": "see attached background image",
        "ui_elements": {
            "health_bars": ui_elements.get('health_bars', False),
            "super_meter": ui_elements.get('super_meter', False),
            "character_names": ui_elements.get('character_names', False),
            "move_name": ui_elements.get('move_name', '')
        },
        "style": FLAT_LIGHTING_STYLE,
        "scene": {
            "prompt": scene_prompt
        },
        "constraints": ANTI_HALLUCINATION_CONSTRAINTS,
        "anti_hallucination": ANTI_HALLUCINATION_RULES
    }

    if additional_instructions:
        yaml_data["additional_instructions"] = additional_instructions

    yaml_content = yaml.dump(yaml_data, allow_unicode=True, default_flow_style=False, sort_keys=False)

    # 画像数をカウント
    image_count = len([img for img in images_data if img.get('path') or img.get('description')])

    # インストラクションを対戦モードに応じて変更
    if battle_mode == "versus_facing":
        instruction = f"""Composite the {image_count} character/element images with the background image based on the YAML below.
This is a VERSUS BATTLE scene - characters must FACE EACH OTHER and their attacks should be directed at their opponent.
Left character faces RIGHT, right character faces LEFT.
Combine all attached images into a single cohesive {layout_name} scene.

"""
    elif battle_mode == "coop_same_direction":
        instruction = f"""Composite the {image_count} character/element images with the background image based on the YAML below.
This is a COOPERATIVE scene - both characters should face the SAME DIRECTION.
Combine all attached images into a single cohesive {layout_name} scene.

"""
    else:
        instruction = f"""Composite the {image_count} character/element images with the background image based on the YAML below.
Combine all attached images into a single cohesive {layout_name} scene.
Maintain the style and quality of the original images while blending them naturally.

"""

    return instruction + yaml_content, instruction
