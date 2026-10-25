#!/usr/bin/env python3
"""2026-11-13〜11-19 の投稿一覧（動画のみ）を作る。形は build_schedule_2026-11-06_11-12.py と同じで、
カルーセルは作らない（2026-10-07にShiryuが「Instagramは動画だけ」と決定）。

  python3 schedule/build_schedule_2026-11-13_2026-11-19.py

出力: schedule/2026-11-13_2026-11-19.md と .json（日付は実際に投稿する日付）

品の選び方（2026-10-03に決めたもの）:
  まだどこにも出していない品（state/used.json に無い）から、お酒6種類がまんべんなく出るように選んだ。
"""
import collections
import datetime
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "lib"))
import common  # noqa: E402

APP_URL = "https://osakenomitai.com/sakenotsumami/"
SOURCES = ["instagram", "tiktok", "youtube"]
WEEKDAY = "月火水木金土日"
NAME = "2026-11-13_2026-11-19"

D = common.load_all()
R = {r["id"]: r for r in D["recipes"]}
DRINK = {x["id"]: x["name"] for x in D["drinks"]}
THEME = {"quick": "10分以内", "nofire": "火を使わない", "range": "レンジ", "all": "全部"}

# (日付, 型, お酒, theme, 品, フォルダ名の上書き)   1品型＝月・水・土、◯選型＝火・木・金・日（金曜はビールかハイボール）
PLAN = [
    ("2026-11-13", "list", "highball", "nofire", ["salmon-poke", "saladchicken-bangbangji", "negi-chashu"], None),
    ("2026-11-14", "single", "wine", None, ["hotate-butter"], None),
    ("2026-11-15", "list", "shochu", "quick", ["roastbeef-yukke", "ninjin-shirishiri", "ika-mekabu"], None),
    ("2026-11-16", "single", "sour", None, ["buta-negishio-lemon"], None),
    ("2026-11-17", "list", "sake", "range", ["shiokara-jagabutter", "shintama-range", "okura-okaka"], None),
    ("2026-11-18", "single", "shochu", None, ["buri-teriyaki"], None),
    ("2026-11-19", "list", "sour", "all", ["tomato-tamago", "zucchini-namul", "butamaki-okura"], None),
]
CAROUSELS = {}   # Instagramは動画だけ（2026-10-07決定）。カルーセルは新規に作らない


def url(source):
    return f"{APP_URL}?utm_source={source}&utm_medium=social&utm_campaign=launch"


def where(kind, folder):
    """queue にあればそこ、投稿済みで posted へ移っていればそちら。"""
    q = ROOT / kind / "queue" / folder
    p = ROOT / kind / "posted" / folder
    return p if not q.exists() and p.exists() else q


def list_folder(drink, theme, ids):
    for d in sorted([*(ROOT / "reels" / "queue").glob(f"list-{drink}-{theme}-*"),
                     *(ROOT / "reels" / "posted").glob(f"list-{drink}-{theme}-*")]):
        m = json.loads((d / "meta.json").read_text(encoding="utf-8"))
        if m["ids"] == ids:
            return d.name
    sys.exit(f"◯選型の動画が queue にありません: {drink} {theme} {ids}")


