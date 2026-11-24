#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 15 批 · 低频补录（三类口径）
逐字源码取自 www.luogu.com/article/<lid>：
  ju6tr560 (P1424) / v5aspqez (P1909) / ngy7hblx (P1012) / a8f6uiq9 (P1328)
另 azdjstpm (P1008) 三次不同通道取回均失败 → 「登记·不计数」，不拿搜索摘要验证。
口径：题面内 + 确定性 WA/RE + 不看评测机波动；只验核心逻辑，不判代码完整度。
每篇附一个「变异版」敏感性检查：故意改一处后对拍必须抓到错，证明测试集非空跑。
"""
import os, json, random, subprocess, itertools

BASE = "/data/workspace/luogu_hack"
D = os.path.join(BASE, "build", "r15")
os.makedirs(D, exist_ok=True)
R = {}

def build(name, src):
    p = os.path.join(D, name + ".cpp")
    open(p, "w", encoding="utf-8").write(src)
    e = os.path.join(D, name)
    r = subprocess.run(["g++", "-std=gnu++17", "-O2", "-w", "-o", e, p],
                       capture_output=True, text=True, timeout=90)
    return e, r.returncode, r.stderr[:400]

def run(e, inp, t=10):
    try:
        p = subprocess.run([e], input=inp, capture_output=True, text=True, timeout=t)
        return p.stdout.strip(), p.returncode
    except subprocess.TimeoutExpired:
        return "<TIMEOUT>", -99

# ============================================================ A. P1424 ju6tr560
SRC_A = r"""#include<cstdio>
using namespace std;
int a[8]={0,250,250,250,250,250,0,0};
int x,n,cnt;
int main(){
    scanf("%d%d",&x,&n);
    int temp=n/7;
    n%=7;
    cnt+=1250*temp;
    for(int i=1;i<=n;i++){
        cnt+=a[x];
        x++;
        if(x>7)x-=7;
    }
    printf("%d",cnt);
}
"""
SRC_A_MUT = SRC_A.replace("cnt+=1250*temp;", "cnt+=1000*temp;")

# ============================================================ B. P1909 v5aspqez
SRC_B = r"""#include<cstdio>
inline int min(int x,int y){return x<y?x:y;}
int n,ans=2147483647;
int main(){
    scanf("%d",&n);
    for(int i=1;i<=3;i++){
        int a,b;
        scanf("%d%d",&a,&b);
        ans=min(ans,b*((n+a-1)/a));
    }
    printf("%d\n",ans);
}
"""
SRC_B_MUT = SRC_B.replace("(n+a-1)/a", "n/a")

# ============================================================ C. P1012 ngy7hblx
SRC_C = r"""#include <bits/stdc++.h>
using namespace std;
const int N=50;
int n;
string s[N];
bool cmp(string a,string b){
    return (a+b)>(b+a);
}
signed main(){
    cin>>n;
    for(int i=1;i<=n;i++){
        cin>>s[i];
    }
    sort(s+1,s+n+1,cmp);
    for(int i=1;i<=n;i++){
        cout<<s[i];
    }
    return 0;
}
"""
SRC_C_MUT = SRC_C.replace("return (a+b)>(b+a);", "return a>b;")

# ============================================================ D. P1328 a8f6uiq9
SCORE_LINES = "\n".join(
    f" score[{i}][{j}]={v};"
    for i, row in enumerate([
        [0,-1,1,1,-1],[1,0,-1,1,-1],[-1,1,0,-1,1],
        [-1,-1,1,0,1],[1,1,-1,-1,0]]) for j, v in enumerate(row))
SRC_D = "#include<iostream>\nusing namespace std;\nint main(){\n int score[5][5];\n" \
        + SCORE_LINES + r"""
 int n,m,k; int ans=0; int bns=0; cin>>n>>m>>k;
 int a[m+1],b[k+1];
 for(int i=1;i<=m;i++) cin>>a[i];
 for(int i=1;i<=k;i++) cin>>b[i];
 int anum=1; int bnum=1;
 for(int i=1;i<=n;i++){
   if(score[a[anum]][b[bnum]]==1) ans++;
   else if(score[a[anum]][b[bnum]]==-1) bns++;
   anum++; bnum++;
   if(anum>m){ anum=1; }
   if(bnum>k){ bnum=1; }
 }
 cout<<ans<<" "<<bns; return 0; }
