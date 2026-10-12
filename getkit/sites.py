#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""站点识别、链接归一化，以及 yt-dlp 本地插件参数。"""

from __future__ import annotations

import os
import re
from urllib.parse import urlsplit

from .config import PLUGIN_DIR

# 站点识别
INSTAGRAM_RE = re.compile(r"https?://(?:www\.)?instagram\.com/", re.I)
DOUYIN_RE = re.compile(r"https?://(?:[\w-]+\.)?(?:douyin\.com|iesdouyin\.com)/", re.I)
XHS_RE = re.compile(r"https?://(?:www\.)?(?:xiaohongshu\.com|xhslink\.com)/", re.I)

# 用于 cookie 检测：域名（子串）-> 认证 cookie 名（命中其一即视为已登录）
SITE_AUTH: list[tuple[str, tuple[str, ...]]] = [
    ("instagram.com", ("sessionid",)),
    ("youtube.com", ("SAPISID", "SID", "SIDCC")),
    ("google.com", ("SAPISID", "SID")),
    ("bilibili.com", ("SESSDATA",)),
    ("xiaohongshu.com", ("web_session", "a1")),
    ("douyin.com", ("UIFID", "UIFID_TEMP")),
]

# 短链/别名 -> 用于 cookie 检测的真实域名
DOMAIN_ALIAS = {
    "youtu.be": "youtube.com",
    "b23.tv": "bilibili.com",
    "xhslink.com": "xiaohongshu.com",
    "v.douyin.com": "douyin.com",
    "iesdouyin.com": "douyin.com",
}


def site_of(url: str) -> str:
    """判断链接归属：instagram / douyin / xiaohongshu / ytdlp。"""
    if INSTAGRAM_RE.search(url):
        return "instagram"
    if DOUYIN_RE.search(url):
        return "douyin"
    if XHS_RE.search(url):
        return "xiaohongshu"
    return "ytdlp"


def plugin_args() -> list[str]:
    """给 yt-dlp 传本地插件目录（抖音签名修复）。"""
    if os.path.isdir(PLUGIN_DIR):
        return ["--plugin-dirs", PLUGIN_DIR]
    return []


def normalize_url(url: str) -> str:
    """把抖音「用户主页 + modal_id」形式重写成标准视频地址。"""
    if site_of(url) != "douyin":
        return url
    match = re.search(r"[?&]modal_id=(\d+)", url)
    if match:
        return f"https://www.douyin.com/video/{match.group(1)}"
    return url


# 域名 -> 归档目录名（未命中归“其它”）
SITE_FOLDERS: list[tuple[tuple[str, ...], str]] = [
    (("youtube.com", "youtu.be"), "YouTube"),
    (("bilibili.com", "b23.tv"), "Bilibili"),
    (("xiaohongshu.com", "xhslink.com"), "小红书"),
    (("instagram.com",), "Instagram"),
    (("douyin.com", "iesdouyin.com"), "抖音"),
]


def site_folder(url: str) -> str:
    """给定链接返回其归档目录名（如 YouTube / Bilibili / 抖音 / 其它）。"""
    host = urlsplit(url).netloc.lower().split("@")[-1].split(":")[0]
    if host.startswith("www."):
        host = host[4:]
    for domains, folder in SITE_FOLDERS:
        if any(host == d or host.endswith("." + d) for d in domains):
            return folder
    return "其它"
