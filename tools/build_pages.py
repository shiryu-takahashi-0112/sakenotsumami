#!/usr/bin/env python3
"""検索エンジンが読めるページを書き出す。recipes.js を変えたら実行する。

  python3 tools/build_pages.py

出力:
  recipes/<id>/index.html          … レシピ1品ずつのページ（構造化データ付き）
  drinks/<id>/index.html           … 「ビールに合うつまみ」などお酒ごとの一覧
  drinks/<id>/<条件>/index.html    … 「ハイボールに合う、火を使わないつまみ」などお酒×作り方の一覧（4品以上あるものだけ）
  ingredients/<slug>/index.html    … 「キャベツのつまみ」など食材ごとの一覧（4品以上あるものだけ）
  week/index.html                  … 今週のリールで紹介するつまみ（data/reels_week.json から。Instagramのプロフィールのリンク先）
  sitemap.xml, robots.txt

お酒×作り方と食材のページは2026-10-10に追加した（検索から来る人を増やすため。Shiryu承認）。
python 3.9 でも動くように書く（Macの python3 が 3.9 のため）。

アプリ（index.html）はJavaScriptで画面を描くので、検索エンジンや共有時のプレビューには
中身が伝わりにくい。そのため、同じ内容を素のHTMLでも用意する。
公開URLを変えるときは BASE だけを直す。
"""
import html, json, pathlib, re, shutil, subprocess, datetime

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


def thumb(r, up='../../'):
    """一覧のカードの写真。写真がまだ無い品は黄色の地にする"""
    if has_photo(r):
        return f'<img src="{up}images/{r["id"]}.jpg" alt="" loading="lazy" width="72" height="72">'
    return '<i></i>'


def card(r, up='../../', drinks=False):
    """一覧の1品。drinks=True なら、説明の代わりに合うお酒を出す"""
    sub = '・'.join(DNAME[d] for d in r['drinks']) + 'に合う' if drinks else r['catch']
    return (f'<li><a class="card" href="{up}recipes/{r["id"]}/">{thumb(r, up)}<div><b>{e(r["name"])}</b>'
            f'<span>{r["min"]}分・{e(TOOLS[r["tool"]]["name"])}｜{e(sub)}</span></div></a></li>')


# お酒×作り方のページの条件。slug はURLに使う
CONDS = [
    {'slug': 'no-fire', 'name': '火を使わない', 'mod': '火を使わない', 'how': '火を使わずに作れる', 'test': lambda r: r['tool'] == 'none'},
    {'slug': '5min',    'name': '5分以内',     'mod': '5分以内の',     'how': '5分以内で作れる',     'test': lambda r: r['min'] <= 5},
    {'slug': 'range',   'name': 'レンジだけ',   'mod': 'レンジだけの',   'how': '電子レンジだけで作れる', 'test': lambda r: r['tool'] == 'range'},
    {'slug': 'pan',     'name': 'フライパンひとつ', 'mod': 'フライパンひとつの', 'how': 'フライパンひとつで作れる', 'test': lambda r: r['tool'] == 'pan'},
]
MIN_ITEMS = 4      # お酒×作り方で、これより少ない組み合わせはページを作らない（中身の薄いページを増やさない）
MIN_ING_ITEMS = 5  # 食材も同じ。5品以上にすると、よく使う食材の約20種になる

