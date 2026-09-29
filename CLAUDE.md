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
| `brand/` | ロゴタイプのSVG（サケノツマミ・オサケノミタイ） |
| `tools/logotype.py` | ロゴタイプをフォントから線に起こす |

## 決めごと

- **レシピは誰でも見られる。保存だけ会員にする**（2026-09-28にShiryuが決定）。ログインは Google とメールリンク（パスワードなし）。
- レシピを足すときは、既存と同じ書き方（常体、手順3〜5、お酒2〜3個）にする。鶏肉・豚肉は火の通りを確かめる手順を入れる。
- 写真はGeminiで生成し、`python3 tools/photos.py` で変換する。生成画像は背景の端に酒瓶の文字や人物が入りやすいので、中央やや下に寄せて切り抜いている。
- お酒を扱うアプリなので、「お酒は20歳になってから」などの注意表示を消さない。マネタイズの検討は https://claude.ai/artifact/FKV4KTo1wEVTgr59R8DLPC

## Firestoreのルールの反映

今はFirebaseコンソールの「ルール」に貼って公開している（2026-09-28にCoworkが初回を公開済み）。
`firestore.rules` を変えたら、コンソールにも同じ内容を反映する。

## ロゴ

2026-09-29にShiryuと決めた。オサケノミタイと同じ作り方・同じ字間でそろえる。

- 書体は **Zen Kaku Gothic New の Black**。文字をSVGの線に起こして使う（端末によって書体が変わらないように）。
- 字間は3案（文字の高さの約22%・29%・36%）から、**いちばん広い約36%（案C）**を採用。
- 小さく見える字は少し大きくする（ノ12%・マ10%・ツ7%・ミ6%・イ3%）。文字の中心の高さはそろえる。
- 字間は自動で置いたあと、組み合わせごとに目で見て直している（`tools/logotype.py` の `KERN`）。
- 使っている場所：アプリ上部の `.logo`、個人サイトのProject。オサケノミタイ側は `~/dev/osakenomitai/CLAUDE.md` を参照。
