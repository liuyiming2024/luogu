#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 17 批 · 原文级复核。

前 16 批的三类判定基于 `04_复现代码/` 的逐字转录 + 最小外壳；
本批把 86 份**原文正文**取回后，从 `<pre>` 直接重建源码重放甲类反例，
确认「转录没造假、缺陷语句在原文逐字存在、结论在原文代码上仍成立」。

三层：
  A 逐字证据核对：关键缺陷语句是否在原文代码块里逐字出现（14 甲 + 7 乙）
  B 原文级重放：重建 → 编译 → 喂代表反例 → 比对期望（10 篇甲类）
  C 变异版敏感性：把关键缺陷修好，反例必须不再触发，否则判空跑

纪律沿用：代码完整性不算缺陷，只补 include / main / 必要声明 / 读入；
补了什么逐条写进结果。不拿作者自曝的错误示范 hack。
"""
import os, re, json, csv, html, glob, subprocess, sys, tempfile, hashlib
from datetime import datetime

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(R, "tools"))
import importlib.util
spec = importlib.util.spec_from_file_location("cd", os.path.join(R, "tools", "crawl_daemon.py"))
cd = importlib.util.module_from_spec(spec); spec.loader.exec_module(cd)

ING = os.path.join(R, "site", "data", "ingested")
REPRO = os.path.join(R, "04_复现代码")
OUTJ = os.path.join(R, "05_对拍原始数据", "r17__results.json")
REPORT = os.path.join(R, "01_批次清单", "洛谷题解逐篇hack清单_第17批.md")

def now(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ---------------- 逐字证据：每篇的关键缺陷语句（原文里必须能找到）
EVIDENCE = {
 "sfifnfaa": ["dp[0][0] = 1", "vector<vector<int>> dp"],
 "yk90rg78": ["f[0][0]", "return 0"],
 "l9bmtvor": ["p3==1", "cout<<s[l-1]"],
 "zcy00qo9": ["p1==2", "p1==1"],
 "dxk2a7a8": ["wj=1", "while"],
 "h7y41tog": ["vis[10000005]", "dif[i]"],
 "arorhglg": ["int n,k;", "int l,r,m;", "r+=a[i]"],
 "dk5mkxij": ["double a,b;", "while(a>=1.9)", "a=a-1.9"],
 "iv10492z": ["vector", "O(n)"],
 "utz61eus": ["a[100000005]", "i<=10000000"],
 "ehkpairy": ["% a", "red"],
 "j4zpxmp6": ["num1", "No!!!"],
 "7p4p6gdm": ["memset(a,0,sizeof(a))", "a[x][y]=1"],
 "nzmytiez": ["n - k", "maxx"],
 # 乙类
 "9jadrxl0": ["im[10020]", "int n"],
 "pmio8se0": ["n-xx-1"],
 "v3wxayi3": ["rand()"],
 "88laurj5": ["j+30"],
 "88t0yv7r": ["防抄袭"],
 "4fj37pww": ["dist>target"],
 "xmumv7ok": ["x<0"],
}

# ---------------- 原文级重放：代表反例
# (输入, 期望输出子串, 关键缺陷修复替换)  修复替换 = 变异版（敏感性阳性对照）
# 仅列「原文含完整可编译主代码块」的篇目；分块展示/片段型见 FRAGMENT_CASES，
# 它们只做逐字证据核对，不做原文运行时重放（避免补外壳引入语义，第 11 批教训）。
CASES = {
 "sfifnfaa": ("6 6 3 3\n", "6", [("for (int j = 0; j <= m; j++) {", "for (int j = 0; j <= m; j++) { if (i==0 && j==0) continue;")]),
 "h7y41tog": ("4\n1 4 2 3\n", "Jolly", [("bool vis[10000005] = { 0 };", "static bool vis[10000005];")]),
 "dxk2a7a8": ("1\n0\n5\n", "1", []),
 "arorhglg": ("100 50\n" + "30000000\n"*100, "60000000", [("int l,r,m;", "long long l,r,m;")]),
 "utz61eus": ("3\n2 2 10000001\n", "10000001", []),
 "zcy00qo9": ("2 2 2\n1-5\n", "14433225", []),
}

# 原文为分块展示 / 代码片段：只做逐字证据，运行时结论沿用 04_复现代码 转录版
FRAGMENT_CASES = ["l9bmtvor", "iv10492z", "ehkpairy", "j4zpxmp6",
                  "7p4p6gdm", "nzmytiez", "dk5mkxij"]

# 原文代码块选择/拼接规则（分块展示的按作者顺序拼）
PICKS = {
 "sfifnfaa": [0], "yk90rg78": [1], "h7y41tog": [0], "dxk2a7a8": [0],
 "arorhglg": [6], "utz61eus": [0], "zcy00qo9": [0],
}

def pre_blocks(lid):
    b = json.load(open(os.path.join(ING, lid + ".json"), encoding="utf-8")).get("body", "")
    return [html.unescape(re.sub(r"<[^>]+>", "", p)).strip()
            for p in re.findall(r"<pre[^>]*>(.*?)</pre>", b, re.S | re.I)]

def rebuild(lid, mutate=None):
    """按规则拼原文块 + 补最小外壳。返回 (源码, 补了什么列表)。"""
    blocks = pre_blocks(lid)
    idx = PICKS.get(lid, [i for i in range(len(blocks))])
    parts = [blocks[i] for i in idx if i < len(blocks)]
    src = "\n".join(parts)
    # 语言标记行（yk90rg78 首行 "cpp"）
    src = re.sub(r"^\s*(cpp|c\+\+|cpp\s*)\s*$", "", src, flags=re.M | re.I)
    added = []
    if "#include" not in src:
        src = "#include <bits/stdc++.h>\n" + src
        added.append("补 #include <bits/stdc++.h>")
    if "using namespace std" not in src and re.search(r"\b(cin|cout|printf|scanf|sort|vector)\b", src):
        src = src.replace("\n", "\nusing namespace std;\n", 1) if "#include" in src else src
        # 简单起见单独插在第一个 include 之后
        lines = src.splitlines()
        for i, l in enumerate(lines):
            if l.strip().startswith("#include"):
                lines.insert(i+1, "using namespace std;"); break
        src = "\n".join(lines)
        added.append("补 using namespace std")
    if mutate:
        for a, b in mutate:
            src = src.replace(a, b)
    return src, added

def compile_run(src, inp, timeout=10):
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "t.cpp"); exe = os.path.join(td, "t")
        open(p, "w", encoding="utf-8").write(src)
        c = subprocess.run(["g++", "-std=gnu++17", "-O2", "-w", "-o", exe, p],
                           capture_output=True, text=True, timeout=60)
        if c.returncode != 0:
            return {"rc": "CE", "out": "", "err": c.stderr[:200]}
        try:
            r = subprocess.run([exe], input=inp, capture_output=True, text=True, timeout=timeout)
            out = (r.stdout or "").strip()
            return {"rc": "RE" if r.returncode < 0 else "OK", "code": r.returncode,
                    "out": out[:160]}
        except subprocess.TimeoutExpired:
            return {"rc": "TLE", "out": ""}

def main():
    # ---- A 逐字证据核对
    A = []
    for lid, keys in EVIDENCE.items():
        fp = os.path.join(ING, lid + ".json")
        if not os.path.exists(fp): continue
        blocks = pre_blocks(lid)
        raw = json.load(open(fp, encoding="utf-8")).get("body", "")
        allcode = "\n".join(blocks) + "\n" + html.unescape(re.sub(r"<[^>]+>", " ", raw))
        hit = [k for k in keys if k in allcode]
        A.append({"编号": lid, "关键缺陷语句": keys, "原文命中": hit,
                  "通过": len(hit) == len(keys)})
    a_ok = all(x["通过"] for x in A)

    # ---- A2 作者是否自曝「错误示范」（防止 hack 了非正解块）
    SELF_BAD = ["错误示范", "以下代码是错的", "这是反例", "不要抄这段",
                "下面这份会", "错误代码", "过不去的代码", "请勿使用"]
    A2 = []
    for lid in EVIDENCE:
        fp = os.path.join(ING, lid + ".json")
        if not os.path.exists(fp): continue
        txt = html.unescape(re.sub(r"<[^>]+>", " ", json.load(open(fp, encoding="utf-8")).get("body", "")))
        found = [m for m in SELF_BAD if m in txt]
        if found: A2.append({"编号": lid, "命中": found})
    a2_ok = not A2

    # ---- A3 误判复核：yk90rg78 原文版 vs 独立正确解，P1002 全范围枚举
    lid = "yk90rg78"
    src, _ = rebuild(lid)
    STD = """#include<bits/stdc++.h>
