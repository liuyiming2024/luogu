#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第 5 批验证（三类口径）
补最小外壳后只验核心逻辑，不判完整度。
逐字源码：
  P1164 2yru0rav  https://www.luogu.com/article/2yru0rav
  P2240 bv44vwt6  https://www.luogu.com/article/bv44vwt6
  P1060 0hps6y5z  https://www.luogu.com/article/0hps6y5z
"""
import os, json, random, subprocess
from fractions import Fraction

BASE = "/data/workspace/luogu_hack/build/r5"
os.makedirs(BASE, exist_ok=True)
R = {}
SOL = {}

SOL["P1164_2yru0rav"] = r"""
#include<bits/stdc++.h>
using namespace std;
const int N=110,M=10010;
int f[N][M],n,m,a[N];
int main(){
 cin>>n>>m;
 for(int i=1;i<=n;i++) cin>>a[i];
 for(int i=1;i<=n;i++)
     for(int j=0;j<=m;j++){
         if(j==a[i]) f[i][j]=f[i-1][j]+1;
         if(j>a[i]) f[i][j]=f[i-1][j]+f[i-1][j-a[i]];
         if(j<a[i]) f[i][j]=f[i-1][j];
     }
 cout<<f[n][m];
 return 0;
}
"""

SOL["P2240_bv44vwt6"] = r"""
#include <bits/stdc++.h>
using namespace std;
int n,m;
struct node{ double v,w,x; }a[110];
int cmp(node a,node b){ return a.x>b.x; }
int main(){
 cin>>n>>m;
 for(int i=1;i<=n;i++) cin>>a[i].v>>a[i].w,a[i].x=a[i].w/a[i].v;
 sort(a+1,a+n+1,cmp);
 double res=0,weigh=m;
 for(int i=1;i<=n;i++){
     if(weigh){
         if(weigh>=a[i].v){res+=a[i].w,weigh-=a[i].v;}
         else {res+=(weigh/a[i].v)*a[i].w,weigh=0;}
     }
 }
 cout<<fixed<<setprecision(2)<<res<<endl;
 return 0;
}
"""

SOL["P1060_0hps6y5z"] = r"""
#include<iostream>
#include<cstdio>
using namespace std;
int n,m,b[25+1][30000+5]={0},i,j,v[25+1],p[25+1];
int main(){
 scanf("%d %d",&n,&m);
 for(i=1;i<=m;i++){
     scanf("%d %d",&v[i],&p[i]);
     for(j=n;j>=1;j--){
         b[i][j]=b[i-1][j];
         if(j>=v[i]&&b[i-1][j-v[i]]+v[i]*p[i]>b[i][j])b[i][j]=b[i-1][j-v[i]]+v[i]*p[i];
     }
 }
 printf("%d",b[m][n]);
 return 0;
}
"""

def build(name):
    src=os.path.join(BASE,name+".cpp"); exe=os.path.join(BASE,name)
    open(src,"w",encoding="utf-8").write(SOL[name])
    p=subprocess.run(["g++","-std=c++17","-O2","-o",exe,src],capture_output=True,text=True)
    return exe,(p.stderr[:600] if p.returncode else ""),p.returncode

def run(exe,inp,timeout=25):
    p=subprocess.run([exe],input=inp,capture_output=True,text=True,timeout=timeout)
    return p.stdout.strip(),p.returncode

# ================================================================ P1164
def p1164_correct(prices,M):
    dp=[0]*(M+1); dp[0]=1
    for a in prices:
        for j in range(M,a-1,-1): dp[j]+=dp[j-a]
    return dp[M]

ex,err,ce=build("P1164_2yru0rav")
R["P1164_2yru0rav"]={"compile_error":err,"cases":[],"random_tested":0,"random_mismatch":0}
if ce==0:
    fixed=[("官方样例",4,4,[1,1,2,2]),("单道菜刚好",1,5,[5]),
           ("单道菜超钱",1,5,[6]),("重复价格",5,10,[2,2,2,2,2])]
    for label,n,M,pr in fixed:
        exp=p1164_correct(pr,M)
        out,rc=run(ex,f"{n} {M}\n"+" ".join(map(str,pr))+"\n")
        R["P1164_2yru0rav"]["cases"].append({"label":label,"input":f"{n} {M} / {pr}","expected":exp,"actual":out,"hacked":out!=str(exp)})
    rnd=random.Random(20261120); bad=[]
    for t in range(250):
        n=rnd.randint(1,30); M=rnd.randint(1,200)
        pr=[rnd.randint(1,min(1000,M+50)) for _ in range(n)]
        exp=p1164_correct(pr,M)
        out,rc=run(ex,f"{n} {M}\n"+" ".join(map(str,pr))+"\n")
        R["P1164_2yru0rav"]["random_tested"]+=1
        if out!=str(exp):
            R["P1164_2yru0rav"]["random_mismatch"]+=1
            if len(bad)<4: bad.append({"input":f"{n} {M} / {pr[:8]}","expected":exp,"actual":out})
    R["P1164_2yru0rav"]["random_examples"]=bad

# ================================================================ P2240
def p2240_correct(items,T):
    """Fraction 精确贪心，避免浮点误差；返回保留两位小数的字符串"""
    items=sorted(items,key=lambda iv: Fraction(iv[1],iv[0]),reverse=True)
    rem=T; val=Fraction(0)
    for w,v in items:
        if rem<=0: break
        if w<=rem: val+=v; rem-=w
        else: val+=Fraction(v*rem,w); rem=0
    # C printf %.2lf 的舍入（round half away from zero 近似）
    from decimal import Decimal,ROUND_HALF_UP
    d=Decimal(val.numerator)/Decimal(val.denominator)
    return str(d.quantize(Decimal("0.01"),rounding=ROUND_HALF_UP))

ex,err,ce=build("P2240_bv44vwt6")
R["P2240_bv44vwt6"]={"compile_error":err,"cases":[],"random_tested":0,"random_mismatch":0}
if ce==0:
    fixed=[("官方样例",4,50,[("10","60"),("20","100"),("25","100"),("15","45")])]
    for label,n,T,items in fixed:
        exp=p2240_correct([(int(w),int(v)) for w,v in items],T)
        inp=f"{n} {T}\n"+"\n".join(f"{w} {v}" for w,v in items)+"\n"
        out,rc=run(ex,inp)
        R["P2240_bv44vwt6"]["cases"].append({"label":label,"input":inp.strip().replace("\n"," / "),"expected":exp,"actual":out,"hacked":out!=exp})
    rnd=random.Random(20261120); bad=[]
    for t in range(300):
        n=rnd.randint(1,20); T=rnd.randint(1,1000)
        items=[(rnd.randint(1,100),rnd.randint(1,100)) for _ in range(n)]
        exp=p2240_correct(items,T)
        inp=f"{n} {T}\n"+"\n".join(f"{w} {v}" for w,v in items)+"\n"
        out,rc=run(ex,inp)
        R["P2240_bv44vwt6"]["random_tested"]+=1
        if out!=exp:
            R["P2240_bv44vwt6"]["random_mismatch"]+=1
            if len(bad)<5: bad.append({"input":inp.strip().replace("\n"," / "),"expected":exp,"actual":out})
    R["P2240_bv44vwt6"]["random_examples"]=bad

# ================================================================ P1060
def p1060_correct(N,M,items):
    """items: [(price, importance)]，价值 = price*importance"""
    dp=[0]*(N+1)
    for pr,imp in items:
        val=pr*imp
        for j in range(N,pr-1,-1):
            dp[j]=max(dp[j],dp[j-pr]+val)
    return dp[N]

ex,err,ce=build("P1060_0hps6y5z")
R["P1060_0hps6y5z"]={"compile_error":err,"cases":[],"random_tested":0,"random_mismatch":0}
if ce==0:
    rnd=random.Random(20261120); bad=[]
    for t in range(250):
        M=rnd.randint(1,25); N=rnd.randint(1,600)
        items=[(rnd.randint(1,max(1,N//2)),rnd.randint(1,5)) for _ in range(M)]
        exp=p1060_correct(N,M,items)
        inp=f"{N} {M}\n"+"\n".join(f"{pr} {imp}" for pr,imp in items)+"\n"
        out,rc=run(ex,inp)
        R["P1060_0hps6y5z"]["random_tested"]+=1
        if out!=str(exp):
            R["P1060_0hps6y5z"]["random_mismatch"]+=1
            if len(bad)<4: bad.append({"input":inp.strip().replace("\n"," / "),"expected":exp,"actual":out})
    R["P1060_0hps6y5z"]["random_examples"]=bad

json.dump(R,open(os.path.join(BASE,"results.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=2)
print(json.dumps(R,ensure_ascii=False,indent=2))