def main():
    days, errors, uses = [], [], collections.Counter()
    for date, typ, drink, theme, ids, folder_override in PLAN:
        day = datetime.date.fromisoformat(date)
        wd = WEEKDAY[day.weekday()]
        if typ == "single":
            folder = folder_override or ids[0]
            title = f"1品型：{R[ids[0]]['name']}（{DRINK[drink]}）"
            if wd not in "月水土":
                errors.append(f"{date}: 1品型は月・水・土")
            text, is_catch = common.pairing_text(R[ids[0]], drink)
            if is_catch or not common.fits(text, drink):
                errors.append(f"{date}: 合う理由が見出しのお酒の話になっていない")
        else:
            folder = list_folder(drink, theme, ids)
            title = f"◯選型：{DRINK[drink]}・{THEME[theme]}・{len(ids)}品（" + "／".join(R[i]["name"] for i in ids) + "）"
            if wd not in "火木金日":
                errors.append(f"{date}: ◯選型は火・木・金・日")
            if wd == "金" and drink not in ("beer", "highball"):
                errors.append(f"{date}: 金曜はビールかハイボール")
        vdir = where("reels", folder)
        for f in ("reel.mp4", "caption.txt", "cover.jpg"):
            if not (vdir / f).exists():
                errors.append(f"{date}: {vdir / f} がありません")
        if (vdir / "caption.txt").exists():
            common.check_banned((vdir / "caption.txt").read_text(encoding="utf-8"))
        uses.update(ids)
        days.append({
            "date": date, "weekday": wd,
            "video": {"type": typ, "folder": folder, "title": title, "drink": drink, "items": ids,
                      "files": {"mp4": f"reels/queue/{folder}/reel.mp4", "caption": f"reels/queue/{folder}/caption.txt",
                                "cover": f"reels/queue/{folder}/cover.jpg"},
                      "platforms": ["instagram", "tiktok", "youtube"]},
            "carousel": None,
            "urls": {s: url(s) for s in SOURCES},
        })
    over = {k: v for k, v in uses.items() if v >= 2}
    if over:
        errors.append(f"2回以上出る品: {over}")
    if errors:
        sys.exit("\n".join(errors))
    out = ROOT / "schedule"
    (out / f"{NAME}.json").write_text(json.dumps({
        "period": ["2026-11-13", "2026-11-19"], "app_url": APP_URL,
        "post_time": {"reel": "12:00"},
        "utm": {"medium": "social", "campaign": "launch", "sources": SOURCES}, "days": days,
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (out / f"{NAME}.md").write_text(markdown(days), encoding="utf-8")
    print(out / f"{NAME}.md")
    print(out / f"{NAME}.json")
    print("お酒の回数:", dict(collections.Counter(DRINK[d["video"]["drink"]] for d in days)))


def markdown(days):
    L = ["# サケノツマミ 投稿一覧（2026-11-13〜11-19）", "",
         "11/13 から7日分の、動画の一覧（Instagramは動画だけ、カルーセルは作らない）。",
         "日付は実際に投稿する日付。",
         "Threads は別の一覧（`postboard/threads_2026-11-13_11-19.json`）で、ここには載せていない。",
         "作り直しは `python3 schedule/build_schedule_2026-11-13_2026-11-19.py`（同じ内容の `.json` も出る）。", "",
         "### 毎日やること", "",
         "| 順 | 投稿先 | 使うもの |", "|---|---|---|",
         "| 1 | Instagram リール・TikTok・YouTube ショート（12:00） | その日の動画フォルダの `reel.mp4`。キャプションは `caption.txt` |",
         "",
         "> **守ること**",
         "> - 投稿が済んだ動画は `reels/queue/<フォルダ>` から `reels/posted/` へ移す。",
         "> - キャプションの見出しと、ハッシュタグ5個が入っているかを確かめてから投稿する（「※写真は…」「お酒は20歳…」の2行は2026-10-07から入れない）。",
         "",
         "### プロフィールのリンク", "",
         "| SNS | URL |", "|---|---|"]
    for s in SOURCES:
        L.append(f"| {s} | `{url(s)}` |")
    L += ["", "### 7日の一覧", "", "| 日 | 動画 |", "|---|---|"]
    for d in days:
        L.append(f"| {d['date'][5:]}（{d['weekday']}） | {d['video']['title']} |")
    for d in days:
        v = d["video"]
        L += ["", f"### {d['date']}（{d['weekday']}）", "",
              "#### 動画（Instagram リール・TikTok・YouTube ショート）", "",
              f"- 内容：{v['title']}",
              f"- フォルダ：`reels/queue/{v['folder']}/`（`reel.mp4`・`caption.txt`・`cover.jpg`）"]
    L += ["", "### 決め方の背景", "",
          "- 1品型は月・水・土、◯選型は火・木・金・日。金曜（11/13）はハイボールの◯選。",
          "- 15品すべて、まだどこにも出していない品（state/used.json に無い）から選んだ。",
          "- お酒は highball・wine・shochu・sour・sake・shochu・sour の7本で、6種類がまんべんなく出るようにした。"]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
