#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
洛谷站内题解「逐篇 hack」本地静态验证脚本（第 1 批）
- 题解源码逐字取自 https://www.luogu.com/article/<id> 与 https://siyuan.blog.luogu.org/solution-p5179
- 仅本地编译运行 + 独立正确解对拍，不登录洛谷、不提交任何数据
- 输出 build/results.json 供生成清单使用
"""
import os, json, random, subprocess, itertools
from math import gcd

BASE = "/data/workspace/luogu_hack"
BUILD = os.path.join(BASE, "build")
os.makedirs(BUILD, exist_ok=True)

# ---------------------------------------------------------------- 题解源码
SOL = {}

SOL["P1001_zaohomhi"] = r"""
#include<iostream>
using namespace std;
int main(){
  int a,b;
  cin>>a>>b;
  cout<<a+b;
  return 0;
}
"""

SOL["P1002_sfifnfaa"] = r"""
#include <iostream>
#include <vector>
using namespace std;

int countPaths(int n, int m, int horse_x, int horse_y) {
    vector<vector<int>> dp(n+1, vector<int>(m+1, 0));
    dp[0][0] = 1;

    for (int i = 0; i <= n; i++) {
        for (int j = 0; j <= m; j++) {
            if ((i-2 == horse_x && j-1 == horse_y) || (i-1 == horse_x && j-2 == horse_y)) {
                dp[i][j] = 0;
            } else {
                dp[i][j] = (i > 0 ? dp[i-1][j] : 0) + (j > 0 ? dp[i][j-1] : 0);
            }
        }
    }

    return dp[n][m];
}

