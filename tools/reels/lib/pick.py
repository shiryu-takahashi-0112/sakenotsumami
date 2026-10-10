"""◯選型の品の選び方（make_list_reel_v2.py から使う）。

2026-10-09：クラウドのルーティーンで動かすため、~/sakenotsumami-cowork/make_list_reel.py から移した。
クラウドでは reels/queue・reels/posted が実行のたびに空になるので、
「もう出した品」は state/used.json（コミットしてある記録）も合わせて数える。
"""
import json
import sys
import zlib

import common

ROOT = common.ROOT
THEMES = {
    "quick": ("10分以内の", lambda r: r["min"] <= 10),
    "nofire": ("火を使わない", lambda r: r["tool"] == "none"),
    "range": ("レンジだけの", lambda r: r["tool"] == "range"),
    "all": ("", lambda r: True),
}
REEL_DIRS = [ROOT / "reels" / "posted", ROOT / "reels" / "queue"]
LEDGER = ROOT / "state" / "used.json"


def ledger_items():
    if not LEDGER.exists():
        return []
    return json.loads(LEDGER.read_text(encoding="utf-8")).get("items", [])


def used_so_far():
    """これまでに出した（出す予定の）品の id と、◯選の組み合わせ。"""
    ids, combos = set(), set()
    for base in REEL_DIRS:
        if not base.exists():
            continue
        for d in base.iterdir():
            if not d.is_dir():
                continue
            meta = d / "meta.json"
            if meta.exists():
                m = json.loads(meta.read_text(encoding="utf-8"))
                ids.update(m.get("ids", []))
                combos.add(frozenset(m.get("ids", [])))
            else:
                ids.add(d.name)          # 1品型のフォルダ名はレシピの id
    for x in ledger_items():
        if x.get("kind") != "reel":
            continue
        ids.update(x.get("ids", []))
        if x.get("type") == "list":
            combos.add(frozenset(x.get("ids", [])))
    return ids, combos


def pick(recipes, drink, theme, count):
    cond = THEMES[theme][1]
    # 写真がまだ無い品（足したばかりのレシピ）は、動画にできないので外す
    cands = [r for r in recipes if drink in r["drinks"] and cond(r) and (common.IMAGES / f"{r['id']}.jpg").exists()]
    if len(cands) < count:
        sys.exit(f"条件に合うレシピが {len(cands)} 品しかありません（drink={drink} theme={theme} count={count}）")
    ids, combos = used_so_far()
    # まだ出していない品 → why にそのお酒の名前がある品／お酒の名前が無い品（common.pick_rank）→ id から決まる順
    key = lambda r: (r["id"] in ids, common.pick_rank(r, drink), zlib.crc32(f"{drink}:{theme}:{r['id']}".encode()))
    order = sorted(cands, key=key)
    # すでに出した組み合わせと同じにならないよう、ずらしながら選ぶ
    for i in range(len(order) - count + 1):
        sel = order[i:i + count]
        if frozenset(r["id"] for r in sel) not in combos:
            return sel
    return order[:count]
