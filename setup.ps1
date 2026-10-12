# getkit 依赖引导脚本（Windows）
# 用法：powershell -ExecutionPolicy Bypass -File setup.ps1

function Have($name) { return [bool](Get-Command $name -ErrorAction SilentlyContinue) }

$missing = @()
foreach ($t in @("yt-dlp", "gallery-dl", "ffmpeg")) {
  if (-not (Have $t)) { $missing += $t }
}

if ($missing.Count -eq 0) {
  Write-Host "依赖齐全：yt-dlp / gallery-dl / ffmpeg"
  exit 0
}
Write-Host ("缺少依赖: " + ($missing -join ", "))

$ans = Read-Host "安装依赖？[y/N]"
if ($ans -notin @("y", "Y")) { Write-Host "已取消"; exit 1 }

if (Have winget) {
  if ($missing -contains "yt-dlp") { winget install -e --id yt-dlp.yt-dlp }
  if ($missing -contains "ffmpeg") { winget install -e --id Gyan.FFmpeg }
} else {
  Write-Host "未找到 winget，ffmpeg 需手动安装。"
}

if ($missing -contains "gallery-dl" -or $missing -contains "yt-dlp") {
  if (Have pip) { pip install -r requirements.txt }
  elseif (Have python) { python -m pip install -r requirements.txt }
}

Write-Host "完成。现在可运行: python get.py"
