from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

try:
    import torch
except ModuleNotFoundError as error:
    raise unittest.SkipTest(f"PyTorch is not installed in current environment: {error}")

from unet_training.losses import BCEDiceLoss, DiceLoss, binary_segmentation_metrics
from unet_training.model import UNet


class TestUNetModel(unittest.TestCase):
    def test_forward_preserves_spatial_size_bilinear(self) -> None:
        model = UNet(in_channels=3, out_channels=1, bilinear=True)
        inputs = torch.randn(2, 3, 128, 160)

        outputs = model(inputs)

        self.assertEqual(tuple(outputs.shape), (2, 1, 128, 160))

    def test_forward_preserves_spatial_size_transposed_conv(self) -> None:
        model = UNet(in_channels=3, out_channels=1, bilinear=False)
        inputs = torch.randn(1, 3, 128, 128)

        outputs = model(inputs)

        self.assertEqual(tuple(outputs.shape), (1, 1, 128, 128))

    def test_backward_computes_gradients(self) -> None:
        model = UNet(in_channels=3, out_channels=1, bilinear=True)
        criterion = BCEDiceLoss()

        inputs = torch.randn(2, 3, 64, 64)
        targets = torch.randint(0, 2, (2, 1, 64, 64), dtype=torch.float32)

        logits = model(inputs)
        loss = criterion(logits, targets)
        loss.backward()

        first_param = next(model.parameters())
        self.assertIsNotNone(first_param.grad)
        self.assertTrue(torch.isfinite(first_param.grad).all().item())


class TestLossesAndMetrics(unittest.TestCase):
    def test_dice_loss_near_zero_for_perfect_predictions(self) -> None:
        criterion = DiceLoss(smooth=1.0)

        targets = torch.tensor([[[[1.0, 0.0], [0.0, 1.0]]]])
        logits = torch.where(targets == 1.0, torch.tensor(20.0), torch.tensor(-20.0))

        loss = criterion(logits, targets)

        self.assertLess(loss.item(), 1e-4)

    def test_dice_loss_high_for_opposite_predictions(self) -> None:
        criterion = DiceLoss(smooth=1.0)

        targets = torch.tensor([[[[1.0, 1.0], [0.0, 0.0]]]])
        logits = torch.where(targets == 1.0, torch.tensor(-20.0), torch.tensor(20.0))

        loss = criterion(logits, targets)

        self.assertGreater(loss.item(), 0.6)

    def test_bce_dice_matches_weighted_sum(self) -> None:
        logits = torch.randn(2, 1, 16, 16)
        targets = torch.randint(0, 2, (2, 1, 16, 16), dtype=torch.float32)

        criterion = BCEDiceLoss(bce_weight=0.7, dice_weight=0.3)
        bce_only = criterion.bce(logits, targets)
        dice_only = criterion.dice(logits, targets)

        combined = criterion(logits, targets)
        expected = 0.7 * bce_only + 0.3 * dice_only

        self.assertTrue(torch.allclose(combined, expected, atol=1e-7))

    def test_binary_metrics_perfect_prediction(self) -> None:
        targets = torch.tensor([[[[1.0, 0.0], [1.0, 0.0]]]])
        logits = torch.where(targets == 1.0, torch.tensor(20.0), torch.tensor(-20.0))

        metrics = binary_segmentation_metrics(logits, targets, threshold=0.5)

        self.assertAlmostEqual(metrics["dice"], 1.0, places=6)
        self.assertAlmostEqual(metrics["iou"], 1.0, places=6)

    def test_binary_metrics_complete_mismatch(self) -> None:
        targets = torch.tensor([[[[1.0, 1.0], [0.0, 0.0]]]])
        logits = torch.where(targets == 1.0, torch.tensor(-20.0), torch.tensor(20.0))

        metrics = binary_segmentation_metrics(logits, targets, threshold=0.5)

        self.assertLess(metrics["dice"], 1e-4)
        self.assertLess(metrics["iou"], 1e-4)


if __name__ == "__main__":
    unittest.main()
