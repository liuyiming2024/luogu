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

# ------------------------------------------------------------ 来源署名 / 完整性签名
RIGHTS_SHORT = ("版权归原作者及洛谷所有；本库仅作个人学习 / 学术研究的离线归档与校对留痕，"
                "不用于商业用途。每篇保留原文链接与作者署名；权利人可申请移除，"
                "详见《归档与版权声明》。")
PROV_PATH = os.path.join(DATA, "provenance.json")
PROV = {}
if os.path.exists(PROV_PATH):
    try:
        PROV = json.load(open(PROV_PATH, encoding="utf-8")).get("entries", {})
    except Exception:
        PROV = {}
RIGHTS_PAGE = "归档与版权声明.md.html"

def prov_of(lid, url, prob):
    return PROV.get(lid, {
        "original_url": url, "author": "见原文页面署名（正文待补录）",
        "title": f"{prob} 题解 · {lid}", "fetched_at": "待补录",
        "content_sha256": "", "signature": "", "scope": "仅索引（正文待补录）",
        "citation": f"《{prob} 题解 · {lid}》. 洛谷, 原文: {url}. 版权归原作者所有，仅作学术归档引用。",
    })

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
            # 防御：某行被上面的排除规则挡住、却没被任何专用分支接住时，
            # 段落 while 一次不进 → 若不强制推进 i 会无限循环（第12批文档触发）。
            if not buf:
                buf.append(L.strip()); i += 1
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
for _extra in ["爬取进度.md", "基础设施审查与验证报告.md",
               "全量爬取与校对说明.md", "归档与版权声明.md"]:
    # 归档与版权声明在 00_总览 里已由上面的循环收集，避免重复
    if _extra == "归档与版权声明.md": continue
    _p = os.path.join(REPO, "02_文章编号索引", _extra)
    if os.path.exists(_p):
        REPORT_FILES.append(("02_文章编号索引", _extra, _p))
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
    pr = prov_of(lid, r["URL"], prob)
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
<tr><th>原文地址</th><td><a href="{esc(pr['original_url'])}" referrerpolicy="no-referrer" rel="noopener">{esc(pr['original_url'])}</a> <span class="hint">（原文链接 · 点击跳转；离线时仅留来源）</span></td></tr>
<tr><th>原文作者</th><td>{esc(pr['author'])}</td></tr>
<tr><th>归档 / 取回时间</th><td>{esc(pr['fetched_at'])} · {esc(pr['scope'])}</td></tr>
<tr><th>内容完整性签名</th><td><code>{esc(pr['signature'] or '待补录')}</code><span class="hint"> · sha256 内容校验值（非加密签名）</span></td></tr>
</tbody></table>"""]

    parts.append(f'''<h2>引用与署名</h2>
<div class="src" style="border-left:3px solid var(--acc)"><p>{esc(pr['citation'])}</p>
<p class="hint">{esc(RIGHTS_SHORT)} <a href="../reports/{RIGHTS_PAGE}">《归档与版权声明》</a></p></div>''')

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
    parts.append('</ul></main><footer><div class="wrap">纯离线静态页 · 无外部资源 · 无网络请求 · 原文版权归作者所有 · '
                 + esc(RIGHTS_SHORT[:38]) + ' … <a href="../reports/' + RIGHTS_PAGE + '">声明</a></div></footer></body></html>')

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
        "original_url": pr["original_url"], "author": pr["author"],
        "fetched_at": pr["fetched_at"], "content_sha256": pr["content_sha256"],
        "signature": pr["signature"], "scope": pr["scope"],
        "citation": pr["citation"], "rights": RIGHTS_SHORT,
    })

# ------------------------------------------------------------ 数据文件
with open(os.path.join(DATA, "articles.json"), "w", encoding="utf-8") as f:
    json.dump({
        "说明": "已发现的全部 8 位文章编号，按题号升序、同题按编号字典序有序编目；逐条判定是否题解",
        "收录总数": len(articles),
        "全站规模说明": "洛谷全站题解约 16 万篇；本表为当前已发现并登记的全部编号，非全站遍历结果。新增编号用 ingest.py 低频补录。",
        "引用规范": "每条含原文链接 original_url、作者署名 author、取回时间 fetched_at、content_sha256 与完整性签名 signature；见 site/data/provenance.json",
        "版权声明": RIGHTS_SHORT,
        "articles": articles,
    }, f, ensure_ascii=False, indent=1)
with open(os.path.join(DATA, "articles.csv"), "w", encoding="utf-8-sig", newline="") as f:
    wr = csv.DictWriter(f, fieldnames=["lid", "problem", "title", "is_article", "class",
                                       "batch", "verifiable", "note", "url", "page", "has_code",
                                       "original_url", "author", "fetched_at", "signature"])
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
<p class="hint">📌 <b>引用与署名</b>：每篇均保留<a href="reports/{RIGHTS_PAGE}">原文链接、作者署名、取回时间与内容完整性签名</a>；版权归原作者及洛谷所有，本库仅作学术归档留痕，权利人可申请移除。</p>
<p class="hint">⚙️ <b>运行态自己加 / 自己下载</b>：静态站只是壳，GitHub Actions 即现成运行态。
首次在 Secrets 写一次 <code>LUOGU_SUBMIT_CONSENT</code> 后，评论 / 发文 / 洛谷 IDE 评测 →
本地待推队列 → <b>自动写回仓库 outbox</b> → Action 自动低频代提交，
<b>本人不用提交、不用手动跑工作流</b>；凭据走 Secrets，<b>不进仓库</b>。授权由本人自行完成（不代填、不接收 token 明文），
保存路径见<a href="reports/帮助手册.md.html">帮助手册 5d</a>；未配置 consent 永远只预览。
<a href="reports/架构可达性测试报告.md.html">架构可达性报告</a> ·
<a href="reports/帮助手册.md.html">帮助手册 5c</a>。</p>
<p class="hint">💬 <b>评论持久化 = 直接推洛谷</b>：本地先存离线副本 + 待推队列，由持有个人账号登录态的一端低频推送；<b>静态站不直连洛谷</b>（CORS + HttpOnly/SameSite cookie + CSRF 不可达）。详见<a href="reports/架构可达性测试报告.md.html">架构可达性测试报告</a>。</p>
<p class="hint">⚙ <b>真编译借洛谷 IDE</b>（联网+已登录、用你自己的账号，新窗口 + 剪贴板）；<b>所有写操作先过后果自担确认门</b>（勾选 + 输入「我自担」）。见<a href="reports/帮助手册.md.html">帮助手册</a>与<a href="reports/隐私声明与数据处理条款.md.html">隐私声明</a>。</p>
</div></header>
<main class="wrap"><div id="groups">{''.join(cards)}</div>
<p id="none" class="empty" hidden>没有匹配的文章。</p>
<h2>归档资料</h2><ul class="links">
{''.join(f'<li><a href="{report_map[fn]}">{esc(fn)}</a></li>' for _, fn, _ in REPORT_FILES)}
<li><a href="data/articles.json">机读索引 articles.json</a></li>
<li><a href="data/articles.csv">机读索引 articles.csv</a></li>
<li><a href="data/provenance.json">来源署名与完整性签名 provenance.json</a></li>
<li><a href="reports/{RIGHTS_PAGE}">归档与版权声明（原文引用 / 移除入口）</a></li>
<li><a href="reports/爬取进度.md.html">爬取进度</a></li>
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
</main><footer><div class="wrap">纯离线静态页 · 无 CDN · 无外部资源 · 不发起任何网络请求 · 仓库内无账号与凭据<br>{esc(RIGHTS_SHORT[:60])} … <a href="reports/{RIGHTS_PAGE}">《归档与版权声明》</a></div></footer>
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
- `articles/<编号>.html` —— 每篇一页：判定、归类、批次、**原文地址/作者/取回时间/完整性签名/可复制引用**、代码、反例、复现命令
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

仓库已设为**公开**并由 GitHub Pages 上线归档库网页。站点内不含账号、密码、令牌；每篇保留原文链接、作者署名与内容完整性签名，离线时链接仅留来源。
""")

