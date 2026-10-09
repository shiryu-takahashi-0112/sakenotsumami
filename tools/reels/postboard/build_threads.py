#!/usr/bin/env python3
"""サケノツマミの Threads（@sakenotsumami.12）の投稿文を、2026-10-03〜10-16 の14日分（1日5本・70本）作る。

  python3 postboard/build_threads.py

出力: postboard/threads_2026-10-03_10-16.json
  [{"scheduled_at": "2026-10-03T11:05:00+09:00", "kind": "小ワザ", "text": "…", "recipe_ids": ["…"]}, …]

| 時刻 | 型 | 中身 |
|---|---|---|
| 11:05 | 小ワザ | つまみ作りの小さなコツ（recipes.js の手順から） |
| 15:05 | どっち派 | 2択の問いかけ（AかBで返信を促す）。お酒の量や強さは比べない |
| 17:05 | 今夜の一品 | その日のリールに合わせた1品（料理名・分・道具・合うお酒・catch か why） |
| 19:05 | その日の本文 | schedule/2026-10-05_2026-10-18.json の Threads 用の本文（10/3＝2日目 … 10/15＝14日目）。10/16 は今夜の一品 |
| 21:00 | ◯選・問いかけ | 「◯◯に合う3品」の一覧か、「今夜はなに飲みますか」系の問いかけ |

確かめること（どれかに当たれば止まる）:
  禁止語（common.banned_hits）／行数2〜5・500文字以内／「お酒は20歳になってから。」を入れない（2026-10-03にShiryuが指示）／
  ハッシュタグ1つまで（最後の行）／絵文字なし／URLは7日ごとに2回まで／同じ品は2週間で2回まで／
  今夜の一品・◯選の見出しのお酒と文のずれ（common.fits）／数字（分）は recipes.js から入れる
"""
import collections
import datetime
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "lib"))
import common  # noqa: E402

START = datetime.date(2026, 10, 3)
DAYS = 14
URL = "https://osakenomitai.com/sakenotsumami/?utm_source=threads&utm_medium=social&utm_campaign=launch"
NOTE = common.AGE_NOTE   # Threadsには入れない（2026-10-03にShiryuが「付けないで」と指示）。入っていたら外す・止める
OUT = ROOT / "postboard" / "threads_2026-10-03_10-16.json"
SCHEDULE = ROOT / "schedule" / "2026-10-05_2026-10-18.json"

D = common.load_all()
R = {r["id"]: r for r in D["recipes"]}
DRINK = {x["id"]: x["name"] for x in D["drinks"]}
TOOL = {k: v["name"] for k, v in D["tools"].items()}


def name(rid):
    return R[rid]["name"]


def mt(rid):
    """「フライパンで8分」「火を使わず5分」。数字は recipes.js から。"""
    r = R[rid]
    return f"火を使わず{r['min']}分" if r["tool"] == "none" else f"{TOOL[r['tool']]}で{r['min']}分"


def sentences(text):
    return [s + "。" for s in text.split("。") if s.strip()]


# ---- 11:05 小ワザ（手順にあるコツを1つ。説明は手順に書いてあることだけにする）
TIPS = [
    ("mugen-piman", ["無限ピーマンのツナは、油を切らずに油ごと入れる。", "鶏ガラスープの素と一緒に、ピーマンにからむ。"]),
    ("yaki-shishito", ["ししとうは、焼く前に竹串で1か所穴をあける。", "焼いている途中の破裂を防げる。"]),
    ("tomato-marinade", ["ミニトマトのマリネは、和えたあと冷蔵庫で10分以上おく。", "冷やすあいだに味がなじむ。"]),
    ("ika-butter", ["イカのバター醤油焼きは、白く色が変わったらすぐ仕上げる。", "炒めすぎると硬くなる。"]),
    ("okura-okaka", ["オクラは、塩をふってこすってから水で洗う。", "うぶ毛を取ってから、レンジで1分30秒加熱する。"]),
    ("konnyaku-pirikara", ["こんにゃくは、油をひかずにキュッと音がするまでからいりする。", "そのあとの味がしみこみやすい。"]),
    ("piman-maruyaki", ["ピーマンを丸ごと焼くときは、手で軽く押して割れ目を入れておく。", "破裂を防げる。"]),
    ("shungiku-salad", ["春菊を生で使うときは、葉をつんで冷水につける。", "パリッとさせてから、水気をよく切る。"]),
    ("hotate-butter", ["ホタテのバターソテーは、焼く前に水気をよくふく。", "表面に焼き色がつきやすくなる。"]),
    ("onion-okaka", ["オニオンスライスは、繊維に沿って薄切りにして水に5分さらす。", "水気はしっかり絞る。"]),
    ("asari-sakamushi", ["あさりの酒蒸しをレンジで作るときは、口が開いたかを見る。", "開いていないものがあれば、30秒ずつ追加で加熱する。"]),
    ("daikon-hotate", ["大根とホタテ缶のサラダは、ホタテ缶を汁ごと使う。", "缶汁のうまみが大根にしみる。"]),
    ("aburaage-pizza", ["油揚げピザは、のせる前に油揚げの余分な油をキッチンペーパーでふく。", "焼き上がりがカリッと軽くなる。"]),
    ("buri-teriyaki", ["ぶりの照り焼きは、塩をふって5分おき、出てきた水気をふく。", "それから小麦粉を薄くまぶして焼く。"]),
]

