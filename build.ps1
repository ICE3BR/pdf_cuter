[CmdletBinding()]
param(
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$outputName = "PDF-Cuter"

Push-Location $projectRoot
try {
    $uv = Get-Command uv -ErrorAction SilentlyContinue
    if (-not $uv) {
        throw "O comando 'uv' não foi encontrado. Instale o uv ou adicione-o ao PATH."
    }

    if (-not (Test-Path -LiteralPath "main.py")) {
        throw "main.py não foi encontrado na raiz do projeto."
    }

    if ($Clean) {
        foreach ($directoryName in @("build", "dist")) {
            $directoryPath = Join-Path $projectRoot $directoryName
            if (Test-Path -LiteralPath $directoryPath) {
                Write-Host "Removendo saída anterior: $directoryName"
                Remove-Item -LiteralPath $directoryPath -Recurse -Force
            }
        }
    }

    Write-Host "Sincronizando dependências..."
    & $uv.Source sync
    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao sincronizar as dependências."
    }

    Write-Host "Compilando $outputName..."
    & $uv.Source run pyinstaller `
        --noconfirm `
        --clean `
        --windowed `
        --name $outputName `
        --collect-all tkinterdnd2 `
        main.py
    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao compilar o executável."
    }

    $executablePath = Join-Path $projectRoot "dist\$outputName\$outputName.exe"
    if (-not (Test-Path -LiteralPath $executablePath)) {
        throw "A compilação terminou, mas o executável não foi encontrado em: $executablePath"
    }

    Write-Host ""
    Write-Host "Build concluído com sucesso!" -ForegroundColor Green
    Write-Host "Executável: $executablePath"
}
finally {
    Pop-Location
}
