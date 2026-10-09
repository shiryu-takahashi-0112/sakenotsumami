"""投稿管理ツール（Postboard）への接続（schedule_instagram.py・schedule_threads.py から使う）。

鍵の扱い（2026-10-09：クラウドのルーティーンでも動くようにした）
- 環境変数 POSTBOARD_API_KEY があれば、それを Authorization: Bearer で付ける。
- 無ければ、Mac の鍵のファイル（~/.config/sns-scheduler/api-key。POSTBOARD_KEY_FILE で場所を変えられる）があれば使う。
- どちらも無ければ、Authorization を付けない。クラウドの環境では /api/ への通信に鍵が自動で付く
  （自分で付けると、自動で付く鍵とぶつかって失敗するおそれがある）。
鍵の中身は表示しない。
"""
import datetime
import json
import os
import pathlib
import subprocess
import sys

BASE = os.environ.get("POSTBOARD_BASE", "https://sns-scheduler.mhack.workers.dev")
BRAND, IG, TH = 2, 4, 2     # サケノツマミのブランド、Instagram・Threads のアカウント


def _key():
    k = os.environ.get("POSTBOARD_API_KEY", "").strip()
    if k:
        return k
    f = pathlib.Path(os.environ.get("POSTBOARD_KEY_FILE", "~/.config/sns-scheduler/api-key")).expanduser()
    return f.read_text().strip() if f.exists() else ""


def api(method, path, body=None, form=None):
    cmd = ["curl", "-sS", "-X", method]
    key = _key()
    if key:
        cmd += ["-H", f"Authorization: Bearer {key}"]
    cmd.append(BASE + path)
    if body is not None:
        cmd += ["-H", "Content-Type: application/json", "--data-binary", json.dumps(body, ensure_ascii=False)]
    for k, v in (form or {}).items():
        cmd += ["-F", f"{k}={v}"]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    try:
        res = json.loads(out)
    except json.JSONDecodeError:
        sys.exit(f"失敗：{path} の返事が JSON ではありません（先頭: {out[:200]}）")
    if not res.get("ok"):
        sys.exit(f"失敗：{path} {res}")
    return res


def taken_times(account):
    """そのアカウントの予定（取り消していないもの）の日時の集合（UTC の datetime）。
    クラウドでは registered.json が古いことがあるので、二重に入れないよう Postboard の予定とも比べる。"""
    posts = api("GET", f"/api/posts?tab=queue&brand={BRAND}&account={account}")["posts"]
    out = set()
    for p in posts:
        if any(t.get("account_id") == account for t in p.get("targets", [])):
            out.add(parse(p["scheduled_at"]))
    return out


def parse(s):
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(datetime.timezone.utc)
