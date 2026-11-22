#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第 9 批验证（三类口径）
补最小外壳后只验核心逻辑；搜索摘要 != 正文；渲染吞字符按题解文字补最小外壳。
逐字源码：
  P1423 4fj37pww   https://www.luogu.org/article/4fj37pww
  P1328 0z8yhoc0   https://www.luogu.com/article/0z8yhoc0
  P1012 kckry124   https://www.luogu.com/article/kckry124
  P1204 gw5uvykg   https://www.luogu.com/article/gw5uvykg
  P1553 nxvqnwg8   https://www.luogu.com/article/nxvqnwg8
  P1102 dxk2a7a8   https://www.luogu.com/article/dxk2a7a8
  P1598 biep97vd   https://www.luogu.com/article/biep97vd  (Python 3)
"""
import os, json, random, subprocess, itertools, functools
from collections import Counter

BASE = "/data/workspace/luogu_hack/build/r9"
os.makedirs(BASE, exist_ok=True)
R = {}

def cc(name, src):
    p=os.path.join(BASE,name+".cpp"); e=os.path.join(BASE,name)
    open(p,"w",encoding="utf-8").write(src)
    r=subprocess.run(["g++","-std=c++17","-O2","-o",e,p],capture_output=True,text=True)
    return e,(r.stderr[:700] if r.returncode else ""),r.returncode

def py(name, src):
    p=os.path.join(BASE,name+".py")
    open(p,"w",encoding="utf-8").write(src)
    return p

def run(exe,inp,t=30,python=False):
    cmd = ["python3",exe] if python else [exe]
    p=subprocess.run(cmd,input=inp,capture_output=True,text=True,timeout=t)
    return p.stdout,p.returncode,p.stderr[:300]

# =====================================================================
# A. P1423 4fj37pww —— 二分版；疑点：dist>target 应为 dist>=target
# =====================================================================
A_SRC = r"""
#include<iostream>
#include<limits.h>
using namespace std;
int L,R=INT_MAX,mid;
double target,dist,per=2;
int main(){
 cin>>target;
 while(R>=L){
  mid=(L+R)/2;
  for(int i=1;i<=mid;i++){
   dist+=per;
   per*=0.98;
   if(dist>target) break;
  }
  if(dist>target) R=mid-1;
  else L=mid+1;
  dist=0; per=2;
 }
 cout<<L;
 return 0;
}
"""
# 修复版：两处 > 改成 >=
A_FIX = A_SRC.replace("if(dist>target) break;","if(dist>=target) break;").replace("if(dist>target) R=mid-1;","if(dist>=target) R=mid-1;")

def ok1423(s):
    d=0.0; per=2.0; ans=0
    while d < s - 1e-12:
        d += per; per *= 0.98; ans += 1
        if ans > 100000: break
    return ans

for tag,src in [("orig",A_SRC),("fix",A_FIX)]:
    e,err,ce=cc("a_1423_"+tag,src)
    R.setdefault("P1423_4fj37pww",{})[tag]={"compile_error":err}

if all(v.get("compile_error")=="" for v in R["P1423_4fj37pww"].values()):
    # 恰好等于前 k 步累计和的输入（double 可精确表示 s=2）
    partial=[2.0]
    d=2.0; per=2.0*0.98
    for k in range(2,12):
        d += per; per *= 0.98; partial.append(d)
    pts = ["4.3","2","2.0","3.96","5.8808","0.5","1","1.9","1.99","2.01",
           "10","50","99","99.9"] + [repr(x) for x in partial[:8]]
    cases=[]
    for s in pts:
        try: exp=ok1423(float(s))
        except: continue
        o,rc,_=run(f"{BASE}/a_1423_orig",s+"\n",t=15)
        w,rc2,_=run(f"{BASE}/a_1423_fix",s+"\n",t=15)
        cases.append({"input":s,"expected":exp,"actual":o.strip(),"orig_rc":rc,"fix_actual":w.strip(),"hacked":o.strip()!=str(exp)})
    R["P1423_4fj37pww"]["cases"]=cases
    rnd=random.Random(20261121)
    stats={t:{"tested":0,"mismatch":0,"examples":[]} for t in ["orig","fix"]}
    for _ in range(200):
        s=round(rnd.uniform(0.01,99.9),6)
        exp=ok1423(s); inp=f"{s}\n"
        for tag in ["orig","fix"]:
            o,rc,_=run(f"{BASE}/a_1423_{tag}",inp,t=15)
            stats[tag]["tested"]+=1
            if o.strip()!=str(exp):
                stats[tag]["mismatch"]+=1
                if len(stats[tag]["examples"])<4: stats[tag]["examples"].append({"input":s,"expected":exp,"actual":o.strip()})
    R["P1423_4fj37pww"]["random"]=stats

# =====================================================================
# B. P1328 0z8yhoc0 —— w[a] =「能赢 a 的手势」
# 逐字取回里 `for(int i(nb+1;i<=n;i++)` 是渲染吞 '='，按题解文字补最小外壳
# =====================================================================
B_SRC = r"""
#include<cstdio>
int a[201],b[201]; int ansa=0,ansb=0; int n,na,nb,ma,mb;
int w[5][2]={{1,4},{2,4},{0,3},{0,1},{2,3}};
int main(){
 ma=1,mb=1;
 scanf("%d%d%d",&n,&na,&nb);
 for(int i=1;i<=na;i++) scanf("%d",&a[i]);
 for(int i=1;i<=nb;i++) scanf("%d",&b[i]);
 for(int i=na+1;i<=n;i++){ a[i]=a[ma];ma++; if(ma==na+1) ma=1; }
 for(int i=nb+1;i<=n;i++){ b[i]=b[mb];mb++; if(mb==nb+1) mb=1; }
 for(int i=1;i<=n;i++){
  if(a[i]==b[i]) continue;
  for(int j=0;j<=1;j++) if(b[i]==w[a[i]][j]) ansb++;
  for(int j=0;j<=1;j++) if(a[i]==w[b[i]][j]) ansa++;
 }
 printf("%d %d",ansa,ansb);
 return 0;
}
"""
# 题面胜负表：0剪刀赢2布/3蜥蜴人；1石头赢0剪刀/3蜥蜴人；2布赢1石头/4斯波克
WIN = {0:{2,3},1:{0,3},2:{1,4},3:{2,4},4:{0,1}}
def ok1328(n,fa,fb):
    sa=sb=0
    for i in range(n):
        x=fa[i%len(fa)]; y=fb[i%len(fb)]
        if x==y: continue
        if y in WIN[x]: sa+=1
        else: sb+=1
    return f"{sa} {sb}"

e,err,ce=cc("b_1328",B_SRC)
R["P1328_0z8yhoc0"]={"compile_error":err}
if not ce:
    fixed=[(10,5,6,[0,1,2,3,4],[0,3,4,2,1,0]),(9,5,5,[0,1,2,3,4],[1,0,3,2,4]),
           (1,1,1,[0],[0]),(1,1,1,[0],[1]),(3,1,2,[4],[2,3]),(200,200,200,None,None)]
    cases=[]
    rnd0=random.Random(1)
    for n,na,nb,fa,fb in fixed:
        if fa is None:
            fa=[rnd0.randint(0,4) for _ in range(na)]; fb=[rnd0.randint(0,4) for _ in range(nb)]
        inp=f"{n} {na} {nb}\n"+" ".join(map(str,fa))+"\n"+" ".join(map(str,fb))+"\n"
        exp=ok1328(n,fa,fb); o,rc,_=run(e,inp)
        cases.append({"label":f"n={n} na={na} nb={nb}","expected":exp,"actual":o.strip(),"hacked":o.strip()!=exp})
    R["P1328_0z8yhoc0"]["cases"]=cases
    rnd=random.Random(20261121); mism=0; ex=[]
    for t in range(300):
        n=rnd.randint(1,200); na=rnd.randint(1,200); nb=rnd.randint(1,200)
        fa=[rnd.randint(0,4) for _ in range(na)]; fb=[rnd.randint(0,4) for _ in range(nb)]
        inp=f"{n} {na} {nb}\n"+" ".join(map(str,fa))+"\n"+" ".join(map(str,fb))+"\n"
        exp=ok1328(n,fa,fb); o,rc,_=run(e,inp)
        if o.strip()!=exp:
            mism+=1
            if len(ex)<4: ex.append({"input":inp.strip().replace("\n"," / "),"expected":exp,"actual":o.strip()})
    R["P1328_0z8yhoc0"].update({"random_tested":300,"mismatch":mism,"examples":ex})

# =====================================================================
# C. P1012 kckry124 —— sort(a+1,a+n+1,cmp)
# =====================================================================
C_SRC = r"""
#include <iostream>
#include <algorithm>
using namespace std;
bool cmp(string a, string b){ return a + b > b + a; }
int main(){
 int n; string a[21]; cin >> n;
 for (int i = 1; i <= n; i++) cin >> a[i];
 sort(a + 1, a + n + 1, cmp);
 for (int i = 1; i <= n; i++) cout << a[i];
 return 0;
}
"""
def ok1012(vals):
    return max("".join(p) for p in itertools.permutations(vals))
e,err,ce=cc("c_1012",C_SRC)
R["P1012_kckry124"]={"compile_error":err}
if not ce:
    rnd=random.Random(20261121); mism=0; ex=[]
    fixed=[["13","312","343"],["12","121"],["9","98","987"],["1","10","100"],["321","32","3"]]
    cases=[]
    for vals in fixed:
        inp=f"{len(vals)}\n"+" ".join(vals)+"\n"; exp=ok1012(vals); o,rc,_=run(e,inp)
        cases.append({"input":" ".join(vals),"expected":exp,"actual":o.strip(),"hacked":o.strip()!=exp})
    R["P1012_kckry124"]["cases"]=cases
    for t in range(300):
        k=rnd.randint(1,7); vals=[str(rnd.randint(0,9999)) for _ in range(k)]
        inp=f"{k}\n"+" ".join(vals)+"\n"; exp=ok1012(vals); o,rc,_=run(e,inp)
        if o.strip()!=exp:
            mism+=1
            if len(ex)<4: ex.append({"input":" ".join(vals),"expected":exp,"actual":o.strip()})
    R["P1012_kckry124"].update({"random_tested":300,"mismatch":mism,"examples":ex})

# =====================================================================
# D. P1204 gw5uvykg —— 区间合并
# =====================================================================
D_SRC = r"""
#include<bits/stdc++.h>
using namespace std;
int N;
struct node{ int begin, end; }m[5005];
bool cmp(node a, node b){ return a.begin < b.begin; }
int main(){
 scanf("%d", &N);
 for(register int i = 1; i <= N; ++ i) scanf("%d%d", &m[i].begin, &m[i].end);
 sort(m + 1, m + 1 + N, cmp);
 int begin = m[1].begin; int end = m[1].end; int ans1 = 0, ans2 = 0;
 for(register int i = 2; i <= N; ++ i){
  if(m[i].begin <= end) end = max(end, m[i].end);
  else{ ans1 = max(ans1, end - begin); ans2 = max(ans2, m[i].begin - end); begin = m[i].begin; end = m[i].end; }
 }
 ans1 = max(ans1, end - begin);
 printf("%d %d", ans1, ans2);
 return 0;
}
"""
def ok1204(ints):
    lo=min(a for a,b in ints); hi=max(b for a,b in ints)
    busy=[0]*(hi-lo+2)
    for a,b in ints:
        for t in range(a,b): busy[t-lo]=1   # [a,b) 有人
    cur=0; mx1=0; mx2=0
    for t in range(lo,hi):
        if busy[t-lo]: cur+=1; mx1=max(mx1,cur)
        else: cur=0
    # 最长无人段（只在有人的区间之间）
    run0=0; started=False
    for t in range(lo,hi):
        if busy[t-lo]:
            if started: mx2=max(mx2,run0)
            started=True; run0=0
        elif started: run0+=1
    return f"{mx1} {mx2}"
e,err,ce=cc("d_1204",D_SRC)
R["P1204_gw5uvykg"]={"compile_error":err}
if not ce:
    rnd=random.Random(20261121); mism=0; ex=[]; tested=0
    for t in range(300):
        k=rnd.randint(1,12); ints=[]
        for _ in range(k):
            a=rnd.randint(1,200); b=a+rnd.randint(1,60); ints.append((a,b))
        inp=f"{k}\n"+"\n".join(f"{a} {b}" for a,b in ints)+"\n"
        exp=ok1204(ints); o,rc,_=run(e,inp); tested+=1
        if o.strip()!=exp:
            mism+=1
            if len(ex)<4: ex.append({"input":inp.strip().replace("\n"," / "),"expected":exp,"actual":o.strip()})
    R["P1204_gw5uvykg"].update({"random_tested":tested,"mismatch":mism,"examples":ex})

# =====================================================================
# E. P1553 nxvqnwg8 —— 逐字取回的完整代码
# =====================================================================
E_SRC = r"""
#include<iostream>
#include<cstring>
#include<cstdio>
using namespace std;
char a[200];
int len=0;
void reversef(int fro,int to){
    bool is_ok=false;
    for(int i=to;i>=fro;i--){
        if(is_ok==false){
            if(a[i]!='0'){ is_ok=true; cout<<a[i]; }
        }
        else cout<<a[i];
        if(is_ok==false&&i==fro) cout<<"0";
    }
}
void reverseb(int fro,int to){
    bool is_ok=false;
    for(int i=fro;i<=to;i++){
        if(a[i]!='0'){ fro=i; is_ok=true; break; }
    }
    if(is_ok==false){ cout<<"0"; return; }
    else { for(int i=to;i>=fro;i--) cout<<a[i]; }
}
int main(){
    cin>>a;
    len=strlen(a);
    for(int i=0;i<len;i++){
        if(a[i]=='.'){ reversef(0,i-1); cout<<a[i]; reverseb(i+1,len-1); return 0; }
        if(a[i]=='/'){ reversef(0,i-1); cout<<a[i]; reversef(i+1,len-1); return 0; }
        if(a[i]=='%'){ reversef(0,i-1); cout<<"%"; return 0; }
    }
    reversef(0,len-1);
    return 0;
}
"""
def revf(t):
    r=t[::-1].lstrip('0'); return r if r else '0'
def revb(t):
    s=t.lstrip('0'); return s[::-1] if s else '0'
def ok1553(s):
    if '.' in s:
        i=s.index('.'); return revf(s[:i])+'.'+revb(s[i+1:])
    if '/' in s:
        i=s.index('/'); return revf(s[:i])+'/'+revf(s[i+1:])
    if '%' in s:
        i=s.index('%'); return revf(s[:i])+'%'
    return revf(s)
e,err,ce=cc("e_1553",E_SRC)
R["P1553_nxvqnwg8"]={"compile_error":err}
if not ce:
    fixed=["0","1200","120.120","0.0012","12.0","120/210","0/120","1200%","0%","123","100","000","100.000","600/006","000%","3.1415","1000/1"]
    cases=[]
    for s in fixed:
        exp=ok1553(s); o,rc,_=run(e,s+"\n")
        cases.append({"input":s,"expected":exp,"actual":o.strip(),"hacked":o.strip()!=exp})
    R["P1553_nxvqnwg8"]["cases"]=cases
    rnd=random.Random(20261121); mism=0; ex=[]; tested=0
    for t in range(300):
        a="".join(rnd.choice("0123456789") for _ in range(rnd.randint(1,8)))
        kind=rnd.choice(["int","dec","frac","pct"])
        if kind=="dec": s=a+"."+"".join(rnd.choice("0123456789") for _ in range(rnd.randint(1,6)))
        elif kind=="frac": s=a+"/"+"".join(rnd.choice("0123456789") for _ in range(rnd.randint(1,6)))
        elif kind=="pct": s=a+"%"
        else: s=a
        exp=ok1553(s); o,rc,_=run(e,s+"\n"); tested+=1
        if o.strip()!=exp:
            mism+=1
            if len(ex)<5: ex.append({"input":s,"expected":exp,"actual":o.strip()})
    R["P1553_nxvqnwg8"].update({"random_tested":tested,"mismatch":mism,"examples":ex})

# =====================================================================
# F. P1102 dxk2a7a8 —— 降序排序 + 双指针
# =====================================================================
F_SRC = r"""
#include<bits/stdc++.h>
using namespace std;
bool cmp(const long long& a,const long long& b){ return a>b; }
long long shu[300000]={0};
int main(){
 int n,c;
 scanf("%d%d",&n,&c);
 for(int i=0;i<n;i++)scanf("%lld",&shu[i]);
 sort(shu,shu+n,cmp);
 int t=0,w=1;
 int tj,wj;
 int st,sw;
 long long sum=0;
 while(w<n){
  if(shu[t]-shu[w]>c)t++;
  if(shu[t]-shu[w]<c)w++;
  if(shu[t]-shu[w]==c){
   tj=wj=0;
   st=t,sw=w;
   for(int i=t;shu[i]==shu[st];i++){ tj++; t++; }
   if(c==0)wj=1;
   else
   for(int i=w;shu[i]==shu[sw];i++){ wj++; w++; }
   sum+=(long long)tj*(long long)wj;
  }
 }
 printf("%lld",sum);
 return 0;
}
"""
def ok1102(arr,c):
    cnt=Counter(arr)
    return sum(cnt[x+c] for x in arr)
e,err,ce=cc("f_1102",F_SRC)
R["P1102_dxk2a7a8"]={"compile_error":err}
if not ce:
    rnd=random.Random(20261121); mism=0; ex=[]; tested=0
    fixed=[([1,1,2,3],1),([1,2,3,4,5],1),([5,5,5],0),([1,5,3],2),([2,2,4,4,6],2)]
    cases=[]
    for arr,c in fixed:
        n=len(arr); inp=f"{n} {c}\n"+" ".join(map(str,arr))+"\n"
        exp=str(ok1102(arr,c)); o,rc,_=run(e,inp,t=15)
        cases.append({"input":f"{c} / "+" ".join(map(str,arr)),"expected":exp,"actual":o.strip(),"hacked":o.strip()!=exp})
    R["P1102_dxk2a7a8"]["cases"]=cases
    for t in range(300):
        n=rnd.randint(1,60); c=rnd.randint(0,10)
        arr=[rnd.randint(1,30) for _ in range(n)]
        inp=f"{n} {c}\n"+" ".join(map(str,arr))+"\n"
        exp=str(ok1102(arr,c)); o,rc,_=run(e,inp,t=15); tested+=1
        if o.strip()!=exp:
            mism+=1
            if len(ex)<4: ex.append({"input":inp.strip().replace("\n"," / "),"expected":exp,"actual":o.strip(),"rc":rc})
    R["P1102_dxk2a7a8"].update({"random_tested":tested,"mismatch":mism,"examples":ex})

# =====================================================================
# G. P1598 biep97vd —— Python 3 垂直柱状图
# =====================================================================
G_SRC = r"""
letters = [chr(i) for i in range(65, 91)]
staDic = dict(zip(letters, [0] * 26))
ins = [j for i in range(4) for j in input()]
for k in ins:
    if k in letters:
        staDic[k] += 1
