import os,json,subprocess,random
from collections import Counter
B="/data/workspace/luogu_hack/build/r9"
def cc(name,src):
    p=f"{B}/{name}.cpp";e=f"{B}/{name}"
    open(p,"w",encoding="utf-8").write(src)
    r=subprocess.run(["g++","-std=c++17","-O2","-o",e,p],capture_output=True,text=True)
    return e,(r.stderr[:400] if r.returncode else ""),r.returncode
def run(e,inp,t=15):
    try:
        p=subprocess.run([e],input=inp,capture_output=True,text=True,timeout=t)
        return p.stdout.strip(),p.returncode
    except subprocess.TimeoutExpired:
        return "<TIMEOUT>",-9
R={}

# ---- P1102 原版（逐字） ----
ORIG=r"""
#include<bits/stdc++.h>
using namespace std;
bool cmp(const long long& a,const long long& b){ return a>b; }
long long shu[300000]={0};
int main(){
 int n,c; scanf("%d%d",&n,&c);
 for(int i=0;i<n;i++)scanf("%lld",&shu[i]);
 sort(shu,shu+n,cmp);
 int t=0,w=1; int tj,wj; int st,sw; long long sum=0;
 while(w<n){
  if(shu[t]-shu[w]>c)t++;
  if(shu[t]-shu[w]<c)w++;
  if(shu[t]-shu[w]==c){
   tj=wj=0; st=t,sw=w;
   for(int i=t;shu[i]==shu[st];i++){ tj++; t++; }
   if(c==0)wj=1;
   else for(int i=w;shu[i]==shu[sw];i++){ wj++; w++; }
   sum+=(long long)tj*(long long)wj;
  }
 }
 printf("%lld",sum); return 0;
}
"""
# 修复尝试1：只给 c==0 补 wj=tj（改一处表达式）
FIX1=ORIG.replace("if(c==0)wj=1;","if(c==0){wj=tj;w=t;}")
# 修复尝试2：改成标准 map 计数（重写核心）
FIX2=r"""
#include<bits/stdc++.h>
using namespace std;
int main(){
 int n; long long c; scanf("%d%lld",&n,&c);
 map<long long,long long> cnt;
 for(int i=0;i<n;i++){ long long x; scanf("%lld",&x); cnt[x]++; }
 long long ans=0;
 vector<pair<long long,long long>> v(cnt.begin(),cnt.end());
 for(auto &kv:v) ans+=kv.second*cnt[kv.first+c];
 printf("%lld",ans); return 0;
}
"""
def ok(arr,c):
    cnt=Counter(arr); return sum(cnt[x+c] for x in arr)
for tag,src in [("orig",ORIG),("fix1",FIX1),("fix2",FIX2)]:
    e,err,ce=cc(f"x_1102_{tag}",src)
    R[tag]={"compile_error":err}

if all(v.get("compile_error")=="" for v in R.values()):
    fixed=[(1,0,[5]),(2,0,[5,5]),(3,0,[5,5,5]),(1,1,[5]),(4,1,[1,2,3,4]),
           (5,0,[1,1,2,2]),(6,2,[2,2,4,4,6,6]),(3,1,[1,5,3])]
    cases=[]
    for n,c,arr in fixed:
        inp=f"{n} {c}\n"+" ".join(map(str,arr))+"\n"; exp=str(ok(arr,c))
        row={"input":f"{n} {c} / "+" ".join(map(str,arr)),"expected":exp}
        for tag in ["orig","fix1","fix2"]:
            o,rc=run(f"{B}/x_1102_{tag}",inp,t=12)
            row[tag]=o; row[tag+"_rc"]=rc
        row["hacked"]=row["orig"]!=exp
        cases.append(row)
    R["cases"]=cases
    rnd=random.Random(20261121);stats={t:{"tested":0,"mismatch":0} for t in ["orig","fix1","fix2"]}
    for _ in range(300):
        n=rnd.randint(1,60);c=rnd.randint(0,10);arr=[rnd.randint(1,30) for _ in range(n)]
        inp=f"{n} {c}\n"+" ".join(map(str,arr))+"\n";exp=str(ok(arr,c))
        for tag in ["orig","fix1","fix2"]:
            o,rc=run(f"{B}/x_1102_{tag}",inp,t=12)
            stats[tag]["tested"]+=1
            if o!=exp or rc!=0: stats[tag]["mismatch"]+=1
    R["random"]=stats

# ---- P1423 单处改动对照 ----
A=r"""
#include<iostream>
#include<limits.h>
using namespace std;
int L,R=INT_MAX,mid; double target,dist,per=2;
int main(){ cin>>target;
 while(R>=L){ mid=(L+R)/2;
  for(int i=1;i<=mid;i++){ dist+=per; per*=0.98; __IN__ break; }
  __OUT__
  dist=0; per=2; }
 cout<<L; return 0; }
"""
variants={
 "orig":("if(dist>target)","if(dist>target) R=mid-1; else L=mid+1;"),
 "only_inner":("if(dist>=target)","if(dist>target) R=mid-1; else L=mid+1;"),
 "only_outer":("if(dist>target)","if(dist>=target) R=mid-1; else L=mid+1;"),
 "both":("if(dist>=target)","if(dist>=target) R=mid-1; else L=mid+1;"),
}
for tag,(inn,out) in variants.items():
    src=A.replace("__IN__",inn).replace("__OUT__",out)
    e,err,ce=cc("y_1423_"+tag,src)
    if ce: R.setdefault("P1423_variants",{})[tag]={"compile_error":err}; continue
    rows=[]
    for s in ["2","3.96","5.8808","4.3","10","99.9"]:
        d=0.0;per=2.0;ans=0
        while d<float(s)-1e-12:
            d+=per;per*=0.98;ans+=1
        o,rc=run(e,s+"\n",t=12)
        rows.append({"s":s,"expected":ans,"actual":o,"rc":rc})
    R.setdefault("P1423_variants",{})[tag]=rows

# ---- 差点误判：P1914「超过 z 减一次 26」在题面 n<=26 内是否真错 ----
P1914=r"""
#include<bits/stdc++.h>
using namespace std;
int main(){ int n; string a; cin>>n>>a;
 for(int i=0;i<(int)a.size();i++){
  if(a[i]+n>'z') a[i]+=n-26; else a[i]+=n;
 }
 cout<<a; return 0; }
"""
e,err,ce=cc("z_1914",P1914)
if ce: R["P1914_sub26"]={"compile_error":err}
else:
    bad=0;ex=[]
    for n in range(1,27):
        for c in "abcdefghijklmnopqrstuvwxyz":
            exp=chr(ord('a')+(ord(c)-ord('a')+n)%26)
            o,rc=run(e,f"{n}\n{c}\n")
            if o!=exp:
                bad+=1
                if len(ex)<4: ex.append({"n":n,"c":c,"expected":exp,"actual":o})
    R["P1914_sub26"]={"tested":26*26,"mismatch":bad,"examples":ex}

print(json.dumps(R,ensure_ascii=False,indent=2))
json.dump(R,open(f"{B}/results_extra.json","w",encoding="utf-8"),ensure_ascii=False,indent=2)
