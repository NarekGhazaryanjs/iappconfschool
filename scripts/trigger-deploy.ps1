# Triggers GitHub Actions CI+CD (FTP) via empty commit + push. Run:  .\scripts\trigger-deploy.ps1
# Prerequisite: git remote origin, branch main, GitHub Actions secrets (FTP_*).
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$msg = if ($args.Count -ge 1) { $args[0] } else { "chore: trigger FTP deploy" }
git commit --allow-empty -m $msg
git push origin main
$url = (git remote get-url origin) -replace '\.git$', ''
if ($url -match 'github\.com[:/](.+)$') { $url = "https://github.com/$($Matches[1])/actions" }
Write-Host "Actions: $url" -ForegroundColor Cyan
