#!/usr/bin/env python3

import argparse
import random
import xml.etree.ElementTree as ET
from pathlib import Path

import cv2
import numpy as np
import tensorflow as tf


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


def normalize_rel_path(path_like: str):
    s = str(path_like).replace("\\", "/").strip()
    while s.startswith("./"):
        s = s[2:]
    return s


def seed_everything(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)


def parse_points(raw: str):
    points = []
    for pair in raw.split(";"):
        pair = pair.strip()
        if not pair:
            continue
        x, y = pair.split(",")
        points.append((float(x), float(y)))
    return points


def polygons_to_mask(width: int, height: int, polygons):
    mask = np.zeros((height, width), dtype=np.uint8)
    pts_all = []
    for poly in polygons:
        if len(poly) < 3:
            continue
        pts = np.round(np.array(poly, dtype=np.float32)).astype(np.int32)
        pts[:, 0] = np.clip(pts[:, 0], 0, width - 1)
        pts[:, 1] = np.clip(pts[:, 1], 0, height - 1)
        pts_all.append(pts)
    if pts_all:
        cv2.fillPoly(mask, pts_all, color=1)
    return mask


def decode_cvat_rle(rle: str, width: int, height: int):
    vals = [int(v.strip()) for v in rle.split(",") if v.strip()]
    flat = np.zeros(width * height, dtype=np.uint8)
    idx, value = 0, 0
    for run in vals:
        if run <= 0:
            value = 1 - value
            continue
        end = min(idx + run, flat.size)
        if value == 1:
            flat[idx:end] = 1
        idx = end
        value = 1 - value
        if idx >= flat.size:
            break
    return flat.reshape((height, width))


def build_xml_index(xml_path: Path, label=None):
    index = {}
    for _event, image_elem in ET.iterparse(xml_path, events=("end",)):
        if image_elem.tag != "image":
            continue

        image_name = image_elem.get("name", "")
        width = int(image_elem.get("width", "0"))
        height = int(image_elem.get("height", "0"))

        polygons = []
        for polygon in image_elem.findall("polygon"):
            poly_label = polygon.get("label", "")
            if label is not None and poly_label != label:
                continue
            polygons.append(parse_points(polygon.get("points", "")))

        masks = []
        for mask in image_elem.findall("mask"):
            mask_label = mask.get("label", "")
            if label is not None and mask_label != label:
                continue
            masks.append(
                {
                    "rle": mask.get("rle", ""),
                    "left": int(mask.get("left", "0")),
                    "top": int(mask.get("top", "0")),
                    "width": int(mask.get("width", "0")),
                    "height": int(mask.get("height", "0")),
                }
            )

        if polygons or masks:
            index[image_name] = {
                "width": width,
                "height": height,
                "polygons": polygons,
                "masks": masks,
            }

        image_elem.clear()

    return index


def resolve_image_path(
    image_name: str,
    images_root: Path,
    dataset_root: Path,
    basename_index: dict,
    relpath_index: dict,
):
    raw_norm = normalize_rel_path(image_name)
    raw_path = Path(raw_norm)
    candidates = []

    if raw_path.is_absolute():
        candidates.append(raw_path)
    candidates.append(images_root / raw_path)
    candidates.append(dataset_root / raw_path)
    candidates.append(images_root / raw_path.name)
    candidates.append(dataset_root / raw_path.name)

    parts = raw_path.parts
    for i in range(1, len(parts)):
        tail = Path(*parts[i:])
        candidates.append(images_root / tail)
        candidates.append(dataset_root / tail)

    for cand in candidates:
        if cand.exists() and cand.is_file():
            return cand

    direct_rel = relpath_index.get(raw_norm)
    if direct_rel is not None:
        return direct_rel

    if raw_norm.startswith("/"):
        alt = relpath_index.get(raw_norm.lstrip("/"))
        if alt is not None:
            return alt

    rel_matches = [p for key, p in relpath_index.items() if key.endswith(raw_norm)]
    if len(rel_matches) == 1:
        return rel_matches[0]

    matches = basename_index.get(raw_path.name, [])
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1 and raw_path.parent != Path("."):
        parent_tail = normalize_rel_path(str(raw_path.parent))
        narrowed = [p for p in matches if normalize_rel_path(str(p.parent)).endswith(parent_tail)]
        if len(narrowed) == 1:
            return narrowed[0]

    return None


