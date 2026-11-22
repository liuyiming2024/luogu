#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 12 批补充 C：修正 ehkpairy 修复版位置；iv10492z 峰值 RSS 与 8MB 限制对照。"""
import os, json, subprocess, itertools, random, resource
from math import gcd

D = "/data/workspace/luogu_hack/build/r12"
OUT = {}

# ---------------------------------------------------------------- 1. ehkpairy 修复版（特判放到 scanf 之后）
orig = open(os.path.join(D, "P1618_ehkpairy.cpp"), encoding="utf-8").read()
FIX_A = orig.replace(
    "    scanf(\"%d%d%d\", &a, &b, &c);",
    "    scanf(\"%d%d%d\", &a, &b, &c);\n    if (a == 0) { printf(\"No!!!\"); return 0; }")
assert FIX_A != orig, "replace 未命中"
p = os.path.join(D, "ehkpairy_fix.cpp")
open(p, "w", encoding="utf-8").write(FIX_A)
exe = os.path.join(D, "ehkpairy_fix")
r = subprocess.run(["g++","-std=c++17","-O2","-w","-o",exe,p],
                   capture_output=True,text=True,timeout=90)

TRIPLES = []
for perm in itertools.permutations("123456789"):
    TRIPLES.append((int("".join(perm[0:3])), int("".join(perm[3:6])),
                    int("".join(perm[6:9]))))
TRIPLES.sort()
RATIO = {}
for n1,n2,n3 in TRIPLES:
    g = gcd(gcd(n1,n2),n3)
    RATIO.setdefault((n1//g,n2//g,n3//g),[]).append(f"{n1} {n2} {n3}")
def correct(A,B,C):
    if A==0: return "No!!!"
    g=gcd(gcd(A,B),C)
    L=RATIO.get((A//g,B//g,C//g),[])
    return "\n".join(L) if L else "No!!!"
def norm(s): return "\n".join(l.rstrip() for l in s.strip().splitlines() if l.strip())

cases = list(itertools.combinations(range(0,21),3))
rnd = random.Random(20261122)
for _ in range(60):
    A=rnd.randint(0,900); B=rnd.randint(A+1,950); C=rnd.randint(B+1,999)
    cases.append((A,B,C))
cases += [(0,1,2),(0,2,3),(2,4,6),(4,6,8),(3,6,9),(1,2,3),(2,3,4),
          (1,3,5),(5,10,15),(7,14,21),(2,6,10)]
bad=[]
for A,B,C in cases:
    q = subprocess.run([exe], input=f"{A} {B} {C}\n", capture_output=True, text=True, timeout=8)
    if q.returncode!=0 or norm(q.stdout)!=norm(correct(A,B,C)):
        bad.append((f"{A} {B} {C}", q.stdout[:60], q.returncode))
OUT["ehkpairy_fix"] = {"compile_rc": r.returncode, "tested": len(cases),
                       "mismatch": len(bad), "examples": bad[:5]}
print("ehkpairy_fix compile", r.returncode, "tested", len(cases), "bad", len(bad), bad[:3])

# ---------------------------------------------------------------- 2. 峰值 RSS（fork + wait4，单进程精确值）
O1 = "#include<cstdio>\nint main(){int n,s=0,x; scanf(\"%d\",&n); for(int i=1;i<=n;i++){scanf(\"%d\",&x); s^=x;} printf(\"%d\",s); return 0;}\n"
p2 = os.path.join(D, "p1469_o1.cpp"); open(p2,"w",encoding="utf-8").write(O1)
exe_o1 = os.path.join(D, "p1469_o1")
subprocess.run(["g++","-std=c++17","-O2","-w","-o",exe_o1,p2],
               capture_output=True,text=True,timeout=90)
exe_vec = os.path.join(D, "P1469_iv10492z")

def peak_rss(exe, inp_file):
    devnull = os.open(os.devnull, os.O_WRONLY)
    pid = os.fork()
    if pid == 0:
        fd = os.open(inp_file, os.O_RDONLY)
        os.dup2(fd, 0); os.dup2(devnull, 1); os.dup2(devnull, 2)
        os.execv(exe, [exe])
        os._exit(127)
    _, status, ru = os.wait4(pid, 0)
    os.close(devnull)
    return {"exit": os.waitstatus_to_exitcode(status), "peak_rss_KB": ru.ru_maxrss}

N = 10000001
big = os.path.join(D, "mem_input.txt")
if not os.path.exists(big):
    with open(big,"w",encoding="utf-8") as f:
        f.write(f"{N}\n"); f.write("1 "*(N-1)); f.write("2\n")

OUT["peak_rss"] = {}
for tag, e in [("iv10492z_vector", exe_vec), ("o1_xor_对照", exe_o1)]:
    OUT["peak_rss"][tag] = peak_rss(e, big)
    v = OUT["peak_rss"][tag]
    print("PEAK", tag, "exit", v["exit"], "RSS", v["peak_rss_KB"], "KB =",
          round(v["peak_rss_KB"]/1024,1), "MB")

# ---------------------------------------------------------------- 3. RLIMIT_AS 对照（模拟题面 8Mb）
STATIC = {}
for tag, src in [("vec", open(os.path.join(D,"P1469_iv10492z.cpp"),encoding="utf-8").read()),
                 ("o1", O1)]:
    sp = os.path.join(D, "stat_"+tag+".cpp"); open(sp,"w",encoding="utf-8").write(src)
    se = os.path.join(D, "stat_"+tag)
    rr = subprocess.run(["g++","-std=c++17","-O2","-w","-static","-o",se,sp],
                        capture_output=True,text=True,timeout=120)
    STATIC[tag] = (se, rr.returncode, rr.stderr[:200])
    print("STATIC BUILD", tag, rr.returncode, rr.stderr[:100].replace("\n"," "))

small = os.path.join(D, "mem_small.txt")
M = 3000001     # 300 万个数：vector 需 ~12MB，静态 O(1) 版远小于 8MB
with open(small,"w",encoding="utf-8") as f:
    f.write(f"{M}\n"); f.write("1 "*(M-1)); f.write("2\n")

def with_limit(exe, inp_file, mb):
    def lim():
        b = mb*1024*1024
        resource.setrlimit(resource.RLIMIT_AS,(b,b))
    try:
        with open(inp_file,"rb") as fin:
            q = subprocess.run([exe], stdin=fin, capture_output=True, text=True,
                               timeout=20, preexec_fn=lim)
        return {"rc": q.returncode, "out": q.stdout.strip()[:20],
                "err": q.stderr.strip()[:100]}
    except subprocess.TimeoutExpired:
        return {"rc": -99, "out": "<TIMEOUT>", "err": ""}

OUT["rlimit"] = {}
for mb in [8, 16, 32]:
    row = {}
    for tag,(se,rc,_) in STATIC.items():
        row[tag] = with_limit(se, small, mb)
    OUT["rlimit"][f"{mb}MB"] = row
    print("RLIMIT", mb, "MB ->", {k:(v["rc"],v["out"]) for k,v in row.items()})

json.dump(OUT, open(os.path.join(D,"results_extra_c.json"),"w",encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("DONE")