# 生成器本身已位于仓库根目录，clone 后可直接重跑

print("SITE_PAGES", 2 + len(articles) + len(REPORT_FILES))
print("ARTICLES", len(articles))
print("WITH_CODE", sum(1 for a in articles if a["has_code"]))
print("REPORTS", len(REPORT_FILES))
# ============================================================ 本地轻量版 luogu 层
# （最终要求 2026-11-27；追加在末尾，确保 assets/style.css 与 app.js 已写完，
#  因为上面的选择性清理会 rmtree site/assets/）
import shutil as _sh, html as _html

def _inject(fp, depth):
    if not os.path.exists(fp): return
    t = open(fp, encoding="utf-8").read()
    pre = "../" * depth
    if "local.css" not in t:
        t = t.replace("</head>", f'<link rel="stylesheet" href="{pre}assets/local.css"></head>')
    if "local.js" not in t:
        t = t.replace("</body>", f'<script src="{pre}assets/local.js"></script></body>')
    open(fp, "w", encoding="utf-8").write(t)

# 1) 常驻前端资产（site_src/ 是源，assets/ 是产物；重生成不丢源文件）
_src = os.path.join(REPO, "site_src")
for _f in ["local.css", "local.js"]:
    _p = os.path.join(_src, _f)
    if os.path.exists(_p):
        _sh.copyfile(_p, os.path.join(SITE, "assets", _f))

