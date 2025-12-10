# -*- coding: utf-8 -*-
"""
シーンビルダーロジック
シーンテンプレートの定義と生成
"""

# シーンタイプ定義（プリセット）
SCENE_TYPES = {
    "1キャラ: カットイン": {
        "description": "1キャラのみの大きなカットイン（必殺技演出など）",
        "single_character": True,
        "left_style": "cutin_large",
        "right_style": None,
    },
    "同一キャラ: カットイン/ドット絵": {
        "description": "同じキャラが左にリアル(カットイン)、右にドット絵で表示",
        "single_character": False,
        "same_character": True,
        "left_style": "cutin",      # カットイン
        "right_style": "pixel",     # ドット絵
    },
    "同一キャラ: ドット絵/カットイン": {
        "description": "同じキャラが左にドット絵、右にリアル(カットイン)で表示",
        "single_character": False,
        "same_character": True,
        "left_style": "pixel",
        "right_style": "cutin",
    },
    "別キャラ: 両方カットイン": {
        "description": "異なるキャラが両方リアル(カットイン)で対戦",
        "single_character": False,
        "same_character": False,
        "left_style": "cutin",
        "right_style": "cutin",
    },
    "別キャラ: 両方通常配置": {
        "description": "異なるキャラが両方リアル(通常配置)で対戦",
        "single_character": False,
        "same_character": False,
        "left_style": "normal",
        "right_style": "normal",
    },
    "別キャラ: 両方ドット絵": {
        "description": "異なるキャラが両方ドット絵で対戦",
        "single_character": False,
        "same_character": False,
        "left_style": "pixel",
        "right_style": "pixel",
    },
}

# スタイル表示名
STYLE_NAMES = {
    "cutin_large": "大カットイン",
    "cutin": "リアル(カットイン)",
    "normal": "リアル(通常配置)",
    "pixel": "ドット絵(16bit)",
}

# アクション定義
ACTIONS = {
    "attacking": "attacking, firing energy beam, offensive pose",
    "defending": "defending, blocking, guarding pose",
    "damaged": "taking damage, hurt, recoiling",
    "victory": "victorious, triumphant, winning pose",
    "ready": "battle ready, fighting stance, determined expression",
    "special": "charging special attack, power gathering, glowing aura",
}

ACTION_NAMES = {
    "attacking": "攻撃",
    "defending": "防御",
    "damaged": "ダメージ",
    "victory": "勝利",
    "ready": "構え",
    "special": "必殺技チャージ",
}

# 背景定義
BACKGROUNDS = {
    "教室": "Classroom background with desks and chalkboard.",
    "体育館": "Gymnasium background with wooden floor.",
    "屋上": "School rooftop background with fence and blue sky.",
    "街中": "Urban street background at night with neon lights and buildings.",
    "異世界": "Fantasy world background with magical atmosphere and floating crystals.",
    "闘技場": "Battle arena background with audience and spotlights.",
    "公園": "Park background with trees and benches.",
    "ビーチ": "Beach background with sand and ocean waves.",
}

# 同一キャラ指示文
SAME_CHARACTER_INSTRUCTION = """IMPORTANT: Both characters shown are THE SAME PERSON displayed in different art styles. They must have IDENTICAL clothing, hair color, and hair style. The only difference is the rendering style."""

# 別キャラ指示文
DIFFERENT_CHARACTER_INSTRUCTION = """IMPORTANT: The left and right characters are DIFFERENT PEOPLE. They should have distinct appearances, but the art style should be consistent between them."""


def get_scene_types() -> list:
    """シーンタイプ名のリストを取得"""
    return list(SCENE_TYPES.keys())


def get_scene_type_info(scene_type: str) -> dict:
    """シーンタイプの情報を取得"""
    return SCENE_TYPES.get(scene_type, {})


def get_action_names() -> dict:
    """アクション名の辞書を取得（日本語: 英語キー）"""
    return {v: k for k, v in ACTION_NAMES.items()}


def get_action_display_names() -> list:
    """アクションの表示名リストを取得"""
    return list(ACTION_NAMES.values())


def get_background_names() -> list:
    """背景名のリストを取得"""
    return list(BACKGROUNDS.keys())


def _build_character_description(style: str, action: str, position: str, zoom: str = "normal") -> str:
    """キャラクターの説明文を生成"""
    action_desc = ACTIONS.get(action, action)

    if style == "cutin_large":
        if zoom == "extreme":
            return f"extreme close-up anime-style character cut-in, face and upper body filling the entire frame, very dramatic angle, {action_desc}"
        else:
            return f"dramatic full-screen anime-style character cut-in, intense close-up filling most of the frame, {action_desc}"
    elif style == "cutin":
        return f"large anime-style character cut-in, dramatic close-up, {action_desc}"
    elif style == "normal":
        return f"anime-style character in full body view, {action_desc}"
    elif style == "pixel":
        return f"pixel art 16-bit chibi character sprite, {action_desc}"
    return ""


