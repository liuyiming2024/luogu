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
    "P1909": {"n": (1, 10000), "pack": (1, 10000),
              "引用": "保证所有的 7 个数都是不超过 10000 的正整数"},
    "P1028": {"n": (1, 1000), "引用": "1≤n≤10^3"},
    "P1044": {"n": (1, 18), "引用": "1≤n≤18"},
    "P1059": {"N": (1, 100), "val": (1, 1000), "引用": "N≤100"},
    "P1003": {"n": (0, 10**4), "coord": (0, 10**5)},
    "P1024": {"root": (-100, 100)},
    "P1025": {"n": (7, 200), "k": (2, 6)},
    "P1029": {"x": (2, 10**5), "y": (2, 10**5)},
    "P1030": {"nodes": (1, 8)},
    "P1031": {"N": (1, 100), "Ai": (1, 10000)},
    "P1022": {}, "P1023": {}, "P1026": {}, "P1027": {}, "P1032": {},
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
    "P1909": {"count": 40, "bounds": "n 与 6 个包装数均为 1..10000 正整数"},
    "P1028": {"count": 40, "bounds": "1≤n≤1000"},
    "P1044": {"count": 40, "bounds": "1≤n≤18"},
    "P1059": {"count": 40, "bounds": "1≤N≤100，N 个数在 1..1000"},
    "P1003": {"count": 40}, "P1024": {"count": 40}, "P1025": {"count": 40},
    "P1029": {"count": 40}, "P1030": {"count": 40}, "P1031": {"count": 40},
    "P1022": {"count": 40}, "P1023": {"count": 40}, "P1026": {"count": 40},
    "P1027": {"count": 40}, "P1032": {"count": 40},
}


NEW_TEXT_PIDS = {"P1003","P1024","P1025","P1029","P1030","P1031",
                 "P1022","P1023","P1026","P1027","P1032"}


def _text_in_range(pid, line):
    """含多行/非纯数字结构的题：按题面逐字校验结构，不凭记忆。"""
    L = line.strip().splitlines()
    try:
        if pid == "P1003":
            if len(L) < 2: return False
            n = int(L[0].split()[0])
            if not (0 <= n <= 10**4 and len(L) == n + 2): return False
            for row in L[1:1+n]:
                v = list(map(int, row.split()))
                if len(v) != 4 or any(not (0 <= x <= 10**5) for x in v): return False
            v = list(map(int, L[-1].split()))
            return len(v) == 2 and all(0 <= x <= 10**5 for x in v)
        if pid == "P1024":
            if len(L) != 1: return False
            v = list(map(float, L[0].split()))
            return len(v) == 4 and v[0] != 0
        if pid == "P1025":
            if len(L) != 1: return False
            v = list(map(int, L[0].split()))
            return len(v) == 2 and 6 < v[0] <= 200 and 2 <= v[1] <= 6
        if pid == "P1029":
            if len(L) != 1: return False
            v = list(map(int, L[0].split()))
            return len(v) == 2 and all(2 <= x <= 10**5 for x in v)
        if pid == "P1030":
            return (len(L) == 2 and all(x.isalpha() and x.isupper() for x in L)
                    and 1 <= len(L[0]) <= 8 and len(L[0]) == len(L[1])
                    and set(L[0]) == set(L[1]))
        if pid == "P1031":
            if len(L) != 2: return False
            n = int(L[0].split()[0]); v = list(map(int, L[1].split()))
            return (1 <= n <= 100 and len(v) == n
                    and all(1 <= x <= 10000 for x in v) and sum(v) % n == 0)
        if pid == "P1022":
            if len(L) != 1: return False
            x = L[0]
            if x.count("=") != 1: return False
            a, b = x.split("=")
            if not a or not b: return False
            if any(not (ch.isdigit() or ch.islower() or ch in "+-=") for ch in x): return False
            return len(set(ch for ch in x if ch.islower())) == 1
        if pid == "P1023":
            if len(L) < 4: return False
            if len(L[0].split()) != 1 or len(L[1].split()) != 2: return False
            end = -1
            for i in range(2, len(L)-1):
                v = list(map(int, L[i].split()))
                if v == [-1, -1]: end = i; break
                if len(v) != 2 or any(not (0 <= x < 10**5) for x in v): return False
            if end < 0 or len(L[-1].split()) != 1: return False
            nums = [int(L[0].split()[0])] + list(map(int, L[1].split())) + [int(L[-1].split()[0])]
            return all(0 <= x < 10**5 for x in nums)
        if pid == "P1026":
            if len(L) < 3: return False
            p, k = map(int, L[0].split())
            if not (1 <= p <= 10 and 2 <= k <= 40 and len(L) >= 1+p+2): return False
            for row in L[1:1+p]:
                if len(row) != 20 or not row.isalpha() or not row.islower(): return False
            sd = int(L[1+p])
            if not (1 <= sd <= 6 and len(L) == 2+p+sd): return False
            return all(w.isalpha() and w.islower() and len(w) <= 20 for w in L[2+p:])
        if pid == "P1027":
            n = int(L[0].split()[0]); idx = 1
            if not (1 <= n <= 10): return False
            for _ in range(n):
                if idx >= len(L): return False
                S, t, A, B = map(int, L[idx].split()); idx += 1
                if not (1 <= S <= 100 and 0 <= t <= 500 and 1 <= A <= S and 1 <= B <= S): return False
                if idx + S > len(L): return False
                for row in L[idx:idx+S]:
                    v = list(map(int, row.split()))
                    if len(v) != 7 or any(not (0 <= x <= 500) for x in v): return False
                idx += S
            return idx == len(L)
        if pid == "P1032":
            if len(L) < 2 or len(L) > 8: return False
            for row in L:
                v = row.split()
                if len(v) != 2: return False
                if any(not (w.isalpha() and w.islower() and len(w) <= 20) for w in v): return False
            return True
    except Exception:
        return False
    return False


