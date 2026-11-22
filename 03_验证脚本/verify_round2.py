#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 1 批补充验证：P5179 只测合法区间；P3959 用随机生成树采样寻找「更优合法解」"""
import os, json, random, subprocess, heapq
from fractions import Fraction
from math import gcd

BUILD = "/data/workspace/luogu_hack/build"
OUT = {}

def run(exe, inp, timeout=30):
    p = subprocess.run([exe], input=inp, capture_output=True, text=True, timeout=timeout)
    return p.stdout.strip(), p.stderr.strip()[:200], p.returncode

# ------------------------------------------------- P5179：只保留 a/b < c/d 的合法区间
def brute(a, b, c, d):
    for q in range(1, 20000):
        p = (a * q) // b + 1
        if p * d < c * q and gcd(p, q) == 1:
            return f"{p}/{q}"
    return "?"

exe = os.path.join(BUILD, "P5179_siyuan")
rnd = random.Random(20261120)
legal = [(1, 2, 2, 3), (0, 1, 1, 3), (1, 3, 1, 2), (7, 8, 8, 9), (1, 1, 3, 2)]
for _ in range(300):
    b = rnd.randint(1, 40); d = rnd.randint(1, 40)
    a = rnd.randint(0, 40); c = rnd.randint(1, 40)
    if a * d < c * b:
        legal.append((a, b, c, d))
# 大数（检验 long long 中间量 c - d*(a/b)）
big = [(10**9, 10**9 - 1, 10**9, 10**9 - 2),
       (10**9 - 1, 10**9, 10**9, 10**9 - 1),
       (1, 10**9, 2, 10**9),
       (10**18, 10**18 + 1, 10**18 + 1, 10**18 + 2)]
legal += big
bad = []
for (a, b, c, d) in legal:
    exp = brute(a, b, c, d)
    out, se, rc = run(exe, f"{a} {b} {c} {d}\n")
    if out != exp:
        bad.append({"input": f"{a} {b} {c} {d}", "expected": exp, "actual": out})
OUT["P5179_siyuan"] = {"legal_tested": len(legal), "mismatch_count": len(bad), "cases": bad[:12]}

# ------------------------------------------------- P3959：随机生成树采样找更优解
def tree_cost(n, tree, root):
    adj = [[] for _ in range(n + 1)]
    for u, v, w in tree:
        adj[u].append((v, w)); adj[v].append((u, w))
    dep = [0] * (n + 1); dep[root] = 1
    q = [root]; res = 0
    while q:
        u = q.pop(0)
        for v, w in adj[u]:
            if dep[v] == 0:
                dep[v] = dep[u] + 1
                res += w * dep[u]
                q.append(v)
    return res

def random_tree(n, edges, rnd):
    seq = [rnd.randint(1, n) for _ in range(n - 2)]
    deg = [1] * (n + 1)
    for x in seq:
        deg[x] += 1
    heap = [v for v in range(1, n + 1) if deg[v] == 1]
    heapq.heapify(heap)
    tree = []
    for x in seq:
        if not heap:
            return None
        leaf = heapq.heappop(heap)
        deg[leaf] = 0; deg[x] -= 1
        if deg[x] == 1:
            heapq.heappush(heap, x)
        key = (min(leaf, x), max(leaf, x))
        if key not in edges:
            return None
        tree.append((leaf, x, edges[key]))
    rem = [v for v in range(1, n + 1) if deg[v] == 1]
    if len(rem) != 2:
        return None
    key = (min(rem[0], rem[1]), max(rem[0], rem[1]))
    if key not in edges:
        return None
    tree.append((rem[0], rem[1], edges[key]))
    return tree

exe = os.path.join(BUILD, "P3959_l6u32sp7")
found = None
tried = 0
for sd in range(40):
    rnd = random.Random(sd + 33000)
    n = rnd.choice([8, 9, 10])
    perm = list(range(1, n + 1)); rnd.shuffle(perm)
    ed = {}
    for i in range(1, n):
        u, v = perm[i], perm[rnd.randint(0, i - 1)]
        key = (min(u, v), max(u, v))
        ed[key] = rnd.randint(1, 100)
    for _ in range(rnd.randint(n, n * 2)):
        u, v = rnd.sample(range(1, n + 1), 2)
        key = (min(u, v), max(u, v))
        if key not in ed:
            ed[key] = rnd.randint(1, 100)
    lines = [f"{n} {len(ed)}"]
    for (u, v), w in ed.items():
        lines.append(f"{u} {v} {w}")
    inp = "\n".join(lines) + "\n"
    out, se, rc = run(exe, inp, timeout=40)
    try:
        actual = int(out)
    except Exception:
        continue
    tried += 1
    # 随机采样生成树，找比题解输出更小的合法解
    best, besttree, bestroot = actual, None, None
    for _ in range(12000):
        t = random_tree(n, ed, rnd)
        if t is None:
            continue
        for r in range(1, n + 1):
            c = tree_cost(n, t, r)
            if c < best:
                best, besttree, bestroot = c, t, r
        if best < actual:
            break
    if best < actual:
        found = {"input": inp.strip(), "n": n, "seed": sd + 33000,
                 "solution_output": actual, "better_cost": best,
                 "better_tree": sorted((min(u, v), max(u, v), w) for u, v, w in besttree),
                 "root": bestroot}
        break

OUT["P3959_l6u32sp7"] = {"graphs_tried": tried, "found": found}

with open(os.path.join(BUILD, "results2.json"), "w", encoding="utf-8") as f:
    json.dump(OUT, f, ensure_ascii=False, indent=2)
print(json.dumps(OUT, ensure_ascii=False, indent=2))
