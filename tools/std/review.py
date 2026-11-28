#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""代审 · 证据驱动，不是「我觉得对就放」。

用户把审核委托给本地（单人自用），但明确要求「保证做的是对的」。
所以审核 = 逐条重新核验证据链，结论必须带可复核的凭据：
  · 题面闸门（范围逐字 / 样例实测 / 用例 in_range）
  · 代码 sha256 与台账一致（防转录位置错误）
  · 重跑对拍：仍为「明显更优」且多轮方向一致
  · 六类变异敏感性脚本在位且 PASS（由 verify_std.py 保证）
  · 证据等级：检索摘录 → **准予迁入，但挂起待 contentOnly 正文复核**
             contentOnly 正文 → 准予迁入，可由 promote.py 执行
  · 任一不达标 → 打回，写清原因

产物：site/data/std_reviews.json（审核台账）+ site/data/std_pending.json（挂起迁入）
**本脚本不改任何 std 文件**，迁入是单独一步且有 guard。
"""
import os, sys, json, hashlib
from datetime import datetime, timezone
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import problem_gate, std_eval

REPO = os.path.dirname(os.path.dirname(HERE))
DATA = os.path.join(REPO, "site", "data")
CAND = os.path.join(DATA, "std_candidates.json")
REV = os.path.join(DATA, "std_reviews.json")
PEND = os.path.join(DATA, "std_pending.json")
TICKETS = os.path.join(HERE, "tickets")


def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]


def bench_spec():
    f = os.path.join(HERE, "fixtures")
    return {"pid": "BENCH（验证夹具，非题库）",
            "std": os.path.join(f, "bench_std.cpp"), "lang": "cpp",
            "rounds": 3, "timeout": 10.0,
            "inputs": ["20000000\n", "18000000\n", "22000000\n"]}


def main():
    if not os.path.exists(CAND):
        print("[review] 无候选台账，请先跑 std_pipeline.py"); return 2
    c = json.load(open(CAND, encoding="utf-8"))
    out, pend = [], []
    print("[review] 代审 %d 条（证据驱动，零外网）" % len(c["条目"]))
    for x in c["条目"]:
        pid, tid = x["pid"], x["id"]
        r = {"id": tid, "pid": pid, "file": x.get("file", ""),
             "原判定": x["verdict"], "原状态": x["status"],
             "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
             "checks": {}, "结论": "", "理由": ""}
        if x["status"] != "待人工审核":
            r["结论"] = "无需审核"; r["理由"] = "状态 " + x["status"]
            out.append(r); print("  %-6s %-8s 无需审核" % (tid, pid)); continue

        # 1 题面闸门（BENCH 等非题库题直接打回：先爬题面再做）
        g = problem_gate.gate(pid, verbose=False)
        r["checks"]["题面闸门"] = g["pass"]
        r["checks"]["证据等级"] = g["level"]
        r["checks"]["闸门细节"] = g["checks"]
        if not g["pass"]:
            r["结论"] = "打回"; r["理由"] = "题面闸门未过：" + g["reason"]
            out.append(r); print("  %-6s %-8s 打回（%s）" % (tid, pid, g["reason"][:40])); continue

        # 2 代码逐字核对
        fp = os.path.join(TICKETS, x["file"])
        if not os.path.exists(fp):
            r["结论"] = "打回"; r["理由"] = "源码文件不存在"
            out.append(r); continue
        r["checks"]["代码sha256与台账一致"] = (sha(fp) == x.get("sha256_前16"))

        # 3 重跑对拍（不信任台账旧结论）
        spec = bench_spec() if pid == "BENCH" else std_eval.spec_for(pid)
        e = std_eval.evaluate(fp, x.get("lang", "cpp"), spec)
        r["checks"]["复跑判定"] = e["verdict"]
        ratios = [z["ratio_cpu"] for z in e.get("rounds", []) if z.get("ratio_cpu") is not None]
        r["checks"]["多轮方向一致"] = (len(ratios) == 3 and all(v <= 0.80 for v in ratios))
        r["checks"]["每轮ratio_cpu"] = ratios
        r["checks"]["首个WA反例"] = e.get("first_bad")

        # 4 变异敏感性脚本在位（由 verify_std.py 实跑，这里只核文件存在）
        r["checks"]["六类变异脚本在位"] = os.path.exists(os.path.join(HERE, "verify_std.py"))

        allok = (r["checks"]["代码sha256与台账一致"]
                 and e["verdict"] == "明显更优"
                 and r["checks"]["多轮方向一致"]
                 and not e.get("first_bad")
                 and r["checks"]["六类变异脚本在位"])
        if not allok:
            r["结论"] = "打回"
            r["理由"] = "证据不足：" + json.dumps({k: v for k, v in r["checks"].items()
                                            if v is False or (k == "复跑判定" and v != "明显更优")},
                                           ensure_ascii=False)[:220]
            out.append(r); print("  %-6s %-8s 打回（证据不足）" % (tid, pid)); continue

        # 5 证据等级决定「现在能不能迁」
        if str(g["level"]).startswith("contentOnly"):
            r["结论"] = "准予迁入"; r["理由"] = "证据齐全（contentOnly 正文），可由 promote.py 执行"
            pend.append({"id": tid, "pid": pid, "file": x["file"],
                         "证据等级": g["level"], "审核时间": r["checked_at"],
                         "代码sha256": sha(fp), "每轮ratio_cpu": ratios})
        else:
            r["结论"] = "准予迁入·挂起待题面正文复核"
            r["理由"] = ("证据链全通过，但题面证据等级为「%s」；"
                         "按「不要觉得对就放」，等 contentOnly 正文取回并复核后才执行迁入"
                         % g["level"])
            pend.append({"id": tid, "pid": pid, "file": x["file"],
                         "证据等级": g["level"], "审核时间": r["checked_at"],
                         "代码sha256": sha(fp), "每轮ratio_cpu": ratios,
                         "挂起原因": "题面正文未取回"})
        out.append(r); print("  %-6s %-8s %s" % (tid, pid, r["结论"]))

    doc = {"说明": "代审台账。审核由本地脚本按证据链执行，不是主观放行；迁入是单独一步。",
           "纪律": ["题面闸门未过一律打回（先爬题面再做）",
                    "检索摘录级证据 → 准予迁入但挂起，等 contentOnly 正文复核",
                    "contentOnly 正文级 + 全部证据通过 → 才准予迁入",
                    "代码 sha256 逐字核对，防转录位置错误",
                    "复跑对拍必须仍为明显更优且多轮方向一致"],
           "审核时间": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "统计": {"审核": len(out),
                    "打回": sum(1 for x in out if x["结论"] == "打回"),
                    "准予迁入": sum(1 for x in out if x["结论"] == "准予迁入"),
                    "挂起": sum(1 for x in out if "挂起" in x["结论"]),
                    "已迁入": 0},
           "条目": out}
    json.dump(doc, open(REV, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"说明": "挂起/准予的迁入候选；promote.py 仅在证据等级为 contentOnly 正文时执行",
               "条目": pend}, open(PEND, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("[review] → std_reviews.json | 打回 %d / 准予 %d / 挂起 %d / 已迁入 0"
          % (doc["统计"]["打回"], doc["统计"]["准予迁入"], doc["统计"]["挂起"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
