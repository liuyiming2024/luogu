# P1034 朴素（子集枚举精确解，与 std 的区间 DP 完全不同的实现路径）：
# 枚举每个点属于哪个矩形（k^n），逐组算包围盒，显式检查两两矩形「完全分开」
#（x 或 y 区间严格错开，端点不许重合），再取最小面积和。
import sys, itertools

def main():
    data = sys.stdin.read().split()
    n, k = int(data[0]), int(data[1]); idx = 2
    pts = []
    for _ in range(n):
        pts.append((int(data[idx]), int(data[idx+1]))); idx += 2
    INF = 10**18; best = INF
    for assign in itertools.product(range(k), repeat=n):
        groups = [[] for _ in range(k)]
        for p, g in zip(pts, assign): groups[g].append(p)
        boxes = []
        for g in groups:
            if not g: continue
            xs = [p[0] for p in g]; ys = [p[1] for p in g]
            boxes.append((min(xs), max(xs), min(ys), max(ys),
                          (max(xs)-min(xs))*(max(ys)-min(ys))))
        ok = True
        for i in range(len(boxes)):
            for j in range(i+1, len(boxes)):
                a, b = boxes[i], boxes[j]
                sep = (a[1] < b[0] or b[1] < a[0] or a[3] < b[2] or b[3] < a[2])
                if not sep: ok = False; break
            if not ok: break
        if not ok: continue
        total = sum(b[4] for b in boxes)
        if total < best: best = total
    ans = best
    print(ans)

if __name__ == "__main__": main()
