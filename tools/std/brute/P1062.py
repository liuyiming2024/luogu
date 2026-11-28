# P1062 朴素（**枚举所有 k 的幂子集和并排序**，按题面「递增序列」定义直接取第 N 项）：
# 不做二进制映射推导；子集数 2^11 足以覆盖 N≤1000，可全量对拍。
import sys
def main():
    k, N = map(int, sys.stdin.read().split())
    vals = []
    for mask in range(1, 1 << 11):
        s = 0; p = 1
        for i in range(11):
            if mask >> i & 1: s += p
            p *= k
        vals.append(s)
    vals.sort()
    print(vals[N-1])
if __name__ == "__main__": main()
