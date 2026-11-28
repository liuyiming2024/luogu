# P1047 朴素（显式区间排序合并，再算剩余点数；不用差分标记）：
import sys
def main():
    d = list(map(int, sys.stdin.read().split()))
    l, m = d[0], d[1]; idx = 2
    segs = []
    for i in range(m):
        u, v = d[idx], d[idx+1]; idx += 2
        if u > v: u, v = v, u
        segs.append((u, v))
    segs.sort()
    merged = []
    for u, v in segs:
        if merged and u <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(merged[-1][1], v))
        else:
            merged.append((u, v))
    removed = sum(v-u+1 for u, v in merged)
    print(l+1-removed)
if __name__ == "__main__": main()
