#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""待推队列 → luogu 的低频代提交器（GitHub Actions / 本机运行态共用）。

凭据全部从环境变量读，**绝不写进仓库、绝不打印、绝不硬编码**：
  LUOGU_COOKIE / LUOGU_CSRF / LUOGU_UID / LUOGU_SUBMIT_ENDPOINT / LUOGU_IDE_ENDPOINT

端点**不写死**：洛谷接口会变，按你当前登录后的页面填写到
Settings → Secrets / Variables。留空时只预览，不编造接口、不发请求。

纪律：
  - 只处理 confirmed=true 且未成功的条目（前端由本人显式确认写入）
  - 2.0~3.5s 随机抖动、每 20 次小憩 ~30s、每日 2000 上限
  - 403/429/5xx/「队列堵塞 / Request denied / 降级」→ 立即停止，失败不轰炸重试
  - 未确认 / 无凭据 / 无端点 → 强制 dry-run
"""
import os, sys, json, glob, time, random, hashlib, argparse, urllib.request, urllib.error
from datetime import datetime, timezone

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(R, "site", "data", "outbox")
STATE = os.path.join(OUT, "_状态.json")
STOP_MARK = ["队列堵塞", "Request denied", "policy_default_denied", "服务降级", "503", "429"]

def now(): return datetime.now(timezone.utc).isoformat(timespec="seconds")

def log(*a): print("[luogu-submit]", *a, flush=True)

def load_items(kind):
    items = []
    for p in sorted(glob.glob(os.path.join(OUT, "*.json"))):
        if os.path.basename(p).startswith("_") or "示例" in os.path.basename(p):
            continue
        try: d = json.load(open(p, encoding="utf-8"))
        except Exception: continue
        for raw in (d if isinstance(d, list) else [d]):
            if not isinstance(raw, dict): continue
            if raw.get("confirmed") is not True: continue
            if raw.get("state") in ("已提交", "已推送"): continue
            if kind != "all" and raw.get("kind") != kind: continue
            # 拷贝一份：避免把 _file 等内部字段写回用户文件，也避免改到原数组引用
            it = dict(raw); it["_file"] = p
            items.append(it)
    return items

def endpoint_for(it):
    if it.get("kind") == "judge":
        return os.environ.get("LUOGU_IDE_ENDPOINT", "")
    return os.environ.get("LUOGU_SUBMIT_ENDPOINT", "")

def real_submit(it, ep, cookie, csrf, uid):
    body = {k: it.get(k) for k in
            ("kind", "lid", "pid", "text", "code", "lang", "id") if it.get(k) is not None}
    data = json.dumps(body, ensure_ascii=False).encode()
    h = {"Content-Type": "application/json; charset=utf-8",
         "User-Agent": "Mozilla/5.0 (local-archive-submit)",
         "Referer": "https://www.luogu.com/",
         "Accept": "application/json, text/plain, */*"}
    if cookie: h["Cookie"] = cookie
    if csrf: h["x-csrf-token"] = csrf
    if uid: h["x-luogu-uid"] = uid
    req = urllib.request.Request(ep, data=data, headers=h, method="POST")
    with urllib.request.urlopen(req, timeout=20) as r:
        raw = r.read().decode("utf-8", "replace")
        return r.status, raw[:400]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--kind", default="all", choices=["all", "comment", "publish", "judge"])
    a = ap.parse_args()

    os.makedirs(OUT, exist_ok=True)
    items = load_items(a.kind)
    cookie = os.environ.get("LUOGU_COOKIE", "").strip()
    csrf = os.environ.get("LUOGU_CSRF", "").strip()
    uid = os.environ.get("LUOGU_UID", "").strip()
    any_ep = bool(os.environ.get("LUOGU_SUBMIT_ENDPOINT", "").strip() or
                  os.environ.get("LUOGU_IDE_ENDPOINT", "").strip())

    dry = a.dry_run or not cookie or not any_ep
    reasons = []
    if a.dry_run: reasons.append("显式 dry-run / 未确认")
    if not cookie: reasons.append("未配置 LUOGU_COOKIE（Settings → Secrets）")
    if not any_ep: reasons.append("未配置端点（按洛谷当前页面填 Secrets/Variables，不编造接口）")

    log(f"待处理 {len(items)} 条 | kind={a.kind} | 模式={'预览' if dry else '真实低频提交'}")
    if reasons:
        for r in reasons: log("  ·", r)

    results, sent, stopped = [], 0, False
    for i, it in enumerate(items):
        ep = endpoint_for(it)
        rec = {"id": it.get("id") or hashlib.sha256(
            json.dumps(it, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:12],
               "kind": it.get("kind"), "lid": it.get("lid"), "pid": it.get("pid"),
               "confirmed": True, "checked_at": now()}
        if dry or not ep:
            rec["state"] = "预览（未提交）"
            rec["note"] = "；".join(reasons) or "端点未配置"
            results.append(rec); continue
        try:
            code, raw = real_submit(it, ep, cookie, csrf, uid)
            rec["state"] = "已提交" if 200 <= code < 300 else "失败待重试"
            rec["http"] = code
            if any(m in raw for m in STOP_MARK) or code in (403, 429) or code >= 500:
                rec["state"] = "失败待重试"; rec["note"] = "命中降级/限流特征，本轮立即停止"
                stopped = True
            sent += 1
        except urllib.error.HTTPError as e:
            rec["state"] = "失败待重试"; rec["http"] = e.code
            if e.code in (403, 429) or e.code >= 500:
                rec["note"] = "限流/服务端错误，本轮立即停止"; stopped = True
        except Exception as e:
            rec["state"] = "失败待重试"; rec["note"] = type(e).__name__
        results.append(rec)
        it["state"] = rec["state"]
        # 回写原条目状态（不含凭据）
        try:
            src = it["_file"]
            obj = json.load(open(src, encoding="utf-8"))
            arr = obj if isinstance(obj, list) else [obj]
            for x in arr:
                if x.get("id") == it.get("id"): x["state"] = rec["state"]
            json.dump(obj, open(src, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        except Exception as e:
            log("  状态回写跳过:", type(e).__name__)
        if stopped:
            log("  命中降级/限流 → 本轮停止，剩余条目留待下轮，不轰炸重试"); break
        if sent >= 2000:
            log("  触及每日 2000 上限 → 停止"); break
        time.sleep(random.uniform(2.0, 3.5))
        if sent and sent % 20 == 0:
            log("  每 20 次小憩 ~30s"); time.sleep(30)

    json.dump({"生成时间": now(), "模式": "预览" if dry else "真实提交",
               "处理": len(results), "实际发出": sent, "提前停止": stopped,
               "凭据来源": "Settings Secrets（本文件不含任何凭据）",
               "低频": "2.0~3.5s 抖动 / 每20次小憩30s / 降级即停 / 失败不轰炸重试",
               "结果": results},
              open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    log(f"完成：处理 {len(results)} / 实际发出 {sent} / 提前停止 {stopped}")
    log("状态文件:", os.path.relpath(STATE, R))
    return 0

if __name__ == "__main__":
    sys.exit(main())
