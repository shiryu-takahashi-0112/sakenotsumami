#!/usr/bin/env python3
"""サケノツマミの Threads の投稿文を、2026-10-30〜11-05 の7日分（1日5本・35本）作る。

  python3 postboard/build_threads_2026-10-30_11-05.py

出力: postboard/threads_2026-10-30_11-05.json
文の部品と確認は postboard/build_threads.py のものを使う（禁止語・行数・文字数・末尾の注意表示・
ハッシュタグ・絵文字・URLの回数・同じ品の回数・お酒のずれ）。

2026-10-09・Shiryuの指示で、15:05は「どっち派」をやめ、大喜利・投票・ツッコミを日ごとに順に回す
（返信しやすい形で終える）。21:00の「問いかけ」の日は、家飲み・つまみのあるあるにする
（◯選の日はそのまま）。お手本は postboard/humor_2026-10-12_10-29.json。
2026-10-12：Threads に「同じ投稿やコメントを繰り返す」スパムとして投稿を消されたため、書き分けの決まりを入れた
（CLAUDE.md「Threadsで同じ文・同じ形を繰り返さない」、確認は postboard/variety.py）。
  - 自分で付ける返信（self_reply）は使わない（10/10 に始めた「レシピはこちら👇＋URL」は取りやめ）
  - 「小ワザ。」「今夜の一品は、」「〜に合う、つまみ3品。」を毎日の1行目にしない。1行目は回ごとに形を変える
    （variety.TONIGHT_HEADS・LIST_HEADS を順に使う。「今夜の一品」の言葉は1日1回まで、毎日は使わない）
  - 「トースターで10分。」のような時間だけの行は作らない（毎日同じ文になる）。料理名とつなげて1文にする
  - URLは本文に7日で2本まで。前に置く文は毎回変える（URL_LEADS）
  - Postboard の公開済み・予定（直近14日〜）と合わせて、同じ文・1行目の重なりを確かめてから書き出す
  ※ 10/30〜11/05 の予約済み35本は、10/12 に ~/sakenotsumami-cowork/postboard/antispam_rewrite.json の文へ差し替えた。
    このファイルは来週からの写し元として直したもの。実行しても、すでに予約済みの時刻は schedule_threads.py が飛ばす。

写して使うとき（週の作り足し）:
  1. START・DAYS・SCHEDULE・OUT・URL_DAYS と、TIPS・HUMOR・TONIGHT・LIST_SECOND・SINGLE_EVENING・ALARUARU・EVENING_LIST を差し替える
  2. TIPS の1行目は料理名や手順から始め、「小ワザ。」を置かない。HUMOR の締めの文（「返信でどうぞ。」など）は毎回変える
  3. python3 postboard/build_threads_<期間>.py を実行し、指摘が0件になるまで直す（variety の指摘も止まる）

| 時刻 | 型 | 中身 |
|---|---|---|
| 11:05 | 小ワザ | 手順にあるコツを1つ（1行目に「小ワザ。」を置かない） |
| 15:05 | 大喜利／投票／ツッコミ | 日ごとに順に回す。返信しやすい形で終える |
| 17:05 | 今夜の一品 | その日のリール（schedule/2026-10-30_2026-11-05.json）の品。◯選型の日は1品目。1行目は回ごとに形を変える |
| 19:05 | 今夜の一品／◯選 | 1品型の日は同じお酒に合う3品、◯選型の日はリールの2品目。URLは週2回まで |
| 21:00 | あるある／◯選 | 1品型の日（問いかけの日）はあるある、◯選型の日はそのまま |
"""
import collections
import datetime
import importlib.util
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import variety  # noqa: E402

spec = importlib.util.spec_from_file_location("bt", HERE / "build_threads.py")
bt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bt)
common, R, DRINK, TOOL = bt.common, bt.R, bt.DRINK, bt.TOOL

START = datetime.date(2026, 10, 30)
DAYS = 7
SCHEDULE = bt.ROOT / "schedule" / "2026-10-30_2026-11-05.json"
OUT = HERE / "threads_2026-10-30_11-05.json"
URL_DAYS = {"2026-11-02", "2026-11-05"}   # 本文にアプリのURLを入れる日（7日で2本まで。前の週の最後のURLとも7日あける）
URL_LEADS = [   # URLの前に置く文（回ごとに変える。同じ文を14日以内に使わない）
    "ほかのお酒に合うつまみも、アプリで探せます。",
    "作り方と分量は、アプリのページに。",
    "お酒を選ぶと、合うつまみがまとめて出てきます。",
    "材料と手順は、こちらから。",
]
TIP_TAGS = ["#おつまみ", "#おつまみレシピ", "#家飲み"]   # 小ワザのハッシュタグ（毎日同じにしない）

