# サケノツマミ リールの作り足しの道具（クラウド用）

レシピ（リポジトリ直下の `recipes.js` と `images/<id>.jpg`）から、Instagram・TikTok 用の縦動画（v2・冒頭のフック付き）と、Threads の投稿文を作り、投稿管理ツール（Postboard）に予約として入れる道具です。
2026-10-09に、Shiryu の Mac の `~/sakenotsumami-cowork` から、クラウドのルーティーンで動かすために必要なものだけを移しました。
毎週の手順は `ROUTINE.md` にあります。

> 予約・投稿をする道具が入っています。
> `postboard/schedule_instagram.py`・`postboard/schedule_threads.py` は、`--dry` を付けずに流すと Postboard に予約が入ります。
> 試すときは必ず `--dry` を付けてください。

### 必要なもの

| もの | 使う所 | 入れ方（Ubuntu） |
|---|---|---|
| Python 3.9 以上 | すべての入口 | 標準のライブラリだけを使う。`pip install` は要らない |
| Node.js 18 以上 | `lib/load_recipe.mjs`（レシピの読み込み）・`video/render.mjs`（コマの撮影） | 多くの環境に最初から入っている |
| Playwright と Chromium | HTML の型を1コマずつ撮る | `npm ci` のあと `npx playwright install --with-deps chromium` |
| ffmpeg（libx264・aac 入り） | コマをつないで mp4 にする・表紙の jpg | `apt-get install -y ffmpeg` |
| curl | Postboard への接続 | 多くの環境に最初から入っている |

まとめて入れるときは、次を流します。

```plain text
bash tools/reels/setup_cloud.sh
```

`setup_cloud.sh` は、ffmpeg が無ければ `apt-get` で入れ（root でなければ `sudo` を使う）、`npm ci` と Chromium の取得を行い、最後に1コマだけ撮って動くかを確かめます。

- ブラウザは、Mac では入っている Google Chrome を、Linux では Playwright の Chromium を使います（`video/render.mjs`・`shoot.mjs`）。
  環境変数 `PLAYWRIGHT_CHANNEL` で上書きできます（空文字なら同梱の Chromium）。
- 文字は `fonts/` の Zen Kaku Gothic New をファイルから読むので、環境の日本語フォントには頼りません。
- BGM は `video/bgm_v2.py` が波形から作るので、外部の音源は要りません。

### 使い方

```plain text
cd tools/reels
python3 make_reel_v2.py saba-lemon --drink sour --hooks-file reels/hooks_2026-10-10_10-29.json   # 1品型 → reels/queue/saba-lemon/
python3 make_list_reel_v2.py --drink beer --theme quick --hooks-file reels/hooks_<期間>.json       # ◯選型 → reels/queue/list-beer-quick-<6桁>/
python3 make_batch.py --hooks-file reels/hooks_<期間>.json saba-lemon:sour list:beer:quick       # まとめて
python3 make_reel_v2.py saba-lemon --drink sour --preview 0.5 3 8                                # 指定秒のコマだけ（確認用）
video/contact_sheet.sh out.png work/v2_saba-lemon/preview/*.png                                  # 確認用のコマを並べる（赤＝文字の安全範囲、青＝3:4）
python3 check_pairing.py                                                                         # 見出しのお酒と合う理由のずれ（0件であること）
node lib/load_recipe.mjs --list                                                                  # レシピの id の一覧
```

- 1本を作るのに、Mac（Apple Silicon）で約2分半かかります。
  7本で20分前後なので、クラウドでも時間に余裕を持たせてください。
- 動画の作り方・フック・BGM・キャプションの決まりは、Mac の `~/sakenotsumami-cowork/README.md` と同じです（このフォルダに移したのは v2 だけ。旧版の `make_reel.py`・`make_list_reel.py`・カルーセルは移していません）。

### Postboard への予約

```plain text
python3 postboard/schedule_instagram.py --schedule schedule/<開始日>_<終了日>.json --dry   # 入れる予定だけを出す
python3 postboard/schedule_threads.py postboard/threads_<開始日>_<終了日>.json --dry
```

- 動画は、手元の `reel.mp4` をそのまま `POST /api/media` に送ります（multipart。Postboard の保存場所 R2 に置かれ、`/media/<キー>` の URL ができる）。
  URL を渡す方式ではありません。
- リールは毎日12時（日本時間。2026-10-08にShiryuが18時から変えた）。`--time` で変えられます。
- 二重に入れないよう、`postboard/registered.json` に入れたものを残し、あわせて Postboard の予定とも比べます（Instagram は同じ日、Threads は同じ時刻があれば飛ばす）。
- 鍵の扱いは `postboard/pb.py` にまとめています。

