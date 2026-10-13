"""yt-dlp plugin: 修复抖音 Douyin 下载（Argus 反爬 + 签名 + 图集）。

背景：
    抖音对 /aweme/v1/web/aweme/detail/ 接口新增了校验，缺 uifid / 签名会返回
    HTTP 403 "Blocked by ArgusSecurityPlugin ..."。此外，接口还需要一整套 web
    参数（device_platform/aid/channel/...），否则即使签名正确也会返回
    {"aweme_detail": null}（图集、较新的作品尤其明显）。

    签名算法来自 yt-dlp issue #9667（viking1304 2026-10-11 的发现）与
    Evil0ctal 的公开结论：
        query = 除签名外的全部参数（URL 编码）
        sig   = md5(f"{uifid}_{timestamp}_{SALT}_{query}")   # timestamp 留空
        SALT  = A96D855A08C0A9707F8BEF0D9A527E4E
    a_bogus 与单条作品详情接口无关，无需生成。uifid 取自浏览器 cookie。

    图集（aweme_type=68）会返回 images[]，每张图可能是 live photo（图内带视频）。
    本插件把图集展开成 playlist：图片条目 + live 动图条目，供上层选择下载。

    本插件为普通插件类（会被前置加载，优先于内置 DouyinIE），复用
    TikTokBaseIE._parse_aweme_video_app 解析视频格式。上游合并后可删除本文件。
"""

import hashlib
import urllib.parse

from yt_dlp.extractor.tiktok import DouyinIE
from yt_dlp.utils import ExtractorError, traverse_obj

_SECSDK_SALT = "A96D855A08C0A9707F8BEF0D9A527E4E"

# 抖音 web 端固定参数（缺失会导致 aweme_detail 为 null）
_WEB_PARAMS = {
    "device_platform": "webapp",
    "aid": "6383",
    "channel": "channel_pc_web",
    "pc_client_type": "1",
    "version_code": "170400",
    "version_name": "17.4.0",
    "cookie_enabled": "true",
    "screen_width": "1920",
    "screen_height": "1080",
    "browser_language": "zh-CN",
    "browser_platform": "MacIntel",
    "browser_name": "Chrome",
    "browser_version": "141.0.0.0",
    "browser_online": "true",
    "engine_name": "Blink",
    "engine_version": "141.0.0.0",
    "os_name": "Mac OS",
    "os_version": "10.15.7",
    "cpu_core_num": "8",
    "device_memory": "8",
    "platform": "PC",
    "downlink": "10",
    "effective_type": "4g",
    "round_trip_time": "50",
}

_DETAIL_HOSTS = (
    "https://www-hj.douyin.com/aweme/v1/web/aweme/detail/",
    "https://www.douyin.com/aweme/v1/web/aweme/detail/",
)

# 官方播放端点：会 302 跳到当前可用的 CDN（比第三方 douyinvod 镜像更可靠）
_DOUYIN_PLAY_PATH = "douyin.com/aweme/v1/play/"


def _dedupe_mirrors(formats):
    """每个清晰度抖音会返回多个 CDN 镜像，其中部分会 403。

    优先保留官方 play 端点（/aweme/v1/play/，会跳转到可用 CDN），丢弃其余镜像，
    避免 yt-dlp 抽到返回 403 的坏节点。
    """
    chosen = {}
    order = []
    for fmt in formats:
        fmt_id = fmt.get("format_id")
        if fmt_id not in chosen:
            chosen[fmt_id] = fmt
            order.append(fmt_id)
        if _DOUYIN_PLAY_PATH in (fmt.get("url") or ""):
            chosen[fmt_id] = fmt
    return [chosen[fmt_id] for fmt_id in order]


