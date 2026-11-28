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
    "P1033": {}, "P1034": {}, "P1035": {}, "P1036": {}, "P1037": {},
    "P1038": {}, "P1039": {}, "P1040": {}, "P1041": {}, "P1042": {},
    "P1043": {}, "P1045": {}, "P1046": {}, "P1047": {}, "P1048": {},
    "P1049": {}, "P1050": {}, "P1051": {}, "P1052": {}, "P1053": {},
    "P1054": {}, "P1055": {}, "P1056": {}, "P1057": {}, "P1058": {},
    "P1060": {}, "P1061": {}, "P1062": {}, "P1063": {}, "P1064": {},
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
    "P1033": {"count": 40, "bounds": "1≤H,S1,V,L,K,n≤10^5；构造 K<H 且覆盖窗口远宽于采样步长"},
    "P1034": {"count": 40, "bounds": "1≤n≤50，1≤k≤4，0≤xi,yi≤500；对拍限 n≤7"},
    "P1035": {"count": 40, "bounds": "1≤k≤15"},
    "P1036": {"count": 40, "bounds": "1≤n≤20，k<n，1≤xi≤5×10^6；对拍限 n≤12"},
    "P1037": {"count": 40, "bounds": "n<10^30，k≤15，规则右部非零"},
    "P1038": {"count": 40, "bounds": "1≤n≤100，|W|≤10^9；对拍限 n≤8 的 DAG，输入层 U=0"},
    "P1039": {"count": 40, "bounds": "1≤M≤20，0≤N≤M，1≤P≤100；对拍限 M≤6"},
    "P1040": {"count": 40, "bounds": "1≤n<30，分数<100；对拍限 n≤8"},
    "P1041": {"count": 40, "bounds": "1≤n≤300 的树；疑似错题，对拍限 n≤9"},
    "P1042": {"count": 40, "bounds": "每行≤25 字母、≤2500 行，含 E"},
    "P1043": {"count": 40, "bounds": "1≤n≤50、1≤m≤9、|ai|≤10^4；对拍限 n≤8、m≤3"},
    "P1045": {"count": 40, "bounds": "1000<P<3100000；对拍限 P≤20000（朴素全量展开）"},
    "P1046": {"count": 40, "bounds": "10 个高度 100..200，手高 100..120"},
    "P1047": {"count": 40, "bounds": "1≤l≤10^4，1≤m≤100，0≤u≤v≤l"},
    "P1048": {"count": 40, "bounds": "1≤T≤1000，1≤M≤100；对拍限 M≤12"},
    "P1049": {"count": 40, "bounds": "0<n≤30，1≤V≤20000"},
    "P1050": {"count": 40, "bounds": "1≤n<10^100，1≤k≤100；对拍限 k≤3"},
    "P1051": {"count": 40, "bounds": "1≤N≤100，成绩 0..100，论文 0..10"},
    "P1052": {"count": 40, "bounds": "1≤L≤10^9，1≤S≤T≤10，1≤M≤100；对拍限 L≤300"},
    "P1053": {"count": 40, "bounds": "3≤n≤50000；对拍限 n≤30"},
    "P1054": {"count": 40, "bounds": "表达式≤50 字符、2≤n≤26；含非法括号选项（题面逐字忽略）"},
    "P1055": {"count": 40, "bounds": "x-xxx-xxxxx-x 格式，识别码可为 X"},
    "P1056": {"count": 40, "bounds": "2≤N,M≤1000、0≤K<M、0≤L<N、0≤D≤2000；对拍限 M,N≤8"},
    "P1057": {"count": 40, "bounds": "3≤n≤30、1≤m≤30；对拍限 m≤12"},
    "P1058": {"count": 40, "bounds": "1≤m,n≤50、每格 1..100；对拍限 m,n≤4 且高度≤3"},
    "P1060": {"count": 40, "bounds": "n<3×10^4、m<25；对拍限 m≤12"},
    "P1061": {"count": 40, "bounds": "1≤s<t≤26、2≤w≤t-s；对拍限 w≤6、t-s≤9"},
    "P1062": {"count": 40, "bounds": "3≤k≤15、10≤N≤1000（朴素子集枚举可全量覆盖）"},
    "P1063": {"count": 40, "bounds": "4≤N≤100、标记≤1000；对拍限 n≤6"},
    "P1064": {"count": 40, "bounds": "1≤n≤3.2×10^4、1≤m≤60；对拍限 m≤10"},
}


