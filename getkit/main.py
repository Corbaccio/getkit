#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""主程序：工具检查、配置加载、主菜单。"""

from __future__ import annotations

from .config import Config, ensure_output_dir
from .cookies import cookie_summary
from .flows.dispatcher import download_flow
from .settings import settings_flow
from .tools import check_tools


def main() -> None:
    check_tools()
    cfg = Config.load()
    ensure_output_dir(cfg)

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
