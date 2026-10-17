#!/usr/bin/env python3
"""Threads の投稿で、同じ文・同じ形を繰り返さないための部品と確認（2026-10-12〜）。

2026-10-12、Threads に「同じ投稿やコメントを繰り返す」スパムとして投稿を消された。
毎日の「レシピはこちら👇＋URL」の自分で付ける返信と、「今夜の一品は、」「小ワザ。」などの
決まった書き出しが原因と見て、次の決まりを作った（リポジトリ直下の CLAUDE.md「SNS」）。

  - 自分で付ける返信（self_reply）は使わない
  - アプリ・レシピのURLは、本文に入れるのを1日1本・7日で7本まで（2026-10-17 定例で週2本から変更）
  - 同じ文は14日のあいだに2回使わない
  - 1行目の最初の3文字が同じ投稿は、7日で2本まで（シリーズ名を1行目に置かない）
  - 「今夜の一品」の言葉は1日1回まで。「どっち派」は7日で2回まで

使い方（週の Threads の作成処理から）:

    import variety
    history = variety.load_history()          # Postboard の公開済み・予定（直近14日〜先）。取れなければ []
    errors = variety.check(posts, history)     # posts は [{"scheduled_at", "text", ...}]
    line = variety.tonight_head(k, name, mt)   # 「今夜の一品」の1行目を、回ごとに違う形で

単体で動かすと、Postboard にある Threads の予定と公開済みをまとめて確かめる:

    python3 postboard/variety.py            # 予定と直近14日の公開済みを確かめる
"""
import collections
import datetime
import re
import sys

JST = datetime.timezone(datetime.timedelta(hours=9))
WINDOW_HEAD = 7       # 1行目の書き出しを数える幅（日）
WINDOW_TEXT = 14      # 同じ文を使わない幅（日）
MAX_HEAD = 2          # 同じ3文字で始まる投稿の上限（WINDOW_HEAD のあいだ）
MAX_URL = 7           # URL入りの投稿の上限（7日）。1日1本（2026-10-17 定例）
MAX_WHICH = 2         # 「どっち派」の上限（7日）
SERIES = ("小ワザ", "今夜の一品", "【大喜利】")   # 1行目に毎日置かないシリーズ名

# ---- 「今夜の一品」の1行目（料理名と時間をつなげて1文にする。「トースターで10分。」だけの行は毎日同じ文になるため作らない）
#   {mt}＝「フライパンで8分」「火を使わず5分」、{min}＝分の数、{how}＝「フライパンで作る」「火を使わない」など
TONIGHT_HEADS = [
    "{name}、{mt}。",
    "{min}分でできる、{name}。",
    "つまみに{name}。{mt}。",
    "{name}は、{mt}。",
    "{how}、{name}。{min}分。",
    "{name}。かかるのは{min}分。",
]
HOW = {"pan": "フライパンで作る", "range": "レンジで作る", "toaster": "トースターで焼く", "none": "火を使わない"}

# ---- ◯選の1行目（お酒の名前や「つまみ3品」から始める形を毎日使わない）
LIST_HEADS = [
    "{drink}のそばに置きたい3品。",
    "3品そろえるなら、{drink}にはこれ。",
    "合わせるお酒が{drink}なら、この3品。",
    "迷ったときの、{drink}向きの3品。",
    "冷蔵庫と相談して決める、{drink}の3品。",
    "{drink}の夜に回したい、つまみを3つ。",
    "{drink}に合わせるなら、この3つ。",
]

# ---- 返信をうながす締めの文（「返信でどうぞ。」を毎回使わない）
CLOSERS = [
    "返信でどうぞ。",
    "ひとこと、返信で。",
    "思いついたら返信に。",
    "返信欄で待っています。",
    "答えは返信で。",
    "記号ひとつで、返信を。",
    "選んだものを返信で教えてください。",
    "あなたの家の場合を、返信で。",
]

URL_RE = re.compile(r"https?://|osakenomitai\.com")
ITEM_RE = re.compile(r"（\d+分・")          # ◯選の品の行（料理名（10分・レンジ））は文として数えない
VOTE_RE = re.compile(r"^[A-CＡ-Ｃ][ 　]")    # 投票の選択肢の行


