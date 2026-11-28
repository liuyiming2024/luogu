# P1037 朴素（Python BFS 求可达集 + 原生大整数，不用 Floyd/不用 __int128）：
# 对每个出现过的数字从它出发做显式队列 BFS，逐位乘进 Python int。
import sys
from collections import deque

def main():
    data = sys.stdin.read().split()
    n = data[0]; k = int(data[1]); idx = 2
    g = {d: set([d]) for d in range(10)}
    edges = {d: [] for d in range(10)}
    for _ in range(k):
        a, b = int(data[idx]), int(data[idx+1]); idx += 2
        edges[a].append(b)
    def closure(start):
        seen = {start}; q = deque([start])
        while q:
            u = q.popleft()
            for v in edges[u]:
                if v not in seen: seen.add(v); q.append(v)
        return len(seen)
    cache = {}
    ans = 1
    for ch in n:
        d = int(ch)
        if d not in cache: cache[d] = closure(d)
        ans *= cache[d]
    print(ans)

if __name__ == "__main__": main()