def build_basename_index(dataset_root: Path):
    index = {}
    for p in dataset_root.rglob("*"):
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS:
            index.setdefault(p.name, []).append(p)
    return index


def build_relpath_index(dataset_root: Path):
    index = {}
    for p in dataset_root.rglob("*"):
        if not (p.is_file() and p.suffix.lower() in IMAGE_EXTS):
            continue
        rel = normalize_rel_path(p.relative_to(dataset_root).as_posix())
        index[rel] = p
    return index


def get_image_and_mask_from_index(image_name: str, xml_index: dict, resolved_image_paths: dict):
    info = xml_index[image_name]
    width, height = info["width"], info["height"]

    image_path = resolved_image_paths[image_name]
    image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Failed to load image: {image_path}")

    full_mask = polygons_to_mask(width, height, info["polygons"])

    for mask_info in info["masks"]:
        if mask_info["width"] <= 0 or mask_info["height"] <= 0:
            continue
        local_mask = decode_cvat_rle(mask_info["rle"], mask_info["width"], mask_info["height"])

        y1, x1 = mask_info["top"], mask_info["left"]
        y2, x2 = y1 + mask_info["height"], x1 + mask_info["width"]

        y1c, x1c = max(0, y1), max(0, x1)
        y2c, x2c = min(height, y2), min(width, x2)
        if y1c >= y2c or x1c >= x2c:
            continue

        ly1, lx1 = y1c - y1, x1c - x1
        ly2, lx2 = ly1 + (y2c - y1c), lx1 + (x2c - x1c)
        full_mask[y1c:y2c, x1c:x2c] = np.maximum(
            full_mask[y1c:y2c, x1c:x2c],
            local_mask[ly1:ly2, lx1:lx2],
        )

    return image, full_mask


def preprocess_sample(image_name: str, xml_index: dict, resolved_image_paths: dict, img_size: int):
    image, mask = get_image_and_mask_from_index(image_name, xml_index, resolved_image_paths)

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, (img_size, img_size), interpolation=cv2.INTER_AREA)
    mask = cv2.resize(mask.astype(np.uint8), (img_size, img_size), interpolation=cv2.INTER_NEAREST)

    image = image.astype(np.float32) / 255.0
    mask = (mask > 0).astype(np.float32)
    mask = np.expand_dims(mask, axis=-1)
    return image, mask


def make_numpy_dataset(image_names, xml_index, resolved_image_paths: dict, img_size: int):
    images = []
    masks = []
    for name in image_names:
        image, mask = preprocess_sample(name, xml_index, resolved_image_paths, img_size)
        images.append(image)
        masks.append(mask)
    return np.stack(images, axis=0), np.stack(masks, axis=0)


def make_tf_dataset(images, masks, batch_size: int, training: bool):
    ds = tf.data.Dataset.from_tensor_slices((images, masks))
    if training:
        ds = ds.shuffle(buffer_size=len(images), reshuffle_each_iteration=True)
    ds = ds.batch(batch_size)
    ds = ds.prefetch(tf.data.AUTOTUNE)
    return ds


def conv_block(x, filters: int, use_batchnorm: bool = False):
    x = tf.keras.layers.Conv2D(filters, 3, padding="same", use_bias=False)(x)
    if use_batchnorm:
        x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.ReLU()(x)
    x = tf.keras.layers.Conv2D(filters, 3, padding="same", use_bias=False)(x)
    if use_batchnorm:
        x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.ReLU()(x)
    return x


