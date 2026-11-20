from __future__ import annotations

import argparse
from pathlib import Path

from .config import TrainConfig


def parse_args() -> TrainConfig:
    parser = argparse.ArgumentParser(description="Train U-Net for binary image segmentation")

    parser.add_argument("--output-dir", type=Path, default=Path("checkpoints/unet"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", type=str, default="auto", choices=["auto", "cuda", "cpu", "mps"])
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--pin-memory", action="store_true", default=True)
    parser.add_argument("--no-pin-memory", dest="pin_memory", action="store_false")

    parser.add_argument("--in-channels", type=int, default=3)
    parser.add_argument("--out-channels", type=int, default=1)
    parser.add_argument("--bilinear", action="store_true", default=True)
    parser.add_argument("--no-bilinear", dest="bilinear", action="store_false")
    parser.add_argument("--dropout", type=float, default=0.0)

    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--grad-clip-norm", type=float, default=1.0)
    parser.add_argument("--no-amp", action="store_true", help="Disable mixed precision")

    parser.add_argument("--scheduler", type=str, default="cosine", choices=["cosine", "plateau", "none"])
    parser.add_argument("--eta-min-lr", type=float, default=1e-6)
    parser.add_argument("--plateau-patience", type=int, default=5)
    parser.add_argument("--plateau-factor", type=float, default=0.5)

    parser.add_argument("--bce-weight", type=float, default=0.5)
    parser.add_argument("--dice-weight", type=float, default=0.5)
    parser.add_argument("--threshold", type=float, default=0.5)

    parser.add_argument("--save-every", type=int, default=1)

    parser.add_argument("--colab-mount-drive", action="store_true")
    parser.add_argument(
        "--colab-drive-output-dir",
        type=str,
        default=None,
        help="Example: MyDrive/unet_runs (used only in Google Colab)",
    )

    args = parser.parse_args()

    return TrainConfig(
        output_dir=args.output_dir,
        seed=args.seed,
        device=args.device,
        num_workers=args.num_workers,
        pin_memory=args.pin_memory,
        in_channels=args.in_channels,
        out_channels=args.out_channels,
        bilinear=args.bilinear,
        dropout=args.dropout,
        epochs=args.epochs,
        lr=args.lr,
        weight_decay=args.weight_decay,
        grad_clip_norm=args.grad_clip_norm,
        amp=not args.no_amp,
        scheduler=args.scheduler,
        eta_min_lr=args.eta_min_lr,
        plateau_patience=args.plateau_patience,
        plateau_factor=args.plateau_factor,
        bce_weight=args.bce_weight,
        dice_weight=args.dice_weight,
        threshold=args.threshold,
        save_every=args.save_every,
        colab_mount_drive=args.colab_mount_drive,
        colab_drive_output_dir=args.colab_drive_output_dir,
    )
