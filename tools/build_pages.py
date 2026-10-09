#!/usr/bin/env python3
"""検索エンジンが読めるページを書き出す。recipes.js を変えたら実行する。

  python3 tools/build_pages.py

出力:
  recipes/<id>/index.html … レシピ1品ずつのページ（構造化データ付き）
  drinks/<id>/index.html  … 「ビールに合うつまみ」などお酒ごとの一覧
  sitemap.xml, robots.txt

アプリ（index.html）はJavaScriptで画面を描くので、検索エンジンや共有時のプレビューには
中身が伝わりにくい。そのため、同じ内容を素のHTMLでも用意する。
公開URLを変えるときは BASE だけを直す。
"""
import html, json, pathlib, re, subprocess, datetime

BASE = 'https://osakenomitai.com/sakenotsumami/'
ROOT = pathlib.Path(__file__).resolve().parent.parent

# recipes.js をそのまま node で読んで JSON にする（データの定義を二重に持たないため）
data = json.loads(subprocess.run(
    ['node', '-e', "const vm=require('vm');const c={};vm.createContext(c);"
     "vm.runInContext(require('fs').readFileSync(process.argv[1],'utf8')+';this.o={DRINKS,TOOLS,RECIPES}',c);"
     "process.stdout.write(JSON.stringify(c.o))", str(ROOT / 'recipes.js')],
    check=True, capture_output=True, text=True).stdout)
DRINKS, TOOLS, RECIPES = data['DRINKS'], data['TOOLS'], data['RECIPES']
DNAME = {d['id']: d['name'] for d in DRINKS}
e = html.escape
LOGO = (ROOT / 'brand' / 'sakenotsumami-logotype.svg').read_text()
LOGO = re.sub(r'<svg ', '<svg class="logo" ', LOGO, count=1)
TODAY = datetime.date.today().isoformat()
# 写真がまだ無いレシピ（足したばかりの品）は、写真の代わりに黄色の地を出し、共有画像はアプリの共有画像にする
has_photo = lambda r: (ROOT / 'images' / f"{r['id']}.jpg").exists()

CSS = '''
:root{--white:#fff;--ink:#121212;--main:#F2C600;--main-soft:rgba(242,198,0,.16);--soft:#f7f7f5;--line:rgba(18,18,18,.12);--muted:rgba(18,18,18,.55);}
*{box-sizing:border-box;}
body{margin:0;background:var(--white);color:var(--ink);font-family:'Zen Kaku Gothic New',sans-serif;line-height:1.8;}
a{color:inherit;}
.wrap{max-width:720px;margin:0 auto;padding:calc(16px + env(safe-area-inset-top,0px)) 16px 48px;}
.top{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:18px;}
.logo{display:block;width:132px;height:auto;}
.logo path{fill:var(--ink);}
.open{font-size:12.5px;font-weight:700;border:1.5px solid var(--ink);border-radius:999px;padding:6px 14px;text-decoration:none;white-space:nowrap;}
.crumb{font-size:12px;color:var(--muted);margin:0 0 10px;}
.crumb a{text-decoration:none;}
h1{font-size:24px;font-weight:900;line-height:1.4;margin:0;}
.catch{margin:8px 0 0;font-size:14px;color:var(--muted);}
.hero{display:block;width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:16px;margin:0 0 18px;background:var(--main-soft);}
.meta{display:grid;grid-template-columns:repeat(3,1fr);margin:18px 0 0;border:1px solid var(--line);border-radius:14px;overflow:hidden;}
.meta div{padding:10px 8px;text-align:center;}
.meta div+div{border-left:1px solid var(--line);}
.meta dt{font-size:11px;color:var(--muted);font-weight:700;}
.meta dd{margin:4px 0 0;font-size:14.5px;font-weight:900;}
h2{margin:28px 0 10px;font-size:16px;font-weight:900;display:flex;align-items:center;gap:8px;}
h2:before{content:'';width:4px;height:16px;border-radius:2px;background:var(--main);}
.pair{display:flex;flex-wrap:wrap;gap:6px;}
.pair a{font-size:13px;font-weight:700;border:1.5px solid var(--ink);border-radius:999px;padding:5px 12px;text-decoration:none;}
.why{margin:12px 0 0;background:var(--soft);border-radius:12px;padding:12px 14px;font-size:13.5px;line-height:1.7;}
.ing{list-style:none;margin:0;padding:0;}
.ing li{display:flex;justify-content:space-between;gap:12px;padding:10px 2px;border-bottom:1px dashed var(--line);font-size:14.5px;}
.ing li span:last-child{font-weight:700;white-space:nowrap;}
.steps{list-style:none;margin:0;padding:0;counter-reset:s;}
.steps li{counter-increment:s;position:relative;padding:0 0 16px 38px;font-size:14.5px;line-height:1.75;}
.steps li:before{content:counter(s);position:absolute;left:0;top:1px;width:26px;height:26px;border-radius:50%;background:var(--ink);color:var(--white);font-size:13px;font-weight:900;display:flex;align-items:center;justify-content:center;}
.cta{display:block;margin:28px 0 0;text-align:center;background:var(--main);border:1.5px solid var(--ink);border-radius:999px;padding:14px;font-weight:900;text-decoration:none;}
.list{list-style:none;margin:0;padding:0;display:grid;gap:10px;}
.card{display:flex;gap:12px;align-items:center;border:1px solid var(--line);border-radius:16px;padding:12px;text-decoration:none;}
.card img,.card i{width:72px;height:72px;border-radius:12px;object-fit:cover;flex:none;background:var(--main-soft);}
.card b{display:block;font-size:15px;line-height:1.4;}
.card span{display:block;font-size:12px;color:var(--muted);margin-top:2px;}
.lead{font-size:14px;color:var(--muted);margin:8px 0 18px;}
.drinks{display:flex;flex-wrap:wrap;gap:6px;margin:24px 0 0;}
.drinks a{font-size:13px;font-weight:700;border:1.5px solid var(--line);border-radius:999px;padding:5px 12px;text-decoration:none;}
.note{margin:32px 0 0;font-size:11.5px;color:var(--muted);text-align:center;line-height:1.7;}
.note a{margin:0 6px;}
'''