| 環境 | 鍵 |
|---|---|
| クラウドのルーティーン | 何も設定しない。`Authorization` のヘッダーを付けずに呼べば、環境が `/api/` への通信に鍵を自動で付ける |
| 環境変数で渡すとき | `POSTBOARD_API_KEY` |
| Shiryu の Mac | `~/.config/sns-scheduler/api-key`（`POSTBOARD_KEY_FILE` で場所を変えられる） |

鍵の中身は表示しません。

### 状態の記録（コミットして残すもの）

クラウドの環境は実行のたびに作り直されるので、次の回に要るものはリポジトリに残します。

| ファイル | 中身 |
|---|---|
| `state/used.json` | これまで動画・カルーセルに出した品。◯選型の自動選択（`lib/pick.py`）と、品を選ぶときに見る。予約したあと `python3 state/record_used.py schedule/<期間>.json` で足す |
| `postboard/registered.json` | Postboard に入れた予約の ID |
| `schedule/<期間>.json`・`.md` | 週ごとの動画の一覧 |
| `postboard/threads_<期間>.json` | Threads の投稿文 |
| `reels/hooks_<期間>.json` | 動画の冒頭のフック |

作った動画（`reels/queue/`）と作業用（`work/`）は `.gitignore` で除いています。
動画は Postboard に上げたものが正本になります。

### ファイルの構成

| ファイル | 役割 |
|---|---|
| `make_reel_v2.py`・`make_list_reel_v2.py`・`make_batch.py` | 入口（1品型・◯選型・まとめて） |
| `lib/common.py` | レシピ読み込み・見出し・キャプション・禁止の言い回し・お酒と合う理由のルール |
| `lib/v2.py` | v2 の部品（ポイントの1行・主な材料・フック） |
| `lib/build.py` | コマの撮影 → BGM → mp4・表紙 |
| `lib/pick.py` | ◯選型の品の自動選択 |
| `lib/load_recipe.mjs` | `recipes.js` を JSON にする（既定はこのリポジトリの `recipes.js`。`SAKE_RECIPES` で変えられる） |
| `lib/phrase.js` | 日本語の文を単語の途中で改行しない |
| `video/reel_v2.html`・`video/list_reel_v2.html` | 動画の型 |
| `video/cover.html`・`shoot.mjs` | フックが無い動画の表紙（今の手順では使わないが、`--hook` を省いたときに要る） |
| `video/render.mjs` | Playwright で30fpsのコマを撮る |
| `video/bgm_v2.py` | BGM を波形から作る |
| `video/contact_sheet.sh` | 確認用のコマを並べる |
| `check_pairing.py` | 見出しのお酒と合う理由のずれを調べる |
| `postboard/pb.py` | Postboard への接続（鍵の扱い・予定の一覧） |
| `postboard/schedule_instagram.py`・`schedule_threads.py` | 予約に入れる |
| `postboard/apply_hook_caption.py` | キャプションの1行目をフックにする（作り直し用） |
| `postboard/build_threads.py`・`build_threads_<期間>.py` | Threads の投稿文を作る（新しい週は、いちばん新しいものを写して日付と品を変える） |
| `postboard/humor_2026-10-12_10-29.json` | 15:05・21:00 の笑いの投稿のお手本 |
| `schedule/build_schedule_<期間>.py` | 週の動画の一覧を作る（同じく写して使う） |
| `fonts/` | Zen Kaku Gothic New（OFL。`OFL.txt`） |
| `brand/logotype.svg` | 動画の締めのロゴ |

### 移したときに変えたこと（2026-10-09）

- Mac の絶対パス（`/Users/shiryutakahashi/dev/sakenotsumami`）を、このフォルダからの相対パス（リポジトリ直下）にした。
- `make_reel.py` の `build_video` と `make_cover.py` の表紙の処理を `lib/build.py` に、`make_list_reel.py` の品の選び方を `lib/pick.py` に移した（中身は同じ）。
- 品の選び方は、`reels/queue`・`reels/posted` に加えて `state/used.json` も見るようにした。
- ブラウザを、Mac では Chrome、Linux では Chromium にした。
- 予約の道具から、鍵のファイルを必ず読む部分と、カルーセル（Mac の `sips` を使っていた）を外した。
  リールの時刻の既定を12時にし、Postboard の予定と比べて二重に入れないようにした。
- `make_batch.py` は動画だけを作るようにし、`--hooks-file` を渡せるようにした。
- 同じレシピ（saba-lemon・レモンサワー・フック付き）で、Mac の元の仕組みの出力（`review/v4-bgm/saba-lemon`）と比べた。
  キャプション・表紙・音声は完全に同じで、映像は平均 PSNR 55.7dB（目では差が分からない程度。いくつかのコマは完全に同じ）だった。
