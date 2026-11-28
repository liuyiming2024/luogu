# P1064 朴素（**枚举全部 2^m 购买子集**，显式检查「附件的主件必须在子集内」的依赖）：
# 不做分组背包；组合数指数级，对拍限 m≤10（如实标注，不假装覆盖 m≤60）。
import sys
def main():
    d = list(map(int, sys.stdin.read().split()))
    N, m = d[0], d[1]; idx = 2
    v = [0]*(m+1); w = [0]*(m+1); q = [0]*(m+1)
    for i in range(1, m+1):
        v[i], w[i], q[i] = d[idx], d[idx+1], d[idx+2]; idx += 3
    best = 0
    for mask in range(1 << m):
        chosen = {i+1 for i in range(m) if mask >> i & 1}
        ok = True
        for i in chosen:
            if q[i] and q[i] not in chosen: ok = False; break
        if not ok: continue
        cost = sum(v[i] for i in chosen)
        if cost > N: continue
        val = sum(v[i]*w[i] for i in chosen)
        best = max(best, val)
    print(best)
if __name__ == "__main__": main()
