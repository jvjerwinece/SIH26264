param(
  [Parameter(Mandatory=$true)][string]$In,
  [Parameter(Mandatory=$true)][string]$Out
)
$ErrorActionPreference = "Stop"
$In  = (Resolve-Path -LiteralPath $In).Path
$OutDir = Split-Path -Parent $Out
if (-not (Test-Path -LiteralPath $OutDir)) { New-Item -ItemType Directory -Path $OutDir | Out-Null }
$Out = [System.IO.Path]::GetFullPath($Out)
if (Test-Path -LiteralPath $Out) { Remove-Item -LiteralPath $Out -Force }

$app = New-Object -ComObject PowerPoint.Application
try {
  $pres = $app.Presentations.Open($In, -1, 0, -1)  # ReadOnly, Untitled=false, WithWindow=true
  try {
    $pres.SaveAs($Out, 32)  # ppSaveAsPDF
    Start-Sleep -Milliseconds 400
  } finally {
    $pres.Close()
  }
} finally {
  $app.Quit()
  [System.Runtime.Interopservices.Marshal]::ReleaseComObject($app) | Out-Null
}
if (-not (Test-Path -LiteralPath $Out)) { throw "PDF not created: $Out" }
Get-Item -LiteralPath $Out | Select-Object FullName, Length
