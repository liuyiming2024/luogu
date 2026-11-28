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

BRUTE_LANG = {"P1001": "python", "P1022": "python", "P1026": "python",
              "P1034": "python", "P1036": "python", "P1037": "python",
              "P1039": "python", "P1040": "python", "P1041": "python",
              "P1042": "python", "P1043": "python", "P1045": "python",
              "P1046": "python", "P1047": "python", "P1048": "python",
              "P1049": "python", "P1050": "python", "P1051": "python",
              "P1053": "python", "P1054": "python", "P1055": "python",
              "P1056": "python", "P1057": "python", "P1058": "python",
              "P1060": "python", "P1061": "python", "P1062": "python",
              "P1063": "python", "P1064": "python"}
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
    if pid == "P1003":
        return base[:20], "坐标 ≤64（朴素逐格涂色，网格上限 128，不假装全范围）"
    if pid == "P1024":
        return base[:16], "整数根构造（朴素 0.001 步长扫描，不二分）"
    if pid == "P1025":
        return [x for x in base if int(x.split()[0]) <= 30][:16], "n≤30（朴素 DFS 枚举非降序拆分，指数级）"
    if pid == "P1029":
        return [x for x in base if int(x.split()[1]) <= 2000][:16], "y0≤2000（朴素双重枚举 P,Q）"
    if pid == "P1030":
        return base[:20], "节点 ≤8（朴素显式建树 + 栈遍历）"
    if pid == "P1031":
        keep = [x for x in base if (lambda L: int(L[0]) <= 4 and
                sum(map(int, L[1].split())) <= 12)(x.strip().splitlines())]
        return keep[:12], "N≤4 且总数≤12（朴素 BFS 状态搜索，指数级）"
    if pid == "P1022":
        return base[:20], "题面内方程（朴素数值二分求根，200 次迭代）"
    if pid == "P1023":
        return base[:12], "价位表小规模（朴素显式销量表逐项算利润）"
    if pid == "P1026":
        return [x for x in base if int(x.strip().splitlines()[0].split()[1]) <= 3][:10], "p=1 且 k≤3（朴素枚举全部切点组合，组合数指数级）"
    if pid == "P1027":
        return base[:12], "S≤4（朴素 Floyd-Warshall 全源最短路，点数三次增长）"
    if pid == "P1032":
        return base[:12], "短串 + 2~3 条规则（朴素迭代加深 DFS）"
    if pid == "P1033":
        return base[:12], "位移网格 20001 点（数值扫描，非解析区间；用例避开临界边界）"
    if pid == "P1034":
        # 全量 40 组：曾在此抓到「区间 DP 对混合方向划分不精确」的真 bug，保留为回归检查点
        return base[:40], "n≤7、k≤4 全量（子集枚举 k^n + 显式矩形分离检查，精确解）"
    if pid == "P1035":
        return base[:15], "k=1..15 全量（朴素二分 + Kahan 补偿重算）"
    if pid == "P1036":
        return base[:16], "n≤12、k≤4（Python 组合枚举 + Miller-Rabin）"
    if pid == "P1037":
        return base[:20], "n≤8 位（Python BFS 闭包 + 原生大整数）"
    if pid == "P1038":
        return base[:20], "n≤8 的 DAG（反图 DFS 记忆化；输入层 U=0 避免阈值歧义）"
    if pid == "P1039":
        return base[:10], "M≤6（显式枚举 2^M 说谎者标签组合）"
    if pid == "P1040":
        return base[:16], "n≤8（递归枚举全部二叉树，Catalan 指数级）"
    if pid == "P1041":
        return base[:8], "n≤9 的小树（bitmask 状态搜索，指数级；疑似错题如实标注）"
    if pid == "P1042":
        return base[:20], "题面内记录（Python 递归切出最早完局）"
    if pid == "P1043":
        return base[:40], "n≤8、m≤3 全量（枚举起点×切点组合，指数级）"
    if pid == "P1045":
        return base[:40], "P≤20000 全量（Python 内置大整数展开，不假装覆盖 P<3100000）"
    if pid == "P1046":
        return base[:40], "题面内全量（排序 + 二分上界计数）"
    if pid == "P1047":
        return base[:40], "题面内全量（显式区间排序合并，不用差分）"
    if pid == "P1048":
        return base[:40], "M≤12 全量（枚举 2^M 子集，指数级）"
    if pid == "P1049":
        return base[:40], "题面内全量（集合 BFS 扩展可达体积，非 DP 数组）"
    if pid == "P1050":
        return base[:40], "k≤3 全量（逐次乘幂观察循环，状态数 10^k；不假装覆盖 k≤100）"
    if pid == "P1051":
        return base[:40], "题面内全量（规则表 + 生成器求和）"
    if pid == "P1052":
        return base[:40], "L≤300 全量（**不压缩**的原始坐标 DP，不假装覆盖 L≤10^9）"
    if pid == "P1053":
        return base[:40], "n≤30 全量（显式枚举方向×全部旋转，O(n²)；不假装覆盖 n≤50000）"
    if pid == "P1054":
        return base[:40], "构造式表达式全量（栈式优先级 + 精确大整数对递归下降模素数指纹）"
    if pid == "P1055":
        return base[:40], "题面内全量（按 '-' 分段 + zip 权重 + reduce）"
    if pid == "P1056":
        return base[:40], "M,N≤8 全量（枚举全部横/纵通道组合，不假装覆盖 M,N≤1000）"
    if pid == "P1057":
        return base[:40], "m≤12 全量（枚举 2^m 传球方向序列，不假装覆盖 m≤30）"
    if pid == "P1058":
        return base[:40], "m,n≤4、高度≤3 全量（逐像素反查 + 显式棱位置表，不假装覆盖 m,n≤50）"
    if pid == "P1060":
        return base[:40], "m≤12 全量（枚举 2^m 购买子集，不假装覆盖 m<25）"
    if pid == "P1061":
        return base[:40], "w≤6、t-s≤9 全量（枚举全部严格递增组合并排序）"
    if pid == "P1062":
        return base[:40], "k=3..15、10≤N≤1000 全量（枚举全部 k 幂子集和排序，不依赖二进制映射）"
    if pid == "P1063":
        return base[:40], "n≤6 全量（递归枚举全部相邻聚合顺序，不假装覆盖 n≤100）"
    if pid == "P1064":
        return base[:40], "m≤10 全量（枚举 2^m 子集 + 显式主件依赖检查，不假装覆盖 m≤60）"
    return base[:40], "题面内全量（本题朴素算法多项式时间）"


