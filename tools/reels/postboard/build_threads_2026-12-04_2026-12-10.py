#!/usr/bin/env python3
"""サケノツマミの Threads の投稿文を、2026-12-04〜12-10 の7日分（1日5本・35本）作る。

  python3 postboard/build_threads_2026-12-04_2026-12-10.py

出力: postboard/threads_2026-12-04_12-10.json
文の部品と確認は postboard/build_threads.py のものを使う（禁止語・行数・文字数・末尾の注意表示・
ハッシュタグ・絵文字・同じ品の回数・お酒のずれ）。

Threads のレシピへのリンクは17:05の「今夜の一品」だけ・1日1本（2026-10-17の定例で決定）。
毎回違う言い回しの1行と、レシピのURL（campaign=evening）を本文の最後（ハッシュタグの上）に置く。

2026-11-09（灯の指示・試験導入）：19:05枠「今夜の一品」（◯選型の日のみ）の文末に、断定せず軽く開けて
終える一言を1つ足す（他の合わせ方を尋ねる型／好みの分岐を残す型／置き換え食材を尋ねる型の3パターンを
品に合わせて言い換えて使う）。17:05・21:00・11:05・15:05は変えない。

2026-11-10（灯の指示）：15:05枠（大喜利／投票／ツッコミ）の結びに、大喜利タイプも含め必ず明示的な
「返信で」を含める。結びの言い回しは3〜4パターンに分け、「返信でどうぞ。」の多用を避ける。

写して使うとき（週の作り足し）:
  1. START・DAYS・SCHEDULE・OUT と、TIPS・HUMOR・TONIGHT・LIST_SECOND・SINGLE_EVENING・ALARUARU・EVENING_LIST・URL_LEADS を差し替える
  2. python3 postboard/build_threads_2026-12-04_2026-12-10.py を実行し、指摘が0件になるまで直す（variety の指摘も止まる）

| 時刻 | 型 | 中身 |
|---|---|---|
| 11:05 | 小ワザ | 手順にあるコツを1つ |
| 15:05 | 大喜利／投票／ツッコミ | 日ごとに順に回す。返信しやすい形で終える |
| 17:05 | 今夜の一品 | その日のリール（schedule/2026-12-04_2026-12-10.json）の品。◯選型の日は1品目。本文の最後にレシピのURL |
| 19:05 | 今夜の一品／◯選 | 1品型の日は別の3品（◯選）、◯選型の日はリールの2品目（◯選型の日だけ文末に一言を試験追加） |
| 21:00 | あるある／◯選 | 1品型の日（問いかけの日）はあるある、◯選型の日は別のお酒の3品（◯選） |
"""
import collections
import datetime
import importlib.util
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import variety  # noqa: E402

spec = importlib.util.spec_from_file_location("bt", HERE / "build_threads.py")
bt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bt)
common, R, DRINK, TOOL = bt.common, bt.R, bt.DRINK, bt.TOOL

START = datetime.date(2026, 12, 4)
DAYS = 7
SCHEDULE = bt.ROOT / "schedule" / "2026-12-04_2026-12-10.json"
OUT = HERE / "threads_2026-12-04_12-10.json"
RECIPE_URL_TMPL = "https://osakenomitai.com/sakenotsumami/recipes/{id}/?utm_source=threads&utm_medium=social&utm_campaign=evening"
URL_LEADS = [   # 17:05のURLの前に置く文（毎回変える。同じ文を14日以内に使わない）
    "詳しい手順は、アプリのレシピページに置いています。",
    "材料の量は、レシピページでご確認ください。",
    "作り方の続きは、アプリのページからどうぞ。",
    "レシピの手順は、こちらのページにまとめました。",
    "今日の分量は、レシピページでどうぞ。",
    "材料と手順、アプリのページに置いています。",
    "作り方はこの先、レシピページで見られます。",
]

