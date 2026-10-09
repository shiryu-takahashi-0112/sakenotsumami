#!/bin/bash
# 確認用：縦長のコマを横に並べた1枚にする。赤枠=文字を置いてよい範囲、青線=プロフィール一覧の3:4切り抜き。
#   video/contact_sheet.sh out.png a.png b.png ...
out=$1; shift
args=(); f=""; i=0
for p in "$@"; do
  args+=(-i "$p")
  f+="[$i:v]drawbox=x=80:y=250:w=850:h=1420:color=red@0.8:t=4,drawbox=x=0:y=240:w=1080:h=1440:color=blue@0.7:t=3,scale=360:640[v$i];"
  i=$((i+1))
done
ins=""; for ((k=0;k<i;k++)); do ins+="[v$k]"; done
ffmpeg -loglevel error -y "${args[@]}" -filter_complex "${f}${ins}hstack=inputs=$i" "$out"
echo "$out"
