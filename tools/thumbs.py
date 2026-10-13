#!/usr/bin/env python3
"""表示を速くするための、小さい写真（WebP）を作る（2026-10-13、Shiryu「画像を読み込むスピードが遅い」）。

  python3 tools/thumbs.py          # 足りないもの・元の写真が変わったものだけ作る
  python3 tools/thumbs.py --force  # すべて作り直す

images/<id>.jpg（800px）と images/drinks/・images/ingredients/ の写真から、次の3つを作る。
  images/w240/<id>.webp … 一覧の小さい写真（72px）
  images/w480/<id>.webp … ホームの横に流れるカード（132px）
  images/w720/<id>.webp … レシピの詳細の大きい写真
元の 800px の JPEG は、共有のプレビュー（og:image）と検索用の構造化データで使うので残す。

どの元の写真から作ったかは tools/image_sizes.json に持つ（元の写真の中身のハッシュ）。
写真を差し替えたら、次に実行したときに作り直される。
Pillow が要る（Mac の python3 には入っている）。tools/build_pages.py が最初にこれを呼ぶ。
Pillow が無い環境（GitHub Actions のビルド確認など）では何もしない。作ったファイルはコミットする。
"""
import hashlib, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMAGES = ROOT / 'images'
SIZES = (240, 480, 720)
QUALITY = 75
MANIFEST = ROOT / 'tools' / 'image_sizes.json'


def sources():
    """元の写真（images 直下と、お酒・食材の写真）。images/images 以下の相対パス"""
    out = sorted(p.relative_to(IMAGES) for p in IMAGES.glob('*.jpg'))
    for kind in ('drinks', 'ingredients'):
        out += sorted(p.relative_to(IMAGES) for p in (IMAGES / kind).glob('*.jpg'))
    return out


def out_path(rel, w):
    return IMAGES / f'w{w}' / rel.with_suffix('.webp')


def ensure(force=False, quiet=False):
    try:
        from PIL import Image
    except ImportError:
        return 0
    try:
        manifest = json.loads(MANIFEST.read_text())
    except (FileNotFoundError, ValueError):
        manifest = {}
    made = 0
    srcs = sources()
    for rel in srcs:
        key = rel.as_posix()
        digest = hashlib.sha1((IMAGES / rel).read_bytes()).hexdigest()[:16]
        if not force and manifest.get(key) == digest and all(out_path(rel, w).exists() for w in SIZES):
            continue
        im = Image.open(IMAGES / rel).convert('RGB')
        for w in SIZES:
            o = out_path(rel, w)
            o.parent.mkdir(parents=True, exist_ok=True)
            h = round(im.height * w / im.width)
            im.resize((w, h), Image.LANCZOS).save(o, 'WEBP', quality=QUALITY, method=6)
        manifest[key] = digest
        made += 1
    # 元の写真が無くなったものは消す
    keep = {r.as_posix() for r in srcs}
    for key in [k for k in manifest if k not in keep]:
        for w in SIZES:
            out_path(pathlib.PurePosixPath(key), w).unlink(missing_ok=True)
        del manifest[key]
        made += 1
    if made:
        MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=0, sort_keys=True) + '\n')
        if not quiet:
            print(f'thumbs: {made}枚を作り直しました')
    return made


def has(rel, w=240):
    """小さい写真があるか（images からの相対パス。例: 'mugen-piman.jpg'）"""
    return out_path(pathlib.PurePosixPath(rel), w).exists()


if __name__ == '__main__':
    ensure(force='--force' in sys.argv)
