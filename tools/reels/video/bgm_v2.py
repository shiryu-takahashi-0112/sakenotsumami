#!/usr/bin/env python3
"""サケノツマミのリール v2 用BGM（2026-10-09〜）。テンポの速い編集に合わせた、明るく軽い曲を波形から作る。

  python3 video/bgm_v2.py --dur 22.1 --marks 1.8,4.9,7.3 --accents 0,1.95,2.15 --out work/x/bgm.wav

2026-10-09：Shiryuの指摘「画面の切り替わりなどはスピーディーなのに、音楽がゆったりしている」で作った。
旧版 video/bgm.py（88BPMのゆるいジャズ風）は旧版の動画（make_reel.py・make_list_reel.py）用に残す。

- 外部の音源は使わず、すべてここで波形から作る（著作権・ライセンスの確認が要らない）。
- 曲調：120〜128BPM、キッチンで流れていそうな軽いハウス寄りのポップ。
  4つ打ちの軽いキック、2・4拍のクラップ、16分のハイハット、弾むベース、裏拍の明るい和音、マリンバ風の分散和音。
  和音は Fmaj7 → Dm7 → B♭maj7 → C（1小節ずつ）。
- テンポは、動画の長さがちょうど小節の切れ目（無理なら2拍の切れ目）で終わるように 120〜128 の中から選ぶ。
  最後で曲が切れても、動画の頭（0秒の1拍目）につながる。
- --marks（場面の切り替え）には「シュッ」と入る音＋短いヒット、--accents（文字が出る時刻）には短い「ポン」を置く。
  0秒（フックの最初のコマ）にもヒットを置く。
- 音は0秒から鳴らす（頭のフェードは5ms）。お尻は30msで切る。
- 音量は平均 -21dB（ffmpeg の volumedetect の mean_volume）にそろえ、最大は -2dBFS 以下に抑える。
"""
import argparse
import array
import math
import random
import wave

SR = 44100
ap = argparse.ArgumentParser()
ap.add_argument("--dur", type=float, default=22.0)
ap.add_argument("--marks", default="", help="場面の切り替えの時刻（秒、カンマ区切り）")
ap.add_argument("--accents", default="", help="文字が出る時刻（秒、カンマ区切り）")
ap.add_argument("--out", default="bgm.wav")
ap.add_argument("--bpm", type=float, help="指定しなければ 120〜128 から選ぶ")
ap.add_argument("--mean-db", type=float, default=-21.0, help="平均の音量（dBFS）")
ap.add_argument("--peak-db", type=float, default=-2.0, help="最大の音量（dBFS）")
args = ap.parse_args()

DUR = args.dur
N = int(round(SR * DUR))


def pick_bpm(dur):
    """動画の長さが小節（4拍）の切れ目で終わるテンポを 120〜128 から探す。無ければ2拍の切れ目。それも無ければ124。"""
    for unit in (4, 2):
        best = None
        for beats in range(1, 200):
            if beats % unit:
                continue
            bpm = beats * 60 / dur
            if 120 <= bpm <= 128:
                key = abs(bpm - 124)
                if best is None or key < best[0]:
                    best = (key, bpm, unit)
        if best:
            return best[1], best[2]
    return 124.0, 0


if args.bpm:
    BPM, UNIT = args.bpm, 0
else:
    BPM, UNIT = pick_bpm(DUR)
BEAT = 60 / BPM
BAR = BEAT * 4
S16 = BEAT / 4

L = array.array("d", bytes(8 * N))
R = array.array("d", bytes(8 * N))


def add(t0, samples, gain=1.0, pan=0.0):
    i0 = int(round(t0 * SR))
    gl = gain * math.cos((pan + 1) * math.pi / 4)
    gr = gain * math.sin((pan + 1) * math.pi / 4)
    j0 = max(0, -i0)
    end = min(N, i0 + len(samples))
    for i in range(max(0, i0), end):
        v = samples[i - i0]
        L[i] += v * gl
        R[i] += v * gr
    return j0


_cache = {}


def cached(fn):
    def w(*a):
        k = (fn.__name__,) + a
        if k not in _cache:
            _cache[k] = fn(*a)
        return _cache[k]
    return w


def env_ad(t, a, d):
    return min(1.0, t / a) * math.exp(-t * d)


@cached
def kick():
    n = int(0.22 * SR)
    out, ph = [], 0.0
    for k in range(n):
        t = k / SR
        ph += 2 * math.pi * (52 + 110 * math.exp(-t * 40)) / SR
        out.append(math.sin(ph) * env_ad(t, 0.001, 16) + 0.25 * math.sin(ph * 2) * math.exp(-t * 60))
    return out


