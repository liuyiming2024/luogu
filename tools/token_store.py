#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""可插拔令牌库读取器 · **默认关闭、当前未接入**。

用途（第 15 条）：本人把 token 自己存进数据库，Action 从库里读，
Settings Secrets 里只需 1 个 DB 只读访问凭据（可用 GitHub 加密接口代写），
不必逐个填 5 个洛谷 Secret。

硬约束：
  - **默认关闭**：`LUOGU_TOKEN_STORE != "1"` → 返回 {}，不联网、不导入任何驱动、不打印
  - **不编造端点**：URL / DSN / 表名全部由环境变量给；没给就明确回退，不猜
  - **只补空键**：库里的值只在 os.environ 该键为空时写入，Secrets 显式给的优先
  - **绝不打印值**：日志只出现键名；异常只打印类型名（DSN 可能含口令，不外泄）
  - **不接收明文**：本文件不含任何 token；对话里也不收，由本人自行写入库

已定义两种后端（其余类型明确报「未支持」，不做成假功能）：
  supabase : LUOGU_TOKEN_SUPABASE_URL + LUOGU_TOKEN_SUPABASE_KEY + LUOGU_TOKEN_TABLE
             → PostgREST GET {url}/rest/v1/{table}?select=name,value
  sql      : LUOGU_TOKEN_DSN (postgresql:// 或 mysql://) + LUOGU_TOKEN_TABLE
             → 惰性 import psycopg / pymysql，缺依赖即回退并登记

`python3 tools/token_store.py --check` 只做契约自检，零外网。
"""
import os, sys, json, re, urllib.request, urllib.error

# 只有这些键允许从库回灌，防止库里多写字段污染运行时
ALLOWED = {
    "LUOGU_COOKIE", "LUOGU_CSRF", "LUOGU_UID",
    "LUOGU_SUBMIT_ENDPOINT", "LUOGU_IDE_ENDPOINT", "LUOGU_SUBMIT_CONSENT",
}


def enabled():
    return os.environ.get("LUOGU_TOKEN_STORE", "").strip() == "1"


def _rows_from_supabase(url, key, table):
    ep = url.rstrip("/") + "/rest/v1/" + table + "?select=name,value"
    req = urllib.request.Request(ep, headers={
        "apikey": key,
        "Authorization": "Bearer " + key,
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (local-archive-token-store)",
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read().decode("utf-8", "replace"))
    if not isinstance(data, list):
        return {}
    return {x["name"]: x["value"] for x in data
            if isinstance(x, dict) and "name" in x and "value" in x}


def _rows_from_sql(dsn, table):
    # 惰性导入：未装驱动就明确回退，不静默假装成功
    try:
        if dsn.startswith("postgresql://") or dsn.startswith("postgres://"):
            import psycopg  # noqa
            with psycopg.connect(dsn) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT name, value FROM " + table)
                    return {n: v for n, v in cur.fetchall()}
        if dsn.startswith("mysql://"):
            import pymysql  # noqa
            d = dsn[len("mysql://"):]
            # 不让 DSN 进日志；这里只解析，不打印
            from urllib.parse import urlsplit, unquote
            u = urlsplit("//" + d)
            conn = pymysql.connect(host=u.hostname, user=unquote(u.username or ""),
                                   password=unquote(u.password or ""),
                                   database=(u.path or "/").lstrip("/"),
                                   port=u.port or 3306)
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT name, value FROM " + table)
                    return {n: v for n, v in cur.fetchall()}
            finally:
                conn.close()
    except ImportError:
        raise RuntimeError("缺少数据库驱动（psycopg / pymysql），请按后端类型安装")
    raise RuntimeError("不支持的 DSN 形态（仅 postgresql:// / mysql://）")


def _safe_table(t):
    # 表名来自环境变量，仍做白名单：禁止拼接注入
    return bool(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.]*", t or ""))

def load_tokens():
    """返回 {键: 值}；默认关闭 / 未配置 / 出错 → {} 并安全回退到 Secrets。"""
    if not enabled():
        return {}
    backend = os.environ.get("LUOGU_TOKEN_BACKEND", "").strip().lower()
    table = os.environ.get("LUOGU_TOKEN_TABLE", "").strip()
    if table and not _safe_table(table):
        print("[token-store] 表名不合法，安全回退到 Secrets", flush=True)
        return {}
    try:
        if backend == "supabase":
            url = os.environ.get("LUOGU_TOKEN_SUPABASE_URL", "").strip()
            key = os.environ.get("LUOGU_TOKEN_SUPABASE_KEY", "").strip()
            if not (url and key and _safe_table(table)):
                return {}
            rows = _rows_from_supabase(url, key, table)
        elif backend == "sql":
            dsn = os.environ.get("LUOGU_TOKEN_DSN", "").strip()
            if not (dsn and _safe_table(table)):
                return {}
            rows = _rows_from_sql(dsn, table)
        elif backend:
            raise RuntimeError("未支持的后端类型")
        else:
            return {}
    except Exception as e:
        # 只打印异常类型，绝不打印消息（可能含 DSN / 口令 / 响应体）
        print("[token-store] 读取失败，安全回退到 Secrets：", type(e).__name__, flush=True)
        return {}
    return {k: str(v) for k, v in rows.items()
            if k in ALLOWED and v is not None and str(v).strip()}


def hydrate_environ():
    """只补 os.environ 里为空的键；返回补入的**键名**（不是值）。"""
    filled = []
    for k, v in load_tokens().items():
        if not os.environ.get(k, "").strip():
            os.environ[k] = v
            filled.append(k)
    return filled


def check():
    ok = True
    def t(label, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + label)
        if not cond: ok = False

    saved = {k: os.environ.pop(k, None) for k in
             ["LUOGU_TOKEN_STORE", "LUOGU_TOKEN_BACKEND", "LUOGU_TOKEN_SUPABASE_URL",
              "LUOGU_TOKEN_SUPABASE_KEY", "LUOGU_TOKEN_DSN", "LUOGU_TOKEN_TABLE"]}
    try:
        t("默认关闭：返回空、不联网", not enabled() and load_tokens() == {})
        os.environ["LUOGU_TOKEN_STORE"] = "1"
        t("开启但未配后端：仍返回空、不联网", load_tokens() == {})
        os.environ["LUOGU_TOKEN_BACKEND"] = "unknown-backend"
        t("未知后端：安全回退，不编造接口", load_tokens() == {})
        t("hydrate 只补空键（键名可核对）", hydrate_environ() == [])
    finally:
        for k, v in saved.items():
            os.environ.pop(k, None)
            if v is not None: os.environ[k] = v

    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    # 模式字面量拆写：避免自检扫描自身源码时「自命中」（同角色字样回归的坑）
    pat = (r"(supabase\.co/[a-z]|postgresql://[^\s\"']+@|"
           + "github" + "_pat_|" + "gh" + "p_)")
    t("无硬编码真实主机 / DSN / 明文", not re.search(pat, src))
    t("表名白名单：阻断拼接注入", _safe_table("luogu_tokens") and
      not _safe_table("t; DROP TABLE x") and not _safe_table(""))
    t("白名单键固定，库里多写字段不会污染", ALLOWED == {
        "LUOGU_COOKIE", "LUOGU_CSRF", "LUOGU_UID",
        "LUOGU_SUBMIT_ENDPOINT", "LUOGU_IDE_ENDPOINT", "LUOGU_SUBMIT_CONSENT"})
    print("\n结论：", "PASS · 默认关闭、回退安全、零外网、零明文" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(check())
    names = hydrate_environ()
    print("[token-store] 已从库补入键名（值不打印）：", names or "（无，走 Secrets）")
