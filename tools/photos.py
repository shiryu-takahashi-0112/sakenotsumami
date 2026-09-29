#!/usr/bin/env python3
"""images/raw/<id>.png|jpg（生成したままの画像）を、アプリで使う images/<id>.jpg に変換する。

生成画像は奥に酒瓶のラベルや人物が写りやすいので、料理のある中央やや下を正方形に寄せて切り抜く。
800px・JPEG画質80に縮める（一覧72px・詳細の横幅いっぱいの両方に足りる大きさ）。
"""
from pathlib import Path
from PIL import Image

IMAGES = Path(__file__).resolve().parent.parent / 'images'
ZOOM = 0.72      # 元の一辺に対する切り抜く一辺の割合
CENTER_Y = 0.56  # 切り抜きの中心の高さ（0=上端、1=下端）
SIZE = 800

for src in sorted((IMAGES / 'raw').glob('*')):
    if src.suffix.lower() not in ('.png', '.jpg', '.jpeg'):
        continue
    im = Image.open(src).convert('RGB')
    w, h = im.size
    s = int(min(w, h) * ZOOM)
    left = (w - s) // 2
    top = min(max(int(h * CENTER_Y - s / 2), 0), h - s)
    out = IMAGES / f'{src.stem}.jpg'
    im.crop((left, top, left + s, top + s)).resize((SIZE, SIZE), Image.LANCZOS).save(out, quality=80, optimize=True)
    print(f'{out.name} ({out.stat().st_size // 1024}KB)')
