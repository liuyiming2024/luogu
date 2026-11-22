#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第 3 批补充验证：P1018 pmio8se0 / P1090 zcxe384l
口径：题面内、确定性 WA-RE、不看评测机波动
"""
import os, json, random, subprocess, heapq

BASE = "/data/workspace/luogu_hack/build/r3"
os.makedirs(BASE, exist_ok=True)
R = {}

SOL = {}

SOL["P1018_pmio8se0"] = r"""
#include<bits/stdc++.h>
using namespace std;
int n,k;
string x,ma="";
int q[10005],p[1005],qp[1005];
string add(string a,string b)
{
 memset(q,0,sizeof(q)); memset(p,0,sizeof(p)); memset(qp,0,sizeof(qp));
 int lx,ly; lx=a.size(); ly=b.size();
 for(int i=1;i<=lx;i++) { q[i]=a[lx-i]-'0'; }
 for(int i=1;i<=ly;i++) { p[i]=b[ly-i]-'0'; }
 for(int i=1;i<=ly;i++) { for(int j=1;j<=lx;j++) { qp[i+j-1]+=q[j]*p[i]; } }
 for(int i=1;i<lx+ly;i++) { if(qp[i]>9) { qp[i+1]+=qp[i]/10; qp[i]%=10; } }
 int len=lx+ly;
 while(len>1&&qp[len]==0) len--;
 string ua="";
 for(int i=len;i>=1;i--) ua+=char(qp[i]+'0');
 return ua;
}
void dfs(int xx,string u,int v,string ans)
{
 if(n-xx-1<v) return;
 if(v==0) {
  string uu="";
  for(int i=xx-1;i<n;i++) uu+=x[i];
  ans=add(ans,uu);
  if(ans.size()>ma.size()||ans.size()==ma.size()&&ans>ma) ma=ans;
  return;
 }
 u+=x[xx-1];
 if(v>0) { dfs(xx+1,"",v-1,add(ans,u)); }
 dfs(xx+1,u,v,ans);
}
int main()
{
 cin>>n>>k>>x;
 dfs(1,"",k,"1");
 cout<<ma;
 return 0;
}
"""

# 逐字版（页面渲染出的 pop 行为 heap(heap.size()-1)）
SOL["P1090_zcxe384l"] = r"""
#include<bits/stdc++.h>
using namespace std;
struct my_priority {
    vector<int>heap;
    void init() { heap.push_back(-1e9); }
    void gao(int pos) {
        int flag;
        if(pos*2>heap.size()-1)return;
        else if(pos*2==heap.size()-1)flag=0;
        else flag=heap[pos*2]>heap[pos*2+1];
        if(heap[pos]>heap[pos*2+flag]) { swap(heap[pos],heap[pos*2+flag]); gao(pos*2+flag); }
        return;
    }
    void doit(int i) {
        while(heap[i]<heap[i/2]) { swap(heap[i],heap[i/2]); i>>=1; }
        return;
    }
    void push(int w) { heap.push_back(w); doit(heap.size()-1); }
    int top() { return heap[1]; }
    void pop() { heap[1]=heap(heap.size()-1); heap.pop_back(); gao(1); }
    int size() { return heap.size()-1; }
} q;
int main() {
    int i,ans=0;
    int n,tmp;
    q.init();
    scanf("%d",&n);
    for(i=1; i<=n; i++) { scanf("%d",&tmp); q.push(tmp); }
    while(q.size()>1) {
        tmp=q.top(); q.pop();
        tmp+=q.top(); q.pop();
        ans+=tmp;
        q.push(tmp);
    }
    printf("%d\n",ans);
    return 0;
}
"""

# 补正版：把疑似被页面吞掉的 [] 补回，检验算法本身
SOL["P1090_zcxe384l_fixed"] = SOL["P1090_zcxe384l"].replace(
    "heap[1]=heap(heap.size()-1);", "heap[1]=heap[heap.size()-1];")

def build(name):
    src = os.path.join(BASE, name + ".cpp")
    exe = os.path.join(BASE, name)
    with open(src, "w", encoding="utf-8") as f:
        f.write(SOL[name])
    p = subprocess.run(["g++", "-std=c++17", "-O2", "-o", exe, src],
                       capture_output=True, text=True)
    return exe, (p.stderr[:700] if p.returncode != 0 else ""), p.returncode

def run(exe, inp, timeout=25):
    p = subprocess.run([exe], input=inp, capture_output=True, text=True, timeout=timeout)
    return p.stdout.strip(), p.returncode, p.stderr.strip()[:120]

# ================================================================= P1018
def p1018_correct(s, k):
    n = len(s)
    NEG = -1
    dp = [[NEG] * (k + 1) for _ in range(n + 1)]
    dp[0][0] = 1
    for i in range(1, n + 1):
        dp[i][0] = int(s[:i])
    for j in range(1, k + 1):
        for i in range(j + 1, n + 1):
            best = NEG
            for p in range(j, i):
                if dp[p][j - 1] >= 0:
                    v = dp[p][j - 1] * int(s[p:i])
                    if v > best:
                        best = v
            dp[i][j] = best
    return dp[n][k]

exe, err, ce = build("P1018_pmio8se0")
R["P1018_pmio8se0"] = {"compile_error": err, "cases": [], "random_tested": 0, "random_mismatch": 0}
if ce == 0:
    rnd = random.Random(20261120)
    fixed = [
        ("k=n-1 最小反例 (n=6,k=5)", 6, 5, "123456"),
        ("k=n-1 (n=7,k=6,含0)", 7, 6, "1020304"),
        ("k=n-1 (n=8,k=7)", 8, 7, "11111111"),
        ("k=n-2 对照组", 6, 4, "123456"),
        ("k=1 对照组", 6, 1, "123456"),
        ("k=2 对照组", 6, 2, "123456"),
    ]
    for label, n, k, s in fixed:
        exp = p1018_correct(s, k)
        out, rc, se = run(exe, f"{n} {k}\n{s}\n")
        R["P1018_pmio8se0"]["cases"].append({
            "label": label, "input": f"{n} {k} / {s}",
            "expected": str(exp), "actual": out, "rc": rc,
            "hacked": out != str(exp)})
    bad = []
    for t in range(150):
        n = rnd.randint(3, 12)
        k = rnd.randint(1, n - 1)
        s = "".join(str(rnd.randint(0, 9)) for _ in range(n))
        exp = p1018_correct(s, k)
        out, rc, se = run(exe, f"{n} {k}\n{s}\n")
        R["P1018_pmio8se0"]["random_tested"] += 1
        if out != str(exp):
            R["P1018_pmio8se0"]["random_mismatch"] += 1
            if len(bad) < 4:
                bad.append({"input": f"{n} {k} / {s}", "expected": str(exp), "actual": out})
    R["P1018_pmio8se0"]["random_examples"] = bad

# ================================================================= P1090
def p1090_correct(a):
    if len(a) <= 1:
        return 0
    h = list(a); heapq.heapify(h); ans = 0
    while len(h) > 1:
        x = heapq.heappop(h); y = heapq.heappop(h)
        s = x + y; ans += s; heapq.heappush(h, s)
    return ans

for name in ["P1090_zcxe384l", "P1090_zcxe384l_fixed"]:
    exe, err, ce = build(name)
    R[name] = {"compile_error": err, "compile_rc": ce}
    if ce != 0:
        continue
    rnd = random.Random(4242)
    bad = []
    tested = 0
    for t in range(200):
        n = rnd.randint(1, 40)
        a = [rnd.randint(1, 20000) for _ in range(n)]
        exp = p1090_correct(a)
        out, rc, se = run(exe, f"{n}\n" + " ".join(map(str, a)) + "\n")
        tested += 1
        if out != str(exp):
            if len(bad) < 4:
                bad.append({"input": f"{n} / {a[:6]}...", "expected": exp, "actual": out, "rc": rc})
    # 贴题面上界的构造（答案保证 < 2^31）
    big = [20000] * 10000
    exp = p1090_correct(big)
    out, rc, se = run(exe, "10000\n" + " ".join(map(str, big)) + "\n")
    R[name].update({"tested": tested + 1, "mismatch": len(bad), "examples": bad,
                    "max_case": {"n": 10000, "expected": exp, "actual": out, "rc": rc}})

with open(os.path.join(BASE, "results2.json"), "w", encoding="utf-8") as f:
    json.dump(R, f, ensure_ascii=False, indent=2)
print(json.dumps(R, ensure_ascii=False, indent=2))
