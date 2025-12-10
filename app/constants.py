# -*- coding: utf-8 -*-
"""
定数定義モジュール
1コマ漫画生成アプリで使用する定数を定義
"""

# 基本設定
MAX_SPEECH_LENGTH = 30
MAX_RECENT_FILES = 5
MAX_CHARACTERS = 5

# カラーモード定義
COLOR_MODES = {
    "フルカラー": ("fullcolor", ""),
    "モノクロ": ("monochrome", "monochrome, black and white, grayscale"),
    "セピア色": ("sepia", "sepia tone, vintage brown tint, old photograph style"),
    "二色刷り": ("duotone", "")  # 色選択と組み合わせる
}

# 二色刷りの色の組み合わせ
DUOTONE_COLORS = {
    "赤×黒": ("red and black duotone, two-color print, manga style", "red_black"),
    "青×黒": ("blue and black duotone, two-color print", "blue_black"),
    "緑×黒": ("green and black duotone, two-color print", "green_black"),
    "紫×黒": ("purple and black duotone, two-color print", "purple_black"),
    "オレンジ×黒": ("orange and black duotone, two-color print", "orange_black"),
}

# 出力タイプ定義
OUTPUT_TYPES = {
    "イラスト生成": "illustration",
    "全身三面図": "fullbody_sheet",
    "顔三面図": "face_sheet",
    "背景生成": "background",
    "装飾テキスト": "decorative_text"
}

# 装飾テキストスタイル定義
DECORATIVE_TEXT_STYLES = {
    "タイトル": "title",
    "サブタイトル": "subtitle",
    "クレジット": "credit",
    "キャッチコピー": "catchphrase",
    "ロゴ風": "logo"
}

# キャラクターシート用プロンプト
CHARACTER_SHEET_PROMPTS = {
    "fullbody_sheet": "character reference sheet, full body, three views (front view, side view, back view), standing at attention pose, arms at sides, white background, clean lines, consistent character design, model sheet",
    "face_sheet": "character face reference sheet, three views (front view, 3/4 view, side profile), neutral expression, emotionless, white background, clean lines, consistent facial features, expression sheet"
}

# 三面図用デフォルトシーン説明
CHARACTER_SHEET_DEFAULT_SCENES = {
    "fullbody_sheet": "neutral expression, standing at attention pose, arms at sides",
    "face_sheet": "neutral expression, emotionless"
}

# 背景生成用プロンプト
BACKGROUND_PROMPT = "background only, no characters, no people, detailed environment, scenic"

# 出力スタイル定義
OUTPUT_STYLES = {
    "おまかせ": "",
    "シンプルな漫画風": "simple manga style, clean lines, cel shading",
    "精緻な劇画風": "detailed gekiga style, realistic shading, dramatic",
    "アニメ風": "anime style, vibrant colors, expressive",
    "水彩イラスト風": "watercolor illustration style, soft colors",
    "アメコミ風": "american comic style, bold colors, dynamic",
    "少女漫画風": "shoujo manga style, sparkles, soft atmosphere",
    "少年漫画風": "shounen manga style, dynamic action, bold lines",
    "実写風": "photorealistic, realistic, photograph style, high detail",
    "ドット絵風": "pixel art style, 16-bit, retro game graphics, pixelated",
    "ゲーム画面風": "video game screenshot style, game UI aesthetic, digital art",
    "格闘ゲーム風": "fighting game style, dynamic action pose, dramatic lighting, energy effects",
    "RPGバトル風": "JRPG battle scene style, turn-based RPG aesthetic, fantasy game art",
    "SDキャラ風": "super deformed, chibi style, 2-head tall proportion, cute, big head small body",
    "二頭身デフォルメ": "chibi character, 2-head proportion, deformed cute style, large head, small body"
}

# テキスト位置定義
TEXT_POSITIONS = {
    "左上": "top-left",
    "中央上": "top-center",
    "右上": "top-right",
    "左中": "middle-left",
    "中央": "center",
    "右中": "middle-right",
    "左下": "bottom-left",
    "中央下": "bottom-center",
    "右下": "bottom-right"
}

# アスペクト比定義
ASPECT_RATIOS = {
    "1:1": "1:1",
    "16:9": "16:9",
    "9:16": "9:16",
    "4:3": "4:3",
    "3:4": "3:4"
}

