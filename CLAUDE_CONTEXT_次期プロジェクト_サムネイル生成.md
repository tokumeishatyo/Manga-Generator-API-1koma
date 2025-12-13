# YouTubeサムネイル生成ツール - 新規プロジェクト引き継ぎ

## 作成日: 2025-12-12

---

## プロジェクト概要

**目的**: シンガーソングライター「彩瀬こよみ」のYouTube活動用サムネイル・バナー生成ツール

**ターゲットユーザー**: 音楽系YouTuber、VTuber、クリエイター

---

## キャラクター設定

**彩瀬こよみ（あやせ こよみ）**
- 女子高生シンガーソングライター
- 茶色のボブヘア、茶色の瞳
- 紺色セーラー服
- 楽曲例: 「秋風のプロミス」

**参照画像**（前プロジェクトから持ってくる）:
- `彩瀬こよみ.png` - 顔三面図（正面・斜め・横顔）
- `秋風のプロミス.png` - CDジャケット風（夕焼け教室）
- `登校シーン高画質.png` - 桜の校門、漫画風

---

## 実装予定機能

### Phase 1: YouTubeサムネイル
| 機能 | 説明 |
|------|------|
| テンプレート選択 | 新曲発表/カバー/歌ってみた/MV/LIVE告知 |
| キャラ参照画像 | 登録済みキャラを選択 |
| 曲名・テキスト入力 | タイトル、アーティスト名等 |
| 背景生成 | Gemini APIで背景を生成 or プリセット |
| 出力 | 1280×720px (YouTube推奨サイズ) |

### Phase 2: SNSバナー・ヘッダー
| プラットフォーム | サイズ |
|------------------|--------|
| Twitter/X ヘッダー | 1500×500 |
| YouTube チャンネルアート | 2560×1440 |
| ニコニコ ヘッダー | 1280×300 |

### Phase 3: ゲーム向け（将来）
- TRPGキャラカード
- 立ち絵ジェネレーター

---

## 技術スタック

- **Python**: 3.10+
- **GUI**: CustomTkinter
- **API**: google-genai (gemini-2.0-flash-preview-image-generation)
- **画像処理**: Pillow
- **データ**: PyYAML（設定保存用）

---

## 前プロジェクトから流用するファイル

### 必須（コピー推奨）
```
Manga-Generator-API-1koma/
├── app/logic/api_client.py      # Gemini API通信 ★そのまま使える
├── app/requirements.txt         # 依存関係
├── run_app.command              # macOS/Linux起動スクリプト
└── run_app_windows.bat          # Windows起動スクリプト
```

### 参考（必要に応じて）
```
├── app/logic/file_manager.py    # ファイル操作（一部流用）
├── app/ui/base_settings_window.py  # 設定ウィンドウ基底クラス
└── app/constants.py             # 定数定義パターン
```

### 流用しない
```
├── app/ui/scene_builder_window.py
├── app/ui/pose_window.py
├── app/ui/effect_window.py
├── その他漫画生成専用ファイル
└── YAMLテンプレート群
```

---

## 推奨ディレクトリ構成

```
youtube-thumbnail-generator/
├── app/
│   ├── main.py                 # メインアプリケーション
│   ├── constants.py            # 定数定義
│   ├── requirements.txt        # 依存関係
│   ├── logic/
│   │   ├── api_client.py       # Gemini API通信（流用）
│   │   ├── image_composer.py   # 画像合成ロジック（新規）
│   │   └── template_manager.py # テンプレート管理（新規）
│   └── ui/
│       ├── main_window.py      # メインウィンドウ
│       ├── thumbnail_editor.py # サムネイル編集UI
│       └── character_manager.py # キャラ管理UI
├── templates/                   # サムネイルテンプレート定義
│   ├── new_song.yaml           # 新曲発表用
│   ├── cover.yaml              # カバー曲用
│   └── live.yaml               # LIVE告知用
├── characters/                  # キャラクター参照画像
│   └── 彩瀬こよみ/
│       ├── face_sheet.png      # 顔三面図
│       ├── profile.yaml        # キャラ設定
│       └── poses/              # ポーズ別画像
├── output/                      # 生成画像の出力先
├── README.md
├── run_app.command
├── run_app_windows.bat
└── CLAUDE_CONTEXT.md           # 開発コンテキスト
```