# ---- 15:05 どっち派（2択。お酒の量や強さは比べない）
WHICH = [
    ("つまみは、冷たい派？温かい派？", "冷奴やマリネ", "焼き物や炒め物", []),
    ("豆腐のつまみ、どっち派？", "のせるだけの冷奴", "カリッと焼いた豆腐ステーキ", []),
    ("チーズのつまみ、どっち派？", "とろけるまで焼く", "そのまま切ってのせる", []),
    ("枝豆、どっち派？", "塩ゆで", "にんにくと鷹の爪で炒める", []),
    ("鶏のつまみ、どっち派？", "塩とレモン", "甘辛いたれ", []),
    ("刺身のつまみ、どっち派？", "ポン酢と薬味", "わさび醤油", []),
    ("今夜のつまみ、どっち派？", "5分で作れるもの", "20分かけて焼くもの", []),
    ("キムチ、どっち派？", "冷たい豆腐にのせる", "豚肉と炒める", []),
    ("なすのつまみ、どっち派？", name("yakinasu"), name("nasu-chukadare"), ["yakinasu", "nasu-chukadare"]),
    ("長芋、どっち派？", "焼いてほくほく", "生でシャキシャキ", []),
    ("じゃがいものつまみ、どっち派？", name("shiokara-jagabutter"), name("mentai-potesala"), ["shiokara-jagabutter", "mentai-potesala"]),
    ("ねぎ、どっち派？", "薬味として少し", "主役として丸ごと焼く", []),
    ("卵のつまみ、どっち派？", name("dashimaki"), name("nira-tama"), ["dashimaki", "nira-tama"]),
    ("その日の最後の一品、どっち派？", "さっぱり", "こってり", []),
]

# ---- 17:05 今夜の一品（その日のリールのお酒に合わせる。19:05 と同じ品にならないよう、リールの別の品か同じお酒の品）
TONIGHT = [
    ("nagaimo-butter", "beer"),        # 10/3 リール：ビール・10分以内の3選
    ("chikuwa-isobe", "highball"),     # 10/4 リール：枝豆のペペロンチーノ（ハイボール）
    ("mentai-dip", "wine"),            # 10/5 リール：ワインの3選
    ("yum-woonsen", "highball"),       # 10/6 リール：ハイボール・レンジの4選
    ("caprese", "wine"),               # 10/7 リール：マッシュルームのアヒージョ（ワイン）
    ("katsuo-tataki", "sake"),         # 10/8 リール：日本酒・火を使わない3選
    ("garlic-shrimp", "beer"),         # 10/9 リール：豚キムチ（ビール）
    ("kanikama-kyuri", "sour"),        # 10/10 リール：レモンサワー・10分以内の3選
    ("chicken-negishio", "sour"),      # 10/11 リール：サバ缶マリネ（レモンサワー）
    ("horenso-goma", "shochu"),        # 10/12 リール：焼酎・レンジの3選
    ("german-potato", "beer"),         # 10/13 リール：ビールの5選
    ("namaham-cheese", "wine"),        # 10/14 リール：カマンベールのはちみつ焼き（ワイン）
    ("creamcheese-okaka", "sake"),     # 10/15 リール：日本酒の3選
    ("shiitake-mayo", "beer"),         # 10/16 リールなし
]

# ---- 19:05 その日の本文（schedule の何日目か → その本文で紹介している品）
DAY_ITEMS = {
    2: ["hanpen-cheese"], 3: ["edamame-peperoncino"], 4: ["celery-asazuke", "carrot-rapee"],
    5: ["sasami-wasabi", "broccoli-okakamayo", "snap-pea-anchovy", "yum-woonsen"], 6: ["mushroom-ajillo"],
    7: ["tomato-shiokombu"], 8: ["buta-kimchi"], 9: ["nira-tama"], 10: ["saba-lemon"],
    11: ["satsumaimo-butter", "renkon-kinpira"],
    12: ["tebanaka-shio", "tofu-steak", "enoki-bacon", "bulgogi", "german-potato"],
    13: ["camembert-honey"], 14: ["furofuki-daikon"],
}
LAST_DAY_ITEM = ("oil-sardine", "highball")   # 10/16（15日目は無いので今夜の一品）

