# 1コマ漫画生成アプリ - 開発コンテキスト

## 最終更新: 2025-12-13 (Step4機能拡張: 表情・ズーム・手足指定)

---

## 次回作業予定

**Step 5: オーラ（エフェクト）付与機能**
- EffectWindow の確認・調整
- オーラエフェクトの生成テスト

---

## プロジェクト概要

**リポジトリ**: https://github.com/tokumeishatyo/Manga-Generator-API-1koma

Google Gemini API (`gemini-3-pro-image-preview`) を使用した1コマ高品質イラスト生成アプリ。
**段階的生成ワークフロー**で、キャラクターデザインからシーン合成まで一貫した制作が可能。

---

## ブランチ構成

| ブランチ | 説明 | 状態 |
|----------|------|------|
| **main** | 段階的生成パターン（推奨） | ✅ 最新 |
| oldpattern | 旧1画面完結パターン（バックアップ） | 凍結 |

---

## 現在の実装状況（mainブランチ）

### 出力モード

| モード | 説明 | 状態 |
|--------|------|------|
| YAML出力 | ブラウザ版Geminiにコピペして使用 | ✅ |
| API画像出力（通常） | アプリ内で直接画像生成 | ✅ |
| API画像出力（清書） | 参考画像を高画質化（詳細設定不要） | ✅ |

### 清書モードの特徴

- **YAML + 参照画像を両方使用**: ブラウザ版で成功したYAMLを読み込む
- **高品質再描画**: YAMLの指示に従いつつ、参照画像の構図を再現してより高品質に再描画
- **フロー**: API出力 → 清書モード → YAML読込 → 参考画像選択 → タイトル入力 → 生成

### 出力タイプ

| 出力タイプ | YAMLテンプレート | UIウィンドウ | 状態 |
|------------|------------------|--------------|------|
| キャラデザイン（全身/顔） | character_basic.yaml | CharacterSheetWindow | ✅ |
| 衣装着用三面図 | character_basic.yaml | OutfitWindow | ✅ |
| ポーズ付きキャラ | character_pose.yaml | PoseWindow | ✅ |
| エフェクト追加 | character_effect.yaml | EffectWindow | ✅ |

### Step3 衣装着用三面図

| モード | 説明 |
|--------|------|
| プリセットから選ぶ | 服装ビルダーで英語プロンプト自動生成 |
| 参考画像から着せる | 別画像の衣装をキャラに着せる（著作権注意） |

**参考画像モード**: 参考画像のパス＋衣装説明テキストを指定

### ポーズプリセット（5種類）

| プリセット | 説明 | Google謹製プロンプト |
|------------|------|---------------------|
| 波動拳（かめはめ波） | 両手を合わせてエネルギー弾 | `Thrusting both palms forward at waist level...` |
| スペシウム光線 | 腕を十字に組んで光線発射 | `Crossing arms in a plus sign shape (+)...` |
| ライダーキック | 空中で飛び蹴り | `Mid-air dynamic flying kick...` |
| 指先ビーム | 人差し指から光線 | `Pointing index finger forward...` |
| 坐禅（瞑想） | 結跏趺坐で瞑想 | `Sitting cross-legged in lotus position...` |

※プリセット選択で自動入力、プロンプトはcharacter_pose.yaml準拠

### Step4 追加機能（2025-12-13実装）

| 機能 | 選択肢 | 備考 |
|------|--------|------|
| **表情** | 無表情/笑顔/怒り/泣き/恥じらい | 補足テキストで「苦笑い」等も指定可 |
| **向き拡張** | 正面/→右向き/←左向き/↗斜め右/↖斜め左/背面 | 三面図の角度に対応 |
| **ポーズ拡張** | 立ち/座り/しゃがみ/ジャンプ/走り/歩き/瞑想/祈り/腕組み等 | バトル系＋基本動作 |
| **ズーム拡張** | 全身/上半身/バストアップ/胸から上/胴体中ほどから上/みぞおちから上/顔アップ | 「バストアップ」→Medium Close Upに変換（セーフティ対策） |
| **手足の指定** | 使用する手・足（指定なし/右/左/両方） | 詳細テキストで「右手が上」「左足が前」等も指定可 |
| **背景透過** | チェックボックス | 合成用に透過PNG出力 |

**ズーム設定のTips**（README記載済み）:
- 攻撃系ポーズ + 顔アップ → 実質バストアップになる（腕を含めるため）
- 座りポーズ + ズーム → 効きにくい（体がコンパクトなため）

| 出力タイプ | YAMLテンプレート | UIウィンドウ | 状態 |
|------------|------------------|--------------|------|
| 背景のみ生成 | background_template.yaml | BackgroundWindow | ✅ |
| 装飾テキスト | ui_text_overlay.yaml | DecorativeTextWindow | ✅ |

