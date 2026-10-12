#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""设置流程：输出目录、cookies、并发、文件名模板。"""

from __future__ import annotations

import os

from .config import Config
from .cookies import BROWSERS, cookie_summary
from .prompts import ask, choose


def settings_flow(cfg: Config) -> None:
    while True:
        choice = choose(
            "设置（修改后自动保存）：",
            [
                ("1", f"输出目录：{cfg.output_dir}"),
                ("2", f"cookies：{cookie_summary(cfg)}"),
                ("3", f"并发分片数：{cfg.concurrency}"),
                ("4", f"文件名模板：{cfg.filename_template}"),
                ("0", "返回主菜单"),
            ],
        )
        if choice == "0":
            break

        if choice == "1":
            path = os.path.expanduser(ask("输入输出目录", cfg.output_dir))
            if not os.path.isdir(path):
                if ask(f"目录不存在，是否创建 {path}？(Y/n)", "Y").lower() in ("y", "yes", ""):
                    try:
                        os.makedirs(path, exist_ok=True)
                    except OSError as e:
                        print(f"  [错误] 创建失败: {e}")
                        continue
                else:
                    continue
            cfg.output_dir = path

        elif choice == "2":
            picked = choose("选择用于读取 cookies 的浏览器（登录/风控时需要）：",
                            [(v, label) for v, label in BROWSERS])
            cfg.cookies_browser = picked
            if picked == "chrome":
                auto = choose("Chrome profile 选择方式：", [
                    ("1", "自动（按站点挑选登录有效的 profile，推荐）"),
                    ("2", "手动指定"),
                ])
                if auto == "1":
                    cfg.auto_profile = True
                else:
                    cfg.auto_profile = False
                    cfg.cookies_profile = ask(
                        "浏览器 profile 名称（Chrome 通常为 Default）",
                        cfg.cookies_profile or "Default")
            elif picked:
                cfg.auto_profile = False
                cfg.cookies_profile = ask(
                    "浏览器 profile 名称（留空用默认）", cfg.cookies_profile or "")

        elif choice == "3":
            n = ask("并发分片数（1-16，越大越快但可能被限速）", str(cfg.concurrency))
            if n.isdigit() and 1 <= int(n) <= 16:
                cfg.concurrency = int(n)
            else:
                print("  输入无效。")

        elif choice == "4":
            tpl = ask("文件名模板", cfg.filename_template)
            if tpl:
                cfg.filename_template = tpl

        cfg.save()
