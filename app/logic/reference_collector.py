# -*- coding: utf-8 -*-
"""
参照画像収集モジュール
API画像生成時に使用する参照画像のパスを収集
"""

import os


def collect_reference_image_paths(settings: dict) -> list:
    """
    設定データから参照画像のパスを収集

    Args:
        settings: current_settingsの辞書

    Returns:
        参照画像パスのリスト
    """
    paths = []
    if not settings:
        return paths

    # 各出力タイプに応じた参照画像パスを収集
    step_type = settings.get('step_type', '')

    # Step2: 素体三面図 - 顔三面図を参照
    if step_type == 'step2_body':
        face_path = settings.get('face_sheet_path', '')
        if face_path and os.path.exists(face_path):
            paths.append(face_path)

    # Step3: 衣装着用 - 素体三面図を参照（+ 参考衣装画像）
    elif step_type == 'step3_outfit':
        body_path = settings.get('body_sheet_path', '')
        if body_path and os.path.exists(body_path):
            paths.append(body_path)
        # 参考画像モードの場合、参考衣装画像も追加
        if settings.get('outfit_source') == 'reference':
            ref_path = settings.get('reference_image_path', '')
            if ref_path and os.path.exists(ref_path):
                paths.append(ref_path)

    # Step4: ポーズ - キャラクター画像を参照（+ ポーズ参考画像）
    elif 'image_path' in settings:  # pose_window
        img_path = settings.get('image_path', '')
        if img_path and os.path.exists(img_path):
            paths.append(img_path)
        # ポーズキャプチャモードの場合、ポーズ参考画像も追加
        if settings.get('pose_capture_enabled'):
            pose_ref = settings.get('pose_reference_image', '')
            if pose_ref and os.path.exists(pose_ref):
                paths.append(pose_ref)

    # スタイル変換 - 変換元画像を参照
    elif step_type == 'style_transform':
        source_path = settings.get('source_image_path', '')
        if source_path and os.path.exists(source_path):
            paths.append(source_path)

    # インフォグラフィック - メイン画像とおまけ画像を参照
    elif step_type == 'infographic':
        main_path = settings.get('main_image_path', '')
        if main_path and os.path.exists(main_path):
            paths.append(main_path)
        bonus_path = settings.get('bonus_image_path', '')
        if bonus_path and os.path.exists(bonus_path):
            paths.append(bonus_path)

    return paths
