#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 luogu 仓库资料生成一个「像保存站一样」的纯离线静态站点。
无 CDN、无外部依赖、无网络请求；双击 index.html 即可浏览。
"""
import os, re, csv, json, html, shutil, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
# 位于仓库根目录时以自身位置为准（clone 到任意路径都能重建）；否则用工作区默认路径
REPO = _HERE if os.path.isdir(os.path.join(_HERE, "02_文章编号索引")) else "/data/workspace/luogu_repo"
SITE = os.path.join(REPO, "site")
DATA = os.path.join(SITE, "data")
# 选择性清理：只重建生成器产出的目录；**绝不删除** site/ 下的常驻资产
# （ingest.py / lowfreq_fetch.py / data/ingested/ / 取回日志），否则离线补录成果会被抹掉。
os.makedirs(SITE, exist_ok=True)
os.makedirs(DATA, exist_ok=True)
for sub in ["articles", "reports", "assets"]:
    _p = os.path.join(SITE, sub)
    if os.path.exists(_p):
        shutil.rmtree(_p)
    os.makedirs(_p)
for _f in ["index.html", "README.md"]:
    _p = os.path.join(SITE, _f)
    if os.path.exists(_p):
        os.remove(_p)
for _f in ["articles.json", "articles.csv"]:
    _p = os.path.join(DATA, _f)
    if os.path.exists(_p):
        os.remove(_p)

def esc(s):
    return html.escape(str(s), quote=True)

# ------------------------------------------------------------ 极简 Markdown 渲染
def inline(t):
    t = esc(t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    return t

def md2html(md):
    lines = md.splitlines()
    out, i, n = [], 0, len(lines)
    while i < n:
        L = lines[i]
        # 代码块
        if L.strip().startswith("```"):
            lang = L.strip()[3:].strip()
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i]); i += 1
            i += 1
            out.append(f'<pre class="code"><code>{esc(chr(10).join(buf))}</code></pre>')
            continue
        # 表格
        if L.strip().startswith("|") and i + 1 < n and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i+1]):
            head = [c.strip() for c in L.strip().strip("|").split("|")]
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            t = ['<table class="tb"><thead><tr>']
            t += [f"<th>{inline(c)}</th>" for c in head]
            t.append("</tr></thead><tbody>")
            for r in rows:
                t.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            t.append("</tbody></table>")
            out.append("".join(t))
            continue
        # 标题
        m = re.match(r"^(#{1,6})\s+(.*)$", L)
        if m:
            lv = len(m.group(1))
            out.append(f"<h{lv}>{inline(m.group(2))}</h{lv}>")
            i += 1; continue
        # 水平线
        if re.match(r"^\s*(---|\*\*\*|___)\s*$", L):
            out.append("<hr>"); i += 1; continue
        # 引用
        if L.strip().startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip()[1:].strip()); i += 1
            out.append(f"<blockquote>{inline(' '.join(buf))}</blockquote>")
            continue
        # 列表
        if re.match(r"^\s*([-*]|\d+\.)\s+", L):
            ordered = bool(re.match(r"^\s*\d+\.\s+", L))
            tag = "ol" if ordered else "ul"
            buf = []
            while i < n and re.match(r"^\s*([-*]|\d+\.)\s+", lines[i]):
                buf.append(re.sub(r"^\s*([-*]|\d+\.)\s+", "", lines[i])); i += 1
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in buf) + f"</{tag}>")
            continue
        # 段落
        if L.strip():
            buf = []
            while i < n and lines[i].strip() and not re.match(
                r"^\s*(#{1,6}\s|```|\||>|[-*]\s|\d+\.\s|---|\*\*\*|___)", lines[i]):
                buf.append(lines[i].strip()); i += 1
            out.append(f"<p>{inline(' '.join(buf))}</p>")
            continue
        i += 1
    return "\n".join(out)

# ------------------------------------------------------------ 读索引
with open(os.path.join(REPO, "02_文章编号索引/article_index.csv"), encoding="utf-8-sig") as f:
    ROWS = list(csv.DictReader(f))

# ------------------------------------------------------------ 关联复现代码
CODE_DIR = os.path.join(REPO, "04_复现代码")
code_by_lid = {}
code_by_prob = {}
for fn in sorted(os.listdir(CODE_DIR)):
    if not fn.endswith((".cpp", ".c")):
        continue
    try:
        txt = open(os.path.join(CODE_DIR, fn), encoding="utf-8").read()
    except Exception:
        continue
    m = re.search(r"[_\-]([a-z0-9]{8})(?:[_\.]|$)", fn)
    if m:
        code_by_lid.setdefault(m.group(1), []).append(
            {"file": fn, "text": txt, "link": "编号精确匹配"})
        continue
    # 无 8 位编号：按题号关联（如 s1042.cpp / x3397_full.cpp / p1014_v6gwt3bu.cpp）
    pm = re.search(r"[PpSsXx](\d{4})", fn)
    if pm:
        prob = "P" + pm.group(1)
        code_by_prob.setdefault(prob, []).append(
            {"file": fn, "text": txt, "link": "按题号关联"})

# 反例行（按 lid 从总览 md 抽）
hacks_md = open(os.path.join(REPO, "00_总览/甲类合法反例_23条.md"), encoding="utf-8").read()
hack_lines = [L for L in hacks_md.splitlines() if L.strip().startswith("| H-")]

# ------------------------------------------------------------ 报告页
REPORT_FILES = []
for sub in ["01_批次清单", "00_总览"]:
    d = os.path.join(REPO, sub)
    for fn in sorted(os.listdir(d)):
        if fn.endswith(".md"):
            REPORT_FILES.append((sub, fn, os.path.join(d, fn)))
for sub, fn, p in REPORT_FILES:
    md = open(p, encoding="utf-8").read()
    body = md2html(md)
    page = f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(fn)} · 离线归档</title><link rel="stylesheet" href="../assets/style.css"></head>
<body><header class="top"><a href="../index.html">← 归档首页</a><span class="crumb">{esc(sub)} / {esc(fn)}</span></header>
<main class="doc">{body}</main><footer>纯离线静态页 · 无外部资源 · 无网络请求</footer></body></html>"""
    out = os.path.join(SITE, "reports", re.sub(r"[^\w\u4e00-\u9fa5.\-]", "_", fn)[:60] + ".html")
    open(out, "w", encoding="utf-8").write(page)
