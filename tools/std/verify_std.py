#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""std 流程的「类对拍」验证：不能只证明跑过了，得证明测试集有分辨力。

每个变异实现都必须被抓到；若有变体被误放进候选，判 FAIL。
零外网、零写入仓库（台账只在 std_pipeline 里生成）。
"""
import os, sys, json, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import std_eval, runner, problem_gate

FIX = os.path.join(HERE, "fixtures")
ok = True


def check(label, cond, extra=""):
    global ok
    print(("  ✓ " if cond else "  ✗ ") + label + ((" | " + extra) if extra else ""))
    if not cond: ok = False


def bench_spec():
    return {"pid": "BENCH（验证夹具，非题库）",
            "std": os.path.join(FIX, "bench_std.cpp"), "lang": "cpp",
            "rounds": 3, "timeout": 10.0,
            "inputs": ["20000000\n", "18000000\n", "22000000\n"]}


def main():
    print("=== std 对跑流程 · 类对拍（零外网） ===")
    spec = bench_spec()

    # 0 基准：std 与自身对跑必须「等价、不收」，且没有任何 WA
    base = std_eval.evaluate(os.path.join(FIX, "bench_std.cpp"), "cpp", spec)
    check("基准自对拍：0 WA / 等价不收", base["verdict"] == "等价" and not base.get("first_bad"),
          "verdict=" + base["verdict"])

    expected = {
        "bench_wa.cpp": ("WA", "去除"),
        "bench_ce.cpp": ("CE", "去除"),
        "bench_re.cpp": ("RE", "去除"),
        "bench_slow.cpp": ("不优", "去除"),
        "bench_fast.cpp": ("明显更优", "待人工审核"),
        "bench_equiv.cpp": ("等价", "不收"),
    }
    got = {}
    for fn, (v, st) in expected.items():
        r = std_eval.evaluate(os.path.join(FIX, fn), "cpp", spec)
        got[fn] = r
        check("变异 %-18s → %s / %s" % (fn, v, st),
              r["verdict"] == v and r["status"] == st,
              "实际 %s / %s" % (r["verdict"], r["status"]))

    # 分辨力：除 fast 外，任何变体都不许进候选
    wrong_admit = [k for k, r in got.items() if r["status"] == "待人工审核"
                   and k != "bench_fast.cpp"]
    check("分辨力：仅明显更优者进候选，其余全被拒", not wrong_admit, str(wrong_admit))
    check("WA 变体给出首个反例证据", bool(got["bench_wa.cpp"].get("first_bad")))
    check("更优/不优有多轮方向证据（每轮 ratio 可核对）",
          len(got["bench_fast.cpp"]["rounds"]) == 3 and
          len(got["bench_slow.cpp"]["rounds"]) == 3)
    check("CPU 时间取自 rusage 非墙钟（比值可核对）",
          all(x["ratio_cpu"] is not None for x in got["bench_fast.cpp"]["rounds"]))

    # 脚本绝不自动迁入
    check("脚本不产出「已迁入」状态",
          all(r["status"] != "已迁入" for r in list(got.values()) + [base]))

    # 离线期望输出表：不编译也能判出已知 hack 的错解
    exp = std_eval.build_expect()
    pids = [x["pid"] for x in std_eval.load_bank()["题库"]]
    check("期望表覆盖全部题库（题面进度 = STD 进度）", set(exp) == set(pids),
          "%d 题 %s" % (len(pids), str(sorted(pids))))
    p1421 = {c["in"]: c["out"] for c in exp["P1421"]["cases"]}
    std_ans = p1421.get("7 6\n")
    bad_ans = "3"          # 第 7 批：double 反复减 1.9 在 19 角整数倍处少买一支
    check("std 期望 7 6 → 4", std_ans == "4", str(std_ans))
    check("离线对照能判出已知错解 3 ≠ 4",
          runner.normalize(bad_ans) != runner.normalize(std_ans or ""))
    p1002 = {c["in"]: c["out"] for c in exp["P1002"]["cases"]}
    check("官方样例 6 6 3 3 → 6（起点覆盖版给 0）", p1002.get("6 6 3 3\n") == "6",
          str(p1002.get("6 6 3 3\n")))

    # 题面内输入纪律
    import cases as cg
    cs = cg.cases("P1421")
    check("P1421 用例全在题面内 (0<=a<=1e4, 0<=b<=9)",
          all(0 <= int(x.split()[0]) <= 10000 and 0 <= int(x.split()[1]) <= 9 for x in cs))
    cs2 = cg.cases("P1002")
    # 题面只保证「起点不是马的控制点」，并未保证终点 —— 旧检查点把合法输入误判为违规
    check("P1002 用例遵守题面保证（仅起点不是马的控制点，终点不限）",
          all(cg.in_range("P1002", x) for x in cs2))
    check("P1002 含官方样例 6 6 3 3（题面逐字）", "6 6 3 3\n" in cs2)

    # 题面闸门：先爬到题面、证据可核对，才允许做 std
    gates = problem_gate.gate_all()
    check("题面闸门：全部 STD 题证据/范围引用/样例实测/用例范围全过",
          all(g["pass"] for g in gates.values()),
          str({k: g["reason"][:26] for k, g in gates.items() if not g["pass"]}))
    check("范围引用逐字命中题面存档（不是凭记忆）",
          all(g["checks"].get("范围引用逐字命中") for g in gates.values()))
    check("题面样例用 std 实测全过",
          all(g["checks"].get("题面样例实测全过") for g in gates.values()))
    check("证据等级如实标注（摘录不伪装成队列正文）",
          all("检索摘录" in str(g["level"]) or "contentOnly" in str(g["level"])
              for g in gates.values()))
    check("验证夹具 BENCH 不进正式题库（不做 std）",
          "BENCH" not in pids)
    # 第 17 条：题面进度 = STD 进度 + 每题配独立朴素算法
    import glob
    REPO = os.path.dirname(os.path.dirname(HERE))
    prob_files = {os.path.basename(x)[:-5] for x in
                  glob.glob(os.path.join(REPO, "site", "data", "problems", "P*.json"))}
    # 队列会持续爬到新题面（auto-range），STD 必须逐题补，不能凭空做。
    # 硬口径：STD 不允许超出题面；题面领先则如实报告「待补 STD」，不假装已做。
    todo = sorted(prob_files - set(pids))
    check("STD 题库 ⊆ 题面存档（std 不凭空超出题面）",
          not (set(pids) - prob_files),
          "STD 无题面 %s" % sorted(set(pids) - prob_files))
    print("  · 题面 %d / STD %d ｜题面待补 STD：%s" %
          (len(prob_files), len(pids), ",".join(todo) if todo else "无"))
    bj = os.path.join(REPO, "site", "data", "std_brute_check.json")
    if os.path.exists(bj):
        b = json.load(open(bj, encoding="utf-8"))
        check("STD↔朴素对拍：全部题 PASS 且变异全被抓到",
              b["统计"]["PASS"] == b["统计"]["题目数"] == len(pids)
              and b["统计"]["变异抓到"] == len(pids),
              str(b["统计"]))
        check("朴素对拍用例数可核对（非 0 空跑）", b["统计"]["用例总数"] >= 100,
              str(b["统计"]["用例总数"]))
    else:
        check("STD↔朴素对拍台账存在", False)

    print("\n结论：", "PASS · 变异全被抓到，测试集有分辨力（零外网）" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