# ---- 11:05 小ワザ（手順にあるコツを1つ。今週のリールとは別の品から選んだ）
TIPS = [
    ("tako-carpaccio", ["タコのカルパッチョは、玉ねぎを薄切りにして水にさらす。", "辛みが抜けて、タコの味を邪魔しない。"]),
    ("nagaimo-ume", ["長芋の梅おかか和えは、梅干しをたたいてめんつゆと混ぜる。", "酸味がやわらぎ、長芋にからみやすくなる。"]),
    ("shungiku-salad", ["春菊を生で使うときは、冷水に少しつけてパリッとさせる。", "水気をよく切ってから和える。"]),
    ("mentai-dip", ["明太クリームチーズディップは、クリームチーズを室温でやわらかくする。", "なめらかに混ざり、味が均一になる。"]),
    ("eringi-butter", ["エリンギのバター醤油は、手で縦に細くさく。", "切るより断面が増えて、味がよくからむ。"]),
    ("okura-okaka", ["オクラは、塩でこすってうぶ毛を取ってから加熱する。", "口当たりがなめらかになる。"]),
    ("onion-okaka", ["オニオンスライスは、薄切りにしてから5分水にさらす。", "辛みが抜け、水気はしっかり絞る。"]),
]

# ---- 15:05 大喜利／投票／ツッコミ（日ごとに順に回す。結びは必ず明示的な「返信で」。言い回しは複数用意する）
HUMOR = [
    ("ツッコミ", ["調味料の蓋、", "気づけば輪ゴムで留まっている時期がある。", "思い当たる人は、返信にどうぞ。"]),
    ("投票", ["一品を盛る器、どっちで選ぶ？", "A 料理に合わせて選ぶ", "B 洗い物の少なさで選ぶ", "選んだ記号は、返信にどうぞ。"]),
    ("大喜利", ["【大喜利】", "引っ越しのたびに増えていく、謎のタッパーのふた。", "その正体を、返信で聞かせてください。"]),
    ("ツッコミ", ["キッチンのメモ用紙、", "買うものを書いたのに、持たずに出かける。", "似た経験があれば、返信で。"]),
    ("投票", ["選ぶときに見るのは？", "A 冷蔵庫にあるもの", "B 気分で決める", "C お酒に合わせる", "選んだ記号を、ひとつ返信で。"]),
    ("ツッコミ", ["シンクの排水口のネット、", "交換するタイミングをいつも逃す。", "そうなる人は、返信でひとこと。"]),
    ("大喜利", ["食器棚の奥でずっと眠っている、もらいもののグラス。", "出番を、返信で予想してください。"]),
]

# ---- 17:05 今夜の一品（その日のリールのお酒に合わせる。◯選型の日は1品目）
TONIGHT = [
    ("chikuwa-kyuri", "beer"),        # 12/04 リール：ビール・火を使わない3選
    ("gorgonzola-honey", "wine"),     # 12/05 リール：ゴルゴンゾーラのはちみつくるみ（ワイン）
    ("oil-sardine", "highball"),      # 12/06 リール：ハイボール・10分以内の3選
    ("sasami-umeshiso", "sake"),      # 12/07 リール：ささみの梅しそチーズ焼き（日本酒）
    ("myoga-amazu", "shochu"),        # 12/08 リール：焼酎・火を使わない3選
    ("torikawa", "sour"),             # 12/09 リール：鶏皮のパリパリ焼き（レモンサワー）
    ("cheese-senbei", "wine"),        # 12/10 リール：ワイン・10分以内の3選
]

# ---- 19:05：◯選型の日はリールの2品目（今夜の一品）。1品型の日は別のお酒の3品（◯選）
LIST_SECOND = {
    "2026-12-04": ("deviled-egg", "beer"),
    "2026-12-06": ("chingensai-oyster", "highball"),
    "2026-12-08": ("tofu-shiokombu", "shochu"),
    "2026-12-10": ("gyoza-pizza", "wine"),
}
SINGLE_EVENING = {
    "2026-12-05": ("beer", ["ika-butter", "saladchicken-bangbangji", "range-mapo"]),
    "2026-12-07": ("highball", ["negi-chashu", "mune-panko-yaki", "sunagimo-garlic"]),
    "2026-12-09": ("shochu", ["gyu-shigure", "katsuo-tataki", "ika-mekabu"]),
}

