#!/usr/bin/env bash
# Download all models used by the 5 matting workflows into the correct ComfyUI folders.
# Usage: COMFYUI=/path/to/ComfyUI MIRROR=https://hf-mirror.com bash scripts/download_models.sh
set -euo pipefail
COMFYUI="${COMFYUI:-$HOME/ComfyUI}"
MIRROR="${MIRROR:-https://hf-mirror.com}"
M="${MIRROR%/}"

get() {
  local url="$1" dest="$2"
  mkdir -p "$(dirname "$dest")"
  if [ -f "$dest" ]; then echo "[skip] $dest"; return; fi
  echo "[get ] $url"
  curl -L --retry 5 --retry-delay 2 -C - --silent --show-error -o "$dest" "$url"
  echo "[ok  ] $dest ($(stat -c%s "$dest" 2>/dev/null || stat -f%z "$dest") bytes)"
}

get "$M/Comfy-Org/BiRefNet/resolve/main/background_removal/lucida.safetensors" "$COMFYUI/models/background_removal/lucida.safetensors"

for f in birefnet.py BiRefNet_config.py config.json BiRefNet-HR.safetensors; do
  get "$M/1038lab/BiRefNet/resolve/main/$f" "$COMFYUI/models/RMBG/BiRefNet/$f"
done

get "$M/1038lab/inspyrenet/resolve/main/inspyrenet.safetensors" "$COMFYUI/models/RMBG/INSPYRENET/inspyrenet.safetensors"

get "$M/1038lab/SDMatte/resolve/main/SDMatte.safetensors" "$COMFYUI/models/RMBG/SDMatte/SDMatte.safetensors"
for c in scheduler text_encoder tokenizer unet vae; do
  case "$c" in
    scheduler) files="scheduler_config.json" ;;
    text_encoder) files="config.json" ;;
    tokenizer) files="merges.txt special_tokens_map.json tokenizer_config.json vocab.json" ;;
    unet) files="config.json" ;;
    vae) files="config.json" ;;
  esac
  for f in $files; do
    get "$M/1038lab/SDMatte/resolve/main/$c/$f" "$COMFYUI/models/RMBG/SDMatte/$c/$f"
  done
done

get "$M/facebook/sapiens2-matting-1b/resolve/main/model.safetensors" "$COMFYUI/models/sapiens2/matting/model.safetensors"

echo "All done. Restart ComfyUI, then open the workflow from ComfyUI/user/default/workflows/."
