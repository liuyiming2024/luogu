#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""低频有序取回器 —— 按 2 秒一次（可配置）把文章编号逐篇取回并登记。

设计前提（务必先读）：
  1. 「枚举」= 对**已登记/明确给出**的 8 位编号按题号升序有序取回，
     **绝不遍历 36^8 编号空间、绝不并发、绝不猜测 ID**。
  2. 默认间隔 2.0 秒/次；失败指数退避；遇到「服务降级公告」「Request denied」
     或连续 403/429 立即停止本轮，不重试轰炸。
  3. 当前沙盒出口对 luogu.me 全路径返回 403 policy_default_denied，
     且保存站文章页为 SPA 骨架（正文靠 JS 调保存 API）。本脚本需在
     **能正常访问目标站点的网络**里运行；保存站首页自己挂着
     「近期有大量 AI 自动化程序不断请求保存 API，导致队列堵塞」的降级公告，
     所以即使能用也请保持低频、不要用保存 API 做批量拉取。
  4. 取回结果只写 site/data/ingested/<lid>.json 与取回日志，
     **不自动修改 article_index.csv**；判定「是否题解」后由人工/生成器合并。

用法：
  # 预览这一轮要取哪些（不发包）
  python3 site/lowfreq_fetch.py --dry-run --limit 10

  # 用保存站作源，2 秒一次，最多 10 篇
  python3 site/lowfreq_fetch.py --base https://www.luogu.me/article/{lid} --delay 2.0 --limit 10

  # 用可直读的 luogu.com 作源
  python3 site/lowfreq_fetch.py --base https://www.luogu.com/article/{lid} --delay 2.0 --limit 10

  # 只处理指定编号（有序补录单篇）
  python3 site/lowfreq_fetch.py --lids g8gclrnk,88laurj5 --delay 2.0