def build_unet(input_shape=(256, 256, 3), out_channels=1, features=(64, 128, 256, 512), use_batchnorm: bool = False):
    inputs = tf.keras.Input(shape=input_shape)
    x = inputs
    skips = []

    for filters in features:
        x = conv_block(x, filters, use_batchnorm=use_batchnorm)
        skips.append(x)
        x = tf.keras.layers.MaxPool2D(pool_size=2)(x)

    x = conv_block(x, features[-1] * 2, use_batchnorm=use_batchnorm)
    skips = skips[::-1]

    for filters, skip in zip(reversed(features), skips):
        x = tf.keras.layers.Conv2DTranspose(filters, kernel_size=2, strides=2)(x)
        x = tf.keras.layers.Concatenate()([skip, x])
        x = conv_block(x, filters, use_batchnorm=use_batchnorm)

    outputs = tf.keras.layers.Conv2D(out_channels, kernel_size=1)(x)
    return tf.keras.Model(inputs=inputs, outputs=outputs)


def dice_loss(y_true, y_pred, smooth=1.0):
    probs = tf.nn.sigmoid(y_pred)
    y_true_f = tf.reshape(y_true, [tf.shape(y_true)[0], -1])
    probs_f = tf.reshape(probs, [tf.shape(probs)[0], -1])
    intersection = tf.reduce_sum(y_true_f * probs_f, axis=1)
    denom = tf.reduce_sum(y_true_f, axis=1) + tf.reduce_sum(probs_f, axis=1)
    dice = (2.0 * intersection + smooth) / (denom + smooth)
    return 1.0 - tf.reduce_mean(dice)


def bce_dice_loss(y_true, y_pred, bce_w=0.5, dice_w=0.5):
    y_true = tf.clip_by_value(tf.cast(y_true, tf.float32), 0.0, 1.0)
    y_pred = tf.cast(y_pred, tf.float32)
    y_pred = tf.clip_by_value(y_pred, -30.0, 30.0)

    bce = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(labels=y_true, logits=y_pred))
    d = dice_loss(y_true, y_pred)
    bce = tf.where(tf.math.is_finite(bce), bce, tf.constant(1e3, dtype=tf.float32))
    d = tf.where(tf.math.is_finite(d), d, tf.constant(1.0, dtype=tf.float32))
    return bce_w * bce + dice_w * d


def dice_metric(threshold=0.5, eps=1e-7):
    def metric(y_true, y_pred):
        probs = tf.nn.sigmoid(y_pred)
        preds = tf.cast(probs >= threshold, tf.float32)
        y_true_f = tf.reshape(y_true, [tf.shape(y_true)[0], -1])
        preds_f = tf.reshape(preds, [tf.shape(preds)[0], -1])
        tp = tf.reduce_sum(preds_f * y_true_f, axis=1)
        fp = tf.reduce_sum(preds_f * (1.0 - y_true_f), axis=1)
        fn = tf.reduce_sum((1.0 - preds_f) * y_true_f, axis=1)
        return tf.reduce_mean((2.0 * tp + eps) / (2.0 * tp + fp + fn + eps))

    metric.__name__ = "dice"
    return metric


