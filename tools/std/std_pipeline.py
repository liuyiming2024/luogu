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
import std_eval, problem_gate

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
    # 外部工单（别人投稿）：扫描 tickets/external/*.json 与 external_index.json
    ext = os.path.join(TICKETS, "external")
    if os.path.isdir(ext):
        for fn in sorted(os.listdir(ext)):
            if not fn.endswith(".json"): continue
            try: d = json.load(open(os.path.join(ext, fn), encoding="utf-8"))
            except Exception: continue
            items = d if isinstance(d, list) else (d.get("条目", [d]) if isinstance(d, dict) else [])
            for it in items:
                if isinstance(it, dict) and it.get("id") and it.get("pid") and it.get("file"):
                    it = dict(it); it["id"] = "ext:" + str(it["id"])
                    it["_ext_dir"] = ext
                    idx.append(it)
    rows = []
    print("[std-pipeline] 工单", len(idx), "条 | 本地对跑，零外网")
    for t in idx:
        src = os.path.join(t.get("_ext_dir", TICKETS), t["file"])
        if not os.path.exists(src):
            rows.append({"id": t["id"], "pid": t["pid"], "verdict": "缺失",
                         "status": "去除", "reason": "源码文件不存在"}); continue
        if t.get("archived"):
            # 已迁入的工单归档：不再重复对跑，也不让脚本「自动迁入」
            rows.append({"id": t["id"], "pid": t["pid"], "file": t["file"],
                         "sha256_前16": sha(src), "note": t.get("note", ""),
                         "verdict": "已迁入（工单归档）", "status": "已迁入",
                         "reason": t["archived"], "_archived": True,
                         "证据等级": "", "题面闸门": {},
                         "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds")})
            print("  %-6s %-8s 已迁入归档（skip）" % (t["id"], t["pid"]))
            continue
        g = problem_gate.gate(t["pid"], verbose=False)
        if not g["pass"]:
            # 「先爬到题面的，你再做」：闸门未过一律不做、不判、不放
            row = {"id": t["id"], "pid": t["pid"], "file": t["file"],
                   "sha256_前16": sha(src), "note": t.get("note", ""),
                   "verdict": "题面闸门未过", "status": "不做",
                   "reason": g["reason"], "证据等级": g["level"],
                   "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
            rows.append(row)
            print("  %-6s %-8s 题面闸门未过 → 不做（%s）" % (t["id"], t["pid"], g["reason"][:36]))
            continue
        spec = bench_spec() if t["pid"] == "BENCH" else std_eval.spec_for(t["pid"])
        r = std_eval.evaluate(src, t.get("lang", "cpp"), spec)
        row = {"id": t["id"], "pid": t["pid"], "file": t["file"],
               "sha256_前16": sha(src), "note": t.get("note", ""),
               "verdict": r["verdict"], "status": r["status"],
               "reason": r["reason"],
               "median_ratio_cpu": r.get("median_ratio_cpu"),
               "median_ratio_rss": r.get("median_ratio_rss"),
               "证据等级": g["level"], "题面闸门": g["checks"],
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
                    "不做": sum(1 for x in rows if x["status"] == "不做"),
                    "已迁入": sum(1 for x in rows if x["status"] == "已迁入")},
           "条目": rows}
    from stable_write import stable_write
    stable_write(CAND, doc)
    # 脚本绝不自动迁入：台账里出现「已迁入」只能来自显式 archived 标记
    assert all(x.get("_archived") for x in rows if x["status"] == "已迁入"), \
        "脚本不得自动迁入（已迁入条目必须有 archived 标记）"

    exp = std_eval.build_expect()
    exp_doc = {"说明": "由本地 std 逐条跑出的期望输出；供离线 IDE「本地评测」对照，不引用官方数据、不需要编译。",
               "题目数": len(exp),
               "用例总数": sum(len(v["cases"]) for v in exp.values()),
               "题目": exp}
    from stable_write import stable_write
    stable_write(EXPECT, exp_doc)
    print("[std-pipeline] 台账 →", os.path.relpath(CAND, REPO))
    print("[std-pipeline] 期望表 →", os.path.relpath(EXPECT, REPO),
          "|", exp_doc["题目数"], "题", exp_doc["用例总数"], "组")
    print("[std-pipeline] 待人工审核", doc["统计"]["待人工审核"],
          "| 去除", doc["统计"]["去除"], "| 不收", doc["统计"]["不收"],
          "| 不做", doc["统计"]["不做"],
          "| 已迁入", doc["统计"]["已迁入"], "（仅来自显式 archived 归档）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
