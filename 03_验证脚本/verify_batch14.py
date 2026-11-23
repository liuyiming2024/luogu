#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 14 批 · 低频补录（三类口径）
逐字源码取自 www.luogu.com/article/<lid>：
  g8gclrnk  (P5015) —— 新增编号
  88laurj5  (P1098) —— 第 8 批「代码取不全」登记条目，现逐字取回全文
  2edysvbn  (P1428) —— 第 9 批「只有思路无 AC 代码」登记条目，现逐字取回全文
口径：题面内 + 确定性 WA/RE + 不看评测机波动；只验核心逻辑，不判代码完整度。
"""
import os, json, random, subprocess

BASE = "/data/workspace/luogu_hack"
D = os.path.join(BASE, "build", "r14")
os.makedirs(D, exist_ok=True)
R = {}

def build(name, src):
    p = os.path.join(D, name + ".cpp")
    open(p, "w", encoding="utf-8").write(src)
    e = os.path.join(D, name)
    r = subprocess.run(["g++", "-std=c++17", "-O2", "-w", "-o", e, p],
                       capture_output=True, text=True, timeout=90)
    return e, r.returncode, r.stderr[:400]

def run(e, inp, t=10):
    try:
        p = subprocess.run([e], input=inp, capture_output=True, text=True, timeout=t)
        return p.stdout.strip(), p.returncode
    except subprocess.TimeoutExpired:
        return "<TIMEOUT>", -99

# ============================================================ A. P5015 g8gclrnk
SRC_A = r"""#include<bits/stdc++.h>
using namespace std;
string s;
int cnt=0;
int main(){
getline(cin,s);
for(char c:s)	if(c!=' '&&c!='\n') cnt++;
cout<<cnt;
return 0;
}
"""

# ============================================================ B. P1098 88laurj5
# 逐字取回（页面吞字符处按题解文字补最小外壳：仅补 main 结束括号配对与必要空白）
SRC_B = r"""#include<bits/stdc++.h>
using namespace std;
int p1,p2,p3; char a[101];
int main() {
scanf("%d%d%d",&p1,&p2,&p3);
cin>>a;
for(int i=0;i<strlen(a);i++) {
if(a[i]!='-') { cout<<a[i]; continue; }
if(a[i-1]>='0'&&a[i-1]<='9'&&(a[i+1]<'0'||a[i+1]>'9')) { printf("-"); continue; }
if(a[i+1]>='0'&&a[i+1]<='9'&&(a[i-1]<'0'||a[i-1]>'9')) { printf("-"); continue; }
if(a[i-1]>=a[i+1]) { printf("-"); continue; }
if(a[i+1]=='-'||a[i-1]=='-') { printf("-"); continue; }
if(i==0) { printf("-"); continue; }
if(p1==3&&i!=0) { for(char j=a[i-1]+1;j<a[i+1];j++) for(int k=1;k<=p2;k++) printf("*"); continue; }
if(p3==1) {
if(p1==1) for(char j=a[i-1]+1;j<a[i+1];j++) for(int k=1;k<=p2;k++) cout<<char(j);
if(p1==2) for(char j=a[i-1]-31;j<a[i+1]-32;j++) for(int k=1;k<=p2;k++) { if((a[i+1]>='0'&&a[i+1]<='9')||(a[i-1]>='0'&&a[i-1]<='9')) cout<<char(j+30); else cout<<char(j); }
}
if(p3==2) {
if(p1==1) for(char j=a[i+1]-1;j>a[i-1];j--) for(int k=1;k<=p2;k++) cout<<char(j);
if(p1==2) for(char j=a[i+1]-33;j>a[i-1]-32;j--) for(int k=1;k<=p2;k++) { if((a[i+1]>='0'&&a[i+1]<='9')||(a[i-1]>='0'&&a[i-1]<='9')) cout<<char(j+32); else cout<<char(j); }
}
}
return 0;
}
"""
# 修复版：仅把 p3==1 / p1==2 数字分支的 j+30 改成 j+32（一个字符）
SRC_B_FIX = SRC_B.replace("cout<<char(j+30)", "cout<<char(j+32)")

# ============================================================ C. P1428 2edysvbn
SRC_C = r"""#include<bits/stdc++.h>
using namespace std;
int n,a[3010],sum=0;
int main(){
    cin>>n;
    for(int i=1;i<=n;i++)cin>>a[i];
    for(int i=1;i<=n;i++){
        for(int j=i-1;j>=1;j--){
            if(a[i]>a[j])sum++;
        }
        cout<<sum<<' ';
        sum=0;
    }
    return 0;
}
"""

SOURCES = {
    "P5015_g8gclrnk": SRC_A,
    "P1098_88laurj5": SRC_B,
    "P1098_88laurj5_fix": SRC_B_FIX,
    "P1428_2edysvbn": SRC_C,
}
EXE = {}
for k, v in SOURCES.items():
    e, rc, err = build(k, v)
    EXE[k] = e
    R[k] = {"compile_rc": rc, "compile_err": err}
    print("BUILD", k, "rc=", rc, err[:120].replace("\n", " "))

# ---------------------------------------------------------------- 独立正确解
def p5015_correct(s):
    return str(len(s.replace(" ", "").replace("\n", "")))

def ok1098(s, p1, p2, p3):
    """第 8 批验证脚本里的独立正确解（逐字复用）"""
    out = []; L = len(s)
    for i, ch in enumerate(s):
        if ch != '-': out.append(ch); continue
        if i == 0 or i == L - 1: out.append('-'); continue
        a, b = s[i - 1], s[i + 1]
        sd = ('0' <= a <= '9') and ('0' <= b <= '9')
        sa = ('a' <= a <= 'z') and ('a' <= b <= 'z')
        if not (sd or sa): out.append('-'); continue
        if b <= a: out.append('-'); continue
        cs = [chr(c) for c in range(ord(a) + 1, ord(b))]
        if p1 == 3: cs = ['*'] * len(cs)
        elif p1 == 2 and sa: cs = [c.upper() for c in cs]
        if p3 == 2: cs = list(reversed(cs))
        out.append(''.join(c * p2 for c in cs))
    return ''.join(out)

def p1428_correct(arr):
    return " ".join(str(sum(1 for j in range(i) if arr[j] < arr[i]))
                   for i in range(len(arr)))

# ---------------------------------------------------------------- P5015 对拍
bad = []
pool = "ABCxyz0123 "
rnd = random.Random(20261124)
for _ in range(300):
    s = "".join(rnd.choice(pool) for _ in range(rnd.randint(0, 120)))
    out, rc = run(EXE["P5015_g8gclrnk"], s + "\n")
    exp = p5015_correct(s)
    if rc != 0 or out != exp:
        bad.append({"input": repr(s), "expected": exp, "actual": out, "rc": rc})
for s in ["", " ", "   ", "Ca 45", "234", "a b c d e", "A  B   C"]:
    out, rc = run(EXE["P5015_g8gclrnk"], s + "\n")
    exp = p5015_correct(s)
    if rc != 0 or out != exp:
        bad.append({"input": repr(s), "expected": exp, "actual": out, "rc": rc})
R["P5015_g8gclrnk"].update({"tested": 307, "mismatch": len(bad), "examples": bad[:6]})
print("P5015_g8gclrnk bad", len(bad))

# ---------------------------------------------------------------- P1098 对拍
fixed = [
    ("官方样例1", 1, 2, 1, "abcs-w1234-9s-4zz"),
    ("官方样例2", 2, 3, 2, "a-d-d"),
    ("p3=2 纯字母", 1, 2, 2, "d-h"),
    ("p3=2 数字", 1, 2, 2, "1-5"),
    ("p1=2 数字顺序", 2, 2, 1, "1-5"),
    ("p1=2 字母顺序", 2, 2, 1, "a-d"),
    ("p1=2 数字逆序", 2, 2, 2, "1-5"),
    ("p1=2 字母逆序", 2, 2, 2, "a-d"),
    ("p1=3 数字", 3, 2, 1, "1-5"),
    ("p1=3 字母 p3=2", 3, 2, 2, "a-d"),
    ("长度1", 1, 2, 1, "a"),
    ("长度2 末尾减号", 1, 2, 1, "a-"),
    ("混合类型", 1, 2, 1, "s-4"),
    ("连续减号", 1, 2, 1, "a--d"),
    ("递减", 1, 2, 1, "d-a"),
]
cases = [(l, p1, p2, p3, s) for l, p1, p2, p3, s in fixed]
alpha = "abcdefghijklmnopqrstuvwxyz0123456789-"
for _ in range(400):
    p1 = rnd.randint(1, 3); p2 = rnd.randint(1, 8); p3 = rnd.randint(1, 2)
    L = rnd.randint(1, 30)
    s = "".join(rnd.choice(alpha) for _ in range(L))
    cases.append(("rand", p1, p2, p3, s))

for name in ["P1098_88laurj5", "P1098_88laurj5_fix"]:
    bad = []
    for label, p1, p2, p3, s in cases:
        inp = f"{p1} {p2} {p3}\n{s}\n"
        exp = ok1098(s, p1, p2, p3)
        out, rc = run(EXE[name], inp)
        if rc != 0 or out != exp:
            if len(bad) < 12:
                bad.append({"label": label, "input": inp.strip().replace("\n", " / "),
                            "expected": exp[:90], "actual": out[:90], "rc": rc})
    R[name].update({"tested": len(cases), "mismatch": len(bad), "examples": bad[:12]})
    print(name, "tested", len(cases), "bad", len(bad), bad[:2])

# 定点：p1=2 数字顺序的最小反例
for name in ["P1098_88laurj5", "P1098_88laurj5_fix"]:
    inp = "2 1 1\n1-5\n"
    out, rc = run(EXE[name], inp)
    R[name]["sample_p1_2_digits"] = {
        "input": inp.strip().replace("\n", " / "),
        "expected": ok1098("1-5", 2, 1, 1), "actual": out, "rc": rc}

# ---------------------------------------------------------------- P1428 对拍
bad = []
for _ in range(300):
    n = rnd.randint(1, 100)
    arr = [rnd.randint(0, 100) for _ in range(n)]
    inp = f"{n}\n" + " ".join(map(str, arr)) + "\n"
    exp = p1428_correct(arr)
    out, rc = run(EXE["P1428_2edysvbn"], inp)
    if rc != 0 or " ".join(out.split()) != exp:
        if len(bad) < 8:
            bad.append({"n": n, "expected": exp[:80], "actual": out[:80], "rc": rc})
# 官方样例 + 全相等 + 严格递增 + 严格递减
for arr in [[4, 3, 0, 5, 1, 2], [5] * 100, list(range(100)), list(range(99, -1, -1))]:
    inp = f"{len(arr)}\n" + " ".join(map(str, arr)) + "\n"
    exp = p1428_correct(arr)
    out, rc = run(EXE["P1428_2edysvbn"], inp)
    if rc != 0 or " ".join(out.split()) != exp:
        bad.append({"n": len(arr), "expected": exp[:80], "actual": out[:80], "rc": rc})
R["P1428_2edysvbn"].update({"tested": 304, "mismatch": len(bad), "examples": bad[:8]})
print("P1428_2edysvbn bad", len(bad))

json.dump(R, open(os.path.join(D, "results.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("DONE", os.path.join(D, "results.json"))
