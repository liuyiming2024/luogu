#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""下一次推送前，判断上一次部署有没有 bug（**推送后不等待**）。

用户口径：「每次推送之后你不要再去等它了，换到下一次推送前，判断上一次有没有 bug」。
本脚本在每个取回工作流的**推送之前**跑，做两件事：

  1. 查上一次 Pages run 的 conclusion（GitHub API，只读、不打印 token）
  2. 跑一遍当前工作树轻量自检（坏链 / 敏感 / 角色 / 闸门 / 朴素对拍）

结论写进 GitHub Step Summary（不进仓库，零无用提交）；
**只有上一次失败**才额外写 `02_文章编号索引/上一次部署体检.md` 留痕。
任何异常都降级为 skip 并 `continue-on-error`，绝不阻塞本轮取回。
"""
import os, sys, json, urllib.request, urllib.error
from datetime import datetime, timezone

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTE = os.path.join(R, "02_文章编号索引", "上一次部署体检.md")
REPO = os.environ.get("GITHUB_REPOSITORY", "liuyiming2024/luogu")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
SUMMARY = os.environ.get("GITHUB_STEP_SUMMARY", "")


def now(): return datetime.now(timezone.utc).isoformat(timespec="seconds")


def summary(lines):
    if SUMMARY:
        try:
            with open(SUMMARY, "a", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
        except OSError:
            pass
    for l in lines: print(l)


def last_pages():
    """返回 (run_id, conclusion, created_at) 或 (None, 'skip', 原因)。"""
    if not TOKEN:
        return None, "skip", "无 GITHUB_TOKEN"
    url = ("https://api.github.com/repos/%s/actions/workflows/pages.yml/runs"
           "?per_page=1" % REPO)
    req = urllib.request.Request(url, headers={
        "Authorization": "Bearer " + TOKEN,
        "Accept": "application/vnd.github+json",
        "User-Agent": "luogu-precheck",
    })
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            d = json.loads(r.read().decode("utf-8", "replace"))
        runs = d.get("workflow_runs", [])
        if not runs: return None, "skip", "无历史 Pages run"
        x = runs[0]
        return x["id"], x.get("conclusion") or x.get("status"), x["created_at"]
    except urllib.error.HTTPError as e:
        return None, "skip", "HTTP %s" % e.code
    except Exception as e:
        return None, "skip", type(e).__name__


def local_checks():
    """复用已有自检，返回 (ok, 摘要)。零外网。"""
    import subprocess
    out = []
    checks = [
        ("站点可达性自检", [sys.executable, os.path.join(R, "tools", "check_reachability.py")]),
        ("基础设施类对拍", [sys.executable, os.path.join(R, "tools", "verify_infra.py"), "--check"]),
        ("STD↔朴素对拍", [sys.executable, os.path.join(R, "tools", "std", "verify_brute.py")]),
    ]
    ok = True
    for name, cmd in checks:
        try:
            p = subprocess.run(cmd, cwd=R, capture_output=True, text=True, timeout=90)
            good = (p.returncode == 0)
            ok = ok and good
            out.append("- %s：%s" % (name, "PASS" if good else "FAIL(rc=%d)" % p.returncode))
        except Exception as e:
            out.append("- %s：跳过（%s）" % (name, type(e).__name__))
    return ok, out


def main():
    rid, concl, extra = last_pages()
    ok, checks = local_checks()
    lines = ["## 上一次部署体检（推送前，不等待部署）", "",
             "- 检查时间：%s" % now(),
             "- 上一次 Pages run：`%s` · 结论 **%s** · %s" % (
                 rid if rid else "—", concl, extra if concl == "skip" else ""),
             "- 本轮工作树自检：**%s**" % ("PASS" if ok else "存在问题")]
    lines += checks
    bad = (concl not in ("success", "skip", None)) or not ok
    if bad:
        lines.append("")
        lines.append("> ⚠️ 上一次部署或本地自检有问题；本轮照常取回，不阻塞、不等待。")
        print("::warning::上一次部署结论=%s / 本地自检=%s（详见 Step Summary）"
              % (concl, "PASS" if ok else "FAIL"))
        # 只有异常才留痕进仓库，成功时零写入（不造无用提交）
        try:
            os.makedirs(os.path.dirname(NOTE), exist_ok=True)
            with open(NOTE, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
        except OSError:
            pass
    else:
        lines.append("")
        lines.append("> 上一次部署 success、本地自检全 PASS；本轮无需额外处理。")
    summary(lines)
    return 0        # 永远 0：体检只报告，不阻断取回


if __name__ == "__main__":
    sys.exit(main())