def page(*, path, title, desc, image, body, jsonld, up):
    """1ページ分のHTML。up はサイトの一番上への相対パス（recipes/x/ なら ../../）"""
    url = BASE + path
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<script>if(location.hostname==='shiryu-takahashi-0112.github.io') location.replace('https://osakenomitai.com'+location.pathname+location.search+location.hash);</script>
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<link rel="icon" type="image/svg+xml" href="{up}icons/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="{up}icons/favicon-32.png">
<link rel="apple-touch-icon" href="{up}icons/apple-touch-icon.png">
<meta property="og:type" content="article">
<meta property="og:site_name" content="サケノツマミ">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{image}">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Zen+Kaku+Gothic+New:wght@400;500;700;900&display=swap" rel="stylesheet">
<style>{CSS}</style>
<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>
</head>
<body>
<div class="wrap">
<div class="top"><a href="{up}" aria-label="サケノツマミ トップ">{LOGO}</a><a class="open" href="{up}">アプリで探す</a></div>
{body}
<p class="note">飲みすぎに注意しましょう。飲酒運転は法律で禁止されています。<br>
<a href="{up}terms.html">利用規約</a><a href="{up}privacy.html">プライバシーポリシー</a></p>
</div>
</body>
</html>
'''


def recipe_page(r):
    drinks = '・'.join(DNAME[d] for d in r['drinks'])
    title = f"{r['name']}｜{drinks}に合うつまみ｜サケノツマミ"
    desc = f"{r['catch']}{r['min']}分・{TOOLS[r['tool']]['name']}で作れる、{drinks}に合うつまみのレシピ（2人分）。{r['why']}"
    img = f"{BASE}images/{r['id']}.jpg" if has_photo(r) else f'{BASE}og-image.jpg'
    body = f'''<p class="crumb"><a href="../../">サケノツマミ</a> ／ <a href="../../drinks/{r['drinks'][0]}/">{e(DNAME[r['drinks'][0]])}に合うつまみ</a></p>
{f'<img class="hero" src="../../images/{r["id"]}.jpg" alt="{e(r["name"])}" width="800" height="600">' if has_photo(r) else ''}
<h1>{e(r['name'])}</h1>
<p class="catch">{e(r['catch'])}</p>
<dl class="meta"><div><dt>時間</dt><dd>{r['min']}分</dd></div><div><dt>道具</dt><dd>{e(TOOLS[r['tool']]['name'])}</dd></div><div><dt>分量</dt><dd>2人分</dd></div></dl>
<h2>合うお酒</h2>
<div class="pair">{''.join(f'<a href="../../drinks/{d}/">{e(DNAME[d])}</a>' for d in r['drinks'])}</div>
<p class="why">{e(r['why'])}</p>
<h2>材料（2人分）</h2>
<ul class="ing">{''.join(f'<li><span>{e(n)}</span><span>{e(a)}</span></li>' for n, a in r['ing'])}</ul>
<h2>作り方</h2>
<ol class="steps">{''.join(f'<li>{e(s)}</li>' for s in r['steps'])}</ol>
<a class="cta" href="../../#all/{r['id']}">アプリで開いて保存する</a>
<div class="drinks">{''.join(f'<a href="../../drinks/{d["id"]}/">{e(d["name"])}に合うつまみ</a>' for d in DRINKS)}</div>'''
    jsonld = {
        '@context': 'https://schema.org', '@type': 'Recipe',
        'name': r['name'], 'description': r['catch'], 'image': [img],
        'author': {'@type': 'Organization', 'name': 'サケノツマミ', 'url': BASE},
        'totalTime': f"PT{r['min']}M", 'recipeYield': '2人分',
        'recipeCategory': 'おつまみ', 'keywords': f"おつまみ,家飲み,晩酌,{','.join(DNAME[d] for d in r['drinks'])}",
        'recipeIngredient': [f'{n} {a}' for n, a in r['ing']],
        'recipeInstructions': [{'@type': 'HowToStep', 'text': s} for s in r['steps']],
    }
    return page(path=f"recipes/{r['id']}/", title=title, desc=desc, image=img, body=body, jsonld=jsonld, up='../../')


def drink_page(d):
    items = sorted([r for r in RECIPES if d['id'] in r['drinks']], key=lambda r: r['min'])
    title = f"{d['name']}に合うつまみレシピ{len(items)}品｜サケノツマミ"
    desc = f"{d['name']}に合うおつまみのレシピを{len(items)}品。ほとんどが15分以内、火を使わない・レンジだけのつまみも。合う理由つきで紹介します。"
    body = f'''<p class="crumb"><a href="../../">サケノツマミ</a> ／ {e(d['name'])}に合うつまみ</p>
