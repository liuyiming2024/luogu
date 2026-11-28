# P1041 朴素（bitmask 状态搜索，与 C++ 分层递归完全不同的实现）：
# 状态 = (已感染集合, 当前感染层集合)；枚举切断一条边，其余边传播一代。
# 疑似错题 + 指数状态，对拍只在 n≤9 小树上做（如实标注）。
import sys
from functools import lru_cache

def main():
    data = sys.stdin.read().split()
    n, p = int(data[0]), int(data[1]); idx = 2
    adj = [[] for _ in range(n+1)]
    for _ in range(p):
        i, j = int(data[idx]), int(data[idx+1]); idx += 2
        adj[i].append(j); adj[j].append(i)
    # BFS 定父子（无环树）
    par = [0]*(n+1); par[1] = -1; children = [[] for _ in range(n+1)]
    q = [1]
    while q:
        u = q.pop(0)
        for v in adj[u]:
            if v != par[u]: par[v] = u; children[u].append(v); q.append(v)
    @lru_cache(None)
    def solve(inf_mask, front_mask):
        edges = []
        for u in range(1, n+1):
            if not (front_mask >> u & 1): continue
            for v in children[u]:
                if not (inf_mask >> v & 1): edges.append(v)
        if not edges: return bin(inf_mask).count("1")
        best = 10**9
        for cut in range(len(edges)):
            nm = inf_mask; nf = 0
            for j, v in enumerate(edges):
                if j == cut: continue
                if not (nm >> v & 1): nm |= 1 << v; nf |= 1 << v
            best = min(best, solve(nm, nf))
        return best
    print(solve(1 << 1, 1 << 1))   # 节点编号从 1 起，bit 位必须对应 1<<v

if __name__ == "__main__": main()
