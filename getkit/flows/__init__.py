#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""下载流程注册表：按站点选择对应流程。"""

from __future__ import annotations

from ..config import Config
from .douyin import run as douyin_flow
from .gallery import run as gallery_flow
from .ytdlp import run as ytdlp_flow

_FLOWS = {
    "instagram": gallery_flow,
    "douyin": douyin_flow,
}


def flow_for(site: str):
    return _FLOWS.get(site, ytdlp_flow)


__all__ = ["flow_for", "ytdlp_flow", "gallery_flow", "douyin_flow"]
