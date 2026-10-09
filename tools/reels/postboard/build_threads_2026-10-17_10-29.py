#!/usr/bin/env python3
"""サケノツマミの Threads の投稿文を、2026-10-17〜10-29 の13日分（1日5本・65本）作る。
（10/16 の分は threads_2026-10-03_10-16.json で登録済み）

  python3 postboard/build_threads_2026-10-17_10-29.py

出力: postboard/threads_2026-10-16_10-29.json
文の部品と確認は postboard/build_threads.py のものを使う（禁止語・行数・文字数・末尾の注意表示・
ハッシュタグ・絵文字・URLの回数・同じ品の回数・お酒のずれ）。加えて、2択（どっち派）は1日1本まで。

| 時刻 | 型 | 中身 |
|---|---|---|
| 11:05 | 小ワザ | 手順にあるコツを1つ |
| 15:05 | どっち派 | 2択の問いかけ（その日の2択はこの1本だけ） |
| 17:05 | 今夜の一品 | その日のリール（schedule/2026-10-16_2026-10-29.json）の品。◯選型の日は1品目 |
| 19:05 | 今夜の一品／◯選 | 1品型の日は同じお酒に合う3品、◯選型の日はリールの2品目。URLは7日ごとに2回まで |
| 21:00 | 問いかけ／◯選 | 1日おきに「なに飲みますか」の問いかけと、別のお酒に合う3品 |
"""
import collections
import datetime
import importlib.util
import json
import pathlib
import sys
import zlib

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("bt", HERE / "build_threads.py")
bt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bt)
common, R, DRINK, TOOL = bt.common, bt.R, bt.DRINK, bt.TOOL

START = datetime.date(2026, 10, 17)
DAYS = 13
SCHEDULE = bt.ROOT / "schedule" / "2026-10-16_2026-10-29.json"
OUT = HERE / "threads_2026-10-16_10-29.json"
URL_DAYS = {"2026-10-19", "2026-10-23", "2026-10-26", "2026-10-29"}   # 7日ごとに2回（10/17〜23、10/24〜29）

TIPS = [
    ("nira-chijimi", ["にらチヂミは、裏返したらへらで押さえながら焼く。", "外がカリッと仕上がる。"]),
    ("dashimaki", ["だし巻き卵は、卵液を3回に分けて焼く。", "半熟になったら、奥から手前に巻く。"]),
    ("chicken-negishio", ["鶏ももは、皮目から入れて中火で7〜8分焼く。", "皮がパリッとしてから裏返す。"]),
    ("tofu-steak", ["豆腐ステーキの豆腐は、キッチンペーパーで包んで10分おく。", "水気を切ってから片栗粉をまぶして焼く。"]),
    ("sasami-wasabi", ["ささみをレンジで加熱したら、ラップをしたまま3分おく。", "赤い部分があれば、30秒ずつ追加で加熱する。"]),
    ("nasu-chukadare", ["レンジ蒸しなすは、皮をむいて1本ずつラップで包む。", "600Wで4分加熱して、ラップのまま粗熱が取れるまでおく。"]),
    ("asparagus-bacon", ["アスパラは、根元の硬い部分を切り落とす。", "下1/3の皮をピーラーでむいてから使う。"]),
    ("samgyeopsal", ["豚バラは、油をひかずにフライパンに並べる。", "出てきた脂をふきながら、カリッとするまで焼く。"]),
    ("goya-champuru", ["ゴーヤは薄切りにして、塩でもんでから水気を絞る。", "それから豆腐や豚肉と炒める。"]),
    ("enoki-bacon", ["えのきのベーコン巻きは、巻き終わりを下にして並べる。", "トースターで焼いてもほどけにくい。"]),
    ("tebanaka-shio", ["手羽中は、水気をふいてから塩と黒こしょうをまぶす。", "5分おいてから焼く。"]),
    ("komatsuna-nampla", ["小松菜は、茎と葉に分けておく。", "茎を強火で30秒炒めてから、葉を加えて1分。"]),
    ("mentai-potesala", ["ポテトサラダのじゃがいもは、濡らしたキッチンペーパーとラップで包む。", "600Wで5〜6分、竹串がすっと通るまで加熱する。"]),
]

WHICH = [
    ("ポテトサラダ、どっち派？", "ごろっと残す", "なめらかにつぶす"),
    ("冷奴にのせるなら、どっち派？", "しらすと大葉", "キムチ"),
    ("トマトのつまみ、どっち派？", "冷やして和える", "焼いて甘くする"),
    ("卵焼き、どっち派？", "だしの味", "甘い味"),
    ("クリームチーズにかけるなら、どっち派？", "かつお節と醤油", "はちみつと黒こしょう"),
    ("きゅうり、どっち派？", "たたいて割る", "細切り"),
    ("焼き物にレモン、どっち派？", "しぼる", "しぼらない"),
    ("つまみの並べ方、どっち派？", "小皿にいろいろ", "大皿に一品"),
    ("にんにく、どっち派？", "しっかり効かせる", "ほんのり"),
    ("家で作るつまみ、どっち派？", "レンジだけ", "フライパンで焼く"),
    ("薬味なら、どっち派？", "大葉", "みょうが"),
    ("じゃがいものつまみ、どっち派？", "バターと塩辛", "明太子とマヨネーズ"),
    ("ピリ辛のつまみ、どっち派？", "ラー油", "豆板醤"),
]