# 食材のページ。材料の名前（recipes.js の ing の1つ目）に当てはまる品を集める。調味料・薬味・飾りは入れない。
# MIN_ING_ITEMS 品以上ある食材だけページにする。食材を足すときは、ここに1行足す。
INGREDIENTS = [
    ('cheese',   'チーズ',         r'^(?!粉チーズ).*チーズ'),
    ('onion',    '玉ねぎ',         r'^(玉ねぎ|紫玉ねぎ)'),
    ('egg',      '卵',             r'^(卵|卵黄|うずらの卵)'),
    ('chicken',  '鶏肉',           r'^(鶏(?!ガラ)|手羽|砂肝)'),
    ('pork',     '豚肉',           r'^豚'),
    ('beef',     '牛肉',           r'^牛(?!乳)'),
    ('bacon',    'ベーコン',       r'^ベーコン'),
    ('ham',      'ハム・生ハム',   r'^(ハム|生ハム)'),
    ('tomato',   'トマト',         r'^(トマト|ミニトマト)'),
    ('mushroom', 'きのこ',         r'^(しめじ|エリンギ|えのき|マッシュルーム|しいたけ|舞茸)'),
    ('tofu',     '豆腐',           r'^豆腐'),
    ('aburaage', '油揚げ・厚揚げ', r'^(油揚げ|厚揚げ)'),
    ('piman',    'ピーマン',       r'^(ピーマン|パプリカ)'),
    ('cabbage',  'キャベツ',       r'^キャベツ'),
    ('cucumber', 'きゅうり',       r'^きゅうり'),
    ('potato',   'じゃがいも',     r'^じゃがいも'),
    ('carrot',   'にんじん',       r'^にんじん'),
    ('daikon',   '大根',           r'^大根'),
    ('avocado',  'アボカド',       r'^アボカド'),
    ('nira',     'にら',           r'^にら'),
    ('kimchi',   'キムチ',         r'キムチ'),
    ('shrimp',   'えび',           r'^(むきえび|えび|ボイルえび)'),
    ('salmon',   '鮭・サーモン',   r'^(サーモン|生鮭)'),
    ('nerimono', 'ちくわ・練り物', r'^(ちくわ|はんぺん|さつま揚げ|カニカマ)'),
    ('tuna',     'ツナ・サバ缶',   r'^(ツナ缶|サバ水煮缶|オイルサーディン缶)'),
]


def drink_cond_items(d, c):
    return sorted([r for r in RECIPES if d['id'] in r['drinks'] and c['test'](r)], key=lambda r: (r['min'], r['name']))


def ingredient_items(pat):
    return sorted([r for r in RECIPES if any(re.search(pat, n) for n, _ in r['ing'])], key=lambda r: (r['min'], r['name']))


# ページを作る組み合わせ（4品以上）。レシピのページからのリンクにも使う
DRINK_CONDS = [(d, c) for d in DRINKS for c in CONDS if len(drink_cond_items(d, c)) >= MIN_ITEMS]
INGS = [{'slug': s, 'name': n, 'items': ingredient_items(p)} for s, n, p in INGREDIENTS]
INGS = [g for g in INGS if len(g['items']) >= MIN_ING_ITEMS]