def when(s):
    """'2026-10-12T02:05:00.000Z' / '2026-10-12T11:05:00+09:00' → 日本時間の datetime"""
    s = s.replace("Z", "+00:00")
    s = re.sub(r"\.\d+(?=[+-])", "", s)
    return datetime.datetime.fromisoformat(s).astimezone(JST)


def first_line(text):
    return text.strip().split("\n")[0].strip()


def head3(text):
    return first_line(text).replace(" ", "").replace("　", "")[:3]


def sentences(text):
    """同じ文の確認に使う文。ハッシュタグ・URL・◯選の品の行・投票の選択肢・短すぎるものは除く。"""
    out = []
    for line in text.split("\n"):
        line = line.strip()
        if (not line or line.startswith("#") or URL_RE.search(line) or ITEM_RE.search(line) or VOTE_RE.match(line)
                or re.fullmatch(r"【[^】]*】", line)):   # 【大喜利】などの見出しは、1行目の確認で数える
            continue
        for s in re.split(r"(?<=[。？！?!])", line):
            s = s.strip()
            if len(re.sub(r"[、。？！?!「」…\s]", "", s)) >= 5:
                out.append(s)
    return out


def choose(options, at, context, rest=""):
    """options（1行目の候補）のうち、context（履歴と作った分 [{scheduled_at, text}]）と合わせて
    1行目の重なり・同じ文に当たらない最初のものを返す。rest は1行目のあとに続く本文（同じ文の確認に使う）。
    どれも当たるときは最初の候補を返す（check で止まる）。"""
    t = when(at)
    near7 = [c for c in context if abs((when(c["scheduled_at"]) - t).total_seconds()) < WINDOW_HEAD * 86400]
    near14 = [c for c in context if abs((when(c["scheduled_at"]) - t).total_seconds()) < WINDOW_TEXT * 86400]
    used = {s for c in near14 for s in sentences(c["text"])}
    for o in options:
        h = head3(o)
        if sum(1 for c in near7 if head3(c["text"]) == h) >= MAX_HEAD:
            continue
        if set(sentences(o + "\n" + rest)) & used:
            continue
        if "今夜の一品" in o and any("今夜の一品" in c["text"] and when(c["scheduled_at"]).date() == t.date() for c in context):
            continue
        return o
    return options[0]


def rotate(templates, k, **kw):
    """k 番目から順に並べた候補（choose に渡す）。"""
    return [templates[(k + i) % len(templates)].format(**kw) for i in range(len(templates))]


def pick(templates, k, at, context, rest="", **kw):
    """k 番目の型から順に試し、重ならない最初の1行目を選ぶ。(1行目, 次に使う k) を返す。
    次の k は選んだ型の次にするので、同じ型が続けて出にくい。"""
    opts = rotate(templates, k, **kw)
    line = choose(opts, at, context, rest)
    i = opts.index(line)
    return line, k + i + 1


def tonight_head(k, name, mt):
    return TONIGHT_HEADS[k % len(TONIGHT_HEADS)].format(name=name, mt=mt)


def list_head(k, drink):
    return LIST_HEADS[k % len(LIST_HEADS)].format(drink=drink)


def closer(k):
    return CLOSERS[k % len(CLOSERS)]