# 2) 数据脚本（内联，零 fetch）
_adm = os.path.join(DATA, "self.json")
_self = json.load(open(_adm, encoding="utf-8")).get("operators", []) if os.path.exists(_adm) else []
open(os.path.join(SITE, "assets", "self.js"), "w", encoding="utf-8").write(
    "window.LL_SELF=" + json.dumps(_self, ensure_ascii=False) + ";\n")

# 3) std 期望输出表 = 甲类反例 + 少量标准用例（供 IDE「本地评测」对照）
_cases = [{"label": "P1001 A+B 标准用例", "input": "1 2", "expect": "3",
           "lid": "zaohomhi", "source": "库中 std 对照表", "hack": "—"}]
for L in hack_lines:
    if "~~" in L:      # 第 17 批撤销的 H-006/007 不进测试点
        continue
    cs = [c.strip() for c in L.strip().strip("|").split("|")]
    if len(cs) < 4: continue
    e2a = re.sub(r"\*\*|`", "", cs[3])
    exp = e2a.split("→")[0].strip().split("/")[0].strip()
    lid_m = re.search(r"[a-z0-9]{8}", cs[1])
    _cases.append({"label": re.sub(r"\*\*|`", "", cs[0]) + " " + re.sub(r"\*\*|`", "", cs[1]),
                   "input": re.sub(r"\*\*|`", "", cs[2])[:90],
                   "expect": exp, "lid": lid_m.group(0) if lid_m else "",
                   "source": "甲类合法反例（题面内）", "hack": e2a[:90]})
# 3b) 追加本地 std 期望表（自写独立正确解逐条跑出；不引用官方数据）
_exp_p = os.path.join(DATA, "std_expect.json")
if os.path.exists(_exp_p):
    _exp = json.load(open(_exp_p, encoding="utf-8"))
    for _pid, _v in _exp.get("题目", {}).items():
        for _i, _c in enumerate(_v["cases"][:12]):
            _cases.append({"label": "%s %s · std#%d" % (_pid, _v["title"], _i + 1),
                           "input": _c["in"].strip(), "expect": _c["out"],
                           "lid": "", "source": "本地 std 期望输出表（独立正确解）",
                           "hack": "—"})
    print(" 本地评测测试点：+", sum(min(12, len(v["cases"])) for v in _exp["题目"].values()),
          "组 std 期望")
