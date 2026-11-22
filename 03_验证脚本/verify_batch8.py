#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第 8 批验证（三类口径）
补最小外壳后只验核心逻辑；搜索摘要 != 正文；片段取不全回原文复核。
逐字源码：
  P1098 l9bmtvor  https://www.luogu.com/article/l9bmtvor
  P1044 g17kwzzm  https://www.luogu.com/article/g17kwzzm  (两块)
  P1044 rlz2fzsx  https://www.luogu.com/article/rlz2fzsx
  P1067 hu58r34f  https://www.luogu.com/article/hu58r34f
  P1028 a1sc0wom  https://www.luogu.com/article/a1sc0wom
"""
import os, json, random, subprocess, math

BASE = "/data/workspace/luogu_hack/build/r8"
os.makedirs(BASE, exist_ok=True)
R = {}

def cc(name, src):
    p=os.path.join(BASE,name+".cpp"); e=os.path.join(BASE,name)
    open(p,"w",encoding="utf-8").write(src)
    r=subprocess.run(["g++","-std=c++17","-O2","-o",e,p],capture_output=True,text=True)
    return e,(r.stderr[:600] if r.returncode else ""),r.returncode

def run(e,inp,t=30):
    p=subprocess.run([e],input=inp,capture_output=True,text=True,timeout=t)
    return p.stdout,p.returncode

# =====================================================================
# A. P1098 l9bmtvor —— 逐字取回的完整代码
# =====================================================================
L9 = r"""
#include<bits/stdc++.h>
using namespace std;
int main(){
 int p1,p2,p3,l,k;
 string s; char x,y;
 cin>>p1>>p2>>p3;
 cin>>s;
 l=s.size();
 cout<<s[0];
 for(int t=1;t<l-1;++t){
  char a=s[t-1],b=s[t+1];
  if(p3==2){ x=b-1; y=a; k=-1; }
  else { x=a+1; y=b; k=1; }
  if(s[t]=='-'&&s[t-1]<s[t+1]&&p3==1){
   if(a>='a'&&a<='z'&&b>='a'&&b<='z'){
    if(p1==1){ for(char i=x;i<y&&k==1||i>y&&k==-1;i+=k){ for(int j=1;j<=p2;++j) cout<<char(i); } }
    else if(p1==2){ for(char i=x;i<y&&k==1||i>y&&k==-1;i+=k){ for(int j=1;j<=p2;++j) cout<<char(i-'a'+'A'); } }
    else if(p1==3){ for(char i=x;i<y&&k==1||i>y&&k==-1;i+=k){ for(int j=1;j<=p2;++j) cout<<"*"; } }
   }
   else if(a>='0'&&a<='9'&&b>='0'&&b<='9'){
    if(p1==3){ for(char i=x;i<y&&k==1||i>y&&k==-1;i+=k){ for(int j=1;j<=p2;++j) cout<<"*"; } }
    else { for(char i=x;i<y&&k==1||i>y&&k==-1;i+=k){ for(int j=1;j<=p2;++j) cout<<char(i); } }
   }
   else cout<<"-";
  }
  else cout<<s[t];
 }
 cout<<s[l-1];
 return 0;
}
"""
# 修复版 1：只删掉 "&&p3==1"
L9_FIX1 = L9.replace("if(s[t]=='-'&&s[t-1]<s[t+1]&&p3==1){","if(s[t]=='-'&&s[t-1]<s[t+1]){")
# 修复版 2：再补 l==1 特判（改两处）
L9_FIX2 = L9_FIX1.replace("cout<<s[0];", "cout<<s[0];\n if(l==1) return 0;")

def ok1098(s,p1,p2,p3):
    out=[]; L=len(s)
    for i,ch in enumerate(s):
        if ch!='-': out.append(ch); continue
        if i==0 or i==L-1: out.append('-'); continue
        a,b=s[i-1],s[i+1]
        sd = ('0'<=a<='9') and ('0'<=b<='9')
        sa = ('a'<=a<='z') and ('a'<=b<='z')
        if not (sd or sa): out.append('-'); continue
        if b<=a: out.append('-'); continue
        cs=[chr(c) for c in range(ord(a)+1,ord(b))]
        if p1==3: cs=['*']*len(cs)
        elif p1==2 and sa: cs=[c.upper() for c in cs]
        if p3==2: cs=list(reversed(cs))
        out.append(''.join(c*p2 for c in cs))
    return ''.join(out)

for tag,src in [("orig",L9),("fix1",L9_FIX1),("fix2",L9_FIX2)]:
    e,err,ce=cc("a_l9_"+tag,src)
    R.setdefault("P1098_l9bmtvor",{})[tag]={"compile_error":err}

if all(v.get("compile_error")=="" for v in R["P1098_l9bmtvor"].values()):
    fixed=[
      ("官方样例1",1,2,1,"abcs-w1234-9s-4zz"),
      ("官方样例2",2,3,2,"a-d-d"),
      ("p3=2 纯字母",1,2,2,"d-h"),
      ("p3=2 数字",1,2,2,"1-5"),
      ("后继只删减号",1,2,1,"d-e"),
      ("不展开保留减号",1,2,1,"d-d"),
      ("混合类型",1,2,1,"s-4"),
      ("长度1",1,2,1,"a"),
      ("长度2",1,2,1,"a-"),
      ("p1=3 p3=2",3,2,2,"a-d"),
    ]
    cases=[]
    for label,p1,p2,p3,s in fixed:
        exp=ok1098(s,p1,p2,p3); inp=f"{p1} {p2} {p3}\n{s}\n"
        row={"label":label,"input":f"{p1} {p2} {p3} / {s}","expected":exp}
        for tag in ["orig","fix1","fix2"]:
            o,rc=run(f"{BASE}/a_l9_{tag}",inp)
            row[tag]=o
        row["hacked"]=row["orig"]!=exp
        cases.append(row)
    R["P1098_l9bmtvor"]["cases"]=cases
    rnd=random.Random(20261121)
    stats={t:{"tested":0,"mismatch":0,"examples":[]} for t in ["orig","fix1","fix2"]}
    alpha="abcdefghijklmnopqrstuvwxyz0123456789-"
    for _ in range(400):
        p1=rnd.randint(1,3);p2=rnd.randint(1,8);p3=rnd.randint(1,2)
        L=rnd.randint(1,30); s="".join(rnd.choice(alpha) for _ in range(L))
        exp=ok1098(s,p1,p2,p3); inp=f"{p1} {p2} {p3}\n{s}\n"
        for tag in ["orig","fix1","fix2"]:
            o,rc=run(f"{BASE}/a_l9_{tag}",inp)
            stats[tag]["tested"]+=1
            if o!=exp:
                stats[tag]["mismatch"]+=1
                if len(stats[tag]["examples"])<4: stats[tag]["examples"].append({"input":inp.strip().replace("\n"," / "),"expected":exp,"actual":o})
    R["P1098_l9bmtvor"]["random"]=stats

# =====================================================================
# B. P1044 g17kwzzm 两块
# =====================================================================
G1 = r"""
#include<bits/stdc++.h>
using namespace std;
int f[1001];
int main(){ int n; scanf("%d",&n);
 f[0]=1;
 for(int i=1;i<=n;i++) for(int j=1;j<=i;j++) f[i]+=f[j-1]*f[i-j];
 printf("%d\n",f[n]); return 0; }