之后：python3 _build_site.py 重生成离线站（生成器会合并 ingested 正文）。
"""
import os, sys, json, csv, re, time, argparse, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CSV = os.path.join(REPO, "02_文章编号索引", "article_index.csv")
OUT = os.path.join(HERE, "data", "ingested")
LOG = os.path.join(REPO, "02_文章编号索引", "取回日志.jsonl")
POOL = os.path.join(REPO, "02_文章编号索引", "编号池_待取回.csv")

STOP_MARKERS = ["服务降级公告", "Request denied", "policy_default_denied",
                "队列堵塞", "访问过于频繁", "rate limit", "Too Many Requests"]

def load_queue(args):
    """有序编号队列：默认取主表里『可逐字验证=否/待确认』的条目；也可显式给编号。"""
    if args.lids:
        lids = [x.strip() for x in args.lids.split(",") if x.strip()]
        return [(x, "显式指定") for x in lids]
    rows = list(csv.DictReader(open(CSV, encoding="utf-8-sig")))
    def key(r):
        m = re.fullmatch(r"P(\d{4})", r["题号"])
        return (int(m.group(1)) if m else 99999, r["编号"])
    rows.sort(key=key)
    q = []
    for r in rows:
        if r["是否题解"] != "是":
            continue
        if r["可逐字验证"] in ("是",):     # 已逐字验证过的跳过
            continue
        if os.path.exists(os.path.join(OUT, r["编号"] + ".json")):
            continue
        q.append((r["编号"], r["题号"]))
    return q

def looks_like_article(text, lid):
    """粗判「是否题解」：出现题号/思路/代码块特征；非题解（规范/公告）返回 否。"""
    t = text or ""
    has_code = bool(re.search(r"#include|int\s+main|printf\(|cout\s*<|scanf\(", t))
    has_prob = bool(re.search(r"\bP\d{4}\b|题解|思路|算法|题目描述", t))
    is_help = bool(re.search(r"帮助中心|撰写规范|审核标准|服务降级|隐私协议", t))
    if is_help and not has_code:
        return "否", "帮助/规范类页面"
    if has_code and has_prob:
        return "是", "含题号与代码块"
    if has_prob:
        return "是", "含题解文字，代码待补"
    return "未知", "正文不可判定（SPA 骨架或错误页）"

def fetch(url, ua, timeout):
    req = urllib.request.Request(url, headers={"User-Agent": ua,
                                               "Accept": "text/html,application/xhtml+xml"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read(2_000_000)
        return raw.decode("utf-8", errors="ignore"), r.status

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="https://www.luogu.com/article/{lid}",
                    help="URL 模板，{lid} 会被替换；保存站用 https://www.luogu.me/article/{lid}")
    ap.add_argument("--delay", type=float, default=2.0, help="每次请求间隔秒数，默认 2.0")
    ap.add_argument("--limit", type=int, default=10, help="本轮最多取回多少篇")
    ap.add_argument("--lids", default="", help="逗号分隔的显式编号，优先于主表队列")
    ap.add_argument("--dry-run", action="store_true", help="只打印队列，不发包")
    ap.add_argument("--timeout", type=float, default=18.0)
    args = ap.parse_args()

    if args.delay < 1.0:
        print("拒绝：间隔不得低于 1 秒（保存站有降级公告，保持低频）"); return
    q = load_queue(args)
    if not q:
        print("队列为空：主表里没有待取回条目，或用 --lids 显式指定"); return
    print(f"有序队列共 {len(q)} 个，本轮取前 {min(args.limit, len(q))} 个，间隔 {args.delay}s")
    if args.dry_run:
        for lid, prob in q[:args.limit]:
            print(f"  {prob:>7}  {lid}  -> {args.base.format(lid=lid)}")
        return

    os.makedirs(OUT, exist_ok=True)
    ua = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
    done = 0
    with open(LOG, "a", encoding="utf-8") as lg:
        for idx, (lid, prob) in enumerate(q[:args.limit]):
            url = args.base.format(lid=lid)
            rec = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "lid": lid,
                   "problem": prob, "url": url}
            try:
                text, status = fetch(url, ua, args.timeout)
                rec["http"] = status
                hit = [m for m in STOP_MARKERS if m in text]
                if hit:
                    rec["result"] = "stop"
                    rec["reason"] = "命中降级/拒绝标记：" + hit[0]
                    rec["body_head"] = text[:160].replace("\n", " ")
                    print(f"[{lid}] STOP {rec['reason']}")
                    lg.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    break
                verdict, why = looks_like_article(text, lid)
                rec["result"] = "ok"
                rec["is_article"] = verdict
                rec["verdict_reason"] = why
                obj = {"lid": lid, "problem": prob, "source": url,
                       "is_article": verdict, "verdict_reason": why,
                       "body": text}
                json.dump(obj, open(os.path.join(OUT, lid + ".json"), "w",
                                   encoding="utf-8"), ensure_ascii=False, indent=1)
                print(f"[{lid}] HTTP {status} | 是否题解={verdict} | {why} | {len(text)} 字")
                done += 1
            except urllib.error.HTTPError as e:
                rec.update({"http": e.code, "result": "http_error"})
                body = e.read().decode("utf-8", errors="ignore")[:160].replace("\n", " ")
                rec["body_head"] = body
                print(f"[{lid}] HTTP {e.code} | {body[:80]}")
                if e.code in (403, 429, 500, 502, 503, 504):
                    rec["result"] = "stop"
                    rec["reason"] = f"HTTP {e.code}，停止本轮以免加重站点负担"
                    lg.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    break
            except Exception as e:
                rec.update({"result": "error", "reason": type(e).__name__ + ": " + str(e)[:120]})
                print(f"[{lid}] {rec['reason']}")
            lg.write(json.dumps(rec, ensure_ascii=False) + "\n")
            if idx < min(args.limit, len(q)) - 1:
                time.sleep(args.delay)
    print(f"完成：成功 {done} 篇，日志 {os.path.relpath(LOG, REPO)}")
    print("下一步：人工确认 is_article 后更新 article_index.csv，再 python3 _build_site.py")

if __name__ == "__main__":
    main()
