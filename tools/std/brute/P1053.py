# P1053 朴素（显式枚举「目标环方向 × 全部 n 个旋转」，逐位置比较计数，O(n²)）：
# 不做 diff 频次优化；对拍限 n≤30（如实标注，不假装覆盖 n≤50000）。
import sys

def build(n, wish):
    seq = [1]; used = {1}; prev = 0; cur = 1
    for _ in range(1, n):
        nxt = None
        for c in wish[cur]:
            if c != prev and c not in used:
                nxt = c; break
        if nxt is None: return None
        seq.append(nxt); used.add(nxt); prev, cur = cur, nxt
    if len(used) != n: return None
    for i, p in enumerate(seq):
        l, r = seq[(i-1) % n], seq[(i+1) % n]
        if {l, r} != set(wish[p]): return None
    return seq

def main():
    d = list(map(int, sys.stdin.read().split()))
    n = d[0]; idx = 1
    wish = {i+1: [d[idx+2*i], d[idx+2*i+1]] for i in range(n)}
    t = build(n, wish)
    if t is None:
        print(-1); return
    best = 0
    for seq in (t, t[::-1]):
        for shift in range(n):
            same = 0
            for p in range(n):
                if seq[(p+shift) % n] == p+1: same += 1
            best = max(best, same)
    print(n - best)

if __name__ == "__main__": main()