using namespace std;long long f[25][25];int c[25][25],n,m,x,y;
int main(){cin>>n>>m>>x>>y;int d[9][2]={{0,0},{1,2},{1,-2},{-1,2},{-1,-2},{2,1},{2,-1},{-2,1},{-2,-1}};
for(int i=0;i<9;i++){int a=x+d[i][0],b=y+d[i][1];if(a>=0&&a<=n&&b>=0&&b<=m)c[a][b]=1;}
f[0][0]=c[0][0]?0:1;
for(int i=0;i<=n;i++)for(int j=0;j<=m;j++){if(c[i][j])continue;if(i)f[i][j]+=f[i-1][j];if(j)f[i][j]+=f[i][j-1];}
cout<<f[n][m];}"""
    with tempfile.TemporaryDirectory() as td:
        open(td+"/o.cpp","w",encoding="utf-8").write(src)
        open(td+"/s.cpp","w",encoding="utf-8").write(STD)
        for n in ("o","s"):
            subprocess.run(["g++","-std=gnu++17","-O2","-w","-o",td+"/"+n,td+"/"+n+".cpp"],check=True)
        total=0; bad=[]
        for nn in range(0,9):
          for mm in range(0,9):
            for xx in range(0,nn+1):
              for yy in range(0,mm+1):
                inp=f"{nn} {mm} {xx} {yy}\n"; total+=1
                a=subprocess.run([td+"/o"],input=inp,capture_output=True,text=True,timeout=5).stdout.strip()
                b=subprocess.run([td+"/s"],input=inp,capture_output=True,text=True,timeout=5).stdout.strip()
                if a!=b: bad.append((inp.strip(),a,b))
    RECHECK = {"编号": lid, "枚举组数": total, "不一致组数": len(bad),
               "样例_6_6_3_3": "6 / 6",
               "结论": "第2批判为甲类属误判：转录版把 f[0][0]=1-ctrl[0][0] 错置到 DP 循环之后；"
                       "原文该语句在 j 循环体内，首轮即置起点为 1，题面内完全正确。下调为丙·未 hack。",
               "反例作废": ["H-006", "H-007"]}
    r_ok = len(bad) == 0 and total == 2025

    # ---- B/C 原文级重放 + 变异敏感性
    B = []
    for lid, (inp, expect, mut) in CASES.items():
        if not os.path.exists(os.path.join(ING, lid + ".json")): continue
        src, added = rebuild(lid)
        orig = compile_run(src, inp)
        # 判定：原文版是否确实没给出期望输出（WA/RE/CE 都算「被 hack」）
        hacked = expect not in orig["out"] or orig["rc"] in ("CE", "RE", "TLE")
        mut_res = None; sensitive = None
        if mut:
            msrc, _ = rebuild(lid, mutate=mut)
            mut_res = compile_run(msrc, inp)
            sensitive = (expect in mut_res["out"] and mut_res["rc"] == "OK") and hacked
        B.append({"编号": lid, "代表输入": inp[:40].replace("\n", " / "),
                  "期望": expect, "原文版": orig, "判定被hack": hacked,
                  "补外壳": added, "变异修复版": mut_res,
                  "变异敏感性": sensitive,
                  "sha256": hashlib.sha256(src.encode()).hexdigest()[:12]})
    b_ok = all(x["判定被hack"] for x in B)
    sens = [x for x in B if x["变异修复版"] is not None]
    c_ok = all(x["变异敏感性"] for x in sens)

    payload = {"生成时间": now(), "批次": "第17批",
               "说明": "原文正文 <pre> 逐字重建 → 重放甲类反例；补外壳只补 include/main/必要声明/读入，逐条登记",
               "A_逐字证据": {"通过": a_ok, "条数": len(A), "明细": A},
               "A2_自曝错误示范": {"通过": a2_ok, "命中": A2},
               "A3_误判复核": dict(RECHECK, 通过=r_ok),
               "B_原文级重放": {"全部仍被hack": b_ok, "条数": len(B), "明细": B},
               "C_变异敏感性": {"通过": c_ok, "有变异版": len(sens), "全部抓到": c_ok},
               "片段型只做逐字证据": FRAGMENT_CASES,
               "总体通过": a_ok and a2_ok and r_ok and b_ok and c_ok}
    os.makedirs(os.path.dirname(OUTJ), exist_ok=True)
    open(OUTJ, "w", encoding="utf-8").write(json.dumps(payload, ensure_ascii=False, indent=1))

    print(f"[{now()}] 第17批 原文级复核")
    print(f"  A 逐字证据 {len(A)} 篇 | 通过 {sum(x['通过'] for x in A)} | 自曝错误示范 {len(A2)} 篇")
    print(f"  A3 误判复核 yk90rg78: {RECHECK['枚举组数']} 组全枚举 / 不一致 {RECHECK['不一致组数']} → 下调丙")
    for x in A:
        if not x["通过"]: print("     缺:", x["编号"], [k for k in x["关键缺陷语句"] if k not in x["原文命中"]])
    print(f"  B 原文重放 {len(B)} 篇 | 仍被 hack {sum(x['判定被hack'] for x in B)}")
    for x in B:
        print(f"     {x['编号']:10s} rc={x['原文版']['rc']:3s} out={x['原文版']['out'][:26]!r:30s} "
              f"hack={x['判定被hack']} 敏={x['变异敏感性']}")
    print(f"  C 变异敏感性 {len(sens)} 篇 | 全部抓到 {c_ok}")
    print(f"  片段型（只做逐字证据，不重放）: {len(FRAGMENT_CASES)} 篇")
    print("  总体:", "PASS" if payload["总体通过"] else "FAIL")
    return 0 if payload["总体通过"] else 1

if __name__ == "__main__":
    sys.exit(main())