ASK = [
    "合うつまみは、お酒から選べます。",
    "決まったら、つまみを一品。",
    "お酒が決まると、つまみも決めやすい。",
    "冷蔵庫にあるもので、一品作れるかもしれません。",
    "火を使わないつまみなら、5分かからないものも。",
    "今夜の一品を、お酒から選ぶのも一つの手。",
    "今週のつまみで気になったものがあれば、それも。",
]
EVENING_DRINKS = ["sake", "beer", "shochu", "sour", "highball", "wine", "sake"]   # 21:00 の◯選のお酒（順に使う）


def load_plan():
    days = json.loads(SCHEDULE.read_text(encoding="utf-8"))["days"]
    return {d["date"]: d for d in days}


def main():
    plan = load_plan()
    uses = collections.Counter()
    posts = []

    def take(drink, n, avoid=()):
        """そのお酒に合う品を n 品（この2週間で2回目までの品。まだ使っていない品と、why にそのお酒の名前がある品を先に）。"""
        c = [r for r in bt.D["recipes"] if drink in r["drinks"] and r["id"] not in avoid
             and common.pick_rank(r, drink) == 0 and uses[r["id"]] == 0]
        c.sort(key=lambda r: (r["id"] in VIDEO, zlib.crc32(f"{drink}:{r['id']}".encode())))
        sel = [r["id"] for r in c[:n]]
        if len(sel) < n:
            sys.exit(f"{drink} に合う品が足りません")
        return sel

    def add(day, hh, mm, kind, lines, ids, tag=None, drink=None, url=False):
        if url:
            lines = list(lines) + [bt.URL]
            tag = None                     # URLを入れる本は行数に収めるためハッシュタグを外す
        p = bt.post(day, hh, mm, kind, lines, ids, tag)
        if drink:
            p["drink"] = drink
        uses.update(ids)
        posts.append(p)

    ask_k = ev_k = 0
    for k in range(DAYS):
        day = START + datetime.timedelta(days=k)
        ds = day.isoformat()
        wd = "月火水木金土日"[day.weekday()]
        v = plan[ds]["video"]
        # 11:05
        rid, lines = TIPS[k]
        add(day, 11, 5, "小ワザ", ["小ワザ。"] + lines, [rid], "#おつまみ")
        # 15:05
        q, a, b = WHICH[k]
        add(day, 15, 5, "どっち派", [q, f"A {a}", f"B {b}", "返信でAかBを。"], [])
        # 17:05 リールの品
        rid, drink = v["items"][0], v["drink"]
        add(day, 17, 5, "今夜の一品", bt.tonight_lines(rid, drink), [rid], common.DRINK_TAGS[drink], drink)
        # 19:05
        url = ds in URL_DAYS
        if v["type"] == "list":
            rid = v["items"][1]
            add(day, 19, 5, "今夜の一品", bt.tonight_lines(rid, drink), [rid], common.DRINK_TAGS[drink], drink, url)
        else:
            ids = take(drink, 3, avoid=v["items"])
            lines = [f"{DRINK[drink]}に合う、つまみ3品。"] + [f"{R[i]['name']}（{R[i]['min']}分・{TOOL[R[i]['tool']]}）" for i in ids]
            add(day, 19, 5, "◯選", lines, ids, common.DRINK_TAGS[drink], drink, url)
        # 21:00
        if k % 2 == 0:
            head = f"{wd}曜の夜、なに飲みますか。" if wd in "金土日" else "今夜はなに飲みますか。"
            add(day, 21, 0, "問いかけ", [head, ASK[ask_k % len(ASK)], "返信で教えてください。"], [])
            ask_k += 1
        else:
            drink = EVENING_DRINKS[ev_k % len(EVENING_DRINKS)]
            if drink == v["drink"]:
                drink = EVENING_DRINKS[(ev_k + 1) % len(EVENING_DRINKS)]
            ev_k += 1
            ids = take(drink, 3)
            lines = [f"{DRINK[drink]}に合う、つまみ3品。"] + [f"{R[i]['name']}（{R[i]['min']}分・{TOOL[R[i]['tool']]}）" for i in ids]
            add(day, 21, 0, "◯選", lines, ids, common.DRINK_TAGS[drink], drink)

    errors = bt.check(posts, start=START, max_which=1)
    if len(posts) != DAYS * 5:
        errors.append(f"件数が {len(posts)}")
    if errors:
        sys.exit("\n".join(errors))
    for p in posts:
        p.pop("drink", None)
    OUT.write_text(json.dumps(posts, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    bt.OUT = OUT
    bt.summary(posts, [])


# この2週間の動画・カルーセルに出す品（Threads の◯選では後回しにする）
_plan = json.loads(SCHEDULE.read_text(encoding="utf-8"))["days"] if SCHEDULE.exists() else []
VIDEO = {i for d in _plan for i in d["video"]["items"]} | {d["carousel"]["folder"] for d in _plan if d.get("carousel")}

if __name__ == "__main__":
    main()
