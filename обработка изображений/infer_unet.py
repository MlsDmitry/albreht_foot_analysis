from __future__ import annotations

import argparse
import random
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


class DoubleConv(nn.Module):
    def __init__(self, in_ch: int, out_ch: int) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1, bias=False),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_ch, out_ch, 3, padding=1, bias=False),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class UNet(nn.Module):
    def __init__(
        self,
        in_channels: int = 3,
        out_channels: int = 1,
        features: tuple[int, int, int, int] = (64, 128, 256, 512),
    ) -> None:
        super().__init__()
        self.downs = nn.ModuleList()
        self.ups = nn.ModuleList()
        self.pool = nn.MaxPool2d(2)

        ch = in_channels
        for f in features:
            self.downs.append(DoubleConv(ch, f))
            ch = f

        self.bottleneck = DoubleConv(features[-1], features[-1] * 2)

        rev = features[::-1]
        up_in = features[-1] * 2
        for f in rev:
            self.ups.append(nn.ConvTranspose2d(up_in, f, kernel_size=2, stride=2))
            self.ups.append(DoubleConv(f * 2, f))
            up_in = f

        self.final_conv = nn.Conv2d(features[0], out_channels, kernel_size=1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        skips: list[torch.Tensor] = []
        for down in self.downs:
            x = down(x)
            skips.append(x)
            x = self.pool(x)

        x = self.bottleneck(x)
        skips = skips[::-1]

        for idx in range(0, len(self.ups), 2):
            x = self.ups[idx](x)
            skip = skips[idx // 2]

            if x.shape[-2:] != skip.shape[-2:]:
                x = F.interpolate(x, size=skip.shape[-2:], mode="bilinear", align_corners=False)

            x = torch.cat([skip, x], dim=1)
            x = self.ups[idx + 1](x)

        return self.final_conv(x)


def get_device(device: str) -> torch.device:
    if device == "auto":
        if torch.cuda.is_available():
            return torch.device("cuda")
        if torch.backends.mps.is_available():
            return torch.device("mps")
        return torch.device("cpu")

    if device == "cuda" and torch.cuda.is_available():
        return torch.device("cuda")
    if device == "mps" and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def load_checkpoint(model: nn.Module, checkpoint_path: Path, device: torch.device) -> None:
    ckpt = torch.load(str(checkpoint_path), map_location=device)

    if isinstance(ckpt, dict) and "model_state_dict" in ckpt:
        state_dict = ckpt["model_state_dict"]
    else:
        state_dict = ckpt

    model.load_state_dict(state_dict)


def preprocess_image(image_bgr: np.ndarray, img_size: int) -> torch.Tensor:
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    image_resized = cv2.resize(image_rgb, (img_size, img_size), interpolation=cv2.INTER_AREA)
    image_float = image_resized.astype(np.float32) / 255.0
    tensor = torch.from_numpy(image_float).permute(2, 0, 1).unsqueeze(0)
    return tensor


def postprocess_mask(logits: torch.Tensor, threshold: float, out_h: int, out_w: int) -> np.ndarray:
    probs = torch.sigmoid(logits)
    pred = (probs >= threshold).float()
    pred = pred.squeeze(0).squeeze(0).cpu().numpy().astype(np.uint8)
    mask = cv2.resize(pred, (out_w, out_h), interpolation=cv2.INTER_NEAREST)
    return (mask * 255).astype(np.uint8)


def list_images(path: Path) -> list[Path]:
    if path.is_file():
        return [path]

    exts = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}
    return sorted([p for p in path.rglob("*") if p.suffix.lower() in exts])


def choose_random_image(dataset_root: Path) -> Path:
    images = list_images(dataset_root)
    if not images:
        raise ValueError(f"No images found in dataset root: {dataset_root}")
    return random.choice(images)


def build_overlay(image_bgr: np.ndarray, mask_uint8: np.ndarray, alpha: float = 0.35) -> np.ndarray:
    overlay = image_bgr.copy()
    red = np.zeros_like(overlay)
    red[:, :, 2] = 255
    mask_bool = mask_uint8 > 0
    overlay[mask_bool] = cv2.addWeighted(overlay, 1 - alpha, red, alpha, 0)[mask_bool]
    return overlay


def show_prediction(image_bgr: np.ndarray, mask_uint8: np.ndarray, overlay_bgr: np.ndarray, title: str) -> None:
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    overlay_rgb = cv2.cvtColor(overlay_bgr, cv2.COLOR_BGR2RGB)

    plt.figure(figsize=(14, 4))
    plt.suptitle(title)

    plt.subplot(1, 3, 1)
    plt.title("Input")
    plt.imshow(image_rgb)
    plt.axis("off")

    plt.subplot(1, 3, 2)
    plt.title("Pred Mask")
    plt.imshow(mask_uint8, cmap="gray")
    plt.axis("off")

    plt.subplot(1, 3, 3)
    plt.title("Overlay")
    plt.imshow(overlay_rgb)
    plt.axis("off")

    plt.tight_layout()
    plt.show()


def save_outputs(
    image_bgr: np.ndarray,
    mask_uint8: np.ndarray,
    out_mask_path: Path,
    out_overlay_path: Path | None,
) -> None:
    out_mask_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_mask_path), mask_uint8)

    if out_overlay_path is not None:
        overlay = build_overlay(image_bgr, mask_uint8)
        out_overlay_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(out_overlay_path), overlay)


