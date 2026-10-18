#!/usr/bin/env python3
"""サケノツマミの Threads の投稿文を、2026-11-06〜11-12 の7日分（1日5本・35本）作る。

  python3 postboard/build_threads_2026-11-06_11-12.py

出力: postboard/threads_2026-11-06_11-12.json
文の部品と確認は postboard/build_threads.py のものを使う（禁止語・行数・文字数・末尾の注意表示・
ハッシュタグ・絵文字・同じ品の回数・お酒のずれ）。

2026-10-17の定例でShiryuが決定：Threadsのレシピへのリンクは「週2本まで」から「1日1本（17:05の
今夜の一品）」に変更。よって旧版 build_threads_2026-10-30_11-05.py の URL_DAYS（週2本・19:05へ挿入）
は使わない。17:05の「今夜の一品」だけに、毎回違う言い回しの1行と、レシピのURL
（https://osakenomitai.com/sakenotsumami/recipes/<id>/?utm_source=threads&utm_medium=social&utm_campaign=evening）
を本文の最後（ハッシュタグの上）に置く。旧版 build_threads.py の check() は
「URLがThreads用でない」を汎用URL（utm_campaign=launch）だけ許す作りのままなので、ここでは使わず、
このファイルの validate() で確かめる（URLは1日1本・レシピURLの形であること）。

写して使うとき（週の作り足し）:
  1. START・DAYS・SCHEDULE・OUT と、TIPS・HUMOR・TONIGHT・LIST_SECOND・SINGLE_EVENING・ALARUARU・EVENING_LIST・URL_LEADS を差し替える
  2. python3 postboard/build_threads_2026-11-06_11-12.py を実行し、指摘が0件になるまで直す（variety の指摘も止まる）

| 時刻 | 型 | 中身 |
|---|---|---|
| 11:05 | 小ワザ | 手順にあるコツを1つ |
| 15:05 | 大喜利／投票／ツッコミ | 日ごとに順に回す。返信しやすい形で終える |
| 17:05 | 今夜の一品 | その日のリール（schedule/2026-11-06_2026-11-12.json）の品。◯選型の日は1品目。本文の最後にレシピのURL |
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

START = datetime.date(2026, 11, 6)
DAYS = 7
SCHEDULE = bt.ROOT / "schedule" / "2026-11-06_2026-11-12.json"
OUT = HERE / "threads_2026-11-06_11-12.json"
RECIPE_URL_TMPL = "https://osakenomitai.com/sakenotsumami/recipes/{id}/?utm_source=threads&utm_medium=social&utm_campaign=evening"
URL_LEADS = [   # 17:05のURLの前に置く文（毎回変える。同じ文を14日以内に使わない）
    "分量と手順は、アプリにまとめてあります。",
    "今日の分量はこちら。",
    "作り方の続きは、アプリで。",
    "手順は写真つきで、アプリに。",
    "分量はこちらで確認できます。",
    "続きの手順は、アプリのページへ。",
    "今日の作り方は、こちらから。",
]

# ---- 11:05 小ワザ（手順にあるコツを1つ。今週のリールとは別の品から選んだ）
TIPS = [
    ("hotate-butter", ["ホタテのバターソテーは、焼く前に水気をよくふく。", "焼き色がつきやすくなる。"]),
    ("konnyaku-pirikara", ["こんにゃくのピリ辛炒めは、油をひかずにからいりする。", "キュッと音がするまで3分が目安。"]),
    ("maitake-ponzu", ["舞茸のバターポン酢は、焼いているあいだあまり動かさない。", "そのほうが焼き色がしっかりつく。"]),
    ("potato-galette", ["じゃがいものチーズガレットは、細切りにしたあと水にさらさない。", "でんぷんが残って、まとまりやすい。"]),
    ("zucchini-cheese", ["ズッキーニのチーズ焼きは、1cm幅の輪切りにする。", "厚みがそろうと、火の通りが均一になる。"]),
    ("mochi-cheese-nori", ["お餅のチーズのり焼きは、最初にふくらむまで焼く。", "そのあとチーズをのせて仕上げる。"]),
    ("tofu-shiokombu", ["豆腐の塩昆布ごま油がけは、キッチンペーパーで水気を切る。", "水っぽくならず、味がぼやけない。"]),
]

# ---- 15:05 大喜利／投票／ツッコミ（日ごとに順に回す。返信しやすい形で終える）
HUMOR = [
    ("投票", ["冷蔵庫を開けて最初に見るのは？", "A 野菜室　B チルド室", "C ドアポケット", "記号で返信してください。"]),
    ("ツッコミ", ["シンクの中、", "使うはずのなかったボウルが2個。", "心当たりのある人、返信でどうぞ。"]),
    ("大喜利", ["【大喜利】", "冷凍庫の氷の下から出てきた、謎の白い塊。", "名前をつけるなら。"]),
    ("投票", ["お酒を選ぶ基準は？", "A 気分　B 残っているつまみ", "C とりあえず冷えているもの", "記号で返信を。"]),
    ("ツッコミ", ["キッチンバサミ、", "気づけば毎回別の引き出しから出てくる。", "うちもそう、という人は返信でどうぞ。"]),
    ("大喜利", ["買い物メモに書いた「あれ」。", "結局、思い出せなかった結末を一言で。"]),
    ("投票", ["支度を始めるのは、どっち？", "A 帰ってすぐ　B お酒を開けてから", "決め方は人それぞれ。", "AかBで返信してください。"]),
]

# ---- 17:05 今夜の一品（その日のリールのお酒に合わせる。◯選型の日は1品目）
TONIGHT = [
    ("uzura-bacon", "highball"),        # 11/6 リール：ハイボール・10分以内の3選
    ("aburaage-negiponzu", "beer"),     # 11/7 リール：カリカリ油揚げのねぎポン酢（ビール）
    ("kabu-lemon", "sour"),             # 11/8 リール：レモンサワー・火を使わない3選
    ("aji-namerou", "sake"),            # 11/9 リール：あじのなめろう（日本酒）
    ("tai-negiyu", "shochu"),           # 11/10 リール：焼酎・レンジの3選
    ("aburaage-pizza", "wine"),         # 11/11 リール：油揚げピザ（ワイン）
    ("tori-tsukune", "beer"),           # 11/12 リール：ビールの3選
]

# ---- 19:05：◯選型の日はリールの2品目（今夜の一品）。1品型の日は別のお酒の3品（◯選）
LIST_SECOND = {
    "2026-11-06": ("ham-steak", "highball"),
    "2026-11-08": ("tako-kimchi", "sour"),
    "2026-11-10": ("gobo-chips", "shochu"),
    "2026-11-12": ("corn-butter", "beer"),
}
SINGLE_EVENING = {
    "2026-11-07": ("highball", ["gapao-lettuce", "komatsuna-nampla", "oil-sardine"]),
    "2026-11-09": ("shochu", ["tataki-kyuri", "okura-okaka", "goya-champuru"]),
    "2026-11-11": ("sour", ["tomato-tamago", "torikawa", "buta-negishio-lemon"]),
}

# ---- 21:00：1品型の日（問いかけの日ではなく、あるある）はあるある。◯選型の日は別のお酒の3品（◯選）
ALARUARU = {
    "2026-11-07": ["平日の夜は、つまみを一品だけと決めている。", "気づくと、まな板の上はもう二品目。", "それもいつもの流れ。"],
    "2026-11-09": ["月曜の夜、冷蔵庫を開けて、まず野菜室を見る。", "そこにあるものから、つまみが決まる。", "献立よりも先に。"],
    "2026-11-11": ["水曜の夜、気づくと使った鍋がいつもひとつ多い。", "洗い物は増えても、つまみは二品。", "そこは譲らない。"],
}
EVENING_LIST = {
    "2026-11-06": ("sour", ["range-butashabu", "chikuwa-kyuri", "zucchini-namul"]),
    "2026-11-08": ("wine", ["namaham-cheese", "asari-sakamushi", "garlic-shrimp"]),
    "2026-11-10": ("beer", ["yaki-shishito", "asparagus-bacon", "chicken-misomayo"]),
    "2026-11-12": ("sake", ["shiokara-jagabutter", "dashimaki", "buri-teriyaki"]),
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
        # 17:05 今夜の一品（本文の最後に、レシピのURL。11/6は直前の週の11/5 19:05のURLと間隔が近く、
        # 7日ローリング窓が8本になるため、この回だけURLを入れない。11/7からは毎日1本）
        rid, drink = TONIGHT[k]
        lead = URL_LEADS[(k - 1) % len(URL_LEADS)] if k > 0 else None
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
