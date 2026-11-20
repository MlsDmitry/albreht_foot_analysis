from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator
import xml.etree.ElementTree as ET

import cv2
import numpy as np


@dataclass(frozen=True)
class AnnotatedImage:
    image_id: int
    image_name: str
    width: int
    height: int
    polygon_count: int
    mask_count: int = 0


@dataclass(frozen=True)
class PolygonAnnotation:
    image_id: int
    image_name: str
    width: int
    height: int
    label: str
    points: list[tuple[float, float]]
    z_order: int | None


@dataclass(frozen=True)
class ImageMask:
    image: AnnotatedImage
    mask: np.ndarray


@dataclass(frozen=True)
class ImageAndMask:
    image_info: AnnotatedImage
    image_path: Path
    image: np.ndarray
    mask: np.ndarray


@dataclass(frozen=True)
class MaskAnnotation:
    image_id: int
    image_name: str
    width: int
    height: int
    label: str
    rle: str
    left: int
    top: int
    mask_width: int
    mask_height: int
    z_order: int | None


def parse_polygon_points(points_raw: str) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    for pair in points_raw.split(";"):
        pair = pair.strip()
        if not pair:
            continue
        x_raw, y_raw = pair.split(",")
        points.append((float(x_raw), float(y_raw)))
    return points


def _filter_by_label(elements: list[ET.Element], label: str | None) -> list[ET.Element]:
    if label is None:
        return elements
    return [element for element in elements if element.get("label") == label]


def _parse_optional_int(raw: str | None) -> int | None:
    return int(raw) if raw is not None else None


def polygons_to_binary_mask(
    width: int,
    height: int,
    polygons: list[list[tuple[float, float]]],
) -> np.ndarray:
    mask = np.zeros((height, width), dtype=np.uint8)
    polygons_int: list[np.ndarray] = []

    for polygon in polygons:
        if len(polygon) < 3:
            continue
        points = np.round(np.array(polygon, dtype=np.float32)).astype(np.int32)
        points[:, 0] = np.clip(points[:, 0], 0, width - 1)
        points[:, 1] = np.clip(points[:, 1], 0, height - 1)
        polygons_int.append(points)

    if polygons_int:
        cv2.fillPoly(mask, polygons_int, color=1)

    return mask


def iter_annotated_images(xml_path: str | Path, label: str | None = None) -> Iterator[AnnotatedImage]:
    xml_path = Path(xml_path)
    for _event, image_elem in ET.iterparse(xml_path, events=("end",)):
        if image_elem.tag != "image":
            continue

        polygons = _filter_by_label(image_elem.findall("polygon"), label)
        masks = _filter_by_label(image_elem.findall("mask"), label)

        if polygons or masks:
            yield AnnotatedImage(
                image_id=int(image_elem.get("id", "-1")),
                image_name=image_elem.get("name", ""),
                width=int(image_elem.get("width", "0")),
                height=int(image_elem.get("height", "0")),
                polygon_count=len(polygons),
                mask_count=len(masks),
            )

        image_elem.clear()


def iter_polygon_annotations(
    xml_path: str | Path,
    label: str | None = None,
) -> Iterator[PolygonAnnotation]:
    xml_path = Path(xml_path)
    for _event, image_elem in ET.iterparse(xml_path, events=("end",)):
        if image_elem.tag != "image":
            continue

        image_id = int(image_elem.get("id", "-1"))
        image_name = image_elem.get("name", "")
        width = int(image_elem.get("width", "0"))
        height = int(image_elem.get("height", "0"))

        for polygon in image_elem.findall("polygon"):
            polygon_label = polygon.get("label", "")
            if label is not None and polygon_label != label:
                continue

            yield PolygonAnnotation(
                image_id=image_id,
                image_name=image_name,
                width=width,
                height=height,
                label=polygon_label,
                points=parse_polygon_points(polygon.get("points", "")),
                z_order=_parse_optional_int(polygon.get("z_order")),
            )

        image_elem.clear()