# 服装データ定義
OUTFIT_DATA = {
    "カテゴリ": {
        "おまかせ": "",
        "モデル用": "simple clothing for character model sheet",
        "スーツ": "business suit",
        "水着": "swimsuit",
        "カジュアル": "casual wear",
        "制服": "uniform",
        "ドレス/フォーマル": "formal wear",
        "スポーツ": "sportswear",
        "和服": "japanese traditional clothing",
        "作業着/職業服": "work uniform"
    },
    "形状": {
        "モデル用": {
            "おまかせ": "",
            "白レオタード": "white leotard, simple, tight-fitting, full body visible",
            "グレーレオタード": "gray leotard, simple, tight-fitting, full body visible",
            "黒レオタード": "black leotard, simple, tight-fitting, full body visible",
            "白下着": "white underwear, simple bra and panties, minimal clothing",
            "Tシャツ+短パン": "simple gray t-shirt and shorts, casual, body shape visible",
            "タンクトップ+短パン": "white tank top and shorts, simple, body shape visible"
        },
        "スーツ": {
            "おまかせ": "",
            "パンツスタイル": "pant suit, trousers",
            "タイトスカート": "pencil skirt",
            "プリーツスカート": "pleated skirt",
            "ミニスカート": "mini skirt suit",
            "スリーピース": "three-piece suit, vest",
            "ダブルスーツ": "double-breasted suit",
            "タキシード": "tuxedo, formal suit"
        },
        "水着": {
            "おまかせ": "",
            "三角ビキニ": "triangle bikini",
            "ホルターネック": "halter neck bikini",
            "バンドゥ": "bandeau bikini",
            "ワンピース": "one-piece swimsuit",
            "ハイレグ": "high-leg swimsuit",
            "パレオ付き": "bikini with pareo",
            "サーフパンツ": "surf shorts, board shorts",
            "競泳パンツ": "racing briefs, speedo"
        },
        "カジュアル": {
            "おまかせ": "",
            "Tシャツ+デニム": "t-shirt and denim jeans",
            "ワンピース": "casual dress",
            "ブラウス+スカート": "blouse and skirt",
            "パーカー": "hoodie",
            "カーディガン": "cardigan outfit",
            "シャツ+チノパン": "button-down shirt and chinos",
            "ポロシャツ": "polo shirt",
            "レザージャケット": "leather jacket"
        },
        "制服": {
            "おまかせ": "",
            "セーラー服": "sailor uniform",
            "ブレザー": "blazer uniform",
            "メイド服": "maid uniform",
            "ナース服": "nurse uniform",
            "OL制服": "office lady uniform",
            "学ラン": "gakuran, japanese male school uniform",
            "詰襟": "standing collar uniform",
            "警察官": "police uniform",
            "軍服": "military uniform"
        },
        "ドレス/フォーマル": {
            "おまかせ": "",
            "イブニングドレス": "evening gown",
            "カクテルドレス": "cocktail dress",
            "ウェディングドレス": "wedding dress",
            "チャイナドレス": "chinese dress, cheongsam",
            "サマードレス": "summer dress",
            "タキシード": "tuxedo",
            "モーニング": "morning coat, formal suit",
            "燕尾服": "tailcoat, white tie"
        },
        "スポーツ": {
            "おまかせ": "",
            "テニスウェア": "tennis wear",
            "体操服": "gym uniform",
            "レオタード": "leotard",
            "ヨガウェア": "yoga wear",
            "競泳水着": "racing swimsuit",
            "サッカーユニフォーム": "soccer jersey, football kit",
            "野球ユニフォーム": "baseball uniform",
            "バスケユニフォーム": "basketball jersey",
            "柔道着": "judo gi, martial arts uniform"
        },
        "和服": {
            "おまかせ": "",
            "着物": "kimono",
            "浴衣": "yukata",
            "振袖": "furisode",
            "巫女服": "miko outfit, shrine maiden",
            "袴": "hakama",
            "紋付袴": "montsuki hakama, formal male kimono",
            "羽織": "haori jacket",
            "甚平": "jinbei, japanese casual wear"
        },
        "作業着/職業服": {
            "おまかせ": "",
            "白衣": "white lab coat, doctor coat",
            "作業着": "work overalls, coveralls",
            "シェフコート": "chef coat, chef uniform",
            "消防服": "firefighter uniform",
            "建設作業員": "construction worker outfit, hard hat"
        }
    },
    "色": {
        "おまかせ": "",
        "黒": "black",
        "白": "white",
        "紺": "navy blue",
        "赤": "red",
        "ピンク": "pink",
        "青": "blue",
        "水色": "light blue",
        "緑": "green",
        "黄": "yellow",
        "オレンジ": "orange",
        "紫": "purple",
        "ベージュ": "beige",
        "グレー": "gray",
        "ゴールド": "gold",
        "シルバー": "silver"
    },
    "柄": {
        "おまかせ": "",
        "無地": "solid color, plain",
        "ストライプ": "striped",
        "チェック": "checkered, plaid",
        "花柄": "floral pattern",
        "ドット": "polka dot",
        "ボーダー": "horizontal stripes",
        "トロピカル": "tropical pattern, hibiscus",
        "レース": "lace",
        "迷彩": "camouflage",
        "アニマル柄": "animal print, leopard"
    },
    "スタイル": {
        "おまかせ": "",
        "大人っぽい": "mature, sophisticated",
        "可愛い": "cute, kawaii",
        "セクシー": "sexy, alluring",
        "クール": "cool, stylish",
        "清楚": "elegant, modest",
        "スポーティ": "sporty, athletic",
        "ゴージャス": "gorgeous, glamorous",
        "ワイルド": "wild, rugged",
        "知的": "intellectual, smart",
        "ダンディ": "dandy, gentlemanly",
        "カジュアル": "casual, relaxed"
    }
}


# シーン説明プレースホルダー
SCENE_PLACEHOLDERS = [
    "1コマのシーンを詳しく説明してください（背景、キャラクターの配置、表情、アクションなど）",
    "キャラクターの全身の特徴を記述（体型、姿勢、特徴的なポイントなど）",
    "キャラクターの顔の特徴を記述（表情、特徴的なポイントなど）",
    "背景の詳細を記述（場所、時間帯、天候、雰囲気など）",
    "（任意）表情やポーズを指定。空欄の場合は無表情・気をつけの姿勢",
    "（任意）表情などを指定。空欄の場合は無表情"
]

# キャラクター説明プレースホルダー
CHARACTER_DESCRIPTION_PLACEHOLDER = "顔、髪型を記述"
