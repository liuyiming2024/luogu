#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第 7 批验证（三类口径）
补最小外壳后只验核心逻辑，不判完整度；搜索摘要 != 正文。
重点：P1421 浮点累减、P1014 float 公式、P1003 数组尺寸。
"""
import os, json, random, subprocess

BASE = "/data/workspace/luogu_hack/build/r7"
os.makedirs(BASE, exist_ok=True)
R = {}

def compile_cpp(name, src, extra=""):
    p=os.path.join(BASE,name+".cpp"); exe=os.path.join(BASE,name)
    open(p,"w",encoding="utf-8").write(src)
    r=subprocess.run(["g++","-std=c++17","-O2",extra,"-o",exe,p] if extra else
                     ["g++","-std=c++17","-O2","-o",exe,p],capture_output=True,text=True)
    return exe,(r.stderr[:500] if r.returncode else ""),r.returncode

def run(exe,inp,timeout=40):
    p=subprocess.run([exe],input=inp,capture_output=True,text=True,timeout=timeout)
    return p.stdout.strip(),p.returncode

# =====================================================================
# A. P1421 dk5mkxij —— 拆段拼装后全枚举 (a=0..10000, b=0..9)
# 题解逐字片段：double a,b; int sum=0; cin>>a>>b; b=b/10; a=a+b;
#               while(a>=1.9){ a=a-1.9; sum++; }  cout<<sum<<endl;
# =====================================================================
SRC_A = r"""
#include <bits/stdc++.h>
using namespace std;
// 题解拼装版（逐字段）
int solve_sol(int A,int B){
    double a,b; int sum=0;
    a=A; b=B;
    b=b/10;
    a=a+b;
    while(a>=1.9){ a=a-1.9; sum++; }
    return sum;
}
// 独立正确解：全部换算成角，整数除法
int solve_ok(int A,int B){ return (A*10+B)/19; }
int main(){
    int total=0,bad=0; vector<string> ex;
    for(int A=0;A<=10000;A++) for(int B=0;B<=9;B++){
        total++;
        int s=solve_sol(A,B), o=solve_ok(A,B);
        if(s!=o){ bad++; if((int)ex.size()<12){ char buf[128]; sprintf(buf,"%d %d -> sol=%d ok=%d",A,B,s,o); ex.push_back(buf); } }
    }
    printf("A|total=%d|bad=%d\n",total,bad);
    for(auto &e:ex) printf("A|%s\n",e.c_str());
    return 0;
}
"""
exe,err,ce=compile_cpp("a_p1421_enum",SRC_A)
if ce: R["P1421_dk5mkxij"]={"compile_error":err}
else:
    out,rc=run(exe,"",timeout=180)
    lines=[l for l in out.splitlines() if l.startswith("A|")]
    head=lines[0][2:] if lines else ""
    R["P1421_dk5mkxij"]={"head":head,"examples":[l[2:] for l in lines[1:]]}

# 同一篇：改一处比较符（加 eps）后是否全对 —— 判断「乙 vs 甲」
SRC_A2 = SRC_A.replace("while(a>=1.9)","while(a>=1.9-1e-9)")
exe,err,ce=compile_cpp("a_p1421_eps",SRC_A2)
if not ce:
    out,rc=run(exe,"",timeout=180)
    R["P1421_dk5mkxij"]["after_eps_fix"]=[l[2:] for l in out.splitlines() if l.startswith("A|")][:1]

# =====================================================================
# B. P1014 float 公式版 —— 1..1e7 全枚举
# =====================================================================
SRC_B = r"""
#include <bits/stdc++.h>
using namespace std;
string sol(int N){
    float n=(float)N;
    int k=int(sqrt(n*2-1.75)+0.5);
    n-=(k-1)*k/2;
    char buf[64];
    if(k%2==1) sprintf(buf,"%g/%g",(double)(k-n+1),(double)n);
    else       sprintf(buf,"%g/%g",(double)n,(double)(k-n+1));
    return string(buf);
}
string ok(int N){
    // 整数二分求最小 k 使 k(k+1)/2 >= N
    int l=1,r=5000;
    while(l<r){ int m=(l+r)/2; if((long long)m*(m+1)/2>=N) r=m; else l=m+1; }
    int k=l; int n=N-(k-1)*k/2;
    char buf[64];
    if(k%2==1) sprintf(buf,"%d/%d",k-n+1,n);
    else       sprintf(buf,"%d/%d",n,k-n+1);
    return string(buf);
}
int main(){
    long long bad=0; vector<string> ex;
    for(int N=1;N<=10000000;N++){
        string s=sol(N), o=ok(N);
        if(s!=o){ bad++; if((int)ex.size()<12){ char b[128]; sprintf(b,"N=%d -> sol=%s ok=%s",N,s.c_str(),o.c_str()); ex.push_back(b); } }
    }
    printf("B|bad=%lld\n",bad);
    for(auto &e:ex) printf("B|%s\n",e.c_str());
    return 0;
}
"""
exe,err,ce=compile_cpp("b_p1014_enum",SRC_B)
if ce: R["P1014_float"]={"compile_error":err}
else:
    out,rc=run(exe,"",timeout=300)
    lines=[l for l in out.splitlines() if l.startswith("B|")]
    R["P1014_float"]={"head":lines[0][2:] if lines else "","examples":[l[2:] for l in lines[1:]]}

# =====================================================================
# C. P1003 9jadrxl0 —— im[10020][4] 对题面 n<=1e5 是否确定性出错
# 对照：仅把 10020 改成 100005
# =====================================================================
BASE_C = r"""
#include <bits/stdc++.h>
using namespace std;
int im[__SIZE__][4];
int n,x,y,ans=-1;
int main(){
 scanf("%d",&n);
 for(int i=1;i<=n;i++) scanf("%d%d%d%d",&im[i][0],&im[i][1],&im[i][2],&im[i][3]);
 scanf("%d%d",&x,&y);
 for(int i=n;i>=1;i--){
  if(im[i][0]+im[i][2]>=x && im[i][1]+im[i][3]>=y && im[i][0]<=x && im[i][1]<=y){ ans=i; break; }
 }
 printf("%d",ans);
 return 0;
}
"""
for tag,size in [("orig","10020"),("wide","100005")]:
    exe,err,ce=compile_cpp(f"c_p1003_{tag}",BASE_C.replace("__SIZE__",size))
    R.setdefault("P1003_9jadrxl0",{})[tag]={"compile_error":err}

def mk1003(rects,qx,qy):
    lines=[str(len(rects))]
    for a,b,g,k in rects: lines.append(f"{a} {b} {g} {k}")
    lines.append(f"{qx} {qy}")
    return "\n".join(lines)+"\n"

def ok1003(rects,qx,qy):
    for i in range(len(rects)-1,-1,-1):
        a,b,g,k=rects[i]
        if a+g>=qx and b+k>=qy and a<=qx and b<=qy: return i+1
    return -1

if all(v.get("compile_error")=="" for v in R["P1003_9jadrxl0"].values()):
    rnd=random.Random(20261121)
    cases=[]
    # 关键：n > 10020，且答案落在下标 > 10020 的地毯上
    for n in [10021, 10050, 20000, 100000]:
        rects=[(200000+i*2, 200000, 1, 1) for i in range(n)]   # 都远离查询点
        rects[-1]=(0,0,qx:=5,qy:=5)  # 最后一张覆盖 (5,5)
        cases.append((f"n={n} 答案={n}",rects,5,5))
    # 普通小 n 对照
    for n in [1,5,100]:
        rects=[(rnd.randint(0,50),rnd.randint(0,50),rnd.randint(0,20),rnd.randint(0,20)) for _ in range(n)]
        cases.append((f"普通 n={n}",rects,rnd.randint(0,60),rnd.randint(0,60)))
    out=[]
    for label,rects,qx,qy in cases:
        inp=mk1003(rects,qx,qy); exp=ok1003(rects,qx,qy)
        o,rc1=run(f"{BASE}/c_p1003_orig",inp,timeout=60)
        w,rc2=run(f"{BASE}/c_p1003_wide",inp,timeout=60)
        out.append({"label":label,"expected":exp,"orig":o,"orig_rc":rc1,"wide":w,"wide_rc":rc2})
    R["P1003_9jadrxl0"]["cases"]=out

# =====================================================================
# D. 其余逐篇（补最小外壳后随机对拍）
# =====================================================================
SOLS={}
SOLS["P1425_beuv9jew"]=r"""
#include<bits/stdc++.h>
using namespace std;
int main(){ int a,b,c,d,x,y; cin>>a>>b>>c>>d;
 if(d>=b){ y=d-b; } else { d+=60; y=d-b; c--; }
 x=c-a; cout<<x<<" "<<y; return 0; }
