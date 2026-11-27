# API 契约 · 只认 token 不认人

> **这是接口契约**，供人工接入 Supabase / Webnote / 自建 Worker。
> 仓库**不内置线上服务端**，静态 Pages 无法持有密钥。
> `api/reference_server.py` 是本地参考实现，默认不启动、不监听公网。

## 鉴权

```
Authorization: Bearer <token>
```

服务端**只校验 token 是否匹配环境变量 `LUOGU_API_TOKEN`**，
不校验自然人、不查 uid、不认账号名。token 不进仓库、不进前端代码，
只由使用者在浏览器「设置」里填入并存本地，或走 Actions secrets。

未带 / 错 token → `401 {"error":"invalid token"}`。
写操作一律要求 token；读接口默认开放（可配置为也要求 token）。

## 接口一览

| 方法 | 路径 | 说明 | 需 token |
|---|---|---|---|
| GET | `/api/health` | 存活与版本 | 否 |
| GET | `/api/articles` | 条目列表（本库数据源） | 否 |
| GET | `/api/article/:lid` | 单条文章 + 署名 + 签名 | 否 |
| GET | `/api/problems` | 题目列表 | 否 |
| GET | `/api/problems/:pid` | 题面 + 附件清单 | 否 |
| GET | `/api/problems/:pid/attachments` | 附件（按需缓存） | 否 |
| GET | `/api/judge/cases` | std 期望输出表 | 否 |
| POST | `/api/judge` | 评测（真编译，接你自己的 runner） | 是 |
| GET | `/api/comments/:lid` | 评论 | 否 |
| POST | `/api/comments` | 本地评论副本同步（可选） | 是 |
| POST | `/api/comments/push-luogu` | **评论持久化 · 直接推洛谷**：入待推队列，由外部执行端用个人账号低频推送 | 是 |
| POST | `/api/login` | cookie/账密 → 本地会话标识 | 是 |
| GET | `/api/profile` | 用户名/头像/颜色状态 | 是 |
| POST | `/api/publish` | **回推 luogu.com.cn 适配器**（默认关闭） | 是 |
| POST | `/api/std/submit` | std 工单投稿 | 是 |
| GET | `/api/std/queue` | 投稿队列 | 是 |
| POST | `/api/std/compare` | 与原 std 对跑 → 去 WA / 去不优 | 是 |
| POST | `/api/std/approve` | 人工审核无错 → 迁入 std | 是（管理员） |
| GET | `/api/search?uid=` / `?name=` | 管理员 search | 是 |
| DELETE | `/api/resources/:id` | 删资源 | 是（管理员） |
| GET | `/api/images/:sha` | 按需图片副本 | 否 |
| GET | `/api/mirrors` | 编译镜像清单（内置下载功能） | 否 |
| GET | `/api/crawl/status` | 爬取进度 / 降级状态 | 否 |

## 评论持久化 · 直接推洛谷（第 9 条口径）

**洛谷文章评论区是权威持久层，不另建评论数据库。** 流程：

```
本地先存（离线可读）→ 待推队列 → POST /api/comments/push-luogu
   → 本机代理 / 自托管 runner / 浏览器扩展（持用户个人账号登录态）
   → 低频、人工确认、可关闭 → 洛谷 → 回写「已推洛谷」
```

- 静态 Pages **绝不直接 `fetch("https://www.luogu.com/...")`**：跨源 preflight、
  HttpOnly + SameSite cookie、csrf-token 三重不可达（详见《架构可达性测试报告》）
- 用**用户个人账号**；管理员账号不参与评论
- 返回 `queued` 只表示已入队，前端状态仍是「待推」；
  只有回传 `pushed:true` / `state:"已推洛谷"` 才标成功，**不谎报**
- 失败进「失败待重试」，**不轰炸重试**；403/降级长退避
- 本地副本始终保留，保证离线可看评论

## 真编译通道 · 借洛谷 IDE（第 10 条）

**不新增评测 API 也能真编译**：前端 `luoguRun()` 在用户联网且已登录时，
`window.open()` 打开**洛谷域下**的 IDE / 题目提交页（同源，登录态自动生效），
代码经剪贴板粘贴，由洛谷自己的 IDE 编译。静态站：

- 不 `fetch` 洛谷、不读 cookie、不调洛谷内部 API（入口 URL 由用户自行确认）
- 打开前必须过第 11 条确认门
- 离线时回退 `site/data/judge_cases.json` 的 std 期望输出对照

若以后要**程序化一键提交**，需扩展 / 本机代理持有登录态，那是另一个执行端，
接口形态仍走本节契约，不在当前静态站范围内。

## 约定

- 所有写操作**幂等**：带 `Idempotency-Key` 或内容 sha，重复提交不产生副本
- 时间统一 ISO8601 UTC；内容一律带 `sha256` 与 `original_url`
- 删除资源：`204` + 写一条「已移除」审计（对应隐私声明「源已删则本地也删」）
- `/api/publish` 只在「已登录 + 联网 + 显式启用」时调用；
  适配器内部仍走低频礼貌节奏，失败不重试轰炸
- 前端 `assets/local.js` 未配置 `apiBase` 时**全部走本地 localStorage**，
  零网络请求；配置了才按上表调用

## 版权

接口只传输本库自己维护的数据与使用者自己的投稿；
原文正文保留 `original_url` / `author` / `signature`，不改写、不去署名。