<h1>{e(d['name'])}に合うつまみ {len(items)}品</h1>
<p class="lead">作る時間の短い順に並べています。</p>
<ul class="list">{''.join(f'<li><a class="card" href="../../recipes/{r["id"]}/">{f'<img src="../../images/{r["id"]}.jpg" alt="" loading="lazy" width="72" height="72">' if has_photo(r) else '<i></i>'}<div><b>{e(r["name"])}</b><span>{r["min"]}分・{e(TOOLS[r["tool"]]["name"])}｜{e(r["catch"])}</span></div></a></li>' for r in items)}</ul>
<a class="cta" href="../../#{d['id']}">アプリで{e(d['name'])}のつまみを探す</a>
<div class="drinks">{''.join(f'<a href="../{o["id"]}/">{e(o["name"])}に合うつまみ</a>' for o in DRINKS if o['id'] != d['id'])}</div>'''
    jsonld = {
        '@context': 'https://schema.org', '@type': 'ItemList', 'name': title,
        'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': f"{BASE}recipes/{r['id']}/"} for i, r in enumerate(items)],
    }
    return page(path=f"drinks/{d['id']}/", title=title, desc=desc, image=f'{BASE}og-image.jpg', body=body, jsonld=jsonld, up='../../')


def write(rel, text):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')


for r in RECIPES:
    write(f"recipes/{r['id']}/index.html", recipe_page(r))
for d in DRINKS:
    write(f"drinks/{d['id']}/index.html", drink_page(d))

urls = [BASE] + [f"{BASE}drinks/{d['id']}/" for d in DRINKS] + [f"{BASE}recipes/{r['id']}/" for r in RECIPES]
write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
      + ''.join(f'  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod></url>\n' for u in urls) + '</urlset>\n')
write('robots.txt', f'User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n')
print(f'recipes: {len(RECIPES)}, drinks: {len(DRINKS)}, sitemap: {len(urls)} URLs')
