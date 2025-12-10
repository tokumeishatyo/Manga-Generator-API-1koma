# -*- coding: utf-8 -*-
"""
シーンビルダーロジック
シーンテンプレートの定義と生成
"""

# シーンテンプレート定義
SCENE_TEMPLATES = {
    "格闘ゲーム風": {
        "name": "格闘ゲーム風",
        "description": "格闘ゲームのバトル画面風。片側にリアルなカットイン、反対側にドット絵キャラ",
        "recommended_style": "格闘ゲーム風",
        "base_prompt": {
            "left_real": """Fighting game style battle screen.
Left side: large anime-style character cut-in, dramatic pose, {left_action} expression.
Right side: pixel art 16-bit chibi version of the character in battle stance, {right_action} pose.
{background}
{same_character_instruction}
Energy effects and dramatic lighting.""",
            "left_deformed": """Fighting game style battle screen.
Left side: pixel art 16-bit chibi version of the character in battle stance, {left_action} pose.
Right side: large anime-style character cut-in, dramatic pose, {right_action} expression.
{background}
{same_character_instruction}
Energy effects and dramatic lighting."""
        },
        "actions": {
            "attacking": "attacking, firing energy beam",
            "defending": "defending, blocking",
            "damaged": "taking damage, hurt",
            "victory": "victorious, triumphant",
            "ready": "battle ready, determined"
        },
        "backgrounds": {
            "教室": "Classroom background with desks and chalkboard.",
            "体育館": "Gymnasium background with wooden floor.",
            "屋上": "School rooftop background with fence and sky.",
            "街中": "Urban street background with buildings.",
            "異世界": "Fantasy world background with magical atmosphere.",
            "闘技場": "Battle arena background with audience."
        }
    }
}

# 同一キャラ指示文
SAME_CHARACTER_INSTRUCTION = """IMPORTANT: Both the anime-style character and the pixel art chibi are THE SAME CHARACTER. They must wear IDENTICAL clothing and have the same hair color/style. The only difference is the art style (realistic vs pixel art)."""


def get_template_names() -> list:
    """
    利用可能なテンプレート名のリストを取得

    Returns:
        テンプレート名のリスト
    """
    return list(SCENE_TEMPLATES.keys())


def get_template(name: str) -> dict:
    """
    指定されたテンプレートを取得

    Args:
        name: テンプレート名

    Returns:
        テンプレート辞書、見つからない場合はNone
    """
    return SCENE_TEMPLATES.get(name)


def get_actions(template_name: str) -> dict:
    """
    テンプレートのアクション選択肢を取得

    Args:
        template_name: テンプレート名

    Returns:
        アクション辞書 {日本語名: 英語プロンプト}
    """
    template = SCENE_TEMPLATES.get(template_name)
    if template:
        return template.get("actions", {})
    return {}


def get_backgrounds(template_name: str) -> dict:
    """
    テンプレートの背景選択肢を取得

    Args:
        template_name: テンプレート名

    Returns:
        背景辞書 {日本語名: 英語プロンプト}
    """
    template = SCENE_TEMPLATES.get(template_name)
    if template:
        return template.get("backgrounds", {})
    return {}


def generate_scene_prompt(
    template_name: str,
    left_is_real: bool = True,
    same_character: bool = True,
    left_action: str = "attacking",
    right_action: str = "defending",
    background: str = "教室"
) -> str:
    """
    シーンプロンプトを生成

    Args:
        template_name: テンプレート名
        left_is_real: True=左がリアル/右がドット絵、False=左がドット絵/右がリアル
        same_character: 同一キャラかどうか
        left_action: 左キャラのアクション
        right_action: 右キャラのアクション
        background: 背景名

    Returns:
        生成されたシーンプロンプト
    """
    template = SCENE_TEMPLATES.get(template_name)
    if not template:
        return ""

    # ベースプロンプトを選択
    base_prompts = template.get("base_prompt", {})
    if left_is_real:
        base_prompt = base_prompts.get("left_real", "")
    else:
        base_prompt = base_prompts.get("left_deformed", "")

    # アクションを取得
    actions = template.get("actions", {})
    left_action_prompt = actions.get(left_action, left_action)
    right_action_prompt = actions.get(right_action, right_action)

    # 背景を取得
    backgrounds = template.get("backgrounds", {})
    background_prompt = backgrounds.get(background, "")

    # 同一キャラ指示
    same_char_instruction = SAME_CHARACTER_INSTRUCTION if same_character else ""

    # プロンプトを組み立て
    prompt = base_prompt.format(
        left_action=left_action_prompt,
        right_action=right_action_prompt,
        background=background_prompt,
        same_character_instruction=same_char_instruction
    )

    return prompt.strip()
