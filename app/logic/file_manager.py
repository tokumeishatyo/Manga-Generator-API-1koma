# -*- coding: utf-8 -*-
"""
ファイル操作ロジック
YAML読み書き、履歴管理、テンプレート読み込み、画像処理
"""

import os
import json
import yaml
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

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


def save_yaml_file(filepath: str, content: str, generated_image_path: str = None) -> tuple:
    """
    YAMLファイルを保存（オプションでメタデータ付き）

    Args:
        filepath: 保存先パス
        content: YAML内容
        generated_image_path: 生成された画像のパス（メタデータとして埋め込む）

    Returns:
        (success: bool, error_message: str or None)
    """
    try:
        final_content = content

        # メタデータを追加（画像パスが指定された場合）
        if generated_image_path:
            metadata = f"""
# ====================================================
# メタデータ (Metadata) - 自動生成
# ====================================================
_metadata:
  created_at: "{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
  generated_image: "{os.path.basename(generated_image_path)}"
  generated_image_full_path: "{generated_image_path}"
"""
            final_content = content + metadata

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(final_content)
        return True, None
    except Exception as e:
        return False, str(e)


def update_yaml_metadata(yaml_filepath: str, image_filepath: str) -> tuple:
    """
    既存のYAMLファイルにメタデータを追加/更新

    Args:
        yaml_filepath: YAMLファイルのパス
        image_filepath: 関連付ける画像ファイルのパス

    Returns:
        (success: bool, error_message: str or None)
    """
    try:
        # 既存のYAMLを読み込む
        with open(yaml_filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 既存のメタデータセクションを削除
        if "# メタデータ (Metadata)" in content:
            content = content.split("# ====================================================\n# メタデータ")[0].rstrip()

        # 新しいメタデータを追加
        metadata = f"""

# ====================================================
# メタデータ (Metadata) - 自動生成
# ====================================================
_metadata:
  created_at: "{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
  generated_image: "{os.path.basename(image_filepath)}"
  generated_image_full_path: "{image_filepath}"
"""
        content += metadata

        with open(yaml_filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, None
    except Exception as e:
        return False, str(e)


def extract_metadata_from_yaml(filepath: str) -> dict:
    """
    YAMLファイルからメタデータを抽出

    Args:
        filepath: YAMLファイルのパス

    Returns:
        メタデータの辞書（存在しない場合は空辞書）
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # YAMLを解析
        data = yaml.safe_load(content)
        if data and '_metadata' in data:
            return data['_metadata']
    except Exception as e:
        print(f"Warning: Could not extract metadata: {e}")
    return {}


def check_yaml_image_match(yaml_filepath: str, image_filepath: str) -> dict:
    """
    YAMLと画像ファイルの整合性をチェック

    Args:
        yaml_filepath: YAMLファイルのパス
        image_filepath: 画像ファイルのパス

    Returns:
        {
            'match': bool,           # 一致しているか
            'warning': str or None,  # 警告メッセージ
            'yaml_image': str or None,  # YAMLに記録された画像名
            'yaml_created': str or None  # YAML作成日時
        }
    """
    result = {
        'match': False,
        'warning': None,
        'yaml_image': None,
        'yaml_created': None
    }

    # YAMLからメタデータを取得
    metadata = extract_metadata_from_yaml(yaml_filepath)

    if not metadata:
        result['warning'] = "YAMLにメタデータがありません。画像との対応を確認してください。"
        return result

    result['yaml_image'] = metadata.get('generated_image')
    result['yaml_created'] = metadata.get('created_at')

    # 画像名を比較
    image_basename = os.path.basename(image_filepath)
    yaml_image = metadata.get('generated_image', '')

    if image_basename == yaml_image:
        result['match'] = True
    else:
        result['warning'] = f"画像ファイルが一致しません。\n" \
                           f"  YAML記録: {yaml_image}\n" \
                           f"  選択画像: {image_basename}\n" \
                           f"  YAML作成: {result['yaml_created']}"

    return result


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


# ====================================================
# 画像処理: タイトル合成機能
# ====================================================

def add_title_to_image(
    image: Image.Image,
    title: str,
    position: str = "top-left",
    font_size: int = None,
    font_color: tuple = (255, 255, 255),
    stroke_color: tuple = (0, 0, 0),
    stroke_width: int = 2,
    margin: int = 20
) -> Image.Image:
    """
    画像にタイトルテキストを合成する

    Args:
        image: 元の画像（PILのImageオブジェクト）
        title: 表示するタイトル文字列
        position: 位置 ("top-left", "top-center", "top-right", "bottom-left", "bottom-center", "bottom-right")
        font_size: フォントサイズ（Noneの場合は画像サイズに応じて自動計算）
        font_color: フォント色 (R, G, B)
        stroke_color: 縁取り色 (R, G, B)
        stroke_width: 縁取りの太さ
        margin: 画像端からの余白

    Returns:
        タイトルが合成された新しい画像
    """
    if not title:
        return image

    # 画像をコピーして編集
    result = image.copy()
    draw = ImageDraw.Draw(result)

    # フォントサイズを自動計算（画像の高さの約5%）
    if font_size is None:
        font_size = max(20, int(image.height * 0.05))

    # フォントを取得（日本語対応フォントを試行）
    font = _get_japanese_font(font_size)

    # テキストのバウンディングボックスを取得
    bbox = draw.textbbox((0, 0), title, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # 位置を計算
    x, y = _calculate_text_position(
        image.width, image.height,
        text_width, text_height,
        position, margin
    )

    # 縁取り付きでテキストを描画
    draw.text(
        (x, y),
        title,
        font=font,
        fill=font_color,
        stroke_width=stroke_width,
        stroke_fill=stroke_color
    )

    return result


def _get_japanese_font(size: int) -> ImageFont.FreeTypeFont:
    """
    日本語対応フォントを取得する

    Args:
        size: フォントサイズ

    Returns:
        ImageFontオブジェクト
    """
    # 日本語フォントの候補リスト（OS別）
    font_candidates = [
        # Windows
        "C:/Windows/Fonts/meiryo.ttc",
        "C:/Windows/Fonts/msgothic.ttc",
        "C:/Windows/Fonts/YuGothM.ttc",
        # macOS
        "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
        # Linux
        "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        # Google Fonts (if installed)
        "/usr/share/fonts/truetype/noto/NotoSansJP-Regular.otf",
    ]

    for font_path in font_candidates:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                continue

    # フォールバック: デフォルトフォント
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()


def _calculate_text_position(
    img_width: int,
    img_height: int,
    text_width: int,
    text_height: int,
    position: str,
    margin: int
) -> tuple:
    """
    テキストの描画位置を計算する

    Args:
        img_width: 画像の幅
        img_height: 画像の高さ
        text_width: テキストの幅
        text_height: テキストの高さ
        position: 位置指定文字列
        margin: 余白

    Returns:
        (x, y) 座標のタプル
    """
    # 水平位置
    if "left" in position:
        x = margin
    elif "right" in position:
        x = img_width - text_width - margin
    else:  # center
        x = (img_width - text_width) // 2

    # 垂直位置
    if "top" in position:
        y = margin
    elif "bottom" in position:
        y = img_height - text_height - margin
    else:  # center
        y = (img_height - text_height) // 2

    return x, y
