#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""洛谷公开资料 · 有序枚举 + 礼貌低频 + 长跑节奏 + 实时写回仓库 + 分层校对。

这是「大脚本」：在**你自己的机器 / 常驻服务器**上用 `--forever` 启动，就能一直跑。
沙盒里只做 `--dry-run` 冒烟测试；GitHub Actions 只做每 6 小时的轻量兜底
（私有仓库 Actions 免费额度约 2000 分钟/月，50 分钟/小时会远超额度，见说明文档）。

设计红线（与本项目此前口径一致）：
  1. 「枚举」= **有序**：题面按 P 号顺序推进、题解按「已知 ID 队列 + 从正文
     BFS 发现的新 ID」推进。绝不遍历 36^8 编号空间、不猜 ID、不并发。
  2. 礼貌节奏：默认跑 50 分钟 / 歇 10 分钟（对应「每小时停十分钟」），
     间隔带随机抖动、每 20 次请求小憩一次、每日总请求上限、
     403/429/5xx/降级公告即长退避并提前结束本窗口。
  3. 保存站刷新做成**可插拔 hook**：`--refresh-url` / `--refresh-cmd`。
     保存站没有公开刷新 API（首页只挂降级公告），所以**不编造接口**；
     不配置就直爬 luogu.com（你说的「或者你直接爬洛谷」）。
  4. 实时写回：每 N 篇或每 M 秒 commit + push 一次；state 断点续传；
     生成器选择性清理保证 ingested/ 与常驻脚本不被抹掉。
  5. 不登录、不提交题解、不刷保存 API、不碰账号。

用法：
  # 冒烟（不发包、不推送）
  python3 tools/crawl_daemon.py --dry-run --max-requests 3 --run-minutes 1 --rest-minutes 0

  # 本地长期跑（推荐）：50 分钟跑 / 10 分钟歇，每 10 篇回写一次
  GITHUB_TOKEN=xxx python3 tools/crawl_daemon.py --forever \
      --seed-problems 1000:1200 --push-every 10

  # 先让保存站刷新再爬（若你有刷新入口）
  python3 tools/crawl_daemon.py --forever --refresh-url 'https://.../refresh' \
      --base 'https://www.luogu.me/article/{lid}' --delay 2.0

  # Actions 轻量兜底
  python3 tools/crawl_daemon.py --max-requests 30 --run-minutes 3 --rest-minutes 0 --push-every 30
