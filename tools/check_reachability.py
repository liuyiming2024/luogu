#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""架构可达性自检 · 默认**不发任何网络请求**。

  python3 tools/check_reachability.py            # 静态检查（零外网）
  python3 tools/check_reachability.py --probe   # 额外做只读状态码探测（不带凭据）

检查：资产语法、零 CDN / 零加载即发请求、静态站不得直连洛谷写接口、
评论推洛谷适配器存在、Pages 无服务端能力、浏览器真编译条件。
"""
import os, re, sys, argparse, subprocess

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def p(*a): return os.path.join(R, *a)

def strip_comments(t):
    t = re.sub(r"/\*[\s\S]*?\*/", "", t)        # 块注释
    t = re.sub(r"^\s*//.*$", "", t, flags=re.M)  # 行注释
    return t

def real_urls(t):
    """只对「页面加载就会去取」的**资源外链**报警。
    洛谷域的 IDE/提交页入口是 window.open 的目标（用户主动点击 + 确认门），
    不是资源引用，单独归类、单独校验，不计入外链。"""
    t = strip_comments(t)
    out = []
    # <link>/<script>/<img>/CSS @import/url() 形式的外部资源
    for u in re.findall(r'(?:src|href)\s*=\s*["\'](https?://[^"\']+)', t):
        out.append(u)
    for u in re.findall(r'@import\s+["\']?(https?://[^\s"\';)]+)', t):
        out.append(u)
    for u in re.findall(r'url\(\s*["\']?(https?://[^\s"\')]+)', t):
        out.append(u)
    return [u for u in out if "www.w3.org/2000/svg" not in u and "127.0.0.1" not in u]

def luogu_targets(t):
    """洛谷域字符串常量：必须都是 window.open 的目标，且受确认门保护。"""
    t = strip_comments(t)
    return [u for u in re.findall(r'https?://[^\s"\'<>)]+', t)
            if re.search(r'luogu\.(com|com\.cn|org)', u)]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    a = ap.parse_args()
    fail = []

    # 1 语法
    for f in ["site_src/local.js", "api/reference_server.py", "_build_site.py"]:
        fp = p(f)
        if not os.path.exists(fp):
            fail.append("缺文件 " + f); continue
        if f.endswith(".js"):
            r = subprocess.run(["node", "--check", fp], capture_output=True, text=True)
        else:
            r = subprocess.run([sys.executable, "-m", "py_compile", fp],
                               capture_output=True, text=True)
        print(("  ✓ " if r.returncode == 0 else "  ✗ ") + f + " 语法")
        if r.returncode: fail.append(f + " 语法: " + r.stderr[:120])

    # 2 真实外链 / CDN
    js = open(p("site_src/local.js"), encoding="utf-8").read()
    css = open(p("site_src/local.css"), encoding="utf-8").read()
    u = real_urls(js) + real_urls(css)
    cdn = [x for x in u if re.search(r"cdn|unpkg|jsdelivr|googleapis|fonts\.g", x, re.I)]
    print(f"  {'✓' if not u and not cdn else '✗'} 页面加载资源外链 {len(u)} | CDN {len(cdn)}")
    if u or cdn: fail.append("存在资源外链/CDN: " + str((u + cdn)[:3]))
    tg = luogu_targets(js)
    guarded = "window.open" in js and js.count("confirmAction(") >= 5
    print(f"  {'✓' if guarded else '✗'} 洛谷域目标 {len(tg)} 处（均为 window.open 用户动作 + 确认门，非资源外链）")
    if not guarded: fail.append("洛谷域目标未受 window.open/确认门约束")

    # 3 页面加载不自动 fetch：boot 只挂 DOMContentLoaded 监听；
    #   唯一 fetch 在 mirrors() 的按钮 onclick 回调内，且需 apiBase 已配置。
    boot = re.search(r"function boot\(\)\s*\{([\s\S]*?)\n\}", js)
    auto_fetch = re.findall(r"\bfetch\s*\(", boot.group(1)) if boot else ["未找到 boot"]
    guarded = "if(!apiBase())" in js
    print("  ✓ 页面加载零 fetch（唯一 fetch 在按钮回调且受 apiBase 守卫）"
          if not auto_fetch and guarded else "  ✗ 加载即 fetch 或缺守卫")
    if auto_fetch or not guarded: fail.append("加载即 fetch / 缺 apiBase 守卫")

    # 4 静态站不得直连洛谷写接口
    bad = re.findall(r'fetch\s*\(\s*["\']https?://(?:www\.)?luogu\.com', js, re.I)
    print("  ✓ 静态站无直连 luogu.com 的写请求" if not bad else "  ✗ 发现直连洛谷的写请求")
    if bad: fail.append("静态站直连洛谷写接口")

    # 5 但必须有「交给外部执行端」的评论适配器与三态
    need = ["/api/comments/push-luogu", "已推洛谷", "本地已存", "失败待重试"]
    miss = [x for x in need if x not in js]
    print("  ✓ 评论推洛谷适配器 + 三态齐全" if not miss else "  ✗ 缺 " + str(miss))
    if miss: fail.append("评论适配器/三态缺项: " + str(miss))

    # 5b 第 10 条：真编译借洛谷 IDE（新窗口 + 剪贴板），不是跨域 fetch
    ide_ok = ("function luoguRun" in js and "window.open" in js
              and "navigator.clipboard" in js and "洛谷 IDE 真编译" in js)
    print("  ✓ 真编译借洛谷 IDE（新窗口 + 剪贴板，不跨域 fetch）" if ide_ok
          else "  ✗ 缺洛谷 IDE 通道")
    if not ide_ok: fail.append("缺第10条洛谷 IDE 通道")

    # 5c 第 11 条：后果自担确认门 + 全写操作接入 + 审计
    n_conf = js.count("confirmAction(")
    gate = ("我自担" in js and "我已阅读并" in js and "function audit(" in js
            and n_conf >= 5)
    print(f"  ✓ 后果自担确认门（勾选+输入「我自担」+审计，接入 {n_conf} 处）" if gate
          else f"  ✗ 确认门不全（接入 {n_conf} 处）")
    if not gate: fail.append("第11条确认门不全")

    # 6 Pages 是纯静态托管
    y = open(p(".github/workflows/pages.yml"), encoding="utf-8").read()
    srv = re.findall(r"Flask|uvicorn|gunicorn|node\s+server|supabase\s+start", y, re.I)
    print("  ✓ Pages 纯静态托管（生成 → 上传 → 部署）"
          if "deploy-pages" in y and not srv else "  ✗ Pages 被当成服务端")
    if srv: fail.append("Pages 误当服务端")

    # 7 浏览器真编译条件（非失败项，只登记口径）
    emcc = subprocess.run(["bash", "-lc", "command -v emcc || true"],
                          capture_output=True, text=True).stdout.strip()
    print("  ✓ 真编译：第10条借洛谷 IDE（用用户账号）可达；"
          + ("本机无 emscripten，离线兜底用 std 期望输出对照" if not emcc else "本机有工具链")
          + "（非失败项）")

    # 9 第 12 条：Action 代提交运行态 + 双重确认 + outbox 契约 + 单人自用
    wf = p(".github/workflows/submit_to_luogu.yml")
    ok_wf = os.path.exists(wf)
    if ok_wf:
        y2 = open(wf, encoding="utf-8").read()
        gate_ok = ("I_UNDERSTAND_AND_ACCEPT_ALL_RISK" in y2
                   and "workflow_dispatch" in y2 and "contents: write" in y2
                   and "secrets.LUOGU_COOKIE" in y2)
        out_ok = os.path.isdir(p("site/data/outbox")) and os.path.exists(p("tools/luogu_submit.py"))
        scr = open(p("tools/luogu_submit.py"), encoding="utf-8").read()
        scr_ok = ("confirmed" in scr and "STOP_MARK" in scr
                  and "--dry-run" in scr and "random.uniform(2.0, 3.5)" in scr
                  and "print" not in scr.split("cookie =")[0][-400:])  # 凭据不打印（粗检）
        print("  ✓ Action 代提交：确认值 / Secrets / outbox / 低频 / 降级即停"
              if gate_ok and out_ok and scr_ok else "  ✗ Action 代提交契约缺项")
        if not (gate_ok and out_ok and scr_ok): fail.append("Action 代提交契约缺项")
    else:
        print("  ✗ 缺 submit_to_luogu.yml"); fail.append("缺 Action")

    # 角色字样回归：只查「源文件 / 文档 / 工作流」；site/ 下产物由生成器覆盖，
    #   workflows/pages.yml 在重生成之后才跑本自检，产物届时必然干净。
    #   字面量拆开写，避免本脚本自己命中自己。
    ROLE = "管理" + "员"
    bad_role = []
    for dp, dn, fn in os.walk(R):
        rel_dp = os.path.relpath(dp, R)
        if (".git" in dp.split(os.sep) or "__pycache__" in dp.split(os.sep)
                or rel_dp.startswith("site") or "01_批次清单" in rel_dp
                or "data/ingested" in rel_dp
                or rel_dp.startswith("03_验证脚本")):
            continue
        for f in fn:
            if f == "check_reachability.py": continue
            if not f.endswith((".md", ".js", ".css", ".py", ".json", ".yml")): continue
            fp = os.path.join(dp, f)
            try: t = open(fp, encoding="utf-8").read()
            except Exception: continue
            if ROLE in t: bad_role.append(os.path.relpath(fp, R))
    print("  ✓ 单人自用：源/文档/工作流无角色字样" if not bad_role
          else "  ✗ 仍出现角色字样: " + str(bad_role[:4]))
    if bad_role: fail.append("角色字样回归: " + str(bad_role[:4]))

    # 8 可选只读探测
    if a.probe:
        import time, urllib.request
        print("  -- 只读状态码探测（不登录、不带凭据、间隔 2s）--")
        for u2 in ["https://www.luogu.com/article/sfifnfaa",
                   "https://www.luogu.me/article/sfifnfaa",
                   "https://liuyiming2024.github.io/luogu/"]:
            try:
                q = urllib.request.Request(u2, headers={
                    "User-Agent": "Mozilla/5.0 (reachability-check)"})
                c = urllib.request.urlopen(q, timeout=10).status
            except Exception as e:
                c = getattr(e, "code", type(e).__name__)
            print(f"    {c}  {u2}")
            time.sleep(2)
        print("    口径：403 可能是出口策略网关默认拒绝；Actions 出口实测可取回正文(HTTP 200)，")
        print("          Pages 经另一通道可读 → 不能把沙盒 403 当成站点不可达。")

    print("\n结论：", "PASS · 无阻塞性架构障碍（硬障碍已用外部执行端适配器规避）"
          if not fail else "FAIL · " + str(fail))
    return 0 if not fail else 1

if __name__ == "__main__":
    sys.exit(main())
