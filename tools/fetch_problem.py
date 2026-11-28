#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""题面取回器 · **先爬题面，再做 std**（对面 Actions / 本机共用）。

接口依据（洛谷 API 文档）：
  · DataResponse 请求 → `_contentOnly` 或头 `x-luogu-type: content-only`
  · LentilleDataResponse 请求 → 头 `x-lentille-request: content-only`
  · UA 不得含 python-requests；非 GET 才需 referer/csrf（本文件只 GET）
题面详情属哪种响应文档未点名，所以**两类头都试**，并记录每个组合的真实响应。

只有真正解析出含题目字段的 JSON 才落盘并升级证据等级；
骨架 / 403 / 503 / 非 JSON 一律不写题面文件，只把诊断写 /tmp，不假装成功。
"""
import os, sys, json, time, hashlib, argparse, urllib.request, urllib.error
from datetime import datetime, timezone

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(R, "site", "data", "problems")
UA = "Mozilla/5.0 (local-archive-problem-fetch)"

# 每个 (URL, 附加头) 组合都有文档依据；不猜内部私有路径
COMBOS = [
    ("https://www.luogu.com/problem/{pid}?_contentOnly=1",
     {"x-luogu-type": "content-only"}),
    ("https://www.luogu.com/problem/{pid}?_contentOnly=1",
     {"x-lentille-request": "content-only"}),
    ("https://www.luogu.com/problem/{pid}?_contentOnly=1",
     {"x-luogu-type": "content-only", "x-lentille-request": "content-only"}),
    ("https://www.luogu.com.cn/problem/{pid}?_contentOnly=1",
     {"x-luogu-type": "content-only"}),
    ("https://www.luogu.com.cn/problem/{pid}?_contentOnly=1",
     {"x-lentille-request": "content-only"}),
    ("https://www.luogu.com.cn/problem/{pid}?_contentOnly=1",
     {"x-luogu-type": "content-only", "x-lentille-request": "content-only"}),
]
PROB_KEYS = ("description", "inputFormat", "outputFormat", "samples",
             "hint", "title", "background")


def now(): return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha(t): return hashlib.sha256(t.encode("utf-8", "replace")).hexdigest()


def _problem_obj(j):
    """洛谷 contentOnly 题面详情（实测 2026-11-28 Actions run 2）：

    正文在 data.problem.contenu，字段名是 formatI / formatO；
    samples 在 data.problem.samples（[[输入,输出], ...]）。
    必须 description 非空且 (formatI 或 hint) 非空才算真·题面，
    绝不把只有 samples 的空壳当正文（第 16 条「不觉得对就放」）。
    """
    try:
        p = j.get("data", {}).get("problem", {})
        c = p.get("contenu", {})
        if not isinstance(c, dict) or not isinstance(p, dict): return None
        desc = str(c.get("description", "") or "")
        fi = str(c.get("formatI", c.get("inputFormat", "")) or "")
        fo = str(c.get("formatO", c.get("outputFormat", "")) or "")
        hint = str(c.get("hint", "") or "")
        if not (desc.strip() and (fi.strip() or hint.strip())):
            return None
        return {
            "title": str(c.get("name", p.get("name", "")) or ""),
            "background": str(c.get("background", "") or ""),
            "description": desc,
            "inputFormat": fi,
            "outputFormat": fo,
            "hint": hint,
            "samples": p.get("samples", c.get("samples", [])),
        }
    except Exception:
        return None


def probe(pid, timeout=12, gap=1.0):
    """返回 (存档dict|None, 诊断list, 失败原因)。低频、不编造。"""
    diag = []
    for ci, (tpl, extra) in enumerate(COMBOS):
        url = tpl.format(pid=pid)
        h = {"User-Agent": UA, "Accept": "application/json, text/plain, */*",
             "Referer": "https://www.luogu.com.cn/"}
        h.update(extra)
        tag = "+".join(sorted(extra.keys()))
        try:
            req = urllib.request.Request(url, headers=h)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read(2_000_000).decode("utf-8", "replace")
                code = r.status
        except urllib.error.HTTPError as e:
            diag.append({"url": url, "heads": tag, "http": e.code, "kind": "HTTPError"})
            if ci + 1 < len(COMBOS): time.sleep(gap)
            continue
        except Exception as e:
            diag.append({"url": url, "heads": tag, "kind": type(e).__name__})
            if ci + 1 < len(COMBOS): time.sleep(gap)
            continue
        head = raw[:100].replace("\n", " ")
        is_json = False
        try:
            j = json.loads(raw)
            is_json = True
        except Exception:
            j = None
        cand = _problem_obj(j) if is_json else None
        d = {"url": url, "heads": tag, "http": code, "bytes": len(raw),
             "json": is_json, "problem_obj": bool(cand), "head": head}
        diag.append(d)
        if ci + 1 < len(COMBOS):
            time.sleep(gap)                 # 组合之间也低频，不密集探测
        if cand:
            samples = cand.get("samples", [])
            doc = {
                "pid": pid, "原文链接": "https://www.luogu.com/problem/" + pid,
                "取回端点": url, "取回头字段": extra, "取回时间": now(),
                "证据等级": "contentOnly 正文（队列取回）",
                "sha256": sha(raw),
                "题面": {
                    "标题": str(cand.get("title", "")),
                    "题目背景": str(cand.get("background", "")),
                    "题目描述": str(cand.get("description", "")),
                    "输入格式": str(cand.get("inputFormat", "")),
                    "输出格式": str(cand.get("outputFormat", "")),
                    "说明提示": str(cand.get("hint", "")),
                    "样例": samples if isinstance(samples, list) else [],
                },
                "原文": raw[:200000],
            }
            return doc, diag, None
    if not diag:
        return None, diag, "无可用端点"
    js = sum(1 for d in diag if d.get("json"))
    sk = sum(1 for d in diag if d.get("http") == 200 and not d.get("json"))
    return None, diag, "HTTP200-JSON%d-骨架%d-错误%d" % (
        js, sk, len(diag) - js - sk)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pids", default="P1001,P1421,P1002")
    ap.add_argument("--delay", type=float, default=2.0)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--auto-range", action="store_true",
                    help="按 crawl_state 的 problems_cursor 有序推进，跳过已有正文级存档")
    ap.add_argument("--batch", type=int, default=10,
                    help="auto-range 单轮最多取回的题面数")
    ap.add_argument("--state", default="site/data/crawl_state.json")
    a = ap.parse_args()
    if a.delay < 1.0:
        print("拒绝：间隔不得低于 1 秒"); return 2
    os.makedirs(OUT, exist_ok=True)
    pids = [x.strip() for x in a.pids.split(",") if x.strip()]
    cursor_file = None
    if a.auto_range:
        # 有序枚举：从游标起往后找「还没有 contentOnly 正文」的 P 号，不遍历空间
        cursor_file = os.path.join(R, a.state)
        cur = 1000
        try:
            st = json.load(open(cursor_file, encoding="utf-8"))
            cur = max(1000, int(st.get("problems_cursor", 1000)))
        except Exception:
            pass
        pids = []
        k = cur
        while len(pids) < a.batch and k < cur + 500:
            pid = "P%d" % k
            fp = os.path.join(OUT, pid + ".json")
            has_body = False
            if os.path.exists(fp):
                try:
                    has_body = str(json.load(open(fp, encoding="utf-8"))
                                   .get("证据等级", "")).startswith("contentOnly")
                except Exception:
                    pass
            if not has_body: pids.append(pid)
            k += 1
        print("[problem] auto-range 游标 P%d 起 → 本轮 %d 题：%s" %
              (cur, len(pids), ",".join(pids)))
    got, failed, all_diag = [], [], []
    for i, pid in enumerate(pids):
        doc, diag, err = probe(pid, gap=max(1.0, a.delay / 2.0))
        all_diag += [{"pid": pid, **d} for d in diag]
        if doc:
            fp = os.path.join(OUT, pid + ".json")
            old = json.load(open(fp, encoding="utf-8")) if os.path.exists(fp) else {}
            unchanged = (str(old.get("证据等级", "")).startswith("contentOnly")
                         and old.get("题面") == doc["题面"])
            if unchanged:
                # 内容完全没变：不写文件、不计入本轮新增，避免仅时间戳漂移造成无用提交
                print("[problem] %s = 无变化（跳过写入，不造提交）" % pid)
            else:
                # 只升级：contentOnly 正文覆盖检索摘录，反之绝不降级
                if str(old.get("证据等级", "")).startswith("contentOnly"):
                    doc = old
                if not a.dry_run:
                    json.dump(doc, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
                got.append(pid)
                print("[problem] %s ✓ %s | %s" % (pid, doc["题面"]["标题"][:24], doc["取回端点"]))
        else:
            failed.append((pid, err))
            print("[problem] %s ✗ %s（不写题面文件、不假装成功）" % (pid, err))
            for d in diag:
                print("    ", d["url"].split("/")[2], d["heads"][:32],
                      "HTTP", d.get("http"), "json", d.get("json"),
                      "prob", d.get("problem_obj"), "bytes", d.get("bytes"),
                      "|", (d.get("head") or "")[:56])
        if i + 1 < len(pids):
            time.sleep(a.delay)
    # 诊断只放 /tmp：不进仓库，不制造无用提交
    try:
        json.dump({"时间": now(), "有效题面": got, "失败": failed, "组合诊断": all_diag},
                  open("/tmp/luogu_problem_diag.json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        open("/tmp/luogu_problem_new", "w", encoding="utf-8").write(str(len(got)))
        codes = {}
        for d in all_diag: codes[d.get("http", "err")] = codes.get(d.get("http", "err"), 0) + 1
        open("/tmp/luogu_problem_tag", "w", encoding="utf-8").write(
            "ok%d-fail%d-" % (len(got), len(failed)) +
            "-".join("h%sx%d" % (k, v) for k, v in sorted(codes.items(), key=lambda x: str(x[0]))))
    except OSError:
        pass
    # 游标推进：只在 auto-range 且本轮确有正文时推进到「本轮最后一个成功 P 号 + 1」
    if a.auto_range and got and cursor_file and not a.dry_run:
        try:
            st = json.load(open(cursor_file, encoding="utf-8"))
            last = max(int(x[1:]) for x in got if x[1:].isdigit())
            st["problems_cursor"] = max(int(st.get("problems_cursor", 1000)), last + 1)
            st["problem_fetch_note"] = "auto-range 推进至 P%d（run %s）" % (
                st["problems_cursor"], now())
            json.dump(st, open(cursor_file, "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)
            print("[problem] 游标推进 → P%d" % st["problems_cursor"])
        except Exception as e:
            print("[problem] 游标回写跳过：%s" % type(e).__name__)
    print("[problem] 本轮有效题面 %d / 失败 %d" % (len(got), len(failed)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
