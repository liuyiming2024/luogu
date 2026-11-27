#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""只认 token 不认人 · 本地参考实现。

⚠️ 这是**接口契约的可运行样例**，供人工接入时对照；
   默认不启动、不监听公网、不持有任何真实凭据。
   启动：LUOGU_API_TOKEN=xxx python3 api/reference_server.py --port 8765
"""
import os, json, argparse, hashlib, re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

TOKEN = os.environ.get("LUOGU_API_TOKEN", "")
STORE = {}          # 内存态；接入时换成 Supabase / 本库文件
AUDIT = []

def ok(h, obj, code=200):
    h.send_response(code)
    h.send_header("Content-Type", "application/json; charset=utf-8")
    h.send_header("Access-Control-Allow-Origin", "*")
    h.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type, Idempotency-Key")
    h.end_headers()
    h.wfile.write(json.dumps(obj, ensure_ascii=False).encode())

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def _auth(self):
        # 只认 token，不认人：不查 uid、不查用户名、不查账号
        return TOKEN and self.headers.get("Authorization", "") == "Bearer " + TOKEN

    def _body(self):
        n = int(self.headers.get("Content-Length", "0") or 0)
        try: return json.loads(self.rfile.read(n) or b"{}")
        except Exception: return {}

    def do_OPTIONS(self):
        self.send_response(204); self.end_headers()

    def do_GET(self):
        u = urlparse(self.path); p = u.path
        if p == "/api/health":
            return ok(self, {"ok": True, "version": "local-luogu/1.0", "token_required": bool(TOKEN)})
        if p == "/api/articles":
            return ok(self, {"items": STORE.get("articles", [])})
        m = re.fullmatch(r"/api/article/([a-z0-9]{8})", p)
        if m:
            return ok(self, {"lid": m.group(1), "item": STORE.get("article:" + m.group(1))})
        if p == "/api/judge/cases":
            return ok(self, {"cases": STORE.get("judge_cases", [])})
        if p == "/api/mirrors":
            return ok(self, {"mirrors": STORE.get("mirrors", []),
                             "note": "内置下载功能：仅用户主动点击时探测，页面加载零外网"})
        if p == "/api/crawl/status":
            return ok(self, {"status": STORE.get("crawl", {"mode": "offline"})})
        if p.startswith("/api/"):
            if not self._auth(): return ok(self, {"error": "invalid token"}, 401)
        return ok(self, {"error": "not found"}, 404)

    def do_POST(self):
        u = urlparse(self.path); p = u.path
        if not self._auth(): return ok(self, {"error": "invalid token"}, 401)
        b = self._body()
        key = self.headers.get("Idempotency-Key") or hashlib.sha256(
            json.dumps(b, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]
        if key in STORE.get("idem", set()):
            return ok(self, {"duplicate": True, "key": key})
        STORE.setdefault("idem", set()).add(key)
        if p == "/api/comments":
            STORE.setdefault("comments", []).append(b)
            return ok(self, {"ok": True, "key": key}, 201)
        if p == "/api/comments/push-luogu":
            # 契约形状：真正发请求的是「本机代理 / 自托管 runner / 扩展」，
            # 它持有用户个人账号登录态；参考服务只入队，不碰洛谷、不持凭据。
            STORE.setdefault("push_q", []).append(dict(b, state="待推"))
            return ok(self, {"ok": True, "queued": True, "state": "待推",
                             "target": "www.luogu.com（文章评论区）",
                             "pushed": False,
                             "note": "静态站不直连洛谷：跨源+HttpOnly cookie+CSRF 不可达；本端点只入队"}, 202)
        if p == "/api/std/submit":
            STORE.setdefault("std_queue", []).append(dict(b, state="待对跑"))
            return ok(self, {"ok": True, "state": "待对跑"}, 201)
        if p == "/api/std/compare":
            # 契约：与原 std 对跑，去除 WA 与不优；真比较在 tools/ 本地执行
            return ok(self, {"ok": True, "removed_wa": [], "removed_worse": [],
                             "note": "真对跑由 tools/ 执行，此处仅返回契约形状"})
        if p == "/api/std/approve":
            return ok(self, {"ok": True, "state": "已迁入 std（需人工确认标记）"})
        if p == "/api/publish":
            if not b.get("enabled"):
                return ok(self, {"ok": False, "reason": "回推适配器默认关闭（需登录+联网+显式启用）"})
            return ok(self, {"ok": True, "queued": True, "note": "低频礼貌节奏"})
        if p == "/api/judge":
            return ok(self, {"ok": True, "verdict": "Queued", "note": "接你自己的 runner"})
        return ok(self, {"error": "not found"}, 404)

    def do_DELETE(self):
        if not self._auth(): return ok(self, {"error": "invalid token"}, 401)
        m = re.fullmatch(r"/api/resources/(.+)", urlparse(self.path).path)
        if not m: return ok(self, {"error": "not found"}, 404)
        rid = m.group(1)
        STORE.pop("article:" + rid, None)
        AUDIT.append({"id": rid, "event": "已移除", "ts": "utc"})
        self.send_response(204); self.end_headers()

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--port", type=int, default=8765)
    a = ap.parse_args()
    if not TOKEN:
        print("⚠️ 未设置 LUOGU_API_TOKEN：只开放读接口，所有写操作返回 401")
    print(f"参考服务 127.0.0.1:{a.port}（只认 token 不认人；勿直接暴露公网）")
    ThreadingHTTPServer(("127.0.0.1", a.port), H).serve_forever()

if __name__ == "__main__": main()
