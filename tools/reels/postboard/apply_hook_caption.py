#!/usr/bin/env python3
"""キャプションの1行目を冒頭のフックにする（2026-10-09・Shiryuの決定。動画のフックとキャプションの1行目をそろえる）。

  python3 postboard/apply_hook_caption.py saba-lemon --hooks-file reels/hooks_2026-10-10_10-29.json
  python3 postboard/apply_hook_caption.py reels/queue/saba-lemon --hook "5分で、ほぼ完成"
  python3 postboard/apply_hook_caption.py saba-lemon --hooks-file ... --dry-run      … 書き換えずに結果だけ見る
  python3 postboard/apply_hook_caption.py saba-lemon --hooks-file ... --replace-first … 元の1行目をフックに置き換える

<folder> は reels/queue のフォルダ名か、フォルダのパス。フックの一覧は {post_id,date,folder,type,hook,sub} の並び（folder で引く）。
- 初回に今の caption.txt を caption_v2.txt に残し、以後は caption_v2.txt を元に作り直す（何度流しても二重にならない）。
- 既定では、フックを1行目に足し、元の行（見出し・料理名・ハッシュタグなど）はすべてそのまま残す。
- 呼んだときだけ caption.txt を書き換える。Postboard には触らない（予約の差し替えは別の手順）。
"""
import argparse
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "lib"))
import common  # noqa: E402
import v2  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder")
    ap.add_argument("--hooks-file")
    ap.add_argument("--hook", help="フックを直接指定（--hooks-file より優先）")
    ap.add_argument("--replace-first", action="store_true", help="元の1行目を置き換える（既定は1行目に足す）")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    if not (a.hook or a.hooks_file):
        ap.error("--hooks-file か --hook を指定してください")

    p = pathlib.Path(a.folder).expanduser()
    folder = p if p.is_dir() else ROOT / "reels" / "queue" / a.folder
    cap, base = folder / "caption.txt", folder / "caption_v2.txt"
    if not cap.exists():
        sys.exit(f"caption.txt がありません: {cap}")
    h = v2.hook_data(a.hook, None, a.hooks_file, [folder.name])
    common.check_banned(h["hook"])
    src = (base if base.exists() else cap).read_text(encoding="utf-8")
    new = common.check_banned(v2.hook_caption(src, h["hook"], a.replace_first))
    if a.dry_run:
        print(new, end="")
        return
    if not base.exists():
        shutil.copy2(cap, base)
    cap.write_text(new, encoding="utf-8")
    print(f"{folder.name}: 1行目を「{h['hook']}」にした（元は caption_v2.txt）")


if __name__ == "__main__":
    main()