report_map = {}
for sub, fn, p in REPORT_FILES:
    out = re.sub(r"[^\w\u4e00-\u9fa5.\-]", "_", fn)[:60] + ".html"
    report_map[fn] = "reports/" + out

# ------------------------------------------------------------ 文章页
CSS_COMMON = "../assets/style.css"
articles = []
for r in ROWS:
    lid, prob, cls = r["编号"], r["题号"], r["归类"]
    codes = list(code_by_lid.get(lid, [])) + list(code_by_prob.get(prob, []))
    # merge low-frequency ingested body/code (site/data/ingested/<lid>.json)
    ing = os.path.join(DATA, "ingested", lid + ".json")
    extra_body = ""
    if os.path.exists(ing):
        try:
            obj = json.load(open(ing, encoding="utf-8"))
            extra_body = obj.get("content", "")
            c = obj.get("code", "")
            if c:
                if isinstance(c, str):
                    codes.append({"file": "ingested/" + lid, "text": c, "link": "补录正文"})
                elif isinstance(c, list):
                    for it in c:
                        codes.append({"file": it.get("file", "ingested"),
                                      "text": it.get("text", ""), "link": "补录正文"})
        except Exception:
            pass
    hks = [L for L in hack_lines if lid in L]
    parts = [f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(prob)} · {esc(lid)} · 题解归档</title><link rel="stylesheet" href="{CSS_COMMON}"></head>
