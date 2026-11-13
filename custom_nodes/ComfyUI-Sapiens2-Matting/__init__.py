"""ComfyUI wrapper for Meta Sapiens2-1B human matting.

Model weights are NOT redistributed here. The Sapiens2 source code in the
`sapiens/` subfolder is vendored from the official `facebook/sapiens2-matting`
Hugging Face Space and is governed by the Sapiens2 License (see
LICENSE_SAPIENS2.md). The model checkpoint must be downloaded separately into
ComfyUI/models/sapiens2/matting/.
"""

from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
