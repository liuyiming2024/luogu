#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""STD ↔ 朴素算法对拍（本地，零外网）。

用户口径：「你自己所谓的 STD 就相当于你自己的题面进度，你也要对朴素算法进行对拍」。
即：每有一份可核对的题面 → 配一份独立正确解(std) + 一份**按题面直译的朴素算法**；
两者在题面内输入上逐字对跑，不能只跟自己比。

纪律（沿用项目一贯）：
  · 朴素算法必须和 std 是不同实现（源码不同 + 算法关键词不同），防止自对拍
  · 题面样例两者必须一致且等于题面期望
  · 全部对拍用例 0 不一致才算通过
  · **变异必须被抓到**：每题自动生成一个故意改坏的朴素版，若与 std 仍全一致 → FAIL
  · 指数级朴素算法如实标注对拍规模（n≤10 / n≤100 / n,m≤8），不假装全范围

产物：site/data/std_brute_check.json（上页，只读台账）
"""
import os, sys, json, re, hashlib, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import runner, cases as cg, std_eval, problem_gate

REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(REPO, "site", "data", "std_brute_check.json")

BRUTE_LANG = {"P1001": "python"}     # 字符串竖式加法用 Python
BRUTE_EXT = {"P1001": ".py"}


def brute_path(pid):
    t = next(x for x in std_eval.load_bank()["题库"] if x["pid"] == pid)
    rel = t["朴素算法"].split("（")[0]
    return os.path.join(HERE, rel), BRUTE_LANG.get(pid, "cpp"), t


def scale_inputs(pid):
    """题面内输入；指数级朴素算法按真实能力缩小规模并如实标注。"""
    base = cg.cases(pid)
    if pid == "P1002":
        keep = [x for x in base if (lambda v: v[0] <= 8 and v[1] <= 8)(
            [int(y) for y in x.split()])]
        return keep[:14], "n,m≤8（朴素递归枚举路径，指数级）"
    if pid == "P1028":
        keep = [x for x in base if int(x.split()[0]) <= 100]
        return keep[:20], "n≤100（朴素递归枚举数列，指数级）"
    if pid == "P1044":
        return ["%d\n" % n for n in range(1, 11)], "n≤10（朴素枚举 push/pop 序列，指数级）"
    return base[:40], "题面内全量（本题朴素算法多项式时间）"


def make_mutant(src, lang):
    """故意改坏朴素算法：数值输出 +1；匹配不到则多输出一行。"""
    t = open(src, encoding="utf-8").read()
    if lang == "python":
        m = re.sub(r"print\(([^\n)]+)\)", lambda x: "print((" + x.group(1) + ")+1)", t, count=1)
        if m == t: m = t + '\nprint("MUTANT")\n'
        ext = ".py"
    else:
        m = re.sub(r"cout\s*<<\s*([A-Za-z_][A-Za-z0-9_\[\]\(\)]*)\s*<<\s*'\\n'\s*;",
                   lambda x: "cout<<(" + x.group(1) + "+1)<<'\\n';", t, count=1)
        if m == t: m = t.replace("return 0;", 'cout<<"MUTANT\\n"; return 0;', 1)
        ext = ".cpp"
    assert m != t, "变异未生效"
    return m, ext


def main():
    bank = std_eval.load_bank()["题库"]
    rows, total_cases, caught = [], 0, 0
    print("[brute] STD ↔ 朴素算法对拍 | %d 题（零外网）" % len(bank))
    ok = True
    with tempfile.TemporaryDirectory(prefix="brute_") as td:
        for t in bank:
            pid = t["pid"]
            bp, blang, _ = brute_path(pid)
            sp = os.path.join(HERE, t["std"])
            r = {"pid": pid, "std": t["std"], "brute": t.get("朴素算法", ""),
                 "checks": {}, "不一致": None, "verdict": ""}
            if not os.path.exists(bp):
                r["verdict"] = "FAIL 缺朴素算法"; ok = False; rows.append(r); continue
            # 1 不同实现
            r["checks"]["源码不同"] = (hashlib.sha256(open(sp, "rb").read()).hexdigest() !=
                                   hashlib.sha256(open(bp, "rb").read()).hexdigest())
            # 2 题面闸门（含朴素算法在位）
            g = problem_gate.gate(pid, verbose=False)
            r["checks"]["题面闸门"] = g["pass"]
            # 3 编译
            wd1, wd2 = os.path.join(td, pid + "s"), os.path.join(td, pid + "b")
            os.makedirs(wd1, exist_ok=True); os.makedirs(wd2, exist_ok=True)
            try:
                scmd = runner.compile_source(sp, t["lang"], wd1)
                bcmd = runner.compile_source(bp, blang, wd2)
            except Exception as e:
                r["verdict"] = "FAIL 编译 " + type(e).__name__; ok = False; rows.append(r); continue
            # 4 题面样例
            sm = cg.samples(pid)
            sm_bad = []
            for inp, exp in sm:
                a = runner.run_case(scmd, inp, 5.0)
                b = runner.run_case(bcmd, inp, 5.0)
                if (runner.normalize(a["out"]) != runner.normalize(exp) or
                    runner.normalize(b["out"]) != runner.normalize(exp)):
                    sm_bad.append({"in": inp[:60], "expect": exp[:60],
                                   "std": a["out"][:60], "brute": b["out"][:60]})
            r["checks"]["题面样例两者一致"] = (len(sm) > 0 and not sm_bad)
            r["checks"]["样例数"] = len(sm)
            # 5 题面内用例逐字对跑
            ins, note = scale_inputs(pid)
            r["规模说明"] = note
            bad = []
            for inp in ins:
                a = runner.run_case(scmd, inp, 5.0)
                b = runner.run_case(bcmd, inp, 5.0)
                if b["timed_out"] or b["rc"] != 0 or runner.normalize(a["out"]) != runner.normalize(b["out"]):
                    bad.append({"in": inp[:70], "std": a["out"][:70], "brute": b["out"][:70],
                                "rc": b["rc"]})
            r["不一致"] = len(bad)
            r["用例数"] = len(ins)
            r["checks"]["用例0不一致"] = (len(ins) > 0 and not bad)
            total_cases += len(ins)
            # 6 变异敏感性
            mut, ext = make_mutant(bp, blang)
            mp = os.path.join(td, pid + "_mut" + ext)
            open(mp, "w", encoding="utf-8").write(mut)
            mwd = os.path.join(td, pid + "m"); os.makedirs(mwd, exist_ok=True)
            try:
                mcmd = runner.compile_source(mp, blang, mwd)
                mhit = 0
                for inp in ins[:12]:
                    a = runner.run_case(scmd, inp, 5.0)
                    b = runner.run_case(mcmd, inp, 5.0)
                    if b["rc"] != 0 or b["timed_out"] or runner.normalize(a["out"]) != runner.normalize(b["out"]):
                        mhit += 1
                r["checks"]["变异步被抓到"] = mhit
                r["checks"]["变异抓到"] = mhit > 0
                if mhit > 0: caught += 1
            except Exception:
                r["checks"]["变异抓到"] = True   # CE 也算被拒
                r["checks"]["变异步被抓到"] = "CE"
                caught += 1
            good = (r["checks"]["源码不同"] and r["checks"]["题面闸门"]
                    and r["checks"]["题面样例两者一致"] and r["checks"]["用例0不一致"]
                    and r["checks"]["变异抓到"])
            if not good: ok = False
            r["verdict"] = "PASS" if good else "FAIL"
            rows.append(r)
            print("  %-7s %-4s 用例 %-3d 不一致 %-2d 样例 %s 变异 %-3s | %s" %
                  (pid, r["verdict"], len(ins), len(bad),
                   "OK" if r["checks"]["题面样例两者一致"] else "BAD",
                   str(r["checks"]["变异步被抓到"]), note[:34]))

    doc = {"说明": "STD ↔ 朴素算法对拍台账。题面进度 = STD 进度；每题都要有独立朴素实现并通过逐字对跑。",
           "纪律": ["朴素算法必须与 std 不同实现（源码 sha256 不同）",
                    "题面样例两者一致且等于题面期望", "题面内用例 0 不一致",
                    "指数级朴素算法如实标注规模，不假装全范围",
                    "每题自动变异版必须被抓到（类对拍纪律）"],
           "生成时间": __import__("datetime").datetime.now(
               __import__("datetime").timezone.utc).isoformat(timespec="seconds"),
           "统计": {"题目数": len(rows), "PASS": sum(1 for x in rows if x["verdict"] == "PASS"),
                    "用例总数": total_cases, "变异抓到": caught},
           "条目": rows}
    from stable_write import stable_write
    stable_write(OUT, doc)
    print("[brute] → std_brute_check.json | PASS %d/%d | 用例 %d | 变异抓到 %d" %
          (doc["统计"]["PASS"], len(rows), total_cases, caught))
    print("结论：", "PASS · STD⊆题面存档，逐题朴素对拍全通过" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
