#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 luogu_hack 全部资料分类整理成可离线查看的 luogu 仓库目录，并生成有序文章编号索引。"""
import os, re, csv, json, shutil, hashlib

# 用法: python3 生成索引_本地参考.py <原始资料目录> <输出目录>
# 警告: 会先清空并重建 <输出目录>！输出目录必须是独立路径，
#       切勿指向 clone 下来的本仓库自身，以免删掉仓库内容。
import sys
SRC = sys.argv[1] if len(sys.argv) > 1 else "/data/workspace/luogu_hack"
REPO = sys.argv[2] if len(sys.argv) > 2 else "/data/workspace/luogu_repo"
if os.path.exists(REPO):
    shutil.rmtree(REPO)
os.makedirs(REPO)

def w(rel, text):
    p = os.path.join(REPO, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    return p

def is_text(path):
    try:
        b = open(path, "rb").read()
    except Exception:
        return False
    if b[:4] == b"\x7fELF":
        return False
    if len(b) > 2_000_000:
        return False
    try:
        b.decode("utf-8")
        return True
    except Exception:
        return False

# ---------------------------------------------------------------- 人工编目
# (lid, 题号, 归类, 批次, 备注)  归类: 甲/乙/丙/登记(不计数)/待补录
CATALOG = [
    ("zaohomhi","P1001","丙","第1批","A+B，未 hack"),
    ("sfifnfaa","P1002","甲","第1批","过河卒 dp[0][0] 被自身覆盖，整表恒零"),
    ("h4cn628r","P1048","丙","第1批","01背包，33组含 w>T 边界全对"),
    ("uezud59i","P1220","丙","第1批","越界数据作废后归未 hack（第2批重判）"),
    ("l6u32sp7","P3959","丙","第1批","Prüfer 全枚举未找到更优解（第2批重判）"),
    ("arorhglg","P1182","甲","第2批","int r 累加 ΣAi 溢出"),
    ("yk90rg78","P1002","甲","第2批","f[0][0] 赋值在 DP 循环之后，输出恒 0"),
    ("ove5v8ck","P1216","丙","第2批","两段代码 120+ 组全对"),
    ("nzmytiez","P5638","甲","第3批","k>=n 时窗口循环不进，输出总长度"),
    ("pmio8se0","P1018","乙","第3批","n-xx-1 少算间隔，删 -1 即全对（第4批由甲下调）"),
    ("dmza5ifn","P1803","丙","第3批","文字与代码不一致但实测全对"),
    ("zcxe384l","P1090","丙","第3批","逐字版 pop() 缺 [] 属展示缺陷，不计"),
    ("up402yw6","P4995","丙","第4批","状压 DP 独立解 120 组全对"),
    ("tneoku44","P1216","丙","第4批","未 hack"),
    ("qsh0tcmu","P1002","丙","第4批","未 hack"),
    ("2yru0rav","P1164","丙","第5批","三段式 +1 恰好补空集项"),
    ("bv44vwt6","P2240","丙","第5批","浮点舍入自查：printf 为银行家舍入"),
    ("0hps6y5z","P1060","丙","第5批","最终代码含复制行，实测全对"),
    ("lgmnaw1h","P1616","丙","第5批","只取第3块最终码，前两块是思路回顾"),
    ("ipduooli","P1164","丙","第5批","自查：曾漏抄题解原有 dp[i][0]=1 造假 WA"),
    ("n5d7jq0b","P1020","丙","第5批","未 hack"),
    ("v3wxayi3","P1049","乙","第5批","作者自述随机放弃最优，反例仅作验证数据"),
    ("xmumv7ok","P1563","乙","第6批","x<0 漏 x==0，改一处即全对；作者自述打表"),
    ("h8ic4o0m","P1909","丙","第6批","搜索摘要与正文冲突，以逐字正文为准"),
    ("apqvl7bn","P1424","丙","第6批","含 n=1e5 边界"),
    ("tehqdnw3","P1093","丙","第6批","未 hack"),
    ("b7py0ojt","P2141","丙","第6批","未 hack"),
    ("6t0wrb4o","P1059","丙","第6批","未 hack"),
    ("05bplzw1","P1059","丙","第6批","sets; 系页面吞字符，补外壳后全对"),
    ("1ndosdfs","P1089","丙","第6批","mom*=1.2 浮点枚举 0 处不一致"),
    ("dk5mkxij","P1421","甲","第7批","double 累减边界，全枚举 2031 组 WA"),
    ("9jadrxl0","P1003","乙","第7批","im[10020][4] 改一个数字即全对"),
    ("nobyk23w","P1425","丙","第7批","借位减法；第10批重复登记"),
    ("beuv9jew","P1425","丙","第7批","全转分钟法；注释说反但代码自洽"),
    ("3hvn4ibz","P1085","丙","第7批","未 hack"),
    ("rjjud4hi","P1075","丙","第7批","未 hack"),
    ("v6gwt3bu","P1014","丙","第7批","2500 组含 N=1e7，float 精度自查 0 不一致"),
    ("f8ckkhfz","P1046","丙","第7批","未 hack"),
    ("l9bmtvor","P1098","甲","第8批","&&p3==1 锁死展开分支 + l==1 双缺陷"),
    ("zcy00qo9","P1098","甲","第8批","p1==2 数字分支缺逆序"),
    ("g17kwzzm","P1044","丙","第8批","两块代码 n=1..18 全枚举全对"),
    ("rlz2fzsx","P1044","丙","第8批","记忆化递归，数组偏小但实测无害"),
    ("hu58r34f","P1067","丙","第8批/第11批","第11批重复验证；两个 #define 宏展示形态"),
    ("a1sc0wom","P1028","丙","第8批","n=1..1000 全枚举全对"),
    ("88laurj5","P1098","登记","第8批","有 lid，逐字代码取不全，登记不计数"),
    ("dxk2a7a8","P1102","甲","第9批","双指针 c==0 不推进 w，越界崩溃"),
    ("4fj37pww","P1423","乙","第9批","dist>target 漏等于；200 组随机全过，需构造边界点"),
    ("0z8yhoc0","P1328","丙","第9批","w[a] 注释写反但代码自洽"),
    ("kckry124","P1012","丙","第9批","未 hack"),
    ("gw5uvykg","P1204","丙","第9批","未 hack"),
    ("nxvqnwg8","P1553","丙","第9批","17 个经典边界全过"),
    ("biep97vd","P1598","丙","第9批","本批唯一 Python 3 题解；第12批重复发现"),
    ("2edysvbn","P1428","登记","第9批","有 lid，正文只有思路无 AC 代码，登记"),
    ("h7y41tog","P1152","甲","第10批","爆栈+下标越界+多组漏读三层缺陷"),
    ("ictzayja","P1200","丙","第10批","不逐步取模，题面范围内安全"),
    ("vckbob2z","P1200","丙","第10批","Pascal 逐步 mod 47"),
    ("kfg4ugka","P1055","丙","第10批","scanf %1d 写 long long，UB 但实测全对"),
    ("59x93a43","P1179","丙","第10批","仅验作者标注的 AC 版"),
    ("qle49r7h","P1100","丙","第11批","转 32 位二进制串交换，0/2^32-1 边界全对"),
    ("03xk59dp","P1308","丙","第11批","getchar+getline，含行首/连续空格"),
    ("aceg4kbr","P1150","丙","第11批","同篇两块（模拟+数论）都验"),
    ("m16r8nbd","P1042","丙","第11批","62525 字符长输入实测；第12批重复发现"),
    ("jm3biw0r","P1706","丙","第11批","STL next_permutation，n=1..6,9 全量一致"),
    ("wiofo14v","P1706","丙","第11批","DFS 回溯 + setw(5)"),
    ("z3dolqp8","P1739","丙","第11批","count++/-- + 提前 break"),
    ("smtoxvvs","P3397","丙","第11批","原文无 using 行；自查外壳引入 map 歧义"),
    ("vt4bqm6v","P1116","丙","第11批","归并求逆序对"),
    ("vgwp3k30","P2089","丙","第11批","10 层枚举，峰值方案数 8953"),
    # 第12批（本轮）新发现：已定位到 article 编号，尚未逐字验证，标「待补录」
    ("ehkpairy","P1618","待补录","第12批","red()+finish()，已逐字取回，待对拍"),
    ("j4zpxmp6","P1618","待补录","第12批","check1/check2 三重枚举，已逐字取回，待对拍"),
    ("iv10492z","P1469","待补录","第12批","vector 累积异或，已逐字取回，待对拍"),
    ("3aph5o1d","P1469","待补录","第12批","Pascal 两块（快排/异或），已逐字取回"),
    ("utz61eus","P1469","待补录","第12批","int a[100000005] 桶排，内存受限，已取回"),
    ("xgwn9tfg","P1914","待补录","第12批","char a[1001]+putchar，已逐字取回"),
    ("d8583wuv","P1046","待补录","第12批","陶陶摘苹果，已逐字取回"),
]

# ---------------------------------------------------------------- 扫描补漏
pat_url = re.compile(r"luogu\.(?:com|org|me)/article/([a-z0-9]{8})")
pat_key = re.compile(r"\bP(\d{4})[_\-]([a-z0-9]{8})\b")
found = {}
for dp, dn, fn in os.walk(SRC):
    for f in fn:
        p = os.path.join(dp, f)
        if not is_text(p):
            continue
        t = open(p, encoding="utf-8").read()
        for m in pat_url.finditer(t):
            found.setdefault(m.group(1), "url")
        for m in pat_key.finditer(t):
            found.setdefault(m.group(2), "P" + m.group(1))
known = {c[0] for c in CATALOG}
extra = sorted(set(found) - known)
# 过滤掉明显不是 lid 的（出现在 URL 里的一律保留；仅 key 命中的做白名单式检查）
extra_real = [x for x in extra if found[x] == "url" or re.search(r"[0-9]", x)]

# ---------------------------------------------------------------- 生成索引
def cls_of(c):
    return {"甲":"甲·已 hack","乙":"乙·笔误/防抄袭","丙":"丙·未 hack",
            "登记":"登记·不计数","待补录":"待补录·未验证"}[c]

rows = []
for lid, prob, cat, batch, note in CATALOG:
    rows.append({
        "序号": 0, "编号": lid, "题号": prob,
        "是否题解": "是", "题解类型": "题解文章（8 位 article 编号）",
        "可逐字验证": "否" if cat in ("登记",) or lid in ("2edysvbn","88laurj5") else "是",
        "归类": cls_of(cat), "批次": batch, "备注": note,
        "URL": f"https://www.luogu.com/article/{lid}",
    })
for lid in extra_real:
    src = found.get(lid, "?")
    prob = src if src.startswith("P") else "未关联"
    rows.append({
        "序号": 0, "编号": lid, "题号": prob,
        "是否题解": "是", "题解类型": "题解文章（扫描补漏，待人工确认）",
        "可逐字验证": "待确认", "归类": "待补录·未验证", "批次": "扫描补漏",
        "备注": "由本地资料的 article URL / 源码键反查得到，未纳入批次计数",
        "URL": f"https://www.luogu.com/article/{lid}",
    })

def sortkey(r):
    p = r["题号"]
    n = int(p[1:]) if re.fullmatch(r"P\d{4}", p) else 99999
    return (n, r["编号"])
rows.sort(key=sortkey)
for i, r in enumerate(rows, 1):
    r["序号"] = i

os.makedirs(os.path.join(REPO, "02_文章编号索引"), exist_ok=True)
with open(os.path.join(REPO, "02_文章编号索引/article_index.csv"), "w",
          encoding="utf-8-sig", newline="") as f:
    wr = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    wr.writeheader()
    wr.writerows(rows)
with open(os.path.join(REPO, "02_文章编号索引/article_index.json"), "w",
          encoding="utf-8") as f:
    json.dump({"说明": "对已发现的全部 8 位文章编号做有序编目，逐条判定是否题解；非全站遍历",
               "总数": len(rows), "条目": rows}, f, ensure_ascii=False, indent=1)

# 有序枚举 md
lines = ["# 所有文章编号 · 有序枚举",
         "",
         "> 「枚举」= 对**已发现的全部 8 位 article 编号**按题号升序、同题按编号字典序编目，"
         "并逐条判定「是否题解」。**不是**对编号空间或全站做遍历，也不发起高频请求；"
         "新增编号按低频逐篇补录后重新生成本表。",
         "",
         f"共 **{len(rows)}** 个编号；其中 `是否题解=是` 的有 "
         f"**{sum(1 for r in rows if r['是否题解']=='是')}** 个。",
         "",
         "| 序号 | 题号 | 编号 | 是否题解 | 归类 | 批次 |",
         "|---|---|---|---|---|---|"]
for r in rows:
    lines.append(f"| {r['序号']} | {r['题号']} | `{r['编号']}` | {r['是否题解']} | "
                 f"{r['归类']} | {r['批次']} |")
lines += ["", "完整字段（URL、可逐字验证、备注）见 `article_index.csv` / `article_index.json`。", ""]
w("02_文章编号索引/所有编号_有序枚举.md", "\n".join(lines))

# 判定口径
w("02_文章编号索引/判定口径.md", """# 「是否题解」判定口径

给一个编号或 URL，按以下顺序判定，命中即停。**只看形态与正文特征，不发起请求**。

| 序 | 判据 | 结论 |
|---|---|---|
| 1 | `www.luogu.com/article/<8位>` 或 `www.luogu.org/article/<8位>`，且正文含题号 / 思路 / 代码块 | **是题解**（本仓库编号体系） |
| 2 | 同上，但正文只有思路、无 AC 代码，或逐字代码取不全 | **是题解**，但 `可逐字验证=否`，登记不计数 |
| 3 | `www.luogu.me/article/<8位>`、`api.luogu.me/...` | **未知**：保存站镜像，只返回站点框架 / 403，正文不可判定 |
| 4 | `luogu.org/problem/Pxxxx`、`luogu.com/problem/Pxxxx` | **否**：题面页，无题解代码 |
| 5 | `luogu.org/blog/<user>/solution-pxxxx` | **题解内容，但不在 8 位编号体系**：旧个人博客 |
| 6 | 搜索结果标题为「首页 - 洛谷 \\| 计算机科学教育新生态」，无 article 路径 | **否**：站点首页 / 导航框架 |
| 7 | 第三方域名（CSDN、博客园、公众号、OJ 镜像、技术博客等） | **否**：转载 / 外部资料，不纳入归档 |
| 8 | 8 位字符串出现在测试数据、期望输出、变量名里（如 `srl7f6h9`、`dggffeeh`） | **否**：非编号，扫描时剔除 |

配套脚本：`classify_article.py`
- `python3 classify_article.py sfifnfaa` → 查索引，返回是否题解 + 归类 + 批次
- `python3 classify_article.py <任意URL>` → 按上表规则判定
- `python3 classify_article.py --stats` → 输出分类统计

> 口径来源：第 4 批「三类 + 代码只是辅助、不判完整度」、第 11 批「搜索摘要 ≠ 正文」「编译报错先分清原文还是自己补的外壳」。
""")

# 判定脚本
w("02_文章编号索引/classify_article.py", '''#!/usr/bin/env python3
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
        if re.search(r"luogu\\.(?:com|org)/article/[a-z0-9]{8}", u):
            m = re.search(r"article/([a-z0-9]{8})", u)
            lid = m.group(1)
            return classify(lid, idx) if lid in idx else f"[规则1] {lid}: 是题解（article 编号体系，未登记）"
        if re.search(r"luogu\\.me/article/", u) or "api.luogu.me" in u:
            return "[规则3] 未知：保存站镜像，正文不可判定（框架/403）"
        if re.search(r"luogu\\.(?:com|org)/problem/", u):
            return "[规则4] 否：题面页"
        if re.search(r"luogu\\.org/blog/.+solution-p\\d+", u):
            return "[规则5] 题解内容，但不在 8 位编号体系（旧个人博客）"
        if re.search(r"luogu\\.(?:com|org)/?$", u):
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
''')

# 非题解页与待补录
w("02_文章编号索引/非题解页与待补录登记.md", """# 非题解页 / 编号体系外 / 待补录登记

## A. 判定为「否」的页面形态（不含 8 位 article 编号，不进索引）

| 形态 | 例子 | 判定 |
|---|---|---|
| 站点首页框架 | 搜索结果标题「首页 - 洛谷 \\| 计算机科学教育新生态」 | 否 |
| 题面页 | `www.luogu.org/problem/P3397`、`luogu.com/problem/P1067` | 否 |
| 旧个人博客 | `www.luogu.org/blog/stonejuice/solution-p1307` | 题解内容，但不在 8 位编号体系 |
| 第三方转载/镜像 | CSDN、博客园、微信公众号、hqwc.cn、coderli.com、牛客、ACGO、清北信奥 OJ、vjudge、HydroOJ、云斗学院、掘金、cfanz、rsywx、ima.qq.com、guopcingithub.github.io、tracylaoshi.com.cn、codeleading、leheavengame 等 | 否 |
| 保存站 | `www.luogu.me/article/<lid>`、`api.luogu.me/article/query/<lid>` | 未知（框架/403，正文不可判定） |

> 保存站状态：首页可确认归档规模与 8 位 ID 体系，但文章页为 SPA，当前出口只返回框架或 403，
> 站点还挂过「AI 自动化请求导致保存 API 队列堵塞」降级公告。因此**不刷接口**，
> 只把它当编号体系的旁证；正文一律以可直读的 `www.luogu.com/article/<lid>` 逐字取回为准。

## B. 已知是题解、但缺 8 位编号（登记不计数）

| 题号 | 形态 | 出处 |
|---|---|---|
| P1002 | vis 标记版 / 滚动数组版 | 第2批、第4批 |
| P1018 | 作者注明「不带高精度」的辅助代码 | 第4批 |
| P1049 | 作者开篇自述「我写这篇题解主要是由于一个 BUG」的演示版 | 第5批 |
| P1089 | 「一堆题解」的 `mom*=1.2` 浮点自查 | 第6批 |
| P1914 | 超过 z 减一次 26（题面 n≤26 自查） | 第9批 |
| P1042 / P1010 / P1141 / P1030 等 | 逐字代码取不全 | 第8批 §6 |

## C. 第 12 批本轮新发现（已定位编号，未及逐字验证 → 待补录）

| 题号 | 编号 | 状态 |
|---|---|---|
| P1618 | `ehkpairy` | 已逐字取回 red()/finish()，待对拍 |
| P1618 | `j4zpxmp6` | 已逐字取回 check1/check2，待对拍 |
| P1469 | `iv10492z` | vector 累积异或，待对拍 |
| P1469 | `3aph5o1d` | Pascal 两块（快排 / 异或） |
| P1469 | `utz61eus` | `int a[100000005]` 桶排，内存受限 |
| P1914 | `xgwn9tfg` | `char a[1001]` + putchar |
| P1046 | `d8583wuv` | 陶陶摘苹果 |
| P1428 | `2edysvbn` | 有编号，正文只有思路无 AC 代码 |

补录流程：低频取回正文 → 本地编译 + 独立解对拍 → 写入 `article_index.csv` 的
`归类/批次/备注` → 重新运行生成脚本更新有序表 → 归入 01_批次清单 的下一批。
""")

# ---------------------------------------------------------------- 总览
w("00_总览/三类口径与累计统计.md", """# 三类口径与累计统计

## 口径（第 4 批定稿，后续各批沿用）

- **甲 · 已 hack**：题面内存在确定性测试点使题解代码 WA / RE，且修复要动算法层面
  （移语句、换类型、补分支）。不考虑评测机波动，不主张 TLE / 随机超时。
- **乙 · 轻微笔误 / 主动防抄袭**（单列）：改一处字符或数字就对，或作者主动删减、
  拆段、声明示意版。划界用「修复代价」；随机化无正确性保证但有确定性反例的也归这里。
- **丙 · 未 hack**：逻辑正确。

两条硬约束：
1. **代码只是辅助，不判完整度**——取到片段只补最小外壳（include、main、必要声明）
   再编译；缺头文件、老式 `main(){}`、页面吞字符一律不计缺陷，只验核心逻辑。
2. **题面内**——违反题面保证的输入（越界坐标、超值域、超长度）一律作废，不计 hack。

## 累计（截至第 11 批）

| 项 | 数 |
|---|---|
| 逐篇验证题解 | **76 篇** |
| 甲 · 已 hack | **9 篇** |
| 乙 · 笔误/防抄袭 | **9 篇** |
| 丙 · 未 hack | **58 篇** |
| 甲类合法反例 | **23 条** |

第 12 批进行中：已定位 7 个新编号，尚未完成对拍，暂不计入累计。

## 自查纪律（逐批累加，误判回查自己）

1. 搜索摘要 ≠ 文章正文，冲突时以逐字取回为准
2. 片段先回原文逐字复核；补最小外壳**不能改变语义**（第11批 P3397 教训）
3. 编译报错先分清是原文、还是自己补的外壳 / 自己写的独立解
4. 浮点题先对齐标程舍入与 ULP；随机对拍全过不等于没问题，边界点与官方样例单独跑
5. 数组越界必须实测到具体规模，分清「栈溢出」与「下标越界」两层
6. 「以为改一处就修好」必须跑修复版复验，再决定甲/乙
7. 作者自曝的非正解块、思路回顾块、辅助示意版不拿来 hack
8. 不登录、不提交、不刷接口；保存站只作编号体系旁证
""")

HACKS = """# 甲类合法反例清单（23 条）

> 全部满足：题面内 + 确定性 WA/RE + 不考虑评测机波动。第 11 批无新增。

| 编号 | 题解 | 代表输入 | 期望 → 实际 |
|---|---|---|---|
| H-001~003 | P1002 `sfifnfaa` | `6 6 3 3` / `20 20 0 20` / `20 20 10 10` | `6` / `137846521561` / `21388094780` → 均 `0` |
| H-004/005/005b | P1182 `arorhglg` | 三段二分边界 | `6e7` / `5e4` / `6e4` → `3e7` / `2.5e4` / `3e4` |
| H-006/007 | P1002 `yk90rg78` | `6 6 3 3` / `20 20 0 20` | `6` / `137846521561` → 均 `0` |
| H-008/009/010 | P5638 `nzmytiez` | `2 100`/`5` · `3 5`/`2 3` · `4 4`/`7 1 9` | 均 `0` → `5` / `5` / `17` |
| H-011/012/013 | P1421 `dk5mkxij` | `7 6` / `19 0` / `20 9` | `4` / `10` / `11` → `3` / `9` / `10` |
| H-014/015/016 | P1098 `l9bmtvor` | `2 3 2 / a-d-d` · `1 2 1 / a` · `3 2 2 / a-d` | `aCCCBBBd-d` / `a` / `a****d` → `a-d-d` / `aa` / `a-d` |
| H-017 | P1098 `zcy00qo9` | `2 2 2 / 1-5` | `14433225` → `12233445` |
| H-018/019/020 | P1102 `dxk2a7a8` | `1 / 0 / 5` · `2 / 0 / 5 5` · `3 / 1 / 1 5 3` | `1` / `4` / `0` → `0` / SIGSEGV / SIGSEGV |
| H-021/022/023 | P1152 `h7y41tog` | 官方样例#1 · `2 / 0 200000000` · `2 / -1e8 1e8` | `Jolly` / `Not jolly` / `Not jolly` → 均 SIGSEGV |

逐条复现方式：在 `04_复现代码/` 找到对应 `P####_<lid>.cpp`，用
`g++ -std=c++17 -O2` 编译后喂上表输入；独立正确解与对拍脚本在 `03_验证脚本/`。
"""
w("00_总览/甲类合法反例_23条.md", HACKS)

# ---------------------------------------------------------------- 分类拷贝
BATCH_DIR = "01_批次清单"
os.makedirs(os.path.join(REPO, BATCH_DIR), exist_ok=True)
for f in sorted(os.listdir(SRC)):
    p = os.path.join(SRC, f)
    if not os.path.isfile(p) or not f.endswith(".md"):
        continue
    shutil.copyfile(p, os.path.join(REPO, BATCH_DIR, f))

script_names = set()
code_names = set()
data_names = set()
for dp, dn, fn in os.walk(SRC):
    for f in fn:
        p = os.path.join(dp, f)
        if not is_text(p):
            continue
        rel = os.path.relpath(p, SRC)
        if f.endswith((".cpp", ".c")):
            dst = os.path.join(REPO, "04_复现代码", rel.replace(os.sep, "__"))
        elif f.endswith((".json", ".log")):
            dst = os.path.join(REPO, "05_对拍原始数据", rel.replace(os.sep, "__"))
        elif f.endswith(".py"):
            dst = os.path.join(REPO, "03_验证脚本", rel.replace(os.sep, "__"))
        elif f.endswith(".md"):
            continue
        else:
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(p, dst)
        (script_names if f.endswith(".py") else code_names if f.endswith((".cpp", ".c"))
         else data_names).add(os.path.basename(dst))

# 顶层 py 单独也放一份（build 目录外的主脚本）
for f in sorted(os.listdir(SRC)):
    if f.endswith(".py"):
        dst = os.path.join(REPO, "03_验证脚本", f)
        if not os.path.exists(dst):
            shutil.copyfile(os.path.join(SRC, f), dst)

# ---------------------------------------------------------------- 文件清单
manifest = []
for dp, dn, fn in os.walk(REPO):
    for f in sorted(fn):
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, REPO)
        manifest.append({
            "路径": rel, "字节": os.path.getsize(p),
            "SHA256": hashlib.sha256(open(p, "rb").read()).hexdigest()[:16],
        })
