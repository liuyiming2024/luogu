#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第 5 批补充验证
  P1020 n5d7jq0b   https://www.luogu.com/article/n5d7jq0b
  P1616 lgmnaw1h   https://www.luogu.com/article/lgmnaw1h  (只取第 3 块=P1616 最终代码)
  P1164 ipduooli   https://www.luogu.com/article/ipduooli
  P1049 v3wxayi3   https://www.luogu.com/article/v3wxayi3 (随机化，仅记录)
"""
import os, json, random, subprocess

BASE = "/data/workspace/luogu_hack/build/r5"
os.makedirs(BASE, exist_ok=True)
R = {}
SOL = {}

SOL["P1020_n5d7jq0b"] = r"""
#include <bits/stdc++.h>
using namespace std;
int a[100010],d[100010],c[100010],n=0;
int main(){
 int x;
 while(cin>>x){ a[++n]=x; }
 memset(d,0x3f,sizeof(d)); memset(c,0x3f,sizeof(c));
 int p=0;
 for(int i=n,j=1; i>=1; i--, j++) {
     p=upper_bound(d+1,d+1+n,a[i])-d; d[p]=a[i];
     p=lower_bound(c+1,c+1+n,a[j])-c; c[p]=a[j];
 }
 int len=1; while(d[len]!=d[0]){ len++; } cout<<len-1<<endl;
 len=1; while(c[len]!=c[0]){ len++; } cout<<len-1<<endl;
 return 0;
}
"""

SOL["P1616_lgmnaw1h_final"] = r"""
#include <bits/stdc++.h>
using namespace std;
int i,j,T,M;
long long t[10001],p[10001],f[10000001];
int main(){
 scanf("%d%d",&T,&M);
 for(i=1;i<=M;i++) scanf("%lld%lld",&t[i],&p[i]);
 for(i=1;i<=M;i++) for(j=t[i];j<=T;j++) f[j]=max(f[j],f[j-t[i]]+p[i]);
 printf("%lld",f[T]);
 return 0;
}
"""

# ipduooli 逻辑等价版：仅把 dp[N][N] 缩到可编译/可运行大小，其余逐字
SOL["P1164_ipduooli"] = r"""
#include <bits/stdc++.h>
using namespace std;
const int inf = 1061109567;
const int N = 1e4 + 10;
int n, m, a[N];
int dp[310][10011];
signed main(){
 cin >> n >> m;
 for (int i = 1; i <= n; i++) cin >>a[i];
 dp[0][0] = 1;
 for (int i = 1; i <= n; i++){
     for (int j = m; j >= 1; -- j) {
         if (j >= a[i]) dp[i][j] = dp[i - 1][j - a[i]] + dp[i - 1][j];
         else dp[i][j] = dp[i - 1][j];
     }
 }
 cout << dp[n][m] << endl;
 return 0;
}
"""

def build(name):
    src=os.path.join(BASE,name+".cpp"); exe=os.path.join(BASE,name)
    open(src,"w",encoding="utf-8").write(SOL[name])
    p=subprocess.run(["g++","-std=c++17","-O2","-o",exe,src],capture_output=True,text=True)
    return exe,(p.stderr[:600] if p.returncode else ""),p.returncode

def run(exe,inp,timeout=30):
    p=subprocess.run([exe],input=inp,capture_output=True,text=True,timeout=timeout)
    return p.stdout.strip(),p.returncode

# ============================================================ P1020
def p1020_correct(seq):
    """第一问：最长不上升子序列长度；第二问：最少不上升序列覆盖数 = 最长上升子序列长度"""
    n=len(seq)
    # LNIS via O(n^2)
    dp=[1]*n
    for i in range(n):
        for j in range(i):
            if seq[j]>=seq[i]: dp[i]=max(dp[i],dp[j]+1)
    q1=max(dp) if n else 0
    # LIS (strict) via O(n^2)
    dp=[1]*n
    for i in range(n):
        for j in range(i):
            if seq[j]<seq[i]: dp[i]=max(dp[i],dp[j]+1)
    q2=max(dp) if n else 0
    return q1,q2

ex,err,ce=build("P1020_n5d7jq0b")
R["P1020_n5d7jq0b"]={"compile_error":err,"cases":[],"random_tested":0,"random_mismatch":0}
if ce==0:
    fixed=[("官方样例",[389,207,155,300,299,170,158,65]),
           ("全相等",[5]*6),("严格上升",[1,2,3,4,5]),("严格下降",[5,4,3,2,1]),
           ("单元素",[7]),("两元素相等",[3,3])]
    for label,seq in fixed:
        q1,q2=p1020_correct(seq)
        out,rc=run(ex," ".join(map(str,seq))+"\n")
        exp=f"{q1}\n{q2}"
        R["P1020_n5d7jq0b"]["cases"].append({"label":label,"input":" ".join(map(str,seq)),"expected":f"{q1} / {q2}","actual":out.replace("\n"," / "),"hacked":out!=exp})
    rnd=random.Random(20261120); bad=[]
    for t in range(250):
        n=rnd.randint(1,40)
        seq=[rnd.randint(1,60) for _ in range(n)]
        q1,q2=p1020_correct(seq); exp=f"{q1}\n{q2}"
        out,rc=run(ex," ".join(map(str,seq))+"\n")
        R["P1020_n5d7jq0b"]["random_tested"]+=1
        if out!=exp:
            R["P1020_n5d7jq0b"]["random_mismatch"]+=1
            if len(bad)<5: bad.append({"input":" ".join(map(str,seq)),"expected":f"{q1} / {q2}","actual":out.replace("\n"," / ")})
    R["P1020_n5d7jq0b"]["random_examples"]=bad

# ============================================================ P1616 最终块
def p1616_correct(T,items):
    f=[0]*(T+1)
    for a,b in items:
        for j in range(a,T+1):
            if f[j-a]+b>f[j]: f[j]=f[j-a]+b
    return f[T]

ex,err,ce=build("P1616_lgmnaw1h_final")
R["P1616_lgmnaw1h_final"]={"compile_error":err,"random_tested":0,"random_mismatch":0}
if ce==0:
    rnd=random.Random(20261120); bad=[]
    for t in range(200):
        M=rnd.randint(1,20); T=rnd.randint(1,400)
        items=[(rnd.randint(1,max(1,T//2)),rnd.randint(1,1000)) for _ in range(M)]
        exp=p1616_correct(T,items)
        inp=f"{T} {M}\n"+"\n".join(f"{a} {b}" for a,b in items)+"\n"
        out,rc=run(ex,inp)
        R["P1616_lgmnaw1h_final"]["random_tested"]+=1
        if out!=str(exp):
            R["P1616_lgmnaw1h_final"]["random_mismatch"]+=1
            if len(bad)<4: bad.append({"input":inp.strip().replace("\n"," / "),"expected":exp,"actual":out})
    R["P1616_lgmnaw1h_final"]["random_examples"]=bad

# ============================================================ P1164 ipduooli
def p1164_correct(prices,M):
    dp=[0]*(M+1); dp[0]=1
    for a in prices:
        for j in range(M,a-1,-1): dp[j]+=dp[j-a]
    return dp[M]

ex,err,ce=build("P1164_ipduooli")
R["P1164_ipduooli"]={"compile_error":err,"random_tested":0,"random_mismatch":0}
if ce==0:
    rnd=random.Random(777); bad=[]
    for t in range(200):
        n=rnd.randint(1,30); M=rnd.randint(1,300)
        pr=[rnd.randint(1,min(1000,M+50)) for _ in range(n)]
        exp=p1164_correct(pr,M)
        inp=f"{n} {M}\n"+" ".join(map(str,pr))+"\n"
        out,rc=run(ex,inp)
        R["P1164_ipduooli"]["random_tested"]+=1
        if out!=str(exp):
            R["P1164_ipduooli"]["random_mismatch"]+=1
            if len(bad)<4: bad.append({"input":f"{n} {M} / {pr[:8]}","expected":exp,"actual":out})
    R["P1164_ipduooli"]["random_examples"]=bad

json.dump(R,open(os.path.join(BASE,"results2.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=2)
print(json.dumps(R,ensure_ascii=False,indent=2))