open(os.path.join(SITE, "assets", "judge_cases.js"), "w", encoding="utf-8").write(
    "window.LL_JUDGE_CASES=" + json.dumps(_cases, ensure_ascii=False) + ";\n")

# 3c) std 候选台账（脚本只写「待人工审核」，不自动迁入）
_cand_p = os.path.join(DATA, "std_candidates.json")
_cand = json.load(open(_cand_p, encoding="utf-8")) if os.path.exists(_cand_p) else {"条目": [], "统计": {}}
open(os.path.join(SITE, "assets", "std_candidates.js"), "w", encoding="utf-8").write(
    "window.LL_STD_CANDIDATES=" + json.dumps(_cand, ensure_ascii=False) + ";\n")

# 3d) 代审台账（证据驱动；只读呈现，页面不判定、不迁入）
_revp = os.path.join(DATA, "std_reviews.json")
_rev = json.load(open(_revp, encoding="utf-8")) if os.path.exists(_revp) else {"条目": [], "统计": {}}
open(os.path.join(SITE, "assets", "std_reviews.js"), "w", encoding="utf-8").write(
    "window.LL_STD_REVIEWS=" + json.dumps(_rev, ensure_ascii=False) + ";\n")

# 4) 编译镜像清单：内置为功能，但不写死可能失效的第三方地址
_mirrors = [
    {"lang": "C++", "url": "", "note": "按你所在网络填写国内易联镜像（示例结构，不写死地址）"},
    {"lang": "Python", "url": "", "note": "同上；无网时先缓存，下载后本地编译"},
    {"lang": "C", "url": "", "note": "同上；页面只在主动点击时探测可达性"},
]
open(os.path.join(SITE, "assets", "mirrors.js"), "w", encoding="utf-8").write(
    "window.LL_MIRRORS=" + json.dumps(_mirrors, ensure_ascii=False) + ";\n")

# 5) 给所有既有页面注入主题与逻辑
for _dp, _dn, _fn in os.walk(SITE):
    if os.path.basename(_dp) == "data": continue
    _depth = 0 if os.path.normpath(_dp) == os.path.normpath(SITE) else 1
    for _f in _fn:
        if _f.endswith(".html"):
            _inject(os.path.join(_dp, _f), _depth)

# 6) 首页：内联文章数据 + 主页价值区块
_idxp = os.path.join(SITE, "index.html")
_t = open(_idxp, encoding="utf-8").read()
_mini = [{"lid": a["lid"], "problem": a["problem"], "page": a["page"], "class": a["class"]}
         for a in articles]
_t = _t.replace('<main class="wrap"><div id="groups">',
                '<main class="wrap"><div id="ll-home"></div><script>window.LL_ARTICLES='
                + json.dumps(_mini, ensure_ascii=False) + ';</script><div id="groups">')
open(_idxp, "w", encoding="utf-8").write(_t)
_inject(_idxp, 0)