"""
SRC_D_MUT = SRC_D.replace("score[0][1]=-1;", "score[0][1]=1;")

SOURCES = {
    "P1424_ju6tr560": SRC_A, "P1424_ju6tr560_mut": SRC_A_MUT,
    "P1909_v5aspqez": SRC_B, "P1909_v5aspqez_mut": SRC_B_MUT,
    "P1012_ngy7hblx": SRC_C, "P1012_ngy7hblx_mut": SRC_C_MUT,
    "P1328_a8f6uiq9": SRC_D, "P1328_a8f6uiq9_mut": SRC_D_MUT,
}
EXE = {}
for k, v in SOURCES.items():
    e, rc, err = build(k, v)
    EXE[k] = e
    R[k] = {"compile_rc": rc, "compile_err": err}
    print("BUILD", k, "rc=", rc, err[:120].replace("\n", " "))

# ---------------------------------------------------------------- 独立正确解
def p1424_correct(x, n):
    """逐天模拟全部 n 天（与题解的『整周优化 + 剩余天数』完全不同的实现）"""
    total, day = 0, x
    for _ in range(n):
        if day <= 5: total += 250
        day = day % 7 + 1
    return str(total)

def p1909_correct(n, packs):
    return str(min(b * ((n + a - 1) // a) for a, b in packs))

def p1012_bruteforce(arr):
    """n<=7 全排列暴力：所有拼接串长度相同，字典序最大即数值最大"""
    return max("".join(p) for p in itertools.permutations(arr))

def p1012_insert(arr):
    """插入法（独立构造，非 sort+cmp）：逐个把新串插到当前序列所有位置取最大"""
    seq = []
    for s in arr:
        best = None
        for i in range(len(seq) + 1):
            cand = seq[:i] + [s] + seq[i:]
            v = "".join(cand)
            if best is None or v > best[0]: best = (v, cand)
        seq = best[1]
    return "".join(seq)

# 从题面胜负关系独立构造（0剪刀 1石头 2布 3蜥蜴人 4斯波克；1=A胜 -1=B胜 0平）
RULES = [[0,-1,1,1,-1],[1,0,-1,1,-1],[-1,1,0,-1,1],
         [-1,-1,1,0,1],[1,1,-1,-1,0]]
def p1328_correct(n, A, B):
    sa = sb = 0
    for i in range(n):
        r = RULES[A[i % len(A)]][B[i % len(B)]]
        if r == 1: sa += 1
        elif r == -1: sb += 1
    return f"{sa} {sb}"

rnd = random.Random(20261124)

# ---------------------------------------------------------------- P1424 对拍
cases = [(3,10),(1,1),(5,1),(6,1),(7,1),(7,7),(1,7),(6,14),(3,1000),
         (1,1000000),(7,1000000),(3,999999)]
for _ in range(300):
    cases.append((rnd.randint(1,7), rnd.randint(1,3000)))
for name in ["P1424_ju6tr560", "P1424_ju6tr560_mut"]:
    bad = []
    for x, n in cases:
        out, rc = run(EXE[name], f"{x} {n}\n")
        exp = p1424_correct(x, n)
        if rc != 0 or out != exp:
            if len(bad) < 8:
                bad.append({"input": f"{x} {n}", "expected": exp, "actual": out[:30], "rc": rc})
    R[name].update({"tested": len(cases), "mismatch": len(bad), "examples": bad[:8]})
    print(name, "tested", len(cases), "bad", len(bad))
R["P1424_ju6tr560"]["sample_3_10"] = {
    "expected": p1424_correct(3,10),
    "actual": run(EXE["P1424_ju6tr560"], "3 10\n")[0]}

# ---------------------------------------------------------------- P1909 对拍
fixed_packs = [
    (57,[(2,2),(50,30),(30,27)]),
    (9998,[(128,233),(128,2333),(128,666)]),
    (9999,[(101,1111),(1,9999),(1111,9999)]),
    (1,[(1,10000),(1,1),(10000,10000)]),
    (10000,[(1,10000),(10000,1),(9999,10000)]),
    (10000,[(10000,10000),(10000,10000),(10000,10000)]),
]
cases = list(fixed_packs)
for _ in range(500):
    n = rnd.randint(1,10000)
    packs = [(rnd.randint(1,10000), rnd.randint(1,10000)) for _ in range(3)]
    cases.append((n, packs))
for name in ["P1909_v5aspqez", "P1909_v5aspqez_mut"]:
    bad = []
    for n, packs in cases:
        inp = f"{n}\n" + "\n".join(f"{a} {b}" for a,b in packs) + "\n"
        out, rc = run(EXE[name], inp)
        exp = p1909_correct(n, packs)
        if rc != 0 or out != exp:
            if len(bad) < 8:
                bad.append({"input": inp.strip().replace("\n"," / "),
                            "expected": exp, "actual": out[:30], "rc": rc})
    R[name].update({"tested": len(cases), "mismatch": len(bad), "examples": bad[:8]})
    print(name, "tested", len(cases), "bad", len(bad))
R["P1909_v5aspqez"]["official_samples"] = [
    {"input": f"{n} / {packs}", "expected": p1909_correct(n,packs),
     "actual": run(EXE["P1909_v5aspqez"],
                   f"{n}\n"+"\n".join(f"{a} {b}" for a,b in packs)+"\n")[0]}
    for n,packs in fixed_packs[:3]]

# ---------------------------------------------------------------- P1012 对拍
small = [
    [13,312,343], [7,13,4,246], [321,32], [321,37], [12,121],
    [1,10], [9,91], [999999999,1], [1,1,1], [32,321,407,135,13,217],
]
for _ in range(200):
    n = rnd.randint(1,7)
    small.append([str(rnd.randint(1,10**9)) for _ in range(n)])
small = [[str(x) for x in arr] for arr in small]
# 大 n：插入法作参考 + 官方样例已知答案
large = [
    [str(x) for x in arr] for arr in [
        [13,312,343], [7,13,4,246], [321,32,407,135,13,217]]
] + [
    [str(rnd.randint(1,10**9)) for _ in range(20)],
    [str(rnd.randint(1,10**9)) for _ in range(20)],
    [str(rnd.randint(1,10**9)) for _ in range(15)],
]
for name in ["P1012_ngy7hblx", "P1012_ngy7hblx_mut"]:
    bad_small, bad_large = [], []
    for arr in small:
        inp = f"{len(arr)}\n" + " ".join(arr) + "\n"
        out, rc = run(EXE[name], inp)
        exp = p1012_bruteforce(arr)
        if rc != 0 or out != exp:
            if len(bad_small) < 8:
                bad_small.append({"input": inp.strip().replace("\n"," / "),
                                  "expected": exp[:60], "actual": out[:60], "rc": rc})
    for arr in large:
        inp = f"{len(arr)}\n" + " ".join(arr) + "\n"
        out, rc = run(EXE[name], inp)
        exp = p1012_insert(arr)
        if rc != 0 or out != exp:
            bad_large.append({"input": inp.strip().replace("\n"," / ")[:90],
                              "expected": exp[:60], "actual": out[:60], "rc": rc})
    R[name].update({"tested_bruteforce": len(small), "mismatch_bruteforce": len(bad_small),
                    "examples_bruteforce": bad_small[:8],
                    "tested_insert": len(large), "mismatch_insert": len(bad_large),
                    "examples_insert": bad_large[:4]})
    print(name, "brute bad", len(bad_small), "| insert bad", len(bad_large))

# ---------------------------------------------------------------- P1328 对拍
fixed_cases = [
    (10,5,6,[0,1,2,3,4],[0,3,4,2,1,0]),
    (9,5,5,[0,1,2,3,4],[1,0,3,2,4]),
]
cases = list(fixed_cases)
for _ in range(400):
    n = rnd.randint(1,200); na = rnd.randint(1,200); nb = rnd.randint(1,200)
    A = [rnd.randint(0,4) for _ in range(na)]
    B = [rnd.randint(0,4) for _ in range(nb)]
    cases.append((n,na,nb,A,B))
for name in ["P1328_a8f6uiq9", "P1328_a8f6uiq9_mut"]:
    bad = []
    for n,na,nb,A,B in cases:
        inp = f"{n} {na} {nb}\n" + " ".join(map(str,A)) + "\n" + " ".join(map(str,B)) + "\n"
        out, rc = run(EXE[name], inp)
        exp = p1328_correct(n,A,B)
        if rc != 0 or " ".join(out.split()) != exp:
            if len(bad) < 8:
                bad.append({"n": n, "na": na, "nb": nb,
                            "expected": exp, "actual": out[:40], "rc": rc})
    R[name].update({"tested": len(cases), "mismatch": len(bad), "examples": bad[:8]})
    print(name, "tested", len(cases), "bad", len(bad))
R["P1328_a8f6uiq9"]["official_samples"] = [
    {"input": f"{n} {na} {nb}", "expected": p1328_correct(n,A,B),
     "actual": run(EXE["P1328_a8f6uiq9"],
                   f"{n} {na} {nb}\n"+" ".join(map(str,A))+"\n"+" ".join(map(str,B))+"\n")[0]}
    for n,na,nb,A,B in fixed_cases]

json.dump(R, open(os.path.join(D, "results.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("DONE", os.path.join(D, "results.json"))
