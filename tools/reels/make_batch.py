#!/usr/bin/env python3
"""複数の動画（v2）をまとめて作る。

  python3 make_batch.py mugen-piman camembert-honey buta-kimchi
  python3 make_batch.py mugen-piman:highball buta-kimchi:sour   … 「id:お酒」でお酒を指定
  python3 make_batch.py list:beer:quick:3 list:wine list:highball:range:4   … ◯選型（list:お酒[:theme[:品数]]）
  python3 make_batch.py --hooks-file reels/hooks_<開始日>_<終了日>.json saba-lemon:sour list:beer:quick   … フックの一覧を全部に渡す

1品で失敗しても残りは続け、最後に成功・失敗を一覧で出す。
2026-10-09：クラウドへ移すときに、カルーセル（2026-10-03から作らない）を外し、動画だけにした。
"""
import argparse
import sys
import traceback

import make_list_reel_v2 as make_list_reel
import make_reel_v2 as make_reel

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("items", nargs="+", metavar="id[:drink] | list:drink[:theme[:count]]")
ap.add_argument("--hooks-file", help="フックの一覧（JSON）。各動画にそのまま渡す")
a = ap.parse_args()
extra_all = ["--hooks-file", a.hooks_file] if a.hooks_file else []

results = []
for item in a.items:
    if item.startswith("list:"):
        parts = item.split(":")[1:]
        args = ["--drink", parts[0]]
        if len(parts) > 1 and parts[1]:
            args += ["--theme", parts[1]]
        if len(parts) > 2 and parts[2]:
            args += ["--count", parts[2]]
        kind, mod, name = "list", make_list_reel, item
    else:
        rid, _, drink = item.partition(":")
        args = [rid] + (["--drink", drink] if drink else [])
        kind, mod, name = "reel", make_reel, rid
    try:
        out = mod.main(args + extra_all)
        results.append(("OK", kind, name, str(out)))
    except (Exception, SystemExit) as e:
        traceback.print_exc()
        results.append(("NG", kind, name, str(e)))

print("\n--- 結果 ---")
for r in results:
    print("\t".join(r))
sys.exit(1 if any(r[0] == "NG" for r in results) else 0)
