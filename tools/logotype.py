"""最初にアプリに置いていたロゴ（Zen Kaku Gothic New Black、字間 0.06em、大きさの補正なし）を、そのままSVGの線に起こす。
  python3 plain.py 0.06   # 字間（1文字の幅に対する割合）
"""
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
TRACK = float(sys.argv[1]) if len(sys.argv) > 1 else 0.06
SUF = sys.argv[2] if len(sys.argv) > 2 else ''
NO = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
KENO = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0   # ケとノの間を、さらに詰める量   # ノの左右を詰める量（1文字の幅に対する割合）
f = TTFont('../ZenKakuGothicNew-Black.ttf'); gs = f.getGlyphSet(); cmap = f.getBestCmap()
TOP, BOTTOM = 830, -75   # 2つのロゴで同じ高さの枠にする（フォント単位）
WORDS = [('サケノツマミ','sakenotsumami'), ('オサケノミタイ','osakenomitai'), ('サケノ','icon-l1'), ('ツマミ','icon-l2')]
for word, name in WORDS:
    x = 0; items = []
    for i, ch in enumerate(word):
        g = gs[cmap[ord(ch)]]
        if ch == 'ノ' and i > 0: x -= NO*1000          # ノの左を詰める
        if ch == 'ノ' and i > 0 and word[i-1] == 'ケ': x -= KENO*1000   # ケとノの間はさらに詰める
        items.append((g, x)); x += g.width + TRACK*1000
        if ch == 'ノ': x -= NO*1000                      # ノの右を詰める
    # 左右は、最初と最後の文字の輪郭の端で切る
    b0 = BoundsPen(gs); items[0][0].draw(b0); b1 = BoundsPen(gs); items[-1][0].draw(b1)
    left = items[0][1] + b0.bounds[0]; right = items[-1][1] + b1.bounds[2]
    paths = []
    for g, ox in items:
        sp = SVGPathPen(gs); g.draw(TransformPen(sp, (1,0,0,-1, ox-left, TOP))); paths.append(sp.getCommands())
    w = round(right-left); h = TOP-BOTTOM
    open(f'{name}-plain{SUF}.svg','w').write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{word}">'+''.join(f'<path d="{p}"/>' for p in paths)+'</svg>')
    print(name, w, h)