"""
G2 = r"""
#include<bits/stdc++.h>
using namespace std;
const int N = 100;
int dp[N][N],n;
int main(){
 dp[1][1]=1; scanf("%d",&n);
 for (int i=2;i<=n*2;i++)
  for (int j=0;j<=min(n,i);j++){
   if (j==0) dp[i][j]=dp[i-1][1];
   else { if (j==min(n,i)) dp[i][j]=dp[i-1][i-1]; else dp[i][j]=dp[i-1][j-1]+dp[i-1][j+1]; }
  }
 printf("%d\n",dp[2*n][0]);
 return 0;
}
"""
def catalan(n): return math.comb(2*n,n)//(n+1)
for tag,src in [("block1_catalan",G1),("block2_dp",G2)]:
    e,err,ce=cc("b_g17_"+tag,src)
    if ce: R.setdefault("P1044_g17kwzzm",{})[tag]={"compile_error":err}; continue
    rows=[]
    for n in range(1,19):
        o,rc=run(e,f"{n}\n"); exp=str(catalan(n))
        rows.append({"n":n,"expected":exp,"actual":o.strip(),"hacked":o.strip()!=exp})
    R.setdefault("P1044_g17kwzzm",{})[tag]={"cases":rows,"mismatch":sum(1 for r in rows if r["hacked"])}

# =====================================================================
# C. P1044 rlz2fzsx 递归记忆化（a[36][18]）
# =====================================================================
RLZ = r"""
#include<bits/stdc++.h>
using namespace std;
int n;
int a[36][18];
int f(int p,int s){
 int aa=0;
 if(p==n*2){ if(s!=0) return 0; else return 1; }
 if(a[p][s]!=0) return a[p][s];
 if(s>0) aa+=f(p+1,s-1);
 aa+=f(p+1,s+1);
 a[p][s]=aa;
 return a[p][s];
}
int main(){ cin>>n; cout<<f(0,0); return 0; }
"""
# 仅把第二维 18 改成 40
RLZ_WIDE = RLZ.replace("int a[36][18];","int a[36][40];")
for tag,src in [("orig",RLZ),("wide",RLZ_WIDE)]:
    e,err,ce=cc("c_rlz_"+tag,src)
    R.setdefault("P1044_rlz2fzsx",{})[tag]={"compile_error":err}
if all(v.get("compile_error")=="" for v in R["P1044_rlz2fzsx"].values()):
    rows=[]
    for n in range(1,19):
        o,rc=run(f"{BASE}/c_rlz_orig",f"{n}\n",t=20)
        w,rc2=run(f"{BASE}/c_rlz_wide",f"{n}\n",t=20)
        exp=str(catalan(n))
        rows.append({"n":n,"expected":exp,"orig":o.strip(),"orig_rc":rc,"wide":w.strip(),"hacked":o.strip()!=exp})
    R["P1044_rlz2fzsx"]["cases"]=rows
    R["P1044_rlz2fzsx"]["mismatch"]=sum(1 for r in rows if r["hacked"])

# =====================================================================
# D. P1067 hu58r34f
# =====================================================================
H58 = r"""
#include<bits/stdc++.h>
#define unique2648 return
#define code 0
using namespace std;
int main(){
 int n,x; cin >> n;
 for (int i = n;i >= 0;i--){ cin >> x;
  if (x!=0){
   if (x>0&&i!=n){ cout << "+"; }
   if (abs(x)!=1||i==0){ cout << x; }
   else if(x==-1) cout << "-";
   if (i>=2) cout << "x^" << i;
   else if (i==1) cout << "x";
  }
 }
 unique2648 code;
}
"""
e,err,ce=cc("d_h58",H58)
R["P1067_hu58r34f"]={"compile_error":err}
if not ce:
    def ok1067(coeffs):
        n=len(coeffs)-1; parts=[]
        for i in range(n,-1,-1):
            x=coeffs[n-i]  # 输入顺序是 an..a0
            x=coeffs[n-i]
        return None
    def ok(coeffs):
        # coeffs: [an, a(n-1), ..., a0]
        n=len(coeffs)-1; out=""
        for idx,x in enumerate(coeffs):
            i=n-idx
            if x==0: continue
            if x>0 and idx!=0: out+="+"
            if abs(x)!=1 or i==0: out+=str(x)
            elif x==-1: out+="-"
            if i>=2: out+=f"x^{i}"
            elif i==1: out+="x"
        return out
    fixed=[("样例1",[100,-1,1,-3,0,10]),("样例2",[-50,0,0,1]),
           ("n=0 仅常数",[5]),("n=0 常数1",[1]),("n=0 常数-1",[-1]),
           ("系数1高次",[1,0,1]),("全零中间",[2,0,0,0,3])]
    cases=[]
    for label,cs in fixed:
        n=len(cs)-1; inp=f"{n}\n"+" ".join(map(str,cs))+"\n"
        exp=ok(cs); o,rc=run(e,inp)
        cases.append({"label":label,"input":inp.strip().replace("\n"," / "),"expected":exp,"actual":o,"hacked":o!=exp})
    R["P1067_hu58r34f"]["cases"]=cases
    rnd=random.Random(20261121); mism=0; ex=[]
    for t in range(300):
        n=rnd.randint(0,100); cs=[rnd.randint(-100,100) for _ in range(n+1)]
        cs[0]=rnd.choice([x for x in range(-100,101) if x!=0])
        exp=ok(cs); inp=f"{n}\n"+" ".join(map(str,cs))+"\n"
        o,rc=run(e,inp)
        if o!=exp:
            mism+=1
            if len(ex)<4: ex.append({"expected":exp,"actual":o})
    R["P1067_hu58r34f"].update({"random_tested":300,"mismatch":mism,"examples":ex})

# =====================================================================
# E. P1028 a1sc0wom 递推版
# =====================================================================
A1 = r"""
#include<bits/stdc++.h>
using namespace std;
int main(){ int n,cnt=1,i,f[1010];
 f[0]=f[1]=1; scanf("%d",&n);
 for(i=2;i<=n;i++){ if(i%2==0){ f[i]=f[i-1]+f[i/2]; } else { f[i]=f[i-1]; } }
 printf("%d\n",f[n]); return 0; }
"""
e,err,ce=cc("e_a1",A1)
R["P1028_a1sc0wom"]={"compile_error":err}
if not ce:
    F=[0]*1001;F[0]=F[1]=1
    for i in range(2,1001): F[i]=F[i-1]+(F[i//2] if i%2==0 else 0)
    mism=0;ex=[]
    for n in range(1,1001):
        o,rc=run(e,f"{n}\n")
        if o.strip()!=str(F[n]):
            mism+=1
            if len(ex)<4:ex.append({"n":n,"expected":F[n],"actual":o.strip()})
    R["P1028_a1sc0wom"].update({"full_range_tested":1000,"mismatch":mism,"examples":ex})

json.dump(R,open(os.path.join(BASE,"results.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=2)
print(json.dumps(R,ensure_ascii=False,indent=2))
