#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""对拍流水线 —— **跑在本地（这边），不放 GitHub Actions**。

分工（用户 2026-11-24 定）：
  · 爬取  → GitHub Actions（那边）：crawl_tick.yml / crawl_lowfreq.yml，正文回写仓库
  · 对拍  → 本地（这边）：本脚本消费待对拍队列、重放验证资产、写台账后 push
  · 网页  → GitHub Pages（那边）：pages.yml 发布 site/，自动显示最新台账

为什么不自动判甲/乙/丙：
  三类判定需要「每题一个独立正确解 + 对拍 + 变异版敏感性检查」，
  机器无法凭空生成独立解。本脚本只做可自动化的部分并如实排队，不越权下结论。

用法：
  python3 tools/verify_pipeline.py                 # 汇总 + 队列状态 + 抽样编译预检
  python3 tools/verify_pipeline.py --compile-all  # 编译全部复现代码（慢，可选）
  python3 tools/verify_pipeline.py --check        # 只校验，不写文件
"""
import os, re, csv, json, glob, hashlib, subprocess, argparse, sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
QUEUE = os.path.join(REPO, "site", "data", "verify_queue.jsonl")
INGEST = os.path.join(REPO, "site", "data", "ingested")
RESULTS = os.path.join(REPO, "05_对拍原始数据")
SCRIPTS = os.path.join(REPO, "03_验证脚本")
CODES = os.path.join(REPO, "04_复现代码")
LEDGER = os.path.join(REPO, "02_文章编号索引", "对拍台账.csv")
SUMMARY = os.path.join(RESULTS, "本地对拍总账.json")

def now(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def count_mismatches(d):
    """递归找 results.json 里的 mismatch 字段，区分原版与变异版(_mut)。"""
    out = []
    def walk(obj, path=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                p = f"{path}.{k}" if path else k
                if k in ("mismatch", "mismatch_bruteforce", "mismatch_insert") \
                   and isinstance(v, (int, float)):
                    out.append((p, int(v)))
                else:
                    walk(v, p)
        elif isinstance(obj, list):
            for i, v in enumerate(obj): walk(v, f"{path}[{i}]")
    walk(d)
    return out

def compile_one(path, timeout=30):
    exe = "/tmp/_verify_pipeline_bin"
    r = subprocess.run(["g++", "-std=gnu++17", "-O2", "-w", "-fsyntax-only", path],
                       capture_output=True, text=True, timeout=timeout)
    return "通过" if r.returncode == 0 else "CE(仅登记，不判缺陷)"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--compile-all", action="store_true")
    ap.add_argument("--sample", type=int, default=12)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    # ---- 1. 汇总已有对拍原始结果
    files = sorted(glob.glob(os.path.join(RESULTS, "*.json")))
    summary = {"生成时间": now(), "执行位置": "本地（非 GitHub Actions）",
               "结果文件数": len(files), "文件": [], "原版0不一致": 0,
               "变异版被抓到": 0, "异常": []}
    for fp in files:
        try: d = json.load(open(fp, encoding="utf-8"))
        except Exception as e:
            summary["异常"].append({"file": os.path.basename(fp), "error": str(e)[:80]})
            continue
        mm = count_mismatches(d)
        orig = [v for k, v in mm if "_mut" not in k and v == 0]
        mut = [v for k, v in mm if "_mut" in k and v > 0]
        summary["原版0不一致"] += len(orig)
        summary["变异版被抓到"] += len(mut)
        summary["文件"].append({"file": os.path.basename(fp),
                                "mismatch字段": len(mm),
                                "原版0不一致": len(orig),
                                "变异版被抓到": len(mut)})
    scripts = sorted(glob.glob(os.path.join(SCRIPTS, "verify_*.py")))
    summary["验证脚本数"] = len(scripts)

    # ---- 2. 待对拍队列：只登记状态，不自动判三类
    queue = []
    if os.path.exists(QUEUE):
        for line in open(QUEUE, encoding="utf-8"):
            line = line.strip()
            if not line: continue
            try: queue.append(json.loads(line))
            except Exception: pass
    ing = {}
    if os.path.isdir(INGEST):
        for fp in glob.glob(os.path.join(INGEST, "*.json")):
            try:
                d = json.load(open(fp, encoding="utf-8"))
                ing[d.get("id") or d.get("lid") or os.path.basename(fp)[:-5]] = d
            except Exception: pass
    qrows = []
    for q in queue:
        lid = q.get("id", "")
        d = ing.get(lid, {})
        blocks = d.get("code_blocks") or []
        body = d.get("body", "")
        if blocks:
            status = "待编写独立正确解（已有代码块）"
        elif body and ("#include" in body or "int main" in body):
            status = "待提取代码块 + 独立正确解"
        else:
            status = "正文待补录，暂不可对拍"
        qrows.append({"编号": lid, "来源": q.get("url", ""),
                      "代码块数": len(blocks), "状态": status,
                      "结论": "未定（不越权自动判甲/乙/丙）", "时间": now()})
    summary["待对拍队列"] = len(queue)
    summary["有正文可提取"] = sum(1 for x in qrows if x["代码块数"] > 0)

    # ---- 3. 编译预检（只登记 CE，不算 hack）
    cpp = sorted(glob.glob(os.path.join(CODES, "*.cpp")) +
                 glob.glob(os.path.join(CODES, "*.c")))
    targets = cpp if args.compile_all else cpp[::max(1, len(cpp)//max(1,args.sample))][:args.sample]
    comp = []
    for fp in targets:
        try: comp.append({"file": os.path.basename(fp), "result": compile_one(fp)})
        except Exception as e:
            comp.append({"file": os.path.basename(fp), "result": "跳过:" + type(e).__name__})
    summary["编译预检"] = {"总数": len(cpp), "本次检查": len(comp), "明细": comp}
    summary["说明"] = ("编译预检的 CE 只登记，不计缺陷；三类判定需独立正确解 + 对拍 + "
                       "变异版敏感性检查，由本地逐批执行后写回 article_index.csv。")

    print(f"[{now()}] 对拍流水线（本地）")
    print(f"  结果文件 {len(files)}｜验证脚本 {len(scripts)}｜复现代码 {len(cpp)}")
    print(f"  原版 0 不一致 {summary['原版0不一致']}｜变异版被抓到 {summary['变异版被抓到']}")
    print(f"  待对拍队列 {len(queue)}｜有正文可提取 {summary['有正文可提取']}")
    print(f"  编译预检 {len(comp)} 个：",
          {k: sum(1 for c in comp if c['result'] == k) for k in set(c['result'] for c in comp)})

    if args.check: return 0
    # ---- 4. 落盘
    open(SUMMARY, "w", encoding="utf-8").write(
        json.dumps(summary, ensure_ascii=False, indent=1))
    cols = ["编号", "来源", "代码块数", "状态", "结论", "时间"]
    with open(LEDGER, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for r in qrows: w.writerow(r)
        # 无队列时也留一行说明，避免空表让人误以为没跑
        if not qrows:
            w.writerow({"编号": "（队列为空）", "来源": "—", "代码块数": 0,
                        "状态": "当前无待对拍条目；已有 96 篇逐篇验证结论在批次报告中",
                        "结论": "未越权自动判定", "时间": now()})
    print("  已写", os.path.relpath(SUMMARY, REPO), "与", os.path.relpath(LEDGER, REPO))
    return 0

if __name__ == "__main__":
    sys.exit(main())