# ---- 21:00 ◯選・問いかけ（None は問いかけ）
EVENING = [
    ("ask", ["今夜はなに飲みますか。", "ビール、ハイボール、レモンサワー、日本酒、焼酎、ワイン。", "返信で教えてください。"]),
    ("list", "highball", ["tunamayo-piman", "komatsuna-nampla", "chicken-misomayo"]),
    ("ask", ["週のはじめの夜、なに飲みますか。", "決まると、合わせるつまみも決めやすい。", "返信で教えてください。"]),
    ("list", "sake", ["aburaage-natto", "satsumaage-aburi", "mochi-cheese-nori"]),
    ("ask", ["今夜はなに飲みますか。", "冷たいつまみか、温かいつまみか。", "お酒から決めるのも一つの手。"]),
    ("list", "shochu", ["goya-champuru", "enoki-nametake", "atsuage-miso"]),
    ("ask", ["金曜の夜、なに飲みますか。", "つまみは、お酒に合わせて選べます。", "返信で教えてください。"]),
    ("list", "wine", ["kabocha-cheese-salad", "zucchini-cheese", "salmon-foil"]),
    ("ask", ["日曜の夜、なに飲みますか。", "火を使わないつまみなら、片付けも少なめ。", "返信で教えてください。"]),
    ("list", "sour", ["dakgalbi", "samgyeopsal", "sunagimo-garlic"]),
    ("ask", ["今夜はなに飲みますか。", "ビールなら塩気、ワインならチーズ、日本酒ならだし。", "返信で教えてください。"]),
    ("list", "beer", ["shishamo", "sausage-cabbage", "kimchi-yakko"]),
    ("ask", ["今夜はなに飲みますか。", "決まったら、合うつまみを一品。", "返信で教えてください。"]),
    ("ask", ["金曜の夜、なに飲みますか。", "今週のつまみで気になったものがあれば、返信で教えてください。"]),
]


def post(day, hh, mm, kind, lines, ids, tag=None):
    body = list(lines) + ([tag] if tag else [])
    return {"scheduled_at": f"{day.isoformat()}T{hh:02d}:{mm:02d}:00+09:00", "kind": kind,
            "text": "\n".join(body), "recipe_ids": list(ids)}


def tonight_lines(rid, drink):
    text, _ = common.pairing_text(R[rid], drink)
    ss = sentences(text)
    if len(ss) > 2:
        ss = sentences(R[rid]["catch"])[:2]
    return [f"今夜の一品は、{name(rid)}。", f"{mt(rid)}。"] + ss