class DouyinSignedIE(DouyinIE):
    IE_NAME = "douyin:signed"
    _VALID_URL = r"https?://(?:www\.)?douyin\.com/(?:video|note)/(?P<id>[0-9]+)"

    # -- 签名相关 ----------------------------------------------------------

    def _uifid(self):
        cookies = self._get_cookies(self._WEBPAGE_HOST)
        for name in ("UIFID", "UIFID_TEMP"):
            cookie = cookies.get(name)
            if cookie is not None and cookie.value:
                return cookie.value
        return None

    def _signed_query(self, aweme_id):
        uifid = self._uifid()
        if not uifid:
            return None
        query = dict(_WEB_PARAMS)
        query["aweme_id"] = aweme_id
        query["uifid"] = uifid
        query_string = urllib.parse.urlencode(query)
        query["x-secsdk-web-signature"] = hashlib.md5(
            f"{uifid}__{_SECSDK_SALT}_{query_string}".encode()).hexdigest()
        return query

    def _fetch_detail(self, aweme_id):
        query = self._signed_query(aweme_id)
        headers = {
            "Referer": f"https://www.douyin.com/video/{aweme_id}",
            "Origin": "https://www.douyin.com",
        }
        filtered = False
        for host in _DETAIL_HOSTS:
            data = self._download_json(
                host, aweme_id, "Downloading signed web detail JSON",
                "Failed to download signed web detail JSON",
                query=query or {"aweme_id": aweme_id}, headers=headers, fatal=False)
            if not data:
                continue
            detail = traverse_obj(data, ("aweme_detail", {dict}))
            if detail:
                return detail
            if data.get("filter_detail") is not None:
                filtered = True
        return "filtered" if filtered else None

    # -- 图集展开 ----------------------------------------------------------

    def _image_entries(self, aweme_id, detail):
        desc = (detail.get("desc") or "").strip()
        entries = []
        images = traverse_obj(detail, ("images", ..., {dict})) or []
        for i, image in enumerate(images, start=1):
            title = f"{desc}_{i}" if desc else f"{aweme_id}_{i}"

            urls = list(dict.fromkeys(traverse_obj(image, ("url_list", ..., {str})) or []))
            formats = [{
                "format_id": "image",
                "url": image_url,
                "ext": "jpg",
                "http_headers": {"Referer": "https://www.douyin.com/"},
            } for image_url in urls]
            if formats:
                entries.append({
                    "id": f"{aweme_id}_p{i}",
                    "title": title,
                    "ext": "jpg",
                    "douyin_type": "image",
                    "formats": formats,
                })

            video = traverse_obj(image, ("video", {dict}))
            if video and traverse_obj(video, ("play_addr", "url_list", ..., {str})):
                live = self._video_info({
                    "aweme_id": f"{aweme_id}_p{i}_live",
                    "video": video,
                    "desc": title,
                })
                live["id"] = f"{aweme_id}_p{i}_live"
                live["title"] = title
                live["douyin_type"] = "live"
                entries.append(live)
        return entries

    # -- 视频格式修正 ------------------------------------------------------

    def _video_info(self, detail):
        """解析视频并把 CDN 镜像收敛到官方 play 端点，避免 403。"""
        info = self._parse_aweme_video_app(detail)
        formats = info.get("formats")
        if formats:
            fixed = []
            for fmt in _dedupe_mirrors(formats):
                headers = dict(fmt.get("http_headers") or {})
                headers.setdefault("Referer", "https://www.douyin.com/")
                fmt["http_headers"] = headers
                fixed.append(fmt)
            info["formats"] = fixed
        return info

    # -- 主入口 ------------------------------------------------------------

    def _real_extract(self, url):
        aweme_id = self._match_id(url)
        detail = self._fetch_detail(aweme_id)

        if detail == "filtered":
            raise ExtractorError(
                "该抖音作品不可用（被过滤 / 审核中 / 私密或已删除）", expected=True)
        if not detail:
            raise ExtractorError(
                "抖音签名/登录失败：需要在 Chrome 登录并访问过 douyin.com 以生成 UIFID。"
                "（若抖音已更改签名算法，请更新本插件）",
                expected=not self._get_cookies(self._WEBPAGE_HOST).get("s_v_web_id"))

        if traverse_obj(detail, ("images", ..., {dict})):
            entries = self._image_entries(aweme_id, detail)
            if entries:
                title = (detail.get("desc") or aweme_id).strip()
                return self.playlist_result(entries, aweme_id, title)

        return self._video_info(detail)