maxValue = max(staDic.values())
ZDic = {'Z': staDic.pop('Z')}
while maxValue > 0:
    for value in staDic.values():
        if value >= maxValue:
            print('*', end=' ')
        else:
            print(' ', end=' ')
    if ZDic['Z'] >= maxValue:
        print('*')
    else:
        print(' ')
    maxValue -= 1
print(' '.join(letters))
"""
def ok1598(lines):
    cnt=[0]*26
    for line in lines:
        for ch in line:
            if 'A'<=ch<='Z': cnt[ord(ch)-65]+=1
    mx=max(cnt); out=[]
    for level in range(mx,0,-1):
        cells=['*' if c>=level else ' ' for c in cnt]
        out.append(' '.join(cells))
    out.append(' '.join(chr(65+i) for i in range(26)))
    return '\n'.join(out)+'\n'
p=py("g_1598",G_SRC)
R["P1598_biep97vd"]={}
rnd=random.Random(20261121); mism=0; ex=[]; tested=0
alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz .,!0123456789"
for t in range(200):
    lines=["".join(rnd.choice(alphabet) for _ in range(rnd.randint(0,60))) for _ in range(4)]
    inp="\n".join(lines)+"\n"
    exp=ok1598(lines); o,rc,err=run(p,inp,t=15,python=True); tested+=1
    if o!=exp:
        mism+=1
        if len(ex)<4: ex.append({"input":inp.strip().replace("\n"," / "),"expected":exp.replace("\n"," / "),"actual":o.replace("\n"," / "),"stderr":err})
R["P1598_biep97vd"].update({"random_tested":tested,"mismatch":mism,"examples":ex})

json.dump(R,open(os.path.join(BASE,"results.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=2)
print(json.dumps(R,ensure_ascii=False,indent=2))
