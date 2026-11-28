# P1060 朴素（枚举全部 2^m 购买子集，逐子集算花费与价值，取可行最大；不做 DP）：
# 组合数指数级，对拍限 m≤12（如实标注，不假装覆盖 m<25）。
import sys
def main():
    d = list(map(int, sys.stdin.read().split()))
    N, m = d[0], d[1]
    items = [(d[2+2*i], d[2+2*i+1]) for i in range(m)]
    best = 0
    for mask in range(1 << m):
        cost = val = 0
        for i in range(m):
            if mask >> i & 1:
                cost += items[i][0]; val += items[i][0]*items[i][1]
                if cost > N: break
        else:
            if cost <= N and val > best: best = val
    print(best)
if __name__ == "__main__": main()
