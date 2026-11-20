from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TrainConfig:
    output_dir: Path = Path("checkpoints/unet")
    seed: int = 42
    device: str = "auto"
    num_workers: int = 0
    pin_memory: bool = True

    in_channels: int = 3
    out_channels: int = 1
    bilinear: bool = True
    dropout: float = 0.0

    epochs: int = 50
    lr: float = 3e-4
    weight_decay: float = 1e-4
    grad_clip_norm: float | None = 1.0
    amp: bool = True

    scheduler: str = "cosine"
    eta_min_lr: float = 1e-6
    plateau_patience: int = 5
    plateau_factor: float = 0.5

    bce_weight: float = 0.5
    dice_weight: float = 0.5
    threshold: float = 0.5

    save_every: int = 1

    colab_mount_drive: bool = False
    colab_drive_output_dir: str | None = None
