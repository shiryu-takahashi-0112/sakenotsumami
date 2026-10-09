#!/usr/bin/env python3
"""投稿一覧（schedule/*.json）のリールを、投稿管理ツール（Postboard）に予約として入れる。

  python3 postboard/schedule_instagram.py --schedule schedule/<開始日>_<終了日>.json
  python3 postboard/schedule_instagram.py --schedule schedule/<開始日>_<終了日>.json --dry   … 入れずに、入れる予定だけ出す

- リールは毎日12:00（日本時間。2026-10-08にShiryuが「リール投稿も12時に」と指示し、18時から変えた）。`--time` で変えられる。Instagram の @sakenotsumami.12（Postboard のアカウントID 4）。
- 動画（reel.mp4）は手元のファイルをそのまま POST /api/media に上げる（Postboard の R2 に置かれる）。
  表紙（cover.jpg）も上げ、両方の URL を registered.json に残す（クラウドで作った動画を、Mac の TikTok のルーティーンが取りに行けるように）。
- 入れたものは postboard/registered.json に残し、二重に入れない。あわせて、Postboard に同じ日（日本時間）の Instagram の予定がすでにあれば飛ばす（1日1本）。
- 鍵の扱いは postboard/pb.py（クラウドでは Authorization を付けない）。
- 2026-10-09：クラウドへ移すときに、カルーセル（2026-10-03から作らない。Mac の sips を使っていた）の部分を外した。
"""
import argparse
import datetime
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pb  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent.parent
JST = datetime.timezone(datetime.timedelta(hours=9))
REG = HERE / "postboard/registered.json"
reg = json.loads(REG.read_text()) if REG.exists() else {}


def upload(rel):
    p = HERE / rel
    t = {".mp4": "video/mp4", ".jpg": "image/jpeg"}[p.suffix]
    return pb.api("POST", "/api/media", form={"brand_id": str(pb.BRAND), "file": f"@{p};type={t}"})["media"]


def jst(day, hh, mm):
    return f"{day.isoformat()}T{hh:02d}:{mm:02d}:00+09:00"


ap = argparse.ArgumentParser()
ap.add_argument("--schedule", required=True)
ap.add_argument("--start", help="一覧の日付ではなく、この日から1日ずつ割り当てる（省くと一覧の日付のまま）")
ap.add_argument("--from-day", type=int, default=1)
ap.add_argument("--time", default="12:00", help="公開の時刻（日本時間、既定 12:00）")
ap.add_argument("--dry", action="store_true")
a = ap.parse_args()
days = json.loads((HERE / a.schedule).read_text())["days"]
start = datetime.date.fromisoformat(a.start) if a.start else None
taken = {x.astimezone(JST).date() for x in pb.taken_times(pb.IG)}
hh, mm = map(int, a.time.split(":"))
n = 0
for i, d in enumerate(days[a.from_day - 1:]):
    day = start + datetime.timedelta(days=i) if start else datetime.date.fromisoformat(d["date"])
    v = d["video"]
    key = f"reel:{v['folder']}"
    when = jst(day, hh, mm)
    if key in reg:
        continue
    if day in taken:
        print(day, "すでに Postboard にこの日のリールの予定があるので飛ばす", v["folder"])
        continue
    cap = (HERE / v["files"]["caption"]).read_text().strip()
    print(day, "リール", v["folder"])
    if a.dry:
        continue
    media = upload(v["files"]["mp4"])
    cover = upload(v["files"]["cover"]) if (HERE / v["files"].get("cover", "-")).is_file() else None
    pid = pb.api("POST", "/api/posts", {"brand_id": pb.BRAND, "account_ids": [pb.IG], "caption": cap, "media_ids": [media["id"]],
                                        "scheduled_at": when, "thumb_offset_ms": 0,   # フックの版は最初のコマが表紙
                                        "memo": f"サケノツマミ 投稿一覧 {d['date']} の分（{v['title']}）"})["id"]
    # TikTok（Mac のルーティーン）が動画・表紙・キャプションを Postboard から取れるよう、URL も残す
    reg[key] = {"post_id": pid, "scheduled": when, "media_url": media["url"], "cover_url": cover and cover["url"],
                "caption": cap}
    REG.write_text(json.dumps(reg, ensure_ascii=False, indent=1))
    n += 1
print("入れた件数", n)
