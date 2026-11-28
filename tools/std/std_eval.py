#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""std 对跑判优器（本地，零外网）。

流程（用户口径）：投稿 → 与「原 std」多轮对跑 → 去除 WA / 去除不优
→ 不 WA 且明显更优 → 添入可选项（**待人工审核**）→ 人工审核无错才迁入 std。
**脚本绝不自动迁入**。

判优用 CPU 时间中位数 + 峰值 RSS，要求多轮方向一致；
落在 0.80~1.25 波动带内判「等价，不收」，避免把评测机抖动当优势。
"""
import os, sys, json, tempfile, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import runner, cases as casegen

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
BANK = os.path.join(HERE, "std_bank.json")


def load_bank():
    return json.load(open(BANK, encoding="utf-8"))


def spec_for(pid):
    for t in load_bank()["题库"]:
        if t["pid"] == pid:
            return {"pid": pid, "std": os.path.join(HERE, t["std"]),
                    "lang": t["lang"], "rounds": 3, "timeout": 5.0}
    raise KeyError("题库未登记: " + pid)


def inputs_for(spec, seed):
    if "inputs" in spec:
        return list(spec["inputs"])
    return casegen.cases(spec["pid"], seed=seed)


def evaluate(cand_path, lang="cpp", spec=None, rounds=None, timeout=None):
    """返回 verdict 与证据；不写任何仓库文件。"""
    spec = dict(spec or spec_for("P1001"))
    rounds = rounds or spec.get("rounds", 3)
    timeout = timeout or spec.get("timeout", 5.0)
    th = load_bank()["阈值"]

    with tempfile.TemporaryDirectory(prefix="stdeval_") as td:
        std_wd = os.path.join(td, "std"); cand_wd = os.path.join(td, "cand")
        os.makedirs(std_wd, exist_ok=True); os.makedirs(cand_wd, exist_ok=True)
        std_cmd = runner.compile_source(spec["std"], spec["lang"], std_wd)
        try:
            cand_cmd = runner.compile_source(cand_path, lang, cand_wd)
        except runner.CompileError as e:
            return {"verdict": "CE", "status": "去除", "reason": "编译失败（CE）",
                    "detail": str(e)[:200], "rounds": []}

        round_rows, first_bad = [], None
        for r in range(rounds):
            ins = inputs_for(spec, r)
            cpu_s = cpu_c = 0.0
            rss_s = rss_c = 0
            for i, inp in enumerate(ins):
                a = runner.run_case(std_cmd, inp, timeout)
                b = runner.run_case(cand_cmd, inp, timeout)
                if b["timed_out"]:
                    return {"verdict": "TLE", "status": "去除",
                            "reason": "单用例超时", "input": inp[:80], "rounds": round_rows}
                if b["rc"] != 0:
                    return {"verdict": "RE", "status": "去除",
                            "reason": "运行期非零退出 rc=%s" % b["rc"],
                            "input": inp[:80], "rounds": round_rows}
                if runner.normalize(a["out"]) != runner.normalize(b["out"]):
                    if first_bad is None:
                        first_bad = {"input": inp[:80], "std": a["out"][:80],
                                     "cand": b["out"][:80]}
                    return {"verdict": "WA", "status": "去除",
                            "reason": "题面内确定性 WA", "first_bad": first_bad,
                            "rounds": round_rows}
                cpu_s += a["cpu"]; cpu_c += b["cpu"]
                rss_s = max(rss_s, a["maxrss"]); rss_c = max(rss_c, b["maxrss"])
            round_rows.append({"seed": r, "n": len(ins),
                               "cpu_std": round(cpu_s, 6), "cpu_cand": round(cpu_c, 6),
                               "ratio_cpu": round(cpu_c / cpu_s, 4) if cpu_s > 0 else None,
                               "rss_std": rss_s, "rss_cand": rss_c,
                               "ratio_rss": round(rss_c / rss_s, 4) if rss_s > 0 else None})

    ratios_cpu = [x["ratio_cpu"] for x in round_rows if x["ratio_cpu"] is not None]
    ratios_rss = [x["ratio_rss"] for x in round_rows if x["ratio_rss"] is not None]
    med_cpu = statistics.median(ratios_cpu) if ratios_cpu else 1.0
    med_rss = statistics.median(ratios_rss) if ratios_rss else 1.0
    faster = [x <= 0.80 for x in ratios_cpu]
    leaner = [x <= 0.80 for x in ratios_rss]
    slower = [x >= 1.25 for x in ratios_cpu]
    fatter = [x >= 1.25 for x in ratios_rss]
    # 多轮方向一致：全部轮次满足才认，避免抖动被当成优势
    better = (all(faster) and len(faster) == rounds) or (all(leaner) and len(leaner) == rounds)
    worse = (all(slower) and len(slower) == rounds) or (all(fatter) and len(fatter) == rounds)

    if worse:
        v, st, why = "不优", "去除", "时间/空间明显劣于原 std（多轮方向一致）"
    elif better:
        v, st, why = "明显更优", "待人工审核", "不 WA 且明显更优 → 添入可选项，待人工审核"
    else:
        v, st, why = "等价", "不收", "落在 0.80~1.25 波动带，无明显优势"
    return {"verdict": v, "status": st, "reason": why,
            "median_ratio_cpu": round(med_cpu, 4), "median_ratio_rss": round(med_rss, 4),
            "first_bad": first_bad, "rounds": round_rows}


def build_expect():
    """用 std 产生每题期望输出表（离线本地评测对照，不引用官方数据）。"""
    out = {}
    with tempfile.TemporaryDirectory(prefix="stdexp_") as td:
        for t in load_bank()["题库"]:
            pid, src = t["pid"], os.path.join(HERE, t["std"])
            wd = os.path.join(td, pid); os.makedirs(wd, exist_ok=True)
            cmd = runner.compile_source(src, t["lang"], wd)
            rows = []
            for i, inp in enumerate(casegen.cases(pid, seed=0)):
                a = runner.run_case(cmd, inp, 5.0)
                rows.append({"in": inp, "out": runner.normalize(a["out"])})
            out[pid] = {"title": t["title"], "范围": t["范围"], "cases": rows}
    return out


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--pid", default="P1001")
    ap.add_argument("--cand", required=True)
    ap.add_argument("--lang", default="cpp")
    a = ap.parse_args()
    print(json.dumps(evaluate(a.cand, a.lang, spec_for(a.pid)), ensure_ascii=False, indent=1))