def iter_mask_annotations(
    xml_path: str | Path,
    label: str | None = None,
) -> Iterator[MaskAnnotation]:
    xml_path = Path(xml_path)
    for _event, image_elem in ET.iterparse(xml_path, events=("end",)):
        if image_elem.tag != "image":
            continue

        image_id = int(image_elem.get("id", "-1"))
        image_name = image_elem.get("name", "")
        width = int(image_elem.get("width", "0"))
        height = int(image_elem.get("height", "0"))

        for mask in image_elem.findall("mask"):
            mask_label = mask.get("label", "")
            if label is not None and mask_label != label:
                continue

            yield MaskAnnotation(
                image_id=image_id,
                image_name=image_name,
                width=width,
                height=height,
                label=mask_label,
                rle=mask.get("rle", ""),
                left=int(mask.get("left", "0")),
                top=int(mask.get("top", "0")),
                mask_width=int(mask.get("width", "0")),
                mask_height=int(mask.get("height", "0")),
                z_order=_parse_optional_int(mask.get("z_order")),
            )

        image_elem.clear()


def build_annotated_image_index(
    xml_path: str | Path,
    label: str | None = None,
) -> dict[str, AnnotatedImage]:
    return {
        item.image_name: item
        for item in iter_annotated_images(xml_path=xml_path, label=label)
    }


def get_image_polygons(
    xml_path: str | Path,
    *,
    image_name: str | None = None,
    image_id: int | None = None,
    label: str | None = None,
) -> tuple[AnnotatedImage, list[PolygonAnnotation]] | None:
    if image_name is None and image_id is None:
        raise ValueError("Either image_name or image_id must be provided")

    xml_path = Path(xml_path)
    for _event, image_elem in ET.iterparse(xml_path, events=("end",)):
        if image_elem.tag != "image":
            continue

        current_id = int(image_elem.get("id", "-1"))
        current_name = image_elem.get("name", "")
        width = int(image_elem.get("width", "0"))
        height = int(image_elem.get("height", "0"))

        id_match = image_id is None or current_id == image_id
        name_match = image_name is None or current_name == image_name
        if not (id_match and name_match):
            image_elem.clear()
            continue

        polygon_annotations: list[PolygonAnnotation] = []
        for polygon in image_elem.findall("polygon"):
            polygon_label = polygon.get("label", "")
            if label is not None and polygon_label != label:
                continue
            polygon_annotations.append(
                PolygonAnnotation(
                    image_id=current_id,
                    image_name=current_name,
                    width=width,
                    height=height,
                    label=polygon_label,
                    points=parse_polygon_points(polygon.get("points", "")),
                    z_order=_parse_optional_int(polygon.get("z_order")),
                )
            )

        result = (
            AnnotatedImage(
                image_id=current_id,
                image_name=current_name,
                width=width,
                height=height,
                polygon_count=len(polygon_annotations),
            ),
            polygon_annotations,
        )
        image_elem.clear()
        return result

    return None


def get_image_shapes(
    xml_path: str | Path,
    *,
    image_name: str | None = None,
    image_id: int | None = None,
    label: str | None = None,
) -> tuple[AnnotatedImage, list[PolygonAnnotation], list[MaskAnnotation]] | None:
    if image_name is None and image_id is None:
        raise ValueError("Either image_name or image_id must be provided")

    xml_path = Path(xml_path)
    for _event, image_elem in ET.iterparse(xml_path, events=("end",)):
        if image_elem.tag != "image":
            continue

        current_id = int(image_elem.get("id", "-1"))
        current_name = image_elem.get("name", "")
        width = int(image_elem.get("width", "0"))
        height = int(image_elem.get("height", "0"))

        id_match = image_id is None or current_id == image_id
        name_match = image_name is None or current_name == image_name
        if not (id_match and name_match):
            image_elem.clear()
            continue

        polygon_annotations: list[PolygonAnnotation] = []
        for polygon in image_elem.findall("polygon"):
            polygon_label = polygon.get("label", "")
            if label is not None and polygon_label != label:
                continue
            polygon_annotations.append(
                PolygonAnnotation(
                    image_id=current_id,
                    image_name=current_name,
                    width=width,
                    height=height,
                    label=polygon_label,
                    points=parse_polygon_points(polygon.get("points", "")),
                    z_order=_parse_optional_int(polygon.get("z_order")),
                )
            )

        mask_annotations: list[MaskAnnotation] = []
        for mask in image_elem.findall("mask"):
            mask_label = mask.get("label", "")
            if label is not None and mask_label != label:
                continue
            mask_annotations.append(
                MaskAnnotation(
                    image_id=current_id,
                    image_name=current_name,
                    width=width,
                    height=height,
                    label=mask_label,
                    rle=mask.get("rle", ""),
                    left=int(mask.get("left", "0")),
                    top=int(mask.get("top", "0")),
                    mask_width=int(mask.get("width", "0")),
                    mask_height=int(mask.get("height", "0")),
                    z_order=_parse_optional_int(mask.get("z_order")),
                )
            )

        result = (
            AnnotatedImage(
                image_id=current_id,
                image_name=current_name,
                width=width,
                height=height,
                polygon_count=len(polygon_annotations),
                mask_count=len(mask_annotations),
            ),
            polygon_annotations,
            mask_annotations,
        )
        image_elem.clear()
        return result

    return None


