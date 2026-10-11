#!/usr/bin/env python3
"""サケノツマミの Threads の投稿文を、2026-10-30〜11-05 の7日分（1日5本・35本）作る。

  python3 postboard/build_threads_2026-10-30_11-05.py

出力: postboard/threads_2026-10-30_11-05.json
文の部品と確認は postboard/build_threads.py のものを使う（禁止語・行数・文字数・末尾の注意表示・
ハッシュタグ・絵文字・URLの回数・同じ品の回数・お酒のずれ）。

2026-10-09・Shiryuの指示で、15:05は「どっち派」をやめ、大喜利・投票・ツッコミを日ごとに順に回す
（返信しやすい形で終える）。21:00の「問いかけ」の日は、家飲み・つまみのあるあるにする
（◯選の日はそのまま）。お手本は postboard/humor_2026-10-12_10-29.json。
2026-10-10・Shiryuの了承で、「今夜の一品」には毎日、そのレシピのページのURLを自分で付ける返信
（self_reply）で付ける。本文にはアプリのURLを週2回まで（common.URL＝旧来のアプリURL）。

| 時刻 | 型 | 中身 |
|---|---|---|
| 11:05 | 小ワザ | 手順にあるコツを1つ |
| 15:05 | 大喜利／投票／ツッコミ | 日ごとに順に回す。返信しやすい形で終える |
| 17:05 | 今夜の一品 | その日のリール（schedule/2026-10-30_2026-11-05.json）の品。◯選型の日は1品目。recipe URLをself_replyで付ける |
| 19:05 | 今夜の一品／◯選 | 1品型の日は同じお酒に合う3品、◯選型の日はリールの2品目（self_reply）。URLは週2回まで |
| 21:00 | あるある／◯選 | 1品型の日（問いかけの日）はあるある、◯選型の日はそのまま |
"""
import collections
import datetime
import importlib.util
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("bt", HERE / "build_threads.py")
bt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bt)
common, R, DRINK, TOOL = bt.common, bt.R, bt.DRINK, bt.TOOL

START = datetime.date(2026, 10, 30)
DAYS = 7
SCHEDULE = bt.ROOT / "schedule" / "2026-10-30_2026-11-05.json"
OUT = HERE / "threads_2026-10-30_11-05.json"
RECIPE_URL = "https://osakenomitai.com/sakenotsumami/recipes/{id}/?utm_source=threads&utm_medium=social&utm_campaign=konya"
URL_DAYS = {"2026-11-02", "2026-11-05"}   # 本文にアプリのURLを入れる日（週2回まで）

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
    ("大喜利", ["【大喜利】", "冷凍庫の奥から出てきた、謎の保存容器。", "開ける前の、ひとことをどうぞ。"]),
    ("投票", ["週末の作り置き、投票です。", "A 多めに作る　B その日の分だけ", "C 気づいたら無くなってる", "返信は記号で。"]),
    ("ツッコミ", ["シンクに積まれた、", "使った鍋が1個のはずが2個。", "覚えのある人、返信でどうぞ。"]),
    ("大喜利", ["【大喜利】", "冷蔵庫に貼ったメモ「あとで使う」。", "その結末を、ひとことで。"]),
    ("投票", ["今夜のつまみ、選び方投票です。", "A 冷蔵庫にあるもので決める　B お酒から決める", "C とりあえず検索する", "返信は記号で。"]),
    ("ツッコミ", ["まな板の上、", "切るものより先に出した調味料の瓶。", "場所を取っている自覚、返信でどうぞ。"]),
    ("大喜利", ["【大喜利】", "皿洗いを後回しにする、言い訳を一つ。", "返信でどうぞ。"]),
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


def self_reply(rid):
    return f"レシピはこちら👇\n{RECIPE_URL.format(id=rid)}"


def main():
    posts = []
    for k in range(DAYS):
        day = START + datetime.timedelta(days=k)
        ds = day.isoformat()
        is_list = ds in LIST_SECOND
        # 11:05
        rid, lines = TIPS[k]
        posts.append(bt.post(day, 11, 5, "小ワザ", ["小ワザ。"] + lines, [rid], "#おつまみ"))
        # 15:05
        kind, lines = HUMOR[k]
        posts.append(bt.post(day, 15, 5, kind, lines, []))
        # 17:05 今夜の一品（self_reply でレシピのURLを付ける）
        rid, drink = TONIGHT[k]
        p = bt.post(day, 17, 5, "今夜の一品", bt.tonight_lines(rid, drink), [rid], common.DRINK_TAGS[drink])
        p["self_reply"] = self_reply(rid)
        posts.append(p)
        # 19:05
        url_day = ds in URL_DAYS
        if is_list:
            rid, drink = LIST_SECOND[ds]
            lines = bt.tonight_lines(rid, drink)
            p = bt.post(day, 19, 5, "今夜の一品", lines + ([bt_url()] if url_day else []), [rid],
                        None if url_day else common.DRINK_TAGS[drink])
            p["self_reply"] = self_reply(rid)
        else:
            drink, ids = SINGLE_EVENING[ds]
            lines = [f"{DRINK[drink]}に合う、つまみ3品。"] + [f"{R[i]['name']}（{R[i]['min']}分・{TOOL[R[i]['tool']]}）" for i in ids]
            if url_day:
                lines = lines + [bt_url()]
            p = bt.post(day, 19, 5, "◯選", lines, ids, None if url_day else common.DRINK_TAGS[drink])
        p["drink"] = drink
        posts.append(p)
        # 21:00
        if ds in ALARUARU:
            posts.append(bt.post(day, 21, 0, "あるある", ALARUARU[ds], []))
        else:
            drink, ids = EVENING_LIST[ds]
            lines = [f"{DRINK[drink]}に合う、つまみ3品。"] + [f"{R[i]['name']}（{R[i]['min']}分・{TOOL[R[i]['tool']]}）" for i in ids]
            p = bt.post(day, 21, 0, "◯選", lines, ids, common.DRINK_TAGS[drink])
            p["drink"] = drink
            posts.append(p)

    errors = bt.check(posts, start=START)
    if len(posts) != DAYS * 5:
        errors.append(f"件数が {len(posts)}")
    if errors:
        sys.exit("\n".join(errors))
    OUT.write_text(json.dumps(posts, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    bt.OUT = OUT
    bt.summary(posts, [])


def bt_url():
    return bt.URL


if __name__ == "__main__":
    main()
