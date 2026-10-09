#!/usr/bin/env python3
"""見出しのお酒と、表示する文（合う理由）のお酒がずれていないかを全組み合わせで確かめる。

  python3 check_pairing.py

全レシピ × 各レシピの drinks（＋ --drink を省いたときの既定のお酒）のすべてについて、次の文を調べる。
  - 1品型・カルーセルの「合う理由」とキャプション（lib/common.py の pairing_text → caption）
  - ◯選型で1品に添える1行（lib/common.py の pairing_line）
「見出しのお酒の名前が無く、別のお酒の名前だけがある」文や、使わない言い回し（common.banned_hits）を含む文が1件でもあれば、一覧を出して終了コード1で終わる。
お酒の名前・言い回しの一覧は lib/common.py の DRINK_WORDS。
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "lib"))
import common  # noqa: E402

d = common.load_all()
names = {x["id"]: x["name"] for x in d["drinks"]}
bad, raw, combos, catches = [], 0, 0, 0
for r in d["recipes"]:
    for dr in dict.fromkeys(r["drinks"] + [common.default_drink(r)]):
        combos += 1
        if not common.fits(r["why"], dr):
            raw += 1                                   # 何もしなかった場合のずれ
        text, is_catch = common.pairing_text(r, dr)
        catches += is_catch
        c = {"recipe": r, "why": text, "drinkId": dr, "drink": names[dr],
             "head1": f"{names[dr]}に合う、", "head2": f"{r['min']}分つまみ"}
        # 1行目の見出しとハッシュタグ（見出しと同じお酒の名前が入る）は除いて調べる
        body = [x for x in common.caption(c, "carousel").split("\n")[1:] if not x.startswith("#")]
        for where, t in (("1品型・カルーセル", text), ("キャプション", "\n".join(body)),
                         ("◯選型", common.pairing_line(r, dr))):
            if not common.fits(t, dr):
                bad.append(f"{r['id']}\t{names[dr]}\t{where}\t{t}")
            hit = common.banned_hits(t)
            if hit:
                bad.append(f"{r['id']}\t{names[dr]}\t{where}\t使わない言い回し {'・'.join(hit)}\t{t}")
for r in d["recipes"]:                          # catch はカルーセル・動画の見出し周りにも出る
    hit = common.banned_hits(r["catch"])
    if hit:
        bad.append(f"{r['id']}\tcatch\t使わない言い回し {'・'.join(hit)}\t{r['catch']}")
print(f"レシピ: {len(d['recipes'])} 品")
print(f"調べた組み合わせ: {combos}（各レシピの drinks ＋ 既定のお酒）")
print(f"why のままだとずれる組み合わせ: {raw}")
print(f"catch に置き換えた組み合わせ: {catches}")
print(f"ずれ・使わない言い回しが残っている文: {len(bad)} 件")
for b in bad:
    print("  " + b)
sys.exit(1 if bad else 0)
