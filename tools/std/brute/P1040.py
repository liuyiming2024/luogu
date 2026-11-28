# P1040 朴素（递归枚举全部二叉树形态，Catalan 指数级；n≤8 如实标注）：
# 不用 DP 填表，直接对每个区间枚举根并递归求左右子树最优，返回 (加分, 前序)。
import sys
from functools import lru_cache

def main():
    data = sys.stdin.read().split()
    n = int(data[0]); d = [0] + list(map(int, data[1:1+n]))
    @lru_cache(None)
    def enum(l, r):
        if l > r: return (1, ())
        # 题面逐字：「叶子的加分就是叶节点本身的分数。不考虑它的空子树」
        # —— 叶子不能套 f*f+d 公式，否则空子树贡献 1 会多算。
        if l == r: return (d[l], (l,))
        best = -1; bpre = ()
        for k in range(l, r+1):
            sl, pl = enum(l, k-1)
            sr, pr = enum(k+1, r)
            v = sl*sr + d[k]
            if v > best:
                best = v; bpre = (k,) + pl + pr
        return (best, bpre)
    score, pre = enum(1, n)
    print(score)
    print(" ".join(map(str, pre)))

if __name__ == "__main__": main()