def check(posts, history=(), max_head=MAX_HEAD):
    """posts（新しく作る分）を、history（Postboard の公開済み・予定）と合わせて確かめる。
    指摘は、新しく作る分が関わるものだけを返す。history に posts と同じ日時のものがあれば、posts の方を使う。"""
    errors = []
    new_at = {when(p["scheduled_at"]) for p in posts}
    items = [(when(p["scheduled_at"]), p, True) for p in posts]
    items += [(when(h["scheduled_at"]), h, False) for h in history if when(h["scheduled_at"]) not in new_at]
    items.sort(key=lambda x: x[0])

    for t, p, new in items:
        if new and p.get("self_reply"):
            errors.append(f"{t:%m/%d %H:%M}: 自分で付ける返信（self_reply）は使わない")

    def within(a, b, days):
        return abs((a - b).total_seconds()) < days * 86400

    # 1行目の書き出し
    for i, (t, p, new) in enumerate(items):
        if not new:
            continue
        h = head3(p["text"])
        same = [u for u, q, _ in items if within(u, t, WINDOW_HEAD) and head3(q["text"]) == h]
        # t を含む7日の幅のどこかで max_head を超えるか
        for start in same:
            n = sum(1 for u in same if start <= u < start + datetime.timedelta(days=WINDOW_HEAD))
            if n > max_head and start <= t < start + datetime.timedelta(days=WINDOW_HEAD):
                errors.append(f"{t:%m/%d %H:%M}: 1行目が「{h}」で始まる投稿が7日で{n}本（上限{max_head}）: {first_line(p['text'])}")
                break

    # 7日の本数で数えるもの（URL・どっち派）
    def count7(pred, limit, label):
        hits = [(u, q, new) for u, q, new in items if pred(q["text"])]
        for t, p, new in hits:
            if not new:
                continue
            for s, _, _ in hits:
                n = sum(1 for u, _, _ in hits if s <= u < s + datetime.timedelta(days=7))
                if n > limit and s <= t < s + datetime.timedelta(days=7):
                    errors.append(f"{t:%m/%d %H:%M}: {label}が7日で{n}本（上限{limit}）")
                    break
    count7(lambda x: bool(URL_RE.search(x)), MAX_URL, "URL入り")
    count7(lambda x: "どっち派" in x, MAX_WHICH, "「どっち派」")

    # 「今夜の一品」は1日1回
    by_day = collections.Counter(t.date() for t, p, _ in items if "今夜の一品" in p["text"])
    for t, p, new in items:
        if new and "今夜の一品" in p["text"] and by_day[t.date()] > 1:
            errors.append(f"{t:%m/%d %H:%M}: 「今夜の一品」が同じ日に{by_day[t.date()]}回")

    # 同じ文を14日のあいだに2回使わない
    seen = collections.defaultdict(list)
    for t, p, new in items:
        for s in set(sentences(p["text"])):
            seen[s].append((t, new))
    for s, uses in seen.items():
        for i, (t, new) in enumerate(uses):
            for u, new2 in uses[i + 1:]:
                if (new or new2) and within(t, u, WINDOW_TEXT):
                    errors.append(f"{u:%m/%d %H:%M}: 同じ文を14日以内に再使用（{t:%m/%d}）: {s}")
    # 重複を消して返す
    return list(dict.fromkeys(errors))


def load_history(account=2, days_back=WINDOW_TEXT):
    """Postboard の Threads（アカウント2）の、直近 days_back 日の公開済みと、これからの予定。取れなければ []。"""
    try:
        import pb
    except ImportError:
        import pathlib
        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
        import pb
    import os
    if os.environ.get("VARIETY_HISTORY"):     # 試すとき：Postboard の代わりに手元の JSON（[{scheduled_at, text}]）を履歴にする
        import json
        return json.load(open(os.environ["VARIETY_HISTORY"], encoding="utf-8"))
    since = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days_back)).strftime("%Y-%m-%d")
    out = []
    try:
        for tab, q in (("sent", f"&from={since}"), ("queue", "")):
            for p in pb.api("GET", f"/api/posts?tab={tab}&brand={pb.BRAND}&account={account}{q}")["posts"]:
                tg = next((x for x in p.get("targets", []) if x.get("account_id") == account), None)
                if not tg:
                    continue
                out.append({"scheduled_at": p["scheduled_at"], "text": tg.get("caption") or p.get("caption") or "",
                            "self_reply": "self_reply" in (tg.get("options") or ""), "id": p["id"]})
    except (Exception, SystemExit) as e:   # pb.api は失敗で sys.exit する
        print(f"注意：Postboard から履歴を取れなかった（{e}）。手元の分だけで確かめる", file=sys.stderr)
        return []
    return out


if __name__ == "__main__":
    hist = load_history()
    future = [h for h in hist if when(h["scheduled_at"]) > datetime.datetime.now(JST)]
    errs = check(future, hist)
    print(f"予定 {len(future)} 本・履歴 {len(hist)} 本を確認。指摘 {len(errs)} 件")
    for e in errs:
        print(" -", e)
    sys.exit(1 if errs else 0)
