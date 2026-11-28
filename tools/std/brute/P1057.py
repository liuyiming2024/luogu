# P1057 朴素（**枚举全部 2^m 条传球方向序列**，逐条模拟，统计回到 1 号的条数）：
# 与 DP 完全不同；指数级，对拍限 m≤12（如实标注，不假装覆盖 m≤30）。
import sys

def main():
    n, m = map(int, sys.stdin.read().split())
    ans = 0
    for mask in range(1 << m):
        cur = 0
        for t in range(m):
            cur = (cur + (1 if (mask >> t & 1) else -1)) % n
        if cur == 0: ans += 1
    print(ans)

if __name__ == "__main__": main()
