"""使い方（2026-09-29にShiryuが字間「C」＝0.36を採用）:
  pip install fonttools pillow
  curl -LO https://github.com/google/fonts/raw/main/ofl/zenkakugothicnew/ZenKakuGothicNew-Black.ttf
  python3 tools/logotype.py Black 0.36   # カレントに <name>-black.svg を書き出す。brand/ に置き換えて使う
Zen Kaku Gothic New から、オサケノミタイ・サケノツマミのロゴタイプをSVGの線に起こす。
- 小さく見える文字（ノ・ツ・マ・ミ・イ）は少し大きくし、文字の中心の高さをそろえる。
- 字間は、隣り合う文字の向かい合う輪郭の平均距離（行ごと、上限あり）が同じになるように置く。
"""
import sys, json
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.svgPathPen import SVGPathPen
from PIL import Image, ImageDraw, ImageChops

WEIGHT = sys.argv[1] if len(sys.argv) > 1 else 'Black'
GAP = float(sys.argv[2]) if len(sys.argv) > 2 else 0.24   # 目標の平均字間（文字の高さに対する割合）
SUFFIX = sys.argv[3] if len(sys.argv) > 3 else ''
CAP = 1.4          # 1行あたりの距離の上限（GAPに対する倍率）。開いた形の文字で字間が開きすぎないように
MINR = 0.62
# 自動で置いたあとの、組み合わせごとの見た目の微調整（フォント単位。＋で広げる）
KERN = {'オサ':-70,'サケ':-20,'ケノ':45,'ノミ':0,'ミタ':-10,'タイ':-20,'ノツ':-35,'ツマ':-100,'マミ':-10}     # いちばん近い所でも、目標の字間のこの割合は空ける
SCALE = {'ノ':1.12,'ツ':1.07,'マ':1.10,'ミ':1.06,'イ':1.03}
CY = 372           # そろえる中心の高さ（フォント単位）

import os
FONT_DIR = os.environ.get('FONT_DIR', '.')
f = TTFont(os.path.join(FONT_DIR, f'ZenKakuGothicNew-{WEIGHT}.ttf')); gs = f.getGlyphSet(); cmap = f.getBestCmap()

class Flat(BasePen):
    def __init__(s, gs): super().__init__(gs); s.c=[]; s.cur=None
    def _moveTo(s,p): s.cur=[p]; s.c.append(s.cur)
    def _lineTo(s,p): s.cur.append(p)
    def _curveToOne(s,p1,p2,p3):
        p0=s.cur[-1]
        for i in range(1,9):
            t=i/8; a=(1-t)**3; b=3*(1-t)**2*t; c=3*(1-t)*t*t; d=t**3
            s.cur.append((a*p0[0]+b*p1[0]+c*p2[0]+d*p3[0], a*p0[1]+b*p1[1]+c*p2[1]+d*p3[1]))
    def _qCurveToOne(s,p1,p2):
        p0=s.cur[-1]
        for i in range(1,7):
            t=i/6; s.cur.append(((1-t)**2*p0[0]+2*(1-t)*t*p1[0]+t*t*p2[0], (1-t)**2*p0[1]+2*(1-t)*t*p1[1]+t*t*p2[1]))
    def _closePath(s): pass
    def _endPath(s): pass

def glyph(ch):
    """文字ごとの変換（拡大・中心合わせ）を済ませた輪郭の点列と、行ごとの左右端"""
    g = gs[cmap[ord(ch)]]; k = SCALE.get(ch, 1.0)
    fp = Flat(gs); g.draw(fp)
    xs=[x for c in fp.c for x,_ in c]; ys=[y for c in fp.c for _,y in c]
    cx0=(min(xs)+max(xs))/2; cy0=(min(ys)+max(ys))/2
    tf = lambda x,y: ((x-cx0)*k, (y-cy0)*k + CY)    # 横は中心0、縦は中心をCYに
    cons=[[tf(x,y) for x,y in c] for c in fp.c]
    # 1単位=1pxで塗って、行ごとの左端・右端を取る（輪郭ごとにXORして穴を抜く）
    X0,X1=-700,700; Y0,Y1=-200,1000
    img=Image.new('1',(X1-X0,Y1-Y0),0)
    for c in cons:
        m=Image.new('1',img.size,0); ImageDraw.Draw(m).polygon([(x-X0,Y1-y) for x,y in c],fill=1)
        img=ImageChops.logical_xor(img,m)
    px=img.load(); W,H=img.size; L={}; R={}
    for row in range(0,H,4):
        on=[x for x in range(0,W,2) if px[x,row]]
        if on: L[row]=on[0]+X0; R[row]=on[-1]+X0
    xs2=[x for c in cons for x,_ in c]
    return dict(ch=ch,g=g,k=k,cx0=cx0,cy0=cy0,L=L,R=R,xmin=min(xs2),xmax=max(xs2))

def layout(word):
    gl=[glyph(ch) for ch in word]
    Hs=[max(y for c in [0] for y in [0])]  # dummy
    H = 860  # 基準の文字の高さ（サ・ケの高さ）
    target=GAP*H; cap=target*CAP
    offs=[0.0]
    rows=sorted(set().union(*[set(g['L']) for g in gl]))
    for a,b in zip(gl,gl[1:]):
        prevoff=offs[-1]
        both=[r for r in rows if r in a['R'] and r in b['L']]
        def mean_gap(ob):
            # 両方に輪郭がある行だけで、向かい合う輪郭の距離を平均する（上限capで打ち切り）
            ds=[min(cap,(b['L'][r]+ob)-(a['R'][r]+prevoff)) for r in both]
            return sum(ds)/len(ds)
        def min_gap(ob):
            return min((b['L'][r]+ob)-(a['R'][r]+prevoff) for r in both)
        lo,hi=prevoff-500, prevoff+3000
        for _ in range(40):
            mid=(lo+hi)/2
            if mean_gap(mid)<target or min_gap(mid)<target*MINR: lo=mid
            else: hi=mid
        offs.append((lo+hi)/2 + KERN.get(a['ch']+b['ch'],0))
    # 最小の実際の隙間も確認（くっつき防止）
    paths=[]; minx=min(g['xmin']+o for g,o in zip(gl,offs)); maxx=max(g['xmax']+o for g,o in zip(gl,offs))
    for g,o in zip(gl,offs):
        sp=SVGPathPen(gs)
        k=g['k']
        # SVGはyが下向き：y' = TOP - y
        tp=TransformPen(sp,(k,0,0,-k, o-minx - g['cx0']*k, TOP_Y - (CY - g['cy0']*k)))
        g['g'].draw(tp); paths.append(sp.getCommands())
    return paths, maxx-minx

TOP_Y = 372+470  # CY+470 を上端0に
out={}
for word in ['オサケノミタイ','サケノツマミ']:
    paths,w=layout(word)
    vb_h=940
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {vb_h}" role="img" aria-label="{word}">'+''.join(f'<path d="{p}"/>' for p in paths)+'</svg>'
    name={'オサケノミタイ':'osakenomitai','サケノツマミ':'sakenotsumami'}[word]
    open(f'{name}-{WEIGHT.lower()}{SUFFIX}.svg','w').write(svg)
    out[word]=round(w)
print(WEIGHT, GAP, out)
