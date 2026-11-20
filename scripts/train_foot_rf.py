from __future__ import annotations

import argparse
import gzip
import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import dump
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    jaccard_score,
)
from sklearn.model_selection import train_test_split


def load_preprocessed_data(file_path: Path) -> tuple[np.ndarray, np.ndarray]:
    with gzip.open(file_path, "rb") as file:
        x_all, y_all = pickle.load(file)

    x = np.vstack(x_all)
    y = np.concatenate(y_all)

    print(f"Загружено признаков: {x.shape}, Меток: {y.shape}")
    return x, y


def diagnose_imbalance(y_true: np.ndarray, y_pred: np.ndarray) -> None:
    cm = confusion_matrix(y_true, y_pred)
    print("Матрица ошибок:")
    print(cm)
    print(f"True Negatives (Фон верно): {cm[0, 0]}")
    print(f"False Positives (Фон -> Стопа): {cm[0, 1]}")
    print(f"False Negatives (Стопа -> Фон): {cm[1, 0]}")
    print(f"True Positives (Стопа верно): {cm[1, 1]}")

    print("\nClassification Report:")
    print(classification_report(y_true, y_pred, target_names=["Фон", "Стопа"]))

    intersection = np.logical_and(y_true, y_pred).sum()
    union = np.logical_or(y_true, y_pred).sum()
    iou = intersection / (union + 1e-6)
    dice = 2 * intersection / (y_true.sum() + y_pred.sum() + 1e-6)

    print(f"\nIoU: {iou:.4f}")
    print(f"Dice: {dice:.4f}")

    if y_pred.sum() == 0:
        print("\n⚠️ ВНИМАНИЕ: Модель предсказала ТОЛЬКО фон! (Полный коллапс)")


