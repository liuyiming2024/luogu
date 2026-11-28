# P1063 朴素（**递归枚举全部相邻聚合顺序**，显式按题面 (m,r)⊕(r,n)→m*r*n 计算）：
# 不做区间 DP 填表；状态为当前珠子头标记环，枚举每一对相邻珠子合并，指数级，
# 对拍限 n≤6（如实标注，不假装覆盖 n≤100）。
import sys
from functools import lru_cache

def solve(seq, n):
    @lru_cache(None)
    def go(t):
        if len(t) == 1: return 0
        best = -1
        L = len(t)
        for j in range(L):
            m = t[j]; r = t[(j+1)%L]; nn = t[(j+2)%L]
            rest = list(t)
            del rest[(j+1)%L]
            best = max(best, m*r*nn + go(tuple(rest)))
        return best
    return go(tuple(seq))

def main():
    d = list(map(int, sys.stdin.read().split()))
    n = d[0]; seq = d[1:1+n]
    print(solve(seq, n))
if __name__ == "__main__": main()