manifest.sort(key=lambda x: x["路径"])
with open(os.path.join(REPO, "00_总览/仓库文件清单.csv"), "w",
          encoding="utf-8-sig", newline="") as f:
    wr = csv.DictWriter(f, fieldnames=["路径", "字节", "SHA256"])
    wr.writeheader(); wr.writerows(manifest)

w("06_离线复现说明.md", """# 离线复现说明

clone 之后整个仓库可完全离线查看，不需要账号、不需要联网。

```
git clone https://github.com/<你的用户名>/luogu.git
cd luogu
```

## 目录怎么查

| 目录 | 内容 |
|---|---|
| `01_批次清单/` | 第 1~11 批逐篇验证报告（含每批的假命中自查） |
| `02_文章编号索引/` | **有序编号枚举 + 是否题解判定**（CSV / JSON / MD / 判定脚本） |
| `03_验证脚本/` | 各批对拍脚本（Python），本地编译 + 独立正确解 |
| `04_复现代码/` | 逐字取回并补最小外壳的题解源码（`.cpp` / `.c`） |
| `05_对拍原始数据/` | 各批 `results.json` / `verify.log` 原始输出 |
| `00_总览/` | 三类口径、累计统计、23 条甲类反例、全仓文件清单 |

## 常用命令

```bash
# 查一个编号是不是题解
python3 02_文章编号索引/classify_article.py sfifnfaa
python3 02_文章编号索引/classify_article.py --stats

# 复现一篇题解（以 P1002 sfifnfaa 为例）
g++ -std=c++17 -O2 -o /tmp/t 04_复现代码/P1002_sfifnfaa.cpp
echo "6 6 3 3" | /tmp/t          # 期望 6，实际 0

# 重跑某一批对拍
python3 03_验证脚本/verify_batch11.py
```

## 更新编号索引

新拿到一个 `article/<8位>` 编号后：低频取回正文 → 本地对拍 → 在
`02_文章编号索引/article_index.csv` 追加/更新一行（`是否题解` 必填）→
重新运行生成脚本刷新 `所有编号_有序枚举.md`。**不要对编号空间做遍历扫描**。

## 依赖

- 编译：`g++`（C++17），Python 3
- 报告与索引用 UTF-8；CSV 带 BOM，Excel 直接打开不乱码
- 全程不登录、不提交、不调用评测接口
""")

