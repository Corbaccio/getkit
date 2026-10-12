#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""外部命令执行、结果输出与批量任务执行。"""

from __future__ import annotations

import subprocess
from typing import List, Tuple

from .prompts import ask

# 单个任务：(说明, 命令行参数)
Task = Tuple[str, List[str]]


def run_command(args: list[str]) -> int:
    """执行外部命令，返回退出码。"""
    print("\n$ " + " ".join(quote(a) for a in args) + "\n")
    try:
        proc = subprocess.run(args)
        return proc.returncode
    except KeyboardInterrupt:
        print("\n[已中断]")
        return 130
    except OSError as e:
        print(f"[错误] 无法启动程序: {e}")
        return 1


def quote(arg: str) -> str:
    return f'"{arg}"' if " " in str(arg) else str(arg)


def show_result(code: int) -> None:
    if code == 0:
        print("\n[完成] 下载成功。")
    elif code == 130:
        print("\n[中断] 已取消。")
    else:
        print(f"\n[失败] 退出码 {code}，请查看上方日志排查原因。")


def run_tasks(tasks: list[Task], output_dir: str) -> None:
    """确认后逐条执行任务（yt-dlp / 抖音流程共用）。"""
    if not tasks:
        print("没有可执行的下载任务。")
        return
    print(f"\n共 {len(tasks)} 个任务，输出目录：{output_dir}")
    if ask("确认开始？(Y/n)", "Y").lower() not in ("y", "yes", ""):
        print("已取消。")
        return
    for desc, args in tasks:
        print(f"\n===== 开始：{desc} =====")
        show_result(run_command(args))


def tail(text: str | None, limit: int = 1500) -> str:
    text = (text or "").strip()
    return text[-limit:] if text else ""


def auth_hint(stderr: str | None) -> None:
    text = (stderr or "").lower()
    if any(k in text for k in ("login", "authentication", "not logged", "challenge", "rate-limit")):
        print("[建议] 该链接需要登录：请在 Chrome 登录对应网站后重试。")
    elif "expired" in text:
        print("[建议] 浏览器登录已过期：请在 Chrome 重新登录对应网站后重试。")
