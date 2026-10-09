#!/usr/bin/env bash
# クラウドの環境（Ubuntu）で、リールを作るのに要るものを入れて、動くかを確かめる。
#   bash tools/reels/setup_cloud.sh
# 入れるもの：ffmpeg（apt）、playwright（npm ci）、Chromium（npx playwright install --with-deps chromium）
set -euo pipefail
cd "$(dirname "$0")"

SUDO=""
if [ "$(id -u)" != "0" ] && command -v sudo >/dev/null 2>&1; then SUDO="sudo"; fi

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "ffmpeg を入れます"
  $SUDO apt-get update -qq
  DEBIAN_FRONTEND=noninteractive $SUDO apt-get install -y -qq ffmpeg
fi
ffmpeg -hide_banner -encoders 2>/dev/null | grep -q libx264 || { echo "ffmpeg に libx264 がありません"; exit 1; }

command -v node >/dev/null 2>&1 || { echo "Node.js がありません（18以上が要る）"; exit 1; }
npm ci --no-audit --no-fund
# --with-deps は Chromium が使うライブラリも apt で入れる（root か sudo が要る）
if [ -n "$SUDO" ] || [ "$(id -u)" = "0" ]; then
  npx playwright install --with-deps chromium
else
  npx playwright install chromium
fi

python3 --version
node --version
ffmpeg -version | head -1

# 1コマだけ撮って確かめる（レシピの読み込み・フォント・ブラウザ）
python3 make_reel_v2.py saba-lemon --drink sour --hook "これ、サバ缶です" --sub "火を使わず5分" --preview 0.5
echo "準備ができました"