# ---- 19:05「今夜の一品」（◯選型の日だけ）の文末に足す一言（2026-11-09・灯の指示の試験導入）
# 他の合わせ方を尋ねる型／好みの分岐を残す型／置き換え食材を尋ねる型を、品に合わせて言い換えて使う。
TONIGHT_EXTRA = {
    "2026-12-04": "マスタードの量は多め・少なめ、好みが分かれそうなところ。",             # 好みの分岐型
    "2026-12-06": "チンゲン菜の代わりに、小松菜で作っても近い仕上がりになりそうなところ。",   # 置き換え食材型
    "2026-12-08": "ほかに合わせるなら、塩昆布以外で試したい薬味も気になる。",             # 他の合わせ方型
    "2026-12-10": "ピーマンは多め・少なめ、好みが分かれそうなところ。",                   # 好みの分岐型
}

# ---- 21:00：1品型の日（問いかけの日）はあるある。◯選型の日は別のお酒の3品（◯選）
ALARUARU = {
    "2026-12-05": ["土曜は、昼から何か作ろうかと思って、結局つまみ1品で終わる。", "予定を詰めない日があってもいい。",
                   "予定を詰めない土曜、ありますか？"],
    "2026-12-07": ["月曜の夜、冷蔵庫を開けて、まず何があるかだけ確認する。", "決めるのはそのあとでいい。",
                   "まず確認だけする夜、ありますか？"],
    "2026-12-09": ["水曜になると、週の初めに買ったものが半分くらい残っている。", "その残りで、どうにか一品にする。",
                   "週の半分で見直す人、ありますか？"],
}
EVENING_LIST = {
    "2026-12-04": ("wine", ["edamame-peperoncino", "roastbeef-yukke", "kabocha-cheese-salad"]),
    "2026-12-06": ("sour", ["kabu-lemon", "mugen-piman", "tunamayo-piman"]),
    "2026-12-08": ("sake", ["maguro-yukke", "dashimaki", "sasami-wasabi"]),
    "2026-12-10": ("beer", ["shishamo", "yaki-shishito", "aburaage-pizza"]),
}

HISTORY = []   # Postboard の公開済み・予定（main で読む）


def ctx(posts):
    return HISTORY + posts


def at(day, hh, mm):
    return f"{day.isoformat()}T{hh:02d}:{mm:02d}:00+09:00"


K = {"tonight": 0, "list": 0}
# 「つまみに〜」の型は1行目が「つまみ」で始まり、既存の予定と重なって上限に当たりやすいので外す。
SAFE_TONIGHT_HEADS = [t for t in variety.TONIGHT_HEADS if not t.startswith("つまみ")]


def tonight(rid, drink, when, posts, url_lead=None, extra=None):
    lines = bt.tonight_lines(rid, drink)[2:]
    r = R[rid]
    head, K["tonight"] = variety.pick(SAFE_TONIGHT_HEADS, K["tonight"], when, ctx(posts), "\n".join(lines),
                                      name=r["name"], mt=bt.mt(rid), min=r["min"], how=variety.HOW[r["tool"]])
    body = [head] + lines
    if extra:
        body += [extra]
    if url_lead:
        body += [url_lead, RECIPE_URL_TMPL.format(id=rid)]
    return body


def list_lines(drink, ids, when, posts):
    head, K["list"] = variety.pick(variety.LIST_HEADS, K["list"], when, ctx(posts), drink=DRINK[drink])
    return [head] + [f"{R[i]['name']}（{R[i]['min']}分・{TOOL[R[i]['tool']]}）" for i in ids]


