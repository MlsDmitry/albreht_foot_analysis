from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import torch
import torch.nn as nn
from torch.amp import GradScaler, autocast
from torch.optim import AdamW
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch.utils.data import DataLoader
from tqdm.auto import tqdm

from .config import TrainConfig
from .data import build_train_loader, build_val_loader, unpack_batch
from .losses import BCEDiceLoss, binary_segmentation_metrics
from .model import UNet
from .utils import (
    build_scheduler,
    config_as_dict,
    current_lr,
    get_device,
    is_colab_runtime,
    resolve_output_dir,
    save_json,
    set_seed,
)


def train_one_epoch(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    scaler: GradScaler,
    device: torch.device,
    amp: bool,
    grad_clip_norm: float | None,
    threshold: float,
) -> dict[str, float]:
    model.train()
    running_loss = 0.0
    running_dice = 0.0
    running_iou = 0.0
    n_batches = 0

    progress = tqdm(loader, desc="train", leave=False)
    for batch in progress:
        images, masks = unpack_batch(batch, device)

        optimizer.zero_grad(set_to_none=True)
        with autocast(device_type=device.type, enabled=amp and device.type in {"cuda", "mps"}):
            logits = model(images)
            loss = criterion(logits, masks)

        scaler.scale(loss).backward()
        if grad_clip_norm is not None and grad_clip_norm > 0:
            scaler.unscale_(optimizer)
            nn.utils.clip_grad_norm_(model.parameters(), grad_clip_norm)
        scaler.step(optimizer)
        scaler.update()

        metrics = binary_segmentation_metrics(logits.detach(), masks, threshold=threshold)
        running_loss += float(loss.item())
        running_dice += metrics["dice"]
        running_iou += metrics["iou"]
        n_batches += 1

        progress.set_postfix(loss=f"{loss.item():.4f}", dice=f"{metrics['dice']:.4f}")

    if n_batches == 0:
        raise ValueError("Training loader returned zero batches")

    return {
        "loss": running_loss / n_batches,
        "dice": running_dice / n_batches,
        "iou": running_iou / n_batches,
    }


@torch.no_grad()
def validate_one_epoch(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
    amp: bool,
    threshold: float,
) -> dict[str, float]:
    model.eval()
    running_loss = 0.0
    running_dice = 0.0
    running_iou = 0.0
    n_batches = 0

    progress = tqdm(loader, desc="val", leave=False)
    for batch in progress:
        images, masks = unpack_batch(batch, device)

        with autocast(device_type=device.type, enabled=amp and device.type in {"cuda", "mps"}):
            logits = model(images)
            loss = criterion(logits, masks)

        metrics = binary_segmentation_metrics(logits, masks, threshold=threshold)
        running_loss += float(loss.item())
        running_dice += metrics["dice"]
        running_iou += metrics["iou"]
        n_batches += 1

        progress.set_postfix(loss=f"{loss.item():.4f}", dice=f"{metrics['dice']:.4f}")

    if n_batches == 0:
        raise ValueError("Validation loader returned zero batches")

    return {
        "loss": running_loss / n_batches,
        "dice": running_dice / n_batches,
        "iou": running_iou / n_batches,
    }


def save_checkpoint(
    path: Path,
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    scaler: GradScaler,
    epoch: int,
    best_val_dice: float,
    config: TrainConfig,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "epoch": epoch,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "scaler_state_dict": scaler.state_dict(),
            "best_val_dice": best_val_dice,
            "config": config_as_dict(config),
        },
        path,
    )


def train(config: TrainConfig) -> None:
    set_seed(config.seed)
    device = get_device(config.device)

    output_dir = resolve_output_dir(config)
    output_dir.mkdir(parents=True, exist_ok=True)
    save_json(config_as_dict(config), output_dir / "config.json")

    train_loader = build_train_loader(config)
    val_loader = build_val_loader(config)

    model = UNet(
        in_channels=config.in_channels,
        out_channels=config.out_channels,
        bilinear=config.bilinear,
        dropout=config.dropout,
    ).to(device)

    criterion = BCEDiceLoss(bce_weight=config.bce_weight, dice_weight=config.dice_weight)
    optimizer = AdamW(model.parameters(), lr=config.lr, weight_decay=config.weight_decay)
    scheduler = build_scheduler(optimizer, config)
    scaler = GradScaler(enabled=config.amp and device.type == "cuda")

    history: list[dict[str, Any]] = []
    best_val_dice = float("-inf")

    if is_colab_runtime():
        print("Google Colab runtime detected")

    print(f"Device: {device}")
    print(f"Output dir: {output_dir}")

    for epoch in range(1, config.epochs + 1):
        epoch_start = time.time()

        train_metrics = train_one_epoch(
            model=model,
            loader=train_loader,
            criterion=criterion,
            optimizer=optimizer,
            scaler=scaler,
            device=device,
            amp=config.amp,
            grad_clip_norm=config.grad_clip_norm,
            threshold=config.threshold,
        )

        val_metrics = validate_one_epoch(
            model=model,
            loader=val_loader,
            criterion=criterion,
            device=device,
            amp=config.amp,
            threshold=config.threshold,
        )

        if scheduler is not None:
            if isinstance(scheduler, ReduceLROnPlateau):
                scheduler.step(val_metrics["dice"])
            else:
                scheduler.step()

        lr = current_lr(optimizer)
        epoch_time = time.time() - epoch_start

        record = {
            "epoch": epoch,
            "lr": lr,
            "epoch_time_sec": epoch_time,
            "train": train_metrics,
            "val": val_metrics,
        }
        history.append(record)

        print(
            f"Epoch {epoch:03d}/{config.epochs} | "
            f"lr={lr:.2e} | "
            f"train_loss={train_metrics['loss']:.4f} train_dice={train_metrics['dice']:.4f} | "
            f"val_loss={val_metrics['loss']:.4f} val_dice={val_metrics['dice']:.4f} "
            f"val_iou={val_metrics['iou']:.4f} | "
            f"{epoch_time:.1f}s"
        )

        if val_metrics["dice"] > best_val_dice:
            best_val_dice = val_metrics["dice"]
            save_checkpoint(
                output_dir / "best.pt",
                model,
                optimizer,
                scaler,
                epoch,
                best_val_dice,
                config,
            )

        if epoch % config.save_every == 0:
            save_checkpoint(
                output_dir / f"epoch_{epoch:03d}.pt",
                model,
                optimizer,
                scaler,
                epoch,
                best_val_dice,
                config,
            )

        save_json({"history": history, "best_val_dice": best_val_dice}, output_dir / "history.json")

    print(f"Training complete. Best val dice: {best_val_dice:.4f}")
