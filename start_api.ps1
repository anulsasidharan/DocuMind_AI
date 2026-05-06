# DocuMind AI - API Server Startup Script
# Usage: .\start_api.ps1 [-Port 8001]
param([int]$Port = 8001)

$projectRoot = $PSScriptRoot
$envFile = Join-Path $projectRoot ".env"
$python = "C:\ProgramData\anaconda3\python.exe"

Write-Host "DocuMind AI - Starting API server on port $Port" -ForegroundColor Cyan

if (-not (Test-Path $envFile)) {
    Write-Warning ".env file not found at $envFile. Copy .env.example and fill in your keys."
    exit 1
}

# Build process with inherited env + .env overrides
$psi = [System.Diagnostics.ProcessStartInfo]::new()
$psi.FileName = $python
$psi.Arguments = "-m uvicorn api.main:app --host 0.0.0.0 --port $Port --reload"
$psi.WorkingDirectory = $projectRoot
$psi.UseShellExecute = $false

foreach ($e in [System.Environment]::GetEnvironmentVariables().GetEnumerator()) {
    if ($e.Key -and $e.Value) { try { $psi.EnvironmentVariables[$e.Key] = $e.Value } catch {} }
}
Get-Content $envFile | ForEach-Object {
    if ($_ -match '^\s*([^#=\s][^=]*?)\s*=\s*(.*)$') {
        $psi.EnvironmentVariables[$Matches[1]] = $Matches[2].Trim()
    }
}

Write-Host "API will be available at: http://localhost:$Port" -ForegroundColor Green
Write-Host "Interactive docs at: http://localhost:$Port/docs" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop.`n"

$proc = [System.Diagnostics.Process]::Start($psi)
$proc.WaitForExit()
