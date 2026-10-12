#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""交互辅助：提问、选择菜单、链接收集、序号选择与时长格式化。"""

from __future__ import annotations

import re


def ask(prompt: str, default: str = "") -> str:
    hint = f" [{default}]" if default else ""
    value = input(f"{prompt}{hint}: ").strip()
    return value if value else default


def choose(prompt: str, options: list[tuple[str, str]]) -> str:
    """options: list of (value, label)。返回所选 value。

    显示为 1、2、3... 的序号，以下三种输入都能识别（大小写不敏感）：
      - 序号：      1
      - 短代码：    chrome / mp3 / 0
      - 显示文字：  Chrome / 不使用
    """
    print(f"\n{prompt}")
    lookup: dict[str, str] = {}
    for i, (value, label) in enumerate(options, start=1):
        print(f"  {i}. {label}")
        lookup[str(i)] = value
        if value:
            lookup.setdefault(str(value).lower(), value)
        lookup.setdefault(str(label).strip().lower(), value)

    while True:
        ans = input("请选择（输入序号）: ").strip().lower()
        if ans == "":
            print("  请输入序号，例如 1")
            continue
        if ans in lookup:
            return lookup[ans]
        print(f"  输入无效，请输入 1-{len(options)} 之间的序号。")


def collect_urls() -> list[str]:
    print("\n粘贴链接，每行一个（也可一行内用空格分隔多个）；输入空行结束：")
    urls: list[str] = []
    while True:
        try:
            line = input("  > ").strip()
        except EOFError:
            break
        if not line:
            break
        urls.extend(line.split())
    return urls


def ask_selection(count: int) -> str:
    """让用户从 count 个条目中选择。返回 'all' / 'skip' / '1,3,5-8'。"""
    while True:
        ans = input("输入要下载的序号（如 1,3,5-8；all=全部；0=跳过）: ").strip().lower()
        sel = parse_selection(ans, count)
        if sel is not None:
            return sel
        print(f"  输入无效，请输入 1-{count} 范围内的序号。")


def parse_selection(text: str, count: int) -> str | None:
    """校验选择字符串，合法返回归一化结果，非法返回 None。"""
    if text in ("", "all", "a", "*"):
        return "all"
    if text in ("0", "q", "skip", "none", "no"):
        return "skip"
    norm: list[str] = []
    for part in re.split(r"[,\s]+", text):
        if not part:
            continue
        if re.fullmatch(r"\d+", part):
            if not 1 <= int(part) <= count:
                return None
            norm.append(part)
        elif re.fullmatch(r"\d+-\d+", part):
            lo, hi = (int(x) for x in part.split("-"))
            if lo < 1 or hi > count or lo > hi:
                return None
            norm.append(part)
        else:
            return None
    return ",".join(norm) if norm else None


def fmt_duration(seconds) -> str:
    if not seconds:
        return ""
    try:
        seconds = int(float(seconds))
    except (TypeError, ValueError):
        return ""
    return f"  [{seconds // 60:02d}:{seconds % 60:02d}]"
