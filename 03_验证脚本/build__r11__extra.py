import os,json,subprocess,random
B="/data/workspace/luogu_hack/build/r11"
def cc(name,src):
    p=f"{B}/{name}.cpp";e=f"{B}/{name}"
    open(p,"w",encoding="utf-8").write(src)
    r=subprocess.run(["g++","-std=c++17","-O2","-o",e,p],capture_output=True,text=True)
    return e,(r.stderr[:500] if r.returncode else ""),r.returncode
def run(e,inp,t=30):
    try:
        p=subprocess.run([e],input=inp,capture_output=True,text=True,timeout=t)
        return p.stdout,p.returncode
    except subprocess.TimeoutExpired: return "<TIMEOUT>",-9
R={}

# --- 1. P3397：补 using 行 vs 原文无 using 行，编译对照 ---
BODY=r"""
#define N 1010
int n,m; int map[N][N],d[N][N];
struct node { int x1,y1,x2,y2; };
node a[N];
namespace WalkerV {
 void Read(){ scanf("%d%d",&n,&m); for(int i=1;i<=m;i++) scanf("%d%d%d%d",&a[i].x1,&a[i].y1,&a[i].x2,&a[i].y2); }
 void Solve(){ for(int i=1;i<=m;i++){ d[a[i].x1][a[i].y1]++; d[a[i].x2+1][a[i].y1]--; d[a[i].x1][a[i].y2+1]--; d[a[i].x2+1][a[i].y2+1]++; }
  for(int i=1;i<=n;i++) for(int j=1;j<=n;j++) map[i][j]=map[i][j-1]+map[i-1][j]-map[i-1][j-1]+d[i][j]; }
 void Print(){ for(int i=1;i<=n;i++) for(int j=1;j<=n;j++) printf("%d%c",map[i][j],j==n?'\n':' '); }
}
int main(){ WalkerV::Read(); WalkerV::Solve(); WalkerV::Print(); return 0; }
"""
for tag,head in [("with_using","#include<bits/stdc++.h>\nusing namespace std;\n"),
                 ("no_using","#include<bits/stdc++.h>\n")]:
    e,err,ce=cc("x3397_"+tag,head+BODY)
    R.setdefault("P3397_compile_probe",{})[tag]={"rc":ce,"error_first_line":err.split("\n")[0] if err else ""}

# --- 2. P3397 满规模 n=1000 m=1000（含 x2==n 触发 d[1001]） ---
e=cc("x3397_full","#include<bits/stdc++.h>\n"+BODY)[0]
rnd=random.Random(20261122)
n=1000;m=1000;rects=[]
for _ in range(m):
    x1=rnd.randint(1,n);x2=rnd.randint(x1,n);y1=rnd.randint(1,n);y2=rnd.randint(y1,n)
    rects.append((x1,y1,x2,y2))
# 强制塞一个贴到底边/右边角的矩形
rects.append((1,1,n,n))
inp=f"{n} {len(rects)}\n"+"".join(f"{a} {b} {c} {d}\n" for a,b,c,d in rects)
o,rc=run(e,inp,t=60)
lines=o.strip().split("\n")
# 独立校验：用二维差分反推（避免 O(n^2*m)）
g=[[0]*(n+2) for _ in range(n+2)]
for x1,y1,x2,y2 in rects:
    g[x1][y1]+=1; g[x2+1][y1]-=1; g[x1][y2+1]-=1; g[x2+1][y2+1]+=1
expected=[]
for i in range(1,n+1):
    row=[]
    for j in range(1,n+1):
        g[i][j]=g[i][j]+g[i-1][j]+g[i][j-1]-g[i-1][j-1]
        row.append(str(g[i][j]))
    expected.append(" ".join(row))
R["P3397_full_scale"]={"n":n,"m":len(rects),"rc":rc,"lines":len(lines),
    "match": "\n".join(lines)==("\n".join(expected))}

# --- 3. P1042 长输入（题面管理员附注：2501 行 × 25 字符） ---
e=cc("x1042_long",open(f"{B}/s1042.cpp",encoding="utf-8").read())[0]
rec="".join(rnd.choice("WL") for _ in range(2501*25))
inp="\n".join([rec[i:i+25] for i in range(0,len(rec),25)])+"\nE\n"
o,rc=run(e,inp,t=60)
# 独立解
res=[]
for target in (11,21):
    w=l=0
    for c in rec:
        if c=='W': w+=1
        else: l+=1
        if max(w,l)>=target and abs(w-l)>=2: res.append(f"{w}:{l}");w=l=0
    res.append(f"{w}:{l}")
    if target==11: res.append("")
R["P1042_long_input"]={"chars":len(rec),"rc":rc,"match":o.rstrip("\n")=="\n".join(res),
    "games_11":len([x for x in res[:res.index("")] if x])}

# --- 4. P1150 解法一在 k=2 极限下的 int 边界 ---
o,rc=run(f"{B}/s1150_A","100000000 2\n",t=15)
R["P1150_int_limit"]={"input":"100000000 2","expected":"199999999","actual":o.strip(),"rc":rc}

print(json.dumps(R,ensure_ascii=False,indent=2))
json.dump(R,open(f"{B}/results_extra.json","w",encoding="utf-8"),ensure_ascii=False,indent=2)
