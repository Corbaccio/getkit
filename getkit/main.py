#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""主程序：工具检查、配置加载、主菜单。"""

from __future__ import annotations

from .config import Config, ensure_output_dir
from .cookies import cookie_summary
from .flows.dispatcher import download_flow
from .settings import settings_flow
from .tools import check_tools


def startup_notice(cfg: Config) -> None:
    """首次运行的显眼提示：cookies 未启用时给出引导。"""
    if not cfg.cookies_browser:
        print("-" * 46)
        print("[提示] 当前未启用浏览器 cookies。")
        print("       Instagram / 小红书 / 抖音等需要登录态，请在「设置 → cookies」")
        print("       选择 Chrome（或其它浏览器）后再下载。")


def main() -> None:
    check_tools()
    cfg = Config.load()
    ensure_output_dir(cfg)
    startup_notice(cfg)

    while True:
        print("\n" + "=" * 46)
        print("        交互式下载器 (yt-dlp / gallery-dl)")
        print("=" * 46)
        print(f"  输出目录 : {cfg.output_dir}")
        print(f"  cookies  : {cookie_summary(cfg)}")
        print(f"  并发分片 : {cfg.concurrency}")
        print("-" * 46)
        print("  1. 开始下载")
        print("  2. 设置")
        print("  0. 退出")
        print("=" * 46)

        try:
            choice = input("请选择: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if choice == "1":
            download_flow(cfg)
        elif choice == "2":
            settings_flow(cfg)
        elif choice == "0" or choice.lower() == "q":
            break
        else:
            print("输入无效。")

    print("再见。")
