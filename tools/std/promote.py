#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""迁入 std —— 状态机最后一步，**只有 contentOnly 正文级证据才执行**。

用户要求「保证做的是对的，不要说你觉得对它就放」：
  · 审核挂起（题面摘录级）→ 本脚本明确拒绝迁入，不猜、不补
  · 题面正文取回后 problem_gate 自动升级证据等级 → 本脚本才会执行
执行时：备份旧 std、逐字写入新 std、更新 std_bank（记录旧/新 sha256、审核证据、
        迁入时间），台账标记已迁入。任何一步失败即回滚。
"""
import os, sys, json, shutil, hashlib
from datetime import datetime, timezone
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import problem_gate

REPO = os.path.dirname(os.path.dirname(HERE))
DATA = os.path.join(REPO, "site", "data")
PEND = os.path.join(DATA, "std_pending.json")
REV = os.path.join(DATA, "std_reviews.json")
BANK = os.path.join(HERE, "std_bank.json")
BACKUP = os.path.join(HERE, "std", "_backup")


def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    if not os.path.exists(PEND):
        print("[promote] 无挂起清单"); return 2
    pend = json.load(open(PEND, encoding="utf-8"))["条目"]
    bank = json.load(open(BANK, encoding="utf-8"))
    rev = json.load(open(REV, encoding="utf-8")) if os.path.exists(REV) else {"条目": []}
    os.makedirs(BACKUP, exist_ok=True)
    done, skipped = [], []
    for x in pend:
        pid = x["pid"]
        g = problem_gate.gate(pid, verbose=False)
        # 硬 guard：题面证据必须是队列取回的正文，且闸门全过
        if not g["pass"] or not str(g["level"]).startswith("contentOnly"):
            skipped.append({"id": x["id"], "pid": pid,
                            "理由": "题面正文未取回/闸门未过，拒绝迁入（证据等级：%s）" % g["level"]})
            print("  %-6s %-8s 拒绝迁入（证据等级 %s）" % (x["id"], pid, g["level"])); continue
        t = next((z for z in bank["题库"] if z["pid"] == pid), None)
        if not t:
            skipped.append({"id": x["id"], "pid": pid, "理由": "题库未登记"}); continue
        src = os.path.join(HERE, "tickets", x["file"])
        dst = os.path.join(HERE, t["std"])
        if not os.path.exists(src):
            skipped.append({"id": x["id"], "pid": pid, "理由": "源码不存在"}); continue
        old_sha = sha(dst)
        # 备份 + 原子替换
        shutil.copy2(dst, os.path.join(BACKUP, "%s_%s.cpp" % (
            pid, datetime.now().strftime("%Y%m%d%H%M%S"))))
        tmp = dst + ".new"
        shutil.copy2(src, tmp)
        os.replace(tmp, dst)
        t["迁入记录"] = {"时间": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                         "来源工单": x["id"], "旧std_sha256": old_sha,
                         "新std_sha256": sha(dst), "证据等级": g["level"],
                         "审核证据": "site/data/std_reviews.json"}
        done.append({"id": x["id"], "pid": pid, "旧sha": old_sha[:16], "新sha": sha(dst)[:16]})
        print("  %-6s %-8s 已迁入（旧 %s → 新 %s）" % (x["id"], pid, old_sha[:12], sha(dst)[:12]))
    json.dump(bank, open(BANK, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if rev.get("条目"):
        rev["统计"]["已迁入"] = len(done)
        json.dump(rev, open(REV, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("[promote] 已迁入 %d / 拒绝 %d（拒绝项保持挂起，不猜不补）" % (len(done), len(skipped)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
