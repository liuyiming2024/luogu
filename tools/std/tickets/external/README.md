# 外部工单（别人投稿）

「实在不行别人发工单呗」——这个目录就是入口。**不需要账号、不需要联网**：
别人把工单文件放进本目录（或提 PR），本地跑一次流水线就会自动扫描。

## 格式

一个工单 = 一个 `.json` 文件 + 一个源码文件，都放在本目录：

```json
{
  "id": "ext-001",
  "pid": "P1001",
  "file": "ext-001.cpp",
  "lang": "cpp",
  "note": "投稿说明（可选）"
}
```

| 字段 | 要求 |
|---|---|
| `id` | 唯一，建议 `ext-` 前缀 |
| `pid` | 必须在 `tools/std/std_bank.json` 题库里；不存在的题**不做 std**（先爬题面再登记） |
| `file` | 同目录下的源码文件名 |
| `lang` | `cpp` / `c` / `python` |
| `note` | 可选 |

也可以放一个 `external_index.json`（数组，多条），流水线同样识别。

## 跑

```bash
python3 tools/std/std_pipeline.py     # 自动扫描 external/ 并入台账
python3 tools/std/review.py           # 代审（证据驱动，不凭感觉）
python3 tools/std/verify_std.py       # 六类变异敏感性回归
python3 _build_site.py                # 台账上页
```

## 审核口径（重要）

- **题面闸门**：该题必须在 `site/data/problems/<PID>.json` 有可核对题面证据；
  范围引用逐字命中、题面样例实测全过、用例全在题面内。**没有题面就不做、不放**。
- **对跑**：与原 std 多轮比对，WA / RE / TLE / CE / 不优 一律去除。
- **证据等级**：检索摘录级只允许到「待题面正文复核」；
  contentOnly 正文级且审核全通过才允许迁入 std。
- 审核由本地脚本代跑，**结论带完整证据链**（sha256、每轮 ratio、样例、用例数），
  不是「觉得对就放」。