WEEK = ROOT / 'data' / 'reels_week.json'
WEEK_DATA = json.loads(WEEK.read_text()) if WEEK.exists() else None
# お知らせ（2026-10-10）。新しい順に並べて出す
NEWS = sorted(json.loads((ROOT / 'data' / 'news.json').read_text()), key=lambda n: n['date'], reverse=True)

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
.note{margin:32px 0 0;font-size:11.5px;color:var(--muted);text-align:center;line-height:1.7;}
.reel{margin:26px 0 0;}
.reel .day{display:flex;align-items:center;gap:8px;font-size:12.5px;font-weight:700;color:var(--muted);margin:0 0 4px;}
.reel .day em{font-style:normal;font-size:11px;font-weight:900;color:var(--ink);background:var(--main);border-radius:999px;padding:1px 8px;}
.reel h2{margin:0 0 10px;}
.reel.later{opacity:.55;}
.cta.top{margin:16px 0 0;}
.news{margin:22px 0 0;padding:0 0 20px;border-bottom:1px solid var(--line);}
.news-date{margin:0;font-size:12.5px;font-weight:700;color:var(--muted);}
.news h2{display:block;margin:4px 0 8px;line-height:1.5;}
.news h2:before{display:none;}
.news p{margin:0 0 6px;font-size:14.5px;line-height:1.8;}
.news-link{display:inline-block;margin-top:4px;font-size:13.5px;font-weight:700;}
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
<link rel="stylesheet" href="{up}footer.css">
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
{related_links(r)}
{footer('../../')}'''
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


def related_links(r):
    """レシピのページから、その品が載っているお酒×作り方・食材の一覧へのリンク"""
    conds = [(d, c) for d, c in DRINK_CONDS if d['id'] in r['drinks'] and c['test'](r)]
    ings = [g for g in INGS if r in g['items']]
    links = [f'<a href="../../drinks/{d["id"]}/{c["slug"]}/">{e(d["name"])}に合う、{e(c["mod"])}つまみ</a>' for d, c in conds]
    links += [f'<a href="../../ingredients/{g["slug"]}/">{e(g["name"])}のつまみ</a>' for g in ings]
    return chips('この品が載っている一覧', links)


def drink_page(d):
    items = sorted([r for r in RECIPES if d['id'] in r['drinks']], key=lambda r: r['min'])
    title = f"{d['name']}に合うつまみレシピ{len(items)}品｜サケノツマミ"
    desc = f"{d['name']}に合うおつまみのレシピを{len(items)}品。ほとんどが15分以内、火を使わない・レンジだけのつまみも。合う理由つきで紹介します。"
    body = f'''<p class="crumb"><a href="../../">サケノツマミ</a> ／ {e(d['name'])}に合うつまみ</p>
<h1>{e(d['name'])}に合うつまみ {len(items)}品</h1>
<p class="lead">作る時間の短い順に並べています。</p>
<ul class="list">{''.join(card(r) for r in items)}</ul>
<a class="cta" href="../../#{d['id']}">アプリで{e(d['name'])}のつまみを探す</a>
{cond_links(d, '')}
{footer('../../', f"drinks/{d['id']}/")}'''
    jsonld = {
        '@context': 'https://schema.org', '@type': 'ItemList', 'name': title,
        'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': f"{BASE}recipes/{r['id']}/"} for i, r in enumerate(items)],
    }
    return page(path=f"drinks/{d['id']}/", title=title, desc=desc, image=f'{BASE}og-image.jpg', body=body, jsonld=jsonld, up='../../')


def chips(title, links):
    """小見出し＋丸いリンクの並び（見た目は footer.css）"""
    return f'<p class="ft-h">{e(title)}</p><div class="ft-chips">{"".join(links)}</div>' if links else ''


def footer(up, here=''):
    """どのページも同じ形で終える：今週のリール・お酒・作り方・食材。here は今いるページのパス（自分へのリンクは出さない）"""
    out = []
    if WEEK_DATA and here != 'week/':
        out.append(week_card(up))
    out.append(chips('お酒からさがす', [f'<a href="{up}drinks/{d["id"]}/">{e(d["name"])}</a>' for d in DRINKS if here != f"drinks/{d['id']}/"]))
    out.append(chips('作り方からさがす', [f'<a href="{up}conditions/{c["slug"]}/">{e(c["name"])}</a>' for c in CONDS if here != f"conditions/{c['slug']}/"]))
    out.append(chips('食材からさがす', [f'<a href="{up}ingredients/{g["slug"]}/">{e(g["name"])}</a>' for g in INGS if here != f"ingredients/{g['slug']}/"]))
    if NEWS and here != 'news/':
        # いちばん新しいお知らせが7日以内なら「NEW」を付ける（日付の判定は開いた人の端末で行う）
        out.append(chips('サケノツマミから', [f'<a href="{up}news/" data-news="{NEWS[0]["date"]}">お知らせ</a>']))
        out.append(NEWS_JS)
    return '\n'.join(out)


NEWS_JS = ("<script>document.querySelectorAll('[data-news]').forEach(function(a){"
           "var d=Date.now()-new Date(a.getAttribute('data-news')+'T00:00:00+09:00').getTime();"
           "if(d<7*864e5&&!a.querySelector('.ft-new'))a.insertAdjacentHTML('beforeend','<span class=\\'ft-new\\'>NEW</span>');});</script>")


def cond_links(d, base, skip=None):
    links = [f'<a href="{base}{c["slug"]}/">{e(c["name"])}</a>' for dd, c in DRINK_CONDS if dd is d and c is not skip]
    return chips(f"{d['name']}に合うつまみを、作り方でしぼる", links)


def list_image(items):
    """一覧のページの共有画像。写真のある最初の品、無ければアプリの共有画像"""
    r = next((r for r in items if has_photo(r)), None)
    return f"{BASE}images/{r['id']}.jpg" if r else f'{BASE}og-image.jpg'


def item_list(title, items):
    return {
        '@context': 'https://schema.org', '@type': 'ItemList', 'name': title, 'numberOfItems': len(items),
        'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': r['name'], 'url': f"{BASE}recipes/{r['id']}/"}
                            for i, r in enumerate(items)],
    }


def examples(items, n=2):
    # 紹介文の例には、写真のある品を先に使う
    picked = sorted(items, key=lambda r: not has_photo(r))[:n]
    return ''.join(f'「{r["name"]}」' for r in picked)


def drink_cond_page(d, c):
    items = drink_cond_items(d, c)
    n = len(items)
    title = f"{d['name']}に合う、{c['mod']}つまみ{n}品｜サケノツマミ"
    quick = sum(r['min'] <= 10 for r in items)
    # 紹介文はデータから作る（品数・時間・例）。お酒の量や勢いには触れない
    intro = (f"{d['name']}に合うつまみのうち、{c['how']}ものを{n}品集めました。"
             f"いちばん短いものは{items[0]['min']}分で、{quick}品が10分以内。{examples(items)}など、すべて2人分です。")
    desc = f"{d['name']}に合う、{c['mod']}おつまみレシピ{n}品。{examples(items, 3)}など。作る時間の短い順に、合う理由つきで紹介します。"
    body = f'''<p class="crumb"><a href="../../../">サケノツマミ</a> ／ <a href="../">{e(d['name'])}に合うつまみ</a> ／ {e(c['name'])}</p>
