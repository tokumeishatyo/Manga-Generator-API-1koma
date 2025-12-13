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

# 出力タイプ定義（完全ステップワークフロー）
# Step 1-3: キャラクター生成フェーズ
# Step 4: ポーズ生成フェーズ
# Step 5: エフェクト生成フェーズ
# Step 6-8: 最終合成フェーズ / 特化プリセット
OUTPUT_TYPES = {
    # === キャラクター生成フェーズ ===
    "Step1: 顔三面図": "step1_face",
    "Step2: 素体三面図": "step2_body",
    "Step3: 衣装着用": "step3_outfit",
    # === ポーズ生成フェーズ ===
    "Step4: ポーズ付与": "step4_pose",
    # === エフェクト生成フェーズ ===
    "Step5a: オーラ追加": "step5a_aura",
    "Step5b: 攻撃エフェクト": "step5b_attack",
    "Step5c: 覚醒変形": "step5c_transform",
    # === 最終合成・特化プリセット ===
    "合成: シンプル": "compose_simple",
    "合成: 力の解放": "compose_power",
    "合成: 参戦スプラッシュ": "compose_sansen",
    "合成: バトル画面": "compose_battle",
    "合成: バリア展開": "compose_barrier",
    # === その他 ===
    "背景生成": "background",
    "装飾テキスト": "decorative_text",
    "4コマ漫画": "four_panel_manga"
}

# ステップの順序定義（進捗トラッカー用）
STEP_ORDER = [
    "step1_face",
    "step2_body",
    "step3_outfit",
    "step4_pose",
    "step5a_aura",
    "step5b_attack",
    "step5c_transform",
]

# ステップの表示名
STEP_LABELS = {
    "step1_face": "Step1: 顔三面図",
    "step2_body": "Step2: 素体三面図",
    "step3_outfit": "Step3: 衣装着用",
    "step4_pose": "Step4: ポーズ付与",
    "step5a_aura": "Step5a: オーラ追加",
    "step5b_attack": "Step5b: 攻撃エフェクト",
    "step5c_transform": "Step5c: 覚醒変形",
}