<body><header class="top"><a href="../index.html">← 归档首页</a><span class="crumb">题解 / {esc(prob)} / {esc(lid)}</span></header>
<main class="article"><h1>{esc(prob)} <span class="lid">{esc(lid)}</span></h1>
<div class="badge {esc(cls.split('·')[0])}">{esc(cls)}</div>
<table class="tb meta"><tbody>
<tr><th>是否题解</th><td>{esc(r['是否题解'])}（{esc(r['题解类型'])}）</td></tr>
<tr><th>归类</th><td>{esc(cls)}</td></tr>
<tr><th>批次</th><td>{esc(r['批次'])}</td></tr>
<tr><th>可逐字验证</th><td>{esc(r['可逐字验证'])}</td></tr>
<tr><th>判定备注</th><td>{esc(r['备注'])}</td></tr>
<tr><th>原文地址</th><td><a href="{esc(r['URL'])}" referrerpolicy="no-referrer">{esc(r['URL'])}</a><span class="hint">（离线时链接不可达，仅留来源）</span></td></tr>
</tbody></table>"""]

    if extra_body:
        parts.append('<h2>题解正文 · 低频补录</h2>')
        parts.append(md2html(extra_body))
    if codes:
        parts.append(f'<h2>题解代码 · 逐字取回 + 最小外壳（{len(codes)} 份）</h2>')
        parts.append('<p class="hint">代码只是辅助：只补 include / main / 必要声明，缺头文件与页面吞字符不计缺陷，仅验核心逻辑。</p>')
        for c in codes:
            parts.append(f'<div class="src"><div class="srcname">{esc(c["file"])} '
                         f'<span class="hint">· {esc(c["link"])}</span></div>'
                         f'<pre class="code"><code>{esc(c["text"])}</code></pre></div>')
    else:
        parts.append('<div class="empty">正文 / 代码待补录：本编号已登记，逐字取回后由 <code>ingest.py</code> 回填。</div>')

    if hks:
        parts.append('<h2>甲类合法反例（题面内 · 确定性 WA/RE）</h2>')
        parts.append('<table class="tb"><thead><tr><th>编号</th><th>题解</th><th>代表输入</th><th>期望 → 实际</th></tr></thead><tbody>')
        for L in hks:
            cells = [c.strip() for c in L.strip().strip("|").split("|")]
            parts.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells) + "</tr>")
        parts.append("</tbody></table>")

    parts.append('<h2>复现</h2><pre class="code"><code>'
                 + esc(f'g++ -std=c++17 -O2 -o /tmp/t 04_复现代码/<对应文件>\n'
                       f'echo "<题面内输入>" | /tmp/t') + '</code></pre>')

    rel_reports = [fn for fn in report_map if r["批次"].replace("批", "") in fn or r["批次"] in fn]
    parts.append('<h2>相关报告</h2><ul class="links">')
    for fn in sorted(rel_reports)[:6]:
        parts.append(f'<li><a href="../{report_map[fn]}">{esc(fn)}</a></li>')
    parts.append(f'<li><a href="../{report_map.get("三类口径与累计统计.md","")}">三类口径与自查纪律</a></li>')
    parts.append('</ul></main><footer>纯离线静态页 · 无外部资源 · 无网络请求</footer></body></html>')

    outp = os.path.join(SITE, "articles", lid + ".html")
    open(outp, "w", encoding="utf-8").write("\n".join(parts))
    articles.append({
        "lid": lid, "problem": prob, "title": f"{prob} 题解 · {lid}",
        "is_article": r["是否题解"], "article_type": r["题解类型"],
        "class": cls, "batch": r["批次"], "verifiable": r["可逐字验证"],
        "note": r["备注"], "url": r["URL"],
        "page": f"articles/{lid}.html",
        "code_files": [c["file"] for c in codes],
        "has_code": bool(codes),
    })

# ------------------------------------------------------------ 数据文件
with open(os.path.join(DATA, "articles.json"), "w", encoding="utf-8") as f:
    json.dump({
        "说明": "已发现的全部 8 位文章编号，按题号升序、同题按编号字典序有序编目；逐条判定是否题解",
        "收录总数": len(articles),
        "全站规模说明": "洛谷全站题解约 16 万篇；本表为当前已发现并登记的全部编号，非全站遍历结果。新增编号用 ingest.py 低频补录。",
        "articles": articles,
    }, f, ensure_ascii=False, indent=1)
with open(os.path.join(DATA, "articles.csv"), "w", encoding="utf-8-sig", newline="") as f:
    wr = csv.DictWriter(f, fieldnames=["lid", "problem", "title", "is_article", "class",
                                       "batch", "verifiable", "note", "url", "page", "has_code"])
    wr.writeheader()
    for a in articles:
        wr.writerow({k: a[k] for k in wr.fieldnames})

# ------------------------------------------------------------ 首页
stat = {}
for a in articles:
    stat[a["class"]] = stat.get(a["class"], 0) + 1
by_prob = {}
for a in articles:
    by_prob.setdefault(a["problem"], []).append(a)
def pkey(p):
    m = re.fullmatch(r"P(\d{4})", p)
    return int(m.group(1)) if m else 99999

cards = []
for p in sorted(by_prob, key=pkey):
    cards.append(f'<section class="group"><h2 id="{esc(p)}">{esc(p)} <span class="cnt">{len(by_prob[p])} 篇</span></h2><div class="grid">')
    for a in by_prob[p]:
        cards.append(f'''<a class="card {esc(a['class'].split('·')[0])}" href="{esc(a['page'])}"
 data-k="{esc((a['problem']+' '+a['lid']+' '+a['class']+' '+a['batch']+' '+a['note']).lower())}">
<div class="ct"><span class="lid">{esc(a['lid'])}</span><span class="tag">{esc(a['class'])}</span></div>
<div class="cnote">{esc(a['note'][:64])}</div>
<div class="cb">{esc(a['batch'])} · {"有代码" if a['has_code'] else "待补录"}</div></a>''')
    cards.append("</div></section>")

stat_html = "".join(
    f'<div class="stat"><b>{v}</b><span>{esc(k)}</span></div>'
    for k, v in sorted(stat.items()))

index = f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>洛谷题解离线归档 · 本地保存站</title><link rel="stylesheet" href="assets/style.css"></head>
<body>
<header class="hero"><div class="wrap">
<h1>洛谷题解 · 离线归档</h1>
<p class="sub">像保存站一样本地浏览：点开任意一篇看题解代码、判定结论与反例。<b>纯静态、零外网、零登录、零请求</b>。</p>
<div class="stats"><div class="stat"><b>{len(articles)}</b><span>已收录文章</span></div>{stat_html}</div>
<div class="ctrls">
<input id="q" type="search" placeholder="搜编号 / 题号 / 归类 / 备注…" autocomplete="off">
<div class="filters"><button class="on" data-f="all">全部</button><button data-f="甲">甲 已 hack</button><button data-f="乙">乙 笔误/防抄袭</button><button data-f="丙">丙 未 hack</button><button data-f="待补录">待补录</button></div>
</div>
<p class="hint">「枚举」= 对已发现的全部 8 位编号按题号升序、同题按编号字典序有序编目并逐条判定是否题解；<b>不对编号空间或全站做高频遍历</b>。新增编号用 <code>ingest.py</code> 低频补录。</p>
</div></header>
<main class="wrap"><div id="groups">{''.join(cards)}</div>
<p id="none" class="empty" hidden>没有匹配的文章。</p>
<h2>归档资料</h2><ul class="links">
{''.join(f'<li><a href="{report_map[fn]}">{esc(fn)}</a></li>' for _, fn, _ in REPORT_FILES)}
<li><a href="data/articles.json">机读索引 articles.json</a></li>
<li><a href="data/articles.csv">机读索引 articles.csv</a></li>
</ul>
<h2>关于「所有文章」</h2>
<p>本离线站当前收录 <b>{len(articles)}</b> 篇——即项目开始以来<b>已发现并登记的全部</b>题解文章（含正文/代码待补录的条目，一篇不漏）。
洛谷全站题解约 16 万篇；全量镜像需要归档数据源或极长时间的低频逐篇取回。
保存站实测（第 14 批）：直连全 403、文章/列表/搜索页均为 SPA 骨架、首页挂着
「AI 自动化程序不断请求保存 API，导致队列堵塞」降级公告，详见
`02_文章编号索引/保存站可用性记录.md`。配套 `site/lowfreq_fetch.py` 与
`tools/crawl_daemon.py`（默认 2 秒/次 + 抖动、跑 50 分钟歇 10 分钟、降级即停），
可在能访问保存站的网络里低频补录；全量长期跑见《全量爬取与校对说明.md》。
架构已按全量设计：<code>data/articles.json</code> 是有序主表，<code>ingest.py</code> 可持续灌入新文章并重生成页面，不需要改结构。</p>
</main><footer><div class="wrap">纯离线静态页 · 无 CDN · 无外部资源 · 不发起任何网络请求 · 仓库内无账号与凭据</div></footer>
<script src="assets/app.js"></script></body></html>"""
open(os.path.join(SITE, "index.html"), "w", encoding="utf-8").write(index)

