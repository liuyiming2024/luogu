#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""来源署名 / 原文链接 / 内容完整性签名。

公开仓库里每一条收录内容都必须能回答四个问题：
  1. 原文在哪？        → original_url（必填，指向 www.luogu.com/article/<id> 或题面页）
  2. 谁写的？          → author（正文 meta 尽力提取；抓不到写「见原文页面署名」，不编造）
  3. 什么时候取的？    → fetched_at
  4. 内容有没有被改？  → content_sha256 + signature（sha256 完整性签名，非加密签名）

产出 site/data/provenance.json，供 _build_site.py 渲染「引用与署名」块。
对尚无正文的条目也生成一条「仅索引签名」，明确标注正文待补录。

用法：python3 tools/provenance.py            # 增量补全
      python3 tools/provenance.py --check    # 只校验，不写文件（退出码 1 = 有缺项）
"""
import os, re, csv, json, sys, html, hashlib, argparse
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "site", "data")
INGEST = os.path.join(DATA, "ingested")
CSVP = os.path.join(REPO, "02_文章编号索引", "article_index.csv")
OUT = os.path.join(DATA, "provenance.json")

RIGHTS = ("版权归原作者及洛谷所有；本仓库仅作个人学习 / 学术研究的离线归档与校对留痕，"
          "不用于商业用途。每篇均保留原文链接与署名；权利人如不希望被收录，"
          "可提交 issue 或按《归档与版权声明.md》申请移除，我们会删除对应正文与索引条目。")

def now(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def sha(s): return hashlib.sha256(s.encode("utf-8", "ignore")).hexdigest()

def article_meta(body):
    """洛谷文章页内嵌 `data.article` JSON（含 author.name / title / solutionFor.pid）。
    这是**原文页面自己的署名**，比 <title> 或猜测可靠得多；逐字解析，不编造。"""
    if not body: return {}
    m = re.search(r'"article"\s*:\s*\{', body)
    if not m: return {}
    seg = body[m.start():m.start() + 6000]
    def js(key):
        mm = re.search(r'"%s"\s*:\s*"((?:\\u[0-9a-fA-F]{4}|\\.|[^"\\])*)"' % key, seg)
        if not mm: return None
        try: return json.loads('"' + mm.group(1) + '"')
        except Exception: return None
    out = {"author": js("name"), "title": js("title"), "lid": js("lid")}
    pm = re.search(r'"solutionFor"\s*:\s*\{[^}]*?"pid"\s*:\s*"([A-Z]\d+)"', seg)
    if pm: out["pid"] = pm.group(1)
    return out

def guess_author(body):
    """只从页面里真实出现的字段提取；提取不到绝不编造。"""
    if not body: return "见原文页面署名（页面未给出可解析作者字段）"
    meta = article_meta(body)
    if meta.get("author"):
        v = html.unescape(meta["author"]).strip()
        if v and not re.search(r"^洛谷$|Luogu|^admin$|^system$", v, re.I):
            return v
    pats = [
        r'<meta[^>]+name=["\']author["\'][^>]+content=["\']([^"\']{1,60})["\']',
        r'"userName"\s*:\s*"([^"]{1,60})"',
        r'作者[：:]\s*([^\s<，,]{1,40})',
    ]
    for p in pats:
        m = re.search(p, body, re.I | re.S)
        if m:
            v = html.unescape(m.group(1)).strip()
            if v and not re.search(r"洛谷|Luogu|admin|system", v, re.I):
                return v
    return "见原文页面署名（页面未给出可解析作者字段）"

def guess_title(body, lid, problem):
    meta = article_meta(body)
    if meta.get("title"):
        t = html.unescape(meta["title"]).strip()
        if t and len(t) < 160: return t
    m = re.search(r"<title>(.*?)</title>", body or "", re.S | re.I)
    if m:
        t = html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip()
        t = re.sub(r"\s*[|\-–]\s*洛谷.*$", "", t).strip()
        if t and len(t) < 120: return t
    return f"{problem} 题解 · {lid}"

def load_ingested():
    out = {}
    if not os.path.isdir(INGEST): return out
    for fn in sorted(os.listdir(INGEST)):
        if not fn.endswith(".json"): continue
        p = os.path.join(INGEST, fn)
        try: d = json.load(open(p, encoding="utf-8"))
        except Exception: continue
        lid = d.get("id") or d.get("lid") or fn[:-5]
        out[lid] = d
    return out

def load_reproduced():
    """仓库里逐字复现的代码（04_复现代码/），按 8 位编号 / 题号关联。
    与 _build_site.py 的关联规则一致；用于给无正文副本的条目也生成内容签名。"""
    by_lid, by_prob = {}, {}
    d = os.path.join(REPO, "04_复现代码")
    if not os.path.isdir(d): return by_lid, by_prob
    for fn in sorted(os.listdir(d)):
        if not fn.endswith((".cpp", ".c")): continue
        try: txt = open(os.path.join(d, fn), encoding="utf-8").read()
        except Exception: continue
        m = re.search(r"[_\-]([a-z0-9]{8})(?:[_\.]|$)", fn)
        if m:
            by_lid.setdefault(m.group(1), []).append((fn, txt)); continue
        pm = re.search(r"[PpSsXx](\d{4})", fn)
        if pm: by_prob.setdefault("P" + pm.group(1), []).append((fn, txt))
    return by_lid, by_prob

def build_entry(lid, problem, url, ingested, reproduced=None):
    body = (ingested or {}).get("body", "")
    code_blocks = (ingested or {}).get("code_blocks") or []
    content = body if body else (code_blocks[0] if code_blocks else "")
    scope_kind = "正文+代码块"
    if not content and reproduced:
        content = "\n\n".join(t for _, t in reproduced)
        scope_kind = "逐字复现代码（原文链接留痕，正文未单独存档）"
    fetched = (ingested or {}).get("fetched_at") or ""
    if not fetched and reproduced and not body:
        # 无正文副本：用「逐字复现（见批次报告）」作稳定归档基准。
        # 不能取文件 mtime —— Actions checkout 会重置 mtime，导致每次重生成
        # 签名全变、上百个页面产生无意义 diff。
        fetched = "逐字复现（见 01_批次清单/对应批次报告）"
    if not fetched:
        fetched = now()
    cs = sha(content) if content else ""
    scope = scope_kind if content else "仅索引（正文待补录）"
    # 内容完整性签名：把 编号/原文/内容哈希/取回时间 绑在一起，便于离线核对是否被改动
    sig = sha(f"{lid}|{url}|{cs}|{fetched}|{scope}")[:32] if cs else ""
    author = guess_author(body)
    title = guess_title(body, lid, problem)
    citation = (f"{author}. 《{title}》. 洛谷, 原文: {url}"
                f"（本仓库归档于 {fetched}，内容 sha256: {cs[:16] or '待补录'}，"
                f"完整性签名: {sig or '待补录'}）. 版权归原作者所有，仅作学术归档引用。")
    return {
        "lid": lid, "problem": problem,
        "original_url": url,
        "author": author,
        "author_source": "原文页面内嵌 data.article.author.name" if (body and (article_meta(body).get("author"))) else "页面未给出可解析作者字段",
        "title": title,
        "publisher": "洛谷（www.luogu.com）",
        "fetched_at": fetched,
        "content_sha256": cs,
        "signature": sig,
        "signature_note": "sha256 内容完整性签名（非加密签名），绑定 编号/原文/内容哈希/归档基准时间",
        "scope": scope,
        "source_files": ([f"04_复现代码/{fn}" for fn, _ in reproduced]
                         if (reproduced and scope_kind != "正文+代码块") else []),
        "citation": citation,
        "rights": RIGHTS,
        "source_file": ("site/data/ingested/%s.json" % lid) if ingested else "",
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    rows = list(csv.DictReader(open(CSVP, encoding="utf-8-sig")))
    ing = load_ingested()
    rep_lid, rep_prob = load_reproduced()
    old = {}
    if os.path.exists(OUT):
        try: old = json.load(open(OUT, encoding="utf-8"))
        except Exception: pass
    prov, missing = {}, []
    for r in rows:
        lid, url = r["编号"], r["URL"]
        if not url or not url.startswith("http"):
            missing.append((lid, "缺原文链接")); continue
        e = build_entry(lid, r["题号"], url, ing.get(lid),
                        rep_lid.get(lid) or rep_prob.get(r["题号"]))
        # 已有正文取回时间不随意刷新，保持签名稳定
        if lid in old and old[lid].get("content_sha256") == e["content_sha256"] \
           and old[lid].get("content_sha256"):
            e["fetched_at"] = old[lid]["fetched_at"]
            e["signature"] = old[lid]["signature"]
            e["citation"] = old[lid]["citation"]
        prov[lid] = e
    payload = {
        "说明": "每条收录内容的原文链接、作者署名（优先取原文页面内嵌 author.name）、归档/取回时间与 sha256 内容完整性签名；无正文副本者以「逐字复现（见批次报告）」为稳定归档基准",
        "生成时间": now(),
        "条目数": len(prov),
        "版权声明": RIGHTS,
        "entries": prov,
    }
    if args.check:
        print("校验：", len(prov), "条 | 缺项", missing[:10])
        return 1 if missing else 0
    tmp = OUT + ".tmp"
    open(tmp, "w", encoding="utf-8").write(json.dumps(payload, ensure_ascii=False, indent=1))
    os.replace(tmp, OUT)
    signed = sum(1 for e in prov.values() if e["signature"])
    print(f"provenance.json：{len(prov)} 条 | 有内容完整性签名 {signed} | 仅索引 {len(prov)-signed}")
    if missing: print("缺项：", missing[:10])
    return 0

if __name__ == "__main__":
    sys.exit(main())