NEW_TEXT_PIDS = {"P1003","P1024","P1025","P1029","P1030","P1031",
                 "P1022","P1023","P1026","P1027","P1032",
                 "P1033","P1034","P1035","P1036","P1037",
                 "P1038","P1039","P1040","P1041","P1042",
                 "P1043","P1045","P1046","P1047","P1048",
                 "P1049","P1050","P1051","P1052","P1053",
                 "P1054","P1055","P1056","P1057","P1058",
                 "P1060","P1061","P1062","P1063","P1064"}


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
        if pid == "P1033":
            if len(L) != 1: return False
            v = list(map(float, L[0].split()))
            return len(v) == 6 and all(1 <= x <= 100000 for x in v) and v[4] < v[0]
        if pid == "P1034":
            if len(L) < 2: return False
            n, k = map(int, L[0].split())
            if not (1 <= n <= 50 and 1 <= k <= 4 and len(L) == n+1): return False
            for row in L[1:]:
                v = list(map(int, row.split()))
                if len(v) != 2 or any(not (0 <= x <= 500) for x in v): return False
            return True
        if pid == "P1035":
            if len(L) != 1: return False
            v = list(map(int, L[0].split()))
            return len(v) == 1 and 1 <= v[0] <= 15
        if pid == "P1036":
            if len(L) != 2: return False
            n, k = map(int, L[0].split())
            if not (1 <= n <= 20 and 1 <= k < n): return False
            v = list(map(int, L[1].split()))
            return len(v) == n and all(1 <= x <= 5*10**6 for x in v)
        if pid == "P1037":
            if len(L) < 1: return False      # k=0（无规则）也是合法输入
            head = L[0].split()
            if len(head) != 2: return False
            n, k = head[0], int(head[1])
            if not (n.isdigit() and n[0] != "0" and len(n) <= 30 and 0 <= k <= 15): return False
            if len(L) != 1+k: return False
            for row in L[1:]:
                v = list(map(int, row.split()))
                if len(v) != 2 or not (0 <= v[0] <= 9) or not (1 <= v[1] <= 9): return False
            return True
        if pid == "P1038":
            if len(L) < 2: return False
            n, p = map(int, L[0].split())
            if not (1 <= n <= 100 and len(L) == 1+n+p): return False
            for row in L[1:1+n]:
                v = list(map(int, row.split()))
                if len(v) != 2: return False
            for row in L[1+n:]:
                v = list(map(int, row.split()))
                if len(v) != 3 or not (1 <= v[0] <= n and 1 <= v[1] <= n) or abs(v[2]) > 10**9: return False
            return True
        if pid == "P1039":
            if len(L) < 3: return False
            M, N, P = map(int, L[0].split())
            if not (1 <= M <= 20 and 0 <= N <= M and 1 <= P <= 100 and len(L) == 1+M+P): return False
            if any(not (x.isalpha() and x.isupper()) for x in L[1:1+M]): return False
            return all(len(row) <= 250 for row in L[1+M:])
        if pid == "P1040":
            if len(L) != 2: return False
            n = int(L[0].split()[0]); v = list(map(int, L[1].split()))
            return 1 <= n < 30 and len(v) == n and all(1 <= x < 100 for x in v)
        if pid == "P1041":
            if len(L) < 2: return False
            n, p = map(int, L[0].split())
            if not (1 <= n <= 300 and len(L) == 1+p): return False
            for row in L[1:]:
                v = list(map(int, row.split()))
                if len(v) != 2 or not (1 <= v[0] <= n and 1 <= v[1] <= n): return False
            return True
        if pid == "P1042":
            if not (1 <= len(L) <= 2500): return False
            for row in L:
                if len(row) > 25: return False
                if any(ch not in "WLE" for ch in row): return False
            return "E" in "\n".join(L)
        if pid == "P1043":
            if len(L) < 2: return False
            h = L[0].split()
            if len(h) != 2: return False
            n, m = int(h[0]), int(h[1])
            if not (1 <= n <= 50 and 1 <= m <= 9 and len(L) == 1+n): return False
            for row in L[1:]:
                v = list(map(int, row.split()))
                if len(v) != 1 or abs(v[0]) > 10**4: return False
            return True
        if pid == "P1045":
            if len(L) != 1: return False
            v = list(map(int, L[0].split()))
            return len(v) == 1 and 1000 < v[0] < 3100000
        if pid == "P1046":
            if len(L) != 2: return False
            a = list(map(int, L[0].split())); b = list(map(int, L[1].split()))
            return (len(a) == 10 and all(100 <= x <= 200 for x in a)
                    and len(b) == 1 and 100 <= b[0] <= 120)
        if pid == "P1047":
            if len(L) < 2: return False
            h = L[0].split()
            if len(h) != 2: return False
            l, m = int(h[0]), int(h[1])
            if not (1 <= l <= 10**4 and 1 <= m <= 100 and len(L) == 1+m): return False
            for row in L[1:]:
                v = list(map(int, row.split()))
                if len(v) != 2 or not (0 <= v[0] <= v[1] <= l): return False
            return True
        if pid == "P1048":
            if len(L) < 2: return False
            h = L[0].split()
            if len(h) != 2: return False
            T, M = int(h[0]), int(h[1])
            if not (1 <= T <= 1000 and 1 <= M <= 100 and len(L) == 1+M): return False
            for row in L[1:]:
                v = list(map(int, row.split()))
                if len(v) != 2 or any(not (1 <= x <= 100) for x in v): return False
            return True
        if pid == "P1049":
            if len(L) < 3: return False
            V = int(L[0].split()[0]); n = int(L[1].split()[0])
            if not (0 < n <= 30 and 1 <= V <= 20000 and len(L) == 2+n): return False
            for row in L[2:]:
                v = list(map(int, row.split()))
                if len(v) != 1 or v[0] < 1: return False
            return True
        if pid == "P1050":
            if len(L) != 1: return False
            v = L[0].split()
            if len(v) != 2: return False
            ns, k = v[0], int(v[1])
            return (ns.isdigit() and ns[0] != "0" and len(ns) <= 100
                    and int(ns) < 10**100 and 1 <= k <= 100)
        if pid == "P1051":
            if len(L) < 2: return False
            N = int(L[0].split()[0])
            if not (1 <= N <= 100 and len(L) == 1+N): return False
            for row in L[1:]:
                f = row.split()
                if len(f) != 6: return False
                if not (f[0].isalpha() and len(f[0]) <= 20): return False
                if not (f[1].isdigit() and f[2].isdigit()): return False
                if not (0 <= int(f[1]) <= 100 and 0 <= int(f[2]) <= 100): return False
                if f[3] not in ("Y","N") or f[4] not in ("Y","N"): return False
                if not (f[5].isdigit() and 0 <= int(f[5]) <= 10): return False
            return True
        if pid == "P1052":
            if len(L) != 3: return False
            L0 = int(L[0].split()[0]); h = list(map(int, L[1].split()))
            if len(h) != 3: return False
            S, T, M = h
            if not (1 <= L0 <= 10**9 and 1 <= S <= T <= 10 and 1 <= M <= 100): return False
            v = list(map(int, L[2].split()))
            return (len(v) == M and len(set(v)) == M
                    and all(1 <= x < L0 for x in v))
        if pid == "P1053":
            if len(L) < 2: return False
            n = int(L[0].split()[0])
            if not (3 <= n <= 50000 and len(L) == 1+n): return False
            for i, row in enumerate(L[1:], 1):
                v = list(map(int, row.split()))
                if len(v) != 2 or v[0] == v[1]: return False
                if any(not (1 <= x <= n) or x == i for x in v): return False
            return True
        if pid == "P1054":
            if len(L) < 3: return False
            if len(L[0]) > 50: return False
            v = L[1].split()
            if len(v) != 1 or not v[0].isdigit(): return False
            n = int(v[0])
            if not (2 <= n <= 26 and len(L) == 2+n): return False
            return all(len(row) <= 50 for row in L[2:])
        if pid == "P1055":
            if len(L) != 1: return False
            ss = L[0].strip(); parts = ss.split('-')
            return (len(parts) == 4 and len(parts[0]) == 1 and parts[0].isdigit()
                    and len(parts[1]) == 3 and parts[1].isdigit()
                    and len(parts[2]) == 5 and parts[2].isdigit()
                    and len(parts[3]) == 1 and (parts[3].isdigit() or parts[3] == 'X'))
        if pid == "P1056":
            if len(L) < 1: return False          # D=0 时无对行，题面允许
            h = list(map(int, L[0].split()))
            if len(h) != 5: return False
            M,N,K,Lc,D = h
            if not (2 <= M <= 1000 and 2 <= N <= 1000 and 0 <= K < M
                    and 0 <= Lc < N and 0 <= D <= 2000 and len(L) == 1+D): return False
            for row in L[1:]:
                v = list(map(int, row.split()))
                if len(v) != 4: return False
                x,y,p,q = v
                if not (1 <= x <= M and 1 <= p <= M and 1 <= y <= N and 1 <= q <= N): return False
                if not ((x == p and abs(y-q) == 1) or (y == q and abs(x-p) == 1)): return False
            return True
        if pid == "P1057":
            if len(L) != 1: return False
            v = list(map(int, L[0].split()))
            return len(v) == 2 and 3 <= v[0] <= 30 and 1 <= v[1] <= 30
        if pid == "P1058":
            if len(L) < 2: return False
            h = L[0].split()
            if len(h) != 2: return False
            m,n = int(h[0]), int(h[1])
            if not (1 <= m <= 50 and 1 <= n <= 50 and len(L) == 1+m): return False
            for row in L[1:]:
                v = list(map(int, row.split()))
                if len(v) != n or any(not (1 <= x <= 100) for x in v): return False
            return True
        if pid == "P1060":
            if len(L) < 2: return False
            h = L[0].split()
            if len(h) != 2: return False
            n,m = int(h[0]), int(h[1])
            if not (1 <= n < 3*10**4 and 1 <= m < 25 and len(L) == 1+m): return False
            for row in L[1:]:
                v = list(map(int, row.split()))
                if len(v) != 2 or not (0 <= v[0] <= 10**4) or not (1 <= v[1] <= 5): return False
            return True
        if pid == "P1061":
            if len(L) != 2: return False
            h = L[0].split()
            if len(h) != 3: return False
            s0,t,w = map(int,h)
            cur = L[1].strip()
            if not (1 <= s0 < t <= 26 and 2 <= w <= t-s0 and len(cur) == w): return False
            vals = [ord(c)-ord('a')+1 for c in cur]
            return all(s0 <= x <= t for x in vals) and all(vals[i] < vals[i+1] for i in range(w-1))
        if pid == "P1062":
            if len(L) != 1: return False
            v = list(map(int, L[0].split()))
            return len(v) == 2 and 3 <= v[0] <= 15 and 10 <= v[1] <= 1000
        if pid == "P1063":
            if len(L) != 2: return False
            n = int(L[0].split()[0])
            v = list(map(int, L[1].split()))
            return 4 <= n <= 100 and len(v) == n and all(1 <= x <= 1000 for x in v)
        if pid == "P1064":
            if len(L) < 2: return False
            h = L[0].split()
            if len(h) != 2: return False
            n,m = int(h[0]), int(h[1])
            if not (1 <= n <= 32000 and 1 <= m <= 60 and len(L) == 1+m): return False
            att_count = {}
            for row in L[1:]:
                v = list(map(int, row.split()))
                if len(v) != 3 or not (0 <= v[0] <= 10**4) or not (1 <= v[1] <= 5) or not (0 <= v[2] <= m): return False
                if v[2] > 0:
                    att_count[v[2]] = att_count.get(v[2], 0) + 1
                    if att_count[v[2]] > 2: return False      # 题面逐字：每个主件最多 2 个附件
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
    elif pid == "P1033":
        while len(out) < spec["count"]:
            H = r.randint(50, 200); K = r.randint(1, 20)
            V = r.randint(1, 10); L = r.randint(3, 15)
            S1 = r.randint(5, 60); n = r.randint(1, 20)
            out.append("%d %d %d %d %d %d\n" % (H, S1, V, L, K, n))
    elif pid == "P1034":
        import random as _rnd
        while len(out) < spec["count"]:
            n = r.randint(3, 7); k = r.randint(1, 4)
            coords = _rnd.Random(20261128 + len(out)).sample(
                [(x, y) for x in range(0, 40) for y in range(0, 40)], n)
            rows = "\n".join("%d %d" % c for c in coords)
            out.append("%d %d\n%s\n" % (n, k, rows))
    elif pid == "P1035":
        for k in range(1, 16): out.append("%d\n" % k)
        while len(out) < spec["count"]:
            out.append("%d\n" % r.randint(1, 15))
    elif pid == "P1036":
        while len(out) < spec["count"]:
            n = r.randint(3, 12); k = r.randint(1, min(4, n-1))
            v = [r.randint(1, 1000) for _ in range(n)]
            out.append("%d %d\n%s\n" % (n, k, " ".join(map(str, v))))
    elif pid == "P1037":
        while len(out) < spec["count"]:
            ln = r.randint(1, 8)
            n = str(r.randint(1, 9)) + "".join(str(r.randint(0, 9)) for _ in range(ln-1))
            k = r.randint(0, 6); rows = []
            for _ in range(k):
                rows.append("%d %d" % (r.randint(0, 9), r.randint(1, 9)))
            if rows:
                out.append("%s %d\n%s\n" % (n, k, "\n".join(rows)))
            else:
                out.append("%s %d\n" % (n, k))   # k=0 时不能有空规则行
    elif pid == "P1038":
        while len(out) < spec["count"]:
            n = r.randint(3, 8)
            edges = []
            for j in range(2, n+1):
                i = r.randint(1, j-1)
                edges.append((i, j, r.randint(-5, 5)))
                if len(edges) < n+4 and r.random() < 0.35:
                    i2 = r.randint(1, j-1)
                    if i2 != i: edges.append((i2, j, r.randint(-5, 5)))
            p = len(edges)
            indeg = [0]*(n+1)
            for i, j, w in edges: indeg[j] += 1
            lines = []
            for i in range(1, n+1):
                C = r.randint(1, 5) if indeg[i] == 0 else 0
                U = 0 if indeg[i] == 0 else r.randint(0, 3)
                lines.append("%d %d" % (C, U))
            for i, j, w in edges: lines.append("%d %d %d" % (i, j, w))
            out.append("%d %d\n%s\n" % (n, p, "\n".join(lines)))
    elif pid == "P1039":
        import string as _st
        WEEK = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        while len(out) < spec["count"]:
            M = r.randint(3, 6); names = list(_st.ascii_uppercase[:M])
            N = r.randint(0, M); P = r.randint(3, 8)
            rows = []
            for _ in range(P):
                sp = r.choice(names); who = r.choice(names)
                t = r.randrange(6)
                if t == 0: c = "I am guilty."
                elif t == 1: c = "I am not guilty."
                elif t == 2: c = "%s is guilty." % who
                elif t == 3: c = "%s is not guilty." % who
                elif t == 4: c = "Today is %s." % r.choice(WEEK)
                else: c = "How are you??"          # 题面：其他话不列入推理
                rows.append("%s: %s" % (sp, c))
            out.append("%d %d %d\n%s\n%s\n" % (M, N, P, "\n".join(names), "\n".join(rows)))
    elif pid == "P1040":
        while len(out) < spec["count"]:
            n = r.randint(1, 8)
            v = [r.randint(1, 99) for _ in range(n)]
            out.append("%d\n%s\n" % (n, " ".join(map(str, v))))
    elif pid == "P1041":
        while len(out) < spec["count"]:
            n = r.randint(3, 9); rows = []
            for j in range(2, n+1): rows.append("%d %d" % (r.randint(1, j-1), j))
            p = len(rows)
            out.append("%d %d\n%s\n" % (n, p, "\n".join(rows)))
    elif pid == "P1042":
        while len(out) < spec["count"]:
            rows = []
            for _ in range(r.randint(2, 6)):
                rows.append("".join(r.choice("WL") for _ in range(r.randint(5, 25))))
            rows.append("E")
            out.append("\n".join(rows) + "\n")
    elif pid == "P1043":
        while len(out) < spec["count"]:
            n = r.randint(2, 8); m = r.randint(1, min(3, n))
            vals = [r.randint(-10000, 10000) for _ in range(n)]
            out.append("%d %d\n%s\n" % (n, m, "\n".join(map(str, vals))))
    elif pid == "P1045":
        for P in [1001, 1279, 2000, 5000, 10000, 20000]:
            out.append("%d\n" % P)
        while len(out) < spec["count"]:
            out.append("%d\n" % r.randint(1001, 20000))
    elif pid == "P1046":
        while len(out) < spec["count"]:
            hs = [r.randint(100, 200) for _ in range(10)]
            out.append("%s\n%d\n" % (" ".join(map(str, hs)), r.randint(100, 120)))
    elif pid == "P1047":
        while len(out) < spec["count"]:
            l = r.randint(1, 10000); m = r.randint(1, 100); rows = []
            for _ in range(m):
                u = r.randint(0, l); v = r.randint(u, l)
                rows.append("%d %d" % (u, v))
            out.append("%d %d\n%s\n" % (l, m, "\n".join(rows)))
    elif pid == "P1048":
        while len(out) < spec["count"]:
            T = r.randint(1, 1000); M = r.randint(1, 12); rows = []
            for _ in range(M):
                rows.append("%d %d" % (r.randint(1, 100), r.randint(1, 100)))
            out.append("%d %d\n%s\n" % (T, M, "\n".join(rows)))
    elif pid == "P1049":
        while len(out) < spec["count"]:
            V = r.randint(1, 20000); n = r.randint(1, 30)
            ws = [r.randint(1, V) for _ in range(n)]
            out.append("%d\n%d\n%s\n" % (V, n, "\n".join(map(str, ws))))
    elif pid == "P1050":
        while len(out) < spec["count"]:
            k = r.randint(1, 3)
            n = r.choice([r.randint(1, 200), r.randint(1, 10**8),
                          r.randint(10**10, 10**30)])
            out.append("%d %d\n" % (n, k))
    elif pid == "P1051":
        import string as _st
        while len(out) < spec["count"]:
            N = r.randint(1, 100); rows = []
            for i in range(N):
                name = "".join(r.choice(_st.ascii_letters) for _ in range(r.randint(3, 12)))
                rows.append("%s %d %d %s %s %d" % (
                    name, r.randint(0, 100), r.randint(0, 100),
                    r.choice("YN"), r.choice("YN"), r.randint(0, 10)))
            out.append("%d\n%s\n" % (N, "\n".join(rows)))
    elif pid == "P1052":
        while len(out) < spec["count"]:
            L = r.randint(20, 300); S = r.randint(1, 5)
            T = r.randint(S, min(10, S+4)); M = r.randint(1, min(20, L-1))
            stones = sorted(r.sample(range(1, L), M))
            out.append("%d\n%d %d %d\n%s\n" % (L, S, T, M, " ".join(map(str, stones))))
    elif pid == "P1053":
        while len(out) < spec["count"]:
            n = r.randint(3, 30)
            if r.random() < 0.7:
                perm = list(range(1, n+1)); r.shuffle(perm)
                w = {p: [perm[(i-1) % n], perm[(i+1) % n]]
                     for i, p in enumerate(perm)}
                rows = ["%d %d" % (w[i][0], w[i][1]) for i in range(1, n+1)]
            else:
                rows = []
                for p in range(1, n+1):
                    c = r.sample([q for q in range(1, n+1) if q != p], 2)
                    rows.append("%d %d" % (c[0], c[1]))
            out.append("%d\n%s\n" % (n, "\n".join(rows)))
    elif pid == "P1054":
        TEMPLATES = [
          ("(a + 1)^2", ["a^2+2*a+1","(a+1)*(a+1)","(a-1)^2+4*a","1+a*2+a^2"], ["a^2+1","a+1","(a+1)^3","a*a+1"]),
          ("a^2+2*a+1", ["(a+1)^2","(a+1) ^ 2","1+2*a+a*a"], ["a^2+a+1","(a+2)^2","a^2+2*a"]),
          ("a*a+a-a", ["a^2","a^2+0","(a)*(a)"], ["a^3","a*a+a","a^2+1"]),
          ("9999+(a-a)*a", ["9999","9999+0*a","10000-1"], ["9998","a+9999"]),
          ("1^10^9", ["1","1^1","2-1"], ["2","1^2^3"]),
          ("(a+2)^3", ["a^3+6*a^2+12*a+8","(a+2)*(a+2)*(a+2)","8+12*a+6*a*a+a^3"], ["(a+2)^2","a^3+8"]),
          ("((a+a))", ["2*a","a+a","a*2"], ["3*a","a*a","a+1"]),
          ("1 + (a -1)^3", ["a^3-3*a^2+3*a","(a-1)^3+1"], ["a^3","1+(a-1)^2"]),
        ]
        INVALID = ["(a+1","a+1)","(a+1))","a++1","a^","a+","a 1","(a+1)^"]
        while len(out) < spec["count"]:
            target, eq, neq = r.choice(TEMPLATES)
            opts = [r.choice(eq)] + [r.choice(neq) for _ in range(r.randint(1,3))]
            if r.random() < 0.4: opts.append(r.choice(INVALID))
            r.shuffle(opts)
            out.append(target + "\n%d\n" % len(opts) + "\n".join(opts) + "\n")
    elif pid == "P1055":
        while len(out) < spec["count"]:
            digits = "".join(str(r.randint(0,9)) for _ in range(9))
            chk = r.choice([str(r.randint(0,9)), "X"])
            out.append("%s-%s-%s-%s\n" % (digits[0], digits[1:4], digits[4:9], chk))
    elif pid == "P1056":
        while len(out) < spec["count"]:
            M = r.randint(2,8); N = r.randint(2,8)
            K = r.randint(0, M-1); Lc = r.randint(0, N-1)
            maxpairs = (M-1)*N + M*(N-1)
            D = r.randint(0, min(12, maxpairs))
            pairs = set()
            while len(pairs) < D:
                x = r.randint(1,M); y = r.randint(1,N)
                if r.random() < 0.5 and x < M: p,q = x+1,y
                elif y < N: p,q = x,y+1
                else: continue
                pairs.add((x,y,p,q))
            rows = "\n".join("%d %d %d %d" % t for t in sorted(pairs))
            out.append("%d %d %d %d %d\n%s\n" % (M,N,K,Lc,len(pairs),rows))
    elif pid == "P1057":
        while len(out) < spec["count"]:
            out.append("%d %d\n" % (r.randint(3,30), r.randint(1,12)))
    elif pid == "P1058":
        while len(out) < spec["count"]:
            m = r.randint(1,4); n = r.randint(1,4)
            hs = [[r.randint(1,3) for _ in range(n)] for _ in range(m)]
            out.append("%d %d\n%s\n" % (m,n,"\n".join(" ".join(map(str,row)) for row in hs)))
    elif pid == "P1060":
        while len(out) < spec["count"]:
            N = r.randint(100, 1000); m = r.randint(1, 12)
            rows = ["%d %d" % (r.randint(0, 10**4), r.randint(1,5)) for _ in range(m)]
            out.append("%d %d\n%s\n" % (N,m,"\n".join(rows)))
    elif pid == "P1061":
        import itertools as _it
        while len(out) < spec["count"]:
            s0 = r.randint(1,17); t = min(26, s0 + r.randint(2,9)); w = r.randint(2, min(6, t-s0))
            combos = list(_it.combinations(range(s0,t+1), w))
            cur = "".join(chr(ord('a')+x-1) for x in r.choice(combos))
            out.append("%d %d %d\n%s\n" % (s0,t,w,cur))
    elif pid == "P1062":
        for k in range(3,16): out.append("%d %d\n" % (k, r.randint(10,1000)))
        while len(out) < spec["count"]:
            out.append("%d %d\n" % (r.randint(3,15), r.randint(10,1000)))
    elif pid == "P1063":
        while len(out) < spec["count"]:
            n = r.randint(4,6)
            a = [r.randint(1,1000) for _ in range(n)]
            out.append("%d\n%s\n" % (n," ".join(map(str,a))))
    elif pid == "P1064":
        while len(out) < spec["count"]:
            N = r.randint(100, 32000); m = r.randint(1, 10)
            rows = []; mains = []; used = {}
            for i in range(1, m+1):
                avail = [x for x in mains if used.get(x,0) < 2]
                if not avail or r.random() < 0.45:
                    rows.append("%d %d 0" % (r.randint(0, 10**4), r.randint(1,5)))
                    mains.append(i)
                else:
                    q = r.choice(avail)
                    used[q] = used.get(q,0) + 1
                    rows.append("%d %d %d" % (r.randint(0, 10**4), r.randint(1,5), q))
            out.append("%d %d\n%s\n" % (N,m,"\n".join(rows)))
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
