#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""题面内输入生成器（固定 seed，确定性，零外网）。

**范围逐字来自 site/data/problems/<PID>.json 的题面存档，不凭记忆。**
纪律：题面外的输入一律作废。每道题给机读 RANGE + in_range()，
verify_std.py 用它核对每个用例；题面样例单独固定入表。

实测修正（2026-11-28 对照洛谷题面页逐字摘录）：
  · P1001 范围是 ∣a∣,∣b∣≤10^9，不是 32 位 int 全范围（旧版生成了题面外输入）
  · P1421 是「小玉买文具」不是「买铅笔」；样例 10 3 → 5
  · P1002 题面只保证「起点不是马的控制点」，并未保证终点不是
    （旧版把马在终点等合法输入误排除，属过度收窄）
"""
import random

# 机读范围：与题面存档「说明提示」逐字对应
RANGE = {
    "P1001": {"keys": ["a", "b"], "lo": -10**9, "hi": 10**9,
              "引用": "∣a∣,∣b∣≤10^9"},
    "P1421": {"keys": ["a", "b"], "a": (0, 10**4), "b": (0, 9),
              "引用": "0≤a≤10^4,0≤b≤9"},
    "P1002": {"n": (1, 20), "m": (1, 20), "horse": (0, 20),
              "保证": "起点不是马的控制点",
              "引用": "1≤n,m≤20,0≤ 马的坐标 ≤20"},
}
MOVES = [(1, 2), (1, -2), (2, 1), (2, -1),
         (-1, 2), (-1, -2), (-2, 1), (-2, -1)]

SPEC = {
    "P1001": {"count": 60, "bounds": "∣a∣,∣b∣≤10^9"},
    "P1421": {"count": 80, "bounds": "0≤a≤10^4,0≤b≤9"},
    "P1002": {"count": 40, "bounds": "1≤n,m≤20,0≤马的坐标≤20；保证起点不是马的控制点"},
}


def in_range(pid, line):
    """机读：该输入是否落在题面存档的范围内。"""
    try:
        v = [int(x) for x in line.split()]
    except Exception:
        return False
    if pid == "P1001":
        return len(v) == 2 and all(-10**9 <= x <= 10**9 for x in v)
    if pid == "P1421":
        return len(v) == 2 and 0 <= v[0] <= 10**4 and 0 <= v[1] <= 9
    if pid == "P1002":
        if len(v) != 4: return False
        n, m, x, y = v
        if not (1 <= n <= 20 and 1 <= m <= 20): return False
        if not (0 <= x <= 20 and 0 <= y <= 20): return False
        # 题面保证：起点 (0,0) 不是马的控制点（马本身 + 8 个落点都不许覆盖起点）
        if (x, y) == (0, 0): return False
        return not any((x + dx, y + dy) == (0, 0) for dx, dy in MOVES)
    return False


def samples(pid):
    """题面存档里的样例（逐字），供 verify 实测。"""
    import json, os
    fp = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))), "site", "data", "problems", pid + ".json")
    if not os.path.exists(fp): return []
    d = json.load(open(fp, encoding="utf-8"))
    out = []
    for s in d["题面"].get("样例", []):
        if isinstance(s, list) and len(s) >= 2:
            out.append((str(s[0]).strip() + "\n", str(s[1]).strip() + "\n"))
    return out


def cases(pid, seed=0):
    r = random.Random(20261128 + seed * 7919)
    spec = SPEC.get(pid)
    if not spec:
        raise KeyError("未登记的题目: " + pid)
    out = []
    # 题面样例永远排在最前（这是「保证做的是对的」的第一道证据）
    for inp, _ in samples(pid):
        out.append(inp)
    if pid == "P1001":
        # 边界点也在题面范围内（±1e9）
        fixed = [(0, 0), (1, -1), (10**9, 10**9), (-10**9, 0),
                 (10**9, -10**9), (-10**9, -10**9)]
        out += ["%d %d\n" % ab for ab in fixed]
        while len(out) < spec["count"]:
            a = r.choice([r.randint(-10**9, 10**9), r.randint(-100, 100), 0])
            b = r.choice([r.randint(-10**9, 10**9), r.randint(-100, 100), 0])
            out.append("%d %d\n" % (a, b))
    elif pid == "P1421":
        # 19 角整数倍边界（第 7 批 double 版在此少买一支）
        for a, b in [(7, 6), (19, 0), (0, 9), (1, 9), (3, 8), (10000, 9), (9999, 0)]:
            out.append("%d %d\n" % (a, b))
        while len(out) < spec["count"]:
            out.append("%d %d\n" % (r.randint(0, 10000), r.randint(0, 9)))
    elif pid == "P1002":
        # 官方样例已由 samples() 置顶；再补题面内的一般值
        out += ["1 1 5 5\n", "20 20 10 10\n", "2 2 5 5\n"]
        while len(out) < spec["count"]:
            n, m = r.randint(1, 20), r.randint(1, 20)
            x, y = r.randint(0, 20), r.randint(0, 20)
            line = "%d %d %d %d\n" % (n, m, x, y)
            if not in_range(pid, line): continue   # 只作废违反题面保证的
            out.append(line)
    assert all(in_range(pid, x) for x in out), "生成器产出了题面外输入"
    return out[:spec["count"]]


def known_hacks():
    """已知 hack 的期望输出（来自甲类反例，用 std 复算，不引用不存在的官方数据）。"""
    return {
        "P1421": [("7 6\n", "4\n"), ("19 0\n", "10\n")],
        "P1002": [("6 6 3 3\n", "6\n")],
        "P1001": [("0 0\n", "0\n"), ("1 -1\n", "0\n")],
    }


if __name__ == "__main__":
    import sys
    pid = sys.argv[1] if len(sys.argv) > 1 else "P1001"
    cs = cases(pid)
    print(pid, "用例", len(cs), "样例:", repr(cs[0]), "| 全部在题面内:",
          all(in_range(pid, x) for x in cs))
