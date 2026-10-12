#!/usr/bin/env bash
# getkit 依赖引导脚本（macOS / Linux）
# 用法：./setup.sh
set -euo pipefail

have() { command -v "$1" >/dev/null 2>&1; }

missing=()
have yt-dlp || missing+=(yt-dlp)
have gallery-dl || missing+=(gallery-dl)
have ffmpeg || missing+=(ffmpeg)

if [ "${#missing[@]}" -eq 0 ]; then
  echo "依赖齐全：yt-dlp / gallery-dl / ffmpeg"
  exit 0
fi
echo "缺少依赖：${missing[*]}"

confirm() {
  read -r -p "$1  [y/N] " ans
  [ "$ans" = "y" ] || [ "$ans" = "Y" ]
}

if have brew; then
  confirm "将执行：brew install ${missing[*]}" || { echo "已取消"; exit 1; }
  brew install "${missing[@]}"
elif have apt-get; then
  pip_cmd="pip3"; have pip3 || pip_cmd="pip"
  confirm "将执行：sudo apt-get install -y ffmpeg 且 ${pip_cmd} install -r requirements.txt" \
    || { echo "已取消"; exit 1; }
  have ffmpeg || sudo apt-get install -y ffmpeg
  "$pip_cmd" install -r requirements.txt
elif have dnf; then
  confirm "将执行：sudo dnf install -y ffmpeg 且 pip install -r requirements.txt" \
    || { echo "已取消"; exit 1; }
  have ffmpeg || sudo dnf install -y ffmpeg
  pip install -r requirements.txt
elif have pacman; then
  confirm "将执行：sudo pacman -S ffmpeg 且 pip install -r requirements.txt" \
    || { echo "已取消"; exit 1; }
  have ffmpeg || sudo pacman -S --noconfirm ffmpeg
  pip install -r requirements.txt
else
  echo "未识别的包管理器。请手动安装：yt-dlp、gallery-dl、ffmpeg"
  exit 1
fi

echo "完成。现在可运行：python3 get.py"