---

## サムネイルテンプレート案

### 新曲発表
```
┌─────────────────────────────────────┐
│ [NEW] ○月○日公開                    │
│ ┌─────────┐                        │
│ │キャラ画像│  「曲名」              │
│ │         │                        │
│ │         │  彩瀬こよみ            │
│ └─────────┘                        │
│            ♪ オリジナル曲 ♪        │
└─────────────────────────────────────┘
```

### カバー曲
```
┌─────────────────────────────────────┐
│ COVER                               │
│ ┌─────────┐  「曲名」              │
│ │キャラ画像│                        │
│ │         │  原曲: ○○○            │
│ └─────────┘  歌: 彩瀬こよみ        │
└─────────────────────────────────────┘
```

---

## UI設計案

### メイン画面（3列構成）
```
┌──────────────────────────────────────────────────────────┐
│ 左列（設定）      │ 中列（編集）       │ 右列（プレビュー）│
├───────────────────┼────────────────────┼───────────────────┤
│ ・テンプレート    │ ・テキスト編集     │ ・サムネプレビュー│
│   - 新曲発表      │   - 曲名           │   1280×720       │
│   - カバー        │   - サブタイトル   │                   │
│   - 歌ってみた    │   - 日付           │ [PNG出力]         │
│                   │                    │ [JPEG出力]        │
│ ・キャラクター    │ ・レイアウト調整   │                   │
│   - 彩瀬こよみ    │   - キャラ位置     │                   │
│   - （追加...）   │   - テキスト位置   │                   │
│                   │                    │                   │
│ ・背景            │                    │                   │
│   - AI生成        │                    │                   │
│   - プリセット    │                    │                   │
│   - 画像読込      │                    │                   │
└───────────────────┴────────────────────┴───────────────────┘
```

---

## 開発手順

### Step 1: プロジェクト初期化
```bash
mkdir youtube-thumbnail-generator
cd youtube-thumbnail-generator
git init

# 前プロジェクトから必要ファイルをコピー
cp /path/to/Manga-Generator-API-1koma/app/logic/api_client.py app/logic/
cp /path/to/Manga-Generator-API-1koma/app/requirements.txt app/
cp /path/to/Manga-Generator-API-1koma/run_app.command .
```

### Step 2: 基本UI作成
- main.py（3列レイアウト）
- テンプレート選択UI
- プレビュー表示

### Step 3: 画像合成ロジック
- Pillowでテキスト合成
- キャラ画像配置
- 背景合成

### Step 4: Gemini API連携
- 背景生成
- キャラポーズ生成（オプション）

### Step 5: キャラクター管理
- 参照画像の登録・管理
- プロファイル保存

---

## 前プロジェクトの参照

**リポジトリ**: https://github.com/tokumeishatyo/Manga-Generator-API-1koma

**特に参考になるファイル**:
- `app/logic/api_client.py` - Gemini API通信パターン
- `app/ui/manga_composer_window.py` - 画像合成UIのパターン
- `app/main.py` - 3列レイアウトの実装

---

## 参照画像の場所

前プロジェクトのワークスペースから持ってくる:
```
/workspace/彩瀬こよみ.png          # 顔三面図
/workspace/秋風のプロミス.png      # CDジャケット風
/workspace/登校シーン高画質.png    # 漫画風シーン
```

---

## クイックスタート

新しいClaudeセッションで:

1. このファイルを読む
2. 前プロジェクトからファイルをコピー
3. 基本UIから実装開始

```bash
# 最初のコマンド
cd /path/to/youtube-thumbnail-generator
cat CLAUDE_CONTEXT.md
```

---

## 関連リンク

- **前プロジェクト**: https://github.com/tokumeishatyo/Manga-Generator-API-1koma
- **Google AI Studio**: https://aistudio.google.com/apikey
- **CustomTkinter Docs**: https://customtkinter.tomschimansky.com/
