#!/usr/bin/env python3
"""写真がまだ無いレシピの料理写真を Gemini で生成し、images/raw/<id>.png に置く（2026-10-10）。

  GEMINI_API_KEY=... python3 tools/gen_photos.py            … 写真の無い品をすべて
  GEMINI_API_KEY=... python3 tools/gen_photos.py id1 id2    … 指定した品だけ（作り直しにも使う）

指示文は images/PROMPTS.md の「料理ごとの指示文」と「共通文」をつなげたもの（手で作っていたときと同じ）。
生成のあとは python3 tools/photos.py で images/<id>.jpg に変換し、python3 tools/build_pages.py を実行する。
モデルは GEMINI_IMAGE_MODEL で変えられる（既定 gemini-2.5-flash-image）。
"""
import base64, json, os, pathlib, re, sys, time, urllib.request, urllib.error

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMAGES = ROOT / 'images'
MODEL = os.environ.get('GEMINI_IMAGE_MODEL', 'gemini-2.5-flash-image')
KEY = os.environ.get('GEMINI_API_KEY')
if not KEY:
    sys.exit('GEMINI_API_KEY がありません')

md = (IMAGES / 'PROMPTS.md').read_text()
COMMON = re.search(r'```plain text\n(.*?)\n```', md, re.S).group(1).strip()
PROMPTS = {m.group(1): m.group(2) for m in re.finditer(r'^\| ([a-z0-9-]+) \| [^|]+ \| `([^`]+)` \|$', md, re.M)}

ids = sys.argv[1:] or sorted(i for i in PROMPTS if not (IMAGES / f'{i}.jpg').exists())
(IMAGES / 'raw').mkdir(exist_ok=True)
url = f'https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent'

failed = []
for n, rid in enumerate(ids, 1):
    if rid not in PROMPTS:
        print(f'[{n}/{len(ids)}] {rid}: PROMPTS.md に指示文がありません'); failed.append(rid); continue
    body = json.dumps({
        'contents': [{'parts': [{'text': PROMPTS[rid] + COMMON}]}],
        'generationConfig': {'responseModalities': ['IMAGE'], 'imageConfig': {'aspectRatio': '1:1'}},
    }).encode()
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, body, {'Content-Type': 'application/json', 'x-goog-api-key': KEY})
            res = json.load(urllib.request.urlopen(req, timeout=180))
            part = next(p for c in res.get('candidates', []) for p in c['content']['parts'] if 'inlineData' in p)
            (IMAGES / 'raw' / f'{rid}.png').write_bytes(base64.b64decode(part['inlineData']['data']))
            print(f'[{n}/{len(ids)}] {rid}: ok')
            break
        except (urllib.error.HTTPError, urllib.error.URLError, StopIteration, KeyError, TimeoutError) as e:
            detail = e.read().decode()[:200] if isinstance(e, urllib.error.HTTPError) else repr(e)
            print(f'[{n}/{len(ids)}] {rid}: 失敗（{attempt + 1}回目） {detail}')
            time.sleep(10 * (attempt + 1))
    else:
        failed.append(rid)

print(f'できた: {len(ids) - len(failed)} / 失敗: {len(failed)} {" ".join(failed)}')