@cached
def noise(dur, seed):
    rnd = random.Random(seed)
    return [rnd.uniform(-1, 1) for _ in range(int(dur * SR))]


@cached
def clap():
    """手拍子風：ずらした3回のノイズ＋短い残り。"""
    nz = noise(0.25, 7)
    out = [0.0] * len(nz)
    prev = 0.0
    for k in range(len(nz)):
        t = k / SR
        e = 0.0
        for off in (0.0, 0.011, 0.023):
            if t >= off:
                e += math.exp(-(t - off) * 120) * 0.6
        e += math.exp(-t * 22) * 0.35 * (t >= 0.023)
        hp = nz[k] - prev * 0.6        # 低いところを少し削る
        prev = nz[k]
        out[k] = hp * e
    return out


@cached
def hat(open_):
    nz = noise(0.18 if open_ else 0.05, 11 + open_)
    out, prev = [], 0.0
    for k in range(len(nz)):
        t = k / SR
        hp = nz[k] - prev
        prev = nz[k]
        out.append(hp * env_ad(t, 0.0008, 18 if open_ else 90))
    return out


@cached
def pluck(freq, dur, bright):
    """裏拍の明るい和音用（短く切れる、少しきらっとした音）。"""
    n = int(dur * SR)
    out = []
    for k in range(n):
        t = k / SR
        x = 2 * math.pi * freq * t
        v = math.sin(x) + 0.35 * math.sin(2 * x) * math.exp(-t * 18) + bright * 0.2 * math.sin(3 * x) * math.exp(-t * 30)
        out.append(v * env_ad(t, 0.003, 9) * min(1.0, (dur - t) / 0.02))
    return out


@cached
def marimba(freq):
    n = int(0.35 * SR)
    out = []
    for k in range(n):
        t = k / SR
        x = 2 * math.pi * freq * t
        out.append((math.sin(x) * math.exp(-t * 10) + 0.4 * math.sin(4 * x) * math.exp(-t * 40)) * min(1.0, t / 0.001))
    return out


@cached
def bass(freq, dur):
    n = int(dur * SR)
    out = []
    for k in range(n):
        t = k / SR
        x = 2 * math.pi * freq * t
        v = math.sin(x) + 0.35 * math.sin(2 * x) + 0.12 * math.sin(3 * x)
        out.append(v * env_ad(t, 0.004, 5) * min(1.0, (dur - t) / 0.015))
    return out


@cached
def whoosh(length):
    """切り替えの直前に「シュッ」と上がっていく音（ノイズを、だんだん高い所だけ通す）。最後の点が切り替えの時刻。"""
    nz = noise(length, 23)
    out, lp = [], 0.0
    n = len(nz)
    for k in range(n):
        p = k / n
        a = 0.04 + 0.5 * p * p                # 進むほど高い音まで通す
        lp += a * (nz[k] - lp)
        out.append((nz[k] - lp) * 0.5 * (p ** 2.2) + lp * 0.6 * (p ** 2))
    return out


@cached
def hit():
    """切り替えの瞬間の短いヒット（低い「ドン」＋明るいきらめき）。"""
    n = int(0.4 * SR)
    out, ph = [], 0.0
    nz = noise(0.4, 31)
    for k in range(n):
        t = k / SR
        ph += 2 * math.pi * (60 + 140 * math.exp(-t * 35)) / SR
        v = math.sin(ph) * env_ad(t, 0.001, 11) * 0.9
        v += nz[k] * math.exp(-t * 45) * 0.35
        v += math.sin(2 * math.pi * 1760 * t) * math.exp(-t * 14) * 0.18
        out.append(v)
    return out


@cached
def pop(freq):
    """文字が出たときの「ポン」（音程が少し下がる短い音）。"""
    n = int(0.09 * SR)
    out, ph = [], 0.0
    for k in range(n):
        t = k / SR
        ph += 2 * math.pi * freq * (1 + 0.6 * math.exp(-t * 90)) / SR
        out.append(math.sin(ph) * env_ad(t, 0.0015, 45))
    return out


