# 排错

## 1. 合成后主体透明、背景还在

`Join Image with Alpha` 的 MASK 语义是「透明度」，而抠图模型输出「白=主体」。
在 Join 之前加 `Invert Mask`（五个工作流已加好）。

## 2. 背景有灰雾 / 有小碎块

用 `Mask Cleanup`：
- `threshold` 0.06–0.12（商品图），0 = 保留软边（人像/发丝）
- `min_area_percent` 0.03–0.1 去孤岛
- `erode_px` 1 去边缘光晕
- `feather_px` 1 羽化

## 3. 抠图模型节点里找不到模型

确认文件放在文档指定的目录，且文件名完全一致（大小写敏感）。
- BiRefNet 需要同目录下 `birefnet.py`、`BiRefNet_config.py`、`config.json`、`BiRefNet-HR.safetensors`
- SDMatte 组件目录（scheduler/text_encoder/tokenizer/unet/vae）不能为空
- Sapiens2 需要 `models/sapiens2/matting/model.safetensors`

## 4. 启动器自动升级 transformers 导致 QwenVL / Florence-2 报错

部分启动器启动时会执行 `pip install -r custom_nodes/*/requirements.txt`，
ComfyUI-RMBG 的 requirements 未锁版本，可能把 transformers 升到 5.x。

回滚命令（本机验证版本）：

```powershell
D:\ComfyUI-aki-v2\python\python.exe -m pip install --no-deps --force-reinstall `
  transformers==4.57.3 tokenizers==0.22.1 huggingface-hub==0.34.4 `
  safetensors==0.5.3 datasets==4.4.1
```

或使用 `scripts/requirements-rmbg-safe.txt` 安装 RMBG 依赖（带版本上限）。

## 5. InSPyReNet 很慢

`process_res` 从 2048 降到 1024（实测 221 秒 → 4.1 秒）。

## 6. 显存不足

- BiRefNet-HR + SDMatte 同时加载约 5.6GB+；24GB 卡正常
- 在节点上打开 `unload_model`，或降低 `process_res`
- Sapiens2 fp32 约 6.2GB 权重；不够就换 bf16
