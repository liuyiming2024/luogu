# tools/std · 本地 std 库、题面闸门、工单对跑与代审

> 顺序：**先爬到题面 → 再做 std**。全部跑在本地，零外网、零登录。
> 不引用不存在的官方测试数据；不凭感觉放行。

## 跑一遍

```bash
python3 tools/std/verify_std.py      # 六类变异 + 题面闸门，必须全 PASS
python3 tools/std/std_pipeline.py    # 工单（含 external/）→ 候选台账 + 期望表
python3 tools/std/review.py          # 代审（证据链复核）
python3 tools/std/promote.py         # 迁入（仅 contentOnly 正文级证据才执行）
python3 _build_site.py               # 台账上页
python3 tools/std/problem_gate.py    # 单看题面闸门
```

## 题面优先（对面）

```bash
python3 tools/fetch_problem.py --pids P1001,P1421,P1002 --delay 2.0
# 或 GitHub Actions: problem_first.yml / crawl_tick.yml --problem-first
```

## 目录

| 文件 | 作用 |
|---|---|
| `fetch_problem.py`（在 `tools/`） | contentOnly 题面取回器，只有真 JSON 才落盘 |
| `problem_gate.py` | 题面闸门：范围逐字 / 样例实测 / 用例 in_range |
| `std_bank.json` | 题库元信息，每题带「范围引用 / 题面证据 / 样例」 |
| `std/P*.cpp` | 三道真题的自写独立正确解 |
| `cases.py` | 题面内用例（范围逐字引用、样例置顶、机读 `in_range`） |
| `runner.py` | fork + `os.wait4`：CPU 时间 / 峰值 RSS / 超时 kill |
| `std_eval.py` | 编译 + 多轮对跑 + 判优 + 期望表 |
| `std_pipeline.py` | 工单队列（含外部投稿）→ 台账 + 期望表 |
| `review.py` | 代审：证据链复核，结论带 sha256 / ratio / 闸门细节 |
| `promote.py` | 唯一迁入入口，证据等级 guard + 备份 + sha256 留痕 |
| `verify_std.py` | 六类变异 + 题面闸门共 20+ 检查点 |
| `tickets/` | 本地工单；`tickets/external/` 是别人投稿入口 |
| `fixtures/` | 验证夹具（**不进正式题库、不做 std**） |

## 证据等级（关键）

| 等级 | 能做 std | 能迁入 |
|---|---|---|
| 无题面存档 | ❌ 闸门「不做」 | ❌ |
| 检索摘录（逐字，可核对） | ✅ 对跑 / 审核 | ❌ 挂起待正文复核 |
| contentOnly 正文（队列取回） | ✅ | ✅ 审核全过后由 `promote.py` 执行 |

把摘录伪装成正文、或凭记忆写范围，都被闸门与回归检查点挡住。

## 第 17 条 · 题面进度 = STD 进度 + 朴素算法对拍

| 目录 | 作用 |
|---|---|
| `brute/P*.cpp` / `brute/P1001.py` | 每题一份按题面直译的**朴素算法**，与 std 不同实现 |
| `verify_brute.py` | STD↔朴素逐字对跑 + 题面样例 + 自动变异敏感性 |
| `site/data/std_brute_check.json` | 对拍台账（上页，只读） |

```bash
python3 tools/std/verify_brute.py    # 7/7 PASS · 197 组 · 变异 7/7
python3 tools/std/verify_std.py      # 含「题面存档集合 == STD 题库集合」检查
```

指数级朴素算法（P1002 / P1028 / P1044）如实标注对拍规模，
**不假装全范围**；全部范围的正确性由 std 自身 + 题面闸门 + 样例实测覆盖。

## 题库现状：28 题 = 28 份正文级题面

| 批次 | 题号 |
|---|---|
| 首批 | P1001 P1421 P1002 P1909 P1028 P1044 P1059 |
| 第二轮补齐 | P1003 P1024 P1025 P1029 P1030 P1031 P1022 P1023 P1026 P1027 P1032 |
| 第三轮补齐 | P1033 P1034 P1035 P1036 P1037 P1038 P1039 P1040 P1041 P1042 |

`brute/` 现 28 份（含 10 份 Python）；`scale_inputs()` 对指数级/资源型朴素算法
逐题标注真实对拍规模，不假装覆盖全范围。`verify_brute.py` 的变异验证在
`+1` 变异 CE 时自动回退到「多输出一行」的可运行变异。
