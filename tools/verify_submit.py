#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""代提交链路的「类对拍」验证 · **零外网**。

用 127.0.0.1 上的假端点模拟 luogu，验证 `tools/luogu_submit.py`：

  1. confirmed=false → 跳过
  2. confirmed=true + dry-run → 只预览、不 POST、不改原条目
  3. confirmed=true + 假端点 → POST 成功、状态「已提交」、回写无内部字段污染
  4. 再跑一次 → 幂等，已提交条目不重复发
  5. 全程不打印 cookie，凭据不落仓库

跑法：python3 tools/verify_submit.py
临时文件用完即删；不向 luogu.com 发任何请求。
"""
import os, sys, json, time, threading, subprocess, tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(R, "site", "data", "outbox")
STATE = os.path.join(OUT, "_状态.json")
TEST = os.path.join(OUT, "verify_tmp.json")
SCRIPT = os.path.join(R, "tools", "luogu_submit.py")
received = []


class Fake(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(n).decode("utf-8"))
        received.append({"id": body.get("id"), "has_cookie": bool(self.headers.get("Cookie")),
                         "has_csrf": bool(self.headers.get("x-csrf-token"))})
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok":true}')


def run(extra_env, *args):
    env = dict(os.environ)
    env.pop("LUOGU_COOKIE", None); env.pop("LUOGU_CSRF", None)
    env.pop("LUOGU_UID", None); env.pop("LUOGU_SUBMIT_ENDPOINT", None)
    env.pop("LUOGU_IDE_ENDPOINT", None)
    env.update(extra_env)
    r = subprocess.run([sys.executable, SCRIPT, *args], cwd=R, env=env,
                       capture_output=True, text=True, timeout=60)
    return r


def main():
    os.makedirs(OUT, exist_ok=True)
    state_backup = None
    if os.path.exists(STATE):
        state_backup = open(STATE, encoding="utf-8").read()

    srv = ThreadingHTTPServer(("127.0.0.1", 0), Fake)
    port = srv.server_address[1]
    th = threading.Thread(target=srv.serve_forever, daemon=True); th.start()
    base = f"http://127.0.0.1:{port}/submit"
    ok = True

    def check(label, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + label)
        if not cond: ok = False

    try:
        def write_items():
            json.dump([
                {"id": "v-false", "kind": "comment", "lid": "sfifnfaa", "text": "跳过",
                 "confirmed": False, "state": "本地已存 · 待推"},
                {"id": "v-true", "kind": "comment", "lid": "sfifnfaa", "text": "提交",
                 "confirmed": True, "state": "本地已存 · 待推"},
            ], open(TEST, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

        # 1+2 dry-run
        write_items()
        r = run({}, "--dry-run", "--kind", "all")
        st = json.load(open(STATE, encoding="utf-8"))
        d = json.load(open(TEST, encoding="utf-8"))
        ids = [x["id"] for x in st["结果"]]
        check("dry-run：confirmed=false 跳过", "v-false" not in ids)
        check("dry-run：confirmed=true 只预览", ids == ["v-true"] and
              st["结果"][0]["state"] == "预览（未提交）")
        check("dry-run：零 POST、零状态改写", len(received) == 0 and
              st["实际发出"] == 0 and d[1]["state"] == "本地已存 · 待推")
        check("dry-run：不打印 cookie", "FAKE_COOKIE" not in r.stdout + r.stderr)

        # 3 真提交（假端点）
        received.clear(); write_items()
        env = {"LUOGU_COOKIE": "FAKE_COOKIE_NOT_REAL", "LUOGU_CSRF": "FAKE_CSRF",
               "LUOGU_UID": "0", "LUOGU_SUBMIT_ENDPOINT": base}
        r = run(env, "--kind", "all")
        st = json.load(open(STATE, encoding="utf-8"))
        d = json.load(open(TEST, encoding="utf-8"))
        check("真提交：POST 到假端点且带凭据头",
              len(received) == 1 and received[0]["has_cookie"] and received[0]["has_csrf"])
        check("真提交：状态「已提交」并回写",
              st["实际发出"] == 1 and st["结果"][0]["state"] == "已提交" and
              d[1]["state"] == "已提交")
        check("真提交：无内部字段污染", all("_file" not in x for x in d))
        check("真提交：不打印 cookie", "FAKE_COOKIE_NOT_REAL" not in r.stdout + r.stderr)

        # 4 幂等
        received.clear()
        r = run(env, "--kind", "all")
        st2 = json.load(open(STATE, encoding="utf-8"))
        check("幂等：已提交条目不重复 POST", len(received) == 0 and
              len(st2["结果"]) == 0 and st2["实际发出"] == 0)
    finally:
        srv.shutdown(); srv.server_close()
        for p in [TEST]:
            if os.path.exists(p): os.remove(p)
        if state_backup is not None:
            open(STATE, "w", encoding="utf-8").write(state_backup)

    print("\n结论：", "PASS · 代提交链路有分辨力且幂等（全程零外网）" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
