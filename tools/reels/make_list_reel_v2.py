#!/usr/bin/env python3
"""◯選型の動画 v2（テンポを上げて約24秒にした版）。旧版 make_list_reel.py は旧版として残す。

  python3 make_list_reel_v2.py --drink sake --ids furofuki-daikon,creamcheese-okaka,daikon-hotate --out review/v2-sample/list
  python3 make_list_reel_v2.py --drink beer --theme quick          … 品の選び方は lib/pick.py
  python3 make_list_reel_v2.py --drink sake --ids ... --preview 0.5 3 8   … 指定秒のコマだけ（確認用）
  python3 make_list_reel_v2.py --drink sour --ids a,b,c --hook "一番合うのは、どれ？" --sub "レモンサワーに"
  python3 make_list_reel_v2.py --drink sour --ids a,b,c --hooks-file reels/hooks_2026-10-10_10-29.json   … フォルダ名で引く

冒頭のフック（2026-10-09〜）：--hook / --sub を渡すと、最初のコマから上にフック、下に写真を並べて出し、
0.3秒で写真が寄る。約1.8秒で1品目へ進む。表紙の静止画は足さず、最初のコマを cover.jpg にする。
キャプションの1行目もフックにする（元のキャプションは caption_v2.txt に残す）。--hook を渡さなければ従来どおり。

流れは video/list_reel_v2.html の先頭に書いてある。
画面に出す文はすべて recipes.js の値から作る（主な材料・ポイントの選び方は lib/v2.py）。
出力：reel.mp4（先頭に表紙0.5秒）・cover.jpg・caption.txt・meta.json。
2026-10-07にShiryuが承認し、現行の作り方になった。出力先は reels/queue/<名前>（--out で変更可）。
"""
import argparse
import json
import pathlib
import shutil
import sys
import zlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "lib"))
import common  # noqa: E402
import v2  # noqa: E402
from build import build_video  # noqa: E402
from pick import THEMES, pick  # noqa: E402

ROOT = common.ROOT


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--drink", required=True)
    ap.add_argument("--theme", default="all", choices=list(THEMES))
    ap.add_argument("--count", type=int, default=3, choices=[3, 4, 5])
    ap.add_argument("--ids")
    ap.add_argument("--out", help="出力フォルダ（省略時 reels/queue/<名前>）")
    ap.add_argument("--preview", nargs="+", type=float, metavar="秒")
    ap.add_argument("--keep-frames", action="store_true")
    ap.add_argument("--hook", help="冒頭のフック（14文字以内・1行）")
    ap.add_argument("--sub", help="フックの下の小さい1行（16文字以内・省略可）")
    ap.add_argument("--hooks-file", help="フックの一覧（JSON）。フォルダ名（--out の名前、無ければ list-<お酒>-<theme>-<6桁>）で引く")
    a = ap.parse_args(argv)

    d = common.load_all()
    drinks = {x["id"]: x["name"] for x in d["drinks"]}
    if a.drink not in drinks:
        sys.exit(f"--drink は {', '.join(drinks)} のどれかにしてください（指定: {a.drink}）")
    by_id = {r["id"]: r for r in d["recipes"]}
    if a.ids:
        ids = [x.strip() for x in a.ids.split(",") if x.strip()]
        miss = [x for x in ids if x not in by_id]
        if miss:
            sys.exit(f"レシピが見つかりません: {', '.join(miss)}")
        if not 3 <= len(ids) <= 5:
            sys.exit("--ids は3〜5品にしてください")
        sel = [by_id[x] for x in ids]
        for r in sel:
            if a.drink not in r["drinks"]:
                print(f"注意: {r['name']} のおすすめのお酒に {drinks[a.drink]} は入っていません", file=sys.stderr)
            if not THEMES[a.theme][1](r):
                print(f"注意: {r['name']} は theme={a.theme} の条件に合いません", file=sys.stderr)
    else:
        sel = pick(d["recipes"], a.drink, a.theme, a.count)

    n = len(sel)
    mid = THEMES[a.theme][0]
    head1 = f"{drinks[a.drink]}に合う、"
    head2 = f"つまみ{n}選"
    items = []
    for r in sel:
        photo = common.IMAGES / f"{r['id']}.jpg"
        if not photo.exists():
            sys.exit(f"写真がありません: {photo}")
        point, k = v2.point_line(r["steps"])
        items.append({
            "id": r["id"], "name": r["name"], "min": r["min"],
            "tool": d["tools"][r["tool"]]["name"],
            "why": common.pairing_line(r, a.drink),
            "photo": photo.as_uri(),
            "keyIngs": v2.key_ings(r["ing"]),
            "point": point, "pointStep": k,
        })
    short = f"{zlib.crc32(','.join(r['id'] for r in sel).encode()):08x}"[:6]
    name = f"list-{a.drink}-{a.theme}-{short}"
    hook = v2.hook_data(a.hook, a.sub, a.hooks_file, ([pathlib.Path(a.out).name] if a.out else []) + [name])
    if hook:
        common.check_banned(hook["hook"] + "\n" + hook["sub"])
    c = {"drinkId": a.drink, "drink": drinks[a.drink], "head1": head1, "headMid": mid, "head2": head2,
         "items": items, "count": d["count"], "hook": hook}

    lines = [head1 + mid + head2]
    lines += [f"{k + 1}. {x['name']}（{x['min']}分・{x['tool']}）" for k, x in enumerate(items)]
    lines += ["", "保存しておくと、飲みたい夜にすぐ作れます。", "レシピはプロフィールのリンクから。", "",   # 注記2行（AI・20歳）は2026-10-07から付けない
              " ".join(common.list_hashtags(name, a.theme, a.drink, drinks[a.drink]))]
    common.check_banned("\n".join(x["why"] for x in items))
    cap = common.check_banned("\n".join(lines) + "\n")

    work = common.WORK / f"v2_{name}"
    html = common.fill_template(ROOT / "video" / "list_reel_v2.html", work / "reel.html", c)
    if a.preview:
        pre = work / "preview"
        common.run(["node", str(ROOT / "video" / "render.mjs"), str(html), str(pre)] + [str(t) for t in a.preview])
        print(pre)
        return pre

    out = pathlib.Path(a.out).expanduser().resolve() if a.out else ROOT / "reels" / "queue" / name
    build_video(html, work, out, lead_cover=not hook, bgm="bgm_v2.py")
    if hook:
        (out / "caption_v2.txt").write_text(cap, encoding="utf-8")       # フックを入れる前のキャプション
        cap = v2.hook_caption(cap, hook["hook"])
    (out / "caption.txt").write_text(cap, encoding="utf-8")
    (out / "meta.json").write_text(json.dumps({"type": "list", "drink": a.drink, "theme": a.theme, "version": 2,
                                               **({"hook": hook} if hook else {}),
                                               "ids": [r["id"] for r in sel]}, ensure_ascii=False, indent=1) + "\n",
                                   encoding="utf-8")
    if not a.keep_frames:
        shutil.rmtree(work / "frames", ignore_errors=True)
    print(out)
    return out


if __name__ == "__main__":
    main()
