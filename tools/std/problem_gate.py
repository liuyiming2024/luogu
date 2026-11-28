#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""题面闸门 —— 「先爬到题面的，你再做」的硬落地。

任一题必须在 site/data/problems/<PID>.json 有**可核对的题面证据**，且：
  1. 题面证据文件存在、sha256 可核对
  2. std_bank 的「范围引用」逐字出现在存档题面文字里（不是我觉得）
  3. 题面样例用 std 实测**全过**（逐字比对，不容忍内容差异）
  4. 用例生成器每个输入都通过 cases.in_range()
全部通过才允许做 std / 进审核；任一不达标 → 明确「未做」，绝不凭感觉放行。

证据等级分层（不把摘录伪装成队列正文）：
  · 检索摘录（逐字）        → 允许对跑与审核，但**不允许迁入 std**
  · contentOnly 正文（队列） → 证据齐全且审核通过才允许迁入
"""
import os, sys, json, hashlib, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import runner, cases as cg, std_eval

REPO = os.path.dirname(os.path.dirname(HERE))
PROB = os.path.join(REPO, "site", "data", "problems")


def bank():
    return json.load(open(os.path.join(HERE, "std_bank.json"), encoding="utf-8"))


def gate(pid, verbose=True):
    """返回 {pass, level, checks, reason}。零外网。"""
    d = bank()
    t = next((x for x in d["题库"] if x["pid"] == pid), None)
    res = {"pid": pid, "pass": False, "level": "无", "checks": {}, "reason": ""}
    if not t:
        res["reason"] = "题库未登记（可能是验证夹具）"; return res
    fp = os.path.join(PROB, pid + ".json")
    if not os.path.exists(fp):
        res["reason"] = "题面未取回：缺 " + os.path.relpath(fp, REPO); return res
    doc = json.load(open(fp, encoding="utf-8"))
    raw = json.dumps(doc["题面"], ensure_ascii=False, sort_keys=True)
    res["checks"]["证据文件存在"] = True
    res["checks"]["原文sha256可核对"] = bool(doc.get("sha256"))
    res["checks"]["证据等级"] = doc.get("证据等级", "")
    res["level"] = doc.get("证据等级", "")

    # 2 范围引用逐字（把存档题面所有文字拼起来查）
    body = " ".join(str(v) for v in doc["题面"].values() if not isinstance(v, list))
    res["checks"]["范围引用逐字命中"] = t.get("范围引用", "") in body
    if not res["checks"]["范围引用逐字命中"]:
        res["reason"] = "范围引用「%s」未逐字出现在题面存档" % t.get("范围引用", ""); return res

    # 3 题面样例用 std 实测全过
    with tempfile.TemporaryDirectory(prefix="gate_") as td:
        wd = os.path.join(td, "std"); os.makedirs(wd)
        cmd = runner.compile_source(os.path.join(HERE, t["std"]), t["lang"], wd)
        sm = cg.samples(pid)
        bad = []
        for inp, exp in sm:
            a = runner.run_case(cmd, inp, 5.0)
            if runner.normalize(a["out"]) != runner.normalize(exp):
                bad.append({"in": inp[:60], "expect": exp[:60], "got": a["out"][:60]})
        res["checks"]["题面样例实测全过"] = (len(sm) > 0 and not bad)
        res["checks"]["样例数"] = len(sm)
        if bad:
            res["reason"] = "题面样例未过: " + json.dumps(bad, ensure_ascii=False)[:200]; return res
        if not sm:
            res["reason"] = "题面存档无样例"; return res

    # 4 用例全部在题面范围内
    cs = cg.cases(pid)
    res["checks"]["用例全部in_range"] = all(cg.in_range(pid, x) for x in cs)
    res["checks"]["用例数"] = len(cs)
    if not res["checks"]["用例全部in_range"]:
        res["reason"] = "用例生成器产出题面外输入"; return res

    res["pass"] = True
    res["reason"] = "证据齐全：范围逐字 / 样例实测 / 用例全在题面内"
    if verbose:
        print("[gate] %s %s | %s | %s" % (pid, "PASS" if res["pass"] else "FAIL",
                                          res["level"], res["reason"]))
    return res


def gate_all():
    return {t["pid"]: gate(t["pid"]) for t in bank()["题库"]}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("--pid", default="")
    a = ap.parse_args()
    rs = {a.pid: gate(a.pid)} if a.pid else gate_all()
    print(json.dumps(rs, ensure_ascii=False, indent=1))
    sys.exit(0 if all(x["pass"] for x in rs.values()) else 1)
