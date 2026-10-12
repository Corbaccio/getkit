#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""下载分发：收集链接、归一化、按站点分流到对应流程。"""

from __future__ import annotations

from ..config import Config
from ..prompts import collect_urls
from ..sites import normalize_url, site_of
from . import flow_for


def download_flow(cfg: Config) -> None:
    urls = collect_urls()
    if not urls:
        print("未输入任何链接。")
        return

    # 抖音：用户主页 + modal_id 重写为标准视频地址
    normalized = []
    for url in urls:
        new_url = normalize_url(url)
        if new_url != url:
            print(f"  [抖音] 已重写链接：{url}")
            print(f"         -> {new_url}")
        normalized.append(new_url)

    # 按站点分组，分别交给对应流程
    groups: dict[str, list[str]] = {}
    for url in normalized:
        groups.setdefault(site_of(url), []).append(url)
    for site, group in groups.items():
        flow_for(site)(cfg, group)
