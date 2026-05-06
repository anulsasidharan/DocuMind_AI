# DocuMind AI - Streamlit UI Startup Script
# Usage: .\start_ui.ps1 [-ApiUrl http://127.0.0.1:8001]
param([string]$ApiUrl = "http://127.0.0.1:8001")

$projectRoot = $PSScriptRoot
$python = "C:\ProgramData\anaconda3\python.exe"

Write-Host "DocuMind AI - Starting Streamlit UI" -ForegroundColor Cyan
Write-Host "Connecting to API at: $ApiUrl" -ForegroundColor Green
Write-Host "UI will open at: http://localhost:8501`n"

$env:DOCUMIND_API_URL = $ApiUrl
& $python -m streamlit run "$projectRoot\ui\streamlit_app.py" --server.address 0.0.0.0 --server.port 8501
