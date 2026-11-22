#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""给一个 8 位编号或 URL，判断它是不是题解页。只读本地索引，不发网络请求。"""
import os, sys, csv, json, re
HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "article_index.csv")

def load():
    with open(CSV, encoding="utf-8-sig") as f:
        return {r["编号"]: r for r in csv.DictReader(f)}

def classify(x, idx):
    if x in idx:
        r = idx[x]
        return f"[索引命中] {x}: 是题解 | {r['题号']} | {r['归类']} | {r['批次']} | {r['URL']}"
    if x.startswith("http"):
        u = x
        if re.search(r"luogu\.(?:com|org)/article/[a-z0-9]{8}", u):
            m = re.search(r"article/([a-z0-9]{8})", u)
            lid = m.group(1)
            return classify(lid, idx) if lid in idx else f"[规则1] {lid}: 是题解（article 编号体系，未登记）"
        if re.search(r"luogu\.me/article/", u) or "api.luogu.me" in u:
            return "[规则3] 未知：保存站镜像，正文不可判定（框架/403）"
        if re.search(r"luogu\.(?:com|org)/problem/", u):
            return "[规则4] 否：题面页"
        if re.search(r"luogu\.org/blog/.+solution-p\d+", u):
            return "[规则5] 题解内容，但不在 8 位编号体系（旧个人博客）"
        if re.search(r"luogu\.(?:com|org)/?$", u):
            return "[规则6] 否：站点首页/导航框架"
        return "[规则7] 否：第三方/外部页面，不纳入归档"
    if re.fullmatch(r"[a-z0-9]{8}", x):
        return f"[未登记] {x}: 8 位编号，索引中无记录；按低频逐篇取回正文后再判定"
    return "[无法判定] 既不是 8 位编号也不是 URL"

def main():
    idx = load()
    args = sys.argv[1:]
    if not args or args[0] == "--stats":
        from collections import Counter
        c = Counter(r["归类"] for r in idx.values())
        print(f"索引共 {len(idx)} 个编号；是否题解=是 的有 "
              f"{sum(1 for r in idx.values() if r['是否题解']=='是')} 个")
        for k, v in sorted(c.items()):
            print(f"  {k}: {v}")
        return
    for a in args:
        print(classify(a.strip(), idx))

if __name__ == "__main__":
    main()
