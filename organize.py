#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""整理下载目录：把散落在根目录的文件按平台归档。

用法：
    python3 organize.py            # 只打印将要做的移动（dry-run）
    python3 organize.py --apply    # 真正执行移动

规则：
    1. instagram/ 等已有子目录不动（本脚本只处理根目录下的散落文件）；
    2. 文件名以 douyin-signed 开头 -> 抖音/；
    3. 去掉开头 "NN - " 与结尾 "_M" 后“文案”相同且 >=2 个文件 -> 抖音/<文案>/；
    4. 其余 -> 其它/。

只移动，不删除、不改名；目标同名时跳过并报告。
"""

from __future__ import annotations

import argparse
import os
import re
import shutil

from getkit.config import Config

_SKIP = {".DS_Store", ".gitkeep"}


def caption_of(filename: str) -> str:
    """从文件名推断“作品文案”：去掉开头序号与结尾分片号。"""
    stem = os.path.splitext(filename)[0]
    stem = re.sub(r"^\d+\s*-\s*", "", stem)
    stem = re.sub(r"_\d+$", "", stem)
    return stem.strip()


def build_plan(root: str) -> list[tuple[str, str]]:
    """返回 [(文件名, 目标子目录)]。"""
    files = [
        name for name in sorted(os.listdir(root))
        if os.path.isfile(os.path.join(root, name))
        and name not in _SKIP and not name.startswith(".")
    ]

    groups: dict[str, list[str]] = {}
    plan: list[tuple[str, str]] = []

    for name in files:
        if os.path.splitext(name)[0].lower().startswith("douyin-signed"):
            plan.append((name, "抖音"))
            continue
        groups.setdefault(caption_of(name), []).append(name)

    for caption, names in groups.items():
        target = os.path.join("抖音", caption) if len(names) >= 2 else "其它"
        for name in names:
            plan.append((name, target))

    return plan


def main() -> None:
    parser = argparse.ArgumentParser(description="按平台整理下载目录")
    parser.add_argument("--apply", action="store_true", help="真正执行移动（默认只预览）")
    args = parser.parse_args()

    root = Config.load().output_dir
    if not os.path.isdir(root):
        print(f"[错误] 目录不存在：{root}")
        return

    plan = build_plan(root)
    if not plan:
        print("没有需要整理的文件。")
        return

    print(f"{'执行' if args.apply else '预览'}整理：{root}")
    moved = skipped = 0
    for name, destdir in plan:
        src = os.path.join(root, name)
        dst = os.path.join(root, destdir, name)
        if not args.apply:
            print(f"  {name}\n    -> {destdir}/")
            continue
        if os.path.exists(dst):
            print(f"  [跳过] 目标已存在：{destdir}/{name}")
            skipped += 1
            continue
        os.makedirs(os.path.join(root, destdir), exist_ok=True)
        shutil.move(src, dst)
        moved += 1

    if args.apply:
        print(f"完成：移动 {moved} 个，跳过 {skipped} 个。")
    else:
        print("（以上为预览；加 --apply 执行）")


if __name__ == "__main__":
    main()
