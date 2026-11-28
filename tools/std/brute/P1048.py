# P1048 朴素（枚举全部 2^M 子集，逐子集算时间/价值，取可行最大；不做 DP）：
# 组合数指数级，对拍限 M≤12（如实标注）。
import sys, itertools
def main():
    d = list(map(int, sys.stdin.read().split()))
    T, M = d[0], d[1]; idx = 2
    items = [(d[idx+2*i], d[idx+2*i+1]) for i in range(M)]
    best = 0
    for mask in range(1 << M):
        t = v = 0
        for i in range(M):
            if mask >> i & 1:
                t += items[i][0]; v += items[i][1]
                if t > T: break
        else:
            if t <= T and v > best: best = v
    print(best)
if __name__ == "__main__": main()
