#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第 6 批验证（三类口径）
补最小外壳后只验核心逻辑，不判完整度；搜索摘要与正文冲突时以逐字取回为准。
逐字源码：
  P1563 xmumv7ok  https://www.luogu.com/article/xmumv7ok
  P1909 h8ic4o0m  https://www.luogu.com/article/h8ic4o0m
  P1424 apqvl7bn  https://www.luogu.com/article/apqvl7bn
  P1093 tehqdnw3  https://www.luogu.com/article/tehqdnw3
  P2141 b7py0ojt  https://www.luogu.com/article/b7py0ojt
  P1059 6t0wrb4o  https://www.luogu.com/article/6t0wrb4o
  P1059 05bplzw1  https://www.luogu.com/article/05bplzw1
  P1089 1ndosdfs  https://www.luogu.com/article/1ndosdfs
"""
import os, json, random, subprocess

BASE = "/data/workspace/luogu_hack/build/r6"
os.makedirs(BASE, exist_ok=True)
R = {}
SOL = {}

SOL["P1563_xmumv7ok"] = r"""
#include <bits/stdc++.h>
using namespace std;
char a[100005][15];
int n,x=1,z=0,m,b[100005],ai,si;
int main(){
 scanf("%d%d",&n,&m);
 for(int o=1;o<n+1;o++) cin>>b[o]>>a[o];
 for(int i=0;i<m;i++){
  scanf("%d%d",&ai,&si);
  if(ai==0&&b[x]==1) z=si;
  if(ai==1&&b[x]==0) z=si;
  if(ai==0&&b[x]==0) z=0-si;
  if(ai==1&&b[x]==1) z=0-si;
  if(z>=0){
   if(z>=n)z=z%n;
   x=x+z;
   if(x>n)x=x%n;
  }else{
   z=-z;
   if(z>=n)z=z%n;
   x=x-z;
   if(x<0)x=n+x;
   if(x>n)x=x%n;
  }
 }
 printf("%s",a[x]);
 return 0;
}
"""
# 仅改一处：x<0 -> x<=0
SOL["P1563_fix_one_char"] = SOL["P1563_xmumv7ok"].replace("if(x<0)x=n+x;", "if(x<=0)x=n+x;")

SOL["P1909_h8ic4o0m"] = r"""
#include<iostream>
using namespace std;
int main(){
 int n,a1,a2,b1,b2,c1,c2,da,db,dc,ans;
 cin>>n>>a1>>a2>>b1>>b2>>c1>>c2;
 if(n%a1!=0) da=(n/a1+1)*a2; else da=(n/a1)*a2;
 if(n%b1!=0) db=(n/b1+1)*b2; else db=(n/b1)*b2;
 if(n%c1!=0) dc=(n/c1+1)*c2; else dc=(n/c1)*c2;
 if(da<db) ans=da; else ans=db;
 if(dc<ans) ans=dc;
 cout<<ans;
 return 0;
}
"""

SOL["P1424_apqvl7bn"] = r"""
#include<cstdio>
int n,k,s=0;
int main(){
 scanf("%d %d",&n,&k);
 for(int i=1;i<=k;i++){
  if(n!=6 && n!=7) s+=250;
  if(n==7) n=1; else n++;
 }
 printf("%d",s);
 return 0;
}
"""

SOL["P1093_tehqdnw3"] = r"""
#include<bits/stdc++.h>
using namespace std;
int n,x,y,a[1000010],b[1000010];
int main(){
 cin>>n;
 for(int i=1;i<=n;i++){
  cin>>a[i]>>x>>y;
  b[i]=(a[i]+x+y)*1000000+a[i]*1000+n-i;
 }
 sort(b+1,b+n+1);
 for(int i=n;i>n-5;i--){
  cout<<n-b[i]%1000<<" "<<b[i]/1000000<<endl;
 }
 return 0;
}
"""

SOL["P2141_b7py0ojt"] = r"""
#include <iostream>
using namespace std;
int main(){
 int n; int a[101]; int b[10001]={0};
 cin>>n;
 for(int i=0;i<n;i++) cin>>a[i];
 for(int i=0;i<n-1;i++) for(int j=i+1;j<n;j++) if(a[i]+a[j]<=10000) b[a[i]+a[j]]=1;
 int count=0;
 for(int i=0;i<n;i++) if(b[a[i]]==1) count++;
 cout<<count;
 return 0;
}
"""

SOL["P1059_6t0wrb4o"] = r"""
#include<bits/stdc++.h>
using namespace std;
const int N=1e6+5;
int n,a[N],b[N],j=0;
int main(){
 cin>>n;
 for(int i=1;i<=n;i++) cin>>a[i];
 sort(a+1,a+1+n);
 for(int i=1;i<=n;i++) if(a[i]!=a[i-1]) b[++j]=a[i];
 cout<<j<<"\n";
 for(int i=1;i<=j;i++) cout<<b[i]<<" ";
 return 0;
}
"""

# 页面渲染把 `set<int> s;` 吞成 `sets;`，按题解文字补最小外壳
SOL["P1059_05bplzw1"] = r"""
#include<bits/stdc++.h>
using namespace std;
set<int> s;
int main(){
 int n; cin>>n;
 while(n--){ int x; cin>>x; s.insert(x); }
 cout<<s.size()<<endl;
 for(auto it=s.begin();it!=s.end();it++) cout<<*it<<" ";
 return 0;
}
"""

SOL["P1089_1ndosdfs"] = r"""
#include <stdio.h>
int main(){
 int me=0,mom=0,spend,i;
 for(i=1;i<=12;i++){
  me+=300;
  scanf("%d",&spend);
  me-=spend;
  if(me<0){ me=-i; break; }
  mom+=me/100*100;
  me%=100;
 }
 if(me<0) printf("%d",me);
 else printf("%g", me+mom*1.2);
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

# ============================================================ P1563
def p1563_correct(n,dirs,names,ops):
    cur=0
    for a,s in ops:
        if dirs[cur]==a: cur=(cur-s)%n
        else: cur=(cur+s)%n
    return names[cur]

def mk1563(n,dirs,names,ops):
    lines=[f"{n} {len(ops)}"]
    for i in range(n): lines.append(f"{dirs[i]} {names[i]}")
    for a,s in ops: lines.append(f"{a} {s}")
    return "\n".join(lines)+"\n"

ex,err,ce=build("P1563_xmumv7ok"); ex2,err2,ce2=build("P1563_fix_one_char")
R["P1563_xmumv7ok"]={"compile_error":err,"fixed_one_char_compile_error":err2,"cases":[],"random_tested":0,"orig_mismatch":0,"fixed_mismatch":0}
if ce==0 and ce2==0:
    fixed=[
      ("最小反例 x 减到 0",3,[0,0,0],["aa","bb","cc"],[(0,1)]),
      ("官方风格 n=7",7,[0,1,0,1,0,1,0],["a","b","c","d","e","f","g"],[(0,3),(1,2),(0,1)]),
      ("朝外向右导致 x=0",4,[1,1,1,1],["p","q","r","s"],[(1,1)]),
      ("正向分支对照",5,[0,0,0,0,0],["v","w","x","y","z"],[(1,2)]),
    ]
    for label,n,dirs,names,ops in fixed:
        exp=p1563_correct(n,dirs,names,ops); inp=mk1563(n,dirs,names,ops)
        o,rc=run(ex,inp); o2,rc2=run(ex2,inp)
        R["P1563_xmumv7ok"]["cases"].append({"label":label,"input":inp.strip().replace("\n"," / "),
            "expected":exp,"actual":o,"fixed_actual":o2,"hacked":o!=exp})
    rnd=random.Random(20261120); bad=[]
    for t in range(300):
        n=rnd.randint(2,30); m=rnd.randint(1,20)
        dirs=[rnd.randint(0,1) for _ in range(n)]
        names=[f"n{i}" for i in range(n)]
        ops=[(rnd.randint(0,1),rnd.randint(1,3*n)) for _ in range(m)]
        exp=p1563_correct(n,dirs,names,ops); inp=mk1563(n,dirs,names,ops)
        o,rc=run(ex,inp); o2,rc2=run(ex2,inp)
        R["P1563_xmumv7ok"]["random_tested"]+=1
        if o!=exp:
            R["P1563_xmumv7ok"]["orig_mismatch"]+=1
            if len(bad)<4: bad.append({"input":inp.strip().replace("\n"," / "),"expected":exp,"actual":o,"fixed_actual":o2})
        if o2!=exp: R["P1563_xmumv7ok"]["fixed_mismatch"]+=1
    R["P1563_xmumv7ok"]["random_examples"]=bad

# ============================================================ P1909
def p1909_correct(n,packs):
    return min((n+a-1)//a*b for a,b in packs)
ex,err,ce=build("P1909_h8ic4o0m")
R["P1909_h8ic4o0m"]={"compile_error":err,"cases":[],"random_tested":0,"random_mismatch":0}
if ce==0:
    fixed=[("样例1",57,[(2,2),(50,30),(30,27)]),("样例2",9998,[(128,233),(128,2333),(128,666)]),
           ("样例3",9999,[(101,1111),(1,9999),(1111,9999)]),("整除",100,[(10,3),(20,5),(25,7)])]
    for label,n,packs in fixed:
        inp=f"{n}\n"+"\n".join(f"{a} {b}" for a,b in packs)+"\n"
        exp=p1909_correct(n,packs); o,rc=run(ex,inp)
        R["P1909_h8ic4o0m"]["cases"].append({"label":label,"input":inp.strip().replace("\n"," / "),"expected":exp,"actual":o,"hacked":o!=str(exp)})
    rnd=random.Random(20261120)
    for t in range(300):
        n=rnd.randint(1,10000); packs=[(rnd.randint(1,10000),rnd.randint(1,10000)) for _ in range(3)]
        inp=f"{n}\n"+"\n".join(f"{a} {b}" for a,b in packs)+"\n"
        exp=p1909_correct(n,packs); o,rc=run(ex,inp)
        R["P1909_h8ic4o0m"]["random_tested"]+=1
        if o!=str(exp): R["P1909_h8ic4o0m"]["random_mismatch"]+=1

# ============================================================ P1424
def p1424_correct(x,k):
    return sum(250 for d in range(k) if (x+d-1)%7+1 not in (6,7))
ex,err,ce=build("P1424_apqvl7bn")
R["P1424_apqvl7bn"]={"compile_error":err,"cases":[],"random_tested":0,"random_mismatch":0}
if ce==0:
    for label,x,k in [("样例",3,10),("周一开始",1,7),("周六开始",6,2),("周日开始",7,1),("大数",5,100000)]:
        exp=p1424_correct(x,k); o,rc=run(ex,f"{x} {k}\n")
        R["P1424_apqvl7bn"]["cases"].append({"label":label,"input":f"{x} {k}","expected":exp,"actual":o,"hacked":o!=str(exp)})
    rnd=random.Random(20261120)
    for t in range(200):
        x=rnd.randint(1,7); k=rnd.randint(1,2000)
        exp=p1424_correct(x,k); o,rc=run(ex,f"{x} {k}\n")
        R["P1424_apqvl7bn"]["random_tested"]+=1
        if o!=str(exp): R["P1424_apqvl7bn"]["random_mismatch"]+=1

# ============================================================ P1093
def p1093_correct(rows):
    arr=[]
    for i,(c,m,e) in enumerate(rows,1): arr.append((-(c+m+e),-c,i,c+m+e))
    arr.sort()
    return "\n".join(f"{t[2]} {t[3]}" for t in arr[:5])
ex,err,ce=build("P1093_tehqdnw3")
R["P1093_tehqdnw3"]={"compile_error":err,"cases":[],"random_tested":0,"random_mismatch":0}
if ce==0:
    fixed=[("样例1",[(90,67,80),(87,66,91),(78,89,91),(88,99,77),(67,89,64),(78,89,98)]),
           ("样例2",[(80,89,89),(88,98,78),(90,67,80),(87,66,91),(78,89,91),(88,99,77),(67,89,64),(78,89,98)])]
    for label,rows in fixed:
        inp=f"{len(rows)}\n"+"\n".join(f"{c} {m} {e}" for c,m,e in rows)+"\n"
        exp=p1093_correct(rows); o,rc=run(ex,inp)
        R["P1093_tehqdnw3"]["cases"].append({"label":label,"expected":exp.replace("\n"," / "),"actual":o.replace("\n"," / "),"hacked":o!=exp})
    rnd=random.Random(20261120)
    for t in range(200):
        n=rnd.randint(5,300)
        rows=[(rnd.randint(0,100),rnd.randint(0,100),rnd.randint(0,100)) for _ in range(n)]
        inp=f"{n}\n"+"\n".join(f"{c} {m} {e}" for c,m,e in rows)+"\n"
        exp=p1093_correct(rows); o,rc=run(ex,inp)
        R["P1093_tehqdnw3"]["random_tested"]+=1
        if o!=exp: R["P1093_tehqdnw3"]["random_mismatch"]+=1

# ============================================================ P2141
def p2141_correct(vals):
    S=set(vals); sums=set()
    for i in range(len(vals)):
        for j in range(i+1,len(vals)): sums.add(vals[i]+vals[j])
    return sum(1 for v in set(vals) if v in sums)
ex,err,ce=build("P2141_b7py0ojt")
R["P2141_b7py0ojt"]={"compile_error":err,"random_tested":0,"random_mismatch":0}
if ce==0:
    rnd=random.Random(20261120)
    for t in range(300):
        n=rnd.randint(3,100)
        vals=rnd.sample(range(1,10001),n)
        exp=p2141_correct(vals)
        inp=f"{n}\n"+" ".join(map(str,vals))+"\n"
        o,rc=run(ex,inp)
        R["P2141_b7py0ojt"]["random_tested"]+=1
        if o!=str(exp): R["P2141_b7py0ojt"]["random_mismatch"]+=1

# ============================================================ P1059 x2
def p1059_correct(vals):
    u=sorted(set(vals)); return str(len(u))+"\n"+" ".join(map(str,u))+" "
for name in ["P1059_6t0wrb4o","P1059_05bplzw1"]:
    ex,err,ce=build(name)
    R[name]={"compile_error":err,"random_tested":0,"random_mismatch":0}
    if ce: continue
    rnd=random.Random(20261120)
    for t in range(250):
        n=rnd.randint(1,100); vals=[rnd.randint(1,1000) for _ in range(n)]
        exp=p1059_correct(vals); inp=f"{n}\n"+" ".join(map(str,vals))+"\n"
        o,rc=run(ex,inp)
        R[name]["random_tested"]+=1
        if o.strip()!=exp.strip(): R[name]["random_mismatch"]+=1

# ============================================================ P1089
def p1089_correct(budgets):
    hand=0; save=0
    for i,b in enumerate(budgets,1):
        hand+=300-b
        if hand<0: return str(-i)
        save+=hand//100*100; hand%=100
    return str(hand+save*6//5)
ex,err,ce=build("P1089_1ndosdfs")
R["P1089_1ndosdfs"]={"compile_error":err,"cases":[],"random_tested":0,"random_mismatch":0}
if ce==0:
    fixed=[("样例1",[290,230,280,200,300,170,340,50,90,80,200,60]),
           ("样例2",[290,230,280,200,300,170,330,50,90,80,200,60]),
           ("全0预算",[0]*12),("全349预算",[349]*12)]
    for label,b in fixed:
        inp="\n".join(map(str,b))+"\n"; exp=p1089_correct(b); o,rc=run(ex,inp)
        R["P1089_1ndosdfs"]["cases"].append({"label":label,"expected":exp,"actual":o,"hacked":o!=exp})
    rnd=random.Random(20261120)
    for t in range(300):
        b=[rnd.randint(0,349) for _ in range(12)]
        inp="\n".join(map(str,b))+"\n"; exp=p1089_correct(b); o,rc=run(ex,inp)
        R["P1089_1ndosdfs"]["random_tested"]+=1
        if o!=exp: R["P1089_1ndosdfs"]["random_mismatch"]+=1

json.dump(R,open(os.path.join(BASE,"results.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=2)
print(json.dumps(R,ensure_ascii=False,indent=2))
