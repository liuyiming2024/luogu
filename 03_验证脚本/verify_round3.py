#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 1 批补充验证 3：P5179 用独立二分求最小分母；P1220 记录硬编码上界的条件性反例"""
import os, json, subprocess
from math import gcd

BUILD = "/data/workspace/luogu_hack/build"
OUT = {}

def run(exe, inp, timeout=20):
    p = subprocess.run([exe], input=inp, capture_output=True, text=True, timeout=timeout)
    return p.stdout.strip(), p.returncode

# ------------------------------------------------- P5179 独立正确解
def best_fraction(a, b, c, d):
    def ok(q):
        return ((a * q) // b + 1) * d < c * q
    hi = 1
    while not ok(hi):
        hi *= 2
        if hi > 10 ** 30:
            return None
    lo, h = 1, hi
    while lo < h:
        mid = (lo + h) // 2
        if ok(mid):
            h = mid
        else:
            lo = mid + 1
    q = lo
    # 防 floor 抖动：向左右各扫几个取最小满足的 q
    for qq in range(max(1, q - 5), q + 1):
        if ok(qq):
            q = qq; break
    p = (a * q) // b + 1
    return f"{p}/{q}"

exe = os.path.join(BUILD, "P5179_siyuan")
import random
rnd = random.Random(20261120)
legal = [(1, 2, 2, 3), (0, 1, 1, 3), (1, 3, 1, 2), (7, 8, 8, 9), (1, 1, 3, 2)]
for _ in range(300):
    b = rnd.randint(1, 40); d = rnd.randint(1, 40)
    a = rnd.randint(0, 40); c = rnd.randint(1, 40)
    if a * d < c * b:
        legal.append((a, b, c, d))
legal += [(10**9, 10**9 - 1, 10**9, 10**9 - 2),
          (10**9 - 1, 10**9, 10**9, 10**9 - 1),
          (1, 10**9, 2, 10**9),
          (10**18, 10**18 + 1, 10**18 + 1, 10**18 + 2)]
bad = []
for (a, b, c, d) in legal:
    exp = best_fraction(a, b, c, d)
    out, rc = run(exe, f"{a} {b} {c} {d}\n")
    if out != exp:
        bad.append({"input": f"{a} {b} {c} {d}", "expected": exp, "actual": out})
OUT["P5179_siyuan"] = {"legal_tested": len(legal), "mismatch_count": len(bad), "cases": bad[:12]}

# ------------------------------------------------- P1220 硬编码上界：越界约束下的条件性反例
def p1220_correct(pos, w, c):
    n = len(pos) - 1
    S = sum(w[1:n + 1])
    pre = [0] * (n + 1)
    for i in range(1, n + 1):
        pre[i] = pre[i - 1] + w[i]
    INF = 10 ** 18
    f = [[[INF, INF] for _ in range(n + 2)] for _ in range(n + 2)]
    f[c][c][0] = f[c][c][1] = 0
    for length in range(2, n + 1):
        for i in range(1, n - length + 2):
            j = i + length - 1
            restL = S - (pre[j] - pre[i])
            f[i][j][0] = min(f[i + 1][j][0] + (pos[i + 1] - pos[i]) * restL,
                             f[i + 1][j][1] + (pos[j] - pos[i]) * restL)
            restR = S - (pre[j - 1] - pre[i - 1])
            f[i][j][1] = min(f[i][j - 1][0] + (pos[j] - pos[i]) * restR,
                             f[i][j - 1][1] + (pos[j] - pos[j - 1]) * restR)
    return min(f[1][n][0], f[1][n][1])

exe = os.path.join(BUILD, "P1220_uezud59i")
xs = [0, 1000000, 2000000, 3000000, 4000000]
ws = [100] * 5
s = "5 3\n0 100\n1000000 100\n2000000 100\n3000000 100\n4000000 100\n"
exp = p1220_correct([0] + xs[1:], [0] + ws, 3)
out, rc = run(exe, s)
OUT["P1220_uezud59i"] = {
    "input": s.strip(),
    "expected": exp,
    "actual": out,
    "note": "该输入刻意突破题面 a_i<=100 的约束，仅用于展示 minn=1e9 硬编码上界的缺陷，不计为合法 hack"
}

with open(os.path.join(BUILD, "results3.json"), "w", encoding="utf-8") as f:
    json.dump(OUT, f, ensure_ascii=False, indent=2)
print(json.dumps(OUT, ensure_ascii=False, indent=2))
