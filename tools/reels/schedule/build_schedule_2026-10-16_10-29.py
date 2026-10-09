#!/usr/bin/env python3
"""2026-10-16〜10-29 の投稿一覧（動画とカルーセル）を作る。形は build_schedule.py と同じで、Threads・X の本文の欄は無い。

  python3 schedule/build_schedule_2026-10-16_10-29.py

出力: schedule/2026-10-16_2026-10-29.md と .json（日付は実際に投稿する日付）
動画・カルーセルのフォルダが queue に無い、キャプションに禁止語がある、同じ品が2週間で2回以上動画・カルーセルに出る、
1品型の合う理由が見出しのお酒とずれている、のどれかがあれば止まる。

品の選び方（2026-10-03 に決めたもの。作り直すときはここを直す）:
  まだどこにも出していない品 → Threads だけで出した品 → 動画・カルーセルで出した品 の順に、
  why にそのお酒の名前がある品（common.pick_rank）を先に選んだ。お酒は14本で6種類がそれぞれ2〜3回。
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
NAME = "2026-10-16_2026-10-29"

D = common.load_all()
R = {r["id"]: r for r in D["recipes"]}
DRINK = {x["id"]: x["name"] for x in D["drinks"]}
THEME = {"quick": "10分以内", "nofire": "火を使わない", "range": "レンジ", "all": "全部"}

# (日付, 型, お酒, theme, 品)   1品型＝月・水・土、◯選型＝火・木・金・日（金曜はビールかハイボール）
PLAN = [
    ("2026-10-16", "list", "highball", "quick", ["butabara-moyashi", "salmon-marinade", "tako-carpaccio"]),
    ("2026-10-17", "single", "wine", None, ["bruschetta"]),
    ("2026-10-18", "list", "sake", "all", ["avocado-wasabi", "hakusai-millefeuille", "eringi-butter"]),
    ("2026-10-19", "single", "beer", None, ["nachos"]),
    ("2026-10-20", "list", "sour", "all", ["nira-chijimi", "yaki-tomato", "dakgalbi"]),
    ("2026-10-21", "single", "shochu", None, ["shirasu-yakko"]),
    ("2026-10-22", "list", "wine", "all", ["asparagus-cheese", "negi-grill", "kabocha-cheese-salad"]),
    ("2026-10-23", "list", "beer", "quick", ["shiodare-cabbage", "onion-okaka", "shungiku-salad"]),
    ("2026-10-24", "single", "sake", None, ["iburigakko-cheese"]),
    ("2026-10-25", "list", "shochu", "all", ["maguro-yukke", "atsuage-miso", "nasu-chukadare"]),
    ("2026-10-26", "single", "highball", None, ["zasai-tofu"]),
    ("2026-10-27", "list", "wine", "all", ["caprese", "shiitake-mayo", "tomato-marinade"]),
    ("2026-10-28", "single", "sour", None, ["chicken-negishio"]),
    ("2026-10-29", "list", "highball", "all", ["range-mapo", "shogayaki", "ebi-chili"]),
]
CAROUSELS = {   # 日付 → (id, お酒)
    "2026-10-20": ("salmon-foil", "wine"),
    "2026-10-22": ("garlic-shrimp", "beer"),
    "2026-10-27": ("piman-maruyaki", "shochu"),
    "2026-10-29": ("sunagimo-garlic", "sour"),
}


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
    for date, typ, drink, theme, ids in PLAN:
        day = datetime.date.fromisoformat(date)
        wd = WEEKDAY[day.weekday()]
        if typ == "single":
            folder = ids[0]
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
        car = None
        if date in CAROUSELS:
            cid, cdrink = CAROUSELS[date]
            cdir = where("carousel", cid)
            if not all((cdir / f).exists() for f in ["01.png", "02.png", "03.png", "04.png", "05.png", "caption.txt"]):
                errors.append(f"{date}: カルーセル {cdir} がそろっていません")
            else:
                cap = (cdir / "caption.txt").read_text(encoding="utf-8")
                common.check_banned(cap)
                if not cap.startswith(f"{DRINK[cdrink]}に合う"):
                    errors.append(f"{date}: カルーセルのお酒が {cdrink} でない")
            uses[cid] += 1
            car = {"folder": cid, "name": R[cid]["name"], "drink": cdrink,
                   "files": [f"carousel/queue/{cid}/{i:02d}.png" for i in range(1, 6)],
                   "caption": f"carousel/queue/{cid}/caption.txt"}
        days.append({
            "date": date, "weekday": wd,
            "video": {"type": typ, "folder": folder, "title": title, "drink": drink, "items": ids,
                      "files": {"mp4": f"reels/queue/{folder}/reel.mp4", "caption": f"reels/queue/{folder}/caption.txt",
                                "cover": f"reels/queue/{folder}/cover.jpg"},
                      "platforms": ["instagram", "tiktok", "youtube"]},
            "carousel": car,
            "urls": {s: url(s) for s in SOURCES},
        })
    over = {k: v for k, v in uses.items() if v >= 2}
    if over:
        errors.append(f"2回以上出る品: {over}")
    if errors:
        sys.exit("\n".join(errors))
    out = ROOT / "schedule"
    (out / f"{NAME}.json").write_text(json.dumps({
        "period": ["2026-10-16", "2026-10-29"], "app_url": APP_URL,
        "post_time": {"reel": "18:00", "carousel": "12:05"},
        "utm": {"medium": "social", "campaign": "launch", "sources": SOURCES}, "days": days,
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (out / f"{NAME}.md").write_text(markdown(days), encoding="utf-8")
    print(out / f"{NAME}.md")
    print(out / f"{NAME}.json")
    print("お酒の回数:", dict(collections.Counter(DRINK[d["video"]["drink"]] for d in days)))


def markdown(days):
    L = ["# サケノツマミ 投稿一覧（2026-10-16〜10-29）", "",
         "10/16 から2週間分の、動画とカルーセルの一覧。",
         "日付は実際に投稿する日付。",
         "Threads は別の一覧（`postboard/threads_2026-10-16_10-29.json`）で、ここには載せていない。",
         "作り直しは `python3 schedule/build_schedule_2026-10-16_10-29.py`（同じ内容の `.json` も出る）。", "",
         "### 毎日やること", "",
         "| 順 | 投稿先 | 使うもの |", "|---|---|---|",
         "| 1 | Instagram リール・TikTok・YouTube ショート（18:00） | その日の動画フォルダの `reel.mp4`。キャプションは `caption.txt` |",
         "| 2 | Instagram カルーセル（12:05、火・木だけ） | カルーセルフォルダの `01.png`〜`05.png` を順に。キャプションは `caption.txt` |",
         "",
         "> **守ること**",
         "> - 投稿が済んだ動画は `reels/queue/<フォルダ>` から `reels/posted/` へ、カルーセルは `carousel/queue/<id>` から `carousel/posted/` へ移す。",
         "> - キャプションの見出しと、ハッシュタグ5個が入っているかを確かめてから投稿する（「※写真は…」「お酒は20歳…」の2行は2026-10-07から入れない）。",
         "",
         "### プロフィールのリンク", "",
         "| SNS | URL |", "|---|---|"]
    for s in SOURCES:
        L.append(f"| {s} | `{url(s)}` |")
    L += ["", "### 2週間の一覧", "", "| 日 | 動画 | カルーセル |", "|---|---|---|"]
    for d in days:
        c = d["carousel"]
        L.append(f"| {d['date'][5:]}（{d['weekday']}） | {d['video']['title']} | "
                 f"{c['name'] + '（' + DRINK[c['drink']] + '）' if c else '―'} |")
    for d in days:
        v = d["video"]
        L += ["", f"### {d['date']}（{d['weekday']}）", "",
              "#### 動画（Instagram リール・TikTok・YouTube ショート）", "",
              f"- 内容：{v['title']}",
              f"- フォルダ：`reels/queue/{v['folder']}/`（`reel.mp4`・`caption.txt`・`cover.jpg`）", "",
              "#### カルーセル（Instagram）", ""]
        if d["carousel"]:
            c = d["carousel"]
            L += [f"- 内容：{c['name']}（{DRINK[c['drink']]}）",
                  f"- フォルダ：`carousel/queue/{c['folder']}/`（`01.png`〜`05.png`・`caption.txt`）"]
        else:
            L += ["- この日は無し"]
    L += ["", "### 決め方の背景", "",
          "- 1品型は月・水・土、◯選型は火・木・金・日。金曜（10/16・10/23）はハイボールとビールの◯選。",
          "- 品は、まだどこにも出していない品を先に使い、足りない分は Threads だけで出した品から選んだ。これまでの動画・カルーセルに出した品は使っていない。",
          "- どの品も、合う理由（why）に見出しのお酒の名前が出てくるものを選んだので、キャプションの一言は why のまま。",
          "- お酒は14本で、ハイボール・ワインが3回、ビール・日本酒・焼酎・レモンサワーが2回。カルーセルはワイン・ビール・焼酎・レモンサワー。"]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
