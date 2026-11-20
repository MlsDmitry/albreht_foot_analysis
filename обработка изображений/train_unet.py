from __future__ import annotations

from unet_training.cli import parse_args
from unet_training.engine import train


def main() -> None:
    config = parse_args()
    train(config)


if __name__ == "__main__":
    main()
