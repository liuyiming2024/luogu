# P1056 朴素（**枚举全部横/纵通道组合**，逐对检查是否被隔开，取被隔开对数最大者）：
# 不做贪心、不按计数排序；组合数 C(M-1,K)*C(N-1,L)，对拍限 M,N≤8、K,L≤3（如实标注）。
import sys, itertools

def main():
    d = list(map(int, sys.stdin.read().split()))
    M, N, K, L, D = d[:5]; idx = 5
    pairs = []
    for i in range(D):
        x, y, p, q = d[idx], d[idx+1], d[idx+2], d[idx+3]; idx += 4
        pairs.append((x, y, p, q))
    def blocked(rows, cols):
        c = 0
        for x, y, p, q in pairs:
            if x == p:
                if min(y, q) in cols: c += 1
            else:
                if min(x, p) in rows: c += 1
        return c
    best = -1; bestAB = None
    for A in itertools.combinations(range(1, M), K):
        for B in itertools.combinations(range(1, N), L):
            v = blocked(set(A), set(B))
            if v > best:
                best = v; bestAB = (A, B)
    A, B = bestAB
    print(" ".join(map(str, A)))
    print(" ".join(map(str, B)))

if __name__ == "__main__": main()
