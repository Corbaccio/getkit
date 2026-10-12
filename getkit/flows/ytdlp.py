#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""yt-dlp 下载流程：最佳画质 / 指定分辨率 / 纯音频 / 手动选格式 / 仅字幕 / 先解析再挑选。"""

from __future__ import annotations

from ..config import Config
from ..cookies import cookie_args_for
from ..engines import build_common_args
from ..listing import ytdlp_list
from ..prompts import ask, ask_selection, choose, fmt_duration
from ..sites import plugin_args, site_folder
from ..tools import YTDLP
from ..runner import run_command, run_tasks

RESOLUTIONS = [
    ("1", "2160", "4K"),
    ("2", "1440", "2K"),
    ("3", "1080", "1080p"),
    ("4", "720", "720p"),
    ("5", "480", "480p"),
    ("6", "worst", "最低画质（省流量）"),
]

AUDIO_FORMATS = [
    ("1", "mp3"),
    ("2", "m4a"),
    ("3", "flac"),
    ("4", "wav"),
    ("5", "opus"),
]


def run(cfg: Config, urls: list[str]) -> None:
    mode = choose(
        "选择下载类型：",
        [
            ("1", "最佳画质视频（自动合并音视频，输出 mp4）"),
            ("2", "指定分辨率视频"),
            ("3", "纯音频（mp3 / m4a / flac ...）"),
            ("4", "列出所有可用格式，手动选择"),
            ("5", "仅下载字幕（不下载视频）"),
            ("6", "先解析条目清单，再挑选下载"),
            ("0", "返回主菜单"),
        ],
    )
    if mode == "0":
        return

    # 是否下载整个播放列表
    if mode == "6":
        playlist_ok = True
    elif len(urls) == 1:
        answer = ask("若链接属于播放列表，是否下载整个列表？(y/N)", "N").lower()
        playlist_ok = answer in ("y", "yes")
    else:
        playlist_ok = True

    common = build_common_args(cfg, playlist_ok)

    def with_site(url: str) -> list[str]:
        """在公共参数基础上，把输出模板加上站点目录前缀。"""
        args = list(common)
        idx = args.index("-o")
        prefix = "%(playlist_index)s - " if (
            playlist_ok and "%(playlist_index)" not in cfg.filename_template) else ""
        args[idx + 1] = f"{site_folder(url)}/{prefix}{cfg.filename_template}"
        return args

    subtitle_args: list[str] = []
    if mode in ("1", "2", "4", "6"):
        answer = ask("是否同时下载字幕（含中英）？(y/N)", "N").lower()
        if answer in ("y", "yes"):
            subtitle_args = [
                "--write-subs",
                "--write-auto-subs",
                "--sub-langs", "zh-Hans,zh-CN,zh-TW,en",
                "--convert-subs", "srt",
            ]

    tasks: list[tuple[str, list[str]]] = []

    if mode == "1":
        for url in urls:
            tasks.append(("最佳画质", with_site(url) + cookie_args_for(cfg, url) + subtitle_args
                          + ["--merge-output-format", "mp4", "-f", "bv*+ba/b", url]))

    elif mode == "2":
        choice = choose("选择目标画质：", [(v, label) for v, _h, label in RESOLUTIONS])
        height = next(h for v, h, _ in RESOLUTIONS if v == choice)
        fmt = "wv*+wa/w" if height == "worst" else f"bv*[height<={height}]+ba/b[height<={height}]"
        for url in urls:
            tasks.append((f"≤{height}p", with_site(url) + cookie_args_for(cfg, url) + subtitle_args
                          + ["--merge-output-format", "mp4", "-f", fmt, url]))

    elif mode == "3":
        choice = choose("选择音频格式：", [(v, ext) for v, ext in AUDIO_FORMATS])
        audio_ext = next(ext for v, ext in AUDIO_FORMATS if v == choice)
        quality = ask("音频质量 0-9（0 最好，数字越小越好）", "0")
        for url in urls:
            tasks.append((f"音频 {audio_ext}", with_site(url) + cookie_args_for(cfg, url)
                          + ["-x", "--audio-format", audio_ext, "--audio-quality", quality, url]))

    elif mode == "4":
        for url in urls:
            print(f"\n=== 可用格式（{url}）===")
            list_args = ([YTDLP, "--list-formats", "--no-playlist"] + plugin_args()
                         + cookie_args_for(cfg, url) + [url])
            run_command(list_args)
            fid = ask("输入要下载的格式编号（如 137+140；留空跳过此链接）")
            if not fid:
                continue
            tasks.append((f"格式 {fid}", with_site(url) + cookie_args_for(cfg, url) + subtitle_args
                          + ["--merge-output-format", "mp4", "-f", fid, url]))

    elif mode == "5":
        for url in urls:
            tasks.append(("仅字幕", with_site(url) + cookie_args_for(cfg, url) + [
                "--skip-download",
                "--write-subs",
                "--write-auto-subs",
                "--sub-langs", "zh-Hans,zh-CN,zh-TW,en",
                "--convert-subs", "srt",
                url,
            ]))

    elif mode == "6":
        for url in urls:
            print(f"\n=== 条目清单（{url}）===")
            items = ytdlp_list(cfg, url)
            if not items:
                print("  未解析到任何条目，跳过。")
                continue
            head = with_site(url) + cookie_args_for(cfg, url) + subtitle_args
            if len(items) == 1:
                print(f"  单条：{items[0]['title']}{fmt_duration(items[0]['duration'])}")
                tasks.append(("条目", head + ["--merge-output-format", "mp4", "-f", "bv*+ba/b", url]))
                continue
            for i, item in enumerate(items, start=1):
                print(f"  {i}. {item['title']}{fmt_duration(item['duration'])}")
            select = ask_selection(len(items))
            if select == "skip":
                continue
            args = head + ["--merge-output-format", "mp4", "-f", "bv*+ba/b"]
            if select != "all":
                args += ["-I", select]
            tasks.append((f"挑选 {select}", args + [url]))

    run_tasks(tasks, cfg.output_dir)
