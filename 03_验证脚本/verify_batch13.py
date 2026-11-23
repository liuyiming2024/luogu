#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 13 批 · 低频补录（三类口径）
逐字源码取自 www.luogu.com/article/<lid>：
  88t0yv7r (P1307) / 7p4p6gdm (P2615) / 79f7f3bn (P2669) / 0dhpwlt6 (P2615)
另 zm6gqovk = 帮助规范文章，判定「是否题解=否」（不编译）。
口径：题面内 + 确定性 WA/RE + 不看评测机波动；只验核心逻辑，不判代码完整度。
"""
import os, json, random, subprocess, resource

BASE = "/data/workspace/luogu_hack"
D = os.path.join(BASE, "build", "r13")
os.makedirs(D, exist_ok=True)
R = {}

def build(name, src):
    p = os.path.join(D, name + ".cpp")
    open(p, "w", encoding="utf-8").write(src)
    exe = os.path.join(D, name)
    r = subprocess.run(["g++", "-std=c++17", "-O2", "-w", "-o", exe, p],
                       capture_output=True, text=True, timeout=90)
    return exe, r.returncode, r.stderr[:400]

def run(exe, inp, timeout=8):
    try:
        p = subprocess.run([exe], input=inp, capture_output=True, text=True, timeout=timeout)
        return p.stdout, p.returncode
    except subprocess.TimeoutExpired:
        return "<TIMEOUT>", -99

def norm(s):
    # 逐行 rstrip：题面「相邻两数单空格」，行尾空格不参与判定（与第 9 批 P1598 同口径）
    return "\n".join(l.rstrip() for l in s.strip().splitlines())

# ============================================================ A. P1307 88t0yv7r
# 逐字正文含不可见 tag characters（防抄袭），逻辑等价版如下；另单独测逐字版编译。
SRC_A = r"""#include <iostream>
#include <algorithm>
using namespace std;
int main()
{
int n ;
cin >> n ;
int m = 0 ;
if ( n < 0 )
{
cout << "-" ;
n *= -1 ;
}
while ( n != 0 )
{
m = n % 10 + m * 10 ;
n /= 10 ;
}
cout << m << endl ;
return 0;
}
"""

# ============================================================ B. P2615 7p4p6gdm
# 逐字正文：int n,a[40][40]; memset(a,0,sizeof(a));//初始化x,y  a[x][y]=1;
# x,y 未声明未赋值 → 最小外壳仅补全局声明 int x,y;（全局零初始化，C++ 标准语义）
SRC_B = r"""#include<bits/stdc++.h>
using namespace std;
int x, y;
int main(){
int n,a[40][40];
cin>>n;
memset(a,0,sizeof(a));//初始化x,y
a[x][y]=1;
for(int i=2;i<=n*n;i++)
{
if(x==1&&y!=n) { x=n; y++; }
else if(y==n&&x!=1) { y=1; x--; }
else if(x==1&&y==n) { x++; y=y; }
else if(x!=1&&y!=n) { if(a[x-1][y+1]==0) { x--; y++; } else { x++; y=y; } }
a[x][y]=i;
}
for(int i=1;i<=n;i++) { for(int j=1;j<=n;j++) cout<<a[i][j]<<" "; cout<<endl; }
return 0;
}
"""
# 修复版：按题面「1 写在第一行的中间」补初值 x=1; y=n/2+1;（必须在读 n 之后）
SRC_B_FIX = SRC_B.replace("cin>>n;\n", "cin>>n;\nx=1; y=n/2+1;\n")
# 对照：若照抄作者文字「先初始化x=n/2+1,y=1」（行列写反）
SRC_B_TEXT = SRC_B.replace("cin>>n;\n", "cin>>n;\nx=n/2+1; y=1;\n")
# 对照：x,y 声明为局部（未初始化，UB）
SRC_B_LOCAL = SRC_B.replace("int x, y;\n", "").replace(
    "int n,a[40][40];\n", "int n,a[40][40],x,y;\n")

# ============================================================ C. P2669 79f7f3bn
SRC_C = r"""#include<cstdio>
int main(){
int k,sum=0,ans=0,t,d,i;
scanf("%d",&k);
for(i=1;;i++){
sum+=i;
ans+=i*i;
if(sum==k){ printf("%d\n",ans); return 0; }
if(sum>k){ t=i-1; break; }
}
ans=0;
for(i=1;i<=t;i++) ans+=i*i;
d=k-sum+t+1;
ans+=d*(t+1);
printf("%d\n",ans);
return 0;
}
"""

# ============================================================ D. P2615 0dhpwlt6
# 页面仅「四个条件语句」思路片段，无 main/输出。按题解文字补最小外壳，
# 与第 1 批 P1220 同例：结论对补全后的等价实现成立。
SRC_D = r"""#include<bits/stdc++.h>
using namespace std;
int n,a[45][45],x,y,xx,yy;
int main(){
cin>>n;
memset(a,0,sizeof(a));
x=1; y=n/2+1;
a[x][y]=1;
for(int k=2;k<=n*n;k++){
if(x==1&&y!=n) xx=n,yy=y+1;
else if(y==n&&x!=1) yy=1,xx=x-1;
else if(x==1&&y==n) xx=x+1,yy=y;
else if(x!=1&&y!=n){ if(!a[x-1][y+1]) xx=x-1,yy=y+1; else xx=x+1,yy=y; }
x=xx; y=yy; a[x][y]=k;
}
for(int i=1;i<=n;i++){ for(int j=1;j<=n;j++) cout<<a[i][j]<<" "; cout<<endl; }
return 0;
}
"""

SOURCES = {
    "P1307_88t0yv7r": SRC_A,
    "P2615_7p4p6gdm": SRC_B,
    "P2615_7p4p6gdm_fix": SRC_B_FIX,
    "P2615_7p4p6gdm_by_text": SRC_B_TEXT,
    "P2615_7p4p6gdm_local": SRC_B_LOCAL,
    "P2669_79f7f3bn": SRC_C,
    "P2615_0dhpwlt6": SRC_D,
}
EXE = {}
for k, v in SOURCES.items():
    e, rc, err = build(k, v)
    EXE[k] = e
    R[k] = {"compile_rc": rc, "compile_err": err, "cases": []}
    print("BUILD", k, "rc=", rc, err[:100].replace("\n", " "))

# ---------------------------------------------------------------- 独立正确解
def p1307_correct(n):
    s = str(abs(n))[::-1].lstrip("0") or "0"
    v = int(s)
    return str(-v if n < 0 else v)

def p2615_correct(n):
    a = [[0] * (n + 2) for _ in range(n + 2)]
    x, y = 1, n // 2 + 1
    a[x][y] = 1
    for k in range(2, n * n + 1):
        if x == 1 and y != n: nx, ny = n, y + 1
        elif y == n and x != 1: nx, ny = x - 1, 1
        elif x == 1 and y == n: nx, ny = x + 1, y
        else:
            nx, ny = (x - 1, y + 1) if a[x - 1][y + 1] == 0 else (x + 1, y)
        a[nx][ny] = k; x, y = nx, ny
    return "\n".join(" ".join(str(a[i][j]) for j in range(1, n + 1))
                     for i in range(1, n + 1))

def p2669_correct(k):
    day, coin, left, total = 0, 1, 1, 0
    while day < k:
        total += coin; day += 1; left -= 1
        if left == 0: coin += 1; left = coin
    return str(total)

# ---------------------------------------------------------------- P1307 对拍
bad = []
cases = [-10**9, -999999999, -380, -100, -1, 0, 1, 10, 100, 123, 380,
         1000000000, 999999999, 100000000, 101, 110, 1000000001 - 1]
rnd = random.Random(20261123)
for _ in range(300):
    cases.append(rnd.randint(-10**9, 10**9))
for n in cases:
    out, rc = run(EXE["P1307_88t0yv7r"], f"{n}\n")
    exp = p1307_correct(n)
    if rc != 0 or out.strip() != exp:
        bad.append({"input": n, "expected": exp, "actual": out.strip()[:40], "rc": rc})
R["P1307_88t0yv7r"].update({"tested": len(cases), "mismatch": len(bad),
                            "examples": bad[:6]})
print("P1307_88t0yv7r bad", len(bad), bad[:2])

# 逐字带不可见 tag characters 的编译对照（防抄袭证据）
tag = "\U000E0050\U000E0049\U000E0063\U000E0054"  # U+E00xx tag characters
SRC_A_RAW = SRC_A.replace("int main()", tag + "int main()").replace(
    "cout << m << endl ;", tag + "cout << m << endl ;")
e_raw, rc_raw, err_raw = build("P1307_88t0yv7r_rawtags", SRC_A_RAW)
R["P1307_88t0yv7r"]["raw_tag_compile"] = {
    "rc": rc_raw, "err": err_raw[:200],
    "note": "逐字含不可见 tag characters 时编译失败；按口径属主动防抄袭，不计缺陷"}

# ---------------------------------------------------------------- P2615 对拍
NS = list(range(1, 40, 2))   # 题面：1<=N<=39 且 N 为奇数
for name in ["P2615_7p4p6gdm", "P2615_7p4p6gdm_fix", "P2615_7p4p6gdm_by_text",
             "P2615_7p4p6gdm_local", "P2615_0dhpwlt6"]:
    bad = []
    for n in NS:
        exp = p2615_correct(n)
        out, rc = run(EXE[name], f"{n}\n")
        if rc != 0 or norm(out) != norm(exp):
            bad.append({"n": n, "rc": rc,
                        "expected_head": exp.splitlines()[0][:50],
                        "actual_head": out.strip().splitlines()[0][:50] if out.strip() else "<empty>"})
    R[name].update({"tested": len(NS), "mismatch": len(bad), "examples": bad[:6]})
    print(name, "bad", len(bad), bad[:2])

# 官方样例定点
for name in ["P2615_7p4p6gdm", "P2615_7p4p6gdm_fix", "P2615_0dhpwlt6"]:
    out, rc = run(EXE[name], "3\n")
    R[name]["sample_3"] = {"rc": rc, "output": out.strip(),
                           "expected": p2615_correct(3)}

# ---------------------------------------------------------------- P2669 对拍
bad = []
ks = list(range(1, 10001))
for k in ks:
    out, rc = run(EXE["P2669_79f7f3bn"], f"{k}\n", timeout=5)
    exp = p2669_correct(k)
    if rc != 0 or out.strip() != exp:
        if len(bad) < 8:
            bad.append({"k": k, "expected": exp, "actual": out.strip()[:30], "rc": rc})
R["P2669_79f7f3bn"].update({"tested": len(ks), "mismatch": len(bad),
                            "examples": bad})
print("P2669_79f7f3bn bad", len(bad), bad[:3])
for k in [1, 2, 3, 6, 10, 1000, 10000]:
    out, rc = run(EXE["P2669_79f7f3bn"], f"{k}\n")
    R["P2669_79f7f3bn"]["cases"].append(
        {"k": k, "expected": p2669_correct(k), "actual": out.strip(), "rc": rc})

json.dump(R, open(os.path.join(D, "results.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("DONE", os.path.join(D, "results.json"))
