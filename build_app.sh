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

# 仮想環境をアクティベート
echo "[1/5] 仮想環境をアクティベート..."
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "エラー: .venvディレクトリが見つかりません"
    echo "先に python3 -m venv .venv を実行してください"
    exit 1
fi

# 依存関係をインストール
echo "[2/5] 依存関係をインストール..."
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
echo "  dist/1コマ漫画生成.app"
echo ""
echo "アプリケーションフォルダにコピーするには:"
echo "  cp -r \"dist/1コマ漫画生成.app\" /Applications/"
echo ""
echo "Dockに追加するには:"
echo "  アプリを右クリック → オプション → Dockに追加"
echo ""
