#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""std 流程的「类对拍」验证：不能只证明跑过了，得证明测试集有分辨力。

每个变异实现都必须被抓到；若有变体被误放进候选，判 FAIL。
零外网、零写入仓库（台账只在 std_pipeline 里生成）。
"""
import os, sys, json, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import std_eval, runner

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
    check("期望表覆盖三道真题", set(exp) == {"P1001", "P1421", "P1002"},
          str(sorted(exp)))
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
    mv = [(1, 2), (1, -2), (2, 1), (2, -1), (-1, 2), (-1, -2), (-2, 1), (-2, -1)]
    def bad(x):
        n, m, hx, hy = map(int, x.split())
        if (hx, hy) in ((0, 0), (n, m)): return True
        return any((hx + dx, hy + dy) in ((0, 0), (n, m)) for dx, dy in mv)
    check("P1002 用例起点/终点不被马位或马控制点占据", not any(bad(x) for x in cs2))

    print("\n结论：", "PASS · 变异全被抓到，测试集有分辨力（零外网）" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
