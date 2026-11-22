#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""低频补录新文章：写进有序编号索引（CSV 为权威主表），再重生成离线站。

用法：
  python3 site/ingest.py new.json          # 数组或 {"articles":[...]}
  python3 site/ingest.py new.jsonl         # 每行一个 JSON 对象
  python3 _build_site.py                  # 回到仓库根目录重生成页面

每个对象字段：
  lid        8 位 article 编号（必填）
  problem    题号，如 P1002
  cls        归类：甲/乙/丙/登记/待补录（默认「待补录」）
  is_article 是否题解（默认「是」）
  title / content / code / url / batch / note / verifiable  可选

设计原则：有序追加、按题号升序重编目、不发起任何网络请求、不对编号空间做遍历。
CSV 是权威主表；`_build_site.py` 从它重建 `site/data/articles.json` 与全部页面，
因此补录后一定要重跑生成器。
"""
import os, sys, json, csv, re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CSV = os.path.join(REPO, "02_文章编号索引", "article_index.csv")
COLS = ["序号","编号","题号","是否题解","题解类型","可逐字验证","归类","批次","备注","URL"]
CLS = {"甲":"甲·已 hack","乙":"乙·笔误/防抄袭","丙":"丙·未 hack",
       "登记":"登记·不计数","待补录":"待补录·未验证"}

def load_new(p):
    t = open(p, encoding="utf-8").read().strip()
    if p.endswith(".jsonl"):
        return [json.loads(l) for l in t.splitlines() if l.strip()]
    d = json.loads(t)
    return d["articles"] if isinstance(d, dict) and "articles" in d else (d if isinstance(d, list) else [d])

def main():
    if len(sys.argv) < 2:
        print(__doc__); return
    with open(CSV, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    by = {r["编号"]: r for r in rows}
    added = updated = 0
    for x in load_new(sys.argv[1]):
        lid = x.get("lid")
        if not lid or not re.fullmatch(r"[a-z0-9]{8}", lid):
            print("跳过：缺合法 lid", x.get("lid")); continue
        if lid in by:
            r = by[lid]; updated += 1
        else:
            r = {k: "" for k in COLS}
            r.update({"编号": lid, "题解类型": "题解文章（8 位 article 编号）",
                      "可逐字验证": "是", "URL": f"https://www.luogu.com/article/{lid}"})
            rows.append(r); by[lid] = r; added += 1
        r["题号"] = x.get("problem", r.get("题号") or "未关联")
        r["是否题解"] = x.get("is_article", r.get("是否题解") or "是")
        r["归类"] = CLS.get(x.get("cls", ""), x.get("cls") or r.get("归类") or "待补录·未验证")
        r["批次"] = x.get("batch", r.get("批次") or "补录")
        r["备注"] = x.get("note", r.get("备注") or "低频补录，待逐字验证")
        if "verifiable" in x: r["可逐字验证"] = x["verifiable"]
        if "url" in x: r["URL"] = x["url"]
        if x.get("content") or x.get("code"):
            d = os.path.join(HERE, "data", "ingested")
            os.makedirs(d, exist_ok=True)
            json.dump({"lid": lid, "title": x.get("title", ""),
                       "content": x.get("content", ""), "code": x.get("code", "")},
                      open(os.path.join(d, lid + ".json"), "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)
    def pk(a):
        m = re.fullmatch(r"P(\d{4})", a.get("题号", ""))
        return (int(m.group(1)) if m else 99999, a["编号"])
    rows.sort(key=pk)
    for i, r in enumerate(rows, 1): r["序号"] = str(i)
    with open(CSV, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(rows)
    print(f"补录完成：新增 {added}，更新 {updated}，当前共 {len(rows)} 个编号（已按题号升序重排）")
    print("下一步：在仓库根目录运行 `python3 _build_site.py` 重生成页面与 site/data/articles.json")

if __name__ == "__main__":
    main()
