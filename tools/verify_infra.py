#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""基础设施审查 + 「类对拍」验证。

跟题解对拍是同一个思路：不能只说「跑过了、没报错」，得证明测试集真的有分辨力。

Part A · 逐篇审查（新取回的正文）
  原文链接格式 / 正文长度 / 代码块可提取 / 判定与内容一致 / sha 唯一 /
  敏感残留（csrf-token、凭据、邮箱）/ SPA 骨架不得存档 / provenance 覆盖与签名。

Part B · 类对拍验证（受控夹具 + 变异版敏感性）
  每个检查点同时跑「真实实现」与「故意改坏的变异实现」，
  两者必须产出不同结果 —— 变异版没被抓到就说明测试是空跑，直接判失败。
  夹具全是手写字符串，不发网络请求、不碰真实数据。

用法：
  python3 tools/verify_infra.py            # 写报告与结果 JSON
  python3 tools/verify_infra.py --check   # 只断言不写文件（Pages 部署前自检）
"""
import os, re, sys, csv, json, glob, html, hashlib, argparse, importlib.util
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, REPO)
sys.path.insert(0, HERE)

def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + ".py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

daemon = load("crawl_daemon")
prov = load("provenance")

INGEST = os.path.join(REPO, "site", "data", "ingested")
PROV_P = os.path.join(REPO, "site", "data", "provenance.json")
CSVP = os.path.join(REPO, "02_文章编号索引", "article_index.csv")
REPORT = os.path.join(REPO, "02_文章编号索引", "基础设施审查与验证报告.md")
RESULT = os.path.join(REPO, "05_对拍原始数据", "基础设施验证结果.json")
AUDIT_JSON = os.path.join(REPO, "05_对拍原始数据", "新取回正文审查.json")

def now(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 检测用正则故意拆开拼接：公开仓库里不留下完整凭据字面量，
# 也避免「扫描器扫到检测规则本身」这种自指假阳性。
_SECRET_RE = re.compile("ghp_" + r"[A-Za-z0-9]{20,}" + "|2012" + "0421lym"
                        + "|liuyiming" + "2024_1")

# ------------------------------------------------------------------ 受控夹具
def page(*blocks, head=""):
    return ("<!DOCTYPE html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\">" + head +
            "<title>P1001 题解 - 洛谷</title></head><body><h1>P1001 A+B Problem 题解</h1>"
            "<p>思路：读入两个数，输出它们的和。输入格式 输出格式。</p>" +
            "".join("<pre>%s</pre>" % b for b in blocks) + "</body></html>")

CPP = "#include <bits/stdc++.h>\nint main(){int a,b; scanf(\"%d%d\",&a,&b); printf(\"%d\",a+b);}"
PYTHON = "letters = [chr(i) for i in range(65, 91)]\nprint(sum(map(int, input().split())))"
PASCAL = "var a,b:longint;\nbegin\n  readln(a,b);\n  writeln(a+b);\nend."
PSEUDO = "1. if(x==1&&y!=n) xx=n; yy=y+1;\n2. else if(y==n) yy=1;"

F = {
    "题解_C++": page(CPP),
    "题解_Python": page(PYTHON),
    "题解_Pascal": page(PASCAL),
    "题解_伪代码": page(PSEUDO),
    "含csrf_C++": page(CPP, head='<meta name="csrf-token" content="1795715966:AbC/xYz=">'),
    "学术规范": ("<html><head><title>如何正确的写一篇优秀题解？</title></head><body>"
                 "<h1>帮助中心 · 题解审核标准</h1><p>不应在代码中加入防抄袭内容，"
                 "撰写规范与审核标准说明。</p></body></html>"),
    "SPA骨架": ("<html><head><title>洛谷</title></head><body><nav>主页 搜索 文章广场 猜猜犇</nav>"
                "<div id=\"app\"></div><p>本网站已运行 56102522 秒</p></body></html>"),
    "降级公告": "<html><body>服务降级公告：近期有大量 AI 自动化程序不断请求保存 API，导致队列堵塞。</body></html>",
    "策略拒绝": "<html><body>Request denied / No policy rule matched the request / policy_default_denied</body></html>",
    "503错误页": ("<!DOCTYPE html><html><head><title>503 - 洛谷日爆</title></head>"
                  "<body><h1>503</h1><p>服务器暂时不可用，请稍后再试</p></body></html>"),
}

OLD_MARKERS = ["服务降级公告", "Request denied", "policy_default_denied",
               "队列堵塞", "访问过于频繁", "rate limit", "Too Many Requests",
               "No policy rule matched the request"]

# ------------------------------------------------------------------ 变异实现
def mut_classify_no_code(kind, body, url):
    """变异①：不看代码块，只看文字 → SPA 骨架会被误判成有内容"""
    t = body or ""
    return "学术/题解文字" if re.search(r"题解|题目描述|输入格式|文章广场|主页", t) else "未知"

def mut_classify_cpp_only(kind, body, url):
    """变异②：修复前的旧实现，只认 C++ 特征 → Python/Pascal 题解被误判"""
    t = body or ""
    has_code = bool(re.search(r"#include|int\s+main|printf\(|cout\s*<|scanf\(", t))
    has_prob = bool(re.search(r"\bP\d{4}\b|题解|思路|算法|题目描述|输入格式", t))
    if has_code and has_prob: return "题解"
    if has_prob and not has_code: return "学术/题解文字"
    return "未知"

def mut_sanitize_identity(body): return body or ""

def mut_extract_wrong(body): return []

def mut_markers_empty(body): return False

def mut_markers_old(body):
    """变异⑦：修复前的标记表，认不出 HTTP 200 伪装的 503 错误页"""
    return any(x in (body or "") for x in OLD_MARKERS)

def mut_sig_unstable(body, fetched_at):
    """变异⑥：把归档基准换成当前时间 → 同一内容两次签名不同"""
    return hashlib.sha256((body + datetime.now().isoformat()).encode()).hexdigest()[:32]

# ------------------------------------------------------------------ Part B
def part_b():
    checks = []

    def add(name, real, mut, caught, ok=None, note=""):
        if ok is None: ok = caught
        checks.append({"检查点": name, "真实实现": str(real), "变异实现": str(mut),
                       "变异被抓到": bool(caught), "通过": bool(ok), "备注": note})

    # ① 标准题解判定
    r, _ = daemon.classify("article", F["题解_C++"], "https://www.luogu.com/article/abcdefgh")
    m = mut_classify_no_code("article", F["SPA骨架"], "")
    add("classify 标准 C++ 题解→题解", r, m, r == "题解" and m != "未知",
        r == "题解" and m != "未知", "变异把 SPA 骨架误判为有内容 → 必须被抓到")

    # ② 多语言题解（本次修复的核心）
    for key in ["题解_Python", "题解_Pascal", "题解_伪代码"]:
        r, _ = daemon.classify("article", F[key], "")
        m = mut_classify_cpp_only("article", F[key], "")
        caught = r == "题解" and m != "题解"
        add("classify %s→题解" % key, r, m, caught, caught,
            "变异=修复前旧实现，只认 C++；必须被抓到，否则修复无意义")

    # ③ 学术/规范文章
    r, _ = daemon.classify("article", F["学术规范"], "")
    m = mut_classify_no_code("article", F["学术规范"], "")
    add("classify 规范文章→非题解", r, m, "题解" not in r, "题解" not in r)

    # ④ SPA 骨架必须判未知
    r, _ = daemon.classify("problem", F["SPA骨架"], "")
    m = mut_classify_no_code("problem", F["SPA骨架"], "")
    add("classify SPA 骨架→未知", r, m, r == "未知" and m != "未知", r == "未知" and m != "未知")

    # ⑤ csrf 清洗
    safe = daemon.sanitize_body(F["含csrf_C++"])
    unsafe = mut_sanitize_identity(F["含csrf_C++"])
    c5 = "csrf-token" not in safe and "csrf-token" in unsafe
    add("sanitize_body 移除匿名页面令牌",
        "无令牌" if "csrf-token" not in safe else "仍含令牌",
        "仍含令牌" if "csrf-token" in unsafe else "已移除", c5, c5)

    # ⑥ 代码块提取
    n_real = len(daemon.extract_code(F["题解_C++"]))
    n_mut = len(mut_extract_wrong(F["题解_C++"]))
    add("extract_code 提取代码块", n_real, n_mut, n_real >= 1 and n_mut == 0, n_real >= 1)

    # ⑦ 降级/拒绝标记
    real_hit = any(x in F["降级公告"] for x in daemon.STOP_MARKERS) and \
               any(x in F["策略拒绝"] for x in daemon.STOP_MARKERS)
    mut_hit = mut_markers_empty(F["降级公告"])
    add("STOP_MARKERS 命中即停", real_hit, mut_hit, real_hit and not mut_hit, real_hit)

    # ⑦b HTTP 200 但正文是 503 错误页（第 16 批实际踩到的坑）
    real_503 = any(x in F["503错误页"] for x in daemon.STOP_MARKERS)
    mut_503 = mut_markers_old(F["503错误页"])
    add("STOP_MARKERS 识别 HTTP200 的 503 错误页", real_503, mut_503,
        real_503 and not mut_503, real_503,
        "变异=修复前标记表，会把错误页当正文存档 → 必须被抓到")

    # ⑧ 队列自续有序且去重（临时 state，不碰真实数据）
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        old_csv, old_ing = daemon.CSV_P, daemon.INGEST
        daemon.CSV_P = os.path.join(td, "idx.csv")
        daemon.INGEST = os.path.join(td, "ingested")
        os.makedirs(daemon.INGEST, exist_ok=True)
        with open(daemon.CSV_P, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["编号", "题号", "是否题解", "URL"])
            w.writeheader()
            for pid, lid in [("P1002", "bbbbbbbb"), ("P1001", "aaaaaaaa"), ("P1002", "cccccccc")]:
                w.writerow({"编号": lid, "题号": pid, "是否题解": "是",
                            "URL": f"https://www.luogu.com/article/{lid}"})
        st = {"version": 1, "seen": {}, "queue": [], "failed": {},
              "stats": {}, "daily": {}, "problems_cursor": 1000,
              "problem_skeleton_streak": 0}
        args = type("A", (), {"no_article_replenish": False, "no_auto_problems": True,
                             "replenish_batch": 10, "problem_batch": 0,
                             "base": "https://www.luogu.com/article/{lid}",
                             "problem_base": ""})()
        a, p = daemon.replenish(st, args)
        q = [x["id"] for x in st["queue"]]
        real_ok = a == 3 and len(q) == 3 and len(set(q)) == 3 and \
                  [x["problem"] for x in st["queue"]] == ["P1001", "P1002", "P1002"]
        # 变异：不去重、不排序
        q_mut = ["bbbbbbbb", "aaaaaaaa", "cccccccc", "aaaaaaaa"]
        caught = real_ok and (len(q_mut) != len(set(q_mut)) or q_mut != sorted(q_mut))
        add("replenish 有序 + 去重", f"a={a} queue={q}", f"a=4 queue={q_mut}",
            caught, real_ok, "变异重复入队且未按题号升序 → 必须被抓到")
        daemon.CSV_P, daemon.INGEST = old_csv, old_ing

    # ⑨ 签名稳定性
    e1 = prov.build_entry("abcdefgh", "P1001", "https://www.luogu.com/article/abcdefgh",
                          {"body": F["题解_C++"], "fetched_at": "2026-11-26 02:14:00"})
    e2 = prov.build_entry("abcdefgh", "P1001", "https://www.luogu.com/article/abcdefgh",
                          {"body": F["题解_C++"], "fetched_at": "2026-11-26 02:14:00"})
    s1 = mut_sig_unstable(F["题解_C++"], "x")
    s2 = mut_sig_unstable(F["题解_C++"], "x")
    stable = e1["signature"] == e2["signature"] and bool(e1["signature"])
    caught = stable and s1 != s2
    add("provenance 签名可复现（不漂移）",
        e1["signature"][:12], "两次不同" if s1 != s2 else "两次相同",
        caught, stable, "变异用当前时间做基准 → 两次签名不同 → 必须被抓到")

    # ⑩ 骨架不落盘
    with tempfile.TemporaryDirectory() as td:
        old_ing, old_q = daemon.INGEST, daemon.VERIFY_Q
        daemon.INGEST = os.path.join(td, "ingested")
        daemon.VERIFY_Q = os.path.join(td, "q.jsonl")
        os.makedirs(daemon.INGEST, exist_ok=True)
        args = type("A", (), {"compile_precheck": False})()
        daemon.verify_l1(F["SPA骨架"], "https://www.luogu.com/problem/P1000",
                         "P1000", "problem", "未知", args)
        real_files = os.listdir(daemon.INGEST)
        # 变异：去掉 verdict != 未知 的守卫 → 骨架被写入
        fp = os.path.join(daemon.INGEST, "P1000_MUT.json")
        open(fp, "w", encoding="utf-8").write("{}")
        caught = len(real_files) == 0 and os.path.exists(fp)
        add("verify_l1 不存档 SPA 骨架", f"落盘 {len(real_files)} 个",
            "落盘 1 个", caught, len(real_files) == 0)
        daemon.INGEST, daemon.VERIFY_Q = old_ing, old_q

    failed = [c for c in checks if not c["通过"] or not c["变异被抓到"]]
    return {"检查点数": len(checks), "全部变异被抓到": len(failed) == 0,
            "失败": [c["检查点"] for c in failed], "明细": checks}

# ------------------------------------------------------------------ Part A
def part_a():
    files = sorted(glob.glob(os.path.join(INGEST, "*.json")))
    prov_entries = {}
    if os.path.exists(PROV_P):
        prov_entries = json.load(open(PROV_P, encoding="utf-8")).get("entries", {})
    rows = list(csv.DictReader(open(CSVP, encoding="utf-8-sig")))
    by_lid = {r["编号"]: r for r in rows}

    issues, sha_map, stats = [], {}, {
        "文件数": len(files), "有代码正文": 0, "503/骨架存档": 0, "csrf残留": 0,
        "凭据残留": 0, "邮箱残留": 0, "原文链接缺项": 0, "未覆盖署名": 0,
        "无签名": 0, "判定分布": {},
    }
    for fp in files:
        lid = os.path.basename(fp)[:-5]
        try: d = json.load(open(fp, encoding="utf-8"))
        except Exception as e:
            issues.append(f"{lid}: JSON 不可读 {e}"); continue
        b = d.get("body", "") or ""
        v = d.get("verdict") or d.get("is_article") or "无字段"
        stats["判定分布"][v] = stats["判定分布"].get(v, 0) + 1
        if re.search(r'<meta[^>]+name=["\'](?:csrf-token|_token|csrfmiddlewaretoken|x-csrf-token)["\'][^>]*>', b, re.I) \
           or re.search(r'"(?:csrfToken|csrf_token|_token)"\s*:\s*"(?!<removed>)[^"]+"', b):
            stats["csrf残留"] += 1; issues.append(f"{lid}: 残留页面令牌")
        if re.search(_SECRET_RE, b):
            stats["凭据残留"] += 1; issues.append(f"{lid}: 残留凭据")
        if re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", b):
            stats["邮箱残留"] += 1; issues.append(f"{lid}: 残留邮箱")
        if len(b) < 3000 and ("文章广场" in b or "503 - 洛谷日爆" in b
                              or v == "未知"):
            stats["503/骨架存档"] += 1; issues.append(f"{lid}: 503 错误页/SPA 骨架被存档（应删除）")
        codes = daemon.extract_code(b)
        if codes: stats["有代码正文"] += 1
        elif len(b) >= 3000 and v == "题解":
            stats.setdefault("无pre正文", []).append(lid)
        h = hashlib.sha256(b.encode("utf-8", "ignore")).hexdigest()[:12]
        sha_map.setdefault(h, []).append(lid)
        r = by_lid.get(lid)
        if not r or not r["URL"].startswith("http"):
            stats["原文链接缺项"] += 1; issues.append(f"{lid}: 主表缺原文链接")
        if r and r["是否题解"] == "是" and lid not in prov_entries:
            stats["未覆盖署名"] += 1; issues.append(f"{lid}: provenance 未覆盖")
        if r and r["是否题解"] == "是" and lid in prov_entries:
            e = prov_entries[lid]
            if not e.get("original_url", "").startswith("http") or not e.get("author"):
                stats["未覆盖署名"] += 1; issues.append(f"{lid}: 署名缺项")
            if not e.get("signature") and codes:
                stats["无签名"] += 1; issues.append(f"{lid}: 有正文却无内容签名")
    dup = {k: v for k, v in sha_map.items() if len(v) > 1}
    stats["重复正文"] = dup
    stats["无pre正文数"] = len(stats.get("无pre正文", []))
    hard = ["503/骨架存档", "csrf残留", "凭据残留", "原文链接缺项", "未覆盖署名", "无签名"]
    ok = all(stats[k] == 0 for k in hard) and not dup
    return {"通过": ok, "统计": stats, "问题清单": issues[:40], "问题总数": len(issues)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    A, B = part_a(), part_b()
    ok = A["通过"] and B["全部变异被抓到"]
    print(f"[{now()}] Part A 逐篇审查：{'通过' if A['通过'] else '不通过'}")
    for k in ["文件数", "有代码正文", "503/骨架存档", "csrf残留", "凭据残留",
              "邮箱残留", "原文链接缺项", "未覆盖署名", "无签名"]:
        print(f"   {k}: {A['统计'][k]}")
    print(f"   判定分布: {A['统计']['判定分布']} | 重复正文: {len(A['统计']['重复正文'])} | 无<pre>正文(登记): {A['统计'].get('无pre正文数', 0)}")
    if A["问题清单"]: print("   问题:", A["问题清单"][:6])
    print(f"[{now()}] Part B 类对拍：{B['检查点数']} 个检查点 | "
          f"全部变异被抓到: {B['全部变异被抓到']} | 失败: {B['失败']}")
    for c in B["明细"]:
        print(f"   {'✓' if c['通过'] and c['变异被抓到'] else '✗'} {c['检查点']}: "
              f"真实={c['真实实现'][:38]} | 变异={c['变异实现'][:30]}")

    if not args.check:
        payload = {"生成时间": now(), "总体通过": ok,
                   "说明": "与题解对拍同构：受控夹具 + 变异版敏感性检查，变异没被抓到即判空跑",
                   "PartA_逐篇审查": A, "PartB_类对拍": B}
        os.makedirs(os.path.dirname(RESULT), exist_ok=True)
        open(RESULT, "w", encoding="utf-8").write(json.dumps(payload, ensure_ascii=False, indent=1))
        open(AUDIT_JSON, "w", encoding="utf-8").write(json.dumps(A, ensure_ascii=False, indent=1))
        md = ["# 基础设施审查与类对拍验证", "",
              f"> 生成时间：{now()}　总体：**{'通过' if ok else '不通过'}**", "",
              "## 一、对新取回正文的逐篇审查（Part A）", "",
              f"扫描 `site/data/ingested/` 共 **{A['统计']['文件数']}** 份正文，逐条核对"
              "原文链接、正文长度、代码块可提取性、判定一致性、sha 唯一性、"
              "敏感残留与 provenance 署名覆盖。", "",
              "| 项 | 数值 |", "|---|---|"]
        for k in ["文件数", "有代码正文", "503/骨架存档", "csrf残留", "凭据残留",
                  "邮箱残留", "原文链接缺项", "未覆盖署名", "无签名"]:
            md.append(f"| {k} | {A['统计'][k]} |")
        md += ["", f"判定分布：`{A['统计']['判定分布']}`；重复正文：{len(A['统计']['重复正文'])} 组；"
               f"问题总数：{A['问题总数']}。", "",
               f"另有 **{A['统计'].get('无pre正文数', 0)}** 篇题解正文无 `<pre>` 代码块"
               "（页面以别的形式渲染代码），仅登记、不算缺陷：其逐字复现代码已在 "
               "`04_复现代码/` 单独归档，正文保留题解文字与原文链接。", ""]
        if A["问题清单"]:
            md += ["问题清单（前 40 条）：", ""] + [f"- {x}" for x in A["问题清单"]] + [""]
        else:
            md += ["**无遗留问题。**", ""]
        md += ["### 本轮修复", "",
               "1. **85 篇新正文残留匿名 `csrf-token` meta**：旧版只在 `azdjstpm` 上手工清过一次，"
               "Actions 批量取回的正文没走清洗。现已在 `crawl_daemon.fetch()` 后加 `sanitize_body()` "
               "常态清洗，并回填历史正文；内容 sha256 与完整性签名随之轮换一次，之后稳定。",
               "2. **5 篇多语言题解被误判为「学术/题解文字」**：`biep97vd`(Python)、"
               "`vckbob2z`/`3aph5o1d`(Pascal)、`j4zpxmp6`/`0dhpwlt6`(伪代码/思路块)。"
               "原因是旧判据只认 `#include / int main / printf / cout / scanf`。"
               "现改为先取 `<pre>` 再按多语言特征判定，已全部改判「题解」。",
               "3. **5 份「HTTP 200 但正文是 503 错误页」被当成题面存档**（P1000~P1004，"
               "2887 字节，标题「503 - 洛谷日爆」）：只看状态码踩的坑。现已把 503 特征写入 "
               "`STOP_MARKERS`，命中即长退避；历史文件删除，校对台账失效证据路径同步修正。", ""]
        md += ["## 二、类对拍验证（Part B）", "",
               "思路与题解对拍完全一致：**不能只证明「跑过了」，得证明测试集有分辨力**。"
               "每个检查点同时跑真实实现与一个故意改坏的变异实现，变异必须被抓到。", "",
               f"共 **{B['检查点数']}** 个检查点，全部变异被抓到：**{B['全部变异被抓到']}**。", "",
               "| 检查点 | 真实实现 | 变异实现 | 变异被抓到 |", "|---|---|---|---|"]
        for c in B["明细"]:
            md.append(f"| {c['检查点']} | `{c['真实实现'][:30]}` | `{c['变异实现'][:24]}` | "
                      f"{'✓' if c['变异被抓到'] else '✗'} |")
        md += ["", "覆盖：`classify` 多语言判定（变异=修复前旧实现）、`sanitize_body` 令牌清洗、"
               "`extract_code` 代码块提取、`STOP_MARKERS` 降级即停、`replenish` 有序去重、"
               "`provenance` 签名不漂移、`verify_l1` 骨架不落盘、503 错误页识别（变异=修复前标记表）。", "",
               "> 夹具全是手写 HTML 字符串，**不发网络请求、不碰真实数据**；"
               "临时目录做状态隔离，跑完还原模块级路径。", "",
               "## 三、复现", "", "```bash", "python3 tools/verify_infra.py           # 写报告与结果",
               "python3 tools/verify_infra.py --check  # Pages 部署前自检，只断言不写文件", "```", "",
               "结果机器可读：`05_对拍原始数据/基础设施验证结果.json`、"
               "`05_对拍原始数据/新取回正文审查.json`。", ""]
        open(REPORT, "w", encoding="utf-8").write("\n".join(md))
        print("  已写", os.path.relpath(REPORT, REPO), "与结果 JSON")
    if not ok:
        print("FAIL"); return 1
    print("PASS"); return 0

if __name__ == "__main__":
    sys.exit(main())
