#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抖音下载流程：单视频 / 图文图集（图片 + live 动图），可解析并挑选。"""

from __future__ import annotations

from ..config import Config
from ..cookies import cookie_args_for
from ..engines import build_common_args
from ..listing import entry_tag, ytdlp_list
from ..prompts import ask_selection, choose, fmt_duration
from ..runner import run_tasks
from ..sites import site_folder


def run(cfg: Config, urls: list[str]) -> None:
    print("\n" + "=" * 46)
    print("        抖音任务（yt-dlp + 签名插件）")
    print("=" * 46)
    mode = choose(
        "选择下载类型：",
        [
            ("1", "解析并挑选（图片 / 动图 / 视频）"),
            ("2", "全部下载"),
            ("0", "返回主菜单"),
        ],
    )
    if mode == "0":
        return

    tasks: list[tuple[str, list[str]]] = []
    for url in urls:
        # -f b：图片与视频条目都能选中；--proxy ""：系统代理会让抖音 CDN 返回 403
        common = build_common_args(cfg, playlist_ok=True) + ["-f", "b", "--proxy", ""]
        # 输出到 抖音/<作品文案>/（图集）或 抖音/（单视频），条目保留原标题
        common[common.index("-o") + 1] = (
            f"{site_folder(url)}/%(playlist_title&{{}}/|)s{cfg.filename_template}")
        cookie = cookie_args_for(cfg, url)

        if mode == "2":
            tasks.append(("全部", common + cookie + [url]))
            continue

        print(f"\n=== 条目清单（{url}）===")
        items = ytdlp_list(cfg, url)
        if not items:
            print("  未解析到任何条目，跳过。")
            continue
        if len(items) == 1:
            item = items[0]
            print(f"  {entry_tag(item)} {item['title']}{fmt_duration(item['duration'])}")
            tasks.append(("单条", common + cookie + [url]))
            continue
        for i, item in enumerate(items, start=1):
            print(f"  {i}. {entry_tag(item)} {item['title']}{fmt_duration(item['duration'])}")
        select = ask_selection(len(items))
        if select == "skip":
            continue
        args = common + cookie
        if select != "all":
            args += ["-I", select]
        tasks.append((f"挑选 {select}", args + [url]))

    run_tasks(tasks, cfg.output_dir)
