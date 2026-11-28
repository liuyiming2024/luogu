#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""std 工单流水线（本地，零外网）。

读 tools/std/tickets/index.json → 每条与「原 std」多轮对跑 → 写台账：
  WA / RE / TLE / CE / 不优 / 等价 → 去除或不收
  明显更优                          → 待人工审核（**脚本不自动迁入**）

产物（供离线站读取，不含凭据）：
  site/data/std_candidates.json   候选与淘汰台账
  site/data/std_expect.json       每题期望输出表（离线本地评测对照，不编译也能用）
"""
import os, sys, json, hashlib
from datetime import datetime, timezone
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import std_eval

REPO = os.path.dirname(os.path.dirname(HERE))
TICKETS = os.path.join(HERE, "tickets")
DATA = os.path.join(REPO, "site", "data")
CAND = os.path.join(DATA, "std_candidates.json")
EXPECT = os.path.join(DATA, "std_expect.json")


def bench_spec():
    f = os.path.join(HERE, "fixtures")
    return {"pid": "BENCH（验证夹具，非题库）",
            "std": os.path.join(f, "bench_std.cpp"), "lang": "cpp",
            "rounds": 3, "timeout": 10.0,
            "inputs": ["20000000\n", "18000000\n", "22000000\n"]}


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def main():
    os.makedirs(DATA, exist_ok=True)
    idx = json.load(open(os.path.join(TICKETS, "index.json"), encoding="utf-8"))
    rows = []
    print("[std-pipeline] 工单", len(idx), "条 | 本地对跑，零外网")
    for t in idx:
        src = os.path.join(TICKETS, t["file"])
        if not os.path.exists(src):
            rows.append({"id": t["id"], "pid": t["pid"], "verdict": "缺失",
                         "status": "去除", "reason": "源码文件不存在"}); continue
        spec = bench_spec() if t["pid"] == "BENCH" else std_eval.spec_for(t["pid"])
        r = std_eval.evaluate(src, t.get("lang", "cpp"), spec)
        row = {"id": t["id"], "pid": t["pid"], "file": t["file"],
               "sha256_前16": sha(src), "note": t.get("note", ""),
               "verdict": r["verdict"], "status": r["status"],
               "reason": r["reason"],
               "median_ratio_cpu": r.get("median_ratio_cpu"),
               "median_ratio_rss": r.get("median_ratio_rss"),
               "first_bad": r.get("first_bad"),
               "rounds": r.get("rounds", []),
               "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        rows.append(row)
        print("  %-6s %-8s %-10s → %-10s %s" %
              (t["id"], t["pid"], r["verdict"], t["file"], row["status"]))

    doc = {"说明": "取不到官方数据，正确性以自写独立正确解 + 题面内输入对拍为准。",
           "状态机": "投稿 → 与原 std 多轮对跑 → 去除 WA / 去除不优 → 明显更优添入可选项 → 人工审核无错才迁入 std",
           "纪律": ["CPU 时间取 rusage(ru_utime+ru_stime) 中位数，不用墙钟，减小评测机波动",
                    "多轮方向一致才认「明显更优/不优」；0.80~1.25 波动带判等价不收",
                    "题面外输入一律作废", "脚本绝不自动迁入，候选一律待人工审核"],
           "生成时间": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "统计": {"工单": len(rows),
                    "待人工审核": sum(1 for x in rows if x["status"] == "待人工审核"),
                    "去除": sum(1 for x in rows if x["status"] == "去除"),
                    "不收": sum(1 for x in rows if x["status"] == "不收"),
                    "已迁入": sum(1 for x in rows if x["status"] == "已迁入")},
           "条目": rows}
    json.dump(doc, open(CAND, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    assert doc["统计"]["已迁入"] == 0, "脚本不得自动迁入"

    exp = std_eval.build_expect()
    exp_doc = {"说明": "由本地 std 逐条跑出的期望输出；供离线 IDE「本地评测」对照，不引用官方数据、不需要编译。",
               "题目数": len(exp),
               "用例总数": sum(len(v["cases"]) for v in exp.values()),
               "题目": exp}
    json.dump(exp_doc, open(EXPECT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("[std-pipeline] 台账 →", os.path.relpath(CAND, REPO))
    print("[std-pipeline] 期望表 →", os.path.relpath(EXPECT, REPO),
          "|", exp_doc["题目数"], "题", exp_doc["用例总数"], "组")
    print("[std-pipeline] 待人工审核", doc["统计"]["待人工审核"],
          "| 去除", doc["统计"]["去除"], "| 不收", doc["统计"]["不收"],
          "| 已迁入", doc["统计"]["已迁入"], "（必须为 0）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
