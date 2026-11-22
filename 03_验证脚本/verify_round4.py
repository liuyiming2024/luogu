#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 1 批定稿验证：修正独立正确解，产出最终结论数据"""
import os, json, subprocess, random
from math import gcd
from functools import lru_cache

BUILD = "/data/workspace/luogu_hack/build"
OUT = {}

def run(exe, inp, timeout=20):
    p = subprocess.run([exe], input=inp, capture_output=True, text=True, timeout=timeout)
    return p.stdout.strip(), p.returncode

# ================================================= P5179：穷举最小分母（独立正确解）
def brute_min(a, b, c, d, QMAX=200000):
    for q in range(1, QMAX + 1):
        lo = (a * q) // b + 1
        hi = (c * q - 1) // d
        if lo <= hi:
            for p in range(lo, min(hi, lo + 50) + 1):
                if gcd(p, q) == 1:
                    return f"{p}/{q}"
    return None

def legal_output(s, a, b, c, d):
    """仅验证输出本身是否为落在区间内的最简分数"""
    try:
        p, q = map(int, s.split("/"))
    except Exception:
        return False
    return q > 0 and gcd(p, q) == 1 and p * b > a * q and p * d < c * q

exe = os.path.join(BUILD, "P5179_siyuan")
rnd = random.Random(20261120)
legal = [(1, 2, 2, 3), (0, 1, 1, 3), (1, 3, 1, 2), (7, 8, 8, 9), (1, 1, 3, 2)]
for _ in range(300):
    b = rnd.randint(1, 40); d = rnd.randint(1, 40)
    a = rnd.randint(0, 40); c = rnd.randint(1, 40)
    if a * d < c * b:
        legal.append((a, b, c, d))
big = [(10**9, 10**9 - 1, 10**9, 10**9 - 2),
       (10**9 - 1, 10**9, 10**9, 10**9 - 1),
       (1, 10**9, 2, 10**9),
       (10**18, 10**18 + 1, 10**18 + 1, 10**18 + 2)]
bad, checked_small, big_legal = [], 0, []
for (a, b, c, d) in legal + big:
    out, rc = run(exe, f"{a} {b} {c} {d}\n")
    if (a, b, c, d) in big:
        big_legal.append({"input": f"{a} {b} {c} {d}", "actual": out,
                          "valid": legal_output(out, a, b, c, d)})
        continue
    exp = brute_min(a, b, c, d)
    checked_small += 1
    if exp is not None and out != exp:
        bad.append({"input": f"{a} {b} {c} {d}", "expected": exp, "actual": out})
OUT["P5179_siyuan"] = {"small_legal_tested": checked_small,
                       "small_mismatch_count": len(bad), "small_cases": bad[:12],
                       "big_cases": big_legal}

# ================================================= P1220：独立记忆化暴力 + 条件性反例
def brute1220(pos, w, c):
    n = len(pos) - 1
    S = sum(w[1:n + 1])
    INF = 10 ** 30
    @lru_cache(None)
    def go(i, j, side, rem):
        if i == 1 and j == n:
            return 0
        cur = pos[i] if side == 0 else pos[j]
        best = INF
        if i > 1:
            best = min(best, (cur - pos[i - 1]) * rem + go(i - 1, j, 0, rem - w[i - 1]))
        if j < n:
            best = min(best, (pos[j + 1] - cur) * rem + go(i, j + 1, 1, rem - w[j + 1]))
        return best
    return go(c, c, 0, S - w[c])

exe = os.path.join(BUILD, "P1220_uezud59i")
def p1220_dp(pos, w, c):
    n = len(pos) - 1
    S = sum(w[1:n + 1])
    pre = [0] * (n + 1)
    for i in range(1, n + 1):
        pre[i] = pre[i - 1] + w[i]
    INF = 10 ** 30
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

xs = [0, 1000000, 2000000, 3000000, 4000000]
ws = [100] * 5
s = "5 3\n0 100\n1000000 100\n2000000 100\n3000000 100\n4000000 100\n"
pos = [0] + xs[1:]; w = [0] + ws
exp_brute = brute1220(pos, w, 3)
exp_dp = p1220_dp(pos, w, 3)
out, rc = run(exe, s)
OUT["P1220_uezud59i"] = {
    "input": s.strip(),
    "brute_expected": exp_brute,
    "dp_expected": exp_dp,
    "actual": out,
    "note": "刻意突破题面 a_i<=100 约束，用于暴露 minn=1e9 硬编码上界，不计为合法 hack"
}

# 顺带核对官方样例
sample = "5 3\n2 10\n3 20\n5 20\n6 30\n8 10\n"
OUT["P1220_uezud59i"]["sample"] = {"input": sample.strip(),
                                   "actual": run(exe, sample)[0],
                                   "expected": brute1220([0, 2, 3, 5, 6, 8],
                                                          [0, 10, 20, 20, 30, 10], 3)}

with open(os.path.join(BUILD, "final.json"), "w", encoding="utf-8") as f:
    json.dump(OUT, f, ensure_ascii=False, indent=2)
print(json.dumps(OUT, ensure_ascii=False, indent=2))
