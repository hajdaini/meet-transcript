$gpuLibs = Join-Path $PSScriptRoot "gpu-libs"
if (Test-Path $gpuLibs) {
    $env:PATH = "$gpuLibs;$env:PATH"
}

if ($env:CUDA_PATH -and (Test-Path (Join-Path $env:CUDA_PATH "bin"))) {
    $env:PATH = "$(Join-Path $env:CUDA_PATH "bin");$env:PATH"
}

$cudaRoot = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA"
if (Test-Path $cudaRoot) {
    $cudaBin = Get-ChildItem $cudaRoot -Directory -Filter "v12.*" | Sort-Object Name -Descending | Select-Object -First 1
    if ($cudaBin) {
        $env:PATH = "$(Join-Path $cudaBin.FullName "bin");$env:PATH"
    }
}

$cudnnRoot = "C:\Program Files\NVIDIA\CUDNN"
if (Test-Path $cudnnRoot) {
    $cudnnBins = Get-ChildItem $cudnnRoot -Directory -Filter "v9*" | Sort-Object Name -Descending | ForEach-Object {
        Get-ChildItem $_.FullName -Recurse -Filter "cudnn_ops64_9.dll" | Select-Object -ExpandProperty DirectoryName
    }
    foreach ($bin in $cudnnBins) {
        $env:PATH = "$bin;$env:PATH"
    }
}

.\.venv\Scripts\python.exe main.py
