# -*- coding: utf-8 -*-
"""
ロジックモジュール
UIから分離されたビジネスロジックを提供
"""

from .character import generate_outfit_prompt
from .yaml_generator import (
    generate_illustration_yaml,
    generate_decorative_yaml,
    build_characters_list,
    build_speeches_list,
    build_texts_list,
    build_layout_instruction
)
from .api_client import generate_image_with_api, process_api_response
from .file_manager import (
    load_yaml_file,
    save_yaml_file,
    load_recent_files,
    save_recent_files,
    load_template
)
from .reference_collector import collect_reference_image_paths

__all__ = [
    'generate_outfit_prompt',
    'generate_illustration_yaml',
    'generate_decorative_yaml',
    'build_characters_list',
    'build_speeches_list',
    'build_texts_list',
    'build_layout_instruction',
    'generate_image_with_api',
    'process_api_response',
    'load_yaml_file',
    'save_yaml_file',
    'load_recent_files',
    'save_recent_files',
    'load_template',
    'collect_reference_image_paths'
]