# ---- 11:05 小ワザ（手順にあるコツを1つ。TIPS済みの品は避けた）
TIPS = [
    ("yodare-dori", ["よだれ鶏は、切って赤い部分がないか確かめる。", "あれば30秒ずつ追加で加熱する。"]),
    ("hakusai-millefeuille", ["白菜と豚肉のミルフィーユは、加熱後に豚肉の色を確かめる。", "全部変わっていなければ、追加で加熱する。"]),
    ("furofuki-daikon", ["ふろふき大根の練り味噌は、大根と別に作る。", "味噌・砂糖・みりんを600Wで30秒加熱するだけ。"]),
    ("german-potato", ["ジャーマンポテトのじゃがいもは、先に600Wで4分加熱する。", "そのあとフライパンで焼き色をつける。"]),
    ("eringi-butter", ["エリンギは、包丁を使わず手で縦にさく。", "断面がでこぼこになり、味がしみやすい。"]),
    ("satsumaage-aburi", ["さつま揚げは、焼く前に浅く格子の切り込みを入れる。", "トースターでふくらみやすくなる。"]),
    ("nachos", ["ナチョスは、アルミホイルの上にチップスを広げる。", "焼いたあとに鉄板にくっつかない。"]),
]

# ---- 15:05 大喜利・投票・ツッコミ（2026-10-09〜。日ごとに順に回す。返信しやすい形で終える）
HUMOR = [
    ("大喜利", ["【大喜利】", "冷凍庫の奥から出てきた、謎の保存容器。", "開ける前の、ひとことをどうぞ。"]),   # 【大喜利】の見出しは9日に1回まで
    ("投票", ["週末の作り置き、どのタイプ？", "A 多めに作る　B その日の分だけ", "C 気づいたら無くなってる", "記号で答えてください。"]),
    ("ツッコミ", ["シンクに積まれた、", "使った鍋が1個のはずが2個。", "覚えのある人、返信でどうぞ。"]),
    ("大喜利", ["冷蔵庫に貼ったメモ「あとで使う」。", "その結末を、ひとことで。"]),
    ("投票", ["決め手は冷蔵庫か、お酒か、検索か。", "A 冷蔵庫にあるもので決める　B お酒から決める", "C とりあえず検索する", "つまみの決め方、記号で返信を。"]),
    ("ツッコミ", ["まな板の上、", "切るものより先に出した調味料の瓶。", "場所を取っている自覚、返信でどうぞ。"]),
    ("大喜利", ["皿洗いを後回しにする、言い訳を一つ。", "思いついたら返信をどうぞ。"]),
]

# ---- 17:05 今夜の一品（その日のリールのお酒に合わせる）
TONIGHT = [
    ("kimchi-yakko", "beer"),           # 10/30 リール：ビール・10分以内の3選
    ("mushroom-ajillo", "wine"),        # 10/31 リール：マッシュルームのアヒージョ（ワイン）
    ("enoki-nametake", "shochu"),       # 11/1 リール：焼酎の3選
    ("yakinasu", "sake"),               # 11/2 リール：焼きなす（日本酒）
    ("sunagimo-garlic", "sour"),        # 11/3 リール：レモンサワーの3選
    ("chikuwa-isobe", "highball"),      # 11/4 リール：ちくわの磯辺揚げ焼き（ハイボール）
    ("sausage-cabbage", "beer"),        # 11/5 リール：ビール・レンジの3選
]

# ---- 19:05：◯選型の日はリールの2品目（今夜の一品）。1品型の日は同じお酒に合う3品（◯選）
LIST_SECOND = {  # 日付 → (id, drink)   ◯選型の日だけ
    "2026-10-30": ("ika-butter", "beer"),
    "2026-11-01": ("satsumaage-aburi", "shochu"),
    "2026-11-03": ("tunamayo-piman", "sour"),
    "2026-11-05": ("mentai-potesala", "beer"),
}
SINGLE_EVENING = {  # 日付 → (drink, [ids])   1品型の日だけ（その日の1品とは別の3品）
    "2026-10-31": ("wine", ["tomato-marinade", "namaham-cheese", "celery-asazuke"]),
    "2026-11-02": ("sake", ["shirasu-yakko", "atsuage-miso", "nagaimo-ume"]),
    "2026-11-04": ("highball", ["butabara-moyashi", "broccoli-okakamayo", "zasai-tofu"]),
}

