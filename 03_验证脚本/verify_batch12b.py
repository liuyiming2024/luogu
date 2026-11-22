#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 12 批补充：修复版复验（划界）、utz61eus 定点、iv10492z 内存剖面。"""
import os, json, subprocess, itertools, resource, random
from math import gcd

D = "/data/workspace/luogu_hack/build/r12"
RR = json.load(open(os.path.join(D, "results.json"), encoding="utf-8"))
OUT = {"bad_full": {}, "fix": {}, "utz61eus_points": [], "mem_profile": []}

print("=== 两篇 P1618 的 bad 全貌 ===")
for k in ["P1618_ehkpairy", "P1618_j4zpxmp6"]:
    OUT["bad_full"][k] = RR[k]["examples"]
    print(k, "tested", RR[k]["tested"], "mismatch", RR[k]["mismatch"])
    for e in RR[k]["examples"][:12]:
        print("   ", e)

# ---------------------------------------------------------------- 独立正确解（查表）
TRIPLES = []
for perm in itertools.permutations("123456789"):
    TRIPLES.append((int("".join(perm[0:3])), int("".join(perm[3:6])),
                    int("".join(perm[6:9]))))
TRIPLES.sort()
RATIO = {}
for n1, n2, n3 in TRIPLES:
    g = gcd(gcd(n1, n2), n3)
    RATIO.setdefault((n1 // g, n2 // g, n3 // g), []).append(f"{n1} {n2} {n3}")

def correct(A, B, C):
    if A == 0: return "No!!!"
    g = gcd(gcd(A, B), C)
    L = RATIO.get((A // g, B // g, C // g), [])
    return "\n".join(L) if L else "No!!!"

def norm(s):
    return "\n".join(l.rstrip() for l in s.strip().splitlines() if l.strip())

cases = list(itertools.combinations(range(0, 21), 3))
rnd = random.Random(20261122)
for _ in range(60):
    A = rnd.randint(0, 900); B = rnd.randint(A + 1, 950); C = rnd.randint(B + 1, 999)
    cases.append((A, B, C))
cases += [(0,1,2),(0,2,3),(2,4,6),(4,6,8),(3,6,9),(1,2,3),(2,3,4),
          (1,3,5),(5,10,15),(7,14,21),(2,6,10)]

# ---------------------------------------------------------------- 修复版
FIX_A = open(os.path.join(D, "P1618_ehkpairy.cpp"), encoding="utf-8").read().replace(
    "    bool no = true;",
    "    bool no = true;\n    if (a == 0) { printf(\"No!!!\"); return 0; }")

FIX_B = r"""#include<bits/stdc++.h>
using namespace std;
int a,b,c;
bool check1(int n){
    string s=to_string(n);
    if(s.size()!=3) return 0;
    for(int i=0;i<s.size();i++) for(int j=0;j<s.size();j++){
        if(i!=j && s[i]==s[j]) return 0;
        if(s[i]=='0'||s[j]=='0') return 0;
    }
    return 1;
}
bool check2(int n,int m){
    string s=to_string(n),t=to_string(m);
    for(int i=0;i<s.size();i++) for(int j=0;j<t.size();j++) if(s[i]==t[j]) return 0;
    return 1;
}
int main(){
    int cnt=0; cin>>a>>b>>c;
    if(a==0||b==0||c==0){ cout<<"No!!!"; return 0; }
    for(int i=1;i<=9;i++) for(int j=1;j<=9;j++){
        if(i==j) continue;
        for(int k=1;k<=9;k++){
            if(i==k||j==k) continue;
            int n1=i*100+j*10+k;
            if((long long)n1*b%a || (long long)n1*c%a) continue;
            int n2=(long long)n1*b/a, n3=(long long)n1*c/a;
            if(!check1(n2)||!check1(n3)) continue;
            if(!check2(n1,n2)||!check2(n1,n3)||!check2(n2,n3)) continue;
            cnt++; cout<<n1<<" "<<n2<<" "<<n3<<"\n";
        }
    }
    if(cnt==0) cout<<"No!!!";
    return 0;
}
"""

def compile_src(name, src):
    p = os.path.join(D, name + ".cpp")
    open(p, "w", encoding="utf-8").write(src)
    exe = os.path.join(D, name)
    r = subprocess.run(["g++","-std=c++17","-O2","-w","-o",exe,p],
                       capture_output=True,text=True,timeout=90)
    return exe, r.returncode, r.stderr[:300]

def run(exe, inp, timeout=8):
    try:
        p = subprocess.run([exe], input=inp, capture_output=True, text=True, timeout=timeout)
        return p.stdout.strip(), p.returncode
    except subprocess.TimeoutExpired:
        return "<TIMEOUT>", -99

for name, src in [("ehkpairy_fix", FIX_A), ("j4zpxmp6_fix", FIX_B)]:
    exe, rc, err = compile_src(name, src)
    bad = []
    for A, B, C in cases:
        exp = correct(A, B, C)
        out, r = run(exe, f"{A} {B} {C}\n")
        if r != 0 or norm(out) != norm(exp):
            bad.append({"input": f"{A} {B} {C}", "expected": exp[:80], "actual": out[:80], "rc": r})
    OUT["fix"][name] = {"compile_rc": rc, "compile_err": err, "tested": len(cases),
                        "mismatch": len(bad), "examples": bad[:6]}
    print("FIX", name, "rc", rc, "tested", len(cases), "bad", len(bad), bad[:2])

# ---------------------------------------------------------------- utz61eus 定点
exe = os.path.join(D, "P1469_utz61eus")
points = [
    ("全在 1e7 内（应正确）", [2,2,9999999], "9999999"),
    ("落单 = 10000001（>1e7，遍历漏）", [2,2,10000001], "10000001"),
    ("落单 = 50000000（>1e7 且 <1e8）", [2,2,50000000], "50000000"),
    ("落单 = 100000000（>1e8，下标越界）", [2,2,100000000], "100000000"),
    ("n=1 且 a1=1e9（题面上界）", [1000000000], "1000000000"),
    ("官方样例", [2,2,1,3,3,3,2,3,1], "2"),
]
for label, arr, exp in points:
    inp = f"{len(arr)}\n" + " ".join(map(str, arr)) + "\n"
    out, rc = run(exe, inp, timeout=6)
    rec = {"label": label, "input": inp.strip().replace("\n", " / "),
           "expected": exp, "actual": out, "rc": rc,
           "hacked": not (rc == 0 and out.strip() == exp)}
    OUT["utz61eus_points"].append(rec)
    print("POINT", label, "->", "HACK" if rec["hacked"] else "ok", "rc", rc, "out", repr(out[:30]))

# ---------------------------------------------------------------- iv10492z 内存剖面
# 题面：n<=1e7+1，空间限制 8Mb。用 ru_maxrss 实测峰值物理内存，并与 O(1) 版对照。
O1 = r"""#include<cstdio>
int main(){int n,s=0,x; scanf("%d",&n); for(int i=1;i<=n;i++){scanf("%d",&x); s^=x;} printf("%d",s); return 0;}
"""
exe_o1, rc, err = compile_src("p1469_o1", O1)
exe_vec = os.path.join(D, "P1469_iv10492z")
N = 10000001
inp_file = os.path.join(D, "mem_input.txt")
with open(inp_file, "w", encoding="utf-8") as f:
    f.write(f"{N}\n")
    f.write("1 " * (N - 1))
    f.write("2\n")          # 1e7 个 1 成对 + 1 个落单 2，n 为奇数、题面内
print("输入文件大小 MB", round(os.path.getsize(inp_file) / 1024 / 1024, 1))

for tag, exe in [("iv10492z_vector", exe_vec), ("o1_xor_对照", exe_o1)]:
    before = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    try:
        with open(inp_file, "rb") as fin:
            p = subprocess.run([exe], stdin=fin, capture_output=True, text=True, timeout=60)
        out, r = p.stdout.strip(), p.returncode
    except subprocess.TimeoutExpired:
        out, r = "<TIMEOUT>", -99
    after = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    # ru_maxrss 为所有子进程峰值上限，取增量需谨慎；这里用 /usr/bin/time 风格另测
    rec = {"tag": tag, "rc": r, "actual": out[:30], "expect": "2",
           "rusage_maxrss_after_KB": after}
    OUT["mem_profile"].append(rec)
    print("MEM", tag, "rc", r, "out", repr(out[:20]), "maxrss(after) KB", after)

# 精确峰值 RSS：用 /usr/bin/time -v 若可用
for tag, exe in [("iv10492z_vector", exe_vec), ("o1_xor_对照", exe_o1)]:
    try:
        with open(inp_file, "rb") as fin:
            t = subprocess.run(["/usr/bin/time", "-v", exe], stdin=fin,
                               capture_output=True, text=True, timeout=60)
        m = __import__("re").search(r"Maximum resident set size \(kbytes\): (\d+)", t.stderr)
        rss = int(m.group(1)) if m else None
    except Exception as e:
        rss = None
    for rec in OUT["mem_profile"]:
        if rec["tag"] == tag:
            rec["peak_rss_KB"] = rss
    print("PEAK", tag, rss, "KB", "≈", round(rss/1024,1) if rss else "?", "MB")

json.dump(OUT, open(os.path.join(D, "results_extra.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("DONE")
