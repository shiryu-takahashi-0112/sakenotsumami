#!/usr/bin/env python3
"""「今週のリールのつまみ」（week/）を作り直す。Instagramのプロフィールのリンク先（2026-10-10に追加）。

  python3 tools/build_week.py                 … data/reels_week.json から week/index.html を書き出す
  python3 tools/build_week.py --from-cowork 2026-10-17
      … その日から7日分のリールの予定を、投稿管理ツールに入れた記録から読んで
        data/reels_week.json を作り直し、続けてページを書き出す（Shiryu の Mac で動くルーティーン用）

data/reels_week.json の形:
  {"start": "2026-10-10", "end": "2026-10-16",
   "items": [{"date": "2026-10-10", "title": "レモンサワーに合う、10分以内のつまみ3選", "ids": ["kanikama-kyuri", ...]}, ...]}
  ids は recipes.js のレシピの id。1品型のリールは1つ、◯選型は紹介する順に並べる。

ページそのものは tools/build_pages.py が書き出す（見た目・サイトマップを検索用ページとそろえるため）。
このスクリプトは、JSONを作ってから build_pages.py を動かすだけ。
"""
import argparse, datetime, json, pathlib, runpy

ROOT = pathlib.Path(__file__).resolve().parent.parent
WEEK = ROOT / 'data' / 'reels_week.json'
COWORK = pathlib.Path.home() / 'sakenotsumami-cowork'


def from_cowork(start, cowork):
    """投稿管理ツールに入れたリールの記録（postboard/registered.json の reel:<フォルダ>）から、7日分を集める。
    フォルダの meta.json に ids があれば◯選型、無ければフォルダ名がそのままレシピの id（1品型）。
    見出しは caption.txt の2行目（1行目はフック、2行目が「レモンサワーに合う、10分以内のつまみ3選」の形）。"""
    end = start + datetime.timedelta(days=6)
    reg = json.loads((cowork / 'postboard' / 'registered.json').read_text())
    items = []
    for key, v in reg.items():
        if not key.startswith('reel:'):
            continue
        day = datetime.date.fromisoformat(v['scheduled'][:10])
        if not start <= day <= end:
            continue
        folder = key[5:]
        base = next((p for p in (cowork / 'reels' / 'queue' / folder, cowork / 'reels' / 'posted' / folder) if p.exists()), None)
        if base is None:
            raise SystemExit(f'リールのフォルダが見つかりません: {folder}')
        meta = json.loads((base / 'meta.json').read_text()) if (base / 'meta.json').exists() else {}
        ids = meta.get('ids') or [folder]
        lines = [l.strip() for l in (base / 'caption.txt').read_text().splitlines() if l.strip()]
        title = lines[1] if len(lines) > 1 else lines[0]
        items.append({'date': day.isoformat(), 'title': title, 'ids': ids})
    items.sort(key=lambda x: x['date'])
    return {'start': start.isoformat(), 'end': end.isoformat(), 'items': items}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--from-cowork', metavar='開始日', help='この日から7日分を投稿管理ツールの記録から作り直す（YYYY-MM-DD）')
    ap.add_argument('--cowork', default=str(COWORK), help='sakenotsumami-cowork の場所')
    a = ap.parse_args()
    if a.from_cowork:
        w = from_cowork(datetime.date.fromisoformat(a.from_cowork), pathlib.Path(a.cowork))
        if not w['items']:
            raise SystemExit('その週のリールの予定が見つかりません')
        WEEK.parent.mkdir(exist_ok=True)
        WEEK.write_text(json.dumps(w, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
        print(f"data/reels_week.json: {w['start']}〜{w['end']} {len(w['items'])}本")
    runpy.run_path(str(ROOT / 'tools' / 'build_pages.py'), run_name='__main__')


if __name__ == '__main__':
    main()
