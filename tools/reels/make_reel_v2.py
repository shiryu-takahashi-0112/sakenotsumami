#!/usr/bin/env python3
"""1品型の動画 v2（テンポを上げて約24秒にした版）。旧版 make_reel.py は旧版として残す。

  python3 make_reel_v2.py buta-kimchi                       … reels/queue/<id>/ に書き出す
  python3 make_reel_v2.py buta-kimchi --out review/v2-sample/one
  python3 make_reel_v2.py buta-kimchi --preview 0.5 3 6 14 17 20 22.5   … 指定秒のコマだけ（確認用）
  python3 make_reel_v2.py saba-lemon --drink sour --hook "5分で、ほぼ完成" --sub "火を使わず、和えるだけ"
  python3 make_reel_v2.py saba-lemon --drink sour --hooks-file reels/hooks_2026-10-10_10-29.json   … フォルダ名で引く

冒頭のフック（2026-10-09〜）：--hook（14文字以内・1行）と --sub（16文字以内）を渡すと、最初のコマから
写真の上にフックを大きく出し、0.3秒で写真が寄る。約1.8秒で材料へ進む。表紙の静止画は先頭に足さず、最初のコマを cover.jpg にする。
キャプションの1行目もフックにする（元のキャプションは caption_v2.txt に残す）。--hook を渡さなければ従来どおり。

流れは video/reel_v2.html の先頭に書いてある。
画面に出す文はすべて recipes.js の値（name・min・tool・drinks・why/catch・ing・steps）から作る。
  「ここがポイント」はレシピに tips の欄が無いので、作り方の文の一部をそのまま出す（lib/v2.py の point_line）。
出力：reel.mp4（先頭に表紙0.5秒）・cover.jpg・caption.txt（キャプションは旧版と同じ作り方）
2026-10-07にShiryuが承認し、現行の作り方になった。出力先は reels/queue/<id>（--out で変更可）。
"""
import argparse
import pathlib
import shutil
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "lib"))
import common  # noqa: E402
import v2  # noqa: E402
from build import build_video  # noqa: E402

ROOT = common.ROOT


def v2_data(c):
    r = c["recipe"]
    point, k = v2.point_line(r["steps"])
    keys = v2.key_ings(r["ing"])
    names = [v2.clean_name(x[0]) for x in r["ing"]]
    shown = r["ing"] if len(r["ing"]) <= 6 else r["ing"][:5]
    return {
        "stepBeats": [v2.beats(s) for s in r["steps"]],
        "point": point,
        "pointStep": k,
        "whyBeats": v2.beats(c["why"]),
        "keyIngs": keys,
        "keyIngIdx": [names.index(x) for x in keys if names.index(x) < len(shown)],
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("recipe_id")
    ap.add_argument("--drink")
    ap.add_argument("--out", help="出力フォルダ（省略時 reels/queue/<id>）")
    ap.add_argument("--preview", nargs="+", type=float, metavar="秒")
    ap.add_argument("--keep-frames", action="store_true")
    ap.add_argument("--hook", help="冒頭のフック（14文字以内・1行）")
    ap.add_argument("--sub", help="フックの下の小さい1行（16文字以内・省略可）")
    ap.add_argument("--hooks-file", help="フックの一覧（JSON）。フォルダ名（--out の名前、無ければ <id>）で引く")
    a = ap.parse_args(argv)

    c = common.load(a.recipe_id, a.drink)
    c["v2"] = v2_data(c)
    common.check_banned(c["why"])     # 画面に出す合う理由も調べる（作り方の文は旧版と同じく対象外）
    rid = c["recipe"]["id"]
    folders = ([pathlib.Path(a.out).name] if a.out else []) + [rid]
    c["hook"] = v2.hook_data(a.hook, a.sub, a.hooks_file, folders)
    if c["hook"]:
        common.check_banned(c["hook"]["hook"] + "\n" + c["hook"]["sub"])
    work = common.WORK / f"v2_{rid}"
    html = common.fill_template(ROOT / "video" / "reel_v2.html", work / "reel.html", c)

    if a.preview:
        pre = work / "preview"
        common.run(["node", str(ROOT / "video" / "render.mjs"), str(html), str(pre)] + [str(t) for t in a.preview])
        print(pre)
        return pre

    cap = v2.strip_notices(common.caption(c, "reel"))   # 注記2行は付けない（2026-10-07）
    out = pathlib.Path(a.out).expanduser().resolve() if a.out else ROOT / "reels" / "queue" / rid
    build_video(html, work, out, lead_cover=not c["hook"], bgm="bgm_v2.py")
    if c["hook"]:
        (out / "caption_v2.txt").write_text(cap, encoding="utf-8")       # フックを入れる前のキャプション
        cap = v2.hook_caption(cap, c["hook"]["hook"])
    (out / "caption.txt").write_text(cap, encoding="utf-8")
    if not a.keep_frames:
        shutil.rmtree(work / "frames", ignore_errors=True)
    print(out)
    return out


if __name__ == "__main__":
    main()