# ------------------------------------------------------------ 样式 / 脚本
open(os.path.join(SITE, "assets/style.css"), "w", encoding="utf-8").write("""
:root{--bg:#0f1218;--panel:#171c25;--panel2:#1d2330;--fg:#e6e9ef;--mut:#98a2b3;--line:#2a3242;--acc:#6ea8fe;--a:#ff6b6b;--b:#f0b429;--c:#43c59e;--d:#8b93a7}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.7 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif}
a{color:var(--acc);text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:960px;margin:0 auto;padding:0 18px}
.hero{background:linear-gradient(160deg,#182033,#0f1218);border-bottom:1px solid var(--line);padding:30px 0 22px}
h1{margin:0 0 6px;font-size:26px;letter-spacing:.5px}.sub{color:var(--mut);margin:0 0 18px;font-size:14px}
.stats{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:18px}
.stat{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:10px 14px;min-width:92px}
.stat b{display:block;font-size:20px}.stat span{color:var(--mut);font-size:12px}
.ctrls{display:flex;flex-direction:column;gap:10px}
#q{width:100%;padding:11px 14px;border-radius:9px;border:1px solid var(--line);background:var(--panel2);color:var(--fg);font-size:15px;outline:none}
#q:focus{border-color:var(--acc)}
.filters{display:flex;gap:8px;flex-wrap:wrap}
.filters button{background:var(--panel);color:var(--mut);border:1px solid var(--line);border-radius:20px;padding:5px 13px;cursor:pointer;font-size:13px}
.filters button.on{background:var(--acc);color:#08101f;border-color:var(--acc);font-weight:600}
.hint{color:var(--mut);font-size:12.5px;margin:10px 0 0}
.top{position:sticky;top:0;background:rgba(15,18,24,.95);backdrop-filter:blur(6px);border-bottom:1px solid var(--line);padding:10px 18px;display:flex;gap:14px;align-items:center;font-size:13px;z-index:9}
.crumb{color:var(--mut)}
main{padding:22px 0 40px}
.group{margin:20px 0 26px}.group h2{font-size:17px;border-left:3px solid var(--acc);padding-left:10px;margin:0 0 12px}
.cnt{color:var(--mut);font-size:12px;font-weight:400;margin-left:6px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:11px}
.card{display:block;background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px;color:var(--fg);transition:.15s;border-left:3px solid var(--d)}
.card:hover{text-decoration:none;background:var(--panel2);transform:translateY(-1px)}
.card.甲{border-left-color:var(--a)}.card.乙{border-left-color:var(--b)}.card.丙{border-left-color:var(--c)}.card.待补录,.card.登记{border-left-color:var(--d)}
.ct{display:flex;justify-content:space-between;gap:8px;align-items:center;margin-bottom:7px}
.lid{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:14px;color:var(--acc)}
.tag{font-size:11px;color:var(--mut);white-space:nowrap}
.cnote{font-size:12.5px;color:var(--fg);opacity:.86;min-height:34px}
.cb{font-size:11px;color:var(--mut);margin-top:6px}
.badge{display:inline-block;padding:3px 11px;border-radius:20px;font-size:12px;background:var(--panel2);border:1px solid var(--line);margin-bottom:14px}
.badge.甲{color:var(--a);border-color:var(--a)}.badge.乙{color:var(--b);border-color:var(--b)}.badge.丙{color:var(--c);border-color:var(--c)}
.tb{border-collapse:collapse;width:100%;margin:12px 0;font-size:13.5px}
.tb th,.tb td{border:1px solid var(--line);padding:7px 10px;text-align:left;vertical-align:top}
.tb th{background:var(--panel2);color:var(--mut);font-weight:600;white-space:nowrap}
.meta th{width:110px}
h2{font-size:18px;margin:26px 0 8px}h3{font-size:15px}
.doc h1,.article h1{font-size:24px}
pre.code{background:#0b0e14;border:1px solid var(--line);border-radius:9px;padding:13px;overflow:auto;font:12.5px/1.6 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;color:#d7e0f0;white-space:pre}
code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;background:var(--panel2);padding:1px 5px;border-radius:4px;font-size:12.5px;color:#b9d2ff}
pre.code code{background:none;padding:0;color:inherit}
.src{margin:12px 0}.srcname{font-size:12px;color:var(--mut);margin-bottom:5px;font-family:ui-monospace,monospace}
.empty{background:var(--panel);border:1px dashed var(--line);border-radius:9px;padding:16px;color:var(--mut);font-size:13.5px}
blockquote{border-left:3px solid var(--acc);margin:12px 0;padding:6px 14px;color:var(--mut);background:var(--panel);border-radius:0 8px 8px 0}
hr{border:0;border-top:1px solid var(--line);margin:20px 0}
ul.links{columns:2;column-gap:22px;padding-left:20px;font-size:13.5px}ul.links li{break-inside:avoid;margin-bottom:5px}
footer{border-top:1px solid var(--line);color:var(--mut);font-size:12px;padding:16px 0 28px;text-align:center}
@media(max-width:620px){.grid{grid-template-columns:1fr}ul.links{columns:1}.stats{gap:6px}.stat{min-width:76px;padding:8px 10px}}
""")
open(os.path.join(SITE, "assets/app.js"), "w", encoding="utf-8").write("""
(function(){
  var q=document.getElementById('q'), cards=[].slice.call(document.querySelectorAll('.card')),
      groups=[].slice.call(document.querySelectorAll('.group')), none=document.getElementById('none'),
      btns=[].slice.call(document.querySelectorAll('.filters button')), cur='all';
  function apply(){
    var k=(q.value||'').trim().toLowerCase(), shown=0;
    cards.forEach(function(c){
      var ok=(cur==='all'||c.classList.contains(cur)) && (!k||c.dataset.k.indexOf(k)>=0);
      c.style.display=ok?'':'none'; if(ok)shown++;
    });
    groups.forEach(function(g){ g.style.display=g.querySelector('.card:not([style*="none"])')?'':'none'; });
    none.hidden=shown>0;
  }
  q.addEventListener('input',apply);
  btns.forEach(function(b){b.addEventListener('click',function(){
    btns.forEach(function(x){x.classList.remove('on')}); b.classList.add('on');
    cur=b.dataset.f; apply();
  })});
})();
""")

