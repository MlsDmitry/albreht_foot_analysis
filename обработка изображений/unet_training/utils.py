from __future__ import annotations

import json
import os
import random
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch.optim.lr_scheduler import CosineAnnealingLR, ReduceLROnPlateau

from .config import TrainConfig


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = False
    torch.backends.cudnn.benchmark = True


def get_device(device_str: str) -> torch.device:
    if device_str == "auto":
        if torch.cuda.is_available():
            return torch.device("cuda")
        if torch.backends.mps.is_available():
            return torch.device("mps")
        return torch.device("cpu")

    if device_str == "cuda" and torch.cuda.is_available():
        return torch.device("cuda")
    if device_str == "mps" and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def is_colab_runtime() -> bool:
    return "google.colab" in sys.modules or "COLAB_RELEASE_TAG" in os.environ


def maybe_mount_google_drive(mount_point: Path = Path("/content/drive")) -> bool:
    if not is_colab_runtime():
        return False

    try:
        from google.colab import drive
    except Exception:
        return False

    drive.mount(str(mount_point), force_remount=False)
    return True


def resolve_output_dir(config: TrainConfig) -> Path:
    if config.colab_drive_output_dir:
        if not is_colab_runtime():
            raise RuntimeError("colab_drive_output_dir is set, but the current runtime is not Google Colab")
        if config.colab_mount_drive:
            maybe_mount_google_drive()
        return Path("/content/drive") / config.colab_drive_output_dir

    if config.colab_mount_drive:
        maybe_mount_google_drive()

    return config.output_dir


def save_json(data: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def build_scheduler(optimizer: torch.optim.Optimizer, config: TrainConfig):
    if config.scheduler == "cosine":
        return CosineAnnealingLR(optimizer, T_max=config.epochs, eta_min=config.eta_min_lr)
    if config.scheduler == "plateau":
        return ReduceLROnPlateau(
            optimizer,
            mode="max",
            patience=config.plateau_patience,
            factor=config.plateau_factor,
            min_lr=config.eta_min_lr,
        )
    if config.scheduler == "none":
        return None
    raise ValueError(f"Unsupported scheduler: {config.scheduler}")


def current_lr(optimizer: torch.optim.Optimizer) -> float:
    return float(optimizer.param_groups[0]["lr"])


def config_as_dict(config: TrainConfig) -> dict[str, Any]:
    return asdict(config)
