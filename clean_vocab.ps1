# ASUS Smart Input - 詞庫前置清理腳本
# 功能：過濾詞長 (2~9字)、去重、限制總量在 2,500 筆以內，輸出為純 UTF-8 (無 BOM)

param (
    [string]$InputPath = "$PWD\raw_words.txt",
    [string]$OutputPath = "$PWD\a.txt",
    [int]$MaxCount = 2200
)

if (-not (Test-Path $InputPath)) {
    Write-Error "找不到來源檔案：$InputPath，請確認檔案存在。"
    exit 1
}

Write-Host "正在讀取並清理：$InputPath..."

$cleaned = Get-Content -Path $InputPath -Encoding UTF8 |
    ForEach-Object { $_.Trim() } |
    Where-Object { $_.Length -ge 2 -and $_.Length -le 9 } |
    Select-Object -Unique |
    Select-Object -First $MaxCount

[System.IO.File]::WriteAllLines($OutputPath, $cleaned, [System.Text.UTF8Encoding]::new($false))

Write-Host "清理完成！產出檔案：$OutputPath，有效詞彙筆數：$($cleaned.Count)"
