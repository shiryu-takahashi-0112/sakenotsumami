#!/usr/bin/env python3
"""Threads の投稿文（postboard/threads_*.json）を、投稿管理ツール（Postboard）に予約として入れる。

  python3 postboard/schedule_threads.py postboard/threads_<開始日>_<終了日>.json
  python3 postboard/schedule_threads.py postboard/threads_<開始日>_<終了日>.json --dry   … 入れずに、入れる予定だけ出す

- Threads の @sakenotsumami.12（Postboard のアカウントID 2）。
- すでに時刻を過ぎたものは入れない。入れたものは registered.json に残し、二重に入れない。
  あわせて Postboard の予定と同じ日時があれば飛ばす（クラウドでは registered.json が古いことがあるため）。
- 鍵の扱いは postboard/pb.py（クラウドでは Authorization を付けない）。
"""
import datetime
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pb  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent.parent
REG = HERE / "postboard/registered.json"
reg = json.loads(REG.read_text()) if REG.exists() else {}
args = [x for x in sys.argv[1:] if not x.startswith("--")]
dry = "--dry" in sys.argv
now = datetime.datetime.now(datetime.timezone.utc)
taken = pb.taken_times(pb.TH)
n = 0
for x in json.loads((HERE / args[0]).read_text()):
    key = f"threads:{x['scheduled_at']}"
    if key in reg:
        continue
    when = pb.parse(x["scheduled_at"])
    if when <= now:
        print("過ぎているので飛ばす", x["scheduled_at"])
        continue
    if when in taken:
        print("すでに Postboard に同じ時刻の予定があるので飛ばす", x["scheduled_at"])
        continue
    print(x["scheduled_at"], x["kind"])
    if dry:
        continue
    body = {"brand_id": pb.BRAND, "account_ids": [pb.TH], "caption": x["text"], "media_ids": [],
            "scheduled_at": x["scheduled_at"], "memo": f"サケノツマミ Threads（{x['kind']}）"}
    res = pb.api("POST", "/api/posts", body)
    reg[key] = {"post_id": res["id"], "kind": x["kind"]}
    REG.write_text(json.dumps(reg, ensure_ascii=False, indent=1))
    n += 1
print("入れた件数", n)
