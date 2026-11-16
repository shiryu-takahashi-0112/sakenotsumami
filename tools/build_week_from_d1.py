#!/usr/bin/env python3
"""「今週のリールのつまみ」（week/）を、Shiryu の Mac を経由せずに作り直す（試作・2026-11-16）。

Mac の ~/sakenotsumami-cowork を読む tools/build_week.py --from-cowork が、日曜20時の
ローカルルーティーンの未実行で何週も空振りしている対策。投稿管理ツール（Postboard）の
D1データベースには、Instagramに予約したリールのキャプションが入っているので、そこから
「見出し」と「紹介する品」を取り出して data/reels_week.json を作り直す。

このスクリプトは D1 に自分で接続しない（APIトークンを埋め込まない）。
クラウドのルーティーンが d1_database_query ツールで次のSQLを実行し、
結果（"results" の配列、または配列そのもの）をJSONファイルに保存してから、
このスクリプトに --posts-json で渡す。

  SELECT p.id, p.caption, p.scheduled_at, p.canceled, p.draft, pt.account_id
  FROM posts p JOIN post_targets pt ON pt.post_id = p.id
  WHERE p.brand_id = 2 AND pt.account_id = 4   -- 4 = Instagram（サケノツマミ）
    AND p.canceled = 0 AND p.draft = 0
    AND p.scheduled_at >= '<開始日>' AND p.scheduled_at < '<開始日+7日>'
  ORDER BY p.scheduled_at ASC

  python3 tools/build_week_from_d1.py --posts-json <上のJSON> --start 2026-11-16

キャプションからの読み取り方（caption.txt の代わり）:
  - 見出し（title）は、空行を除いた2行目（1行目はフック）。tools/build_week.py と同じ決め方。
  - ◯選型（見出しが「3選」「5選」などで終わる）は、「1. 品名（…）」の行から品名を取る。
  - 1品型は、固定文「保存しておくと、買い物のときに見返せます。」の次の行を品名とする
    （2026-10-17の決定でこの1文が必ず入る。見つからなければ品名は取らない＝不明扱い）。
  - 品名は recipes.js の name と「完全一致」したときだけ id を使う。曖味な一致はしない。
  - 1日分の品名が1つでも一致しなければ、その日は data/reels_week.json に入れず、
    標準エラー出力に理由を出す（精度より正直さを優先。CLAUDE.md・灯の依頼どおり）。

tools/build_week.py --from-cowork は変更していない（Macの仕組みが復活したときのために残す）。
"""
import argparse, datetime, json, pathlib, re, runpy, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
WEEK = ROOT / 'data' / 'reels_week.json'
SAVE_LINE = '保存しておくと、買い物のときに見返せます。'
LIST_ITEM_RE = re.compile(r'^\d+\.\s*(.+)$')
LIST_TITLE_RE = re.compile(r'\d+選$')


def load_recipe_names():
    """recipes.js を node で読み、品名→id・id→写真の有無を返す（build_pages.py と同じ読み方）。"""
    data = json.loads(subprocess.run(
        ['node', '-e', "const vm=require('vm');const c={};vm.createContext(c);"
         "vm.runInContext(require('fs').readFileSync(process.argv[1],'utf8')+';this.o={RECIPES}',c);"
         "process.stdout.write(JSON.stringify(c.o))", str(ROOT / 'recipes.js')],
        check=True, capture_output=True, text=True).stdout)
    recipes = data['RECIPES']
    name_to_id = {}
    dup = set()
    for r in recipes:
        if r['name'] in name_to_id and name_to_id[r['name']] != r['id']:
            dup.add(r['name'])
        name_to_id[r['name']] = r['id']
    for n in dup:
        del name_to_id[n]  # 同じ名前が複数の品にある場合は、品名からは確定できないので使わない
    has_photo = {r['id'] for r in recipes if (ROOT / 'images' / f"{r['id']}.jpg").exists()}
    return name_to_id, has_photo, dup


def jst_date(scheduled_at):
    """D1の scheduled_at（UTCのISO文字列）を、日本時間の日付（YYYY-MM-DD）にする。"""
    s = scheduled_at.replace('Z', '+00:00')
    dt = datetime.datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    jst = dt.astimezone(datetime.timezone(datetime.timedelta(hours=9)))
    return jst.date().isoformat()