<h1>{e(d['name'])}に合う、{e(c['mod'])}つまみ {n}品</h1>
<p class="lead">{e(intro)}</p>
<ul class="list">{''.join(card(r, '../../../', drinks=False) for r in items)}</ul>
<a class="cta" href="../../../#{d['id']}">アプリで{e(d['name'])}のつまみを探す</a>
{cond_links(d, '../', skip=c)}
{chips(f"ほかのお酒で、{c['mod']}つまみ", [f'<a href="../../{o["id"]}/{c["slug"]}/">{e(o["name"])}</a>' for o, cc in DRINK_CONDS if cc is c and o is not d])}
{footer('../../../')}'''
    return page(path=f"drinks/{d['id']}/{c['slug']}/", title=title, desc=desc, image=list_image(items), body=body,
                jsonld=item_list(title, items), up='../../../')


def ingredient_page(g):
    items = g['items']
    n = len(items)
    counts = sorted(((sum(d['id'] in r['drinks'] for r in items), i, d) for i, d in enumerate(DRINKS)), key=lambda x: (-x[0], x[1]))
    top = [d for c, _, d in counts if c][:2]
    pair = '・'.join(d['name'] for d in top)
    title = f"{g['name']}のつまみ{n}品｜{pair}に合う｜サケノツマミ"
    quick = sum(r['min'] <= 10 for r in items)
    nofire = sum(r['tool'] == 'none' for r in items)
    often = '、'.join(f"{d['name']}（{c}品）" for c, _, d in counts[:3] if c)
    rest = f'、{nofire}品は火を使わずに作れます' if nofire else 'で作れます'
    intro = f"{g['name']}を使ったつまみを{n}品集めました。合うお酒は{often}が多く、{quick}品が10分以内{rest}。"
    desc = f"{g['name']}を使ったおつまみレシピ{n}品。{examples(items, 3)}など、{pair}に合うつまみを作る時間の短い順に紹介します。"
    body = f'''<p class="crumb"><a href="../../">サケノツマミ</a> ／ 食材からさがす ／ {e(g['name'])}</p>
