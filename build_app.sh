#!/bin/bash
# 1コマ漫画生成アプリ ビルドスクリプト
# 使用方法: ./build_app.sh

set -e

echo "=========================================="
echo "1コマ漫画生成アプリ ビルド開始"
echo "=========================================="

# スクリプトのディレクトリを取得
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Python 3.13のパスを検出
PYTHON313=""
if [ -x "/opt/homebrew/opt/python@3.13/bin/python3.13" ]; then
    PYTHON313="/opt/homebrew/opt/python@3.13/bin/python3.13"
elif [ -x "/usr/local/opt/python@3.13/bin/python3.13" ]; then
    PYTHON313="/usr/local/opt/python@3.13/bin/python3.13"
elif command -v python3.13 &> /dev/null; then
    PYTHON313="python3.13"
else
    echo "エラー: Python 3.13が見つかりません"
    echo "brew install python@3.13 でインストールしてください"
    exit 1
fi
echo "Python 3.13を使用: $PYTHON313"

# 仮想環境を削除して再作成（クリーンビルド）
echo "[1/5] 仮想環境を作成..."
if [ -d ".venv" ]; then
    echo "      既存の.venvを削除中..."
    rm -rf .venv
fi
$PYTHON313 -m venv .venv
source .venv/bin/activate

# 依存関係をインストール
echo "[2/5] 依存関係をインストール..."
pip install --upgrade pip --quiet
pip install -r app/requirements.txt --quiet

# PyInstallerがインストールされているか確認
if ! command -v pyinstaller &> /dev/null; then
    echo "[2/5] PyInstallerをインストール..."
    pip install pyinstaller
fi

# 以前のビルドをクリーンアップ
echo "[3/6] 以前のビルドをクリーンアップ..."
rm -rf build dist

# Swiftツールをビルド（オプション）
echo "[4/6] Swiftツールをビルド..."
if [ -d "tools/BgRemover" ]; then
    cd tools/BgRemover
    if command -v swiftc &> /dev/null; then
        echo "      BgRemoverをコンパイル中..."
        swiftc -O -o BgRemover BgRemover.swift \
            -framework Foundation \
            -framework AppKit \
            -framework Vision \
            -framework CoreImage \
            2>/dev/null && echo "      BgRemover ビルド完了" || echo "      警告: BgRemoverのビルドをスキップ"
    else
        echo "      警告: swiftcが見つかりません。BgRemoverをスキップ。"
    fi
    cd "$SCRIPT_DIR"
else
    echo "      警告: tools/BgRemoverが見つかりません"
fi

# ビルド実行
echo "[5/6] アプリをビルド中..."
pyinstaller manga_generator.spec --noconfirm

# Swiftツールをdistにコピー
echo "[6/6] 完了処理..."
if [ -f "tools/BgRemover/BgRemover" ]; then
    mkdir -p dist/tools/BgRemover
    cp tools/BgRemover/BgRemover dist/tools/BgRemover/
    echo "      BgRemoverをdistにコピーしました"
fi

# 完了メッセージ
echo ""
echo "=========================================="
echo "ビルド完了!"
echo "=========================================="
echo ""
echo "アプリの場所:"
echo "  dist/1コマ漫画生成.app"
echo ""
echo "アプリケーションフォルダにコピーするには:"
echo "  cp -r \"dist/1コマ漫画生成.app\" /Applications/"
echo ""
echo "Dockに追加するには:"
echo "  アプリを右クリック → オプション → Dockに追加"
echo ""