def main():
    HISTORY[:] = variety.load_history()
    posts = []
    for k in range(DAYS):
        day = START + datetime.timedelta(days=k)
        ds = day.isoformat()
        is_list = ds in LIST_SECOND
        # 11:05
        rid, lines = TIPS[k]
        posts.append(bt.post(day, 11, 5, "小ワザ", lines, [rid], "#おつまみ"))
        # 15:05
        kind, lines = HUMOR[k]
        posts.append(bt.post(day, 15, 5, kind, lines, []))
        # 17:05 今夜の一品（本文の最後に、レシピのURL。毎日1本）
        rid, drink = TONIGHT[k]
        lead = URL_LEADS[k % len(URL_LEADS)]
        p = bt.post(day, 17, 5, "今夜の一品", tonight(rid, drink, at(day, 17, 5), posts, lead), [rid], common.DRINK_TAGS[drink])
        p["drink"] = drink
        posts.append(p)
        # 19:05
        if is_list:
            rid, drink = LIST_SECOND[ds]
            lines = tonight(rid, drink, at(day, 19, 5), posts, extra=TONIGHT_EXTRA.get(ds))
            p = bt.post(day, 19, 5, "今夜の一品", lines, [rid], common.DRINK_TAGS[drink])
        else:
            drink, ids = SINGLE_EVENING[ds]
            lines = list_lines(drink, ids, at(day, 19, 5), posts)
            p = bt.post(day, 19, 5, "◯選", lines, ids, common.DRINK_TAGS[drink])
        p["drink"] = drink
        posts.append(p)
        # 21:00
        if ds in ALARUARU:
            posts.append(bt.post(day, 21, 0, "あるある", ALARUARU[ds], []))
        else:
            drink, ids = EVENING_LIST[ds]
            lines = list_lines(drink, ids, at(day, 21, 0), posts)
            p = bt.post(day, 21, 0, "◯選", lines, ids, common.DRINK_TAGS[drink])
            p["drink"] = drink
            posts.append(p)

    errors = validate(posts)
    errors += variety.check(posts, HISTORY)
    if errors:
        sys.exit("\n".join(errors))
    for p in posts:
        p.pop("drink", None)
    out = pathlib.Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else OUT
    if out == OUT and OUT.exists() and "--force" not in sys.argv:
        sys.exit(f"{OUT.name} はもうある（予約済みの記録）。上書きするなら --force、試すなら --out <別の場所>")
    out.write_text(json.dumps(posts, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    bt.OUT = out
    bt.summary(posts, [])


def validate(posts):
    """bt.check() の代わり。2026-10-17の新URL方式（レシピURL・1日1本）にあわせて確かめる。"""
    errors = []
    uses = collections.Counter()
    url_days = collections.Counter()
    url_re = re.compile(r"https://\S+")
    for p in posts:
        t, at_ = p["text"], p["scheduled_at"]
        lines = t.split("\n")
        if not 2 <= len(lines) <= 7:
            errors.append(f"{at_}: 行数 {len(lines)}")
        if len(t) > 500:
            errors.append(f"{at_}: {len(t)}文字")
        if "20歳になってから" in t:
            errors.append(f"{at_}: 「{bt.NOTE}」が入っている")
        hit = common.banned_hits(t)
        if hit:
            errors.append(f"{at_}: 使わない言い回し {hit}")
        tags = re.findall(r"(?:^|\s)#\S+", t)
        if len(tags) > 1 or (tags and not lines[-1].startswith("#")):
            errors.append(f"{at_}: ハッシュタグ {tags}")
        if bt.EMOJI.search(t):
            errors.append(f"{at_}: 絵文字")
        m = url_re.search(t)
        if m:
            url = m.group(0)
            if not url.startswith("https://osakenomitai.com/sakenotsumami/recipes/") or "utm_campaign=evening" not in url:
                errors.append(f"{at_}: URLの形が違う（レシピURL・campaign=evening であること）: {url}")
            else:
                rid_in_url = url.split("/recipes/", 1)[1].split("/", 1)[0]
                if rid_in_url not in R:
                    errors.append(f"{at_}: URLのレシピが無い {rid_in_url}")
            url_days[at_[:10]] += 1
        for rid in p["recipe_ids"]:
            if rid not in R:
                errors.append(f"{at_}: レシピが無い {rid}")
            uses[rid] += 1
        if p["kind"] in ("今夜の一品", "◯選"):
            drink = p.get("drink")
            if drink:
                stripped = t.replace(common.DRINK_TAGS.get(drink, ""), "")
                if not common.fits(stripped, drink):
                    errors.append(f"{at_}: 見出しのお酒と文がずれている")
                for rid in p["recipe_ids"]:
                    if drink not in R[rid]["drinks"]:
                        errors.append(f"{at_}: {rid} の drinks に {drink} が無い")
    for day, n in url_days.items():
        if n > 1:
            errors.append(f"{day}: URLが1日に{n}回")
    over = {k: v for k, v in uses.items() if v >= 3}
    if over:
        errors.append(f"同じ品が3回以上: {over}")
    if len(posts) != DAYS * 5:
        errors.append(f"件数が {len(posts)}")
    return errors


if __name__ == "__main__":
    main()
