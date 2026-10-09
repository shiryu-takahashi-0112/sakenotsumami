"""make_reel.py / make_carousel.py で共通に使う部品。

- レシピの読み込み（recipes.js は node で読むだけ。書き換えない）
- 見出し「◯◯に合う、◯分つまみ」の組み立て
- キャプション（caption.txt）の組み立て
- HTMLの型にデータを差し込む処理
"""
import json
import pathlib
import re
import subprocess
import sys
import zlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
# アプリのリポジトリの直下（このフォルダは <リポジトリ>/tools/reels）。2026-10-09 にクラウドで動かすため相対にした
APP = ROOT.parent.parent
IMAGES = APP / "images"
WORK = ROOT / "work"

# ハッシュタグ（合計5個まで。#サケノツマミ ＋ 料理の種類・お酒・場面・おつまみ系 の4枠）
BRAND_TAG = "#サケノツマミ"
DRINK_TAGS = {
    "beer": "#ビールに合う",
    "highball": "#ハイボールに合う",
    "sour": "#レモンサワーに合う",
    "sake": "#日本酒に合う",
    "shochu": "#焼酎に合う",
    "wine": "#ワインに合う",
}
SCENE_TAGS = ["#家飲み", "#宅飲み", "#晩酌"]
TSUMAMI_TAGS = ["#おつまみ", "#つまみレシピ"]
# 料理の種類：料理名に含まれる語で上から順に判定し、どれにも当たらなければ #野菜おつまみ
KIND_RULES = [
    ("#チーズおつまみ", "チーズ カマンベール カプレーゼ"),
    ("#肉おつまみ", "豚 鶏 牛 手羽 砂肝 ささみ ソーセージ ベーコン つくね タッカルビ サムギョプサル プルコギ ガパオ 生ハム"),
    ("#魚介おつまみ", "サバ サーモン まぐろ かつお タコ イカ えび シュリンプ あさり ホタテ ぶり 鮭 ししゃも しらす サーディン カニカマ ちくわ はんぺん さつま揚げ 明太 塩辛 アンチョビ"),
    ("#豆腐レシピ", "豆腐 奴 厚揚げ 油揚げ 納豆"),
    ("#卵料理", "卵 ニラ玉"),
]
# キャプションに入れない語（飲みすぎ・一気飲みなどを連想させるもの）
BANNED_WORDS = ["飲み過ぎ", "飲みすぎ", "呑み過ぎ", "呑みすぎ", "一気飲み", "イッキ", "がぶ飲み", "ガブ飲み", "浴びるほど",
                "泥酔", "酔いつぶ", "酔い潰", "爆飲", "鯨飲", "無限に飲", "止まらない酒", "ベロベロ", "べろべろ", "二日酔い", "はしご酒"]
# 文中のお酒の言い回し → お酒の id（「お酒」「軽いお酒」「居酒屋」などはどのお酒でもないので数えない）
DRINK_WORDS = [
    ("ビール", {"beer"}),
    ("ハイボール", {"highball"}),
    ("サワー", {"sour"}),                    # 「レモンサワー」も「サワー」単体もここで拾う
    ("日本酒", {"sake"}), ("燗", {"sake"}), ("冷酒", {"sake"}),
    ("焼酎", {"shochu"}), ("お湯割り", {"shochu"}),
    ("ワイン", {"wine"}),
    ("炭酸のお酒", {"beer", "highball", "sour"}),   # 「炭酸のお酒」は炭酸のお酒すべて
    ("炭酸", {"beer", "highball", "sour"}),   # 「炭酸がすっと切る」など。ただし他のお酒の名前があれば数えない（下の drinks_in）
]
AI_NOTE = "※写真はAIで作ったイメージです。"
AGE_NOTE = "お酒は20歳になってから。"


def drinks_in(text):
    """文に出てくるお酒の id の集合。"""
    found = set()
    for word, ids in DRINK_WORDS:
        if word == "炭酸":
            continue
        if word in text:
            found |= ids
    # 「ビールやハイボールの炭酸」のように名前のあとに出てくる「炭酸」は、その名前のお酒の話なので数えない。
    # お酒の名前が無いときの「炭酸」だけ、炭酸のお酒すべてとして数える（「炭酸のお酒」は上で数え済み）。
    if not found and "炭酸" in text:
        found = {"beer", "highball", "sour"}
    return found


def fits(text, drink_id):
    """「お酒X」の文脈で出してよい文か：Xの名前がある、または他のお酒の名前が無い。"""
    m = drinks_in(text)
    return not m or drink_id in m


