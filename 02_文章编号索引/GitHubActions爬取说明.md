# 用仓库自己的 Actions 出口做低频取回

> 第 15 批新增。用户提示「我都给你仓库了，你可以用仓库的 work 来爬取」，
> 于是把取回动作放到 GitHub Actions 里跑：**网络出口换成 GitHub 的**，
> 取回的正文直接 commit 回本仓库，本地再 pull 下来做对拍与归档。

## 为什么这么做

沙盒出口对 `luogu.me` 全路径返回 403 `policy_default_denied`，
`luogu.com/article` 直连也被同一策略层拒；内置取回通道只能读 SPA 骨架。
GitHub Actions 的 runner 是另一套出口，可能能直读正文——尤其适合重试
沙盒里取不到的编号（本批 `azdjstpm` 就是探针）。

## 文件

- `.github/workflows/crawl_lowfreq.yml` —— workflow 本体
- `site/lowfreq_fetch.py` —— 取回器（仓库已有资产，workflow 直接复用）
- `site/data/ingested/<lid>.json` —— 取回正文落盘位置
- `02_文章编号索引/取回日志.jsonl` —— 每次请求的结构化日志

## 触发

只支持**手动** `workflow_dispatch`，**不启用 schedule**：避免无人看管时持续发包。

| 输入 | 默认 | 说明 |
|---|---|---|
| `base` | `https://www.luogu.com/article/{lid}` | 可切保存站 `https://www.luogu.me/article/{lid}` |
| `lids` | `azdjstpm` | 显式 8 位编号，逗号分隔；留空则走主表有序队列 |
| `limit` | `5` | 本轮最多几篇 |
| `delay` | `2.0` | 每次间隔秒数，低于 1 秒脚本直接拒绝 |

在仓库 Actions 页点「Run workflow」即可；也可用 REST：

```
POST /repos/liuyiming2024/luogu/actions/workflows/crawl_lowfreq.yml/dispatches
{"ref":"main","inputs":{"lids":"azdjstpm","limit":"1","delay":"2.0"}}
```

## 硬约束（写进 workflow 与取回器）

1. 默认 **2 秒/次**，不并发，`concurrency` 组保证同一时刻只有一个 crawl run
2. 只处理**明确给出的编号**或主表有序队列，**绝不遍历 36⁸ 编号空间**
3. 命中「服务降级公告 / Request denied / 队列堵塞」或 HTTP 403/429/5xx
   → **立即停止本轮**，不重试轰炸
4. 单次默认 5 篇；不登录、不提交题解、不刷保存 API
5. 取回结果只写 `ingested/` 与日志，**不自动改主表**；
   「是否题解」与三类归类仍由本地对拍后人工确认

## 闭环

```
dispatch → runner 低频取回 → commit 回仓库
   → 本地 git pull --rebase → 从 ingested/ 读正文
   → 编译对拍 / 三类归类 → 更新 article_index.csv
   → _build_site.py 重生成离线站 → push + 重打 zip
```

`_build_site.py` 已改成选择性清理，**重生成不会删除** `site/data/ingested/`
与两个常驻脚本，所以 crawl 成果不会被抹掉。

## 公开与署名（2026-11-24 追加）

仓库已改为**公开**并由 `pages.yml` 部署 GitHub Pages 归档库网页。
取回结果提交前会先跑 `tools/provenance.py`，保证每条新正文都带**原文链接 /
作者署名 / 取回时间 / 内容完整性签名**；网页每篇都有「引用与署名」块与移除入口。
版权归原作者及洛谷所有，仅作学术归档留痕。

## 首次实测

- dispatch 返回 **HTTP 204**，run `45410907569` 进入 `queued`
- 该 run 的探针编号是 `azdjstpm`（P1008 三连击）——沙盒三种通道都取不到正文，
  用它检验 GitHub 出口是否能直读
- 结果以仓库里是否新增 `site/data/ingested/azdjstpm.json` 为准；
  若仍 403 / SPA 骨架，该编号继续维持「登记·不计数」，不拿搜索摘要硬判
