param(
    [int]$TimeoutSeconds = 180
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "[dev-start] $Message"
}

function Wait-ForDocker {
    param([int]$TimeoutSeconds)

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            docker version --format "{{.Server.Version}}" | Out-Null
            return
        }
        catch {
            Start-Sleep -Milliseconds 1000
        }
    }

    throw "Docker daemon is not available after $TimeoutSeconds seconds."
}

function Get-PublishedPortConflicts {
    param([int]$Port)

    $lines = docker ps --format "{{.Names}}|{{.Ports}}"
    if (-not $lines) {
        return @()
    }

    $conflicts = @()
    foreach ($line in $lines) {
        $parts = $line -split "\|", 2
        if ($parts.Count -ne 2) {
            continue
        }

        $name = $parts[0].Trim()
        $ports = $parts[1]
        if ($ports -match ":$Port->") {
            $conflicts += $name
        }
    }

    return $conflicts
}

function Wait-ForHealthy {
    param(
        [string]$ContainerName,
        [int]$TimeoutSeconds
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        $status = docker inspect $ContainerName --format "{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}" 2>$null
        if ($LASTEXITCODE -eq 0) {
            $trimmed = ($status | Out-String).Trim().ToLowerInvariant()
            if ($trimmed -eq "healthy" -or $trimmed -eq "running") {
                return
            }
            if ($trimmed -eq "exited" -or $trimmed -eq "dead") {
                throw "Container $ContainerName is $trimmed."
            }
        }
        Start-Sleep -Milliseconds 1000
    }

    throw "Timeout waiting for $ContainerName to become healthy."
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Push-Location $repoRoot

try {
    Write-Step "Checking Docker daemon..."
    Wait-ForDocker -TimeoutSeconds $TimeoutSeconds

    Write-Step "Precheck: resolving host port 5432 conflicts..."
    $conflicts = Get-PublishedPortConflicts -Port 5432
    $allowed = @("flezibcg-db-1")
    $toStop = @($conflicts | Where-Object { $allowed -notcontains $_ })

    if (@($toStop).Count -gt 0) {
        Write-Step "Stopping conflicting containers: $($toStop -join ', ')"
        docker stop $toStop | Out-Null
    }

    $remaining = @(Get-PublishedPortConflicts -Port 5432 | Where-Object { $_ -ne "flezibcg-db-1" })
    if (@($remaining).Count -gt 0) {
        throw "Port 5432 still in use by: $($remaining -join ', ')."
    }

    Write-Step "Starting db..."
    docker compose up -d db | Out-Null
    Wait-ForHealthy -ContainerName "flezibcg-db-1" -TimeoutSeconds $TimeoutSeconds

    Write-Step "Starting backend..."
    docker compose up -d backend | Out-Null
    Wait-ForHealthy -ContainerName "flezibcg-backend-1" -TimeoutSeconds $TimeoutSeconds

    Write-Step "Starting frontend..."
    docker compose up -d frontend | Out-Null
    Wait-ForHealthy -ContainerName "flezibcg-frontend-1" -TimeoutSeconds $TimeoutSeconds

    Write-Step "Stack is healthy."
    docker compose ps
}
catch {
    Write-Host "[dev-start] ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Step "Recent backend logs:"
    docker compose logs backend --tail=80
    throw
}
finally {
    Pop-Location
}
