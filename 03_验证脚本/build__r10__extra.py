import os,json,subprocess,random
B="/data/workspace/luogu_hack/build/r10"
def cc(name,src):
    p=f"{B}/{name}.cpp";e=f"{B}/{name}"
    open(p,"w",encoding="utf-8").write(src)
    r=subprocess.run(["g++","-std=c++17","-O2","-o",e,p],capture_output=True,text=True)
    return e,(r.stderr[:400] if r.returncode else ""),r.returncode
def run(e,inp,t=15):
    try:
        p=subprocess.run([e],input=inp,capture_output=True,text=True,timeout=t)
        return p.stdout.strip(),p.returncode
    except subprocess.TimeoutExpired: return "<TIMEOUT>",-9
R={}

BASE=r"""
#include <bits/stdc++.h>
using namespace std;
int main(){
    int n,a[1005];
    cin>>n;
    if(n==1){ cout<<"Jolly"; return 0; }
    for(int i=1;i<=n;i++) cin>>a[i];
    int dif[1005];
    for(int i=1;i<=n-1;i++) dif[i]=abs(a[i+1]-a[i]);
    sort(dif+1,dif+n);
    __VIS__
    for(int i=1;i<=n-1;i++) vis[dif[i]]=1;
    for(int i=1;i<=n-1;i++) if(!vis[i]){ cout<<"Not jolly"<<endl; return 0; }
    cout<<"Jolly"<<endl;
    return 0;
}
"""
variants={
 "stack_10m": "bool vis[10000005] = { 0 };",                 # 逐字原文
 "static_10m": "static bool vis[10000005];",                  # 只挪到静态区
 "static_210m": "static bool vis[200000005];",                # 想把下标开够 -> 200MB
}
for tag,decl in variants.items():
    e,err,ce=cc("x_1152_"+tag,BASE.replace("__VIS__",decl))
    R[tag]={"compile_error":err}

def ok(arr):
    n=len(arr)
    if n==1: return "Jolly"
    d=sorted(abs(arr[i+1]-arr[i]) for i in range(n-1))
    return "Jolly" if d==list(range(1,n)) else "Not jolly"

if all(v.get("compile_error")=="" for v in R.values()):
    fixed=[("官方样例1",[1,4,2,3]),("官方样例2",[1,4,2,-1,6]),("n=1",[7]),
           ("大差仍在数组内",[0,10000000]),("diff=10000005",[0,10000005]),
           ("diff=2e8",[0,200000000]),("负值大差",[-100000000,100000000])]
    cases=[]
    for label,arr in fixed:
        inp=f"{len(arr)}\n"+" ".join(map(str,arr))+"\n"; exp=ok(arr)
        row={"label":label,"input":inp.strip().replace("\n"," / "),"expected":exp}
        for tag in variants:
            o,rc=run(f"{B}/x_1152_{tag}",inp,t=15)
            row[tag]=o; row[tag+"_rc"]=rc
        cases.append(row)
    R["cases"]=cases
    # 多组输入（官方题面「每组测试数据」）：static 版仍只读一组
    multi="4\n1 4 2 3\n5\n1 4 2 -1 6\n1\n9\n"
    ms,mrc=run(f"{B}/x_1152_static_10m",multi,t=15)
    R["multi_group_static"]={"input":multi.strip().replace("\n"," / "),
        "expected":"Jolly / Not jolly / Jolly","actual":ms,"rc":mrc}
    # 200MB 静态版是否 MLE（用 /usr/bin/time 粗测最大内存不可靠，这里只看能否跑完官方样例）
    o,rc=run(f"{B}/x_1152_static_210m","4\n1 4 2 3\n",t=20)
    R["static_210m_sample"]={"expected":"Jolly","actual":o,"rc":rc,"note":"静态 bool[200000005] ≈200MB，题面内存限制 125MB"}

# 独立解：排序逐一比对 + 多组（重写核心）
FIX=r"""
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
e,err,ce=cc("x_1152_fix",FIX)
if ce: R["fix"]={"compile_error":err}
else:
    rnd=random.Random(20261121);mism=0
    for _ in range(200):
        n=rnd.randint(1,12); arr=[rnd.choice([rnd.randint(-5,5),rnd.randint(-100000000,100000000)]) for _ in range(n)]
        inp=f"{n}\n"+" ".join(map(str,arr))+"\n"
        o,rc=run(e,inp,t=15)
        if o!=ok(arr) or rc!=0: mism+=1
    mo,mrc=run(e,"4\n1 4 2 3\n5\n1 4 2 -1 6\n1\n9\n",t=15)
    R["fix"]={"random_tested":200,"mismatch":mism,"multi_group":mo,"multi_rc":mrc}

print(json.dumps(R,ensure_ascii=False,indent=2))
json.dump(R,open(f"{B}/results_extra.json","w",encoding="utf-8"),ensure_ascii=False,indent=2)
