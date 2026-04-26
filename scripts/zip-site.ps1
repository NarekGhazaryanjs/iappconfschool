# Ստեղծում է opticssymposia-site.zip — վերբեռնելու / extract cPanel-ում opticssymposia.iapp.am document root-ում։
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$out = Join-Path $Root "opticssymposia-site.zip"
if (Test-Path $out) { Remove-Item $out -Force }

$items = @(
  "index.html", "program.html", "registration.html", "history.html",
  "gallery.html", "invited-speakers.html",
  "css", "js", "downloads", ".htaccess"
)
foreach ($p in $items) {
  if (-not (Test-Path (Join-Path $Root $p))) { Write-Error "Missing: $p" }
}

Compress-Archive -Path $items -DestinationPath $out -Force
Write-Host "Created: $out" -ForegroundColor Green
