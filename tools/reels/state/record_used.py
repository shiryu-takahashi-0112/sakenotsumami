#!/usr/bin/env python3
"""投稿一覧（schedule/*.json）に入れた動画の品を、state/used.json（これまで出した品の記録）に足す。

  python3 state/record_used.py schedule/<開始日>_<終了日>.json

クラウドでは reels/queue・reels/posted が実行のたびに空になるので、品選び（lib/pick.py）と
次の週の作り足しで「もう出した品」が分かるよう、予約に入れたあとでこれを流してコミットする。
同じフォルダがすでにあれば足さない（何度流してもよい）。
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LEDGER = ROOT / "state" / "used.json"

data = json.loads(LEDGER.read_text(encoding="utf-8")) if LEDGER.exists() else {"items": []}
have = {(x.get("kind"), x.get("folder")) for x in data["items"]}
n = 0
for d in json.loads((ROOT / sys.argv[1]).read_text(encoding="utf-8"))["days"]:
    v = d["video"]
    if ("reel", v["folder"]) in have:
        continue
    item = {"date": d["date"], "kind": "reel", "type": v["type"], "folder": v["folder"], "drink": v.get("drink"), "ids": v["items"]}
    data["items"].append(item)
    have.add(("reel", v["folder"]))
    n += 1
data["items"].sort(key=lambda x: (x.get("date") or "9999", x["folder"]))
LEDGER.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("足した件数", n)
