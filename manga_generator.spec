# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for 漫画生成アプリ（1コマ・4コマ対応）
"""

import os
import sys

block_cipher = None

# アプリのベースパス
base_path = os.path.dirname(os.path.abspath(SPEC))

# データファイル（YAMLテンプレートなど）
datas = [
    (os.path.join(base_path, 'template.yaml'), '.'),
    (os.path.join(base_path, 'character_basic.yaml'), '.'),
    (os.path.join(base_path, 'character_pose.yaml'), '.'),
    (os.path.join(base_path, 'character_effect.yaml'), '.'),
    (os.path.join(base_path, 'background_template.yaml'), '.'),
    (os.path.join(base_path, 'ui_text_overlay.yaml'), '.'),
    (os.path.join(base_path, 'scene_composite.yaml'), '.'),
    (os.path.join(base_path, 'story_scene_composite.yaml'), '.'),
    (os.path.join(base_path, 'boss_raid_composition.yaml'), '.'),
    (os.path.join(base_path, 'multi_character_fomation.yaml'), '.'),
    (os.path.join(base_path, 'four_panel_manga.yaml'), '.'),
]

# 存在するファイルのみを含める
datas = [(src, dst) for src, dst in datas if os.path.exists(src)]

# 隠れた依存関係
hiddenimports = [
    'PIL._tkinter_finder',
    'PIL.Image',
    'PIL.ImageDraw',
    'PIL.ImageFont',
    'PIL.ImageTk',
    'customtkinter',
    'yaml',
    'tkinter',
    'tkinter.filedialog',
    'tkinter.messagebox',
]

# Google AI関連（インストールされている場合のみ）
try:
    import google.generativeai
    hiddenimports.extend([
        'google.generativeai',
        'google.ai.generativelanguage',
        'google.api_core',
        'google.auth',
        'google.protobuf',
    ])
except ImportError:
    pass

a = Analysis(
    [os.path.join(base_path, 'app', 'main.py')],
    pathex=[base_path, os.path.join(base_path, 'app')],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MangaGenerator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUIアプリなのでコンソール非表示
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MangaGenerator',
)

# macOS用 .app バンドル
app = BUNDLE(
    coll,
    name='漫画生成.app',
    icon=None,  # アイコンがある場合はここにパスを指定
    bundle_identifier='com.nanobananapro.mangagenerator',
    info_plist={
        'CFBundleName': '漫画生成',
        'CFBundleDisplayName': '漫画生成',
        'CFBundleVersion': '2.0.0',
        'CFBundleShortVersionString': '2.0.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.13.0',
    },
)
