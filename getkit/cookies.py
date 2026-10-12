#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cookie 来源：浏览器选择、Chrome profile 自动检测、参数拼装。"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
import time
from urllib.parse import urlsplit

from .config import Config
from .sites import DOMAIN_ALIAS, SITE_AUTH

BROWSERS = [
    ("", "不使用"),
    ("chrome", "Chrome"),
    ("safari", "Safari"),
    ("edge", "Edge"),
    ("firefox", "Firefox"),
    ("brave", "Brave"),
    ("chromium", "Chromium"),
    ("vivaldi", "Vivaldi"),
    ("opera", "Opera"),
]

def chrome_roots() -> list[str]:
    """返回当前系统下 Chrome 数据目录的候选路径。"""
    home = os.path.expanduser("~")
    if sys.platform == "darwin":
        return [os.path.join(home, "Library/Application Support/Google/Chrome")]
    if os.name == "nt":
        local = os.environ.get("LOCALAPPDATA") or os.path.join(home, "AppData", "Local")
        return [os.path.join(local, "Google", "Chrome", "User Data")]
    return [
        os.path.join(home, ".config", "google-chrome"),
        os.path.join(home, ".config", "chromium"),
        os.path.join(home, ".config", "google-chrome-beta"),
    ]


def browser_label(value: str) -> str:
    for key, label in BROWSERS:
        if key == value:
            return label
    return value or "不使用"


def cookie_spec(cfg: Config, profile: str | None = None) -> str:
    """返回 --cookies-from-browser 的取值，如 'chrome:Default'；未启用则空串。"""
    if not cfg.cookies_browser:
        return ""
    if profile is None:
        profile = cfg.cookies_profile
    return f"{cfg.cookies_browser}:{profile}" if profile else cfg.cookies_browser


def auth_domain(url: str) -> tuple[str, tuple[str, ...] | None]:
    """返回用于 cookie 检测的（域名, 认证字段）。无法识别时字段为 None。"""
    host = urlsplit(url).netloc.lower().split("@")[-1].split(":")[0]
    if host.startswith("www."):
        host = host[4:]
    host = DOMAIN_ALIAS.get(host, host)
    for domain, names in SITE_AUTH:
        if host == domain or host.endswith("." + domain):
            return domain, names
    return host, None


def _chrome_profiles() -> list[str]:
    profiles: list[str] = []
    for root in chrome_roots():
        path = os.path.join(root, "Local State")
        if not os.path.isfile(path):
            continue
        try:
            with open(path, encoding="utf-8") as f:
                info = json.load(f).get("profile", {}).get("info_cache", {})
        except (OSError, ValueError):
            continue
        for name in info:
            if name not in profiles:
                profiles.append(name)
    return profiles


def _cookie_dbs(profile: str):
    for root in chrome_roots():
        for sub in ("Cookies", "Network/Cookies"):
            path = os.path.join(root, profile, sub)
            if os.path.isfile(path):
                yield path


def _has_valid_cookie(profile: str, domain: str, names: tuple[str, ...]) -> bool:
    query = ("SELECT name, expires_utc FROM cookies WHERE host_key LIKE ? "
             "AND name IN (%s)" % ",".join("?" * len(names)))
    now = time.time()
    for db in _cookie_dbs(profile):
        try:
            con = sqlite3.connect(f"file:{db}?immutable=1", uri=True)
            try:
                rows = con.execute(query, (f"%{domain}%", *names)).fetchall()
            finally:
                con.close()
        except sqlite3.Error:
            continue
        for _name, expires_utc in rows:
            exp = expires_utc / 1e6 - 11644473600 if expires_utc else 0
            if exp == 0 or exp > now:
                return True
    return False


def pick_chrome_profile(domain: str, names: tuple[str, ...] | None) -> str | None:
    """在 Chrome 各 profile 中挑出该站点登录有效的一个。"""
    if not names:
        return None
    for profile in _chrome_profiles():
        if _has_valid_cookie(profile, domain, names):
            return profile
    return None


def cookie_args_for(cfg: Config, url: str) -> list[str]:
    """按链接决定 --cookies-from-browser 参数。"""
    if not cfg.cookies_browser:
        return []
    if cfg.cookies_browser == "chrome" and cfg.auto_profile:
        domain, names = auth_domain(url)
        profile = pick_chrome_profile(domain, names) if names else None
        if profile:
            print(f"  [cookies] {domain} 使用 Chrome profile: {profile}")
            return ["--cookies-from-browser", f"chrome:{profile}"]
        if names:
            print(f"  [cookies] 未发现 {domain} 的有效登录，回退到 profile: {cfg.cookies_profile}")
        spec = f"chrome:{cfg.cookies_profile}" if cfg.cookies_profile else "chrome"
        return ["--cookies-from-browser", spec]
    spec = cookie_spec(cfg)
    return ["--cookies-from-browser", spec] if spec else []


def cookie_summary(cfg: Config) -> str:
    """用于菜单显示的一句话 cookies 状态描述。"""
    if not cfg.cookies_browser:
        return "不使用"
    label = browser_label(cfg.cookies_browser)
    if cfg.cookies_browser == "chrome" and cfg.auto_profile:
        return f"{label}（自动选择 profile）"
    return f"{label} (profile: {cfg.cookies_profile})" if cfg.cookies_profile else label