<h1>{e(g['name'])}のつまみ {n}品</h1>
<p class="lead">{e(intro)}</p>
<ul class="list">{''.join(card(r, drinks=True) for r in items)}</ul>
<a class="cta" href="../../">アプリでほかのつまみを探す</a>
{footer('../../', f"ingredients/{g['slug']}/")}'''
    return page(path=f"ingredients/{g['slug']}/", title=title, desc=desc, image=list_image(items), body=body,
                jsonld=item_list(title, items), up='../../')


def cond_page(c):
    """作り方ごとの一覧（お酒を問わない）。アプリのトップの「作り方からさがす」から来る"""
    items = sorted([r for r in RECIPES if c['test'](r)], key=lambda r: (r['min'], r['name']))
    n = len(items)
    counts = sorted(((sum(d['id'] in r['drinks'] for r in items), i, d) for i, d in enumerate(DRINKS)), key=lambda x: (-x[0], x[1]))
    often = '、'.join(f"{d['name']}（{k}品）" for k, _, d in counts[:3] if k)
    title = f"{c['mod']}つまみ{n}品｜お酒に合うおつまみレシピ｜サケノツマミ"
    intro = (f"{c['how']}つまみを{n}品集めました。合うお酒は{often}が多く、"
             f"いちばん短いものは{items[0]['min']}分。{examples(items)}など、すべて2人分です。")
    desc = f"{c['how']}おつまみレシピ{n}品。{examples(items, 3)}など。作る時間の短い順に、合うお酒つきで紹介します。"
    body = f'''<p class="crumb"><a href="../../">サケノツマミ</a> ／ 作り方からさがす ／ {e(c['name'])}</p>
<h1>{e(c['mod'])}つまみ {n}品</h1>
<p class="lead">{e(intro)}</p>
<ul class="list">{''.join(card(r, drinks=True) for r in items)}</ul>
<a class="cta" href="../../">アプリでほかのつまみを探す</a>
{chips(f"お酒ごとに、{c['mod']}つまみ", [f'<a href="../../drinks/{d["id"]}/{c["slug"]}/">{e(d["name"])}</a>' for d, cc in DRINK_CONDS if cc is c])}
{footer('../../', f"conditions/{c['slug']}/")}'''
    return page(path=f"conditions/{c['slug']}/", title=title, desc=desc, image=list_image(items), body=body,
                jsonld=item_list(title, items), up='../../')


def news_page():
    """お知らせ。中身は data/news.json（新しい機能を出したら、同じPRで1件足す）"""
    title = 'お知らせ｜サケノツマミ'
    desc = 'サケノツマミの新しい機能や、レシピの追加のお知らせ。' + (f"最新：{NEWS[0]['title']}（{jp_date(NEWS[0]['date'], False)}）" if NEWS else '')
    items = []
    for n in NEWS:
        link = f'<a class="news-link" href="../{n["link"]["href"]}">{e(n["link"]["label"])}</a>' if n.get('link') else ''
        items.append(f'''<article class="news" id="{e(n['id'])}">
<p class="news-date"><time datetime="{n['date']}">{jp_date(n['date'])}</time></p>
<h2>{e(n['title'])}</h2>
{''.join(f'<p>{e(t)}</p>' for t in n['body'])}
{link}
</article>''')
    body = f'''<p class="crumb"><a href="../">サケノツマミ</a> ／ お知らせ</p>