# 各ステップの必須入力（前ステップの出力）
STEP_REQUIREMENTS = {
    "step1_face": None,  # 最初のステップ、入力不要
    "step2_body": "step1_face",  # 顔三面図が必要
    "step3_outfit": "step2_body",  # 素体三面図が必要
    "step4_pose": "step3_outfit",  # 衣装着用三面図が必要
    "step5a_aura": "step4_pose",  # ポーズ付きキャラが必要
    "step5b_attack": "step4_pose",  # ポーズ付きキャラが必要（オーラなしでもOK）
    "step5c_transform": "step4_pose",  # ポーズ付きキャラが必要
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

# キャラクタースタイル（character_basic.yaml準拠）
CHARACTER_STYLES = {
    "標準アニメ": {
        "style": "日本のアニメスタイル, 2Dセルシェーディング",
        "proportions": "Normal head-to-body ratio (6-7 heads)",
        "description": "High quality anime illustration"
    },
    "ドット絵": {
        "style": "Pixel Art, Retro 8-bit game style, low resolution",
        "proportions": "Pixel sprite proportions",
        "description": "Visible pixels, simplified details, retro game sprite, no anti-aliasing"
    },
    "ちびキャラ": {
        "style": "Chibi style, Super Deformed (SD) anime",
        "proportions": "2 heads tall (2頭身), large head, small body, cute",
        "description": "Cute mascot character, simplified features"
    }
}

# 体型プリセット（Step2: 素体三面図用）
BODY_TYPE_PRESETS = {
    "標準体型（女性）": {
        "description": "average female body, slim build, normal proportions",
        "height": "average height",
        "build": "slim",
        "gender": "female"
    },
    "標準体型（男性）": {
        "description": "average male body, normal build, normal proportions",
        "height": "average height",
        "build": "normal",
        "gender": "male"
    },
    "スリム体型": {
        "description": "slender body, thin build, long limbs",
        "height": "tall",
        "build": "slender",
        "gender": "neutral"
    },
    "筋肉質": {
        "description": "muscular body, athletic build, well-defined muscles",
        "height": "average to tall",
        "build": "muscular",
        "gender": "neutral"
    },
    "ぽっちゃり": {
        "description": "chubby body, soft round build, plump",
        "height": "average",
        "build": "chubby",
        "gender": "neutral"
    },
    "子供体型": {
        "description": "child body, small stature, childlike proportions",
        "height": "short",
        "build": "childlike",
        "gender": "neutral"
    },
    "高身長": {
        "description": "tall body, long legs, model-like proportions",
        "height": "tall",
        "build": "slim",
        "gender": "neutral"
    },
    "低身長": {
        "description": "short body, compact build, petite",
        "height": "short",
        "build": "petite",
        "gender": "neutral"
    }
}

# 素体表現タイプ（Step2用）
BODY_RENDER_TYPES = {
    "シルエット": {
        "description": "solid silhouette, no details, shape only",
        "prompt": "solid black silhouette, shape only, no details, clean outline"
    },
    "素体（白レオタード）": {
        "description": "white leotard/bodysuit, minimal details",
        "prompt": "wearing plain white leotard, simple white bodysuit, minimal details, reference mannequin"
    },
    "素体（白下着）": {
        "description": "white underwear, body shape clearly visible",
        "prompt": "wearing simple white underwear, white bra and white panties, minimal clothing, body shape clearly visible, reference mannequin"
    },
    "解剖学的": {
        "description": "anatomical reference, muscle structure visible",
        "prompt": "anatomical reference, muscle groups visible, artistic anatomy study"
    }
}

# 背景生成用プロンプト
BACKGROUND_PROMPT = "background only, no characters, no people, detailed environment, scenic"

# エフェクト付きキャラ生成用定数
CHARACTER_FACING = {
    "→右向き": "right",
    "←左向き": "left"
}

CHARACTER_POSES = {
    "攻撃": "attacking, offensive pose",
    "防御": "defending, blocking, guarding pose",
    "ダメージ": "taking damage, hurt, recoiling",
    "勝利": "victorious, triumphant, winning pose",
    "構え": "battle ready, fighting stance",
    "必殺技チャージ": "charging special attack, power gathering, glowing aura"
}

EFFECT_TYPES = {
    "なし": "",
    "ビーム": "energy beam",
    "波動": "energy wave",
    "炎": "fire, flames",
    "雷": "lightning, electricity",
    "氷": "ice, frost",
    "闇": "dark energy",
    "光": "light, holy energy",
    "オーラ": "powerful aura"
}

EFFECT_COLORS = {
    "おまかせ": "",
    "青": "blue",
    "赤": "red",
    "黄": "yellow",
    "緑": "green",
    "紫": "purple",
    "白": "white",
    "虹色": "rainbow-colored",
    "金色": "golden",
    "黒": "black, dark"
}

EFFECT_EMISSIONS = {
    "おまかせ": "",
    "手から": "from hand",
    "両手から": "from both hands",
    "人差し指から": "from index finger",
    "剣から": "from sword",
    "杖から": "from staff, wand",
    "目から": "from eyes",
    "全身から": "emanating from entire body"
}

CHARACTER_COMPOSITIONS = {
    "カットイン（大）": "dramatic full-screen anime-style character cut-in, intense close-up filling most of the frame",
    "カットイン（中）": "large anime-style character cut-in, dramatic close-up",
    "全身": "full body view, standing pose",
    "上半身": "upper body, bust shot",
    "バストアップ": "close-up bust shot, face and shoulders"
}

# カットイン構図かどうか（攻撃方向の解釈が変わる）
CUTIN_COMPOSITIONS = ["カットイン（大）", "カットイン（中）"]

# 対戦モード（合成時に向かい合い指示を追加）
COMPOSITE_BATTLE_MODES = {
    "なし": "",
    "対戦（向かい合い）": "versus_facing",
    "協力（同じ方向）": "coop_same_direction"
}

SIMPLE_BACKGROUNDS = {
    "透明風（白）": "plain white background, clean, no distractions",
    "透明風（グレー）": "plain light gray background, neutral",
    "グラデーション": "gradient background, subtle color transition",
    "集中線": "speed lines background, action lines, dramatic",
    "爆発": "explosion background, dramatic impact"
}

# ドット絵キャラ生成用定数
PIXEL_STYLES = {
    "16bit風": "pixel art style, 16-bit, retro game graphics, pixelated sprite",
    "8bit風": "pixel art style, 8-bit, classic retro game, very pixelated",
    "32bit風": "pixel art style, 32-bit, detailed sprite, semi-retro"
}

PIXEL_SIZES = {
    "小（アイコン）": "small sprite, icon size, chibi proportions",
    "中（通常）": "medium sprite, standard game character size",
    "大（詳細）": "large detailed sprite, high detail pixel art"
}

# 画像合成用定数
COMPOSITE_POSITIONS = {
    "左": "left",
    "中央左": "center-left",
    "中央": "center",
    "中央右": "center-right",
    "右": "right"
}

COMPOSITE_SIZES = {
    "特大": "very large, filling most of that area",
    "大": "large",
    "中": "medium",
    "小": "small"
}

COMPOSITE_LAYOUTS = {
    "格闘ゲーム風": "fighting game style battle screen",
    "対戦画面風": "versus screen style, face-off composition",
    "RPGバトル風": "JRPG battle scene style",
    "カットイン演出": "dramatic cut-in composition, special move announcement"
}

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
