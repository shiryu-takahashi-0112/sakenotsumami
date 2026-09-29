# サケノツマミ

お酒の種類から合うつまみを探せるレシピアプリ。
オサケノミタイ（`~/dev/osakenomitai`）の姉妹アプリで、色・書体・フッターの作りをそろえている。

- 本番：https://shiryu-takahashi-0112.github.io/sakenotsumami/ （GitHub Pages。`main` にpushすると反映）
- 個人サイトのProjectに掲載している。内容・URL・ステータスが変わったら、個人サイトも直す。

## 構成

| ファイル | 中身 |
|---|---|
| `index.html` | 画面のすべて（さがす・保存・マイページ、ログイン） |
| `recipes.js` | お酒・道具・レシピ100品のデータ（すべて2人分） |
| `firebase-config.js` | Firebaseのウェブ設定（プロジェクト `sakenotsumami`。公開して問題ない値） |
| `firestore.rules` | 保存データのルール。本人だけが `users/{uid}/saves/{レシピid}` を読み書きできる |
| `images/<id>.jpg` | アプリで使う料理写真（800px） |
| `images/raw/` | 生成したままの写真。重いのでgitに入れない |
| `images/PROMPTS.md` | 写真の生成指示（共通文＋料理ごとの文） |
| `tools/photos.py` | `raw/` から `images/<id>.jpg` を作る |
| `tools/build_pages.py` | 検索用のページ（`recipes/<id>/`・`drinks/<id>/`）と `sitemap.xml` を書き出す |
| `privacy.html`・`terms.html` | プライバシーポリシーと利用規約 |
| `brand/` | ロゴタイプのSVG（サケノツマミ・オサケノミタイ） |
| `tools/logotype.py` | ロゴタイプをフォントから線に起こす |

## 決めごと

- **`recipes.js` を変えたら、必ず `python3 tools/build_pages.py` を実行してからコミットする。** アプリはJavaScriptで画面を描くため、検索エンジンと共有時のプレビュー用に、同じ内容を素のHTMLでも持っている。公開URLが変わったら、このスクリプトの `BASE` と `index.html` の `canonical`・`og:` を直す。

- **レシピは誰でも見られる。保存だけ会員にする**（2026-09-28にShiryuが決定）。ログインは Google とメールリンク（パスワードなし）。
- レシピを足すときは、既存と同じ書き方（常体、手順3〜5、お酒2〜3個）にする。鶏肉・豚肉は火の通りを確かめる手順を入れる。
- 写真はGeminiで生成し、`python3 tools/photos.py` で変換する。生成画像は背景の端に酒瓶の文字や人物が入りやすいので、中央やや下に寄せて切り抜いている。
- お酒を扱うアプリなので、「お酒は20歳になってから」などの注意表示を消さない。マネタイズの検討は https://claude.ai/artifact/FKV4KTo1wEVTgr59R8DLPC

## Firestoreのルールの反映

今はFirebaseコンソールの「ルール」に貼って公開している（2026-09-28にCoworkが初回を公開済み）。
`firestore.rules` を変えたら、コンソールにも同じ内容を反映する。

## ロゴ

2026-09-29にShiryuと決めた（案D）。オサケノミタイも同じ条件で作っている。

- 書体は **Zen Kaku Gothic New の Black**。文字をSVGの線に起こして使う（端末によって書体が変わらないように）。
- **字間はフォント本来の字間に、0.06文字分を足す**（最初にアプリに置いていた文字のロゴと同じ並べ方）。文字の大きさの補正はしない。
- 例外は2か所だけ：**ノの左右を1文字の5%ずつ詰め、ケとノの間はさらに6%詰める**。
- **見た目で均等になるよう字間を詰める作り方（案C）は、Shiryuから「字間が狭すぎて不自然」と言われてやめた。** カタカナ本来のマス目のリズムを崩さない。
- 作り直しは `tools/logotype.py`（`python3 tools/logotype.py 0.06 -final 0.05 0.06`）。SVGは `brand/`。
- **ファビコンは「サ」の一文字**（黄色の地、Zen Kaku Gothic New Black。`icons/favicon.svg`・`favicon-32.png`）。2026-09-29にShiryuが指定。ホーム画面のアプリアイコンは「サケノ／ツマミ」の2行のまま。
- 使っている場所：アプリ上部の `.logo`、20歳の確認画面、アプリアイコン（サケノ／ツマミの2行）、共有画像 `og-image.jpg`、個人サイトのProject。アイコンと共有画像は `~/sakenotsumami-cowork/brand/` のHTMLから書き出している。

## SNS

2026-09-29にShiryuと決めた。運用方針の全文は https://claude.ai/artifact/X8hZavqnBU56yUkdpauZL4

- アカウントは専用のものを5つ（Instagram・Threads・X・TikTok・YouTube）。MACROHACKと同じく、Coworkが毎日12時にまとめて作成し、公開は予約で18時。
- **話し方は案A「ブランドとして淡々と、温度は居酒屋のカウンター程度」。** 一人称は使わず、アプリの `catch`・`why` と同じ文体。人格（大将風・AIアンバサダー）は立てない。写真がAI生成なので、「作った・飲んだ」と体験を語らない。
- 投稿の末尾には必ず「お酒は20歳になってから」と「※写真はAIで作ったイメージです」を入れる。飲む動作、一気・飲みすぎを連想させる言葉、銘柄は出さない。
- 動画と画像は `~/sakenotsumami-cowork/` の仕組みで作る。