<h1>お知らせ</h1>
{''.join(items)}
<a class="cta" href="../">アプリでつまみを探す</a>
{footer('../', 'news/')}'''
    jsonld = {'@context': 'https://schema.org', '@type': 'ItemList', 'name': title,
              'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n['title'], 'url': f"{BASE}news/#{n['id']}"} for i, n in enumerate(NEWS)]}
    return page(path='news/', title=title, desc=desc, image=f'{BASE}og-image.jpg', body=body, jsonld=jsonld, up='../')


def week_card(up):
    n = sum(len(it['ids']) for it in WEEK_DATA['items'])
    return (f'''<p class="ft-h">Instagramのリールから</p><a class="ft-week" href="{up}week/"><div><b>今週のリールのつまみ</b>'''
            f'''<span>{jp_date(WEEK_DATA['start'], False)}〜{jp_date(WEEK_DATA['end'], False)}に紹介する{n}品</span></div></a>''')


def write_app_home():
    """アプリのホーム（index.html の home:start〜home:end の間）を書き出す（2026-10-10）。
    検索用ページの下の一覧（footer）と同じ並び・同じ見た目で、リンク先だけをアプリの中の「さがす」にする。
    作り方・食材で絞るための品の一覧（HOME.presets）と、今日の一品に使う写真のある品（HOME.photos）もここで渡す"""
    presets = {f"c-{c['slug']}": {'label': f"{c['mod']}つまみ", 'ids': [r['id'] for r in RECIPES if c['test'](r)]} for c in CONDS}
    presets.update({f"i-{g['slug']}": {'label': f"{g['name']}のつまみ", 'ids': [r['id'] for r in g['items']]} for g in INGS})
    home = {'presets': presets, 'photos': [r['id'] for r in RECIPES if has_photo(r)]}
    out = []
    if WEEK_DATA:
        out.append(week_card(''))
    out.append(chips('お酒からさがす', [f'<a href="#{d["id"]}">{e(d["name"])}</a>' for d in DRINKS]))
    out.append(chips('作り方からさがす', [f'<a href="#c-{c["slug"]}">{e(c["name"])}</a>' for c in CONDS]))
    out.append(chips('食材からさがす', [f'<a href="#i-{g["slug"]}">{e(g["name"])}</a>' for g in INGS]))
    if NEWS:
        out.append('<p class="ft-h">お知らせ</p><ul class="ft-news">' + ''.join(
            f'<li><a href="news/#{e(n["id"])}"><time datetime="{n["date"]}">{jp_date(n["date"], False)}</time><b>{e(n["title"])}</b></a></li>'
            for n in NEWS[:3]) + f'</ul><a class="ft-more" href="news/" data-news="{NEWS[0]["date"]}">お知らせをすべて見る</a>')
        out.append(NEWS_JS)
    out.append(f'<script>const HOME = {json.dumps(home, ensure_ascii=False, separators=(",", ":"))};</script>')
    p = ROOT / 'index.html'
    src = p.read_text(encoding='utf-8')
    a, b = '<!-- home:start（tools/build_pages.py が書き出す。手で直さない） -->', '<!-- home:end -->'
    i, j = src.index(a) + len(a), src.index(b)
    p.write_text(src[:i] + '\n' + '\n'.join(out) + '\n' + src[j:], encoding='utf-8')


WEEKDAY = '月火水木金土日'


def jp_date(iso, wd=True):
    dt = datetime.date.fromisoformat(iso)
    return f'{dt.month}月{dt.day}日' + (f'（{WEEKDAY[dt.weekday()]}）' if wd else '')


def week_page(w):
    """今週のリールで紹介するつまみ。Instagramのプロフィールのリンクから来た人が、見たリールの品をすぐ開けるようにする"""
    byid = {r['id']: r for r in RECIPES}
    title = '今週のリールのつまみ｜サケノツマミ'
    period = f"{jp_date(w['start'])}〜{jp_date(w['end'])}"
    names = [byid[i]['name'] for it in w['items'] for i in it['ids'] if i in byid]
    desc = f"Instagramのリールで紹介するつまみのレシピ（{period}）。{'・'.join(names[:3])}など{len(names)}品。材料と作り方はここから。"
    sections = []
    for it in w['items']:
        rs = [byid[i] for i in it['ids'] if i in byid]
        sections.append(f'''<section class="reel" data-date="{it['date']}">