def pairing_text(r, drink_id):
    """合う理由として出す文。why が別のお酒の話だけをしているときは catch を使う。
    戻り値は (文, catch を使ったか)。1品型・◯選型・カルーセル・キャプションはすべてここを通す。"""
    if fits(r["why"], drink_id) and not banned_hits(r["why"]):
        return r["why"], False
    return r["catch"], True          # why にお酒の勢いをすすめる言い回しがあるときも catch


def pairing_line(r, drink_id):
    """◯選型で1品に添える1行：why の最初の1文。その1文が別のお酒の話だけなら catch（最後の「。」だけ取る）。"""
    first = r["why"].split("。")[0]
    if fits(first, drink_id) and not banned_hits(first):
        return first
    return r["catch"].rstrip("。")


def pick_rank(r, drink_id):
    """◯選型の自動選択での優先度（小さいほど先）。0＝why にそのお酒の名前がある、1＝どのお酒の名前も無い、2＝別のお酒の話だけ。"""
    m = drinks_in(r["why"])
    if drink_id in m:
        return 0
    return 1 if not m else 2


def default_drink(r):
    """--drink を省いたときのお酒：why に名前が出てくるお酒のうち drinks に入っている最初のもの。無ければ drinks[0]。"""
    m = drinks_in(r["why"])
    for d in r["drinks"]:
        if d in m:
            return d
    return r["drinks"][0]


