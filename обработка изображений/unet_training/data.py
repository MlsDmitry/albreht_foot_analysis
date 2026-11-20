from __future__ import annotations

from typing import TYPE_CHECKING, Any

import torch
from torch.utils.data import DataLoader

if TYPE_CHECKING:
    from .config import TrainConfig


def build_train_loader(config: "TrainConfig") -> DataLoader:
    raise NotImplementedError(
        "Implement build_train_loader(config) and return a torch.utils.data.DataLoader.\n"
        "In Google Colab, start with num_workers=0 and use config.pin_memory for CUDA.\n"
        "Each batch must provide image and mask tensors. Supported formats:\n"
        "  1) dict with keys {'image', 'mask'}\n"
        "  2) tuple/list where batch[0] is image and batch[1] is mask\n"
        "Expected shapes: image [B, C, H, W], mask [B, 1, H, W] or [B, H, W]."
    )


def build_val_loader(config: "TrainConfig") -> DataLoader:
    raise NotImplementedError(
        "Implement build_val_loader(config) and return validation DataLoader with the same batch format."
    )


def unpack_batch(batch: Any, device: torch.device) -> tuple[torch.Tensor, torch.Tensor]:
    if isinstance(batch, dict):
        if "image" not in batch or "mask" not in batch:
            raise KeyError("Batch dict must contain 'image' and 'mask' keys")
        images = batch["image"]
        masks = batch["mask"]
    elif isinstance(batch, (tuple, list)) and len(batch) >= 2:
        images = batch[0]
        masks = batch[1]
    else:
        raise TypeError("Unsupported batch format. Use dict{'image','mask'} or tuple/list(image, mask, ...).")

    if not torch.is_tensor(images) or not torch.is_tensor(masks):
        raise TypeError("Images and masks must be torch.Tensor")

    images = images.to(device=device, dtype=torch.float32, non_blocking=True)
    masks = masks.to(device=device, dtype=torch.float32, non_blocking=True)

    if masks.ndim == 3:
        masks = masks.unsqueeze(1)

    if images.ndim != 4 or masks.ndim != 4:
        raise ValueError(f"Expected image/mask rank 4 tensors, got {images.shape=} and {masks.shape=}")

    if masks.shape[1] != 1:
        raise ValueError(f"Binary segmentation expects mask channel=1, got {masks.shape[1]}")

    return images, masks
