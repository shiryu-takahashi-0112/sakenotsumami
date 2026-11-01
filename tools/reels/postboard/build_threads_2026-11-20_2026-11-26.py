#!/usr/bin/env python3
"""サケノツマミの Threads の投稿文を、2026-11-20〜11-26 の7日分（1日5本・35本）作る。

  python3 postboard/build_threads_2026-11-20_2026-11-26.py

出力: postboard/threads_2026-11-20_11-26.json
文の部品と確認は postboard/build_threads.py のものを使う（禁止語・行数・文字数・末尾の注意表示・
ハッシュタグ・絵文字・同じ品の回数・お酒のずれ）。

Threads のレシピへのリンクは17:05の「今夜の一品」だけ・1日1本（2026-10-17の定例で決定）。
毎回違う言い回しの1行と、レシピのURL（campaign=evening）を本文の最後（ハッシュタグの上）に置く。

写して使うとき（週の作り足し）:
  1. START・DAYS・SCHEDULE・OUT と、TIPS・HUMOR・TONIGHT・LIST_SECOND・SINGLE_EVENING・ALARUARU・EVENING_LIST・URL_LEADS を差し替える
  2. python3 postboard/build_threads_2026-11-20_2026-11-26.py を実行し、指摘が0件になるまで直す（variety の指摘も止まる）

| 時刻 | 型 | 中身 |
|---|---|---|
| 11:05 | 小ワザ | 手順にあるコツを1つ |
| 15:05 | 大喜利／投票／ツッコミ | 日ごとに順に回す。返信しやすい形で終える |
| 17:05 | 今夜の一品 | その日のリール（schedule/2026-11-20_2026-11-26.json）の品。◯選型の日は1品目。本文の最後にレシピのURL |
| 19:05 | 今夜の一品／◯選 | 1品型の日は別の3品（◯選）、◯選型の日はリールの2品目 |
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

START = datetime.date(2026, 11, 20)
DAYS = 7
SCHEDULE = bt.ROOT / "schedule" / "2026-11-20_2026-11-26.json"
OUT = HERE / "threads_2026-11-20_11-26.json"
RECIPE_URL_TMPL = "https://osakenomitai.com/sakenotsumami/recipes/{id}/?utm_source=threads&utm_medium=social&utm_campaign=evening"
URL_LEADS = [   # 17:05のURLの前に置く文（毎回変える。同じ文を14日以内に使わない）
    "今日の材料と手順は、アプリのレシピページに。",
    "作り方の全部は、プロフィールのリンクから。",
    "分量の詳細は、レシピページでどうぞ。",
    "材料の分量は、アプリでまとめて見られます。",
    "今日の手順は、アプリのページに置いています。",
    "レシピの続きは、こちらでご確認を。",
    "作り方の詳細ページは、こちら。",
]

# ---- 11:05 小ワザ（手順にあるコツを1つ。今週のリールとは別の品から選んだ）
TIPS = [
    ("tori-negima", ["フライパンねぎまは、いちばん大きい鶏肉を切って確かめる。", "ピンク色が残っていないか見る。"]),
    ("tebamoto-sujoyu", ["手羽元のさっぱり煮は、いちばん太いところの骨のまわりを切る。", "透明な肉汁が出れば煮えている。"]),
    ("jako-piman", ["じゃこピーマンは、ピーマンを入れる前にじゃこを先にカリッとさせる。", "弱めの中火で2分ほど炒める。"]),
    ("tarako-shirataki", ["たらこしらたきは、たらこが白っぽく色づいたら火が通った目安。", "そこでごま油を加える。"]),
    ("koya-karaage", ["高野豆腐の唐揚げ風は、戻したあと両手でしっかり水気を絞る。", "絞りが甘いと油はねしやすい。"]),
    ("paprika-marinade", ["焼きパプリカのマリネは、皮が黒く焦げるまで焼く。", "そのあと包んで蒸らすと皮がむきやすい。"]),
    ("buta-misozuke", ["豚肩ロースの味噌漬け焼きは、焦げそうならホイルをかぶせる。", "焼けたらピンク色が残っていないか確かめる。"]),
]

# ---- 15:05 大喜利／投票／ツッコミ（日ごとに順に回す。返信しやすい形で終える）
HUMOR = [
    ("投票", ["おつまみを作る前、最初に触るのは？", "A まな板", "B フライパン", "C スマホでレシピ確認", "触れた記号を、返信に。"]),
    ("ツッコミ", ["計量スプーン、", "大さじも小さじも、気づけば1本しかない。", "探した経験がある人は、返信を。"]),
    ("大喜利", ["【大喜利】", "引き出しの奥で見つかる、謎のタレのパック。", "正体を、返信で一言。"]),
    ("投票", ["味見はどこでする派？", "A 鍋の前で直接", "B 小皿に取って", "C スプーンでひとさじ", "記号で、返信にどうぞ。"]),
    ("ツッコミ", ["キッチンタイマー、", "セットしたのに、鳴る前に自分で確認してしまう。", "待てない人は、返信を。"]),
    ("大喜利", ["【大喜利】", "冷蔵庫のドアポケットに増えていく、謎の小袋。", "名づけるなら、返信で。"]),
    ("投票", ["作っているとき、気になるのは？", "A 時間", "B 洗い物", "C 火加減", "気になる記号を、返信で。"]),
]

# ---- 17:05 今夜の一品（その日のリールのお酒に合わせる。◯選型の日は1品目）
TONIGHT = [
    ("pajeori", "beer"),             # 11/20 リール：ビール・10分以内の3選
    ("tara-meuniere", "wine"),       # 11/21 リール：たらのレモンバタームニエル（ワイン）
    ("ebi-avocado", "highball"),     # 11/22 リール：ハイボール・火を使わない3選
    ("salmon-chanchan", "sake"),     # 11/23 リール：鮭のちゃんちゃん焼き（日本酒）
    ("range-yudofu", "shochu"),      # 11/24 リール：焼酎・レンジの3選
    ("ika-gochujang", "sour"),       # 11/25 リール：いかのコチュジャン炒め（レモンサワー）
    ("seafood-marinade", "wine"),    # 11/26 リール：ワインの3選
]

# ---- 19:05：◯選型の日はリールの2品目（今夜の一品）。1品型の日は別のお酒の3品（◯選）
LIST_SECOND = {
    "2026-11-20": ("atsuage-oyster", "beer"),
    "2026-11-22": ("cornedbeef-onion", "highball"),
    "2026-11-24": ("range-japchae", "shochu"),
    "2026-11-26": ("avocado-egg", "wine"),
}
SINGLE_EVENING = {
    "2026-11-21": ("sake", ["salmon-foil", "namaham-kaki", "nasu-dengaku"]),
    "2026-11-23": ("beer", ["ham-macaroni-salad", "sanma-cheese", "gyu-cumin"]),
    "2026-11-25": ("highball", ["ebi-mayo", "iwashi-panko", "buta-sate"]),
}

# ---- 21:00：1品型の日（問いかけの日）はあるある。◯選型の日は別のお酒の3品（◯選）
# 2026-10-17（灯の指示）：あるある調の本文は保ったまま、文末に必ず1行、明示的な問いを入れる
# （「どっち派」は週2回まで。CLAUDE.mdの一人称・お酒の量の言い回しは使わない）。
ALARUARU = {
    "2026-11-21": ["土曜の午前、冷蔵庫の奥から賞味期限ぎりぎりの調味料が出てくる。", "今のうちに使い切ろうと決意する。",
                   "そんな調味料、ありますか？"],
    "2026-11-23": ["月曜の夜、冷凍庫を開けて使いかけの肉を発見する。", "献立がそこで決まる。",
                   "冷凍庫で献立が決まること、ありますか？"],
    "2026-11-25": ["水曜の夜、シンクに洗い物がひとつも無いと気分がいい。", "つまみ一品で済ませた日は、だいたいそう。",
                   "洗い物の少ない夜、好きですか？"],
}
EVENING_LIST = {
    "2026-11-20": ("wine", ["mozzarella-panko", "radish-butter", "spanish-omelet"]),
    "2026-11-22": ("shochu", ["gyu-negimaki", "renkon-steak", "eihire-aburi"]),
    "2026-11-24": ("sour", ["yam-khai-dao", "ebi-broccoli", "jaga-sanra"]),
    "2026-11-26": ("beer", ["saba-tomato", "ontama-kimchi", "corn-cheese"]),
}

HISTORY = []   # Postboard の公開済み・予定（main で読む）


def ctx(posts):
    return HISTORY + posts


def at(day, hh, mm):
    return f"{day.isoformat()}T{hh:02d}:{mm:02d}:00+09:00"


K = {"tonight": 0, "list": 0}


def tonight(rid, drink, when, posts, url_lead=None):
    lines = bt.tonight_lines(rid, drink)[2:]
    r = R[rid]
    head, K["tonight"] = variety.pick(variety.TONIGHT_HEADS, K["tonight"], when, ctx(posts), "\n".join(lines),
                                      name=r["name"], mt=bt.mt(rid), min=r["min"], how=variety.HOW[r["tool"]])
    body = [head] + lines
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
            lines = tonight(rid, drink, at(day, 19, 5), posts)
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
        if not 2 <= len(lines) <= 6:
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
