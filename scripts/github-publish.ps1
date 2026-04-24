# Creates the GitHub repo and pushes (run:  cd project root,  .\scripts\github-publish.ps1 )
# One-time prerequisite:  gh auth login
$ErrorActionPreference = "Stop"
$RepoName = "iappconfschool"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$gh = "${env:ProgramFiles}\GitHub CLI\gh.exe"
if (-not (Test-Path $gh)) {
  Write-Error "GitHub CLI not found. Install: winget install GitHub.cli"
}

& $gh auth status *> $null
if ($LASTEXITCODE -ne 0) {
  Write-Host "Run once in this terminal to sign in to GitHub:" -ForegroundColor Yellow
  Write-Host "  & `"$gh`" auth login -h github.com" -ForegroundColor Cyan
  exit 1
}

$hasOrigin = $false
git remote get-url origin *> $null
if ($LASTEXITCODE -eq 0) { $hasOrigin = $true }

if ($hasOrigin) {
  Write-Host "Remote origin:" (git remote get-url origin)
  git push -u origin main
  exit $LASTEXITCODE
}

& $gh repo create $RepoName --public --source . --remote origin --description "OPTICS-15 / ASRP-BRIA 2026 static site" --push
if ($LASTEXITCODE -ne 0) {
  Write-Host "If the repository name is taken, change `$RepoName in scripts\github-publish.ps1 or run:" -ForegroundColor Yellow
  Write-Host "  gh repo create YOUR-NAME --public --source . --remote origin --push" -ForegroundColor Cyan
  exit $LASTEXITCODE
}

try {
  $j = & $gh repo view --json url 2>$null | ConvertFrom-Json
  if ($j.url) { Write-Host "Repository: $($j.url)" -ForegroundColor Green }
} catch { }