def generate_scene_prompt(
    scene_type: str,
    left_action: str,
    right_action: str,
    background: str,
    left_name: str = "",
    right_name: str = "",
    left_speech: str = "",
    right_speech: str = "",
    move_name: str = "",
    show_health_bars: bool = True,
    show_super_meter: bool = True,
    show_dialogue_box: bool = False,
    zoom: str = "normal"
) -> str:
    """
    シーンプロンプトを生成

    Args:
        scene_type: シーンタイプ名
        left_action: 左キャラのアクション（英語キー）
        right_action: 右キャラのアクション（英語キー）
        background: 背景名
        left_name: 左キャラの名前（オプション）
        right_name: 右キャラの名前（オプション）
        left_speech: 左キャラのセリフ（オプション）
        right_speech: 右キャラのセリフ（オプション）
        move_name: 技名（オプション）
        show_health_bars: ヘルスバーを表示するか
        show_super_meter: SUPERゲージを表示するか
        show_dialogue_box: ダイアログボックスを表示するか
        zoom: ズームレベル（"normal" or "extreme"）- 1キャラモードのみ有効

    Returns:
        生成されたシーンプロンプト
    """
    type_info = SCENE_TYPES.get(scene_type)
    if not type_info:
        return ""

    single_character = type_info.get("single_character", False)
    left_style = type_info["left_style"]
    right_style = type_info.get("right_style")

    # 背景説明
    bg_desc = BACKGROUNDS.get(background, "")

    # 1キャラモードの場合
    if single_character:
        char_desc = _build_character_description(left_style, left_action, "center", zoom)

        # キャラ名の指示
        name_instruction = ""
        if left_name:
            name_instruction = f"\nCharacter name: \"{left_name}\"."

        # セリフの指示
        speech_instruction = ""
        if left_speech:
            if show_dialogue_box:
                speech_instruction = f"\nAdd a dialogue box at the bottom with character portrait, displaying: 「{left_speech}」"
            else:
                speech_instruction = f"\nCharacter's speech bubble: 「{left_speech}」"

        # 技名の指示
        move_instruction = ""
        if move_name:
            move_instruction = f"\nDisplay special move name \"{move_name}\" prominently with dramatic text effects."

        # UI要素の指示を構築
        ui_elements = []
        if show_health_bars:
            ui_elements.append("health bar")
        if show_super_meter:
            ui_elements.append("super meter/gauge")

        if ui_elements:
            ui_instruction = f"Add {', '.join(ui_elements)}."
        else:
            ui_instruction = "Minimal or no game UI elements."

        # プロンプト組み立て（1キャラ版）
        prompt = f"""Game-style special move cut-in scene with dramatic composition.

{char_desc}

{bg_desc}{name_instruction}{speech_instruction}{move_instruction}

{ui_instruction}
Dramatic lighting, energy effects, and dynamic camera angle."""

        return prompt.strip()

    # 2キャラモードの場合
    same_character = type_info.get("same_character", False)

    # キャラクター説明を生成
    left_desc = _build_character_description(left_style, left_action, "left")
    right_desc = _build_character_description(right_style, right_action, "right")

    # キャラ関係の指示
    if same_character:
        char_instruction = SAME_CHARACTER_INSTRUCTION
    else:
        char_instruction = DIFFERENT_CHARACTER_INSTRUCTION

    # キャラ名の指示
    name_instruction = ""
    if left_name or right_name:
        name_parts = []
        if left_name:
            name_parts.append(f"left character named \"{left_name}\"")
        if right_name:
            name_parts.append(f"right character named \"{right_name}\"")
        name_instruction = f"\nCharacter name plates should show: {', '.join(name_parts)}."

    # セリフの指示（ダイアログボックスか吹き出しか）
    speech_instruction = ""
    if left_speech or right_speech:
        if show_dialogue_box:
            # ダイアログボックス形式（RPG風）
            dialogue_text = left_speech or right_speech
            speech_instruction = f"\nAdd a dialogue box at the bottom of the screen with character portrait, displaying: 「{dialogue_text}」"
        else:
            # 吹き出し形式（格闘ゲーム風）
            speech_parts = []
            if left_speech:
                speech_parts.append(f"Left character's speech bubble: 「{left_speech}」")
            if right_speech:
                speech_parts.append(f"Right character's speech bubble: 「{right_speech}」")
            speech_instruction = "\n" + "\n".join(speech_parts)

    # 技名の指示
    move_instruction = ""
    if move_name:
        move_instruction = f"\nDisplay special move name \"{move_name}\" prominently in the scene with dramatic text effects."

    # UI要素の指示を構築
    ui_elements = []
    if show_health_bars:
        ui_elements.append("health bars at top")
    if left_name or right_name:
        ui_elements.append("character name plates")
    if show_super_meter:
        ui_elements.append("super meter/gauge at bottom")

    if ui_elements:
        ui_instruction = f"Add {', '.join(ui_elements)}."
    else:
        ui_instruction = "No game UI elements (no health bars, no meters)."

    # プロンプト組み立て
    prompt = f"""Game-style battle screen with dramatic composition.

Left side: {left_desc}
Right side: {right_desc}

{bg_desc}

{char_instruction}{name_instruction}{speech_instruction}{move_instruction}

{ui_instruction}
Energy effects and dramatic lighting."""

    return prompt.strip()


# 後方互換性のための関数（旧バージョン用）
def get_template_names() -> list:
    """利用可能なテンプレート名のリストを取得（後方互換）"""
    return ["格闘ゲーム風"]


def get_template(name: str) -> dict:
    """テンプレートを取得（後方互換）"""
    if name == "格闘ゲーム風":
        return {"name": "格闘ゲーム風"}
    return None


def get_actions(template_name: str) -> dict:
    """アクション選択肢を取得（後方互換）"""
    return ACTION_NAMES


def get_backgrounds(template_name: str) -> dict:
    """背景選択肢を取得（後方互換）"""
    return BACKGROUNDS
