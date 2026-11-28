#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""题面取回器 · **先爬题面，再做 std**（对面 Actions / 本机共用）。

接口依据（洛谷 API 文档，检索可得）：响应主体为 DataResponse 的请求需要
参数 `_contentOnly`（值任意）或头字段 `x-luogu-type: content-only`；
UA 不得含 python-requests。本取回器**不编造成功**：逐个低频试候选端点，
只有真正解析出含题目字段的 JSON 才落盘；骨架 / 403 / 错误页一律不写文件。

产物：site/data/problems/<PID>.json
  {pid, 原文链接, 取回端点, 取回时间, 证据等级, sha256, 题面{...}, 原文}
证据等级：contentOnly 正文（队列取回） > 检索摘录（人工可核对）
"""
import os, sys, json, re, time, hashlib, argparse, urllib.request, urllib.error
from datetime import datetime, timezone

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(R, "site", "data", "problems")
UA = "Mozilla/5.0 (local-archive-problem-fetch)"

# 候选端点均有公开文档依据；不猜内部路径
ENDPOINTS = [
    "https://www.luogu.com/problem/{pid}?_contentOnly=1",
    "https://www.luogu.com.cn/problem/{pid}?_contentOnly=1",
]

PROB_KEYS = ("description", "inputFormat", "outputFormat", "samples",
             "hint", "title", "background")


def now(): return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha(t): return hashlib.sha256(t.encode("utf-8", "replace")).hexdigest()


def try_fetch(pid, timeout=12):
    """返回 (存档dict, None) 或 (None, 失败原因)。零编造。"""
    for tpl in ENDPOINTS:
        url = tpl.format(pid=pid)
        req = urllib.request.Request(url, headers={
            "User-Agent": UA, "Accept": "application/json, text/plain, */*",
            "x-luogu-type": "content-only",
            "Referer": "https://www.luogu.com.cn/",
        })
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read(2_000_000).decode("utf-8", "replace")
                code = r.status
        except urllib.error.HTTPError as e:
            last = "HTTP %s" % e.code
            continue
        except Exception as e:
            last = type(e).__name__
            continue
        if code != 200:
            last = "HTTP %s" % code
            continue
        try:
            j = json.loads(raw)
        except Exception:
            last = "非 JSON（多为 SPA 骨架）"
            continue
        # 洛谷 contentOnly 常见形态：{...} / {"data":{"problem":{...}}} / {"currentData":{"problem":{...}}}
        cand = None
        for path in (lambda x: x,
                     lambda x: x.get("data", {}).get("problem"),
                     lambda x: x.get("currentData", {}).get("problem"),
                     lambda x: x.get("data", {})):
            try:
                v = path(j)
                if isinstance(v, dict) and any(k in v for k in PROB_KEYS):
                    cand = v; break
            except Exception:
                pass
        if not cand:
            last = "JSON 无题目字段"
            continue
        title = str(cand.get("title", ""))
        samples = cand.get("samples", [])
        doc = {
            "pid": pid, "原文链接": "https://www.luogu.com/problem/" + pid,
            "取回端点": url, "取回时间": now(),
            "证据等级": "contentOnly 正文（队列取回）",
            "sha256": sha(raw),
            "题面": {
                "标题": title,
                "题目背景": str(cand.get("background", "")),
                "题目描述": str(cand.get("description", "")),
                "输入格式": str(cand.get("inputFormat", "")),
                "输出格式": str(cand.get("outputFormat", "")),
                "说明提示": str(cand.get("hint", "")),
                "样例": samples if isinstance(samples, list) else [],
            },
            "原文": raw[:200000],
        }
        return doc, None
    return None, last if 'last' in locals() else "无可用端点"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pids", default="P1001,P1421,P1002")
    ap.add_argument("--delay", type=float, default=2.0)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.delay < 1.0:
        print("拒绝：间隔不得低于 1 秒"); return 2
    os.makedirs(OUT, exist_ok=True)
    got, failed = [], []
    for i, pid in enumerate([x.strip() for x in a.pids.split(",") if x.strip()]):
        doc, err = try_fetch(pid)
        if doc:
            # 已有 contentOnly 存档时不降级覆盖；检索摘录可升级
            fp = os.path.join(OUT, pid + ".json")
            if os.path.exists(fp):
                old = json.load(open(fp, encoding="utf-8"))
                if old.get("证据等级", "").startswith("contentOnly") and not doc:
                    continue
            if not a.dry_run:
                json.dump(doc, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            got.append(pid)
            print("[problem] %s ✓ %s | %s" % (pid, doc["题面"]["标题"][:24], doc["取回端点"]))
        else:
            failed.append((pid, err))
            print("[problem] %s ✗ %s（不写文件、不假装成功）" % (pid, err))
        if i + 1 < len([x for x in a.pids.split(",") if x.strip()]):
            time.sleep(a.delay)
    print("[problem] 本轮有效题面 %d / 失败 %d" % (len(got), len(failed)))
    # 供 workflow 判定「是否值得提交」：只在确有新增正文时写 1
    if not a.dry_run:
        # 计数放 /tmp：不进仓库，不产生「只是写了个计数」的无用提交
        try:
            open("/tmp/luogu_problem_new", "w", encoding="utf-8").write(str(len(got)))
        except OSError:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
