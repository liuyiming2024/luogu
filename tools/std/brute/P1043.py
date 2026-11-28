# P1043 朴素（枚举起点 + 枚举全部 m-1 个切点组合，逐段求和取模相乘）：
# 不做 DP，直接按题面「按顺序分为 m 个部分」组合枚举。指数级，对拍限 n≤8、m≤3。
import sys, itertools

def main():
    data = sys.stdin.read().split()
    n, m = int(data[0]), int(data[1]); idx = 2
    a = [int(data[idx+i]) for i in range(n)]
    lo, hi = 10**18, -1
    for start in range(n):
        ring = a[start:] + a[:start]
        for cuts in itertools.combinations(range(1, n), m-1):
            b = (0,) + cuts + (n,)
            prod = 1
            for i in range(m):
                prod *= (sum(ring[b[i]:b[i+1]]) % 10)
            lo = min(lo, prod); hi = max(hi, prod)
    print(lo); print(hi)

if __name__ == "__main__": main()
