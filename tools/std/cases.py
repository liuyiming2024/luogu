#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""题面内输入生成器（固定 seed，确定性，零外网）。

纪律：题面外的输入一律作废。每道题显式给上界/下界；
已知 hack 边界点（P1421 的 19 角整数倍、P1002 官方样例）单独固定入表。
"""
import random

SPEC = {
    "P1001": {"count": 60, "bounds": "a,b 为 32 位有符号整数"},
    "P1421": {"count": 80, "bounds": "0<=a<=10000, 0<=b<=9"},
    "P1002": {"count": 40, "bounds": "1<=n,m<=20, 0<=x,y<=20，起点/终点不被马控制"},
}


def cases(pid, seed=0):
    r = random.Random(20261128 + seed * 7919)
    spec = SPEC.get(pid)
    if not spec:
        raise KeyError("未登记的题目: " + pid)
    out = []
    if pid == "P1001":
        fixed = [(0, 0), (1, -1), (2147483647, 0), (-2147483648, 0),
                 (2147483647, 2147483647), (-2147483648, -2147483648)]
        out += ["%d %d\n" % ab for ab in fixed]
        while len(out) < spec["count"]:
            a = r.choice([r.randint(-2**31, 2**31-1), r.randint(-100, 100), 0])
            b = r.choice([r.randint(-2**31, 2**31-1), r.randint(-100, 100), 0])
            out.append("%d %d\n" % (a, b))
    elif pid == "P1421":
        # 19 角整数倍边界（double 版在此少买一支）+ 一般值 + 题面上界
        for a, b in [(7, 6), (19, 0), (0, 0), (0, 9), (1, 9), (3, 8), (10000, 9), (9999, 0)]:
            out.append("%d %d\n" % (a, b))
        while len(out) < spec["count"]:
            a = r.randint(0, 10000); b = r.randint(0, 9)
            out.append("%d %d\n" % (a, b))
    elif pid == "P1002":
        moves = [(1, 2), (1, -2), (2, 1), (2, -1),
                 (-1, 2), (-1, -2), (-2, 1), (-2, -1)]
        # 固定用例都满足题面保证：起点/终点不在马位、也不被马位控制
        out += ["6 6 3 3\n", "1 1 5 5\n", "20 20 10 10\n", "2 2 5 5\n"]
        def violates(n, m, x, y):
            if (x, y) in ((0, 0), (n, m)): return True
            # 马自身在 (x,y)，其 8 个落点若覆盖起点或终点，则违反保证
            for dx, dy in moves:
                a, b = x + dx, y + dy
                if (a, b) in ((0, 0), (n, m)): return True
            return False
        while len(out) < spec["count"]:
            n, m = r.randint(1, 20), r.randint(1, 20)
            x, y = r.randint(0, 20), r.randint(0, 20)
            if violates(n, m, x, y): continue
            out.append("%d %d %d %d\n" % (n, m, x, y))
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
    print(pid, "用例", len(cs), "首条:", repr(cs[0]))
