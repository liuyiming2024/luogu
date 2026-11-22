#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第 10 批验证（三类口径）
补最小外壳后只验核心逻辑；搜索摘要 != 正文；片段先回原文逐字复核。
逐字源码：
  P1152 h7y41tog   https://www.luogu.com/article/h7y41tog
  P1200 ictzayja   https://www.luogu.com/article/ictzayja
  P1200 vckbob2z   https://www.luogu.com/article/vckbob2z   (Pascal，按等价逻辑验)
  P1424 apqvl7bn   https://www.luogu.com/article/apqvl7bn
  P1425 nobyk23w   https://www.luogu.com/article/nobyk23w   (C 版 + C++ 版)
  P1425 beuv9jew   https://www.luogu.com/article/beuv9jew
  P1055 kfg4ugka   https://www.luogu.com/article/kfg4ugka
  P1179 59x93a43   https://www.luogu.com/article/59x93a43   (仅验作者标注的 AC 版)
  P1059 6t0wrb4o   https://www.luogu.com/article/6t0wrb4o
"""
import os, json, random, subprocess, itertools

BASE = "/data/workspace/luogu_hack/build/r10"
os.makedirs(BASE, exist_ok=True)
R = {}

def cc(name, src, gcc=False):
    ext = ".c" if gcc else ".cpp"
    p = os.path.join(BASE, name + ext); e = os.path.join(BASE, name)
    open(p, "w", encoding="utf-8").write(src)
    r = subprocess.run(["gcc" if gcc else "g++", "-std=c++17" if not gcc else "-std=c11",
                        "-O2", "-o", e, p], capture_output=True, text=True)
    return e, (r.stderr[:700] if r.returncode else ""), r.returncode

def run(exe, inp, t=20, python=False):
    cmd = ["python3", exe] if python else [exe]
    try:
        p = subprocess.run(cmd, input=inp, capture_output=True, text=True, timeout=t)
        return p.stdout.strip(), p.returncode, p.stderr[:300]
    except subprocess.TimeoutExpired:
        return "<TIMEOUT>", -9, ""

# =====================================================================
# A. P1152 h7y41tog —— bool vis[10000005] 栈数组 + dif 可达 2e8
# =====================================================================
H7 = r"""
#include <iostream>
#include <algorithm>
#include <cstdlib>
using namespace std;
int main() {
    int n, a[1005];
    cin >> n;
    if (n == 1) { cout << "Jolly"; return 0; }
    for (int i = 1; i <= n; i++) cin >> a[i];
    int dif[1005];
    for (int i = 1; i <= n - 1; i++) dif[i] = abs(a[i + 1] - a[i]);
    sort(dif + 1, dif + n);
    bool vis[10000005] = { 0 };
    for (int i = 1; i <= n - 1; i++) vis[dif[i]] = 1;
    for (int i = 1; i <= n - 1; i++) {
        if (!vis[i]) { cout << "Not jolly" << endl; return 0; }
    }
    cout << "Jolly" << endl;
    return 0;
}
"""
# 修复版：排序后逐一比对 + while(cin>>n) 多组（重写核心，非改一处）
H7_FIX = r"""
#include <bits/stdc++.h>
using namespace std;
int main(){
    int n;
    while(cin>>n){
        vector<long long> a(n);
        for(auto &x:a) cin>>x;
        if(n==1){ cout<<"Jolly\n"; continue; }
        vector<long long> d;
        for(int i=0;i<n-1;i++) d.push_back(llabs(a[i+1]-a[i]));
        sort(d.begin(),d.end());
        bool ok=true;
        for(int i=0;i<n-1;i++) if(d[i]!=i+1){ ok=false; break; }
        cout<<(ok?"Jolly":"Not jolly")<<"\n";
    }
    return 0;
}
"""
def ok1152(arr):
    n=len(arr)
    if n==1: return "Jolly"
    d=sorted(abs(arr[i+1]-arr[i]) for i in range(n-1))
    return "Jolly" if d==list(range(1,n)) else "Not jolly"

for tag,src in [("orig",H7),("fix",H7_FIX)]:
    e,err,ce=cc("a_1152_"+tag,src)
    R.setdefault("P1152_h7y41tog",{})[tag]={"compile_error":err}

if all(v.get("compile_error")=="" for v in R["P1152_h7y41tog"].values()):
    fixed=[
      ("官方样例1", [1,4,2,3]),
      ("官方样例2", [1,4,2,-1,6]),
      ("n=1", [7]),
      ("大差仍在vis内", [0,10000000]),
      ("diff=10000005 越界", [0,10000005]),
      ("diff=2e8 越界", [0,200000000]),
      ("负值大差", [-100000000,100000000]),
      ("Jolly 常规", [1,2,4,7,11]),
      ("Not jolly 重复差", [1,4,2,3,1]),
    ]
    cases=[]
    for label,arr in fixed:
        n=len(arr); inp=f"{n}\n"+" ".join(map(str,arr))+"\n"
        exp=ok1152(arr)
        o,rc,_=run(f"{BASE}/a_1152_orig",inp,t=15)
        w,rc2,_=run(f"{BASE}/a_1152_fix",inp,t=15)
        cases.append({"label":label,"input":inp.strip().replace("\n"," / "),"expected":exp,
                      "actual":o,"orig_rc":rc,"fix_actual":w,"hacked":o!=exp or rc!=0})
    R["P1152_h7y41tog"]["cases"]=cases
    rnd=random.Random(20261121)
    stats={t:{"tested":0,"mismatch":0,"examples":[]} for t in ["orig","fix"]}
    for _ in range(200):
        n=rnd.randint(1,12)
        arr=[rnd.choice([rnd.randint(-5,5),rnd.randint(-100000000,100000000)]) for _ in range(n)]
        inp=f"{n}\n"+" ".join(map(str,arr))+"\n"
        exp=ok1152(arr)
        for tag in ["orig","fix"]:
            o,rc,_=run(f"{BASE}/a_1152_{tag}",inp,t=15)
            stats[tag]["tested"]+=1
            if o!=exp or rc!=0:
                stats[tag]["mismatch"]+=1
                if len(stats[tag]["examples"])<4:
                    stats[tag]["examples"].append({"input":inp.strip().replace("\n"," / "),"expected":exp,"actual":o,"rc":rc})
    R["P1152_h7y41tog"]["random"]=stats
    # 多组输入（官方题面「每组测试数据」）
    multi="4\n1 4 2 3\n5\n1 4 2 -1 6\n1\n9\n"
    mo,mrc,_=run(f"{BASE}/a_1152_orig",multi,t=15)
    mf,mrc2,_=run(f"{BASE}/a_1152_fix",multi,t=15)
    R["P1152_h7y41tog"]["multi_group"]={"input":multi.strip().replace("\n"," / "),
        "expected":"Jolly / Not jolly / Jolly","orig":mo,"orig_rc":mrc,"fix":mf,"fix_rc":mrc2}

# =====================================================================
# B. P1200 ictzayja（C++，不逐步取模）
# =====================================================================
ICT = r"""
#include<bits/stdc++.h>
using namespace std;
int main(){
 string s1, s2; int cnt1 = 1, cnt2 = 1;
 cin >> s1 >> s2;
 for (size_t i = 0; i < s1.size(); i++) cnt1 *= s1[i] - 'A' + 1;
 for (size_t i = 0; i < s2.size(); i++) cnt2 *= s2[i] - 'A' + 1;
 if (cnt1 % 47 == cnt2 % 47) cout << "GO";
 else cout << "STAY";
 return 0;
}
"""
def ok1200(a,b):
    def p(s):
        r=1
        for c in s: r*=ord(c)-64
        return r%47
    return "GO" if p(a)==p(b) else "STAY"
e,err,ce=cc("b_1200_ict",ICT)
R["P1200_ictzayja"]={"compile_error":err}
if not ce:
    cases=[("官方样例1","COMETQ","HVNGAT"),("官方样例2","ABSTAR","USACO"),
           ("全Z 6位","ZZZZZZ","ZZZZZZ"),("全A 6位","AAAAAA","AAAAAA"),
           ("单字母","A","A"),("Z vs A","Z","A")]
    rows=[]
    for label,a,b in cases:
        inp=f"{a}\n{b}\n"; exp=ok1200(a,b); o,rc,_=run(e,inp)
        rows.append({"label":label,"input":f"{a} / {b}","expected":exp,"actual":o,"hacked":o!=exp})
    R["P1200_ictzayja"]["cases"]=rows
    rnd=random.Random(20261121); mism=0; ex=[]; tested=0; maxprod=0
    for _ in range(300):
        a="".join(rnd.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(rnd.randint(1,6)))
        b="".join(rnd.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(rnd.randint(1,6)))
        prod=1
        for c in a: prod*=ord(c)-64
        maxprod=max(maxprod,prod)
        inp=f"{a}\n{b}\n"; exp=ok1200(a,b); o,rc,_=run(e,inp); tested+=1
        if o!=exp:
            mism+=1
            if len(ex)<4: ex.append({"input":f"{a} / {b}","expected":exp,"actual":o})
    R["P1200_ictzayja"].update({"random_tested":tested,"mismatch":mism,"max_product_seen":maxprod,
                                 "int_max":2147483647,"examples":ex})

# =====================================================================
# C. P1200 vckbob2z（Pascal，按等价逻辑用 Python 复刻验证）
# =====================================================================
def pascal1200(a,b):
    def p(s):
        x=1
        for c in s: x=(x*(ord(c)-64))%47
        return x
    return "GO" if p(a)==p(b) else "STAY"
rnd=random.Random(20261121); mism=0; tested=0
for _ in range(300):
    a="".join(rnd.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(rnd.randint(1,6)))
    b="".join(rnd.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(rnd.randint(1,6)))
    tested+=1
    if pascal1200(a,b)!=ok1200(a,b): mism+=1
R["P1200_vckbob2z"]={"note":"Pascal 逐步 mod 47，按等价逻辑复刻验证（非 g++ 编译）",
                      "random_tested":tested,"mismatch":mism}

# =====================================================================
# D. P1424 apqvl7bn
# =====================================================================
APQ = r"""
#include<bits/stdc++.h>
using namespace std;
int main(){
    int n,k,s=0;
    scanf("%d %d",&n,&k);
    for(int i=1;i<=k;i++){
        if(n!=6 && n!=7) s+=250;
        if(n==7) n=1;
        else n++;
    }
    printf("%d",s);
    return 0;
}
"""
def ok1424(x,k):
    s=0; w=x
    for _ in range(k):
        if w not in (6,7): s+=250
        w = 1 if w==7 else w+1
    return s
e,err,ce=cc("d_1424",APQ)
R["P1424_apqvl7bn"]={"compile_error":err}
if not ce:
    cases=[(3,1),(6,1),(7,1),(1,7),(1,14),(5,30),(1,1000000),(7,1000000)]
    rows=[]
    for x,k in cases:
        inp=f"{x} {k}\n"; exp=str(ok1424(x,k)); o,rc,_=run(e,inp,t=30)
        rows.append({"input":f"{x} {k}","expected":exp,"actual":o,"hacked":o!=exp})
    R["P1424_apqvl7bn"]["cases"]=rows
    rnd=random.Random(20261121); mism=0; tested=0
    for _ in range(200):
        x=rnd.randint(1,7); k=rnd.randint(1,10000)
        inp=f"{x} {k}\n"; exp=str(ok1424(x,k)); o,rc,_=run(e,inp,t=20); tested+=1
        if o!=exp: mism+=1
    R["P1424_apqvl7bn"].update({"random_tested":tested,"mismatch":mism})

# =====================================================================
# E. P1425 nobyk23w（C 版 + C++ 版，逐字）
# =====================================================================
NOB_C = r"""
#include<stdio.h>
int w_time(int sh,int sm,int eh,int em)
{
	int startm,endm,usem;
	startm=sh*60+sm;
	endm=eh*60+em;
	usem=endm-startm;
	return usem;
}
int main()
{
	int sh,sm,eh,em,uset,useh,usem;
	scanf("%d%d%d%d",&sh,&sm,&eh,&em);
	uset=w_time(sh,sm,eh,em);
	useh=uset/60;
	usem=uset%60;
	printf("%d %d",useh,usem);
	return 0;
}
"""
NOB_CPP = r"""
#include<iostream>
using namespace std;
int w_time(int sh,int sm,int eh,int em)
{
	int startm,endm,usem;
	startm=sh*60+sm;
	endm=eh*60+em;
	usem=endm-startm;
	return usem;
}
int main()
{
	int sh,sm,eh,em,uset,useh,usem;
	cin>>sh>>sm>>eh>>em;
	uset=w_time(sh,sm,eh,em);
	useh=uset/60;
	usem=uset%60;
	cout<<useh<<" "<<usem;
	return 0;
}
"""
def ok1425(a,b,c,d):
    t=(c*60+d)-(a*60+b)
    return f"{t//60} {t%60}"
for tag,src,gcc in [("c",NOB_C,True),("cpp",NOB_CPP,False)]:
    e,err,ce=cc("e_1425_nob_"+tag,src,gcc=gcc)
    R.setdefault("P1425_nobyk23w",{})[tag]={"compile_error":err}
if all(v.get("compile_error")=="" for v in R["P1425_nobyk23w"].values()):
    fixed=[(12,50,19,10),(0,0,23,59),(1,0,1,0),(1,59,2,0),(1,30,3,45),(0,59,1,0)]
    cases=[]
    rnd=random.Random(20261121); stats={t:{"tested":0,"mismatch":0} for t in ["c","cpp"]}
    for a,b,c,d in fixed:
        inp=f"{a} {b} {c} {d}\n"; exp=ok1425(a,b,c,d)
        row={"input":f"{a} {b} {c} {d}","expected":exp}
        for tag in ["c","cpp"]:
            o,rc,_=run(f"{BASE}/e_1425_nob_{tag}",inp); row[tag]=o
        row["hacked"]=row["c"]!=exp or row["cpp"]!=exp
        cases.append(row)
    R["P1425_nobyk23w"]["cases"]=cases
    for _ in range(200):
        a=rnd.randint(0,12); b=rnd.randint(0,59)
        c=rnd.randint(a,23); d=rnd.randint(0,59)
        if c*60+d<=a*60+b: continue
        inp=f"{a} {b} {c} {d}\n"; exp=ok1425(a,b,c,d)
        for tag in ["c","cpp"]:
            o,rc,_=run(f"{BASE}/e_1425_nob_{tag}",inp)
            stats[tag]["tested"]+=1
            if o!=exp: stats[tag]["mismatch"]+=1
    R["P1425_nobyk23w"]["random"]=stats

# =====================================================================
# F. P1425 beuv9jew
# =====================================================================
BEU = r"""
#include<bits/stdc++.h>
using namespace std;
int main(){
	int a,b,c,d;
	cin>>a>>b>>c>>d;
	int x,y;
	if(d>=b){ y=d-b; }
	else{ d+=60; y=d-b; c--; }
	x=c-a;
	cout<<x<<" "<<y;
	return 0;
}
"""
e,err,ce=cc("f_1425_beu",BEU)
R["P1425_beuv9jew"]={"compile_error":err}
if not ce:
    fixed=[(12,50,19,10),(0,0,23,59),(1,0,1,0),(1,59,2,0),(1,30,3,45),(0,59,1,0)]
    cases=[]
    for a,b,c,d in fixed:
        inp=f"{a} {b} {c} {d}\n"; exp=ok1425(a,b,c,d); o,rc,_=run(e,inp)
        cases.append({"input":f"{a} {b} {c} {d}","expected":exp,"actual":o,"hacked":o!=exp})
    R["P1425_beuv9jew"]["cases"]=cases
    rnd=random.Random(20261121); mism=0; tested=0
    for _ in range(300):
        a=rnd.randint(0,12); b=rnd.randint(0,59)
        c=rnd.randint(a,23); d=rnd.randint(0,59)
        if c*60+d<=a*60+b: continue
        inp=f"{a} {b} {c} {d}\n"; exp=ok1425(a,b,c,d); o,rc,_=run(e,inp); tested+=1
        if o!=exp: mism+=1
    R["P1425_beuv9jew"].update({"random_tested":tested,"mismatch":mism})

# =====================================================================
# G. P1055 kfg4ugka —— scanf %1d 配 long long*（UB 自查）
# =====================================================================
KFG = r"""
#include<bits/stdc++.h>
using namespace std;
char j;
long long int a,b,c,d,e,f,g,h,i,k,l;
int main(){
    scanf("%1d-%1d%1d%1d-%1d%1d%1d%1d%1d-%c",&a,&b,&c,&d,&e,&f,&g,&h,&i,&j);
    k=(a*1+b*2+c*3+d*4+e*5+f*6+g*7+h*8+i*9)%11;
    if(j=='X') l=10; else l=j-'0';
    if(k==l) cout<<"Right";
    else if(k==10) cout<<a<<"-"<<b<<c<<d<<"-"<<e<<f<<g<<h<<i<<"-X";
    else cout<<a<<"-"<<b<<c<<d<<"-"<<e<<f<<g<<h<<i<<"-"<<k;
    return 0;
}
"""
def ok1055(s):
    digits=[int(ch) for ch in s if ch.isdigit()][:9]
    ssum=sum(digits[t]*(t+1) for t in range(9))
    code="X" if ssum%11==10 else str(ssum%11)
    correct=f"{digits[0]}-{digits[1]}{digits[2]}{digits[3]}-{digits[4]}{digits[5]}{digits[6]}{digits[7]}{digits[8]}-{code}"
    return "Right" if s[-1]==code else correct
e,err,ce=cc("g_1055",KFG)
R["P1055_kfg4ugka"]={"compile_error":err}
if not ce:
    fixed=["0-670-82162-4","0-670-82162-X","7-302-03825-4","4-000-00000-0",
           "9-999-99999-9","0-000-00000-0","1-234-56789-0"]
    cases=[]
    for s in fixed:
        exp=ok1055(s); o,rc,_=run(e,s+"\n")
        cases.append({"input":s,"expected":exp,"actual":o,"hacked":o!=exp})
    R["P1055_kfg4ugka"]["cases"]=cases
    rnd=random.Random(20261121); mism=0; ex=[]; tested=0
    for _ in range(300):
        ds=[rnd.randint(0,9) for _ in range(9)]
        ssum=sum(ds[t]*(t+1) for t in range(9)); code="X" if ssum%11==10 else str(ssum%11)
        s=f"{ds[0]}-{ds[1]}{ds[2]}{ds[3]}-{ds[4]}{ds[5]}{ds[6]}{ds[7]}{ds[8]}-{code}"
        # 一半概率故意改成错的识别码
        if rnd.random()<0.5:
            wrong=rnd.choice([c for c in "0123456789X" if c!=code])
            s=s[:-1]+wrong
        exp=ok1055(s); o,rc,_=run(e,s+"\n"); tested+=1
        if o!=exp:
            mism+=1
            if len(ex)<4: ex.append({"input":s,"expected":exp,"actual":o})
    R["P1055_kfg4ugka"].update({"random_tested":tested,"mismatch":mism,"examples":ex})

# =====================================================================
# H. P1179 59x93a43 —— 仅验作者标注的 AC 版（第二块）
# =====================================================================
S59 = r"""
#include<bits/stdc++.h>
using namespace std;
int main(){
    long long a,b,s=0,n;
    cin>>a>>b;
    for(int y=a;y<=b;y++){
        n=y;
        while(n!=0){ if(n%10==2) s++; n/=10; }
    }
    cout<<s;
    return 0;
}
"""
def ok1179(L,R):
    return str(sum(str(i).count('2') for i in range(L,R+1)))
e,err,ce=cc("h_1179",S59)
R["P1179_59x93a43"]={"compile_error":err}
if not ce:
    cases=[(2,22),(2,100),(1,1),(1,100000),(22,22),(2,2),(99990,100000)]
    rows=[]
    for L,Rr in cases:
        inp=f"{L} {Rr}\n"; exp=ok1179(L,Rr); o,rc,_=run(e,inp,t=30)
        rows.append({"input":f"{L} {Rr}","expected":exp,"actual":o,"hacked":o!=exp})
    R["P1179_59x93a43"]["cases"]=rows
    rnd=random.Random(20261121); mism=0; tested=0
    for _ in range(200):
        L=rnd.randint(1,1000); Rr=rnd.randint(L,min(100000,L+2000))
        inp=f"{L} {Rr}\n"; exp=ok1179(L,Rr); o,rc,_=run(e,inp,t=20); tested+=1
        if o!=exp: mism+=1
    R["P1179_59x93a43"].update({"random_tested":tested,"mismatch":mism})
    # 作者第一块（自曝的错例）：记录但不作为判据
    R["P1179_59x93a43"]["block1_note"]="作者标注『我编的程序是——』的第一块用 while(y!=0){y/=10} 改循环变量，会死循环；下一块明确写『AC代码应该是这样的』，按第8批 P1028 先例只验 AC 版"

# =====================================================================
# I. P1059 6t0wrb4o —— 补最小外壳（j=0）
# =====================================================================
T6 = r"""
#include<bits/stdc++.h>
using namespace std;
typedef long long ll;
const int N = 1e6+5;
int n,a[N],b[N];
int main(){
    cin>>n;
    for(int i=1;i<=n;i++) cin>>a[i];
    sort(a+1,a+1+n);
    int j=0;
    for(int i=1;i<=n;i++){
        if(a[i]!=a[i-1]){ b[++j]=a[i]; }
    }
    cout<<j<<"\n";
    for(int i=1;i<=j;i++){ cout<<b[i]<<" "; }
    return 0;
}
"""
def ok1059(arr):
    u=sorted(set(arr))
    return f"{len(u)}\n"+" ".join(map(str,u))+" "
e,err,ce=cc("i_1059",T6)
R["P1059_6t0wrb4o"]={"compile_error":err}
if not ce:
    cases=[[20,40,32,67,40,20,89,300,400,15],[1],[1,1,1],[1000,1,1000],[5,4,3,2,1]]
    rows=[]
    for arr in cases:
        inp=f"{len(arr)}\n"+" ".join(map(str,arr))+"\n"
        exp=ok1059(arr).strip(); o,rc,_=run(e,inp)
        rows.append({"input":" ".join(map(str,arr)),"expected":exp,"actual":o.strip(),"hacked":o.strip()!=exp})
    R["P1059_6t0wrb4o"]["cases"]=rows
    rnd=random.Random(20261121); mism=0; tested=0
    for _ in range(300):
        n=rnd.randint(1,100); arr=[rnd.randint(1,1000) for _ in range(n)]
        inp=f"{n}\n"+" ".join(map(str,arr))+"\n"
        exp=ok1059(arr).strip(); o,rc,_=run(e,inp); tested+=1
        if o.strip()!=exp: mism+=1
    R["P1059_6t0wrb4o"].update({"random_tested":tested,"mismatch":mism})

json.dump(R,open(os.path.join(BASE,"results.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=2)
print(json.dumps(R,ensure_ascii=False,indent=2))