def make_mutant(src, lang):
    """故意改坏朴素算法：数值输出 +1；匹配不到则多输出一行。"""
    t = open(src, encoding="utf-8").read()
    if lang == "python":
        # 不猜 print 语句形态：末尾追加一行额外输出，必然被逐行 normalize 抓到
        m = t.rstrip() + '\nprint("MUTANT")\n'
        ext = ".py"
    else:
        m = re.sub(r"cout\s*<<\s*([A-Za-z_][A-Za-z0-9_\[\]\(\)]*)\s*<<\s*'\\n'\s*;",
                   lambda x: "cout<<(" + x.group(1) + "+1)<<'\\n';", t, count=1)
        if m == t: m = t.replace("return 0;", 'cout<<"MUTANT\\n"; return 0;', 1)
        ext = ".cpp"
    assert m != t, "变异未生效"
    return m, ext


def mutant_fallback(src, lang):
    """兜底变异：末尾多输出一行（任何输出类型都能运行，必然被逐行 normalize 抓到）。"""
    t = open(src, encoding="utf-8").read().rstrip()
    if lang == "python":
        return t + '\nprint("MUTANT")\n', ".py"
    m = t.replace("return 0;", 'cout<<"MUTANT\\n"; return 0;', 1)
    if m == t: m = t + '\nint main(){cout<<"MUTANT\\n";}\n'
    return m, ".cpp"


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
                try:
                    mcmd = runner.compile_source(mp, blang, mwd)
                except Exception:
                    # 数值 +1 变异对 string 输出会 CE；回退到「多输出一行」的可运行变异，
                    # 保证变异是「跑起来后被输出比对抓到」，而不是只靠编译失败。
                    m2, ext2 = mutant_fallback(bp, blang)
                    mp2 = os.path.join(td, pid + "_mut2" + ext2)
                    open(mp2, "w", encoding="utf-8").write(m2)
                    mwd2 = os.path.join(td, pid + "m2"); os.makedirs(mwd2, exist_ok=True)
                    mcmd = runner.compile_source(mp2, blang, mwd2)
                    r["checks"]["变异方式"] = "追加输出行（+1 变异 CE 后回退）"
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
                r["checks"]["变异抓到"] = False
                r["checks"]["变异步被抓到"] = "两次变异均不可用"
                ok = False
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