def run_inference(
    model: nn.Module,
    image_paths: list[Path],
    input_root: Path,
    output_dir: Path,
    img_size: int,
    threshold: float,
    device: torch.device,
    save_overlay: bool,
    show_plot: bool,
) -> None:
    model.eval()

    with torch.no_grad():
        for image_path in image_paths:
            image_bgr = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
            if image_bgr is None:
                print(f"[WARN] Skipping unreadable image: {image_path}")
                continue

            h, w = image_bgr.shape[:2]
            inp = preprocess_image(image_bgr, img_size).to(device)
            logits = model(inp)
            mask = postprocess_mask(logits, threshold=threshold, out_h=h, out_w=w)

            rel = image_path.relative_to(input_root) if input_root.is_dir() else Path(image_path.name)
            stem = rel.with_suffix("")

            out_mask_path = output_dir / "masks" / f"{stem}.png"
            out_overlay_path = output_dir / "overlays" / f"{stem}.png" if save_overlay else None
            save_outputs(image_bgr, mask, out_mask_path, out_overlay_path)

            if show_plot:
                overlay = build_overlay(image_bgr, mask)
                show_prediction(image_bgr, mask, overlay, title=image_path.name)

            print(f"[OK] {image_path} -> {out_mask_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run inference with trained U-Net checkpoint")
    parser.add_argument("--checkpoint", type=Path, required=True, help="Path to trained checkpoint (.pt)")
    parser.add_argument("--input", type=Path, default=None, help="Input image file or directory")
    parser.add_argument(
        "--dataset-root",
        type=Path,
        default=Path("../dataset-preprocessed"),
        help="Dataset root used for random image selection",
    )
    parser.add_argument(
        "--random-image",
        action="store_true",
        help="Automatically pick one random image from --dataset-root",
    )
    parser.add_argument("--output-dir", type=Path, default=Path("inference_output"), help="Where to save masks")
    parser.add_argument("--img-size", type=int, default=256, help="Model input size used during training")
    parser.add_argument("--threshold", type=float, default=0.5, help="Sigmoid threshold for binary mask")
    parser.add_argument("--device", type=str, default="auto", choices=["auto", "cuda", "cpu", "mps"])
    parser.add_argument("--no-overlay", action="store_true", help="Disable overlay image saving")
    parser.add_argument("--no-show", action="store_true", help="Disable matplotlib visualization")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.checkpoint.exists():
        raise FileNotFoundError(f"Checkpoint not found: {args.checkpoint}")

    if args.random_image or args.input is None:
        if not args.dataset_root.exists():
            raise FileNotFoundError(f"Dataset root not found: {args.dataset_root}")
        selected = choose_random_image(args.dataset_root)
        image_paths = [selected]
        input_root = args.dataset_root
        print(f"Randomly selected: {selected}")
    else:
        if not args.input.exists():
            raise FileNotFoundError(f"Input path not found: {args.input}")
        image_paths = list_images(args.input)
        if not image_paths:
            raise ValueError(f"No images found in: {args.input}")
        input_root = args.input

    device = get_device(args.device)
    model = UNet(in_channels=3, out_channels=1).to(device)
    load_checkpoint(model, args.checkpoint, device)

    run_inference(
        model=model,
        image_paths=image_paths,
        input_root=input_root,
        output_dir=args.output_dir,
        img_size=args.img_size,
        threshold=args.threshold,
        device=device,
        save_overlay=not args.no_overlay,
        show_plot=not args.no_show,
    )

    print(f"Done. Results in: {args.output_dir}")


if __name__ == "__main__":
    main()
