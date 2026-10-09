"""動画を書き出す部品（make_reel_v2.py・make_list_reel_v2.py・make_cover.py から使う）。

2026-10-09：クラウドのルーティーンで動かすため、~/sakenotsumami-cowork から移した。
中身は元の make_reel.build_video と make_cover.shoot_cover / prepend_cover と同じ。
旧版の型（reel.html・list_reel.html・bgm.py）は移していないので、BGM の既定は bgm_v2.py にした。
"""
import json
import pathlib
import re
import subprocess
import sys

import common

ROOT = common.ROOT
LEAD = 0.5          # 動画の先頭に置く表紙の長さ（秒）。フックの無い動画だけ
MARK = ".cover-v1"  # 表紙を足し終えた印（フックのある動画では「最初のコマが表紙」の印）


def build_video(html, work, out, lead_cover=True, bgm="bgm_v2.py"):
    """HTMLを30fpsで撮り、BGMを合成して reel.mp4 と cover.jpg を out に書き出す（◯選型でも使う）。
    bgm="bgm_v2.py"：テンポの速いBGM。場面の切り替え（marks）と文字が出る時刻（accents）に音を置く。
    lead_cover=False（冒頭のフックがある v2）：先頭に表紙の静止画を足さず、動画の最初のコマ（フックが出ている絵）を cover.jpg にする。"""
    frames = work / "frames"
    common.run(["node", str(ROOT / "video" / "render.mjs"), str(html), str(frames)])
    tl = json.loads((frames / "timeline.json").read_text())
    dur = tl["frames"] / tl["fps"]
    bgm_cmd = [sys.executable, str(ROOT / "video" / bgm), "--dur", f"{dur:.3f}",
               "--marks", ",".join(f"{m:.3f}" for m in tl["marks"]), "--out", str(work / "bgm.wav")]
    if tl.get("accents"):
        bgm_cmd += ["--accents", ",".join(f"{m:.3f}" for m in tl["accents"])]
    common.run(bgm_cmd)
    wav = work / "bgm.wav"
    out.mkdir(parents=True, exist_ok=True)
    common.run(["ffmpeg", "-loglevel", "error", "-y",
                "-framerate", "30", "-i", str(frames / "%04d.png"), "-i", str(wav),
                "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-profile:v", "high",
                "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
                "-movflags", "+faststart", "-shortest", str(out / "reel.mp4")])
    (out / MARK).unlink(missing_ok=True)
    if not lead_cover:
        # 2026-10-09：最初のコマにフックが出ていて、0.3秒以内に写真が寄る。静止画を足すと動きが遅れるので足さない。
        common.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(frames / "0000.png"), "-q:v", "2", str(out / "cover.jpg")])
        (out / MARK).write_text("冒頭のフック版：最初のコマが表紙（表紙の静止画は足さない）\n", encoding="utf-8")
        return out
    # 表紙：料理の写真と見出しの1枚（video/cover.html）。TikTokは最初のコマが表紙になるので、動画の先頭0.5秒にも置く
    prepend_cover(shoot_cover(html, out), out)
    return out


def shoot_cover(reel_html, out):
    """動画を撮ったときの HTML（DATA 入り）から表紙を描き、out/cover.jpg を書き出す。"""
    m = re.search(r"^window\.DATA = .*;$", pathlib.Path(reel_html).read_text(encoding="utf-8"), re.M)
    if not m:
        sys.exit(f"DATA が見つかりません: {reel_html}")
    tpl = (ROOT / "video" / "cover.html").read_text(encoding="utf-8")
    html = pathlib.Path(reel_html).with_name("cover.html")
    html.write_text(tpl.replace("/*__DATA__*/", m.group(0)).replace("__ROOT__", ROOT.as_uri()), encoding="utf-8")
    png = pathlib.Path(reel_html).with_name("cover.png")
    common.run(["node", str(ROOT / "shoot.mjs"), str(html), str(png), "1080", "1920"], stdout=subprocess.DEVNULL)
    out = pathlib.Path(out)
    common.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(png), "-q:v", "2", str(out / "cover.jpg")])
    return png


def prepend_cover(png, out):
    """out/reel.mp4 の先頭に、表紙の静止画を LEAD 秒足す（音は同じだけ無音を足して後ろへずらす）。"""
    out = pathlib.Path(out)
    if (out / MARK).exists():
        return False
    src, tmp = out / "reel.mp4", out / "reel.tmp.mp4"
    ms = int(LEAD * 1000)
    common.run(["ffmpeg", "-loglevel", "error", "-y",
                "-loop", "1", "-framerate", "30", "-t", f"{LEAD}", "-i", str(png), "-i", str(src),
                "-filter_complex",
                f"[0:v]format=yuv420p,setsar=1[c];[1:v]setsar=1[v];[c][v]concat=n=2:v=1:a=0[vo];"
                f"[1:a]adelay={ms}|{ms}[ao]",
                "-map", "[vo]", "-map", "[ao]",
                "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-profile:v", "high",
                "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
                "-movflags", "+faststart", str(tmp)])
    tmp.replace(src)
    (out / MARK).write_text("動画の先頭0.5秒に表紙を足した（make_cover.py）\n", encoding="utf-8")
    return True
