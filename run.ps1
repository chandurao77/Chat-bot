param(
    [switch]$Test,
    [switch]$Ingest,
    [switch]$Rebuild,
    [switch]$Stop,
    [switch]$Logs,
    [switch]$Status,
    [switch]$Clean
)

$BACKEND    = "http://localhost:8000"
$FRONTEND   = "http://localhost:3000"
$API_HEADER = @{ "X-API-Key" = ""; "Content-Type" = "application/json" }

function Write-Header($Text) {
    $line = "=" * 60
    Write-Host ""
    Write-Host $line -ForegroundColor Cyan
    Write-Host "  $Text" -ForegroundColor Cyan
    Write-Host $line -ForegroundColor Cyan
    Write-Host ""
}
function Write-Step($Text) { Write-Host "[*] $Text" -ForegroundColor Yellow }
function Write-OK($Text)   { Write-Host "[+] $Text" -ForegroundColor Green  }
function Write-Fail($Text) { Write-Host "[-] $Text" -ForegroundColor Red    }

function Wait-Healthy($Service, $Seconds = 60) {
    Write-Step "Waiting for $Service to be healthy..."
    $elapsed = 0
    while ($elapsed -lt $Seconds) {
        $s = docker inspect --format='{{.State.Health.Status}}' $Service 2>$null
        if ($s -eq "healthy") { Write-OK "$Service is healthy"; return $true }
        Start-Sleep 3; $elapsed += 3
        Write-Host "  ... ${elapsed}s" -ForegroundColor DarkGray
    }
    Write-Fail "$Service did not become healthy in ${Seconds}s"
    return $false
}

function Start-Stack([switch]$ForceRebuild) {
    Write-Header "Starting JARVIS"
    if ($ForceRebuild) {
        Write-Step "Rebuilding Docker images..."
        docker compose build --no-cache
        if ($LASTEXITCODE -ne 0) { Write-Fail "Build failed"; exit 1 }
        Write-OK "Build complete"
    }
    Write-Step "Starting containers..."
    docker compose up -d
    if ($LASTEXITCODE -ne 0) { Write-Fail "Failed to start containers"; exit 1 }
    Wait-Healthy "qdrant" 60 | Out-Null
    Wait-Healthy "ollama" 60 | Out-Null
    Write-Step "Waiting for backend API..."
    $tries = 0
    while ($tries -lt 20) {
        try {
            $r = Invoke-RestMethod "$BACKEND/api/health" -TimeoutSec 3 -ErrorAction Stop
            if ($r.status -eq "ok") { Write-OK "Backend is up"; break }
        } catch {}
        Start-Sleep 3; $tries++
        Write-Host "  ... attempt $tries/20" -ForegroundColor DarkGray
    }
    if ($tries -ge 20) {
        Write-Fail "Backend did not start"
        docker logs backend --tail 30
        exit 1
    }
    Write-Host ""
    Write-Host "  JARVIS is ready!" -ForegroundColor Green
    Write-Host "  Chat UI -> $FRONTEND" -ForegroundColor White
    Write-Host "  API     -> $BACKEND/docs" -ForegroundColor White
    Write-Host "  Health  -> $BACKEND/api/health" -ForegroundColor White
    Write-Host ""
}

