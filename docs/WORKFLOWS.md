# 工作流说明

## 通用结构

```
Load Image
   └─► 抠图模型（输出 MASK）
          └─► Mask Cleanup（阈值/去孤岛/去边/羽化）
                 ├─► Invert Mask ─► Join Image with Alpha（原图）─► Save Image（透明 RGBA）
                 └─► Mask To Image ─► Save Image（mask）
```

> ComfyUI 的 `Join Image with Alpha` 把 MASK 当「透明度」用，抠图模型输出的是「白=主体」，
> 所以合成前必须 `Invert Mask`。五个工作流都已接好，不要拆掉。

## 1. Lucida 抠图（BiRefNet）

- 节点：核心 `Load Background Removal Model` + `Remove Background`（+ Invert/Join/Save）
- 模型：`models/background_removal/lucida.safetensors`
- 参数：`bg_removal_name = lucida.safetensors`
- 适合：玻璃/透明、文字 logo、插画、印花贴纸
- 注意：核心节点会把图拉伸到 1024×1024 再推理，大图细节有限；商品图更推荐 BiRefNet-HR 工作流

## 2. Sapiens2 人像抠图（软 alpha）

- 节点：仓库附带 `ComfyUI-Sapiens2-Matting`（`Sapiens2 Matting (Human 人像)`）
- 模型：`models/sapiens2/matting/model.safetensors`
- 参数：`precision = fp32`（默认）/ bf16 / fp16
- 适合：人像、模特、发丝、半透明边缘
- 注意：只对人有效；输入固定 1024×768 竖构图；首次跑会加载 6.16GB

## 3. 抠图 · BiRefNet-HR（商品图首选）

- 节点：ComfyUI-RMBG `BiRefNet (RMBG)` + 本仓库配套 `Mask Cleanup`
- 模型：`models/RMBG/BiRefNet/`（`BiRefNet-HR.safetensors` + 3 个代码/配置）
- 参数：模型选 `BiRefNet-HR`（内部 2048）；清理 `threshold 0.08 / erode 1 / feather 1`
- 适合：家具、3C、鞋包等硬边商品图、高分辨率主图
- 实测：2048×1152 约 4.1–4.4 秒

## 4. 抠图 · InSPyReNet（细结构）

- 节点：ComfyUI-RMBG `Remove Background (RMBG)` 选 `INSPYRENET` + `Mask Cleanup`
- 模型：`models/RMBG/INSPYRENET/inspyrenet.safetensors`
- 参数：`process_res 1024`（默认）；**2048 首次实测 221 秒，非常慢**
- 适合：细腿、网格、栏杆、细线、复杂背景、需要保留阴影

## 5. 抠图 · SDMatte（透明/发丝/高难）

- 节点：`BiRefNet (RMBG)`（粗 mask）+ `SDMatte (RMBG)`（精修）+ `Mask Cleanup`
- 模型：`models/RMBG/BiRefNet/` + `models/RMBG/SDMatte/`
- 参数：SDMatte `process_res 1024`、`mask_refine true`、`transparent_object true`
- 适合：玻璃/透明物/发丝/半透明、高价值难图
- 实测：约 13.2 秒（含 5.2GB 加载），之后复用缓存

## 输出

每个工作流输出两张：
- `<前缀>_00001_.png`：透明底 RGBA
- `<前缀>_mask_00001_.png`：白=主体的 mask