# 7) 三个子页面
def _page(title, page_id, body, extra_js=""):
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_html.escape(title)} · 本地轻量版 luogu</title>
<link rel="stylesheet" href="assets/style.css"><link rel="stylesheet" href="assets/local.css"></head>
<body data-page="{page_id}"><main class="wrap">
<h1>{_html.escape(title)}</h1>
<p class="hint">纯静态 · 页面加载零外网请求 · 评论/推送/设置均存浏览器本地</p>
{body}
</main><div class="ll-foot wrap">本地版、轻量版 luogu · 版权归原作者及洛谷所有 ·
<a href="reports/归档与版权声明.md.html">归档与版权声明</a> ·
<a href="reports/帮助手册.md.html">帮助手册</a></div>
<script src="assets/self.js"></script><script src="assets/judge_cases.js"></script><script src="assets/std_candidates.js"></script><script src="assets/std_reviews.js"></script>
<script src="assets/mirrors.js"></script>{extra_js}
<script src="assets/local.js"></script></body></html>'''

open(os.path.join(SITE, "problems.html"), "w", encoding="utf-8").write(_page(
    "题目 · IDE · 本地评测", "problems",
    '<div class="ll-sec"><h2>题目附件（库中缓存）</h2><div class="ll-card">'
    '<p class="ll-empty">附件按「题面 &gt; 题解 &gt; 学术类文章 &gt; 其它」优先级按需抓取；'
    '未缓存的条目不硬造，低频补录后自动出现。</p></div></div>'
    '<div id="ll-ide"></div><div id="ll-hacks"></div><div id="ll-mirrors"></div>'))
open(os.path.join(SITE, "submit.html"), "w", encoding="utf-8").write(_page(
    "std 工单（投稿）", "submit",
    '<div id="ll-submit"></div><div id="ll-std-cand"></div><div id="ll-std-rev"></div>'))
open(os.path.join(SITE, "self.html"), "w", encoding="utf-8").write(_page(
    "本地操作 · 只认 token 不认人", "self", '<div id="ll-admin"></div>'))

# 8) API 契约也做成可点开的报告页，并挂到首页资料清单
_apip = os.path.join(REPO, "api", "API契约.md")
if os.path.exists(_apip):
    _body = md2html(open(_apip, encoding="utf-8").read())
    open(os.path.join(SITE, "reports", "API契约.md.html"), "w", encoding="utf-8").write(
        '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>API契约 · 离线归档</title><link rel="stylesheet" href="../assets/style.css"></head>'
        '<body><header class="top"><a href="../index.html">← 归档首页</a></header>'
        '<main class="doc">' + _body + '</main></body></html>')
    _inject(os.path.join(SITE, "reports", "API契约.md.html"), 1)
    _t = open(_idxp, encoding="utf-8").read()
    _t = _t.replace('<h2>归档资料</h2><ul class="links">',
        '<h2>归档资料</h2><ul class="links">'
        '<li><a href="reports/API契约.md.html">API契约（只认 token 不认人）</a></li>'
        '<li><a href="problems.html">题目 / IDE / 本地评测</a></li>'
        '<li><a href="submit.html">std 投稿</a></li><li><a href="self.html">本地操作面板</a></li>')
    open(_idxp, "w", encoding="utf-8").write(_t)

# 9) 站点说明补一段
_srp = os.path.join(SITE, "README.md")
with open(_srp, "a", encoding="utf-8") as _f:
    _f.write("\n## 本地轻量版 luogu 层（2026-11-27）\n\n"
             "- `assets/local.css` / `local.js`：独立洛谷风主题、三态身份、Markdown 评论 + 算术验证码、"
             "IDE、本地评测、std 投稿、本人、编译环境内置下载面板\n"
             "- `problems.html` / `submit.html` / `self.html`：三个子页面\n"
             "- **评论持久化直接推洛谷**：本地先存 + 待推队列 + `/api/comments/push-luogu` 适配器；"
             "静态站不直连洛谷（跨源 + HttpOnly cookie + CSRF 不可达）\n"
             "- 页面加载零外网请求；`apiBase` 留空时全部功能纯本地可用\n"
             "- 架构可达性结论见 `reports/架构可达性测试报告.md.html`\n"
             "- **本人不用提交**：一次性 `LUOGU_SUBMIT_CONSENT` Secret + 前端 fine-grained token，\n"
             "  导出待推队列即自动入库，push/定时触发 Action 自动低频代提交 luogu；未授权只预览\n")

print(f"LOCAL_LUOGU 层：资产 {len(_mini)} 条数据 · {len(_cases)} 个测试点 · 3 个子页面 · 全页注入完成")