<p class="day">{jp_date(it['date'])}<em hidden></em></p>
<h2>{e(it['title'])}</h2>
<ul class="list">{''.join(card(r, '../', drinks=True) for r in rs)}</ul>
</section>''')
    body = f'''<p class="crumb"><a href="../">サケノツマミ</a> ／ 今週のリールのつまみ</p>
<h1>今週のリールのつまみ</h1>
<p class="lead">{period}にInstagramのリールで紹介するつまみです。品名を押すと、材料と作り方が見られます。</p>
<a class="cta top" href="../">アプリでほかのつまみを探す</a>
{''.join(sections)}
<a class="cta" href="../">アプリでほかのつまみを探す</a>
{footer('../', 'week/')}
<script>
// 今日のリールに印を付け、まだ出ていない日の品は薄くする（日本時間で判定）
(function(){{
  var t = new Date(Date.now() + 9 * 3600e3).toISOString().slice(0, 10);
  document.querySelectorAll('.reel').forEach(function(s){{
    var d = s.getAttribute('data-date'), em = s.querySelector('em');
    if(d === t){{ em.textContent = '今日'; em.hidden = false; }}
    else if(d > t){{ em.textContent = 'これから'; em.hidden = false; s.classList.add('later'); }}
  }});
}})();
</script>'''
    allr = [byid[i] for it in w['items'] for i in it['ids'] if i in byid]
    jsonld = item_list(title, allr)
    return page(path='week/', title=title, desc=desc, image=list_image(allr), body=body, jsonld=jsonld, up='../')


def write(rel, text):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')


# 4品を下回った組み合わせ・外した食材のページが残らないよう、書き出す前に消す
for d in DRINKS:
    for sub in [p for p in (ROOT / 'drinks' / d['id']).iterdir() if p.is_dir()]:
        shutil.rmtree(sub)
shutil.rmtree(ROOT / 'ingredients', ignore_errors=True)
shutil.rmtree(ROOT / 'conditions', ignore_errors=True)

for r in RECIPES:
    write(f"recipes/{r['id']}/index.html", recipe_page(r))
for d in DRINKS:
    write(f"drinks/{d['id']}/index.html", drink_page(d))
for d, c in DRINK_CONDS:
    write(f"drinks/{d['id']}/{c['slug']}/index.html", drink_cond_page(d, c))
for g in INGS:
    write(f"ingredients/{g['slug']}/index.html", ingredient_page(g))
for c in CONDS:
    write(f"conditions/{c['slug']}/index.html", cond_page(c))
week = WEEK_DATA
if week:
    write('week/index.html', week_page(week))
write('news/index.html', news_page())
write_app_home()

urls = ([BASE] + [f"{BASE}drinks/{d['id']}/" for d in DRINKS]
        + [f"{BASE}drinks/{d['id']}/{c['slug']}/" for d, c in DRINK_CONDS]
        + [f"{BASE}conditions/{c['slug']}/" for c in CONDS]
        + [f"{BASE}ingredients/{g['slug']}/" for g in INGS]
        + [f'{BASE}news/']
        + ([f'{BASE}week/'] if week else [])
        + [f"{BASE}recipes/{r['id']}/" for r in RECIPES])
write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
      + ''.join(f'  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod></url>\n' for u in urls) + '</urlset>\n')
write('robots.txt', f'User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n')
print(f'recipes: {len(RECIPES)}, drinks: {len(DRINKS)}, drink×条件: {len(DRINK_CONDS)}, 食材: {len(INGS)}, week: {bool(week)}, sitemap: {len(urls)} URLs')
