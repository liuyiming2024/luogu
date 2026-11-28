#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""本地运行器：fork + os.wait4 取**单个子进程**的 rusage。

为什么不用墙钟：用户口径「不考虑评测机波动」。
  · cpu = ru_utime + ru_stime（CPU 时间，比墙钟稳定得多）
  · maxrss = ru_maxrss（该子进程峰值常驻内存，KB）
墙钟只用于超时 kill，绝不用于判优。
零外网、零第三方依赖。
"""
import os, sys, time, signal, tempfile, shutil


class CompileError(Exception):
    pass


def compile_source(src_path, lang, workdir):
    """编译 C++ / C；Python 直接解释执行。返回命令行 list。"""
    lang = (lang or "cpp").lower()
    if lang == "cpp":
        exe = os.path.join(workdir, "cand.bin")
        r = os.system('g++ -O2 -std=c++17 -o "%s" "%s" > "%s/compile.log" 2>&1'
                      % (exe, src_path, workdir))
        if r != 0 or not os.path.exists(exe):
            raise CompileError(open(os.path.join(workdir, "compile.log"),
                                    encoding="utf-8", errors="replace").read()[:400])
        return [exe]
    if lang == "c":
        exe = os.path.join(workdir, "cand.bin")
        r = os.system('gcc -O2 -o "%s" "%s" > "%s/compile.log" 2>&1'
                      % (exe, src_path, workdir))
        if r != 0 or not os.path.exists(exe):
            raise CompileError(open(os.path.join(workdir, "compile.log"),
                                    encoding="utf-8", errors="replace").read()[:400])
        return [exe]
    if lang in ("py", "python", "python3"):
        return [sys.executable, src_path]
    raise CompileError("不支持的语言: " + lang)


def normalize(s):
    """按行比对：容忍行尾空格与末尾换行差异，不容忍内容差异。"""
    return "\n".join(x.rstrip() for x in s.replace("\r\n", "\n").splitlines())


def run_case(cmd, stdin_text, timeout=5.0):
    """返回 {out, rc, cpu, maxrss, timed_out}；超时 kill，不算进 CPU 判据。"""
    with tempfile.TemporaryDirectory(prefix="stdrun_") as td:
        ip = os.path.join(td, "in"); op = os.path.join(td, "out")
        with open(ip, "w", encoding="utf-8") as f:
            f.write(stdin_text)
        fin = os.open(ip, os.O_RDONLY)
        fout = os.open(op, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        pid = os.fork()
        if pid == 0:
            try:
                os.dup2(fin, 0); os.dup2(fout, 1); os.dup2(fout, 2)
                os.close(fin); os.close(fout)
                os.execvp(cmd[0], cmd)
            except Exception:
                os._exit(127)
        os.close(fin); os.close(fout)
        t0 = time.monotonic(); ru = None; status = None; killed = False
        while True:
            wpid, st, r = os.wait4(pid, os.WNOHANG)
            if wpid == pid:
                status, ru = st, r; break
            if time.monotonic() - t0 > timeout:
                try: os.kill(pid, signal.SIGKILL)
                except ProcessLookupError: pass
                _, status, ru = os.wait4(pid, 0)
                killed = True; break
            time.sleep(0.002)
        try:
            out = open(op, encoding="utf-8", errors="replace").read()
        except OSError:
            out = ""
        rc = -9 if killed else os.waitstatus_to_exitcode(status)
        return {"out": out, "rc": rc,
                "cpu": float(ru.ru_utime + ru.ru_stime),
                "maxrss": int(ru.ru_maxrss), "timed_out": killed}