int main() {
    int n, m, horse_x, horse_y;
    cin >> n >> m >> horse_x >> horse_y;

    int paths = countPaths(n, m, horse_x, horse_y);
    cout << paths << endl;

    return 0;
}
"""

SOL["P1048_h4cn628r"] = r"""
#include<iostream>
#include<cmath>
using namespace std;
int f[1001],n,t,v[101],w[101];
int main(){
 cin>>t>>n;
 for(int i=1;i<=n;i++){
  cin>>w[i]>>v[i];
 }
 for(int i=1;i<=n;i++){
  for(int j=t;j>=w[i];j--) {
   f[j]=max(f[j-w[i]]+v[i], f[j]);
  }
 }
 cout<<f[t];
 return 0;
}
"""

# P1220 题解页面代码有省略，按题解文字描述补全局声明/函数头，核心 DFS 逐字保留
SOL["P1220_uezud59i"] = r"""
#include<bits/stdc++.h>
using namespace std;
long long n,m,minn,s;
long long a[100001],b[100001];
void dfs(int i,int j,int k,int v,int x)
{
 if (v>minn) return;
 if (i==1 && j==n) { if (v<minn) minn=v; return; }
 if (k==0) { if (i>1) dfs(i-1,j,0,v+x*abs(a[i-1]-a[i]),x-b[i-1]); if (j<n) dfs(i,j+1,1,v+x*abs(a[i]-a[j+1]),x-b[j+1]); }
 if (k==1) { if (j<n) dfs(i,j+1,1,v+x*abs(a[j]-a[j+1]),x-b[j+1]); if (i>1) dfs(i-1,j,0,v+x*abs(a[j]-a[i-1]),x-b[i-1]); }
}
int main(){
 cin>>n>>m;
 minn=1000000000;
 for (int i=1; i<=n; ++i) { cin>>a[i]>>b[i]; s+=b[i]; }
 s-=b[m];
 dfs(m,m,0,0,s);
 cout<<minn;
 return 0;
}
"""

SOL["P5179_siyuan"] = r"""
#include <cstdio>
typedef long long LL;
LL gcd(LL x,LL y){ return y?gcd(y,x%y):x; }
void sim(LL &x,LL &y) { LL d=gcd(x,y); x/=d,y/=d; }
void solve(LL a,LL b,LL c,LL d,LL &p,LL &q){
 sim(a,b),sim(c,d);
 LL x=a/b+1,y=(c-1)/d;
 if(x<=y) p=x,q=1;
 else if(!a) p=1,q=d/c+1;
 else if(a<=b&&c<=d) solve(d,c,b,a,q,p);
 else solve(a%b,b,c-d*(a/b),d,p,q),p+=q*(a/b);
}
int main() {
 LL a,b,c,d,p,q;
 while(~scanf("%lld%lld%lld%lld",&a,&b,&c,&d)) {
  solve(a,b,c,d,p,q);
  printf("%lld/%lld\n",p,q);
 }
 return 0;
}
"""

# P3959 题解页面代码有 `……` 省略段（结构体/并查集/链式前向星/自定义 rand），
# 按题解描述补全模板部分；随机化贪心主逻辑 solve()/main() 逐字保留
SOL["P3959_l6u32sp7"] = r"""
#include<cstdio>
#include<algorithm>
#include<cstdlib>
#include<cstring>
#include<queue>
const int maxn=15,maxm=1010*2;
const int inf=0x3f3f3f3f;
const int seed=19260817,randtime=25000,swaptime=10;
struct KEDGE{ int x,y,w; bool isInMST; };
struct STAR{ int e,nxt,w; };
int n,m;
int map[maxn][maxn];
KEDGE kruskalEdge[maxm];
int father[maxn];
int head[maxn],starCnt=0;
STAR starEdge[maxm];
int vis1[maxn],vis2[maxn],kdep[maxn];
int kcnt=0,rcnt=0,cnt=0;
int ans=inf;
int rand(int l,int r){ return l + rand()%(r-l+1); }
bool compareLaw(const KEDGE &a,const KEDGE &b){ return a.w<b.w; }
int find(int x){ return father[x]==x?x:father[x]=find(father[x]); }
void unionx(int x,int y){ father[find(x)]=find(y); }
void add(int x,int y,int w){ starEdge[++starCnt]=(STAR){y,head[x],w}; head[x]=starCnt; }
void solve(int time){
 for(int i=1;i<=n;++i)father[i]=i;
 cnt=1,rcnt=0;
 memset(head,0,sizeof(head));
 memset(starEdge,0,sizeof(starEdge));
 for(int i=1;i<=kcnt;++i)kruskalEdge[i].isInMST=0;
 std::sort(kruskalEdge+1,kruskalEdge+kcnt+1,compareLaw);
 for(int i=1;i<=swaptime;++i)std::swap(kruskalEdge[rand(1,kcnt)],kruskalEdge[rand(1,kcnt)]);
 starCnt=0;
 for(int i=1;i<=kcnt;i++){
  int x=kruskalEdge[i].x,y=kruskalEdge[i].y;
  if(find(x)!=find(y)){
   unionx(x,y);
   kruskalEdge[i].isInMST=1;
   rcnt++;
   if(rcnt==n-1)break;
  }
 }
 for(int i=1;i<=kcnt;++i){
  if(kruskalEdge[i].isInMST){
   int x=kruskalEdge[i].x,y=kruskalEdge[i].y,w=kruskalEdge[i].w;
   add(x,y,w);
   add(y,x,w);
  }
 }
 for(int i=1;i<=n;++i){
  int res=0;
  memset(vis1,0,sizeof(vis1));
  memset(vis2,0,sizeof(vis2));
  memset(kdep,0,sizeof(kdep));
  std::queue<int>q1,q2;
  q1.push(i);
  kdep[i]=1;
  while(!q1.empty()){
   int pos=q1.front(); q1.pop();
   if(vis1[pos])continue;
   vis1[pos]=1;
   for(int j=head[pos];j;j=starEdge[j].nxt){
    int to=starEdge[j].e;
    if(!vis1[to]){ kdep[to]=kdep[pos]+1; q1.push(to); }
   }
  }
  q2.push(i);
  while(!q2.empty()){
   int pos=q2.front(); q2.pop();
   if(vis2[pos])continue;
   vis2[pos]=1;
   for(int j=head[pos];j;j=starEdge[j].nxt){
    int to=starEdge[j].e;
    if(!vis2[to]){ res+=starEdge[j].w*kdep[pos]; q2.push(to); }
   }
  }
  ans=std::min(ans,res);
 }
}
int main(){
 memset(map,0x3f,sizeof(map));
 srand(seed);
 scanf("%d%d",&n,&m);
 if(n==1&&m==0){ printf("0"); return 0; }
 for(int i=1;i<=m;++i){
  int u,v,w;
  scanf("%d%d%d",&u,&v,&w);
  map[u][v]=std::min(map[u][v],w);
  map[v][u]=std::min(map[v][u],w);
 }
 for(int i=1;i<=n;++i){
  for(int j=i;j<=n;++j){
   if(map[i][j]!=inf) kruskalEdge[++kcnt]=(KEDGE){i,j,map[i][j],0};
  }
 }
 for(int i=1;i<=randtime;++i)solve(i);
 printf("%d",ans);
 return 0;
}
"""

# ---------------------------------------------------------------- 工具
def build(name):
    src = os.path.join(BUILD, name + ".cpp")
    exe = os.path.join(BUILD, name)
    with open(src, "w", encoding="utf-8") as f:
        f.write(SOL[name])
    r = subprocess.run(["g++", "-std=c++17", "-O2", "-o", exe, src],
                       capture_output=True, text=True)
    return exe, (r.stderr[:600] if r.returncode else "")

def run(exe, inp, timeout=20):
    p = subprocess.run([exe], input=inp, capture_output=True, text=True, timeout=timeout)
    return p.stdout.strip(), p.stderr.strip()[:200], p.returncode

R = {}

# ---------------------------------------------------------------- P1001
exe, err = build("P1001_zaohomhi")
R["P1001_zaohomhi"] = {"compile_error": err, "cases": []}
for inp in ["1000000000 1000000000\n", "-1000000000 -1000000000\n", "1 2\n"]:
    a, b = map(int, inp.split())
    out, se, rc = run(exe, inp)
    R["P1001_zaohomhi"]["cases"].append(
        {"input": inp.strip(), "expected": a + b, "actual": out, "hacked": out != str(a + b)})

# ---------------------------------------------------------------- P1002
exe, err = build("P1002_sfifnfaa")
def p1002_correct(n, m, hx, hy):
    N, M = n + 2, m + 2
    hx, hy = hx + 2, hy + 2
    dx = [0, -2, -1, 1, 2, 2, 1, -1, -2]
    dy = [0, 1, 2, 2, 1, -1, -2, -2, -1]
    blk = [[False] * (M + 4) for _ in range(N + 4)]
    for u, v in zip(dx, dy):
        x, y = hx + u, hy + v
        if 0 <= x <= N + 2 and 0 <= y <= M + 2:
            blk[x][y] = True
    dp = [[0] * (M + 4) for _ in range(N + 4)]
    dp[2][2] = 0 if blk[2][2] else 1
    for i in range(2, N + 1):
        for j in range(2, M + 1):
            if i == 2 and j == 2:
                continue
            dp[i][j] = 0 if blk[i][j] else dp[i - 1][j] + dp[i][j - 1]
    return dp[N][M]

R["P1002_sfifnfaa"] = {"compile_error": err, "cases": []}
for inp in ["6 6 3 3\n", "20 20 0 20\n", "20 20 10 10\n", "1 1 0 0\n"]:
    n, m, hx, hy = map(int, inp.split())
    exp = p1002_correct(n, m, hx, hy)
    out, se, rc = run(exe, inp)
    R["P1002_sfifnfaa"]["cases"].append(
        {"input": inp.strip(), "expected": exp, "actual": out,
         "hacked": out != str(exp),
         "note": "官方样例" if inp.startswith("6 6") else ""})

# ---------------------------------------------------------------- P1048
exe, err = build("P1048_h4cn628r")
def p1048_correct(T, items):
    dp = [0] * (T + 1)
    for w, v in items:
        for j in range(T, w - 1, -1):
            dp[j] = max(dp[j], dp[j - w] + v)
    return dp[T]

R["P1048_h4cn628r"] = {"compile_error": err, "cases": []}
if not err:
    cases = []
    cases.append(("70 3\n71 100\n69 1\n1 2\n", 70, [(71, 100), (69, 1), (1, 2)]))
    cases.append(("0 1\n1 5\n", 0, [(1, 5)]))
    random.seed(7)
    for _ in range(30):
        T = random.randint(1, 1000); M = random.randint(1, 100)
        items = [(random.randint(1, max(1, T)), random.randint(1, 1000)) for _ in range(M)]
        s = f"{T} {M}\n" + "".join(f"{w} {v}\n" for w, v in items)
        cases.append((s, T, items))
    cases.append(("1000 100\n" + "1 1000\n" * 100, 1000, [(1, 1000)] * 100))
    for s, T, items in cases:
        exp = p1048_correct(T, items)
        out, se, rc = run(exe, s)
        R["P1048_h4cn628r"]["cases"].append(
            {"input": s.strip().split("\n")[0] + " …", "expected": exp,
             "actual": out, "hacked": out != str(exp)})

# ---------------------------------------------------------------- P1220
exe, err = build("P1220_uezud59i")
def p1220_correct(pos, w, c):
    n = len(pos) - 1
    S = sum(w[1:n + 1])
    pre = [0] * (n + 1)
    for i in range(1, n + 1):
        pre[i] = pre[i - 1] + w[i]
    INF = 10 ** 18
    f = [[[INF, INF] for _ in range(n + 2)] for _ in range(n + 2)]
    f[c][c][0] = f[c][c][1] = 0
    for length in range(2, n + 1):
        for i in range(1, n - length + 2):
            j = i + length - 1
            restL = S - (pre[j] - pre[i])
            f[i][j][0] = min(f[i + 1][j][0] + (pos[i + 1] - pos[i]) * restL,
                             f[i + 1][j][1] + (pos[j] - pos[i]) * restL)
            restR = S - (pre[j - 1] - pre[i - 1])
            f[i][j][1] = min(f[i][j - 1][0] + (pos[j] - pos[i]) * restR,
                             f[i][j - 1][1] + (pos[j] - pos[j - 1]) * restR)
    return min(f[1][n][0], f[1][n][1])

R["P1220_uezud59i"] = {"compile_error": err, "cases": []}
if not err:
    def make_case(n, seed):
        rnd = random.Random(seed)
        xs = sorted(rnd.sample(range(1, 101), n))
        ws = [rnd.randint(1, 100) for _ in range(n)]
        c = rnd.randint(1, n)
        pos = [0] + xs; w = [0] + ws
        s = f"{n} {c}\n" + "".join(f"{xs[i]} {ws[i]}\n" for i in range(n))
        return s, pos, w, c
    tests = [("5 3\n2 10\n3 20\n5 20\n6 30\n8 10\n",
              [0, 2, 3, 5, 6, 8], [0, 10, 20, 20, 30, 10], 3)]
    for sd in range(12):
        tests.append(make_case(random.Random(sd + 100).randint(2, 8), sd + 100))
    for s, pos, w, c in tests:
        exp = p1220_correct(pos, w, c)
        out, se, rc = run(exe, s)
        R["P1220_uezud59i"]["cases"].append(
            {"input": s.strip().split("\n")[0] + " …", "expected": exp,
             "actual": out, "hacked": out != str(exp)})

# ---------------------------------------------------------------- P5179
exe, err = build("P5179_siyuan")
def p5179_brute(a, b, c, d):
    # 分母 q 最小，其次分子 p 最小，且 p/q 为最简分数，a/b < p/q < c/d
    for q in range(1, 4000):
        p = (a * q) // b + 1
        if p * d < c * q and gcd(p, q) == 1:
            return f"{p}/{q}"
    return "?"

R["P5179_siyuan"] = {"compile_error": err, "cases": []}
if not err:
    bad = []
    rnd = random.Random(2026)
    tests = [(1, 2, 2, 3), (0, 1, 1, 3), (1, 3, 1, 2), (7, 8, 8, 9), (1, 1, 3, 2)]
    for _ in range(120):
        b = rnd.randint(1, 30); d = rnd.randint(1, 30)
        a = rnd.randint(0, 30); c = rnd.randint(1, 30)
        tests.append((a, b, c, d))
    for (a, b, c, d) in tests:
        exp = p5179_brute(a, b, c, d)
        out, se, rc = run(exe, f"{a} {b} {c} {d}\n")
        if out != exp:
            bad.append({"input": f"{a} {b} {c} {d}", "expected": exp, "actual": out})
    R["P5179_siyuan"]["cases"] = bad[:10]
    R["P5179_siyuan"]["total_tested"] = len(tests)
    R["P5179_siyuan"]["mismatch_count"] = len(bad)

# ---------------------------------------------------------------- P3959
exe, err = build("P3959_l6u32sp7")
def spanning_trees(n, edges):
    """Prüfer 序列枚举全部生成树，edges: {(u,v): w}，1-indexed"""
    seen = set()
    for seq in itertools.product(range(1, n + 1), repeat=n - 2):
        deg = [0] * (n + 1)
        for x in seq:
            deg[x] += 1
        tree = []
        ok = True
        s = list(seq)
        for x in s:
            leaf = -1
            for v in range(1, n + 1):
                if deg[v] == 0:
                    leaf = v; break
            if leaf < 0:
                ok = False; break
            key = (min(leaf, x), max(leaf, x))
            if key not in edges:
                ok = False; break
            tree.append((leaf, x, edges[key]))
            deg[leaf] -= 1; deg[x] -= 1
        if not ok:
            continue
        rem = [v for v in range(1, n + 1) if deg[v] == 0]
        if len(rem) != 2:
            continue
        u, v = rem
        key = (min(u, v), max(u, v))
        if key not in edges:
            continue
        tree.append((u, v, edges[key]))
        seen.add(tuple(sorted((min(a, b), max(a, b), w) for a, b, w in tree)))
    return [list(t) for t in seen]

def tree_cost(n, tree, root):
    adj = [[] for _ in range(n + 1)]
    for u, v, w in tree:
        adj[u].append((v, w)); adj[v].append((u, w))
    dep = [0] * (n + 1); dep[root] = 1
    q = [root]; res = 0
    while q:
        u = q.pop(0)
        for v, w in adj[u]:
            if dep[v] == 0:
                dep[v] = dep[u] + 1
                res += w * dep[u]
                q.append(v)
    return res

R["P3959_l6u32sp7"] = {"compile_error": err, "cases": []}
if not err:
    found = None
    for sd in range(60):
        rnd = random.Random(sd + 9000)
        n = 5
        # 先保证连通：随机生成一棵树
        perm = list(range(1, n + 1)); rnd.shuffle(perm)
        ed = {}
        for i in range(1, n):
            u, v = perm[i], perm[rnd.randint(0, i - 1)]
            key = (min(u, v), max(u, v))
            ed[key] = rnd.randint(1, 30)
        # 再加若干条边
        for _ in range(rnd.randint(2, 6)):
            u, v = rnd.sample(range(1, n + 1), 2)
            key = (min(u, v), max(u, v))
            if key not in ed:
                ed[key] = rnd.randint(1, 30)
        trees = spanning_trees(n, ed)
        best = min(tree_cost(n, t, r) for t in trees for r in range(1, n + 1))
        lines = [f"{n} {len(ed)}"]
        for (u, v), w in ed.items():
            lines.append(f"{u} {v} {w}")
        inp = "\n".join(lines) + "\n"
        out, se, rc = run(exe, inp, timeout=30)
        try:
            actual = int(out)
        except Exception:
            actual = out
        if actual != best:
            found = {"input": inp.strip(), "expected": best, "actual": actual,
                     "spanning_trees": len(trees), "seed": sd + 9000}
            break
    if found:
        R["P3959_l6u32sp7"]["cases"].append(found)
    else:
        R["P3959_l6u32sp7"]["cases"].append(
            {"note": "60 组 n=5 随机连通图内未与全局最优产生差异（不代表算法正确）"})

# ---------------------------------------------------------------- 汇总
with open(os.path.join(BUILD, "results.json"), "w", encoding="utf-8") as f:
    json.dump(R, f, ensure_ascii=False, indent=2)
print(json.dumps(R, ensure_ascii=False, indent=2))