def get_image_binary_mask(
    xml_path: str | Path,
    *,
    image_name: str | None = None,
    image_id: int | None = None,
    label: str | None = None,
) -> np.ndarray:
    result = get_image_polygons(
        xml_path,
        image_name=image_name,
        image_id=image_id,
        label=label,
    )
    if result is None:
        raise ValueError("Image not found in annotations")

    image, polygons = result
    return polygons_to_binary_mask(
        width=image.width,
        height=image.height,
        polygons=[polygon.points for polygon in polygons],
    )


def get_image_and_mask(
    xml_path: str | Path,
    *,
    image_name: str | None = None,
    image_id: int | None = None,
    label: str | None = None,
    images_root: str | Path | None = None,
    imread_flags: int = cv2.IMREAD_COLOR_RGB,
) -> ImageAndMask:
    result = get_image_polygons(
        xml_path,
        image_name=image_name,
        image_id=image_id,
        label=label,
    )
    if result is None:
        raise ValueError("Image not found in annotations")

    image_info, _polygons = result
    mask = get_image_binary_mask(
        xml_path,
        image_name=image_info.image_name,
        label=label,
    )

    base_dir = Path(images_root) if images_root is not None else Path(xml_path).resolve().parent
    image_path = base_dir / image_info.image_name
    if not image_path.exists():
        raise FileNotFoundError(
            f"Image file not found: {image_path}. You can pass images_root explicitly."
        )

    image = cv2.imread(str(image_path), imread_flags)
    if image is None:
        raise ValueError(f"Failed to load image from: {image_path}")
    
    # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    if image.shape[0] != image_info.height or image.shape[1] != image_info.width:
        raise ValueError(
            "Loaded image size does not match annotation size: "
            f"got {image.shape[1]}x{image.shape[0]}, expected {image_info.width}x{image_info.height}"
        )

    return ImageAndMask(
        image_info=image_info,
        image_path=image_path,
        image=image,
        mask=mask,
    )


def iter_binary_masks(
    xml_path: str | Path,
    label: str | None = None,
) -> Iterator[ImageMask]:
    xml_path = Path(xml_path)
    for _event, image_elem in ET.iterparse(xml_path, events=("end",)):
        if image_elem.tag != "image":
            continue

        image_id = int(image_elem.get("id", "-1"))
        image_name = image_elem.get("name", "")
        width = int(image_elem.get("width", "0"))
        height = int(image_elem.get("height", "0"))

        polygons: list[list[tuple[float, float]]] = []
        for polygon in image_elem.findall("polygon"):
            polygon_label = polygon.get("label", "")
            if label is not None and polygon_label != label:
                continue
            polygons.append(parse_polygon_points(polygon.get("points", "")))

        if polygons:
            image = AnnotatedImage(
                image_id=image_id,
                image_name=image_name,
                width=width,
                height=height,
                polygon_count=len(polygons),
            )
            yield ImageMask(
                image=image,
                mask=polygons_to_binary_mask(width=width, height=height, polygons=polygons),
            )

        image_elem.clear()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Parse CVAT XML annotations and list images that have polygon annotations."
    )
    parser.add_argument("xml_path", type=Path, help="Path to annotations.xml")
    parser.add_argument("--label", type=str, default=None, help="Optional polygon label filter")
    parser.add_argument("--limit", type=int, default=10, help="How many annotated images to print")
    args = parser.parse_args()

    annotated_images = iter_annotated_images(xml_path=args.xml_path, label=args.label)

    printed = 0
    for item in annotated_images:
        print(
            f"id={item.image_id} polygons={item.polygon_count} masks={item.mask_count} "
            f"size={item.width}x{item.height} path={item.image_name}"
        )
        printed += 1
        if printed >= args.limit:
            break

    if printed == 0:
        label_text = f" for label '{args.label}'" if args.label else ""
        print(f"No annotated images with polygons found{label_text}.")


if __name__ == "__main__":
    main()
