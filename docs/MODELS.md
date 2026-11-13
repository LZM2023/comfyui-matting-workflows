# 模型清单（URL / 大小 / SHA256 / 目标目录）

> 目标目录都相对 ComfyUI 根目录（例如 `D:\ComfyUI-aki-v2\ComfyUI`）。

## 1. Lucida（Lucida 工作流 / 也可给 SDMatte 打底）

| 字段 | 值 |
|---|---|
| 文件 | `lucida.safetensors` |
| 下载 | https://huggingface.co/Comfy-Org/BiRefNet/resolve/main/background_removal/lucida.safetensors |
| 大小 | 884,878,856 B (844 MiB) |
| SHA256 | `a43e3dd84cbe84db76bd2015ef8f7034c9503c50d9b56fa2155803b69bd2f408` |
| 目标 | `models/background_removal/lucida.safetensors` |
| 许可 | MIT（作者注明训练集含 research-only 数据，商用需自行评估） |

## 2. BiRefNet-HR（BiRefNet-HR 工作流 / SDMatte 工作流的粗 mask）

需要 4 个文件，全部放同一目录 `models/RMBG/BiRefNet/`：

| 文件 | URL | 大小 | SHA256 |
|---|---|---|---|
| `birefnet.py` | https://huggingface.co/1038lab/BiRefNet/resolve/main/birefnet.py | ~92 KB | — |
| `BiRefNet_config.py` | https://huggingface.co/1038lab/BiRefNet/resolve/main/BiRefNet_config.py | ~300 B | — |
| `config.json` | https://huggingface.co/1038lab/BiRefNet/resolve/main/config.json | ~400 B | — |
| `BiRefNet-HR.safetensors` | https://huggingface.co/1038lab/BiRefNet/resolve/main/BiRefNet-HR.safetensors | 444,473,596 B | `9d678bafec0b0019fbb073b7fd02f05ede25dc4b15254f23b2fb0be333200c0d` |

许可：MIT（BiRefNet 原项目）。

## 3. InSPyReNet（InSPyReNet 工作流）

| 字段 | 值 |
|---|---|
| 文件 | `inspyrenet.safetensors` |
| 下载 | https://huggingface.co/1038lab/inspyrenet/resolve/main/inspyrenet.safetensors |
| 大小 | 367,120,444 B |
| SHA256 | `5c8ab4541f9a960b376a80362b07f1d96262e689c501365e6323faa958de47ea` |
| 目标 | `models/RMBG/INSPYRENET/inspyrenet.safetensors` |
| 许可 | MIT |

## 4. SDMatte（SDMatte 工作流）

主权重：

| 字段 | 值 |
|---|---|
| 文件 | `SDMatte.safetensors` |
| 下载 | https://huggingface.co/1038lab/SDMatte/resolve/main/SDMatte.safetensors |
| 大小 | 5,188,458,340 B (4.83 GiB) |
| SHA256 | `191a41d39e2f51dcca61be2b080b1b126d5acf603973eec5388b73f9dfe0e74e` |
| 目标 | `models/RMBG/SDMatte/SDMatte.safetensors` |

组件 configs（缺失时节点也会自动下载，建议手动放好）：

| 文件 | 目标 |
|---|---|
| https://huggingface.co/1038lab/SDMatte/resolve/main/scheduler/scheduler_config.json | `models/RMBG/SDMatte/scheduler/scheduler_config.json` |
| https://huggingface.co/1038lab/SDMatte/resolve/main/text_encoder/config.json | `models/RMBG/SDMatte/text_encoder/config.json` |
| https://huggingface.co/1038lab/SDMatte/resolve/main/tokenizer/merges.txt | `models/RMBG/SDMatte/tokenizer/merges.txt` |
| https://huggingface.co/1038lab/SDMatte/resolve/main/tokenizer/special_tokens_map.json | `models/RMBG/SDMatte/tokenizer/special_tokens_map.json` |
| https://huggingface.co/1038lab/SDMatte/resolve/main/tokenizer/tokenizer_config.json | `models/RMBG/SDMatte/tokenizer/tokenizer_config.json` |
| https://huggingface.co/1038lab/SDMatte/resolve/main/tokenizer/vocab.json | `models/RMBG/SDMatte/tokenizer/vocab.json` |
| https://huggingface.co/1038lab/SDMatte/resolve/main/unet/config.json | `models/RMBG/SDMatte/unet/config.json` |
| https://huggingface.co/1038lab/SDMatte/resolve/main/vae/config.json | `models/RMBG/SDMatte/vae/config.json` |

许可：OpenRAIL++。

## 5. Sapiens2-1B（Sapiens2 人像工作流）

| 字段 | 值 |
|---|---|
| 文件 | `model.safetensors`（仓库内另有同内容 `sapiens2_1b_matting.safetensors`，下载其一即可） |
| 下载 | https://huggingface.co/facebook/sapiens2-matting-1b/resolve/main/model.safetensors |
| 大小 | 6,157,412,312 B (5.73 GiB) |
| SHA256 | `2a0ea4ea2234e8dbd51e952950d8cedfe3ee2eca9099003784fd2d9cec6bc6e1` |
| 目标 | `models/sapiens2/matting/model.safetensors` |
| 许可 | Sapiens2 License（允许商用/分发，禁止监控、生物识别处理、深伪、再识别等；详见 Sapiens2 官方 LICENSE） |

## 校验下载

```powershell
Get-FileHash "ComfyUI\models\background_removal\lucida.safetensors" -Algorithm SHA256
```

如果 SHA256 与上表不一致，请重新下载（中途断点续传、镜像缓存都可能造成坏文件）。
