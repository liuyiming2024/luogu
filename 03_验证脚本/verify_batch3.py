#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第 3 批验证（口径同第 2 批：题面内 / 确定性 WA-RE / 不看评测机波动）
逐字源码来源：
  P5638 nzmytiez  https://www.luogu.com/article/nzmytiez
  P1803 dmza5ifn  https://www.luogu.com/article/dmza5ifn
"""
import os, json, random, subprocess

BASE = "/data/workspace/luogu_hack/build/r3"
os.makedirs(BASE, exist_ok=True)
R = {}

SOL = {}

# 文章把「核心代码 / 头文件初始化 / 读入 / 输出 / return」分 5 段给出，按文章顺序拼成完整程序
SOL["P5638_nzmytiez"] = r"""
#include <bits/stdc++.h>
using namespace std;
int n, k, a, b;
long long cxk[1000010], ans, maxx, ans2;
int main(){
 ios::sync_with_stdio(false);
 cin >> n >> k;
 for (int i = 1; i <= n - 1; i++) cin >> cxk[i], ans += cxk[i];
 a = 0, b = a + k;
 for (int i = a; i < b; i++) ans2 += cxk[i];
 for (int i = 1; i <= n - k; i++) {
  ans2 = ans2 + cxk[b] - cxk[a];
  maxx = max(maxx, ans2);
  a++, b++;
 }
 cout << ans - maxx;
 return 0;
}
"""

# 原页面 main 写成老式 `main(){`，C++17 下补 int 返回类型；其余逐字保留
SOL["P1803_dmza5ifn"] = r"""
#include <stdio.h>
#include <stdlib.h>
int time[1000000][2];
int cmp1(const void *a,const void *b){ return ((int*)a)[0]-((int*)b)[0]; }
int cmp2(const void *a,const void *b){ return ((int*)a)[1]-((int*)b)[1]; }
int main(){
 int n,flag,pos = 0,count = 1;
 int i,j;
 scanf("%d", &n);
 for(i = 0; i < n; i++){ scanf("%d %d", &time[i][0],&time[i][1]); }
 qsort(time,n,sizeof(int)*2,cmp1);
 qsort(time,n,sizeof(int)*2,cmp2);
 for(i = 1; i < n; i++){
  flag = 1;
  if((time[i][0]>=time[pos][0]&&time[i][1]<=time[pos][1]) ||
     (time[i][1]>time[pos][0]&&time[i][1]<=time[pos][1]) ||
     (time[i][0]>=time[pos][0]&&time[i][0]<time[pos][1]) ||
     (time[pos][0]>time[i][0]&&time[pos][1]<time[i][1])){
   flag = 0;
  }
  if(flag == 1){ pos = i; count++; }
 }
 printf("%d", count);
 return 0;
}
"""

def build(name):
    src = os.path.join(BASE, name + ".cpp")
    exe = os.path.join(BASE, name)
    with open(src, "w", encoding="utf-8") as f:
        f.write(SOL[name])
    p = subprocess.run(["g++", "-std=c++17", "-O2", "-o", exe, src],
                       capture_output=True, text=True)
    return exe, (p.stderr[:600] if p.returncode != 0 else "")

def run(exe, inp, timeout=25):
    p = subprocess.run([exe], input=inp, capture_output=True, text=True, timeout=timeout)
    return p.stdout.strip(), p.returncode, p.stderr.strip()[:150]

# ================================================================= P5638
def p5638_correct(n, k, edges):
    """edges[1..n-1]：城市 i -> i+1 的耗时。传送 p -> clamp(p+k, 1..n)，免费。"""
    total = sum(edges[1:n])
    best = 0
    for p in range(1, n):
        dest = min(p + k, n)
        if dest <= p:
            continue
        best = max(best, sum(edges[p:dest]))
    return total - best

exe, err = build("P5638_nzmytiez")
R["P5638_nzmytiez"] = {"compile_error": err, "cases": [], "random_mismatch": 0, "random_tested": 0}
if not err:
    def mk(n, k, edges):
        return f"{n} {k}\n" + " ".join(str(edges[i]) for i in range(1, n)) + "\n"
    fixed = [
        ("官方样例1 (k=0)", 4, 0, [0, 1, 2, 3]),
        ("官方样例2 (k=1)", 4, 1, [0, 1, 2, 3]),
        ("H-008 最小反例 k>=n", 2, 100, [0, 5]),
        ("H-009 k>n (n=3)", 3, 5, [0, 2, 3]),
        ("H-010 k=n (n=4)", 4, 4, [0, 7, 1, 9]),
        ("k=n-1 对照组", 4, 3, [0, 7, 1, 9]),
        ("k=1 对照组", 5, 1, [0, 10, 10, 1, 1]),
        ("k=2 对照组", 5, 2, [0, 10, 10, 1, 1]),
    ]
    for label, n, k, e in fixed:
        exp = p5638_correct(n, k, e)
        out, rc, se = run(exe, mk(n, k, e))
        R["P5638_nzmytiez"]["cases"].append({
            "label": label, "input": mk(n, k, e).strip().replace("\n", " / "),
            "expected": exp, "actual": out, "rc": rc,
            "hacked": out != str(exp)})
    # 随机小数据（含 k>=n）
    rnd = random.Random(20261120)
    bad = []
    for t in range(200):
        n = rnd.randint(2, 25)
        k = rnd.randint(1, 35)
        e = [0] + [rnd.randint(1, 100) for _ in range(n - 1)]
        exp = p5638_correct(n, k, e)
        out, rc, se = run(exe, mk(n, k, e))
        R["P5638_nzmytiez"]["random_tested"] += 1
        if out != str(exp):
            R["P5638_nzmytiez"]["random_mismatch"] += 1
            if len(bad) < 4:
                bad.append({"input": mk(n, k, e).strip().replace("\n", " / "),
                            "expected": exp, "actual": out})
    R["P5638_nzmytiez"]["random_examples"] = bad

# ================================================================= P1803
def p1803_brute(intervals):
    """枚举所有子集，求最大两两不重叠区间数（独立正确解）"""
    n = len(intervals)
    best = 0
    for mask in range(1 << n):
        chosen = [intervals[i] for i in range(n) if mask >> i & 1]
        chosen.sort(key=lambda x: x[1])
        ok = all(chosen[t - 1][1] <= chosen[t][0] for t in range(1, len(chosen)))
        if ok:
            best = max(best, len(chosen))
    return best

exe, err = build("P1803_dmza5ifn")
R["P1803_dmza5ifn"] = {"compile_error": err, "cases": [], "random_mismatch": 0, "random_tested": 0}
if not err:
    def mk(intervals):
        return f"{len(intervals)}\n" + "".join(f"{a} {b}\n" for a, b in intervals)
    fixed = [
        ("官方样例", [(0, 2), (2, 4), (1, 3)]),
        ("短区间错觉反例", [(0, 5), (5, 10), (4, 6)]),
        ("早开始长区间", [(0, 10), (3, 4), (5, 6), (7, 8), (9, 10)]),
        ("单点衔接链", [(1, 2), (2, 4), (4, 6), (6, 8), (8, 10)]),
    ]
    for label, iv in fixed:
        exp = p1803_brute(iv)
        out, rc, se = run(exe, mk(iv))
        R["P1803_dmza5ifn"]["cases"].append({
            "label": label, "input": mk(iv).strip().replace("\n", " / "),
            "expected": exp, "actual": out, "rc": rc,
            "hacked": out != str(exp)})
    rnd = random.Random(777)
    bad = []
    for t in range(400):
        n = rnd.randint(1, 12)
        iv = []
        for _ in range(n):
            a = rnd.randint(0, 12); b = rnd.randint(a + 1, 14)
            iv.append((a, b))
        exp = p1803_brute(iv)
        out, rc, se = run(exe, mk(iv))
        R["P1803_dmza5ifn"]["random_tested"] += 1
        if out != str(exp):
            R["P1803_dmza5ifn"]["random_mismatch"] += 1
            if len(bad) < 5:
                bad.append({"input": mk(iv).strip().replace("\n", " / "),
                            "expected": exp, "actual": out})
    R["P1803_dmza5ifn"]["random_examples"] = bad

with open(os.path.join(BASE, "results.json"), "w", encoding="utf-8") as f:
    json.dump(R, f, ensure_ascii=False, indent=2)
print(json.dumps(R, ensure_ascii=False, indent=2))
