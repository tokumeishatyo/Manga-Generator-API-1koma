# Gemini APIで高品質1コマイラストを量産！キャラクター一貫性を保つツールを作った

## はじめに

以前、[NanoBanana Pro](https://qiita.com/KLaboratory/items/a7dfdd615191239b5336)や[4コマ漫画プロンプト作成ツール](https://qiita.com/KLaboratory/items/xxxxx)を紹介しました。

今回はその発展版として、**Gemini APIを直接叩いて高品質な1コマイラストを生成するツール**を開発しました。

特徴は**キャラクター参照画像**を使って顔や外見の一貫性を保てること。同じキャラクターで様々なシチュエーションのイラストを量産できます。

:::note alert
**注意**
本記事で紹介するツールは、Gemini APIを使用します。**API使用料が発生する**前提でお読みください。
:::

## こんな人におすすめ

- キャラクターの一貫性を保ちながらイラストを量産したい人
- Geminiブラウザ版では物足りない、API版の高品質出力が欲しい人
- キャラクター三面図（設定画）を効率的に作りたい人
- プログラミング知識なしでGemini APIを試したい人
- 下書き→清書のワークフローを確立したい人

## 作ったもの

**1コマ漫画生成アプリ (Manga-Generator-API-1koma)**

Python + CustomTkinter で作成した、Gemini API直結の画像生成GUIアプリです。

<!-- ここにスクリーンショットを挿入 -->

**GitHubリポジトリ**: https://github.com/tokumeishatyo/Manga-Generator-API-1koma

## 主な機能

### 基本機能

| 機能 | 説明 |
|------|------|
| キャラクター最大5人 | 複数キャラの同時登場に対応 |
| キャラクター参照画像 | 画像を添付して顔・外見の一貫性を保持 |
| 服装ビルダー | ドロップダウンで服装を選ぶだけで英語プロンプトを自動生成 |
| セリフ・ナレーション | 吹き出しとナレーションテキストの配置 |
| YAML入出力 | プロンプトの保存・読み込み・再編集 |

### 出力モード

| モード | 用途 |
|--------|------|
| イラスト生成 | 通常の1コマイラスト |
| 全身三面図 | キャラ設定画（フロント・サイド・バック） |
| 顔三面図 | 表情設定画（正面・斜め・横顔） |
| 背景生成 | キャラなしの背景のみ |
| 装飾テキスト | タイトルロゴなど |

### カラーモード・スタイル

- **カラーモード**: フルカラー / モノクロ / セピア / 二色刷り（赤×黒など）
- **出力スタイル**: 漫画風、アニメ風、劇画風、水彩風、アメコミ風、少女漫画風、少年漫画風、実写風、ドット絵風、SDキャラ風...

### 参考画像清書モード

これが今回の目玉機能です。

**ブラウザ版Geminiで下書き → API版で清書**というワークフローを実現します。

1. ブラウザ版Geminiでキャラ・構図を試行錯誤して下書きを生成
2. アプリの「参考画像清書」モードで、下書き画像を参考画像に指定
3. キャラクター参照画像を設定してAPI版で清書

ブラウザ版の手軽さとAPI版の高品質を両立できます。

## 技術スタック

| 項目 | 内容 |
|------|------|
| 言語 | Python 3.10+ |
| GUI | CustomTkinter |
| AI API | google-genai (`gemini-3-pro-image-preview`) |
| データ形式 | YAML (PyYAML) |
| 画像処理 | Pillow |
| クリップボード | pyperclip |

## インストールと起動

### 必要要件
- Python 3.10以上
- macOS / Windows / Linux
- Google AI API Key（[Google AI Studio](https://aistudio.google.com/apikey)で取得）

### 起動方法

**macOS / Linux**
```bash
git clone https://github.com/tokumeishatyo/Manga-Generator-API-1koma.git
cd Manga-Generator-API-1koma
./run_app.command
```

**Windows**
```
run_app_windows.bat をダブルクリック
```

初回起動時に自動的に仮想環境が作成され、必要なライブラリがインストールされます。

## 使い方

### 基本的な流れ

1. **API Key入力**: Google AI API Keyを入力
2. **出力モード選択**: イラスト生成 / 三面図 / 背景 から選択
3. **キャラクター設定**:
   - 名前を入力
   - 「画像あり」で参照画像のパスを指定
   - 服装ビルダーで服装を設定
4. **シーン説明**: 生成したいシーンを詳しく記述
5. **Generate**: ボタンをクリックして生成
6. **画像保存**: 生成された画像を保存

### 三面図の作成

キャラクター設定画を作るのに便利な機能です。

**全身三面図**
- 正面・側面・背面の3方向から描いた設定画
- シーン説明は空欄でOK（デフォルト：無表情・気をつけの姿勢）
- 服装ビルダーで「モデル用」カテゴリを選ぶと、白レオタードなど設定画向けの衣装を選択可能

**顔三面図**
- 正面・斜め・横顔の3方向から描いた設定画
- 全身画像を参照しても顔のみを生成
- プロンプトが強化されており、全身が生成されにくい

### 参考画像清書モード

下書き→清書ワークフローの実現方法：

1. **準備**: ブラウザ版Geminiでキャラ・構図を試行錯誤して下書きを生成・保存
2. **アプリで「参考画像清書」を選択**
3. **参考画像に下書き画像のパスを指定**
4. **キャラクター参照画像を設定**（顔の一貫性を保持）
5. **Generate**で清書版を生成

構図は下書きを参考にしつつ、キャラクターの顔は参照画像から忠実に再現されます。

## 服装ビルダー

AIが理解しやすい英語プロンプトを自動生成する機能です。

### 選択項目

| 項目 | 選択肢例 |
|------|----------|
| カテゴリ | モデル用 / スーツ / 水着 / カジュアル / 制服 / ドレス / スポーツ / 和服 / 作業着 |
| 形状 | カテゴリに応じて変化（例：水着→三角ビキニ、ホルターネック等） |
| 色 | 黒 / 白 / 紺 / 赤 / ピンク / 青 / 緑 / 黄 / 紫 / ゴールド / シルバー... |
| 柄 | 無地 / ストライプ / チェック / 花柄 / ドット / レース / 迷彩... |
| スタイル | 大人っぽい / 可愛い / セクシー / クール / 清楚 / ゴージャス... |

### 使用例

**水着 + 三角ビキニ + 黒 + 無地 + セクシー** を選択すると：

```
black, solid color, plain, triangle bikini, sexy, alluring
```

このプロンプトが自動生成されてYAMLに組み込まれます。日本語で選ぶだけでOK！

## 生成されるYAMLの例

```yaml
color_mode: fullcolor
aspect_ratio: 16:9
output_type: illustration
output_style: anime style, vibrant colors, expressive
scene:
  prompt: A girl walking on a beach at sunset, waves gently lapping at her feet
  speeches:
    - character: 彩瀬
      content: 夕日がきれい
      position: left
characters:
  - name: 彩瀬
    reference: see attached image
    description: outfit: black, solid color, plain, triangle bikini, sexy, alluring
layout_instruction: color tone:  style: anime style, vibrant colors, expressive Generate single panel illustration. Faithfully reproduce each character's appearance from attached images and descriptions. Display dialogue in speech bubbles.
```

## 工夫したポイント

### キャラクターの一貫性

画像生成AIの最大の課題「キャラクターの一貫性」に対応：

- **参照画像対応**: キャラクター画像を添付して顔を再現
- **服装ビルダー**: 毎回同じ服装を簡単に指定
- **三面図生成**: 設定画を作ってから本編制作という流れが可能
- **参考画像清書**: 下書きの構図を維持しつつ顔を統一

### 英語YAMLで精度向上

内部的にYAMLは全て英語で生成されます。日本語UIで入力しても、AIに渡るプロンプトは英語化されているため、意図が正確に伝わります。

### 顔三面図の改善

初期バージョンでは、全身参照画像を使うと顔三面図でも全身が生成される問題がありました。プロンプトを強化して「顔と首のみ、絶対に体や全身を描かない」という指示を徹底することで解決しています。

### YAML読み込み時の設定復元

保存したYAMLを読み込むと、服装設定やアスペクト比など全ての設定がUIに復元されます。過去のプロンプトを微調整して再生成する際に便利です。

## ブラウザ版 vs API版

| 項目 | ブラウザ版Gemini | API版（本ツール） |
|------|------------------|-------------------|
| 手軽さ | ◎ すぐ試せる | △ API Key必要 |
| 料金 | 無料枠あり | 従量課金 |
| 画質 | ○ | ◎ より高品質 |
| キャラ一貫性 | △ | ◎ 参照画像対応 |
| バッチ処理 | × | ○ 将来的に対応可能 |

**おすすめの使い分け**：
- **ブラウザ版**: 構図やキャラデザインの試行錯誤
- **API版**: 本番用の高品質イラスト生成

「参考画像清書」モードを使えば、両者のいいとこ取りができます。

## 今後の展望

- キャラクタープリセット保存機能
- バッチ生成（複数シーンを一括生成）
- 生成履歴の管理
- より細かいレイアウト指定

## おわりに

Gemini APIの画像生成能力は本当に素晴らしいです。特に「参照画像を使ったキャラクターの再現」は、漫画やイラスト制作のワークフローを大きく変える可能性があります。

このツールが、皆さんの創作活動の助けになれば幸いです。ぜひ試してみてください！

---

**GitHub**: https://github.com/tokumeishatyo/Manga-Generator-API-1koma

## 関連記事

- [NanoBanana Pro - Gemini画像生成デスクトップアプリ](https://qiita.com/KLaboratory/items/a7dfdd615191239b5336)
- [Manga-Generator - 4コマ漫画プロンプト作成ツール](https://qiita.com/KLaboratory/items/xxxxx)
