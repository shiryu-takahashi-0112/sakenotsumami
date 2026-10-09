"""v2（テンポを上げて長くした動画の型）で使う部品。make_reel_v2.py・make_list_reel_v2.py から使う。

レシピのデータ（recipes.js）に無いことは書かない。
- 「ポイント」の1行：レシピに tips の欄が無いので、作り方の文の後ろの部分（「、」で区切った最後の1つ以上）を
  そのまま使う。火加減・時間・「〜まで」など、失敗しやすい所を言っている部分を優先する（point_line）。
- 「主な材料」：材料の上から順に、水・塩・油・醤油などの調味料を除いた3つ（key_ings）。
"""
import re

# 「ポイント」として選ぶときに重く見る言い回し（作り方の文にそのまま出てくるもの）
POINT_WORDS = [
    (r"まで", 3),
    (r"\d+(?:〜\d+)?(?:分|秒)", 2),
    (r"中火|弱火|強火|弱めの中火|\d+W", 2),
    (r"直前|しっかり|すっと|さっと|ふんわり|水気|ひと晩|粗熱", 2),
]
POINT_MAX = 30          # 1行で見せる長さの上限（文字）
# 主な材料から外す調味料など（3つ以上残るときだけ外す）
STAPLES = {"水", "塩", "こしょう", "塩こしょう", "砂糖", "醤油", "サラダ油", "ごま油", "オリーブオイル", "酒", "みりん", "酢"}


def _clauses(step):
    return [c for c in re.split(r"(?<=、)", step.strip()) if c]


def point_line(steps):
    """作り方の文から「ポイント」の1行を選ぶ。戻り値は (文, 何番目の手順か)。
    文は手順の後ろの部分をそのまま（文末の「。」は取る）。"""
    best = None
    for k, step in enumerate(steps):
        for s in [x + "。" for x in step.split("。") if x.strip()]:   # 1文ずつ（文をまたがない）
            cs = _clauses(s)
            for i in range(len(cs)):
                text = "".join(cs[i:]).rstrip("。")
                if len(text) > POINT_MAX:
                    continue
                score = sum(w for pat, w in POINT_WORDS if re.search(pat, text))
                key = (score, -len(text))
                if best is None or key > best[0]:
                    best = (key, text, k)
    if best is None:                       # どの手順も長いときは、いちばん短い手順の最後の区切り
        k = min(range(len(steps)), key=lambda j: len(steps[j]))
        return _clauses(steps[k])[-1].rstrip("。"), k
    return best[1], best[2]


def clean_name(name):
    return re.sub(r"（.*?）", "", name).strip()


def key_ings(ing, n=3):
    names = [clean_name(x[0]) for x in ing]
    main = [x for x in names if x not in STAPLES]
    return (main if len(main) >= n else names)[:n]


def beats(text):
    """文を2拍に分ける（最初の「、」の後ろ。無ければ1拍）。"""
    t = text.strip()
    cs = [i for i, ch in enumerate(t) if ch == "、"]
    # 真ん中にいちばん近い「、」で分ける
    if not cs:
        return [t]
    i = min(cs, key=lambda j: abs(j - len(t) / 2))
    if i >= len(t) - 2:
        return [t]
    return [t[:i + 1], t[i + 1:]]


NOTICE_PREFIXES = ("※写真はAIで作ったイメージです", "お酒は20歳になってから")


def strip_notices(text):
    """キャプションから「※写真はAIで…」「お酒は20歳に…」の行を外す（2026-10-07・Shiryuの指示で今後は付けない）。
    外したあとに空行が2つ以上続く所は1つにまとめる。それ以外は変えない。"""
    lines = [x for x in text.split("\n") if not x.strip().startswith(NOTICE_PREFIXES)]
    out = []
    for x in lines:
        if x.strip() == "" and out and out[-1].strip() == "":
            continue
        out.append(x)
    return "\n".join(out)


# ---- 冒頭のフック（2026-10-09・Shiryuの決定：最初の3秒で離脱させない）
HOOK_MAX = 14      # フックの1行（文字）
SUB_MAX = 16       # 下の小さい1行（文字）


def find_hook(hooks_file, folder):
    """フックの一覧（JSON：[{post_id,date,folder,type,hook,sub}, …]）から、フォルダ名が一致するものを返す。無ければ None。
    folder はフォルダ名でもパスでもよい（最後の名前で比べる）。一覧は {"items": [...]} の形でもよい。"""
    import json
    import pathlib
    data = json.loads(pathlib.Path(hooks_file).expanduser().read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("items") or data.get("hooks") or list(data.values())
    name = pathlib.Path(str(folder)).name
    for x in data:
        if isinstance(x, dict) and pathlib.Path(str(x.get("folder", ""))).name == name:
            return x
    return None


def hook_data(hook=None, sub=None, hooks_file=None, folders=()):
    """--hook / --sub / --hooks-file から {"hook","sub"} を作る。どれも無ければ None（従来の v2 のつかみ）。
    --hook を直接指定したときはそちらを優先する。長さが決まりを超えたら止める。"""
    import sys
    if not hook and hooks_file:
        for f in folders:
            x = find_hook(hooks_file, f)
            if x:
                hook, sub = x.get("hook"), sub or x.get("sub")
                break
        else:
            sys.exit(f"フックの一覧にこのフォルダがありません: {', '.join(map(str, folders))}（{hooks_file}）")
    if not hook:
        if sub:
            sys.exit("--sub だけでは作れません。--hook も指定してください")
        return None
    hook, sub = hook.strip(), (sub or "").strip()
    if "\n" in hook or len(hook) > HOOK_MAX:
        sys.exit(f"フックは1行・{HOOK_MAX}文字以内にしてください（{len(hook)}文字: {hook}）")
    if "\n" in sub or len(sub) > SUB_MAX:
        sys.exit(f"下の1行は1行・{SUB_MAX}文字以内にしてください（{len(sub)}文字: {sub}）")
    return {"hook": hook, "sub": sub}


def hook_caption(text, hook, replace_first=False):
    """キャプションの1行目をフックにする。既定では、フックを1行目に足し、元の行はすべてそのまま残す。
    replace_first=True なら元の1行目をフックに置き換える（2行目以降はそのまま）。
    1行目がすでにフックなら何もしない。"""
    lines = text.split("\n")
    if lines and lines[0].strip() == hook:
        return text
    return "\n".join([hook] + (lines[1:] if replace_first else lines))
