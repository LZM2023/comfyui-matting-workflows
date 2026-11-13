"""Sapiens2-1B human matting node for ComfyUI.

Wraps the official inference recipe from the `facebook/sapiens2-matting`
Hugging Face Space:

    model = init_model(config, checkpoint, device)
    data  = model.data_preprocessor(model.pipeline(dict(img=image_bgr)))
    out   = model(data["inputs"])   # B x 4 x H x W: pre-multiplied fg RGB + alpha

The 4-channel output is interpolated back to the source resolution, the
pre-multiplied RGB is un-multiplied to straight (decontaminated) foreground and
returned together with the soft alpha matte.
"""

import glob
import os
import sys

import numpy as np
import torch
import torch.nn.functional as F

import folder_paths

try:  # ComfyUI runtime helpers (present in every recent ComfyUI build)
    import comfy.model_management as model_management
except Exception:  # pragma: no cover - defensive fallback
    model_management = None

NODE_DIR = os.path.dirname(os.path.abspath(__file__))
if NODE_DIR not in sys.path:
    sys.path.insert(0, NODE_DIR)

CONFIG_PATH = os.path.join(
    NODE_DIR,
    "sapiens",
    "dense",
    "configs",
    "matting",
    "gss_p3m_metasim",
    "sapiens2_1b_matting_gss_p3m_metasim-1024x768.py",
)

_MODELS_DIR = getattr(
    folder_paths, "models_dir", os.path.join(folder_paths.base_path, "models")
)
MODELS_ROOT = os.path.join(_MODELS_DIR, "sapiens2")

_PRECISIONS = ["fp32", "bf16", "fp16"]
_DEVICES = ["auto", "cuda", "cpu"]

_CACHE = {}


def _scan_models():
    files = []
    if os.path.isdir(MODELS_ROOT):
        for ext in ("*.safetensors", "*.pth", "*.bin", "*.pt"):
            files.extend(glob.glob(os.path.join(MODELS_ROOT, "**", ext), recursive=True))
    files = sorted(set(files))
    names = [os.path.relpath(p, MODELS_ROOT).replace("\\", "/") for p in files]
    return names, dict(zip(names, files))


def _pick_device(device):
    if device == "cpu":
        return torch.device("cpu")
    if device == "cuda":
        if not torch.cuda.is_available():
            raise RuntimeError("Sapiens2Matting: CUDA requested but not available.")
        return torch.device("cuda")
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _pick_dtype(precision, device):
    if device.type == "cpu":
        return torch.float32
    if precision == "fp16":
        return torch.float16
    if precision == "bf16":
        return torch.bfloat16
    return torch.float32


def _free_comfy_vram():
    """Ask ComfyUI to drop cached models so the 1.5B matting net fits."""
    if model_management is None:
        return
    try:
        model_management.unload_all_models()
    except Exception:
        pass
    try:
        model_management.soft_empty_cache()
    except Exception:
        pass


def _load_model(ckpt_path, precision, device):
    key = (ckpt_path, precision, str(device))
    cached = _CACHE.get(key)
    if cached is not None:
        return cached

    _free_comfy_vram()

    from sapiens.dense.models import init_model  # lazy: keep ComfyUI startup fast

    # init_model always builds the fp32 net on CPU first; precision conversion
    # and the H2D copy happen afterwards.
    net = init_model(CONFIG_PATH, ckpt_path, device="cpu")

    if precision == "fp16":
        net = net.half()
    elif precision == "bf16":
        net = net.bfloat16()
    else:
        net = net.float()

    net = net.to(device)
    net.eval()
    _CACHE[key] = net
    return net


def _infer_one(net, image_tensor, device, dtype):
    """image_tensor: HxWx3 float 0..1 -> (fg HxWx3, alpha HxW, rgba HxWx4)."""
    h0, w0 = int(image_tensor.shape[0]), int(image_tensor.shape[1])

    rgb8 = (
        (image_tensor[..., :3].detach().float().cpu().numpy() * 255.0 + 0.5)
        .clip(0, 255)
        .astype(np.uint8)
    )
    bgr = np.ascontiguousarray(rgb8[..., ::-1])

    data = net.pipeline(dict(img=bgr))
    data = net.data_preprocessor(data)
    x = data["inputs"]
    if x.dim() == 3:
        x = x.unsqueeze(0)
    x = x.to(device=device, dtype=dtype)

    with torch.inference_mode():
        out = net(x)

    out = F.interpolate(
        out.float(), size=(h0, w0), mode="bilinear", align_corners=False
    )
    arr = out[0].float().cpu().numpy()

    premult = np.clip(np.transpose(arr[:3], (1, 2, 0)), 0.0, 1.0)
    alpha = np.clip(arr[3], 0.0, 1.0)

    straight = np.zeros_like(premult)
    valid = alpha > 1e-4
    straight[valid] = np.clip(premult[valid] / alpha[valid][:, None], 0.0, 1.0)

    fg = torch.from_numpy(straight).float()
    mask = torch.from_numpy(alpha).float().unsqueeze(0)
    rgba = torch.cat([fg, mask[0].unsqueeze(-1)], dim=-1)
    return fg, mask, rgba


class Sapiens2Matting:
    CATEGORY = "Sapiens2"
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "MASK", "IMAGE")
    RETURN_NAMES = ("foreground", "alpha", "rgba")

    @classmethod
    def INPUT_TYPES(cls):
        names, _ = _scan_models()
        if not names:
            names = ["<missing: put model.safetensors under models/sapiens2/matting/>"]
        return {
            "required": {
                "image": ("IMAGE",),
                "model": (names,),
                "precision": (_PRECISIONS, {"default": "fp32"}),
                "device": (_DEVICES, {"default": "auto"}),
                "unload_after_run": ("BOOLEAN", {"default": False}),
            }
        }

    def run(self, image, model, precision, device, unload_after_run):
        names, paths = _scan_models()
        if model not in paths:
            raise RuntimeError(
                "Sapiens2Matting: no checkpoint found. Download "
                "facebook/sapiens2-matting-1b -> model.safetensors into "
                f"{MODELS_ROOT}\\matting\\ and refresh ComfyUI. Found: {names}"
            )

        dev = _pick_device(device)
        dtype = _pick_dtype(precision, dev)
        net = _load_model(paths[model], precision, dev)

        fgs, masks, rgbas = [], [], []
        for i in range(image.shape[0]):
            fg, mask, rgba = _infer_one(net, image[i], dev, dtype)
            fgs.append(fg)
            masks.append(mask)
            rgbas.append(rgba)

        if unload_after_run:
            _CACHE.pop((paths[model], precision, str(dev)), None)
            _free_comfy_vram()

        return (torch.stack(fgs, 0), torch.stack(masks, 0), torch.stack(rgbas, 0))


NODE_CLASS_MAPPINGS = {"Sapiens2Matting": Sapiens2Matting}
NODE_DISPLAY_NAME_MAPPINGS = {"Sapiens2Matting": "Sapiens2 Matting (Human 人像)"}