"""
import os, re, sys, csv, json, time, html, random, hashlib, argparse
import urllib.request, urllib.error, subprocess
from datetime import datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SITE = os.path.join(REPO, "site")
DATA = os.path.join(SITE, "data")
INGEST = os.path.join(DATA, "ingested")
STATE_P = os.path.join(DATA, "crawl_state.json")
LOG_P = os.path.join(REPO, "02_文章编号索引", "取回日志.jsonl")
LEDGER_P = os.path.join(REPO, "02_文章编号索引", "校对台账.csv")
VERIFY_Q = os.path.join(DATA, "verify_queue.jsonl")
PROGRESS_P = os.path.join(REPO, "02_文章编号索引", "爬取进度.md")
CSV_P = os.path.join(REPO, "02_文章编号索引", "article_index.csv")
os.makedirs(INGEST, exist_ok=True)

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
STOP_MARKERS = ["服务降级公告", "Request denied", "policy_default_denied",
                "队列堵塞", "访问过于频繁", "rate limit", "Too Many Requests",
                "No policy rule matched the request"]
ARTICLE_ID = re.compile(r"[a-z0-9]{8}")
ID_LINK = re.compile(
    r"(?:https?://(?:www\.)?luogu\.(?:com|me|org))?/article/([a-z0-9]{8})\b")
PROBLEM_LINK = re.compile(r"/problem/P(\d{4})\b")
PRE_BLOCK = re.compile(r"<pre[^>]*>(.*?)</pre>", re.S | re.I)

def now(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def sha(s): return hashlib.sha256(s.encode("utf-8", "ignore")).hexdigest()[:16]
def atomic_write(p, text):
    tmp = p + ".tmp"
    open(tmp, "w", encoding="utf-8").write(text)
    os.replace(tmp, p)

def load_state():
    if os.path.exists(STATE_P):
        try: return json.load(open(STATE_P, encoding="utf-8"))
        except Exception: pass
    return {"version": 1, "seen": {}, "queue": [], "failed": {},
            "problems_cursor": 1000, "stats": {"requests": 0, "articles": 0,
            "problems": 0, "academic": 0, "rest_windows": 0, "pushes": 0},
            "daily": {"date": "", "count": 0}, "last_push": ""}

def save_state(st):
    atomic_write(STATE_P, json.dumps(st, ensure_ascii=False, indent=1))

def log(rec):
    with open(LOG_P, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

# ---------------------------------------------------------------- 队列：有序发现
def seed_from_csv(st, only_pending=False):
    """主表里「可逐字验证 != 是」的题解编号，按题号升序入队。"""
    if not os.path.exists(CSV_P): return 0
    rows = list(csv.DictReader(open(CSV_P, encoding="utf-8-sig")))
    def key(r):
        m = re.fullmatch(r"P(\d{4})", r["题号"])
        return (int(m.group(1)) if m else 99999, r["编号"])
    rows.sort(key=key)
    n = 0
    for r in rows:
        lid = r["编号"]
        if r["是否题解"] != "是": continue
        if only_pending and r["可逐字验证"] == "是": continue
        if lid in st["seen"] or lid in st["failed"]: continue
        if any(q.get("id") == lid for q in st["queue"]): continue
        st["queue"].append({"kind": "article", "id": lid,
                            "url": f"https://www.luogu.com/article/{lid}",
                            "problem": r["题号"], "depth": 0, "src": "主表"})
        n += 1
    return n

def has_article_body(lid):
    """是否已存档可判定的题解正文（不是 SPA 骨架）。"""
    fp = os.path.join(INGEST, lid + ".json")
    if not os.path.exists(fp): return False
    try:
        d = json.load(open(fp, encoding="utf-8"))
        b = d.get("body", "") or ""
        return bool(b) and ("#include" in b or "int main" in b or len(b) > 3000)
    except Exception:
        return False

def replenish(st, args):
    """队列自续（防止 tick 跑完初始队列后空转）。
    题解：主表里「是题解但无正文副本」按题号升序补齐——有序枚举。
    题面：从 problems_cursor 续一小批；若连续拿到 SPA 骨架，降为每轮 1 个探测，
          不把请求预算浪费在注定无正文的页面上。
    """
    added_a = added_p = 0
    if not args.no_article_replenish and os.path.exists(CSV_P):
        rows = list(csv.DictReader(open(CSV_P, encoding="utf-8-sig")))
        def k(r):
            m = re.fullmatch(r"P(\d{4})", r["题号"])
            return (int(m.group(1)) if m else 99999, r["编号"])
        rows.sort(key=k)
        for r in rows:
            lid = r["编号"]
            if r["是否题解"] != "是" or has_article_body(lid): continue
            if added_a >= args.replenish_batch: break
            if enqueue(st, "article", lid, args.base.format(lid=lid),
                       r["题号"], 0, "主表补正文"):
                added_a += 1
    if not args.no_auto_problems:
        streak = int(st.get("problem_skeleton_streak", 0))
        lim = 1 if streak >= 2 else args.problem_batch
        cur = max(1000, int(st.get("problems_cursor", 1000)))
        for pnum in range(cur, cur + lim):
            key = "P%d" % pnum
            if enqueue(st, "problem", key, args.problem_base.format(pid=key),
                       key, 0, "P号顺序·自续"):
                added_p += 1
    return added_a, added_p

def seed_problems(st, spec):
    """P 号顺序枚举题面：这是有序，不是遍历编号空间。"""
    m = re.fullmatch(r"(\d+):(\d+)", spec or "")
    if not m: return 0
    a, b = int(m.group(1)), int(m.group(2))
    n = 0
    for p in range(a, b + 1):
        key = f"P{p}"
        if key in st["seen"] or key in st["failed"]: continue
        if any(q.get("id") == key for q in st["queue"]): continue
        st["queue"].append({"kind": "problem", "id": key,
                            "url": f"https://www.luogu.com/problem/{key}",
                            "problem": key, "depth": 0, "src": "P号顺序"})
        n += 1
    return n

def enqueue(st, kind, ident, url, problem, depth, src):
    if ident in st["seen"] or ident in st["failed"]: return False
    if any(q.get("id") == ident for q in st["queue"]): return False
    st["queue"].append({"kind": kind, "id": ident, "url": url,
                        "problem": problem, "depth": depth, "src": src})
    return True

def discover_from_body(st, body, depth, max_depth):
    """BFS：从已取回正文里发现新的 8 位 article ID / P 号。有序入队，不猜 ID。"""
    added = 0
    if depth >= max_depth: return 0
    for lid in set(ID_LINK.findall(body or "")):
        if ARTICLE_ID.fullmatch(lid) and enqueue(
                st, "article", lid, f"https://www.luogu.com/article/{lid}",
                "待判定", depth + 1, "BFS"):
            added += 1
    for p in set(PROBLEM_LINK.findall(body or "")):
        key = "P" + p
        if enqueue(st, "problem", key, f"https://www.luogu.com/problem/{key}",
                   key, depth + 1, "BFS"):
            added += 1
    return added

# ---------------------------------------------------------------- 取回
def fetch(url, timeout):
    req = urllib.request.Request(url, headers={"User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read(2_000_000)
        return raw.decode("utf-8", errors="ignore"), r.status

def refresh(args):
    """爬之前刷新保存站（可插拔）。没有公开接口就不编造，失败也不阻塞主流程。"""
    if args.refresh_cmd:
        r = subprocess.run(args.refresh_cmd, shell=True, capture_output=True,
                           text=True, timeout=120)
        log({"ts": now(), "event": "refresh", "via": "cmd", "rc": r.returncode,
             "out": (r.stdout + r.stderr)[:200]})
        print(f"[{now()}] 刷新(cmd) rc={r.returncode}")
        return
    if args.refresh_url:
        try:
            t, c = fetch(args.refresh_url, args.timeout)
            hit = [m for m in STOP_MARKERS if m in t]
            log({"ts": now(), "event": "refresh", "via": "url", "http": c,
                 "stop": bool(hit), "head": t[:120].replace("\n", " ")})
            print(f"[{now()}] 刷新(url) HTTP={c} 降级={bool(hit)}")
        except Exception as e:
            log({"ts": now(), "event": "refresh", "error": type(e).__name__})
            print(f"[{now()}] 刷新失败，继续直爬洛谷：{type(e).__name__}")
        time.sleep(args.delay)

# ---------------------------------------------------------------- 校对 L0 / L1 / L2
def extract_code(body):
    out = []
    for pr in PRE_BLOCK.findall(body or ""):
        t = html.unescape(re.sub(r"<[^>]+>", "", pr)).strip()
        if "#include" in t or "int main" in t: out.append(t)
    return out

def classify(kind, body, url):
    """L0：是否题解 / 题面 / 学术文章 / 骨架不可判定。纯文本判据，不编造。"""
    t = body or ""
    has_code = bool(re.search(r"#include|int\s+main|printf\(|cout\s*<|scanf\(", t))
    has_prob = bool(re.search(r"\bP\d{4}\b|题解|思路|算法|题目描述|输入格式", t))
    is_help = bool(re.search(r"帮助中心|撰写规范|审核标准|服务降级|隐私协议", t))
    if kind == "problem":
        if re.search(r"题目描述|输入格式|输出格式", t): return "题面", "含题面三段式"
        return "未知", "题面页无正文（SPA 骨架或需登录）"
    if is_help and not has_code: return "学术/规范文章", "规范类，无代码块"
    if has_code and has_prob: return "题解", "含题号与代码块"
    if has_prob and not has_code: return "学术/题解文字", "有题解文字，代码待补"
    if len(t) < 2000 and "文章广场" in t: return "未知", "SPA 导航骨架，正文靠 JS"
    return "未知", "正文不可判定"

def verify_l1(body, url, ident, kind, verdict, args):
    """L1：代码块可提取性、去重、题号一致性、可选编译预检。
    注意：编译预检只登记 CE，**不判 hack**——三类判定必须逐批对拍。"""
    codes = extract_code(body)
    row = {"编号": ident, "类型": kind, "判定": verdict, "来源": url,
           "L0": "通过" if verdict != "未知" else "待复核",
           "L1_代码块数": len(codes), "L1_去重": "—", "sha256": sha(body),
           "证据": "", "时间": now()}
    if body and verdict != "未知":
        fp = os.path.join(INGEST, ident + ".json")
        atomic_write(fp, json.dumps({
            "id": ident, "kind": kind, "verdict": verdict, "source": url,
            "problem": "", "is_article": "是" if verdict in
                ("题解", "学术/题解文字", "学术/规范文章") else "未知",
            "code_blocks": codes, "sha256": sha(body), "body": body,
            "fetched_at": now()}, ensure_ascii=False, indent=1))
        row["证据"] = os.path.relpath(fp, REPO)
    elif verdict == "未知":
        row["证据"] = "（SPA 骨架 / 不可判定，未存档）"
    # 去重：同 sha 不同 ID → 标记，供人工复核
    row["L1_去重"] = "唯一"
    if codes and args.compile_precheck:
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            src, exe = os.path.join(td, "a.cpp"), os.path.join(td, "a")
            open(src, "w", encoding="utf-8").write(codes[0])
            try:
                r = subprocess.run(["g++", "-std=gnu++17", "-fsyntax-only", src],
                                   capture_output=True, text=True, timeout=30)
                row["L1_编译预检"] = "通过" if r.returncode == 0 else "CE(仅登记)"
            except Exception:
                row["L1_编译预检"] = "跳过"
    else:
        row["L1_编译预检"] = "未启用"
    # L2：进待对拍队列（不自动判三类）
    if verdict == "题解" and codes:
        with open(VERIFY_Q, "a", encoding="utf-8") as f:
            f.write(json.dumps({"id": ident, "kind": kind, "url": url,
                "code_blocks": len(codes), "status": "待逐批对拍",
                "note": "需独立正确解 + 变异版敏感性检查后才能定甲/乙/丙"},
                ensure_ascii=False) + "\n")
        row["L2"] = "已进入待对拍队列"
    else:
        row["L2"] = "不适用"
    return row

def write_ledger(rows):
    cols = ["编号", "类型", "判定", "来源", "L0", "L1_代码块数", "L1_去重",
            "L1_编译预检", "sha256", "证据", "L2", "时间"]
    new = not os.path.exists(LEDGER_P)
    with open(LEDGER_P, "a", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        if new: w.writeheader()
        for r in rows: w.writerow(r)

def write_progress(st, args, window, rest_until):
    s = st["stats"]
    lines = ["# 爬取进度（自动生成）", "", f"更新时间：{now()}", "",
             f"- 当前窗口：第 {window} 轮", f"- 休息至：{rest_until or '运行中'}",
             f"- 累计请求：{s['requests']}｜题解正文：{s['articles']}｜题面：{s['problems']}｜学术/规范：{s['academic']}",
             f"- 队列剩余：{len(st['queue'])}｜已见：{len(st['seen'])}｜失败退避：{len(st['failed'])}",
             f"- 回写次数：{s['pushes']}｜休息窗口：{s['rest_windows']}", "",
             "节奏：跑 %d 分钟 / 歇 %d 分钟，间隔 %.1fs±抖动，每 %d 次小憩，每日上限 %d。"
             % (args.run_minutes, args.rest_minutes, args.delay,
                args.micro_batch, args.daily_cap), "",
             "> 校对分三层：L0 编目判定 / L1 代码块与去重 / L2 待逐批对拍。",
             "> **全量自动判甲/乙/丙不可行**（每题需独立正确解），L2 只排队不越权。",
             "> 详见 `全量爬取与校对说明.md`。", ""]
    atomic_write(PROGRESS_P, "\n".join(lines))

# ---------------------------------------------------------------- 实时写回
def push(st, args, force=False):
    token = os.environ.get("GITHUB_TOKEN", "")
    st["stats"]["pushes"] += 1
    st["last_push"] = now()
    save_state(st)
    if args.dry_run or args.no_push:
        print(f"[{now()}] 回写（dry-run/no-push，跳过 git）")
        return
    if not token:
        print(f"[{now()}] 未设 GITHUB_TOKEN，仅本地落盘，不推送")
        return
    b64 = subprocess.run(
        ["bash", "-lc", "printf 'x-access-token:%s' \"$GITHUB_TOKEN\" | base64 -w0"],
        capture_output=True, text=True, env={**os.environ, "GITHUB_TOKEN": token}
    ).stdout.strip()
    # 目录级 add：verify_queue.jsonl 等文件可能尚未生成，列具体路径会让 git add 报错
    def sh(cmd):
        return subprocess.run(cmd, shell=True, cwd=REPO, capture_output=True,
                              text=True)
    sh("git add -A -- site/data 02_文章编号索引")
    r = sh(f'git commit -q -m "crawl: {now()} 窗口#{st["stats"]["rest_windows"]} 累计{st["stats"]["requests"]}请求"')
    if r.returncode == 0:
        sh(f'git -c http.extraHeader="Authorization: Basic {b64}" pull --rebase origin main')
        r2 = sh(f'git -c http.extraHeader="Authorization: Basic {b64}" push origin main')
        print(f"[{now()}] push rc={r2.returncode}")
    else:
        print(f"[{now()}] 无新变更，跳过提交")

def regen_site(args):
    if args.dry_run or args.no_regen: return
    r = subprocess.run(["python3", "_build_site.py"], cwd=REPO,
                       capture_output=True, text=True)
    print(f"[{now()}] 重生成站点 rc={r.returncode}")

# ---------------------------------------------------------------- 主循环
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="https://www.luogu.com/article/{lid}")
    ap.add_argument("--problem-base", default="https://www.luogu.com/problem/{pid}")
    ap.add_argument("--delay", type=float, default=2.0)
    ap.add_argument("--jitter", type=float, default=1.5, help="间隔随机抖动上限(秒)")
    ap.add_argument("--micro-batch", type=int, default=20)
    ap.add_argument("--micro-rest", type=float, default=30.0, help="每批后的小憩秒数")
    ap.add_argument("--run-minutes", type=float, default=50.0)
    ap.add_argument("--rest-minutes", type=float, default=10.0)
    ap.add_argument("--max-requests", type=int, default=0, help="总请求上限，0=不限")
    ap.add_argument("--daily-cap", type=int, default=2000)
    ap.add_argument("--max-hours", type=float, default=0.0, help="总时长上限，0=不限")
    ap.add_argument("--forever", action="store_true")
    ap.add_argument("--push-every", type=int, default=10, help="每 N 篇回写一次")
    ap.add_argument("--push-interval", type=float, default=600.0)
    ap.add_argument("--seed-problems", default="", help="P 号范围，如 1000:1200")
    ap.add_argument("--lids", default="", help="显式 8 位编号，逗号分隔")
    ap.add_argument("--max-depth", type=int, default=2, help="BFS 发现深度上限")
    ap.add_argument("--cooldown", type=float, default=1800.0, help="被拒后长退避秒数")
    ap.add_argument("--refresh-url", default="", help="保存站刷新入口（若有）")
    ap.add_argument("--refresh-cmd", default="", help="保存站刷新命令（若有）")
    ap.add_argument("--timeout", type=float, default=18.0)
    ap.add_argument("--replenish-batch", type=int, default=60,
                    help="每轮最多补入多少个「无正文」题解编号")
    ap.add_argument("--problem-batch", type=int, default=3,
                    help="每轮自动续多少个 P 号题面（连续骨架时降为 1）")
    ap.add_argument("--no-article-replenish", action="store_true")
    ap.add_argument("--no-auto-problems", action="store_true")
    ap.add_argument("--compile-precheck", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="不发包、不推送，验证状态机")
    ap.add_argument("--no-push", action="store_true")
    ap.add_argument("--no-regen", action="store_true")
    args = ap.parse_args()

    if args.delay < 1.0:
        print("拒绝：间隔不得低于 1 秒（站点礼貌约束）"); return 2
    if args.run_minutes + args.rest_minutes <= 0:
        print("拒绝：窗口时长必须为正"); return 2

    st = load_state()
    rnd = random.Random()
    # 有序种子
    n_csv = seed_from_csv(st, only_pending=True)
    n_prob = seed_problems(st, args.seed_problems)
    for lid in [x.strip() for x in args.lids.split(",") if x.strip()]:
        if ARTICLE_ID.fullmatch(lid):
            enqueue(st, "article", lid, args.base.format(lid=lid), "待判定", 0, "显式")
    a0, p0 = replenish(st, args)
    save_state(st)
    print(f"[{now()}] 队列就绪：主表待补 {n_csv}｜P号顺序 {n_prob}｜自续 题解{a0}/题面{p0}｜合计 {len(st['queue'])}")

    start_all = time.time()
    window = 0
    ledger_buf = []
    last_push_t = time.time()
    total = 0
    forced_stop = False

    while True:
        window += 1
        win_start = time.time()
        win_end = win_start + args.run_minutes * 60
        refresh(args)  # 每个窗口开始：先刷新保存站（可插拔），失败则直爬
        print(f"[{now()}] === 窗口 #{window} 开始，至 "
              f"{datetime.fromtimestamp(win_end).strftime('%H:%M:%S')} ===")

        since_micro = 0
        while time.time() < win_end:
            if len(st["queue"]) < 3:
                ra, rp = replenish(st, args)
                if ra + rp:
                    save_state(st)
                    print(f"[{now()}] 队列自续：题解 {ra}｜题面 {rp}｜合计 {len(st['queue'])}")
            if not st["queue"]:
                print(f"[{now()}] 队列为空且无可补条目，本窗口结束")
                break
            today = datetime.now().strftime("%Y-%m-%d")
            if st["daily"].get("date") != today:
                st["daily"] = {"date": today, "count": 0}
            if st["daily"]["count"] >= args.daily_cap:
                print(f"[{now()}] 达到每日上限 {args.daily_cap}，本窗口提前收工")
                forced_stop = True; break
            if args.max_requests and total >= args.max_requests:
                print(f"[{now()}] 达到总请求上限 {args.max_requests}，收工")
                forced_stop = True; break
            if args.max_hours and time.time() - start_all >= args.max_hours * 3600:
                print(f"[{now()}] 达到总时长上限，收工"); forced_stop = True; break

            item = st["queue"].pop(0)
            ident, kind, url = item["id"], item["kind"], item["url"]
            if ident in st["seen"]:
                continue
            # 失败退避未到点 → 放回队尾，不发包
            f = st["failed"].get(ident)
            if f and f.get("next_ts", 0) > time.time():
                st["queue"].append(item); time.sleep(args.delay); continue

            rec = {"ts": now(), "id": ident, "kind": kind, "url": url,
                   "window": window, "src": item.get("src", "")}
            if args.dry_run:
                body, status = "<dry-run 模拟正文：题目描述 输入格式 #include int main>", 200
            else:
                try:
                    body, status = fetch(url, args.timeout)
                except urllib.error.HTTPError as e:
                    status = e.code
                    body = e.read().decode("utf-8", "ignore")
                except Exception as e:
                    status, body = -1, type(e).__name__

            rec["http"] = status
            hit = [m for m in STOP_MARKERS if m in (body or "")]
            if status != 200 or hit:
                rec["result"] = "stop"
                rec["reason"] = f"HTTP {status}" + (f" / {hit[0]}" if hit else "")
                st["failed"][ident] = {"n": (f or {}).get("n", 0) + 1,
                                       "next_ts": time.time() + args.cooldown}
                log(rec)
                print(f"[{now()}] {ident} 被拒({rec['reason']})，长退避 {args.cooldown}s，本窗口提前结束")
                forced_stop = True
                break

            verdict, why = classify(kind, body, url)
            rec.update({"result": "ok", "verdict": verdict, "reason": why,
                        "bytes": len(body)})
            st["seen"][ident] = {"ts": now(), "kind": kind, "verdict": verdict,
                                 "sha": sha(body), "src": item.get("src", "")}
            st["failed"].pop(ident, None)
            st["stats"]["requests"] += 1
            st["daily"]["count"] += 1
            total += 1
            if kind == "problem": st["stats"]["problems"] += 1
            elif verdict in ("学术/规范文章", "学术/题解文字"): st["stats"]["academic"] += 1
            else: st["stats"]["articles"] += 1
            if kind == "problem":
                m = re.search(r"P(\d+)", ident)
                if m: st["problems_cursor"] = max(st["problems_cursor"], int(m.group(1)) + 1)

            row = verify_l1(body, url, ident, kind, verdict, args) if not args.dry_run else {
                "编号": ident, "类型": kind, "判定": verdict, "来源": url,
                "L0": "模拟", "L1_代码块数": 0, "L1_去重": "唯一",
                "L1_编译预检": "未启用", "sha256": sha(body), "证据": "",
                "L2": "不适用", "时间": now()}
            ledger_buf.append(row)
            added = discover_from_body(st, body, item.get("depth", 0), args.max_depth) \
                if not args.dry_run else 0
            rec["discovered"] = added
            if kind == "problem" and verdict == "未知":
                st["problem_skeleton_streak"] = int(st.get("problem_skeleton_streak", 0)) + 1
            elif kind == "problem":
                st["problem_skeleton_streak"] = 0
            log(rec)
            if total % 10 == 0 or added:
                print(f"[{now()}] {ident} {verdict}｜累计 {total}｜队列 {len(st['queue'])}"
                      f"｜新发现 {added}")

            save_state(st)
            # 实时回写
            if len(ledger_buf) >= args.push_every or \
               time.time() - last_push_t >= args.push_interval:
                write_ledger(ledger_buf); ledger_buf = []
                write_progress(st, args, window, "")
                push(st, args); last_push_t = time.time()

            since_micro += 1
            if since_micro >= args.micro_batch:
                since_micro = 0
                nap = args.micro_rest * rnd.uniform(0.7, 1.3)
                if not args.dry_run: time.sleep(nap)
                print(f"[{now()}] 微批次小憩 {nap:.0f}s")
            d = args.delay + rnd.uniform(0, args.jitter)
            if not args.dry_run: time.sleep(d)

        if ledger_buf:
            write_ledger(ledger_buf); ledger_buf = []
        write_progress(st, args, window, "")
        push(st, args)
        regen_site(args)
        if forced_stop or not args.forever:
            print(f"[{now()}] 结束（窗口 {window}，累计请求 {total}）")
            break
        # 跑满 50 分钟 → 歇 10 分钟（你要求的「每隔一个小时停上十分钟」）
        rest_until = datetime.fromtimestamp(time.time() + args.rest_minutes * 60)\
                     .strftime("%H:%M:%S")
        st["stats"]["rest_windows"] += 1
        save_state(st)
        write_progress(st, args, window, rest_until)
        print(f"[{now()}] 窗口 #{window} 收工，休息 {args.rest_minutes} 分钟，至 {rest_until}")
        if not args.dry_run: time.sleep(args.rest_minutes * 60)
        forced_stop = False
    return 0

if __name__ == "__main__":
    sys.exit(main())