# ---- 21:00：1品型の日（問いかけの日）はあるある。◯選型の日はそのまま◯選
ALARUARU = {
    "2026-10-31": ["土曜の買い出し。", "「一品だけ」のつもりが、", "レジではいつも三品分。"],
    "2026-11-02": ["月曜の夜は、台所に立つ気力が半分。", "それでも、つまみだけは一品作る。", "そこだけは譲れない。"],
    "2026-11-04": ["水曜の夜。", "冷蔵庫の野菜室を見て、", "献立よりつまみが先に決まる。"],
}
EVENING_LIST = {  # 日付 → (drink, [ids])   ◯選型の日だけ
    "2026-10-30": ("sake", ["aburaage-natto", "oil-sardine", "ika-butter"]),
    "2026-11-01": ("wine", ["asparagus-cheese", "negi-grill", "kabocha-cheese-salad"]),
    "2026-11-03": ("highball", ["mentai-dip", "zasai-tofu", "chikuwa-isobe"]),
    "2026-11-05": ("shochu", ["maguro-yukke", "enoki-nametake", "yakinasu"]),
}


HISTORY = []   # Postboard の公開済み・予定（main で読む）


def ctx(posts):
    return HISTORY + posts


def at(day, hh, mm):
    return f"{day.isoformat()}T{hh:02d}:{mm:02d}:00+09:00"


K = {"tonight": 0, "list": 0}   # 1行目の型の順番（選んだ型の次から試す）


def tonight(rid, drink, when, posts):
    """「今夜の一品」の本文。1行目は回ごとに形を変え（variety.TONIGHT_HEADS から、重ならないものを選ぶ）、時間だけの行は作らない。"""
    lines = bt.tonight_lines(rid, drink)[2:]          # 合うお酒の説明の文だけを使う
    r = R[rid]
    head, K["tonight"] = variety.pick(variety.TONIGHT_HEADS, K["tonight"], when, ctx(posts), "\n".join(lines),
                                      name=r["name"], mt=bt.mt(rid), min=r["min"], how=variety.HOW[r["tool"]])
    return [head] + lines


def list_lines(drink, ids, when, posts):
    head, K["list"] = variety.pick(variety.LIST_HEADS, K["list"], when, ctx(posts), drink=DRINK[drink])
    return [head] + [f"{R[i]['name']}（{R[i]['min']}分・{TOOL[R[i]['tool']]}）" for i in ids]


def main():
    HISTORY[:] = variety.load_history()
    posts = []
    nu = 0      # URLの前に置く文の順番
    for k in range(DAYS):
        day = START + datetime.timedelta(days=k)
        ds = day.isoformat()
        is_list = ds in LIST_SECOND
        # 11:05
        rid, lines = TIPS[k]
        posts.append(bt.post(day, 11, 5, "小ワザ", lines, [rid], TIP_TAGS[k % len(TIP_TAGS)]))
        # 15:05
        kind, lines = HUMOR[k]
        posts.append(bt.post(day, 15, 5, kind, lines, []))
        # 17:05 今夜の一品
        rid, drink = TONIGHT[k]
        p = bt.post(day, 17, 5, "今夜の一品", tonight(rid, drink, at(day, 17, 5), posts), [rid], common.DRINK_TAGS[drink])
        p["drink"] = drink
        posts.append(p)
        # 19:05
        url_day = ds in URL_DAYS
        if is_list:
            rid, drink = LIST_SECOND[ds]
            lines = tonight(rid, drink, at(day, 19, 5), posts)
            if url_day:
                lines = lines + [URL_LEADS[nu % len(URL_LEADS)], bt_url()]
                nu += 1
            p = bt.post(day, 19, 5, "今夜の一品", lines, [rid], None if url_day else common.DRINK_TAGS[drink])
        else:
            drink, ids = SINGLE_EVENING[ds]
            lines = list_lines(drink, ids, at(day, 19, 5), posts)
            if url_day:
                lines = lines + [URL_LEADS[nu % len(URL_LEADS)] + bt_url()]
                nu += 1
            p = bt.post(day, 19, 5, "◯選", lines, ids, None if url_day else common.DRINK_TAGS[drink])
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

    errors = bt.check(posts, start=START)
    if len(posts) != DAYS * 5:
        errors.append(f"件数が {len(posts)}")
    # 書き分けの確認（2026-10-12〜）：Postboard の公開済み・予定と合わせて、同じ文・1行目の重なり・URL・「今夜の一品」の回数
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


def bt_url():
    return bt.URL


if __name__ == "__main__":
    main()