### 装飾テキスト（4タイプ）

| タイプ | 説明 | 主な設定 |
|--------|------|----------|
| 技名テロップ | 必殺技名表示 | フォント/サイズ/グラデ色/縁取り/発光 |
| 決め台詞 | キャラの派手なセリフ | 表現タイプ/配色/回転/変形 |
| キャラ名プレート | 名前表示 | デザイン/回転 |
| メッセージウィンドウ | ゲーム風セリフ枠 | 3モード対応 |

**メッセージウィンドウの3モード:**
- フルスペック（名前+顔+セリフ）: スパロボ風
- 顔アイコンのみ: 顔だけ単体出力
- セリフのみ: テキストウィンドウのみ

### シーンビルダー

| 合成タイプ | YAMLテンプレート | 用途 |
|------------|------------------|------|
| バトルシーン | scene_composite.yaml | 2キャラ対戦 |
| ストーリーシーン | story_scene_composite.yaml | 会話/日常 |
| ボスレイド | boss_raid_composition.yaml | 巨大ボス戦 |

**装飾テキスト配置機能:**
- TextOverlayPlacementWindow
- 最大11箇所配置可能
- 絶対位置: 9箇所（上部/中央/下部 × 左/中央/右）
- キャラ相対位置: 2箇所（左キャラ付近/右キャラ付近）
- 同一位置への重複配置防止

### その他の機能

| 機能 | 説明 | 状態 |
|------|------|------|
| タイトル必須 | ファイル名生成に使用 | ✅ |
| 画像へのタイトル合成 | チェックボックスで有効化（PIL使用） | ✅ |
| API生成画像の命名 | 「タイトル_API.png」形式 | ✅ |
| 経過時間表示 | API生成中に秒数表示 | ✅ |
| APIキー保持 | リセット/モード切替で消えない、×ボタンで明示的クリア | ✅ |
| リセットボタン | 全入力をクリア（APIキー除く） | ✅ |
| PyInstallerビルド | スタンドアロンmacOSアプリ生成 | ✅ |

### 未実装（残課題）

| 機能 | YAMLテンプレート | 優先度 |
|------|------------------|--------|
| 多人数フォーメーション | multi_character_fomation.yaml | 低（必要時に実装） |

---

## ファイル構成

```
/workspace/
├── app/
│   ├── main.py                          # メインアプリケーション
│   ├── constants.py                     # 定数定義
│   ├── requirements.txt                 # 依存ライブラリ
│   ├── logic/
│   │   ├── __init__.py
│   │   ├── api_client.py                # Gemini API通信
│   │   ├── yaml_generator.py            # YAML生成ロジック
│   │   ├── file_manager.py              # ファイル操作
│   │   └── character.py                 # キャラクター処理
│   └── ui/
│       ├── __init__.py
│       ├── base_settings_window.py      # 設定ウィンドウ基底クラス
│       ├── character_sheet_window.py    # キャラデザイン設定
│       ├── pose_window.py               # ポーズ設定
│       ├── effect_window.py             # エフェクト設定
│       ├── background_window.py         # 背景設定
│       ├── decorative_text_window.py    # 装飾テキスト設定（4タイプ）
│       ├── text_overlay_placement_window.py  # テキスト配置設定（11箇所）
│       └── scene_builder_window.py      # シーンビルダー（3タイプ）
├── YAMLテンプレート（/workspace/直下）
│   ├── character_basic.yaml             # キャラデザイン用
│   ├── character_pose.yaml              # ポーズ付きキャラ用
│   ├── character_effect.yaml            # エフェクト追加用
│   ├── background_template.yaml         # 背景生成用
│   ├── ui_text_overlay.yaml             # 装飾テキスト用
│   ├── scene_composite.yaml             # バトルシーン用
│   ├── story_scene_composite.yaml       # ストーリーシーン用
│   ├── boss_raid_composition.yaml       # ボスレイド用
│   └── multi_character_fomation.yaml    # 多人数フォーメーション用（未実装）
├── run_app.command                      # macOS/Linux起動スクリプト
├── run_app_windows.bat                  # Windows起動スクリプト
├── build_app.sh                         # PyInstallerビルドスクリプト
├── manga_generator.spec                 # PyInstaller設定ファイル
├── README.md                            # ユーザー向けドキュメント
├── CLAUDE_CONTEXT_1コマアプリ設計.md    # このファイル
└── CLAUDE_CONTEXT_API版.md              # API版についての補足
```

---

## 主要ファイルの役割

