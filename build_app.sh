#!/bin/bash
# AI創作工房 ビルドスクリプト
# 使用方法: ./build_app.sh

set -e

echo "=========================================="
echo "AI創作工房 ビルド開始"
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
echo "[3/5] 以前のビルドをクリーンアップ..."
rm -rf build dist

# ビルド実行
echo "[4/5] アプリをビルド中..."
pyinstaller manga_generator.spec --noconfirm

# 完了
echo "[5/5] 完了処理..."

# 完了メッセージ
echo ""
echo "=========================================="
echo "ビルド完了!"
echo "=========================================="
echo ""
echo "アプリの場所:"
echo "  dist/AI創作工房.app"
echo ""
echo "アプリケーションフォルダにコピーするには:"
echo "  cp -r \"dist/AI創作工房.app\" /Applications/"
echo ""
echo "Dockに追加するには:"
echo "  アプリを右クリック → オプション → Dockに追加"
echo ""
