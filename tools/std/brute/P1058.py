# P1058 朴素（**逐像素反查 + 显式顶点/棱位置表 + 优先级合成**，与 std 的逐 cube 正向绘制不同）：
# 不维护画布写入顺序，而是收集所有 cube 在每个像素留下的字符，按「后画优先」取最高优先级。
# 坐标同样由题面三种相邻图示反推（这是题面规则本身，不是算法），但合成机制完全独立。
import sys

# 按题面图示逐条列出 cube 的非背景字符（含内部空格）：(dr,dc) -> ch
PAT = {}
def put(row, cols, ch):
    for dc in cols: PAT[(row, dc)] = ch
# 顶面四条边 + 内部空白
for dr, cols, ch in [(0, [2,6], '+'), (0, [3,4,5], '-')]: put(dr, cols, ch)
for dr, cols, ch in [(1, [1,5], '/'), (1, [2,3,4], ' '), (1, [6], '|')]: put(dr, cols, ch)
for dr, cols, ch in [(2, [0,4], '+'), (2, [1,2,3], '-'), (2, [5], ' '), (2, [6], '|')]: put(dr, cols, ch)
# 正面 + 右侧面
for dr, cols, ch in [(3, [0,4], '|'), (3, [1,2,3], ' '), (3, [5], ' '), (3, [6], '+')]: put(dr, cols, ch)
for dr, cols, ch in [(4, [0,4], '|'), (4, [1,2,3], ' '), (4, [5], '/')]: put(dr, cols, ch)
for dr, cols, ch in [(5, [0,4], '+'), (5, [1,2,3], '-')]: put(dr, cols, ch)

def main():
    d = list(map(int, sys.stdin.read().split()))
    m, n = d[0], d[1]; idx = 2
    h = [[0]*(n+1) for _ in range(m+1)]
    for i in range(1, m+1):
        for j in range(1, n+1): h[i][j] = d[idx]; idx += 1
    cubes = [(i,j,k) for i in range(1,m+1) for j in range(1,n+1)
             for k in range(1,h[i][j]+1)]
    def pos(i,j,k): return 2*(i-1)+3-3*(k-1), 4*(j-1)+2*(m-i)
    ps = [pos(*cb) for cb in cubes]
    minR = min(r for r,c in ps); minC = min(c for r,c in ps)
    maxR = max(r for r,c in ps)+5; maxC = max(c for r,c in ps)+6
    K, L = maxR-minR+1, maxC-minC+1
    marks = {}
    for pri, (r,c) in enumerate(ps):
        r -= minR; c -= minC
        for (dr,dc), ch in PAT.items():
            marks[(r+dr, c+dc)] = ch          # 后画（pri 大）覆盖先画
    for R in range(K):
        print("".join(marks.get((R,C), '.') for C in range(L)))

if __name__ == "__main__": main()
