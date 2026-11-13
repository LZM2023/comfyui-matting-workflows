# ComfyUI-Sapiens2-Matting

ComfyUI 节点：Meta **Sapiens2-1B** 人像软 alpha 抠图（ICLR 2026）。

- 输入：一张含人物的图（RGB，支持 batch）
- 输出：`foreground`（去色溢出的直通前景 RGB）、`alpha`（0–1 连续软遮罩）、`rgba`（4 通道，可直接 SaveImage 存透明 PNG）
- 局限：**只针对人物**（human-centric），不是通用物体抠图；非人主体请用 Lucida / FeyNoBg。

## 1. 放权重

把 `facebook/sapiens2-matting-1b` 的 `model.safetensors`（6.16 GB，fp32）放到：

```
ComfyUI/models/sapiens2/matting/model.safetensors
```

国内镜像下载（任选其一）：

```bat
curl.exe -L -C - -o "ComfyUI\models\sapiens2\matting\model.safetensors" ^
  "https://hf-mirror.com/facebook/sapiens2-matting-1b/resolve/main/model.safetensors"
```

权重**不在本仓库内**，也不随节点分发；使用前请阅读 `LICENSE_SAPIENS2.md`
（Meta Sapiens2 License：允许使用/再分发/修改，但禁止监控、生物识别处理、
deepfake、再识别等用途；商用请自行做法务评估）。

## 2. 节点参数

| 参数 | 说明 |
|---|---|
| `image` | 输入图像（IMAGE） |
| `model` | `models/sapiens2/` 下扫描到的权重（默认 `matting/model.safetensors`） |
| `precision` | `fp32`（默认，与官方一致）/ `bf16` / `fp16`。24GB 显卡建议 fp32；显存紧张用 bf16 |
| `device` | `auto` / `cuda` / `cpu` |
| `unload_after_run` | 跑完立即释放该模型占的显存（反复跑建议关闭以复用缓存） |

首次运行会先调用 ComfyUI 的 `unload_all_models()` 腾显存，再加载 1.5B 模型；
加载后模型常驻缓存，同参数后续推理不再重新加载。

## 3. 推荐工作流

```
Load Image ──► Sapiens2 Matting ──► foreground ──► Join Image with Alpha ──► Save Image
                                   ├─ alpha ──────┘
                                   └─ rgba ─────────────────────────────────► Save Image
```

- 要透明 PNG：把 `rgba` 直接接 `Save Image`（PNG 保留 alpha）。
- 要合成到新背景：`foreground` + `alpha` 接 `Join Image with Alpha`，再 `ImageCompositeMasked`。
- 边缘微调：`alpha` 接核心 `Feather Mask` / `Grow Mask` 再合成。

## 4. 显存与速度（RTX 4090 24GB 参考）

| 精度 | 权重显存 | 备注 |
|---|---|---|
| fp32 | ~6.2 GB | 官方默认，质量基准 |
| bf16 | ~3.1 GB | 4090 支持，速度更快 |
| fp16 | ~3.1 GB | 部分归一化层对 fp16 更敏感，优先 bf16 |

推理分辨率固定 1024×768（H×W，竖构图），输出会双线性插值回原图尺寸；
横图会被压扁后再拉回，边缘质量会有损失，建议先按 3:4 裁剪或保持竖图。

## 5. 致谢 / 许可

- 代码：vendored 自官方 Space `facebook/sapiens2-matting`（`sapiens/` 包，版本 2.0.0），
  上游 `github.com/facebookresearch/sapiens2`。
- 权重：Meta，Sapiens2 License。
- 本封装节点代码：MIT。
