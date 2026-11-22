#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第 2 批验证（严格口径）：
  - 输入数据严格落在题面约束内
  - 不依赖评测机波动（不主张 TLE / 随机超时）
  - 存在确定性测试点使题解代码 WA / RE

逐字源码取自 www.luogu.com/article/<id>：
  arorhglg (P1182), yk90rg78 (P1002), P1002 vis 版, ove5v8ck (P1216)
"""
import os, json, random, subprocess

BASE = "/data/workspace/luogu_hack/build/r2"
os.makedirs(BASE, exist_ok=True)
R = {}

SOL = {}

SOL["P1182_arorhglg"] = r"""
#include <bits/stdc++.h>
using namespace std;
int n,k;
int l,r,m;
long long t,tot,a[10000001];
inline bool judge(int x)
{
    for(int i=1;i<=n;i++)
	{
        if((t+a[i])<=x)
		t+=a[i];
        else{
        	t=a[i];
			tot++;
		}
    }
    return tot>=k;
}
int main()
{
    scanf("%d%d",&n,&k);
    for(int i=1;i<=n;i++)
	{
        scanf("%d",&a[i]);
        r+=a[i];
        if(a[i]>l)
        l=a[i];
	}
    while(l<=r)
	{
        m=l+(r-l)/2;
        t=0,tot=0;
        if(judge(m))l=m+1;
        else r=m-1;
    }
    printf("%d",l);
    return 0;
}
"""

SOL["P1002_yk90rg78"] = r"""
#include<iostream>
#define MAXN 22
using namespace std;
long long f[MAXN][MAXN]={0};
int ctrl[MAXN][MAXN],n,m,hx,hy;
int d[9][2]={{0,0},{1,2},{1,-2},{-1,2},{-1,-2},{2,1},{2,-1},{-2,1},{-2,-1}};
int main(){
	cin>>n>>m>>hx>>hy;
	for(int i=0;i<9;i++){
		int tmpx=hx+d[i][0],tmpy=hy+d[i][1];
		if(tmpx>=0&&tmpx<=n&&tmpy>=0&&tmpy<=m)
			ctrl[tmpx][tmpy]=1;
	}
	for(int i=0;i<=n;i++)
		for(int j=0;j<=m;j++){
			if(ctrl[i][j])continue;
			if(i!=0)f[i][j]+=f[i-1][j];
			if(j!=0)f[i][j]+=f[i][j-1];
		}
		f[0][0]=1-ctrl[0][0];
		cout<<f[n][m];
	return 0;
}
"""

SOL["P1002_vis"] = r"""
#include <bits/stdc++.h>
using namespace std;
const int maxn=210;
long long dp[maxn][maxn];
int n,m,a,b;
bool vis[maxn][maxn];
const int x[]={0,-2,-1,1,2,2,1,-1,-2};
const int y[]={0,1,2,2,1,-1,-2,-2,-1};
int main(){
 memset(vis,true,sizeof(vis));
 cin>>n>>m>>a>>b;
 n+=2,m+=2,a+=2,b+=2;
 for(int i=1;i<=8;i++){ vis[a+x[i]][b+y[i]]=false; }
 vis[a][b]=false;
 dp[2][1]=1;
 for(int i=2;i<=n;i++){
  for(int j=2;j<=m;j++){
   if(vis[i][j]){ dp[i][j]=dp[i-1][j]+dp[i][j-1]; }
  }
 }
 cout<<dp[n][m]<<endl;
 return 0;
}
"""

def build(name):
    src = os.path.join(BASE, name + ".cpp")
    exe = os.path.join(BASE, name)
    with open(src, "w", encoding="utf-8") as f:
        f.write(SOL[name])
    p = subprocess.run(["g++", "-std=c++17", "-O2", "-o", exe, src],
                       capture_output=True, text=True)
    return exe, (p.stderr[:500] if p.returncode != 0 else "")

def run(exe, inp, timeout=25):
    p = subprocess.run([exe], input=inp, capture_output=True, text=True, timeout=timeout)
    return p.stdout.strip(), p.returncode

# ------------------------------------------------------------------ 正确解
def p1182_correct(a, k):
    lo, hi = max(a), sum(a)
    while lo < hi:
        mid = (lo + hi) // 2
        cnt, cur = 1, 0
        for v in a:
            if cur + v <= mid:
                cur += v
            else:
                cnt += 1; cur = v
        if cnt <= k:
            hi = mid
        else:
            lo = mid + 1
    return lo

def p1002_correct(n, m, hx, hy):
    N, M = n + 2, m + 2
    hx, hy = hx + 2, hy + 2
    d = [(0, 0), (1, 2), (1, -2), (-1, 2), (-1, -2),
         (2, 1), (2, -1), (-2, 1), (-2, -1)]
    blk = [[False] * (M + 4) for _ in range(N + 4)]
    for u, v in d:
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

# ================================================================== P1182
exe, err = build("P1182_arorhglg")
R["P1182_arorhglg"] = {"compile_error": err, "cases": []}
if not err:
    def mk(a, k):
        return f"{len(a)} {k}\n" + " ".join(map(str, a)) + "\n"
    tests = [
        ("官方样例", [4, 2, 4, 5, 1], 3),
        ("未溢出对照组", [25000] * 100, 50),
        ("H-004 溢出(100×3e7)", [30000000] * 100, 50),
        ("H-005 溢出(1e5×25000)", [25000] * 100000, 50000),
        ("H-005b 溢出(1e5×30000)", [30000] * 100000, 50000),
    ]
    for label, a, k in tests:
        exp = p1182_correct(a, k)
        out, rc = run(exe, mk(a, k))
        R["P1182_arorhglg"]["cases"].append({
            "label": label, "input_head": f"{len(a)} {k} / Ai={a[0]}×{len(a)}",
            "sum": sum(a), "int32_overflow": sum(a) > 2 ** 31 - 1,
            "expected": exp, "actual": out, "hacked": out != str(exp)})

# ================================================================== P1002 yk90rg78
exe, err = build("P1002_yk90rg78")
R["P1002_yk90rg78"] = {"compile_error": err, "cases": []}
if not err:
    for inp in ["6 6 3 3\n", "20 20 0 20\n", "20 20 10 10\n", "1 1 0 0\n"]:
        n, m, hx, hy = map(int, inp.split())
        exp = p1002_correct(n, m, hx, hy)
        out, rc = run(exe, inp)
        R["P1002_yk90rg78"]["cases"].append({
            "input": inp.strip(), "expected": exp, "actual": out,
            "hacked": out != str(exp)})

# ================================================================== P1002 vis 版
exe, err = build("P1002_vis")
R["P1002_vis"] = {"compile_error": err, "cases": []}
if not err:
    rnd = random.Random(20261120)
    tests = ["6 6 3 3\n", "20 20 0 20\n", "1 1 0 0\n"]
    for _ in range(60):
        tests.append(f"{rnd.randint(0,20)} {rnd.randint(0,20)} "
                     f"{rnd.randint(0,20)} {rnd.randint(0,20)}\n")
    bad = 0
    for inp in tests:
        n, m, hx, hy = map(int, inp.split())
        exp = p1002_correct(n, m, hx, hy)
        out, rc = run(exe, inp)
        if out != str(exp):
            bad += 1
            if len(R["P1002_vis"]["cases"]) < 5:
                R["P1002_vis"]["cases"].append(
                    {"input": inp.strip(), "expected": exp, "actual": out})
    R["P1002_vis"]["tested"] = len(tests)
    R["P1002_vis"]["mismatch"] = bad

with open(os.path.join(BASE, "results.json"), "w", encoding="utf-8") as f:
    json.dump(R, f, ensure_ascii=False, indent=2)
print(json.dumps(R, ensure_ascii=False, indent=2))
