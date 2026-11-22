#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""低频补录新文章：把新拿到的题解写进 data/articles.json，然后重新生成本站页面。

用法：
  python3 ingest.py new.json          # new.json 为数组或 {"articles":[...]}
  python3 ingest.py new.jsonl         # 每行一个 JSON 对象
  python3 _build_site.py              # 回到仓库根目录重生成（本脚本会自动调用）

每个对象字段：
  lid        8 位 article 编号（必填）
  problem    题号，如 P1002
  title      标题（可选）
  content    题解正文 Markdown（可选）
  code       题解代码字符串或 [{file,text}]（可选）
  url        原文地址（可选，默认 https://www.luogu.com/article/<lid>）
  is_article 是否题解（默认「是」）
  cls        归类：甲/乙/丙/登记/待补录（默认「待补录」）
  batch      批次（可选）
  note       备注（可选）

设计原则：有序追加、按题号升序重编目、不发起任何网络请求、不对编号空间做遍历。
"""
import os, sys, json, subprocess
HERE=os.path.dirname(os.path.abspath(__file__))
DATA=os.path.join(HERE,"data","articles.json")

def load_new(p):
    t=open(p,encoding="utf-8").read().strip()
    if p.endswith(".jsonl"):
        return [json.loads(l) for l in t.splitlines() if l.strip()]
    d=json.loads(t)
    return d["articles"] if isinstance(d,dict) and "articles" in d else (d if isinstance(d,list) else [d])

def main():
    if len(sys.argv)<2:
        print(__doc__); return
    db=json.load(open(DATA,encoding="utf-8"))
    items=db["articles"]
    idx={a["lid"]:a for a in items}
    added=updated=0
    for x in load_new(sys.argv[1]):
        lid=x.get("lid")
        if not lid: print("跳过：缺 lid"); continue
        rec=idx.get(lid)
        if rec is None:
            rec={"lid":lid,"page":f"articles/{lid}.html"}; items.append(rec); idx[lid]=rec; added+=1
        else: updated+=1
        for k_src,k_dst in [("problem","problem"),("title","title"),("content","content"),
                            ("code","code"),("url","url"),("is_article","is_article"),
                            ("cls","class"),("batch","batch"),("note","note")]:
            if k_src in x: rec[k_dst]=x[k_src]
        rec.setdefault("url",f"https://www.luogu.com/article/{lid}")
        rec.setdefault("is_article","是")
        rec.setdefault("class","待补录·未验证")
        rec.setdefault("problem","未关联")
        rec.setdefault("title",f'{rec["problem"]} 题解 · {lid}')
    def pk(a):
        import re
        m=re.fullmatch(r"P(\d{4})",a.get("problem",""))
        return (int(m.group(1)) if m else 99999,a["lid"])
    items.sort(key=pk)
    db["收录总数"]=len(items)
    json.dump(db,open(DATA,"w",encoding="utf-8"),ensure_ascii=False,indent=1)
    print(f"补录完成：新增 {added}，更新 {updated}，当前共 {len(items)} 篇")
    print("下一步：在仓库根目录运行 `python3 _build_site.py` 重生成页面（或把本脚本接入该流程）")

if __name__=="__main__": main()