"""
SOLS["P1425_nobyk23w"]=r"""
#include<bits/stdc++.h>
using namespace std;
int w_time(int sh,int sm,int eh,int em){ int startm,endm,usem; startm=sh*60+sm; endm=eh*60+em; usem=endm-startm; return usem; }
int main(){ int sh,sm,eh,em,uset,useh,usem; cin>>sh>>sm>>eh>>em;
 uset=w_time(sh,sm,eh,em); useh=uset/60; usem=uset%60; cout<<useh<<" "<<usem; return 0; }
"""
SOLS["P1085_3hvn4ibz"]=r"""
#include<bits/stdc++.h>
using namespace std;
int main(){ int MAX=-30,day=0,a,b;
 for(int i=1;i<=7;i++){ cin>>a>>b; if(a+b-8>MAX && a+b-8>0){ MAX=a+b-8; day=i; } }
 cout<<day; return 0; }
"""
SOLS["P1075_rjjud4hi_v3"]=r"""
#include<bits/stdc++.h>
using namespace std;
int main(){ int n; cin>>n; for(int i=2;i<=n;i++) if(n%i==0){ cout<<n/i; break; } return 0; }
"""
# P1421 整数版（搜索摘要，未取到 lid，仅作内部对照）
SOLS["P1421_int_ref"]=r"""
#include<bits/stdc++.h>
using namespace std;
int main(){ int a,b,c,sum; cin>>a>>b; sum=a*10+b; c=sum/19; cout<<c; return 0; }
"""

def ok1425(sh,sm,eh,em):
    t=(eh*60+em)-(sh*60+sm); return f"{t//60} {t%60}"
def ok1085(pairs):
    best=0;day=0
    for i,(a,b) in enumerate(pairs,1):
        s=a+b
        if s>8 and s>best: best=s; day=i
    return day
def ok1075(n):
    for i in range(2,int(n**0.5)+1):
        if n%i==0: return n//i
    return n

for name,src in SOLS.items():
    exe,err,ce=compile_cpp("d_"+name,src)
    if ce: R[name]={"compile_error":err}; continue
    rnd=random.Random(20261121); tested=0; bad=[]; mism=0
    if name.startswith("P1425"):
        for t in range(300):
            sh=rnd.randint(0,23); sm=rnd.randint(0,59)
            # 保证结束 > 开始
            dt=rnd.randint(1,1400)
            tot=sh*60+sm+dt; eh=tot//60; em=tot%60
            if eh>23: eh%=24
            tot=eh*60+em
            if tot<=sh*60+sm: continue
            exp=ok1425(sh,sm,eh,em); out,rc=run(exe,f"{sh} {sm} {eh} {em}\n")
            tested+=1
            if out!=exp: mism+=1; bad.append({"input":f"{sh} {sm} {eh} {em}","expected":exp,"actual":out})
    elif name=="P1085_3hvn4ibz":
        for t in range(300):
            pairs=[(rnd.randint(0,9),rnd.randint(0,9)) for _ in range(7)]
            exp=str(ok1085(pairs)); inp="\n".join(f"{a} {b}" for a,b in pairs)+"\n"
            out,rc=run(exe,inp)
            tested+=1
            if out!=exp: mism+=1; bad.append({"input":inp.strip().replace("\n"," / "),"expected":exp,"actual":out})
    elif name=="P1075_rjjud4hi_v3":
        primes=[2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109,113,127,131,137,139,149,151,157,163,167,173,179,181,191,193,197,199,211,223,227,229,233,239,241,251,257,263,269,271,277,281,283,293,307,311,313,317,331,337,347,349,353,359,367,373,379,383,389,397,401,409,419,421,431,433,439,443,449,457,461,463,467,479,487,491,499,503,509,521,523,541,547,557,563,569,571,577,587,593,599,601,607,613,617,619,631,641,643,647,653,659,661,673,677,683,691,701,709,719,727,733,739,743,751,757,761,769,773,787,797,809,811,821,823,827,829,839,853,857,859,863,877,881,883,887,907,911,919,929,937,941,947,953,967,971,977,983,991,997,1009,1013,1019,1021,1031,1033,1039,1049,1051,1061,1063,1069,1087,1091,1093,1097,1103,1109,1117,1123,1129,1151]
        for t in range(300):
            p,q=rnd.sample(primes,2); n=p*q
            exp=str(ok1075(n)); out,rc=run(exe,f"{n}\n")
            tested+=1
            if out!=exp: mism+=1; bad.append({"input":str(n),"expected":exp,"actual":out})
    else:
        for t in range(200):
            a=rnd.randint(0,10000); b=rnd.randint(0,9)
            exp=str((a*10+b)//19); out,rc=run(exe,f"{a} {b}\n")
            tested+=1
            if out!=exp: mism+=1; bad.append({"input":f"{a} {b}","expected":exp,"actual":out})
    R[name]={"tested":tested,"mismatch":mism,"examples":bad[:4]}

json.dump(R,open(os.path.join(BASE,"results.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=2)
print(json.dumps(R,ensure_ascii=False,indent=2))
