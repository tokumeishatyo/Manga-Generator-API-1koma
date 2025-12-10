# -*- coding: utf-8 -*-
"""
シーンビルダーロジック
シーンテンプレートの定義と生成
"""

# シーンタイプ定義（プリセット）
SCENE_TYPES = {
    "同一キャラ: カットイン/ドット絵": {
        "description": "同じキャラが左にリアル(カットイン)、右にドット絵で表示",
        "same_character": True,
        "left_style": "cutin",      # カットイン
        "right_style": "pixel",     # ドット絵
    },
    "同一キャラ: ドット絵/カットイン": {
        "description": "同じキャラが左にドット絵、右にリアル(カットイン)で表示",
        "same_character": True,
        "left_style": "pixel",
        "right_style": "cutin",
    },
    "別キャラ: 両方カットイン": {
        "description": "異なるキャラが両方リアル(カットイン)で対戦",
        "same_character": False,
        "left_style": "cutin",
        "right_style": "cutin",
    },
    "別キャラ: 両方通常配置": {
        "description": "異なるキャラが両方リアル(通常配置)で対戦",
        "same_character": False,
        "left_style": "normal",
        "right_style": "normal",
    },
    "別キャラ: 両方ドット絵": {
        "description": "異なるキャラが両方ドット絵で対戦",
        "same_character": False,
        "left_style": "pixel",
        "right_style": "pixel",
    },
}

# スタイル表示名
STYLE_NAMES = {
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


def _build_character_description(style: str, action: str, position: str) -> str:
    """キャラクターの説明文を生成"""
    action_desc = ACTIONS.get(action, action)

    if style == "cutin":
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
    background: str
) -> str:
    """
    シーンプロンプトを生成

    Args:
        scene_type: シーンタイプ名
        left_action: 左キャラのアクション（英語キー）
        right_action: 右キャラのアクション（英語キー）
        background: 背景名

    Returns:
        生成されたシーンプロンプト
    """
    type_info = SCENE_TYPES.get(scene_type)
    if not type_info:
        return ""

    same_character = type_info["same_character"]
    left_style = type_info["left_style"]
    right_style = type_info["right_style"]

    # キャラクター説明を生成
    left_desc = _build_character_description(left_style, left_action, "left")
    right_desc = _build_character_description(right_style, right_action, "right")

    # 背景説明
    bg_desc = BACKGROUNDS.get(background, "")

    # キャラ関係の指示
    if same_character:
        char_instruction = SAME_CHARACTER_INSTRUCTION
    else:
        char_instruction = DIFFERENT_CHARACTER_INSTRUCTION

    # プロンプト組み立て
    prompt = f"""Fighting game style battle screen with dramatic composition.

Left side: {left_desc}
Right side: {right_desc}

{bg_desc}

{char_instruction}

Add health bars, character name plates, and fighting game UI elements.
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
