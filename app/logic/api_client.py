# -*- coding: utf-8 -*-
"""
API呼び出しロジック
Gemini APIとの通信処理
"""

import io
from PIL import Image
from google import genai
from google.genai import types


def generate_image_with_api(
    api_key: str,
    yaml_prompt: str,
    char_image_paths: list,
    resolution: str = "2K",
    ref_image_path: str = None
) -> dict:
    """
    Gemini APIを使用して画像を生成

    Args:
        api_key: Google AI API Key
        yaml_prompt: YAMLプロンプト文字列
        char_image_paths: キャラクター参照画像のパスリスト
        resolution: 解像度 ("1K", "2K", "4K")
        ref_image_path: 参考画像（清書モード用）のパス

    Returns:
        結果を含む辞書:
        {
            'success': bool,
            'image': PIL.Image or None,
            'error': str or None
        }
    """
    try:
        client = genai.Client(api_key=api_key)

        # 解像度の設定
        resolution_map = {
            "1K": "approximately 1024x1024 pixels (1K resolution)",
            "2K": "approximately 2048x2048 pixels (2K resolution, high quality)",
            "4K": "approximately 4096x4096 pixels (4K resolution, ultra high quality)"
        }
        resolution_instruction = resolution_map.get(resolution, resolution_map["2K"])

        # 参考画像清書モードの場合、YAML + 参照画像を両方使用
        if ref_image_path:
            # 清書モード: YAMLの指示に従いつつ、参照画像の構図を再現して高品質化
            redraw_instruction = f"""【HIGH-QUALITY REDRAW MODE】

You are performing a high-quality redraw task.
Use the YAML instructions below AND the attached reference image together.

## OUTPUT RESOLUTION:
Generate the image at {resolution_instruction}.
This is critical - output must be high resolution.

## CRITICAL RULES:
1. Follow the YAML prompt instructions for content and style
2. Use the reference image as a guide for:
   - Exact composition and layout
   - Character positions and poses
   - Speech bubble placements (if any)
   - Scene framing and camera angle
3. Generate a MORE DETAILED, higher quality version
4. Improve: line art clarity, shading details, background details, facial features
5. Maintain the same scene but with professional-level quality

## IMPORTANT:
- The reference image shows the desired composition - MATCH IT
- The YAML provides detailed instructions - FOLLOW THEM
- Output should look like a polished, professional version of the reference

---
YAML Instructions:
"""
            contents = [redraw_instruction + "\n" + yaml_prompt]
        else:
            # 通常モード: 解像度指示を追加
            resolution_prefix = f"""## OUTPUT RESOLUTION:
Generate the image at {resolution_instruction}.

---
"""
            contents = [resolution_prefix + yaml_prompt]

        # Add reference image first (if in redraw mode)
        if ref_image_path:
            try:
                ref_img = Image.open(ref_image_path)
                contents.append(ref_img)
            except Exception as e:
                print(f"Error loading reference image {ref_image_path}: {e}")

        # Add character reference images
        for img_path in char_image_paths:
            try:
                pil_img = Image.open(img_path)
                contents.append(pil_img)
            except Exception as e:
                print(f"Error loading image {img_path}: {e}")

        # Call API
        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE']
            )
        )

        # Process response
        return process_api_response(response)

    except Exception as e:
        return {
            'success': False,
            'image': None,
            'error': str(e)
        }


def process_api_response(response) -> dict:
    """
    APIレスポンスを処理して画像を抽出

    Args:
        response: Gemini APIレスポンス

    Returns:
        結果を含む辞書:
        {
            'success': bool,
            'image': PIL.Image or None,
            'error': str or None
        }
    """
    try:
        # レスポンス自体がNoneかチェック
        if response is None:
            return {
                'success': False,
                'image': None,
                'error': "APIからレスポンスがありませんでした。"
            }

        # candidatesの存在チェック
        if not hasattr(response, 'candidates') or response.candidates is None:
            return {
                'success': False,
                'image': None,
                'error': "APIレスポンスに候補データがありません。"
            }

        if len(response.candidates) == 0:
            # ブロック理由があれば取得
            block_reason = ""
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                feedback = response.prompt_feedback
                if hasattr(feedback, 'block_reason') and feedback.block_reason:
                    block_reason = f" (理由: {feedback.block_reason})"
            return {
                'success': False,
                'image': None,
                'error': f"APIから候補が返されませんでした。コンテンツがブロックされた可能性があります。{block_reason}"
            }

        candidate = response.candidates[0]

        # finish_reasonのチェック（安全性フィルター等）
        if hasattr(candidate, 'finish_reason') and candidate.finish_reason:
            finish_reason = str(candidate.finish_reason)
            if 'SAFETY' in finish_reason.upper():
                return {
                    'success': False,
                    'image': None,
                    'error': f"安全性フィルターによりコンテンツがブロックされました。プロンプトや参照画像を変更してお試しください。"
                }
            elif 'RECITATION' in finish_reason.upper():
                return {
                    'success': False,
                    'image': None,
                    'error': "著作権関連の問題でコンテンツがブロックされました。"
                }

        # contentの存在チェック
        if not hasattr(candidate, 'content') or candidate.content is None:
            return {
                'success': False,
                'image': None,
                'error': "APIレスポンスにコンテンツがありません。生成に失敗した可能性があります。"
            }

        # partsの存在チェック
        if not hasattr(candidate.content, 'parts') or candidate.content.parts is None:
            return {
                'success': False,
                'image': None,
                'error': "APIレスポンスにパーツデータがありません。画像生成に失敗した可能性があります。"
            }

        if len(candidate.content.parts) == 0:
            return {
                'success': False,
                'image': None,
                'error': "APIレスポンスのパーツが空です。"
            }

        # 画像データを探す
        generated_img_data = None
        text_response = ""

        for part in candidate.content.parts:
            if hasattr(part, 'inline_data') and part.inline_data:
                generated_img_data = part.inline_data.data
                break
            elif hasattr(part, 'text') and part.text:
                text_response = part.text

        if generated_img_data:
            image_bytes = io.BytesIO(generated_img_data)
            image = Image.open(image_bytes)
            return {
                'success': True,
                'image': image,
                'error': None
            }
        else:
            # 画像がなくテキストのみの場合
            error_msg = "APIから画像データが返されませんでした。"
            if text_response:
                # テキストレスポンスがある場合は一部を表示
                preview = text_response[:200] + "..." if len(text_response) > 200 else text_response
                error_msg += f"\n\nAPIからのメッセージ:\n{preview}"
            return {
                'success': False,
                'image': None,
                'error': error_msg
            }

    except AttributeError as e:
        return {
            'success': False,
            'image': None,
            'error': f"レスポンス構造エラー: APIレスポンスの形式が想定と異なります。({e})"
        }
    except Exception as e:
        return {
            'success': False,
            'image': None,
            'error': f"レスポンス処理エラー: {e}"
        }


def validate_api_key(api_key: str) -> bool:
    """
    API Keyの基本的な検証

    Args:
        api_key: 検証するAPI Key

    Returns:
        有効な形式かどうか
    """
    if not api_key:
        return False
    if len(api_key) < 10:
        return False
    return True