def load_all():
    """全レシピ・お酒・道具を読む。"""
    out = subprocess.run(["node", str(ROOT / "lib" / "load_recipe.mjs"), "--all"], capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(out.stderr.strip() or "レシピを読めませんでした")
    return json.loads(out.stdout)


def load(recipe_id, drink_id=None):
    """レシピと表示用の値をまとめた dict を返す。"""
    out = subprocess.run(["node", str(ROOT / "lib" / "load_recipe.mjs"), recipe_id],
                         capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(out.stderr.strip() or f"レシピを読めませんでした: {recipe_id}")
    d = json.loads(out.stdout)
    r = d["recipe"]
    drinks = {x["id"]: x["name"] for x in d["drinks"]}
    drink_id = drink_id or default_drink(r)
    if drink_id not in drinks:
        sys.exit(f"--drink は {', '.join(drinks)} のどれかにしてください（指定: {drink_id}）")
    if drink_id not in r["drinks"]:
        print(f"注意: {r['name']} のおすすめのお酒に {drinks[drink_id]} は入っていません（{', '.join(drinks[x] for x in r['drinks'])}）",
              file=sys.stderr)
    photo = IMAGES / f"{r['id']}.jpg"
    if not photo.exists():
        sys.exit(f"写真がありません: {photo}")
    why, why_is_catch = pairing_text(r, drink_id)
    return {
        "recipe": r,
        "why": why,
        "whyIsCatch": why_is_catch,
        "drinkId": drink_id,
        "drink": drinks[drink_id],
        "drinkNames": [drinks[x] for x in r["drinks"]],
        "allDrinks": d["drinks"],
        "tool": d["tools"][r["tool"]]["name"],
        "count": d["count"],
        "head1": f"{drinks[drink_id]}に合う、",
        "head2": f"{r['min']}分つまみ",
        "photo": photo.as_uri(),
    }


def headline(c):
    return c["head1"] + c["head2"]


def _name_tag(name):
    """料理名そのもののタグ。記号や空白を含む名前・長い名前は使わない。"""
    if not all(ch.isalnum() for ch in name) or len(name) > 8:
        return None
    return "#" + name


def _kind_tag(name):
    for tag, words in KIND_RULES:
        if any(w in name for w in words.split()):
            return tag
    return "#野菜おつまみ"


def hashtags(c):
    """#サケノツマミ ＋ 4枠。どれを使うかはレシピの id から決める（毎回同じ組み合わせにならないように）。"""
    r = c["recipe"]
    h = zlib.crc32(r["id"].encode("utf-8"))
    kind = _kind_tag(r["name"])
    name_tag = _name_tag(r["name"])
    if name_tag and h % 2 == 1:
        kind = name_tag                       # 料理の種類の枠に、料理名そのもののタグを入れる
    return _five(h, kind, c["drinkId"], c["drink"])


def _five(h, kind, drink_id, drink_name):
    tags = [
        BRAND_TAG,
        kind,
        DRINK_TAGS.get(drink_id, "#" + drink_name + "に合う"),
        SCENE_TAGS[(h >> 1) % len(SCENE_TAGS)],
        TSUMAMI_TAGS[(h >> 3) % len(TSUMAMI_TAGS)],
    ]
    assert len(tags) == len(set(tags)) <= 5, tags
    return tags


# ◯選型の「料理の種類」の枠：1品に決まらないので汎用のタグにする
LIST_KIND_TAGS = {
    "quick": ["#簡単おつまみ", "#時短おつまみ"],
    "nofire": ["#火を使わないレシピ", "#おつまみレシピ"],
    "range": ["#レンジおつまみ", "#レンジレシピ"],
    "all": ["#おつまみレシピ", "#おうち居酒屋"],
}


def list_hashtags(seed, theme, drink_id, drink_name):
    """◯選型のハッシュタグ。決め方は1品型と同じで、料理の種類の枠だけ汎用のタグにする。seed は出力フォルダ名。"""
    h = zlib.crc32(seed.encode("utf-8"))
    kinds = LIST_KIND_TAGS.get(theme, LIST_KIND_TAGS["all"])
    return _five(h, kinds[(h >> 5) % len(kinds)], drink_id, drink_name)


# お酒の量や勢いをすすめる言い回し（正規表現）。つまみについて言う「箸が進む」「箸が止まらない」は除く。
BANNED_PATTERNS = [
    (r"(?<!箸が)(?<!箸も)進[むみまめ]", "進む"),
    (r"進ませ", "進ませ"),
    (r"(?<!箸が)(?<!箸も)(?<!手が)止まらな", "止まらない（お酒について）"),
    (r"もう一杯", "もう一杯"),
    (r"一杯目", "一杯目"),
    (r"ちびちび", "ちびちび"),
    (r"ぐいっ|グイッ|ぐいぐい|グイグイ", "ぐいっ"),
    (r"ぐびっ|グビッ|ぐびぐび|グビグビ", "ぐびっ"),
    (r"流し込", "流し込"),
    (r"流[すしせさ]", "流す"),          # 「ビールで流す」「炭酸が流してくれる」など
    (r"冷ま[しすさせ]", "冷ます"),       # 「ビールで冷ましながら」など（お酒で辛さを冷ます＝飲む量につながる）
    (r"追いかけ", "追いかけ"),           # 「ビールで追いかけたくなる」など
    (r"を呼ぶ", "呼ぶ"),                # 「ビールを呼ぶ味」など
    (r"飲むのに", "飲むのに"),          # 「焼酎をゆっくり飲むのにいい」など（飲む動作は出さない）
]
# BANNED_WORDS・BANNED_PATTERNS を当てるのは catch・why・キャプション・◯選の1行だけ（材料・作り方には当てない）。


def banned_hits(text):
    """text に入っている、使わない語・言い回しの一覧。"""
    hit = [w for w in BANNED_WORDS if w in text]
    hit += [label for pat, label in BANNED_PATTERNS if re.search(pat, text)]
    return hit


def check_banned(text):
    hit = banned_hits(text)
    if hit:
        sys.exit(f"キャプションに使わない語が入っています: {', '.join(hit)}（レシピの文面を確認してください）")
    return text


def caption(c, kind="reel"):
    """ブランドとして淡々と、一人称なしで書く。"""
    r = c["recipe"]
    lines = [
        headline(c),
        r["name"],
        "",
        c["why"],
        "",
    ]
    if kind == "carousel":
        lines.append("材料と作り方は2枚目から。")
    lines += [
        "レシピはプロフィールのリンクから。",
        "",
        AI_NOTE,
        AGE_NOTE,
        "",
        " ".join(hashtags(c)),
    ]
    return check_banned("\n".join(lines) + "\n")


def fill_template(template, out_html, c):
    """HTMLの型に DATA と作業場所のパス（フォント・ロゴ画像の場所）を差し込んで書き出す。"""
    tpl = pathlib.Path(template).read_text(encoding="utf-8")
    data = dict(c)
    if "allDrinks" in c:
        data["allDrinks"] = [x["name"] for x in c["allDrinks"]]
    for key, val in (
        ("/*__DATA__*/", "window.DATA = " + json.dumps(data, ensure_ascii=False) + ";"),
        ("__ROOT__", ROOT.as_uri()),
    ):
        assert key in tpl, key
        tpl = tpl.replace(key, val)
    out_html = pathlib.Path(out_html)
    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text(tpl, encoding="utf-8")
    return out_html


def run(cmd, **kw):
    subprocess.run(cmd, check=True, **kw)