def dish_names_from_caption(caption):
    """キャプションの文字列から、見出し（title）と、紹介する品名の並びを取り出す。
    品名が1つも取れない／型が分からないときは (title_or_None, []) を返す（呼び出し側で不明扱いにする）。"""
    lines = [l.strip() for l in caption.splitlines() if l.strip()]
    if not lines:
        return None, []
    title = lines[1] if len(lines) > 1 else lines[0]
    if LIST_TITLE_RE.search(title):
        names = []
        for l in lines:
            m = LIST_ITEM_RE.match(l)
            if not m:
                continue
            name = re.split(r'[（(]', m.group(1), 1)[0].strip()
            if name:
                names.append(name)
        return title, names
    if SAVE_LINE in lines:
        idx = lines.index(SAVE_LINE)
        if idx + 1 < len(lines):
            return title, [lines[idx + 1]]
        return title, []
    return title, []


def posts_to_items(posts, name_to_id, has_photo, dup, warn):
    """D1の行（caption・scheduled_at を持つ辞書の並び）を、reels_week.json の items に変換する。"""
    items = []
    for p in posts:
        if p.get('canceled'):
            continue
        if p.get('draft'):
            continue
        date = jst_date(p['scheduled_at'])
        title, names = dish_names_from_caption(p.get('caption') or '')
        if title is None:
            warn(f'{date}（post id={p.get("id")}）: キャプションが空で読み取れない → 不明として外す')
            continue
        if not names:
            warn(f'{date}「{title}」（post id={p.get("id")}）: 品名の行が見つからない → 不明として外す')
            continue
        ids, missing, ambiguous = [], [], []
        for n in names:
            if n in dup:
                ambiguous.append(n)
            elif n in name_to_id:
                ids.append(name_to_id[n])
            else:
                missing.append(n)
        if missing or ambiguous:
            reason = []
            if missing:
                reason.append('recipes.js に無い: ' + '・'.join(missing))
            if ambiguous:
                reason.append('同じ品名が複数ある: ' + '・'.join(ambiguous))
            warn(f'{date}「{title}」（post id={p.get("id")}）: {"／".join(reason)} → 不明として外す')
            continue
        no_photo = [i for i in ids if i not in has_photo]
        if no_photo:
            warn(f'{date}「{title}」（post id={p.get("id")}）: 写真が無い品が混じっている（{"・".join(no_photo)}）。'
                 'week/ では写真のある品だけが表示される')
        items.append({'date': date, 'title': title, 'ids': ids})
    items.sort(key=lambda x: x['date'])
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--posts-json', required=True, metavar='パス',
                     help='D1のクエリ結果を保存したJSONファイル（{"results":[...]} でも配列そのものでもよい）')
    ap.add_argument('--start', required=True, metavar='開始日', help='週の開始日（YYYY-MM-DD、日本時間）')
    ap.add_argument('--out', default=str(WEEK), metavar='パス', help='書き出し先（既定: data/reels_week.json）')
    ap.add_argument('--skip-build-pages', action='store_true',
                     help='data/reels_week.json だけ作り、build_pages.py は実行しない（確認用）')
    a = ap.parse_args()

    start = datetime.date.fromisoformat(a.start)
    end = start + datetime.timedelta(days=6)

    raw = json.loads(pathlib.Path(a.posts_json).read_text(encoding='utf-8'))
    posts = raw['results'] if isinstance(raw, dict) and 'results' in raw else raw
    if isinstance(raw, list) and raw and isinstance(raw[0], dict) and 'results' in raw[0]:
        posts = raw[0]['results']  # d1_database_query が配列のレスポンスを返す形

    name_to_id, has_photo, dup = load_recipe_names()
    warnings = []
    items = posts_to_items(posts, name_to_id, has_photo, dup, warnings.append)
    items = [it for it in items if start.isoformat() <= it['date'] <= end.isoformat()]

    print(f'{a.start}〜{end.isoformat()}: {len(items)}日分を取り出せた（対象の投稿 {len(posts)}件）', file=sys.stderr)
    for w in warnings:
        print('  不明: ' + w, file=sys.stderr)
    missing_days = {(start + datetime.timedelta(days=i)).isoformat() for i in range(7)} - {it['date'] for it in items}
    if missing_days:
        print(f'  この週で data/reels_week.json に入らない日: {", ".join(sorted(missing_days))}', file=sys.stderr)

    if not items:
        raise SystemExit('この週は1日も取り出せなかった。data/reels_week.json は変更しない。')

    out_path = pathlib.Path(a.out)
    w = {'start': start.isoformat(), 'end': end.isoformat(), 'items': items}
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(w, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f'{out_path}: {len(items)}日分を書いた', file=sys.stderr)

    if not a.skip_build_pages:
        runpy.run_path(str(ROOT / 'tools' / 'build_pages.py'), run_name='__main__')


if __name__ == '__main__':
    main()