w("README.md", f"""# luogu · 题解逐篇 hack 资料库（离线归档）

> 把「逐篇尝试 hack 洛谷题解」的全部资料分类整理，供以后离线查看。
> 含**有序枚举的全部已发现 8 位文章编号**与逐条「是否题解」判定。

## 一眼看懂

- **口径**：甲（已 hack）/ 乙（轻微笔误·主动防抄袭，单列）/ 丙（未 hack）三类
- **累计**：76 篇题解 · 甲 9 · 乙 9 · 丙 58 · 甲类合法反例 23 条
- **编号索引**：{len(rows)} 个 8 位 article 编号，按题号升序有序编目，逐条判定是否题解
- **第 12 批**：进行中，7 个新编号已定位、未及验证，标「待补录」

## 「枚举」的确切含义

对**已发现的全部编号**做有序编目（题号升序 → 编号字典序），并逐条判定是否题解；
**不是**对 36^8 编号空间或全站做高频遍历。新增编号按低频逐篇补录，见
`02_文章编号索引/判定口径.md` 与 `06_离线复现说明.md`。

## 快速入口

| 想看什么 | 打开 |
|---|---|
| 编号有序表 | `02_文章编号索引/所有编号_有序枚举.md` |
| 机读索引（含是否题解） | `02_文章编号索引/article_index.csv` |
| 给一个编号判定是否题解 | `python3 02_文章编号索引/classify_article.py <编号或URL>` |
| 23 条确凿反例 | `00_总览/甲类合法反例_23条.md` |
| 三类口径与自查纪律 | `00_总览/三类口径与累计统计.md` |
| 逐批报告 | `01_批次清单/` |
| 全仓文件清单 | `00_总览/仓库文件清单.csv` |

## 目录

```
00_总览/            口径、累计统计、反例清单、文件清单
01_批次清单/        第 1~11 批逐篇验证报告
02_文章编号索引/    有序枚举 + 是否题解判定 + 判定脚本 + 非题解页登记
03_验证脚本/        各批对拍脚本
04_复现代码/        逐字取回的题解源码（补最小外壳）
05_对拍原始数据/    results.json / verify.log
06_离线复现说明.md  clone、编译、重跑、补录流程
```

## 约束

- 全程本地编译 + 独立正确解对拍，**不登录、不提交、不刷接口**
- 代码只是辅助，不判完整度；缺头文件 / 页面吞字符不计缺陷
- 题面外的输入一律作废，不计 hack
- 保存站仅作编号体系旁证，正文以可直读文章页逐字取回为准
- 仓库内不含任何账号、凭据或令牌

整理日期：2026-11-22
""")

print("REPO_FILES", len(manifest))
print("INDEX_ROWS", len(rows))
print("EXTRA_SCAN", extra_real)
print("BATCH_MD", len([f for f in os.listdir(os.path.join(REPO, BATCH_DIR))]))