def save_preview_on_original(
    model,
    image_name: str,
    xml_index: dict,
    resolved_image_paths: dict,
    img_size: int,
    out_path: Path,
    threshold: float = 0.5,
):
    import matplotlib.pyplot as plt

    image_bgr, full_mask = get_image_and_mask_from_index(image_name, xml_index, resolved_image_paths)
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

    resized = cv2.resize(image_rgb, (img_size, img_size), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
    logits = model.predict(resized[None, ...], verbose=0)
    prob_small = tf.nn.sigmoid(logits[0]).numpy().squeeze().astype(np.float32)
    prob_full = cv2.resize(
        prob_small,
        (image_rgb.shape[1], image_rgb.shape[0]),
        interpolation=cv2.INTER_LINEAR,
    )
    pred_full = (prob_full >= threshold).astype(np.uint8)

    gt_full = (full_mask > 0).astype(np.uint8)

    heat = np.clip(prob_full, 0.0, 1.0)
    heat_u8 = (heat * 255.0).astype(np.uint8)
    heat_color_bgr = cv2.applyColorMap(heat_u8, cv2.COLORMAP_JET)
    heat_color = cv2.cvtColor(heat_color_bgr, cv2.COLOR_BGR2RGB)

    overlay = image_rgb.copy().astype(np.float32)
    alpha_map = np.clip(heat[..., None] * 0.60, 0.0, 0.60)
    overlay = (1.0 - alpha_map) * overlay + alpha_map * heat_color.astype(np.float32)
    overlay = np.clip(overlay, 0, 255).astype(np.uint8)

    contours, _ = cv2.findContours(pred_full.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        cv2.drawContours(overlay, contours, contourIdx=-1, color=(0, 255, 0), thickness=2)

    fig = plt.figure(figsize=(12, 4))
    ax1 = fig.add_subplot(1, 3, 1)
    ax1.set_title("Original Image")
    ax1.imshow(image_rgb)
    ax1.axis("off")

    ax2 = fig.add_subplot(1, 3, 2)
    ax2.set_title("GT Mask (Original Size)")
    ax2.imshow(gt_full, cmap="gray")
    ax2.axis("off")

    ax3 = fig.add_subplot(1, 3, 3)
    ax3.set_title(f"Pred Overlay (thr={threshold:.2f})")
    ax3.imshow(overlay)
    ax3.axis("off")

    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def parse_args():
    parser = argparse.ArgumentParser(description="TensorFlow/Keras U-Net training for CVAT XML dataset")
    parser.add_argument("--dataset-root", type=Path, default=Path("dataset-preprocessed"))
    parser.add_argument("--annotations-xml", type=Path, default=Path("annotations.xml"))
    parser.add_argument("--images-root", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, default=Path("unet_runs_tf"))
    parser.add_argument("--label-filter", type=str, default=None)
    parser.add_argument("--img-size", type=int, default=256)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--val-split", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--soft-placement", action="store_true", default=True)
    parser.add_argument("--no-soft-placement", action="store_false", dest="soft_placement")
    parser.add_argument("--log-device-placement", action="store_true", default=False)
    parser.add_argument("--use-batchnorm", action="store_true", default=False)
    parser.add_argument("--clipnorm", type=float, default=1.0)
    parser.add_argument("--cache-in-ram", action="store_true", default=True)
    parser.add_argument("--no-cache-in-ram", action="store_false", dest="cache_in_ram")
    parser.add_argument("--preview", action="store_true", default=True)
    parser.add_argument("--no-preview", action="store_false", dest="preview")
    parser.add_argument("--preview-threshold", type=float, default=0.5)
    parser.add_argument("--save-history", action="store_true", default=False)
    parser.add_argument("--no-save-history", action="store_false", dest="save_history")
    args, _ = parser.parse_known_args()
    return args


def format_lr_for_name(lr: float):
    return f"{lr:.0e}".replace("+", "")


def build_run_name(args):
    label = args.label_filter if args.label_filter else "all"
    label = str(label).replace("/", "-").replace(" ", "_")
    bn = "bn1" if args.use_batchnorm else "bn0"
    return (
        f"unet_img{args.img_size}_bs{args.batch_size}_lr{format_lr_for_name(args.lr)}"
        f"_ep{args.epochs}_val{int(args.val_split * 100)}_seed{args.seed}_{bn}_label-{label}"
    )


def main():
    args = parse_args()
    tf.config.set_soft_device_placement(args.soft_placement)
    tf.debugging.set_log_device_placement(args.log_device_placement)
    seed_everything(args.seed)

    if not args.dataset_root.exists():
        raise FileNotFoundError(f"Missing dataset folder: {args.dataset_root}")
    if not args.annotations_xml.exists():
        raise FileNotFoundError(f"Missing annotations XML: {args.annotations_xml}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    run_name = build_run_name(args)
    xml_index = build_xml_index(args.annotations_xml, label=args.label_filter)
    basename_index = build_basename_index(args.dataset_root)
    relpath_index = build_relpath_index(args.dataset_root)

    resolved_image_paths = {}
    unresolved = []
    for name in sorted(xml_index.keys()):
        path = resolve_image_path(name, args.images_root, args.dataset_root, basename_index, relpath_index)
        if path is None:
            unresolved.append(name)
            continue
        resolved_image_paths[name] = path

    image_names = list(resolved_image_paths.keys())

    if not image_names:
        msg = "No valid annotated image paths found. Check --images-root/--dataset-root and XML image names."
        if unresolved:
            preview = ", ".join(unresolved[:5])
            msg += f" Unresolved examples: {preview}"
        raise RuntimeError(msg)

    random.Random(args.seed).shuffle(image_names)
    val_size = max(1, int(len(image_names) * args.val_split))
    train_names = image_names[val_size:]
    val_names = image_names[:val_size]
    if not train_names:
        raise RuntimeError("Training split is empty. Reduce --val-split.")

    print(f"TensorFlow version: {tf.__version__}")
    gpus = tf.config.list_physical_devices("GPU")
    print(f"GPU devices: {len(gpus)}")
    print(f"Soft placement: {args.soft_placement}")
    print(f"Device placement logging: {args.log_device_placement}")
    print(f"Run name: {run_name}")
    print(f"Samples total/train/val: {len(image_names)}/{len(train_names)}/{len(val_names)}")
    if unresolved:
        print(f"Warning: unresolved XML image entries skipped: {len(unresolved)}")

    train_images, train_masks = make_numpy_dataset(train_names, xml_index, resolved_image_paths, args.img_size)
    val_images, val_masks = make_numpy_dataset(val_names, xml_index, resolved_image_paths, args.img_size)

    train_ds = make_tf_dataset(train_images, train_masks, args.batch_size, training=True)
    val_ds = make_tf_dataset(val_images, val_masks, args.batch_size, training=False)

    model = build_unet(
        input_shape=(args.img_size, args.img_size, 3),
        out_channels=1,
        use_batchnorm=args.use_batchnorm,
    )
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=args.lr, clipnorm=args.clipnorm),
        loss=bce_dice_loss,
        metrics=[dice_metric()],
    )

    checkpoint_path = args.output_dir / f"{run_name}_best.keras"
    callbacks: list[tf.keras.callbacks.Callback] = [
        tf.keras.callbacks.TerminateOnNaN(),
        tf.keras.callbacks.ModelCheckpoint(
            filepath=str(checkpoint_path),
            monitor="val_dice",
            mode="max",
            save_best_only=True,
        )
    ]

    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=args.epochs,
        callbacks=callbacks,
        verbose=1,
    )

    history_path = args.output_dir / f"{run_name}_history.csv"
    if args.save_history:
        with history_path.open("w", encoding="utf-8") as f:
            keys = list(history.history.keys())
            f.write("epoch," + ",".join(keys) + "\n")
            n_epochs = len(history.history[keys[0]]) if keys else 0
            for i in range(n_epochs):
                row = [str(i + 1)]
                for key in keys:
                    row.append(str(history.history[key][i]))
                f.write(",".join(row) + "\n")

    best_val = float(np.max(history.history.get("val_dice", [0.0])))
    print(f"Finished. Best val dice: {best_val:.4f}")
    print(f"Model saved to: {checkpoint_path}")
    if args.save_history:
        print(f"History saved to: {history_path}")

    if args.preview:
        preview_path = args.output_dir / f"{run_name}_preview.png"
        save_preview_on_original(
            model,
            val_names[0],
            xml_index,
            resolved_image_paths,
            args.img_size,
            preview_path,
            threshold=args.preview_threshold,
        )
        print(f"Preview saved to: {preview_path}")


if __name__ == "__main__":
    main()