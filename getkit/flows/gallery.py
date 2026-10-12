#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Instagram 下载流程（gallery-dl）：图片 / 视频 / 列清单挑选。"""

from __future__ import annotations

from ..config import Config
from ..engines import build_gallery_args
from ..listing import IMAGE_FILTER, VIDEO_FILTER, gallerydl_list, print_gallery_items
from ..prompts import ask_selection, choose
from ..runner import run_command, show_result
from ..tools import GALLERY_DL


def run(cfg: Config, urls: list[str]) -> None:
    print("\n" + "=" * 46)
    print("        Instagram 任务（gallery-dl）")
    print("=" * 46)
    if GALLERY_DL is None:
        print("[错误] 未安装 gallery-dl，无法下载 Instagram。请执行：brew install gallery-dl")
        return

    mode = choose(
        "选择下载类型：",
        [
            ("1", "图片 + 视频（全部原始画质）"),
            ("2", "仅视频"),
            ("3", "仅图片"),
            ("4", "先列出媒体清单，手动挑选"),
            ("0", "跳过"),
        ],
    )
    if mode == "0":
        return

    filter_expr = None
    if mode == "2":
        filter_expr = VIDEO_FILTER
    elif mode == "3":
        filter_expr = IMAGE_FILTER

    for url in urls:
        select = None
        if mode == "4":
            print(f"\n=== 媒体清单（{url}）===")
            items = gallerydl_list(cfg, url)
            if not items:
                print("  未解析到任何媒体，跳过。")
                continue
            print_gallery_items(items)
            select = ask_selection(len(items))
            if select == "skip":
                continue

        args = build_gallery_args(cfg, url)
        if filter_expr:
            args += ["--filter", filter_expr]
        if select and select != "all":
            args += ["--range", select]
        args.append(url)

        print("\n===== 开始：Instagram =====")
        show_result(run_command(args))