# 和音（1小節ずつ）：Fmaj7 → Dm7 → B♭maj7 → C
CH = [
    (87.31, [349.23, 440.00, 523.25, 659.25]),
    (73.42, [349.23, 440.00, 523.25, 587.33]),
    (58.27, [349.23, 440.00, 587.33, 466.16]),
    (65.41, [392.00, 523.25, 659.25, 783.99]),
]
bars = int(DUR / BAR) + 1
for b in range(bars):
    t0 = b * BAR
    root, notes = CH[b % 4]
    for k in range(4):
        tb = t0 + k * BEAT
        add(tb, kick(), 0.55)                                   # 4つ打ち
        if k in (1, 3):
            add(tb, clap(), 0.30, 0.05)                         # 2・4拍
        for s in range(4):                                      # 16分のハイハット（裏を強めに）
            add(tb + s * S16, hat(s == 2 and k == 3), (0.10 if s == 2 else 0.05), 0.35)
        # ベース：8分で弾む（表は根音、裏はオクターブ上）
        add(tb, bass(root, BEAT * 0.42), 0.34)
        add(tb + BEAT / 2, bass(root * 2, BEAT * 0.35), 0.22)
        # 裏拍の和音（明るく短く）
        for j, f in enumerate(notes):
            add(tb + BEAT / 2 + j * 0.004, pluck(f, BEAT * 0.38, 1), 0.045, -0.3 + j * 0.2)
    # マリンバ風の分散和音（16分で上り下り、小節の後半だけ）
    arp = [notes[0] * 2, notes[1] * 2, notes[2] * 2, notes[3] * 2, notes[2] * 2, notes[1] * 2]
    for s, f in enumerate(arp):
        add(t0 + BEAT * 2 + s * S16 * 1.0, marimba(round(f, 2)), 0.07, 0.4 if s % 2 else -0.4)

# 場面の切り替え：シュッ（切り替えに向けて上がる）＋ヒット。0秒（フックの最初のコマ）にもヒット
marks = sorted({round(float(x), 3) for x in args.marks.split(",") if x.strip()})
WL = 0.22
for m in marks:
    if 0 < m < DUR - 0.05:
        w = whoosh(WL)
        add(m - WL, w, 0.22, 0.0)
        add(m, hit(), 0.42)
add(0.0, hit(), 0.42)

# 文字が出る時刻：ポン（切り替えから60ms以内のものは、切り替えの音に任せる）
acc = sorted({round(float(x), 3) for x in args.accents.split(",") if x.strip()})
notes_pop = [1046.5, 1174.66, 1318.51, 1567.98]
used = []
for i, a in enumerate(acc):
    if not (0 <= a < DUR - 0.05):
        continue
    if any(abs(a - m) < 0.06 for m in marks + [0.0]) and a > 0.0:
        continue
    if used and a - used[-1] < 0.06:
        continue
    used.append(a)
    add(a, pop(notes_pop[len(used) % len(notes_pop)]), 0.20, 0.25 if len(used) % 2 else -0.25)

# 仕上げ：やわらかく丸めて、頭5ms・お尻30msだけフェード、平均と最大をそろえる
def finish(gain):
    out_l = array.array("d", bytes(8 * N))
    out_r = array.array("d", bytes(8 * N))
    for i in range(N):
        t = i / SR
        g = min(1.0, t / 0.005) * min(1.0, (DUR - t) / 0.03)
        out_l[i] = math.tanh(L[i] * gain) * g
        out_r[i] = math.tanh(R[i] * gain) * g
    return out_l, out_r


def stats(a, b):
    s = sum(x * x for x in a) + sum(x * x for x in b)
    rms = math.sqrt(s / (2 * N))
    pk = max(max(abs(x) for x in a), max(abs(x) for x in b))
    return rms, pk


target_rms = 10 ** (args.mean_db / 20)
target_pk = 10 ** (args.peak_db / 20)
drive, scale = 1.0, 1.0
for _ in range(8):
    ol, orr = finish(drive)
    rms, pk = stats(ol, orr)
    scale = target_rms / rms
    if pk * scale <= target_pk:
        break
    drive *= 1.35        # 最大が超えるときは、丸めを強めて平均との差を縮める
ol, orr = finish(drive)
rms, pk = stats(ol, orr)
scale = min(target_rms / rms, target_pk / pk)
with wave.open(args.out, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(array.array("h", (int(v) for i in range(N) for v in (ol[i] * scale * 32767, orr[i] * scale * 32767))).tobytes())
print(f"{args.out} {DUR:.3f}秒 {BPM:.2f}BPM（{'小節' if UNIT == 4 else '2拍' if UNIT == 2 else '切れ目なし'}で終わる・{DUR / BEAT:.2f}拍）"
      f" 平均 {20 * math.log10(rms * scale):.1f}dB 最大 {20 * math.log10(pk * scale):.1f}dBFS"
      f" 切り替え {len([m for m in marks if 0 < m < DUR - 0.05]) + 1}か所 ポン {len(used)}か所")
