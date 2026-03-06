# Windows 打包脚本：严格按官方流程
# 参考 https://docs.activitywatch.net/en/latest/installing-from-source.html#packaging-your-changes
# 各子模块在各自目录内用各自的 spec 独立 package，再把 aw-qt 移到根目录，保证根目录有完整 Python 运行时（含 python310.dll），体积接近官方 ~80MB，无重复右键菜单。
#
# 使用前请：
#   1. 在仓库根目录创建并激活 venv：python -m venv venv; .\venv\Scripts\Activate.ps1
#   2. 安装依赖并构建：make build（或按文档 pip install 各子模块 + 构建 aw-server-rust）
#   3. 在仓库根目录执行：.\scripts\package\package-windows.ps1

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $RepoRoot

# 版本号（与 getversion.sh 逻辑一致，不依赖 exact-match 避免 PowerShell 报错）
$base = (git describe --tags --abbrev=0 2>&1) | Where-Object { $_ -match '^v?' }
if (-not $base) { $base = "v0.0.0" }
$commit = (git rev-parse --short HEAD 2>&1) | Where-Object { $_ -match '^[a-f0-9]+$' }
if (-not $commit) { $commit = "unknown" }
$tag = "${base}.dev-${commit}"
$version = $tag -replace '^v', ''

Write-Host "Building ActivityWatch package for Windows, version: $version"

# 清理并创建 dist/activitywatch
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
New-Item -ItemType Directory -Path "dist\activitywatch" -Force | Out-Null

# 各 Python 模块：在各自目录内执行 pyinstaller，再复制到 dist/activitywatch
$pythonModules = @(
    @{ Name = "aw-qt";      Spec = "aw-qt.spec" }
    @{ Name = "aw-server";  Spec = "aw-server.spec" }
    @{ Name = "aw-watcher-afk";    Spec = "aw-watcher-afk.spec" }
    @{ Name = "aw-watcher-window";  Spec = "aw-watcher-window.spec" }
)

foreach ($m in $pythonModules) {
    $dir = $m.Name
    $spec = $m.Spec
    Write-Host "Packaging $dir ..."
    Push-Location $dir
    try {
        pyinstaller --clean --noconfirm $spec
        if (-not (Test-Path "dist\$dir")) { throw "dist\$dir not found after pyinstaller" }
        Copy-Item -Path "dist\$dir" -Destination "..\dist\activitywatch\$dir" -Recurse -Force
    } finally {
        Pop-Location
    }
}

# aw-server-rust：cargo build 后复制到 dist/activitywatch/aw-server-rust
Write-Host "Packaging aw-server-rust ..."
Push-Location "aw-server-rust"
try {
    cargo build --release --bin aw-server --bin aw-sync
    $rustOut = "..\dist\activitywatch\aw-server-rust"
    New-Item -ItemType Directory -Path $rustOut -Force | Out-Null
    Copy-Item -Path "target\release\aw-server.exe" -Destination "$rustOut\aw-server-rust.exe" -Force
    Copy-Item -Path "target\release\aw-sync.exe" -Destination "$rustOut\aw-sync.exe" -Force
} finally {
    Pop-Location
}

# 将 aw-qt 内容移到根目录（与 Makefile 一致：mv aw-qt aw-qt-tmp; mv aw-qt-tmp/* .; rmdir aw-qt-tmp）
Write-Host "Moving aw-qt to activitywatch root ..."
$awQtDir = "dist\activitywatch\aw-qt"
$awQtTmp = "dist\activitywatch\aw-qt-tmp"
Rename-Item -Path $awQtDir -NewName "aw-qt-tmp"
Get-ChildItem -Path $awQtTmp -Force | Move-Item -Destination "dist\activitywatch" -Force
Remove-Item -Path $awQtTmp -Force -Recurse -ErrorAction SilentlyContinue

# 移除不需要的项（与 Makefile 一致，.so 仅 Linux，Windows 只删 pytz）
$pytzPath = "dist\activitywatch\pytz"
if (Test-Path $pytzPath) { Remove-Item -Recurse -Force $pytzPath }

# 打 zip
$zipName = "activitywatch-${version}-windows-$(if ($env:PROCESSOR_ARCHITEW6432 -eq 'AMD64') { 'x86_64' } else { $env:PROCESSOR_ARCHITECTURE }).zip"
Write-Host "Creating $zipName ..."
$zipPath = "dist\$zipName"
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
Compress-Archive -Path "dist\activitywatch\*" -DestinationPath $zipPath -CompressionLevel Optimal
# 修正 zip 结构：Compress-Archive 会把内容包在 activitywatch 下，而官方是 zip 内一层即 activitywatch 目录
Remove-Item $zipPath -Force
Push-Location "dist"
Compress-Archive -Path "activitywatch" -DestinationPath $zipName -CompressionLevel Optimal
Pop-Location

# Inno Setup 安装包
$iscc = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
if (Test-Path $iscc) {
    Write-Host "Building installer ..."
    $env:AW_VERSION = $version
    & $iscc "scripts\package\activitywatch-setup.iss"
    $setupName = "activitywatch-${version}-windows-$(if ($env:PROCESSOR_ARCHITEW6432 -eq 'AMD64') { 'x86_64' } else { $env:PROCESSOR_ARCHITECTURE })-setup.exe"
    if (Test-Path "dist\activitywatch-setup.exe") {
        Move-Item "dist\activitywatch-setup.exe" "dist\$setupName" -Force
        Write-Host "Installer: dist\$setupName"
    }
} else {
    Write-Host "Inno Setup 6 not found, skipping installer. Install from: https://jrsoftware.org/isinfo.php"
}

Write-Host "Done. dist\activitywatch is the runnable folder; dist\$zipName is the zip."