### app/main.py
- CustomTkinterによるGUI
- 3列レイアウト（左:出力タイプ選択、中央:YAMLプレビュー、右:画像プレビュー）
- 出力タイプ別の設定ウィンドウ起動
- YAML生成・API呼び出し

### app/ui/decorative_text_window.py
- 装飾テキスト4タイプの設定UI
- 技名テロップ/決め台詞/キャラ名プレート/メッセージウィンドウ
- メッセージウィンドウは3モード対応

### app/ui/text_overlay_placement_window.py
- シーン合成時の装飾テキスト配置UI
- 最大11箇所（絶対位置9 + キャラ相対2）
- 位置の重複防止機能

### app/ui/scene_builder_window.py
- シーン合成UI（バトル/ストーリー/ボスレイド）
- 装飾テキスト配置ボタンで配置ウィンドウ起動
- YAML生成してメインウィンドウにコールバック

### app/ui/base_settings_window.py
- 設定ウィンドウの基底クラス
- 共通のOK/キャンセルボタン、コールバック処理

---

## 技術スタック

- **Python**: 3.10+
- **GUI**: CustomTkinter
- **API**: google-genai (gemini-3-pro-image-preview)
- **画像処理**: Pillow（タイトル合成、日本語フォント対応）
- **データ**: PyYAML
- **クリップボード**: tkinter組み込み機能（macOSスタンドアロン対応）
- **ビルド**: PyInstaller（オプション）

---

## 開発時の注意点

### 1. UIパターン
- 各出力タイプは専用の設定ウィンドウ（CTkToplevel）を持つ
- 設定完了後、コールバックでメインウィンドウにデータを渡す
- 基底クラス `BaseSettingsWindow` を継承

### 2. YAML生成
- 各出力タイプごとに `_generate_xxx_yaml()` メソッドを持つ
- ファイルパスはファイル名のみ出力（ブラウザ版との互換性）
- `title_overlay`セクションはチェックボックスがオンの場合のみ出力

### 3. 定数管理
- 日本語→英語の変換辞書は各UIファイル内に定義
- 共通定数は `constants.py` に集約

### 4. シーンビルダー
- 3つの合成タイプを1つのウィンドウで切り替え
- 装飾テキスト配置は別ウィンドウ（TextOverlayPlacementWindow）

### 5. API関連
- **清書モード**: YAML + 参照画像を両方使用して高品質再描画
  - YAMLの読込が必須（ブラウザ版で成功したYAMLを使用）
  - 詳細設定ボタンは無効化
- APIキーはリセット/モード切替で消えない（×ボタンで明示的クリア）
- 生成中は経過時間を表示（`_update_progress_display`）
- API生成画像は「タイトル_API」形式でファイル名提案

### 6. 4コマ漫画
- YAML冒頭に**画像生成指示文を自動追加**（日英両方）
- ブラウザ版Geminiにコピペするだけで画像生成が可能
- キャラクター参照画像と一緒に送信する必要あり

### 7. スタンドアロンアプリ
- クリップボードはtkinter組み込み機能を使用（pyperclipはmacOSアプリで動作しない）
- PyInstallerビルドは`build_app.sh`で実行

---

## よくある作業

### アプリ起動
```bash
cd /workspace
./run_app.command  # または python app/main.py
```

### Git操作
```bash
git add .
git commit -m "変更内容"
git push origin main
```

### 構文チェック
```bash
python -m py_compile app/main.py app/ui/*.py
```

### スタンドアロンアプリのビルド（macOS）
```bash
./build_app.sh
# 出力: dist/1コマ漫画生成.app
```

---

## 引き継ぎ時のクイックスタート

新しいClaudeセッションで作業を再開する場合:

1. このファイルを読む: `Read /workspace/CLAUDE_CONTEXT_1コマアプリ設計.md`
2. 現在の状態確認: `git status` と `git log --oneline -5`
3. 主要ファイル:
   - メイン: `app/main.py`
   - ポーズ設定: `app/ui/pose_window.py` ← **Step4の中心**
   - エフェクト設定: `app/ui/effect_window.py` ← **次回作業対象**
   - 衣装設定: `app/ui/outfit_window.py`
   - 装飾テキスト: `app/ui/decorative_text_window.py`
   - シーンビルダー: `app/ui/scene_builder_window.py`
   - テキスト配置: `app/ui/text_overlay_placement_window.py`
4. YAMLテンプレート: `/workspace/*.yaml`
5. 定数定義: `app/constants.py`（CHARACTER_FACING, CHARACTER_POSES等）

---

## 関連リンク

- **GitHub**: https://github.com/tokumeishatyo/Manga-Generator-API-1koma
- **Qiita記事**: https://qiita.com/KLaboratory/items/77b81226d1db8089c7fc
- **Google AI Studio**: https://aistudio.google.com/apikey