def train_and_compare_models(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_val: np.ndarray,
    y_val: np.ndarray,
    *,
    max_iter: int,
    learning_rate: float,
    max_depth: int,
    min_samples_leaf: int,
    l2_regularization: float,
    random_state: int,
    verbose_diagnostics: bool,
) -> tuple[dict[str, HistGradientBoostingClassifier], pd.DataFrame]:
    class_counts = np.bincount(y_train.astype(np.int64), minlength=2)
    class_counts = np.maximum(class_counts, 1)
    balanced_weights = {
        0: float(len(y_train) / (2 * class_counts[0])),
        1: float(len(y_train) / (2 * class_counts[1])),
    }

    weight_schemes = {
        "Без весов": None,
        "Balanced": balanced_weights,
        "Ручные веса": {0: 1.0, 1: 4.0},
    }

    models = {
        name: HistGradientBoostingClassifier(
            max_iter=max_iter,
            learning_rate=learning_rate,
            max_depth=max_depth,
            min_samples_leaf=min_samples_leaf,
            l2_regularization=l2_regularization,
            random_state=random_state,
        )
        for name in weight_schemes
    }

    trained_models: dict[str, HistGradientBoostingClassifier] = {}
    rows: list[dict[str, float | str]] = []

    for model_name, clf in models.items():
        print(f"\n{'=' * 50}")
        print(f"Модель: {model_name}")
        print("=" * 50)

        scheme = weight_schemes[model_name]
        if scheme is None:
            sample_weight = None
        else:
            sample_weight = np.where(y_train == 1, scheme[1], scheme[0]).astype(np.float32)

        clf.fit(x_train, y_train, sample_weight=sample_weight)
        y_pred = clf.predict(x_val)

        f1_foot = f1_score(y_val, y_pred, pos_label=1)
        f1_bg = f1_score(y_val, y_pred, pos_label=0)
        iou = jaccard_score(y_val, y_pred, pos_label=1)

        intersection = np.logical_and(y_val, y_pred).sum()
        dice = 2 * intersection / (y_val.sum() + y_pred.sum() + 1e-6)

        rows.append(
            {
                "Модель": model_name,
                "F1_Стопа": float(f1_foot),
                "F1_Фон": float(f1_bg),
                "IoU": float(iou),
                "Dice": float(dice),
            }
        )

        print(f"F1-score (Стопа): {f1_foot:.4f}")
        print(f"F1-score (Фон):   {f1_bg:.4f}")
        print(f"IoU:              {iou:.4f}")
        print(f"Dice:             {dice:.4f}")

        if verbose_diagnostics:
            diagnose_imbalance(y_val, y_pred)

        trained_models[model_name] = clf

    results_df = pd.DataFrame(rows).set_index("Модель").sort_values("IoU", ascending=False)

    print("\n\n" + "=" * 50)
    print("СВОДНАЯ ТАБЛИЦА РЕЗУЛЬТАТОВ")
    print("=" * 50)
    print(results_df)

    return trained_models, results_df


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Обучение Gradient Boosting для сегментации стопы из предвычисленных признаков"
    )
    parser.add_argument(
        "--features-file",
        type=Path,
        default=Path("features.pkl.gz"),
        help="Путь до .pkl.gz файла с (X_all, y_all)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts"),
        help="Папка для сохранения модели и таблицы метрик",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="Доля валидационной выборки",
    )
    parser.add_argument(
        "--random-state",
        type=int,
        default=42,
        help="Фиксированный seed",
    )
    parser.add_argument(
        "--max-iter",
        type=int,
        default=300,
        help="Количество boosting-итераций",
    )
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=0.05,
        help="Скорость обучения",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=8,
        help="Максимальная глубина деревьев",
    )
    parser.add_argument(
        "--min-samples-leaf",
        type=int,
        default=20,
        help="Минимум объектов в листе",
    )
    parser.add_argument(
        "--l2-regularization",
        type=float,
        default=0.0,
        help="L2-регуляризация для листовых значений",
    )
    parser.add_argument(
        "--save-all-models",
        action="store_true",
        help="Сохранить все 3 модели (по умолчанию сохраняется только лучшая по IoU)",
    )
    parser.add_argument(
        "--verbose-diagnostics",
        action="store_true",
        help="Печатать полную диагностику дисбаланса для каждой модели",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    x, y = load_preprocessed_data(args.features_file)

    x_train, x_val, y_train, y_val = train_test_split(
        x,
        y,
        test_size=args.test_size,
        random_state=args.random_state,
        stratify=y,
    )

    models, results_df = train_and_compare_models(
        x_train,
        y_train,
        x_val,
        y_val,
        max_iter=args.max_iter,
        learning_rate=args.learning_rate,
        max_depth=args.max_depth,
        min_samples_leaf=args.min_samples_leaf,
        l2_regularization=args.l2_regularization,
        random_state=args.random_state,
        verbose_diagnostics=args.verbose_diagnostics,
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)

    results_csv_path = args.output_dir / "metrics.csv"
    results_json_path = args.output_dir / "metrics.json"
    results_df.to_csv(results_csv_path)
    results_df.to_json(results_json_path, orient="index", force_ascii=False, indent=2)

    best_model_name = str(results_df.index[0])
    best_model = models[best_model_name]

    model_path = args.output_dir / "best_model.joblib"
    dump(best_model, model_path)

    print(f"\nЛучшая модель: {best_model_name}")
    print(f"Сохранена в: {model_path}")
    print(f"Метрики CSV: {results_csv_path}")
    print(f"Метрики JSON: {results_json_path}")

    if args.save_all_models:
        for model_name, model in models.items():
            safe_name = model_name.lower().replace(" ", "_")
            extra_model_path = args.output_dir / f"hgb_{safe_name}.joblib"
            dump(model, extra_model_path)
            print(f"Сохранена модель: {extra_model_path}")

    meta = {
        "features_file": str(args.features_file),
        "output_dir": str(args.output_dir),
        "test_size": args.test_size,
        "random_state": args.random_state,
        "max_iter": args.max_iter,
        "learning_rate": args.learning_rate,
        "max_depth": args.max_depth,
        "min_samples_leaf": args.min_samples_leaf,
        "l2_regularization": args.l2_regularization,
        "best_model_name": best_model_name,
    }
    with (args.output_dir / "run_config.json").open("w", encoding="utf-8") as file:
        json.dump(meta, file, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
