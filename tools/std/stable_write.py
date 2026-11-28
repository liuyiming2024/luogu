#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""台账稳定写盘：内容没变就不写文件（差值推送的核心）。

用户口径：「不要创造无用的提交历史」「能不能差值推送」。
派生台账（候选 / 审核 / 期望表 / 朴素对拍）每次重跑都会带新的
`checked_at` / `生成时间` 时间戳，导致 git 里出现「内容一样、只有时间变了」的
无用 diff，进而触发 Pages 与提交。这里按**剥离时间类元数据后的内容**比对：
  · 内容未变 → 不写盘，保留原文件（时间戳也保持原值）
  · 内容真变了 → 才写盘并允许更新时间
"""
import os, json

TIME_KEYS = {"生成时间", "审核时间", "checked_at", "时间", "取回时间",
             "迁入时间", "checkedAt", "generated_at"}


def strip_times(o):
    if isinstance(o, dict):
        return {k: strip_times(v) for k, v in o.items() if k not in TIME_KEYS}
    if isinstance(o, list):
        return [strip_times(x) for x in o]
    return o


def stable_write(path, doc):
    """返回 True=写了新内容 / False=内容未变跳过写入。"""
    try:
        if os.path.exists(path):
            old = json.load(open(path, encoding="utf-8"))
            if strip_times(old) == strip_times(doc):
                return False
    except Exception:
        pass
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(doc, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return True