# ------------------------------------------------------------ 常驻脚本（不覆盖，缺失时从模板恢复）
# ingest.py = 低频补录入口；lowfreq_fetch.py = 2 秒一次的有序取回器。
# 两者都是可维护资产，重生成站点时绝不删除或覆盖；data/ingested/ 同理保留。
for _name, _tplname in [("ingest.py", "ingest_template.py"),
                        ("lowfreq_fetch.py", "lowfreq_fetch_template.py")]:
    _dst = os.path.join(SITE, _name)
    _tpl = os.path.join(REPO, "02_文章编号索引", _tplname)
    if not os.path.exists(_dst) and os.path.exists(_tpl):
        shutil.copyfile(_tpl, _dst)
os.makedirs(os.path.join(DATA, "ingested"), exist_ok=True)

# ------------------------------------------------------------ 站点说明
open(os.path.join(SITE, "README.md"), "w", encoding="utf-8").write(f"""# 离线保存站 · 使用说明

**双击 `index.html` 即可浏览**（或 `python3 -m http.server 8000` 后开 `localhost:8000/site/`）。
纯静态：无 CDN、无外部字体、无 JS 框架、不发起任何网络请求；离线、断网、无账号都能看。

## 有什么

- `index.html` —— 按题号分组的全部文章卡片，支持本地搜索与「甲/乙/丙/待补录」筛选
- `articles/<编号>.html` —— 每篇一页：是否题解判定、归类、批次、原文地址、逐字取回的题解代码、甲类反例、复现命令
- `reports/` —— {len(REPORT_FILES)} 份批次报告 + 总览文档，全部渲染成 HTML
- `data/articles.json` / `.csv` —— 有序主表，{len(articles)} 条，机读
- `ingest.py` —— 低频补录入口（写 CSV 主表）
- `lowfreq_fetch.py` —— 有序取回器，默认 2 秒/次，可切保存站 / luogu.com
- `tools/crawl_daemon.py` —— 大脚本：跑 50/歇 10、抖动、实时写回、三层校对
- `02_文章编号索引/全量爬取与校对说明.md` —— 全量汇集架构

## 「所有文章」的口径

本站收录 **{len(articles)} 个 8 位编号 = 项目开始以来已发现并登记的全部文章**，
含 1 个**非题解**规范文章（`zm6gqovk`），一篇不漏；`登记·不计数` 0 个。
另有 10 篇无 8 位编号的题解（vis 版、辅助示意版等）只在批次报告中验证，
故「逐篇验证 96 篇」与「编号 87 个」口径不同。
洛谷全站题解约 16 万篇；全量镜像必须有归档数据源或极长时间的低频逐篇取回。
保存站实测（第 14 批）：直连全 403 `policy_default_denied`，文章 / 列表 / 搜索 /
统计页均为 SPA 骨架，首页挂着「AI 自动化程序不断请求保存 API，导致队列堵塞」
降级公告——瓶颈不在频率。所以**不刷保存 API**；`lowfreq_fetch.py` 默认 2 秒/次、
有序队列、降级即停，留给能正常访问保存站的网络环境用。详见
`02_文章编号索引/保存站可用性记录.md`。

架构按全量设计：主表有序、补录器可无限追加、页面由脚本重生成，不需要改结构。

## 补录一篇新文章

```bash
# 1) 准备一个 JSON（字段见 ingest.py 顶部注释）
cat > new.json <<'EOF'
[{{"lid":"abcdefgh","problem":"P1002","title":"某篇题解","content":"正文…","code":"源码…","cls":"丙","batch":"第13批"}}]
EOF
# 2) 灌入主表
python3 site/ingest.py new.json
# 3) 重生成页面（生成器见仓库根目录或 02_文章编号索引/生成索引_本地参考.py 同批脚本）
```

有序性：每次补录后按「题号升序 → 编号字典序」重排，不对编号空间做遍历。

## 隐私

仓库已设为 **private**。站点内不含账号、密码、令牌；原文链接仅作来源留痕，离线时不可达。
""")

# 生成器本身已位于仓库根目录，clone 后可直接重跑

print("SITE_PAGES", 2 + len(articles) + len(REPORT_FILES))
print("ARTICLES", len(articles))
print("WITH_CODE", sum(1 for a in articles if a["has_code"]))
print("REPORTS", len(REPORT_FILES))