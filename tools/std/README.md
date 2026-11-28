# tools/std · 本地 std 库与工单对跑

> 落实最终要求第 2 条：**取不到官方数据，所以使用 std 对拍**；
> std 支持工单投稿，先与原 std 多轮对跑，去除 WA 与不优的。
> 全部跑在**本地**，零外网、零登录、不刷接口；不引用不存在的官方测试数据。

## 跑一遍

```bash
python3 tools/std/verify_std.py        # 类对拍：变异必须全被抓到（零外网）
python3 tools/std/std_pipeline.py      # 工单 → 对跑 → 台账 + 期望表
python3 _build_site.py                # 把台账/期望表渲染进离线站
```

单条工单手动看结果：

```bash
python3 tools/std/std_eval.py --pid P1421 --cand tools/std/tickets/P1421_double.cpp
```

## 目录

| 文件 | 作用 |
|---|---|
| `std_bank.json` | 题库元信息（题面范围、std 路径、判优阈值） |
| `std/P*.cpp` | 三道真题的**独立正确解**（自写，不假装官方） |
| `cases.py` | 题面内输入生成器（固定 seed；题面外输入作废） |
| `runner.py` | fork + `os.wait4`：取单子进程 CPU 时间 / 峰值 RSS / 超时 kill |
| `std_eval.py` | 编译 + 多轮对跑 + 判优；产出期望输出表 |
| `std_pipeline.py` | 工单队列 → 台账 `site/data/std_candidates.json` + 期望表 |
| `verify_std.py` | 类对拍：WA / CE / RE / 不优 / 更优 / 等价 六类变异必须全被抓到 |
| `tickets/` | 示例工单（含第 7 批 double 版、第 2 批起点覆盖版） |
| `fixtures/` | 验证夹具（**不进正式题库**），用于稳定复现「明显更优/不优」 |

## 判据（写死，不随评测机波动）

- CPU 时间取 `ru_utime + ru_stime`（rusage），**不用墙钟**；墙钟只用于超时 kill
- 多轮（3 轮不同 seed）**方向一致**才认「明显更优 / 明显不优」
- 阈值 0.80 / 1.25；落在波动带 → **等价，不收**（无明显优势）
- WA / RE / TLE / CE 一律去除，首个反例留证据
- **脚本绝不产出「已迁入」**：明显更优只到「待人工审核」，本人逐条确认无错才迁入

## 与既有甲类反例的呼应

| 工单 | 对跑结果 |
|---|---|
| `P1421_double.cpp` | `7 6` 期望 `4`、实际 `3` → WA 去除（第 7 批 double 累减 1.9） |
| `P1002_start_overwrite.cpp` | `6 6 3 3` 期望 `6`、实际 `0` → WA 去除（起点赋值在 DP 之后） |
| `P1001_scanf.cpp` | 不 WA，CPU 中位数约 0.60× → 明显更优，待人工审核 |
| `BENCH_fast.cpp` | 流程演示夹具，明显更优，待人工审核 |

离线站里：`problems.html` 的「本地评测」下拉框已并入 std 期望表（共 49 个测试点），
`submit.html` 底部显示候选台账（只读）。
