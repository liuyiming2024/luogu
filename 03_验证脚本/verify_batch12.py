#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 12 批 · 低频补录批（三类口径）
逐字源码取自 www.luogu.com/article/<lid>，页面吞字符按题解文字补最小外壳：
  ehkpairy j4zpxmp6 (P1618) / iv10492z 3aph5o1d utz61eus (P1469)
  xgwn9tfg (P1914) / d8583wuv (P1046) / qajlal91 (P5015)
口径：题面内 + 确定性 WA/RE + 不看评测机波动；只验核心逻辑，不判代码完整度。
"""
import os, re, json, random, subprocess, itertools, resource
from math import gcd

BASE = "/data/workspace/luogu_hack"
BUILD_DIR = os.path.join(BASE, "build", "r12")
os.makedirs(BUILD_DIR, exist_ok=True)
R = {}

def save(name, src):
    p = os.path.join(BUILD_DIR, name + ".cpp")
    open(p, "w", encoding="utf-8").write(src)
    return p

def build(name, src):
    p = save(name, src)
    exe = os.path.join(BUILD_DIR, name)
    r = subprocess.run(["g++", "-std=c++17", "-O2", "-w", "-o", exe, p],
                       capture_output=True, text=True, timeout=90)
    return exe, r.returncode, r.stderr[:400]

def run(exe, inp, timeout=8, mem_mb=None):
    def lim():
        if mem_mb:
            b = mem_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (b, b))
    try:
        p = subprocess.run([exe], input=inp, capture_output=True, text=True,
                           timeout=timeout, preexec_fn=lim)
        return p.stdout.strip(), p.returncode
    except subprocess.TimeoutExpired:
        return "<TIMEOUT>", -99
    except Exception as e:
        return "<SPAWN_FAIL:%s>" % type(e).__name__, -98

# ============================================================ A. P1618 ehkpairy
SRC_A = r"""#include <cstdio>
#include <cstring>
int a, b, c;
void red(void);
bool finish(int i, int j, int k);
int main() {
    bool no = true;
    scanf("%d%d%d", &a, &b, &c);
    red();
    for (int i = 100 + a - 100 % a; i <= 999; i += a) {
        int j, k;
        if (i / a * c > 999) break;
        j = i / a * b; k = i / a * c;
        if (finish(i, j, k)) {
            printf("%d %d %d\n", i, j, k);
            no = false;
        }
    }
    if (no) printf("No!!!");
    return 0;
}
void red(void) {
    if (a == 1) return;
    for (int i = a; i > 1; --i) {
        while (!(a % i) && !(b % i) && !(c % i))
            a /= i, b /= i, c /= i;
        if (a == 1) return;
    }
}
bool finish (int i, int j, int k) {
    bool ret = true, used[10];
    memset(used, 0, sizeof(used));
    used[i % 10] = used[i / 100] = used[i / 10 % 10] = true;
    used[j % 10] = used[j / 100] = used[j / 10 % 10] = true;
    used[k % 10] = used[k / 100] = used[k / 10 % 10] = true;
    for (int i = 1; i < 10; ++i)
        if (!used[i]) { ret = false; break; }
    return ret;
}
"""

# ============================================================ B. P1618 j4zpxmp6
SRC_B = r"""#include<bits/stdc++.h>
using namespace std;
int a,b,c;
bool check1(int n) {
    string a = to_string(n);
    if (a.size() != 3) return 0;
    for (int i = 0; i < a.size(); i++)
        for (int j = 0; j < a.size(); j++) {
            if (i != j)
                if (a[i] == a[j])
                    return 0;
            if (a[i] == '0' || a[j] == '0')
                return 0;
        }
    return 1;
}
bool check2(int n, int m) {
    string a = to_string(n), b = to_string(m);
    for (int i = 0; i < a.size(); i++)
        for (int j = 0; j < b.size(); j++)
            if (a[i] == b[j]) return 0;
    return 1;
}
int main(){
    int cnt = 0;
    cin >> a >> b >> c;
    if (a == 0 || b == 0 || c == 0) { cout << "No!!!"; return 0; }
    for (int i = 1; i <= 9; i++) {
        for (int j = 1; j <= 9; j++) {
            if (i == j) continue;
            for (int k = 1; k <= 9; k++) {
                if (i == k || j == k) continue;
                int num1 = i * 100 + j * 10 + k;
                if (num1 % a) continue;
                int num2 = num1 / a * b;
                if (num2 % b || !check1(num2) || !check2(num1, num2)) continue;
                int num3 = num2 / b * c;
                if (num3 % c || !check1(num3) || !check2(num1, num3) || !check2(num2, num3)) continue;
                cnt++;
                cout << num1 << " " << num2 << " " << num3 << "\n";
            }
        }
    }
    if (cnt == 0) cout << "No!!!";
    return 0;
}
"""

# ============================================================ C. P1469 iv10492z
SRC_C = r"""#include<bits/stdc++.h>
using namespace std;
int n;
vector<int>p;
int main()
{
scanf("%d",&n);
p.resize(n+1);
for(int i=1;i<=n;i++)
scanf("%d",&p[i]);
for(int i=2;i<=n;i++)
p[i]=p[i]^p[i-1];
printf("%d",p[n]);
return 0;
}
"""

# ============================================================ D. P1469 3aph5o1d 等价 C++（Pascal 无编译器）
SRC_D1 = r"""#include<bits/stdc++.h>
using namespace std;
int a[1000001];
int n;
void qsort_(int l,int r){
    int i=l,j=r,x=a[(l+r)/2];
    do{
        while(a[i]<x) i++;
        while(x<a[j]) j--;
        if(i<=j){ int y=a[i]; a[i]=a[j]; a[j]=y; i++; j--; }
    }while(i<=j);
    if(l<j) qsort_(l,j);
    if(i<r) qsort_(i,r);
}
int main(){
    scanf("%d",&n);
    for(int i=1;i<=n;i++) scanf("%d",&a[i]);
    qsort_(1,n);
    int i=1;
    while(i+1<=n && a[i]==a[i+1]) i+=2;
    printf("%d",a[i]);
    return 0;
}
"""
SRC_D2 = r"""#include<bits/stdc++.h>
using namespace std;
int main(){
    int n,s=0,t;
    scanf("%d",&n);
    for(int i=1;i<=n;i++){ scanf("%d",&t); s=s^t; }
    printf("%d",s);
    return 0;
}
"""

# ============================================================ E. P1469 utz61eus
SRC_E = r"""#include <iostream>
#include <cstdio>
#include <cstring>
using namespace std;
long long n,k;
int a[100000005];
int main()
{
    cin>>n;
    for(int i=1;i<=n;i++)
    {
        cin>>k;
        a[k]++;
        if(a[k]==2)
        {
            a[k]=0;
        }
    }
    for(int i=1;i<=10000000;i++)
    {
        if(a[i]==1)
        {
            cout<<i;
            break;
        }
    }
    return 0;
}
"""

# ============================================================ F. P1914 xgwn9tfg（补最小外壳）
SRC_F = r"""#include <stdio.h>
int main(){
char a[1001];
int n, i;
scanf("%d%s", &n, a);
for(i = 0; a[i] != '\0'; i++)
putchar((a[i]-'a'+n)%26+'a');
return 0;
}
"""

# ============================================================ G. P1046 d8583wuv（补最小外壳）
SRC_G = r"""#include<bits/stdc++.h>
using namespace std;
int a[15],height,ans;
int main(){
ios::sync_with_stdio(0); cin.tie(0); cout.tie(0);
for(int i=1;i<=10;i++)
cin>>a[i];
cin>>height;
for(int i=1;i<=10;i++)
if(height+30>=a[i])//判断
ans++;//累加
cout<<ans<<endl;//输出
return 0;
}
"""

# ============================================================ H. P5015 qajlal91
SRC_H = r"""#include<bits/stdc++.h>
using namespace std;
string n;
int main(){
	int cnt=0;
	getline(cin,n,'\n');
	for(int i=0;i<n.size();i++){
		if(n[i]!=' '){
			cnt++;
		}
	}
	cout<<cnt;
	return 0;
}
"""

SOURCES = {
    "P1618_ehkpairy": SRC_A, "P1618_j4zpxmp6": SRC_B,
    "P1469_iv10492z": SRC_C, "P1469_3aph5o1d_qsort": SRC_D1,
    "P1469_3aph5o1d_xor": SRC_D2, "P1469_utz61eus": SRC_E,
    "P1914_xgwn9tfg": SRC_F, "P1046_d8583wuv": SRC_G,
    "P5015_qajlal91": SRC_H,
}
EXE = {}
for k, v in SOURCES.items():
    exe, rc, err = build(k, v)
    EXE[k] = exe
    R[k] = {"compile_rc": rc, "compile_err": err, "cases": []}
    print("BUILD", k, "rc=", rc, err[:120].replace("\n", " "))

# ---------------------------------------------------------------- 独立正确解
# P1618：枚举 1..9 全排列 → (num1,num2,num3)；按 num1 升序
TRIPLES = []
for perm in itertools.permutations("123456789"):
    n1 = int("".join(perm[0:3])); n2 = int("".join(perm[3:6])); n3 = int("".join(perm[6:9]))
    TRIPLES.append((n1, n2, n3))
TRIPLES.sort()
# 预建「最简比例 -> 全部解」索引：比例成比例 <=> 各自 gcd 化简后相同
RATIO = {}
for n1, n2, n3 in TRIPLES:
    g = gcd(gcd(n1, n2), n3)
    RATIO.setdefault((n1 // g, n2 // g, n3 // g), []).append(f"{n1} {n2} {n3}")

def p1618_correct(A, B, C):
    if A == 0:
        return "No!!!"
    g = gcd(gcd(A, B), C)
    lines = RATIO.get((A // g, B // g, C // g), [])
    return "\n".join(lines) if lines else "No!!!"

def p1469_correct(arr):
    s = 0
    for x in arr: s ^= x
    return str(s)

def p1914_correct(n, s):
    return "".join(chr((ord(c) - 97 + n) % 26 + 97) for c in s)

def p1046_correct(apples, h):
    return str(sum(1 for x in apples if h + 30 >= x))

def p5015_correct(s):
    return str(len(s.replace(" ", "")))

def norm(s):
    return "\n".join(l.rstrip() for l in s.strip().splitlines() if l.strip() != "")

# ---------------------------------------------------------------- P1618 对拍
p1618_cases = []
for A, B, C in itertools.combinations(range(0, 21), 3):
    p1618_cases.append((A, B, C))
rnd = random.Random(20261122)
for _ in range(60):
    A = rnd.randint(0, 900); B = rnd.randint(A + 1, 950); C = rnd.randint(B + 1, 999)
    p1618_cases.append((A, B, C))
# 明确构造：A=0 / 非最简放大 / 官方样例
p1618_cases += [(0, 1, 2), (0, 2, 3), (2, 4, 6), (4, 6, 8), (3, 6, 9),
                (1, 2, 3), (2, 3, 4), (1, 3, 5), (5, 10, 15)]

for name in ["P1618_ehkpairy", "P1618_j4zpxmp6"]:
    bad = []
    for A, B, C in p1618_cases:
        inp = f"{A} {B} {C}\n"
        exp = p1618_correct(A, B, C)
        out, rc = run(EXE[name], inp)
        ok = (rc == 0 and norm(out) == norm(exp))
        if not ok and len(bad) < 12:
            bad.append({"input": inp.strip(), "expected": exp[:120],
                        "actual": out[:120], "rc": rc})
    R[name]["tested"] = len(p1618_cases)
    R[name]["mismatch"] = len(bad)
    R[name]["examples"] = bad
    print(name, "tested", len(p1618_cases), "bad", len(bad), bad[:2])

# 非最简放大：单独验证 2:3:4 是否有 t 为奇数的解（j4zpxmp6 的 num1%a 门槛）
amp = []
for k in range(1, 6):
    A, B, C = 2 * k, 3 * k, 4 * k
    exp = p1618_correct(A, B, C)
    if exp != "No!!!":
        out, rc = run(EXE["P1618_j4zpxmp6"], f"{A} {B} {C}\n")
        amp.append({"k": k, "input": f"{A} {B} {C}", "expected": exp,
                    "actual": out, "rc": rc, "match": norm(out) == norm(exp)})
R["P1618_j4zpxmp6"]["amplified"] = amp
print("2:3:4 放大检查:", amp)

# ---------------------------------------------------------------- P1469 对拍
p1469_cases = []
for _ in range(40):
    m = rnd.randint(0, 30)
    pair = [rnd.randint(1, 10**9) for _ in range(m)]
    arr = pair + pair + [rnd.randint(1, 10**9)]
    rnd.shuffle(arr)
    p1469_cases.append(arr)
# 大值边界（题面 ai<=1e9）
p1469_cases += [[2, 2, 1000000000], [1000000000, 1000000000, 1],
                [999999999, 999999999, 1000000000], [1], [1, 1, 2]]
# 小规模：n=1..7，值域 1..5
for n in range(1, 8, 2):
    for _ in range(4):
        pair = [rnd.randint(1, 5) for _ in range(n // 2)]
        arr = pair + pair + [rnd.randint(1, 5)]
        rnd.shuffle(arr)
        p1469_cases.append(arr)

for name in ["P1469_iv10492z", "P1469_3aph5o1d_qsort", "P1469_3aph5o1d_xor",
             "P1469_utz61eus"]:
    bad = []
    cases = p1469_cases[:22] if name == "P1469_utz61eus" else p1469_cases
    for arr in cases:
        inp = f"{len(arr)}\n" + " ".join(map(str, arr)) + "\n"
        exp = p1469_correct(arr)
        out, rc = run(EXE[name], inp, timeout=3 if name == "P1469_utz61eus" else 8)
        ok = (rc == 0 and out.strip() == exp)
        if not ok and len(bad) < 10:
            bad.append({"input_head": f"n={len(arr)} arr={arr[:6]}",
                        "expected": exp, "actual": out[:80], "rc": rc})
    R[name]["tested"] = len(cases)
    R[name]["mismatch"] = len(bad)
    R[name]["examples"] = bad
    print(name, "tested", len(cases), "bad", len(bad), bad[:2])

# utz61eus 在题面 8MB 空间限制下的实测（RLIMIT_AS）
for mb in [8, 64, 512]:
    out, rc = run(EXE["P1469_utz61eus"], "3\n2 2 1000000000\n", timeout=6, mem_mb=mb)
    R["P1469_utz61eus"].setdefault("mem_profiles", []).append(
        {"limit_mb": mb, "rc": rc, "actual": out[:60]})
print("utz61eus 内存剖面:", R["P1469_utz61eus"]["mem_profiles"])

# ---------------------------------------------------------------- P1914 对拍
bad = []
for n in range(1, 27):
    for s in ["qwe", "abcxyz", "z", "a" * 50, "".join(chr(97 + (i * 7) % 26)
                                                     for i in range(50))]:
        inp = f"{n}\n{s}\n"
        exp = p1914_correct(n, s)
        out, rc = run(EXE["P1914_xgwn9tfg"], inp)
        if rc != 0 or out != exp:
            bad.append({"input": inp.strip(), "expected": exp, "actual": out, "rc": rc})
R["P1914_xgwn9tfg"].update({"tested": 26 * 5, "mismatch": len(bad), "examples": bad[:6]})
print("P1914_xgwn9tfg bad", len(bad))

# ---------------------------------------------------------------- P1046 对拍
bad = []
for _ in range(300):
    apples = [rnd.randint(100, 300) for _ in range(10)]
    h = rnd.randint(100, 200)
    inp = " ".join(map(str, apples)) + f"\n{h}\n"
    exp = p1046_correct(apples, h)
    out, rc = run(EXE["P1046_d8583wuv"], inp)
    if rc != 0 or out.strip() != exp:
        bad.append({"input": inp.strip(), "expected": exp, "actual": out, "rc": rc})
for apples, h in [([100] * 10, 100), ([300] * 10, 100), ([130] * 10, 100),
                  ([100] * 10, 200)]:
    inp = " ".join(map(str, apples)) + f"\n{h}\n"
    exp = p1046_correct(apples, h)
    out, rc = run(EXE["P1046_d8583wuv"], inp)
    if rc != 0 or out.strip() != exp:
        bad.append({"input": inp.strip(), "expected": exp, "actual": out, "rc": rc})
R["P1046_d8583wuv"].update({"tested": 304, "mismatch": len(bad), "examples": bad[:6]})
print("P1046_d8583wuv bad", len(bad))

# ---------------------------------------------------------------- P5015 对拍
bad = []
pool = "ABCxyz0123 \t"
for _ in range(300):
    s = "".join(rnd.choice(pool) for _ in range(rnd.randint(0, 120))).replace("\t", " ")
    inp = s + "\n"
    exp = p5015_correct(s)
    out, rc = run(EXE["P5015_qajlal91"], inp)
    if rc != 0 or out.strip() != exp:
        bad.append({"input": repr(s), "expected": exp, "actual": out, "rc": rc})
for s in ["", " ", "   ", "Ca 45", "234", "a b c d e", "A  B   C"]:
    inp = s + "\n"
    exp = p5015_correct(s)
    out, rc = run(EXE["P5015_qajlal91"], inp)
    if rc != 0 or out.strip() != exp:
        bad.append({"input": repr(s), "expected": exp, "actual": out, "rc": rc})
R["P5015_qajlal91"].update({"tested": 307, "mismatch": len(bad), "examples": bad[:6]})
print("P5015_qajlal91 bad", len(bad))

json.dump(R, open(os.path.join(BUILD_DIR, "results.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("DONE", os.path.join(BUILD_DIR, "results.json"))
