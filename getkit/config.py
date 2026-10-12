#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""配置：路径常量、Config 数据类、读写与输出目录准备。"""

from __future__ import annotations

import dataclasses
import json
import os
from dataclasses import dataclass, field
from typing import Any

# 项目根目录（get.py 所在目录），getkit 位于其下
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "get_config.json")
PLUGIN_DIR = os.path.join(BASE_DIR, "plugins")


def default_output_dir() -> str:
    return os.path.join(BASE_DIR, "Arsenal")


@dataclass
class Config:
    """用户偏好，序列化到 get_config.json（键名与旧版保持兼容）。"""

    output_dir: str = field(default_factory=default_output_dir)
    cookies_browser: str = ""          # 空 = 不使用 cookies
    cookies_profile: str = "Default"   # 手动模式下的浏览器 profile
    auto_profile: bool = True          # True = 按站点自动挑选登录有效的 Chrome profile
    concurrency: int = 4               # 并发分片数
    filename_template: str = "%(title)s.%(ext)s"

    @classmethod
    def load(cls) -> "Config":
        data: dict[str, Any] = {}
        if os.path.isfile(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, encoding="utf-8") as f:
                    data = json.load(f)
            except (OSError, ValueError):
                print("  [警告] 配置文件读取失败，已使用默认设置。")
        names = {f.name for f in dataclasses.fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in names})

    def save(self) -> None:
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(dataclasses.asdict(self), f, ensure_ascii=False, indent=2)
        except OSError as e:
            print(f"  [警告] 配置保存失败: {e}")


def ensure_output_dir(cfg: Config) -> None:
    if os.path.isdir(cfg.output_dir):
        return
    try:
        os.makedirs(cfg.output_dir, exist_ok=True)
        print(f"[提示] 已自动创建输出目录：{cfg.output_dir}")
    except OSError as e:
        print(f"[警告] 输出目录创建失败：{e}")
