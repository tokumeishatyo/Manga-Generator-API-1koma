#!/bin/bash
# BgRemover ビルドスクリプト
# macOS専用の背景透過ツールをコンパイル

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "BgRemover ビルド開始"
echo "=========================================="

# macOSチェック
if [[ "$(uname)" != "Darwin" ]]; then
    echo "エラー: このツールはmacOS専用です"
    exit 1
fi

# Swiftコンパイラチェック
if ! command -v swiftc &> /dev/null; then
    echo "エラー: swiftcが見つかりません"
    echo "Xcode Command Line Toolsをインストールしてください:"
    echo "  xcode-select --install"
    exit 1
fi

# コンパイル
echo "コンパイル中..."
swiftc -O -o BgRemover BgRemover.swift \
    -framework Foundation \
    -framework AppKit \
    -framework Vision \
    -framework CoreImage

# 実行権限を付与
chmod +x BgRemover

echo ""
echo "=========================================="
echo "ビルド完了!"
echo "=========================================="
echo ""
echo "使用方法:"
echo "  ./BgRemover <入力画像> <出力画像>"
echo ""
echo "例:"
echo "  ./BgRemover photo.jpg transparent.png"
echo ""
