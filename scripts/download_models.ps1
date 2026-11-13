<#
.SYNOPSIS
  Download all models used by the 5 matting workflows into the correct ComfyUI folders.
.EXAMPLE
  powershell -ExecutionPolicy Bypass -File scripts\download_models.ps1 -ComfyUI "D:\ComfyUI-aki-v2\ComfyUI"
  powershell -ExecutionPolicy Bypass -File scripts\download_models.ps1 -ComfyUI "D:\ComfyUI" -Mirror "https://huggingface.co"
#>
param(
    [string]$ComfyUI = "D:\ComfyUI-aki-v2\ComfyUI",
    [string]$Mirror  = "https://hf-mirror.com",
    [switch]$SkipLucida,
    [switch]$SkipBiRefNet,
    [switch]$SkipInSPyReNet,
    [switch]$SkipSDMatte,
    [switch]$SkipSapiens2
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path $ComfyUI)) { throw "ComfyUI folder not found: $ComfyUI" }

function Get-File([string]$url, [string]$dest) {
    $dir = Split-Path $dest -Parent
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    if (Test-Path $dest) {
        Write-Host "[skip] exists: $dest"
        return
    }
    Write-Host "[get ] $url"
    & curl.exe -L --retry 5 --retry-delay 2 -C - --silent --show-error -o $dest $url
    if ($LASTEXITCODE -ne 0) { throw "download failed: $url" }
    $size = (Get-Item $dest).Length
    Write-Host ("[ok  ] {0}  ({1:N0} bytes)" -f $dest, $size)
}

$m = $Mirror.TrimEnd('/')

if (-not $SkipLucida) {
    Get-File "$m/Comfy-Org/BiRefNet/resolve/main/background_removal/lucida.safetensors" `
             "$ComfyUI\models\background_removal\lucida.safetensors"
}

if (-not $SkipBiRefNet) {
    $d = "$ComfyUI\models\RMBG\BiRefNet"
    foreach ($f in @("birefnet.py", "BiRefNet_config.py", "config.json", "BiRefNet-HR.safetensors")) {
        Get-File "$m/1038lab/BiRefNet/resolve/main/$f" "$d\$f"
    }
}

if (-not $SkipInSPyReNet) {
    Get-File "$m/1038lab/inspyrenet/resolve/main/inspyrenet.safetensors" `
             "$ComfyUI\models\RMBG\INSPYRENET\inspyrenet.safetensors"
}

if (-not $SkipSDMatte) {
    $d = "$ComfyUI\models\RMBG\SDMatte"
    Get-File "$m/1038lab/SDMatte/resolve/main/SDMatte.safetensors" "$d\SDMatte.safetensors"
    $comps = @{
        "scheduler"    = @("scheduler_config.json")
        "text_encoder" = @("config.json")
        "tokenizer"    = @("merges.txt", "special_tokens_map.json", "tokenizer_config.json", "vocab.json")
        "unet"         = @("config.json")
        "vae"          = @("config.json")
    }
    foreach ($c in $comps.Keys) {
        foreach ($f in $comps[$c]) {
            Get-File "$m/1038lab/SDMatte/resolve/main/$c/$f" "$d\$c\$f"
        }
    }
}

if (-not $SkipSapiens2) {
    Get-File "$m/facebook/sapiens2-matting-1b/resolve/main/model.safetensors" `
             "$ComfyUI\models\sapiens2\matting\model.safetensors"
}

Write-Host ""
Write-Host "All done. Restart ComfyUI, then open the workflow from ComfyUI/user/default/workflows/."