def main():
    sched = {d_["date"]: d_ for d_ in json.loads(SCHEDULE.read_text(encoding="utf-8"))["days"]}
    sched_by_no = {k + 1: d_ for k, d_ in enumerate(sorted(sched.values(), key=lambda x: x["date"]))}
    posts, notes = [], []
    for k in range(DAYS):
        day = START + datetime.timedelta(days=k)
        wd = "月火水木金土日"[day.weekday()]
        # 11:05
        rid, lines = TIPS[k]
        posts.append(post(day, 11, 5, "小ワザ", ["小ワザ。"] + lines, [rid], "#おつまみ"))
        # 15:05
        q, a, b, ids = WHICH[k]
        posts.append(post(day, 15, 5, "どっち派", [q, f"A {a}", f"B {b}", "返信でAかBを。"], ids))
        # 17:05
        rid, drink = TONIGHT[k]
        posts.append(post(day, 17, 5, "今夜の一品", tonight_lines(rid, drink), [rid], common.DRINK_TAGS[drink]))
        # 19:05
        no = k + 2
        if no in sched_by_no and no in DAY_ITEMS:
            text = sched_by_no[no]["text"]["threads"]
            lines = text.split("\n")
            if lines[-1] == NOTE:   # 投稿一覧の本文には入っているので外す
                lines = lines[:-1]
            if lines[0].startswith("金曜の夜に、") and wd != "金":
                # 投稿を前倒ししたので、金曜でない日は「今夜は、」にする
                lines[0] = lines[0].replace("金曜の夜に、", "今夜は、", 1)
                notes.append(f"{day}（{wd}）19:05：「金曜の夜に、」を「今夜は、」に変えた（{no}日目の本文）")
            posts.append({"scheduled_at": f"{day.isoformat()}T19:05:00+09:00", "kind": "その日の本文",
                          "text": "\n".join(lines), "recipe_ids": DAY_ITEMS[no], "schedule_day": no})
        else:
            rid, drink = LAST_DAY_ITEM
            posts.append(post(day, 19, 5, "今夜の一品", tonight_lines(rid, drink), [rid], common.DRINK_TAGS[drink]))
        # 21:00
        e = EVENING[k]
        if e[0] == "ask":
            posts.append(post(day, 21, 0, "問いかけ", e[1], []))
        else:
            _, drink, ids = e
            lines = [f"{DRINK[drink]}に合う、つまみ3品。"] + [f"{name(i)}（{R[i]['min']}分・{TOOL[R[i]['tool']]}）" for i in ids]
            posts.append(post(day, 21, 0, "◯選", lines, ids, common.DRINK_TAGS[drink]))

    errors = check(posts)
    if errors:
        sys.exit("\n".join(errors))
    OUT.write_text(json.dumps(posts, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    summary(posts, notes)


EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿\U0001F000-\U0001F2FF]")


def check(posts, start=None, max_which=None):
    """start: URLの回数を数える7日ごとの区切りの最初の日。max_which: 1日の2択（どっち派）の上限（None なら数えない）。"""
    start = start or START
    errors = []
    uses = collections.Counter()
    url_weeks = collections.Counter()
    for p in posts:
        t, at = p["text"], p["scheduled_at"]
        lines = t.split("\n")
        if not 2 <= len(lines) <= 5:
            errors.append(f"{at}: 行数 {len(lines)}")
        if len(t) > 500:
            errors.append(f"{at}: {len(t)}文字")
        if "20歳になってから" in t:
            errors.append(f"{at}: 「{NOTE}」が入っている（Threadsには入れない）")
        hit = common.banned_hits(t)
        if hit:
            errors.append(f"{at}: 使わない言い回し {hit}")
        tags = re.findall(r"(?:^|\s)#\S+", t)
        if len(tags) > 1 or (tags and not lines[-1].startswith("#")):
            errors.append(f"{at}: ハッシュタグ {tags}")
        if EMOJI.search(t):
            errors.append(f"{at}: 絵文字")
        if "http" in t:
            if URL not in t:
                errors.append(f"{at}: URLがThreads用でない")
            url_weeks[(datetime.date.fromisoformat(at[:10]) - start).days // 7] += 1
        for rid in p["recipe_ids"]:
            if rid not in R:
                errors.append(f"{at}: レシピが無い {rid}")
            uses[rid] += 1
        # 分の数字が recipes.js と合っているか（料理名の直後の「（◯分・」と「◯で◯分」）
        for rid in p["recipe_ids"]:
            for m in re.finditer(re.escape(name(rid)) + r"（(\d+)分", t):
                if int(m.group(1)) != R[rid]["min"]:
                    errors.append(f"{at}: {rid} の分が違う")
        if p["kind"] in ("今夜の一品", "◯選"):
            drink = p.get("drink") or next(k for k, v in common.DRINK_TAGS.items() if v in t)
            if not common.fits(t.replace(common.DRINK_TAGS[drink], ""), drink):
                errors.append(f"{at}: 見出しのお酒と文がずれている")
            for rid in p["recipe_ids"]:
                if drink not in R[rid]["drinks"]:
                    errors.append(f"{at}: {rid} の drinks に {drink} が無い")
    if max_which:
        which = collections.Counter(p["scheduled_at"][:10] for p in posts if "どっち派" in p["text"])
        for day, n in which.items():
            if n > max_which:
                errors.append(f"{day}: 2択が{n}本")
    for w, n in url_weeks.items():
        if n > 2:
            errors.append(f"{w + 1}週目: URLが{n}回")
    over = {k: v for k, v in uses.items() if v >= 3}
    if over:
        errors.append(f"同じ品が3回以上: {over}")
    if start == START and len(posts) != DAYS * 5:
        errors.append(f"件数が {len(posts)}")
    return errors


def summary(posts, notes):
    by_day = collections.Counter(p["scheduled_at"][:10] for p in posts)
    by_kind = collections.Counter(p["kind"] for p in posts)
    urls = [p["scheduled_at"][:10] for p in posts if "http" in p["text"]]
    uses = collections.Counter(r for p in posts for r in p["recipe_ids"])
    print(OUT)
    print("日ごと:", dict(by_day))
    print("型ごと:", dict(by_kind))
    print("URLを入れた日:", urls)
    print("品の数:", len(uses), "／ 2回出る品:", sorted(k for k, v in uses.items() if v == 2))
    print("最長:", max(len(p["text"]) for p in posts), "文字")
    for n in notes:
        print("メモ:", n)


if __name__ == "__main__":
    main()