function Invoke-Ingest {
    Write-Header "Ingesting Local Documents"
    if (Test-Path "./sample_docs") {
        Write-Step "Copying sample docs to container..."
        Get-ChildItem "./sample_docs" | ForEach-Object {
            docker cp $_.FullName backend:/local_docs/
            Write-OK "Copied $($_.Name)"
        }
    } else {
        Write-Step "No ./sample_docs folder found, skipping"
    }
    Write-Step "Triggering ingestion..."
    try {
        $r = Invoke-RestMethod -Method POST "$BACKEND/api/ingest/local" -Headers $API_HEADER
        Write-OK "Ingestion started: $($r.status)"
    } catch {
        Write-Fail "Ingestion failed: $_"
        return
    }
    Write-Step "Polling ingestion status..."
    $tries = 0
    while ($tries -lt 30) {
        Start-Sleep 3
        try {
            $s = Invoke-RestMethod "$BACKEND/api/ingest/status" -Headers $API_HEADER
            Write-Host "  running=$($s.running) progress=$($s.progress)/$($s.total)" -ForegroundColor DarkGray
            if (-not $s.running) { Write-OK "Done! $($s.total) chunks indexed"; break }
        } catch {}
        $tries++
    }
    try {
        $m = Invoke-RestMethod "$BACKEND/api/health/metrics" -Headers $API_HEADER
        Write-Host "  Indexed documents : $($m.indexed_documents)" -ForegroundColor White
        Write-Host "  Total queries     : $($m.total_queries)" -ForegroundColor White
    } catch {}
}

function Invoke-Tests {
    Write-Header "Running All Tests"
    Write-Step "Backend tests (pytest)..."
    docker compose exec backend sh -c "cd /app && python -m pytest tests/ -v --tb=short"
    if ($LASTEXITCODE -eq 0) { Write-OK "Backend tests passed" } else { Write-Fail "Backend tests failed" }
    Write-Step "Frontend tests (vitest)..."
    if (Test-Path "./frontend") {
        Push-Location frontend
        npm test -- --run
        if ($LASTEXITCODE -eq 0) { Write-OK "Frontend tests passed" } else { Write-Fail "Frontend tests failed" }
        Pop-Location
    }
}

function Show-Status {
    Write-Header "JARVIS Status"
    docker compose ps
    Write-Host ""
    foreach ($svc in @("qdrant","ollama","backend","frontend")) {
        $s = docker inspect --format='{{.State.Status}} ({{.State.Health.Status}})' $svc 2>$null
        if ($s -match "running.*healthy") { Write-OK "$svc -> $s" }
        elseif ($s -match "running")      { Write-Host "[~] $svc -> $s" -ForegroundColor Yellow }
        else                              { Write-Fail "$svc -> not running" }
    }
    Write-Host ""
    try {
        $h = Invoke-RestMethod "$BACKEND/api/health" -TimeoutSec 5
        Write-OK "API status: $($h.status)"
        $h.components.PSObject.Properties | ForEach-Object {
            $c = if ($_.Value -eq "ok") { "Green" } else { "Red" }
            Write-Host "    $($_.Name): $($_.Value)" -ForegroundColor $c
        }
        $m = Invoke-RestMethod "$BACKEND/api/health/metrics" -TimeoutSec 5
        Write-Host "  Indexed documents : $($m.indexed_documents)" -ForegroundColor White
        Write-Host "  Total queries     : $($m.total_queries)" -ForegroundColor White
    } catch {
        Write-Fail "API unreachable at $BACKEND"
    }
    Write-Host ""
    Write-Step "Ollama models:"
    docker exec ollama ollama list 2>$null
}

function Stop-Stack {
    Write-Header "Stopping JARVIS"
    docker compose down
    Write-OK "All containers stopped"
}

function Clean-Stack {
    Write-Header "Full Reset"
    $confirm = Read-Host "WARNING: Deletes ALL data. Type yes to confirm"
    if ($confirm -ne "yes") { Write-Host "Cancelled."; return }
    docker compose down -v
    Write-OK "Clean complete. Run .\run.ps1 to start fresh"
}

function Show-Logs {
    Write-Header "Live Logs (Ctrl+C to stop)"
    docker compose logs -f --tail=50
}

if ($Stop)    { Stop-Stack;  exit 0 }
if ($Clean)   { Clean-Stack; exit 0 }
if ($Logs)    { Show-Logs;   exit 0 }
if ($Status)  { Show-Status; exit 0 }
if ($Rebuild) { Start-Stack -ForceRebuild } else { Start-Stack }
if ($Ingest)  { Invoke-Ingest }
if ($Test)    { Invoke-Tests }
Write-Header "JARVIS is running at $FRONTEND"
