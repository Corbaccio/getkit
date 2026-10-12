#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""getkit —— yt-dlp / gallery-dl 交互式下载器。

模块划分：
    config    配置与路径
    sites     站点识别与链接归一化
    cookies   浏览器 cookies / Chrome profile 自动检测
    tools     外部工具定位与检查
    runner    命令执行与结果输出
    prompts   交互辅助
    listing   条目解析（列出清单）
    engines   下载命令参数构造
    flows     各站点下载流程
    settings  设置流程
    main      主菜单
"""

__version__ = "2.0.0"

from .main import main

__all__ = ["main", "__version__"]