def in_range(pid, line):
    """机读：该输入是否落在题面存档的范围内。"""
    if pid in NEW_TEXT_PIDS:
        return _text_in_range(pid, line)
    try:
        v = [int(x) for x in line.split()]
    except Exception:
        return False
    if pid == "P1001":
        return len(v) == 2 and all(-10**9 <= x <= 10**9 for x in v)
    if pid == "P1421":
        return len(v) == 2 and 0 <= v[0] <= 10**4 and 0 <= v[1] <= 9
    if pid == "P1909":
        return len(v) == 7 and all(1 <= x <= 10000 for x in v)
    if pid == "P1028":
        return len(v) == 1 and 1 <= v[0] <= 1000
    if pid == "P1044":
        return len(v) == 1 and 1 <= v[0] <= 18
    if pid == "P1059":
        return (2 <= len(v) <= 101 and 1 <= v[0] <= 100
                and len(v) == 1 + v[0] and all(1 <= x <= 1000 for x in v[1:]))
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
    elif pid == "P1909":
        while len(out) < spec["count"]:
            n = r.randint(1, 10000)
            out.append("%d\n%d %d\n%d %d\n%d %d\n" % (
                n, r.randint(1,10000), r.randint(1,10000),
                r.randint(1,10000), r.randint(1,10000),
                r.randint(1,10000), r.randint(1,10000)))
    elif pid == "P1028":
        for n in [1, 2, 3, 4, 5, 6, 10, 100, 1000]:
            out.append("%d\n" % n)
        while len(out) < spec["count"]:
            out.append("%d\n" % r.randint(1, 1000))
    elif pid == "P1044":
        for n in range(1, 19): out.append("%d\n" % n)
        while len(out) < spec["count"]:
            out.append("%d\n" % r.randint(1, 18))
    elif pid == "P1059":
        while len(out) < spec["count"]:
            N = r.randint(1, 100)
            out.append("%d\n%s\n" % (N, " ".join(str(r.randint(1,1000)) for _ in range(N))))
    elif pid == "P1003":
        while len(out) < spec["count"]:
            n = r.randint(1, 8); rows = []
            for _ in range(n):
                a, b = r.randint(0, 30), r.randint(0, 30)
                g, k = r.randint(0, 30), r.randint(0, 30)
                rows.append("%d %d %d %d" % (a, b, g, k))
            out.append("%d\n%s\n%d %d\n" % (n, "\n".join(rows), r.randint(0, 64), r.randint(0, 64)))
    elif pid == "P1024":
        while len(out) < spec["count"]:
            rs = sorted(r.sample(range(-100, 101), 3))
            if min(rs[1]-rs[0], rs[2]-rs[1]) < 1: continue
            r1, r2, r3 = rs
            out.append("1 %d %d %d\n" % (-(r1+r2+r3), r1*r2+r1*r3+r2*r3, -r1*r2*r3))
    elif pid == "P1025":
        for n in [7, 8, 9, 10, 12, 15, 20, 25, 30]:
            out.append("%d %d\n" % (n, r.randint(2, 6)))
        while len(out) < spec["count"]:
            out.append("%d %d\n" % (r.randint(7, 200), r.randint(2, 6)))
    elif pid == "P1029":
        primes = [2, 3, 5, 7, 11, 13]
        while len(out) < spec["count"]:
            x = r.randint(2, 300); m = 1
            for q in primes:
                if r.random() < 0.45: m *= q
            y = x*m
            if not (2 <= y <= 10**5): continue
            if r.random() < 0.2: y = r.randint(2, 2000)
            out.append("%d %d\n" % (x, y))
    elif pid == "P1030":
        import string as _st
        def _tree(seq):
            if not seq: return None
            m = r.randrange(len(seq))
            return (seq[0], _tree(seq[1:1+m]), _tree(seq[1+m:]))
        def _ino(t): return "" if t is None else _ino(t[1])+t[0]+_ino(t[2])
        def _post(t): return "" if t is None else _post(t[1])+_post(t[2])+t[0]
        while len(out) < spec["count"]:
            n = r.randint(1, 8); seq = r.sample(list(_st.ascii_uppercase), n); t = _tree(seq)
            out.append(_ino(t)+"\n"+_post(t)+"\n")
    elif pid == "P1031":
        for _ in range(14):
            n = r.randint(1, 4); avg = r.randint(1, 3); v = [1]*n
            for _ in range(n*avg-n): v[r.randrange(n)] += 1
            out.append("%d\n%s\n" % (n, " ".join(map(str, v))))
        while len(out) < spec["count"]:
            n = r.randint(5, 100); avg = r.randint(1, 50); v = [1]*n
            for _ in range(n*avg-n): v[r.randrange(n)] += 1
            out.append("%d\n%s\n" % (n, " ".join(map(str, v))))
    elif pid == "P1022":
        import string as _st
        while len(out) < spec["count"]:
            var = r.choice(_st.ascii_lowercase); q = r.randint(-40, 40)
            Ac = r.randint(1, 6); Cc = Ac + 4
            B = r.randint(-20, 20); D = B + q
            L = "%d%s%+d" % (Ac, var, B); Rr = "%d%s%+d" % (Cc, var, D)
            if r.random() < 0.3:
                L = "%+d%+d%s" % (B, Ac, var); Rr = "%+d%+d%s" % (D, Cc, var)
            out.append(L+"="+Rr+"\n")
    elif pid == "P1023":
        while len(out) < spec["count"]:
            C = r.randint(10, 40); V0 = r.randint(90, 150)
            prices = sorted(r.sample(range(C+1, C+10), r.randint(2, 4)))
            vol = V0; rows = []
            for p in prices:
                vol -= r.randint(1, 12)
                if vol < 1: vol = 1
                rows.append("%d %d" % (p, vol))
            E = r.choice(prices); d = r.randint(5, 20)
            out.append("%d\n%d %d\n%s\n-1 -1\n%d\n" % (E, C, V0, "\n".join(rows), d))
    elif pid == "P1026":
        import string as _st
        while len(out) < spec["count"]:
            k = r.randint(2, 3) if len(out) < 14 else r.randint(2, 6)
            sd = r.randint(1, 4)
            words = ["".join(r.choice(_st.ascii_lowercase) for _ in range(r.randint(1, 3))) for _ in range(sd)]
            body = ""
            while len(body) < 20:
                body += r.choice(words) if r.random() < 0.6 else r.choice(_st.ascii_lowercase)
            body = body[:20]
            out.append("1 %d\n%s\n%d\n%s\n" % (k, body, sd, "\n".join(words)))
    elif pid == "P1027":
        while len(out) < spec["count"]:
            n = r.randint(1, 2); blocks = []
            for _ in range(n):
                S = r.randint(2, 4); t = r.randint(1, 20); rows = []
                for i in range(S):
                    x, y = r.randint(0, 25), r.randint(0, 25)
                    w, h = r.randint(1, 8), r.randint(1, 8); T = r.randint(1, 10)
                    rows.append("%d %d %d %d %d %d %d" % (x, y, x, y+h, x+w, y, T))
                blocks.append("%d %d 1 %d\n%s" % (S, t, S, "\n".join(rows)))
            out.append("%d\n%s\n" % (n, "\n".join(blocks)))
    elif pid == "P1032":
        import string as _st
        def _ws(lo, hi): return "".join(r.choice(_st.ascii_lowercase) for _ in range(r.randint(lo, hi)))
        while len(out) < spec["count"]:
            A = _ws(2, 5); rows = []
            for _ in range(r.randint(2, 3)): rows.append("%s %s" % (_ws(1, 2), _ws(1, 2)))
            if r.random() < 0.5:
                left, right = rows[0].split()
                A = _ws(1, 2)+left+_ws(1, 2)
                B = A.replace(left, right, 1)
                if len(B) > 20: B = B[:20]
            else: B = _ws(1, 5)
            out.append("%s %s\n%s\n" % (A, B, "\n".join(rows)))
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
