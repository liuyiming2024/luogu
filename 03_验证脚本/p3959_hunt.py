#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按用户口径重新找「合法 hack」：
  - 数据严格落在题面约束内
  - 不考虑评测机波动（不靠 TLE / 随机超时）
  - 存在确定性测试点使题解代码 WA / RE

本脚本专攻第 1 批遗留的 P3959 随机化贪心题解：
用 Prüfer 序列穷举全部生成树求精确最优，与题解输出比对。
P3959 约束：1<=n<=12, 0<=m<=1000, v<=5*10^5。
"""
import os, json, random, subprocess, itertools

BUILD = "/data/workspace/luogu_hack/build"
EXE = os.path.join(BUILD, "P3959_l6u32sp7")

def prufer_tree(n, seq):
    deg = [1] * (n + 1)
    for x in seq:
        deg[x] += 1
    edges = []
    s = list(seq)
    ptr = 0
    leaf = -1
    # 找最小叶子
    leaves = [v for v in range(1, n + 1) if deg[v] == 1]
    import heapq
    heapq.heapify(leaves)
    for x in s:
        leaf = heapq.heappop(leaves)
        edges.append((min(leaf, x), max(leaf, x)))
        deg[leaf] -= 1
        deg[x] -= 1
        if deg[x] == 1:
            heapq.heappush(leaves, x)
    rem = [v for v in range(1, n + 1) if deg[v] == 1]
    edges.append((min(rem[0], rem[1]), max(rem[0], rem[1])))
    return edges

def tree_cost(n, edges, ew, root):
    adj = [[] for _ in range(n + 1)]
    for u, v in edges:
        w = ew[(u, v)]
        adj[u].append((v, w)); adj[v].append((u, w))
    dep = [0] * (n + 1); dep[root] = 1
    q = [root]; res = 0; head = 0
    while head < len(q):
        u = q[head]; head += 1
        for v, w in adj[u]:
            if dep[v] == 0:
                dep[v] = dep[u] + 1
                res += w * dep[u]
                q.append(v)
    return res if len(q) == n else None

def exact_best(n, ew):
    best = None
    bestinfo = None
    for seq in itertools.product(range(1, n + 1), repeat=n - 2):
        edges = prufer_tree(n, seq)
        if any(e not in ew for e in edges):
            continue
        for r in range(1, n + 1):
            c = tree_cost(n, edges, ew, r)
            if c is not None and (best is None or c < best):
                best, bestinfo = c, (edges, r)
    return best, bestinfo

# 先用题面样例校验精确解
s1 = {(1, 2): 1, (1, 3): 3, (1, 4): 1, (2, 3): 4, (3, 4): 1}
s2 = {(1, 2): 1, (1, 3): 3, (1, 4): 1, (2, 3): 4, (3, 4): 2}
print("sanity sample1:", exact_best(4, s1)[0], "(expect 4)")
print("sanity sample2:", exact_best(4, s2)[0], "(expect 5)")

def run_solution(inp, timeout=40):
    p = subprocess.run([EXE], input=inp, capture_output=True, text=True, timeout=timeout)
    return p.stdout.strip(), p.returncode

found = []
tried = 0
for sd in range(1, 401):
    rnd = random.Random(sd * 7919)
    n = rnd.choice([5, 6])
    # 先随机一棵生成树保证连通
    perm = list(range(1, n + 1)); rnd.shuffle(perm)
    ew = {}
    for i in range(1, n):
        u, v = perm[i], perm[rnd.randint(0, i - 1)]
        ew[(min(u, v), max(u, v))] = rnd.randint(1, 30)
    # 加若干额外边
    for _ in range(rnd.randint(0, 6)):
        u, v = rnd.sample(range(1, n + 1), 2)
        key = (min(u, v), max(u, v))
        if key not in ew:
            ew[key] = rnd.randint(1, 30)
    lines = [f"{n} {len(ew)}"]
    for (u, v), w in ew.items():
        lines.append(f"{u} {v} {w}")
    inp = "\n".join(lines) + "\n"
    best, info = exact_best(n, ew)
    if best is None:
        continue
    out, rc = run_solution(inp)
    tried += 1
    try:
        actual = int(out)
    except Exception:
        actual = None
    if actual != best:
        found.append({
            "seed": sd * 7919, "input": inp.strip(),
            "n": n, "m": len(ew),
            "exact_optimal": best,
            "solution_output": out,
            "optimal_tree_edges": [(u, v, ew[(u, v)]) for u, v in info[0]],
            "optimal_root": info[1],
        })
        print("FOUND mismatch at seed", sd * 7919, "best", best, "out", out)
        if len(found) >= 5:
            break
    if sd % 50 == 0:
        print("... tried", tried, "found", len(found), flush=True)

with open(os.path.join(BUILD, "p3959_hunt.json"), "w", encoding="utf-8") as f:
    json.dump({"graphs_tried": tried, "found": found}, f, ensure_ascii=False, indent=2)
print(json.dumps({"graphs_tried": tried, "found": found}, ensure_ascii=False, indent=2))
