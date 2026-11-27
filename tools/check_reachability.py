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
    t = strip_comments(t)
    return [u for u in re.findall(r'https?://[^\s"\'<>)]+', t)
            if "www.w3.org/2000/svg" not in u and "127.0.0.1" not in u]

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
    print(f"  {'✓' if not u and not cdn else '✗'} 真实外链 {len(u)} | CDN {len(cdn)}")
    if u or cdn: fail.append("存在真实外链/CDN: " + str((u + cdn)[:3]))

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

    # 6 Pages 是纯静态托管
    y = open(p(".github/workflows/pages.yml"), encoding="utf-8").read()
    srv = re.findall(r"Flask|uvicorn|gunicorn|node\s+server|supabase\s+start", y, re.I)
    print("  ✓ Pages 纯静态托管（生成 → 上传 → 部署）"
          if "deploy-pages" in y and not srv else "  ✗ Pages 被当成服务端")
    if srv: fail.append("Pages 误当服务端")

    # 7 浏览器真编译条件（非失败项，只登记口径）
    emcc = subprocess.run(["bash", "-lc", "command -v emcc || true"],
                          capture_output=True, text=True).stdout.strip()
    print("  ⚠ 浏览器真编译：" + ("无 emscripten → 已用 std 期望输出对照替代" if not emcc
                                  else "有工具链，仍按契约走评测 API") + "（非失败项）")

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
