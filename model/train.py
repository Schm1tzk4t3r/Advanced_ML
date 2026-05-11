"""Train and evaluate the VinhaGuard climate-stress risk model.

This script is the Person 3 / ML Lead deliverable. It trains a transparent
baseline and a stronger tree model, writes evaluation charts, and saves the
production inference artifact used by ``model.predict``.

Run from the repository root:
    python -m model.train
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    PrecisionRecallDisplay,
    RocCurveDisplay,
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GroupKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = REPO_ROOT / "data" / "processed" / "vinhaguard_dataset.csv"
ARTIFACT_DIR = REPO_ROOT / "model" / "artifacts"
FIGURE_DIR = REPO_ROOT / "docs" / "figures"

TARGET = "climate_stress_year"
CATEGORICAL_FEATURES = ["subregion"]
NUMERIC_FEATURES = [
    "elevation_m",
    "latitude",
    "longitude",
    "heat_days_30",
    "heat_days_35",
    "heat_days_38",
    "max_summer_tmax",
    "mean_summer_tmax",
    "heatwave_max_streak",
    "gdd_growing_season",
    "spring_frost_days",
    "spring_severe_frost_days",
    "min_spring_tmin",
    "annual_precip_mm",
    "summer_precip_mm",
    "dry_days",
    "max_consecutive_dry_days",
]
FEATURE_COLUMNS = CATEGORICAL_FEATURES + NUMERIC_FEATURES

TRAIN_END_YEAR = 2019
TEST_START_YEAR = 2020
RANDOM_STATE = 42


def load_dataset() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    required = set(FEATURE_COLUMNS + [TARGET, "location_id", "year"])
    missing = sorted(required.difference(df.columns))
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")
    return df


def add_trigger_diagnostics(df: pd.DataFrame) -> pd.DataFrame:
    """Add hazard-specific labels used for pricing diagnostics.

    These are not the main ML target. They let the pricing backend explain heat,
    frost, drought, and combined coverage from historical trigger behavior.
    """
    df = df.copy()
    heat_p80 = df.groupby("location_id")["heat_days_35"].transform(lambda x: x.quantile(0.80))
    dry_p80 = df.groupby("location_id")["max_consecutive_dry_days"].transform(lambda x: x.quantile(0.80))
    df["heat_trigger"] = (df["heat_days_35"] >= heat_p80).astype(int)
    df["frost_trigger"] = (df["spring_severe_frost_days"] >= 3).astype(int)
    df["drought_trigger"] = (df["max_consecutive_dry_days"] >= dry_p80).astype(int)
    return df


def make_preprocessor(scale_numeric: bool) -> ColumnTransformer:
    numeric_transformer: str | StandardScaler
    numeric_transformer = StandardScaler() if scale_numeric else "passthrough"
    return ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_FEATURES),
            ("num", numeric_transformer, NUMERIC_FEATURES),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def make_models() -> dict[str, Pipeline]:
    return {
        "logistic_regression": Pipeline(
            steps=[
                ("preprocess", make_preprocessor(scale_numeric=True)),
                (
                    "model",
                    LogisticRegression(
                        max_iter=5000,
                        class_weight="balanced",
                        solver="lbfgs",
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        ),
        "random_forest": Pipeline(
            steps=[
                ("preprocess", make_preprocessor(scale_numeric=False)),
                (
                    "model",
                    RandomForestClassifier(
                        n_estimators=500,
                        max_depth=6,
                        min_samples_leaf=5,
                        class_weight="balanced_subsample",
                        random_state=RANDOM_STATE,
                        n_jobs=-1,
                    ),
                ),
            ]
        ),
    }


def metric_dict(y_true: pd.Series, y_prob: np.ndarray) -> dict[str, Any]:
    y_pred = (y_prob >= 0.50).astype(int)
    return {
        "roc_auc": round(float(roc_auc_score(y_true, y_prob)), 4),
        "average_precision": round(float(average_precision_score(y_true, y_prob)), 4),
        "brier_score": round(float(brier_score_loss(y_true, y_prob)), 4),
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
        "classification_report": classification_report(y_true, y_pred, output_dict=True, zero_division=0),
    }


def get_feature_names(model: Pipeline) -> list[str]:
    preprocessor = model.named_steps["preprocess"]
    return list(preprocessor.get_feature_names_out())


def compute_feature_importance(model: Pipeline, x_test: pd.DataFrame, y_test: pd.Series) -> pd.DataFrame:
    rf = model.named_steps["model"]
    model_importance = getattr(rf, "feature_importances_", None)
    if model_importance is None:
        raise TypeError("Feature importance is only available for the Random Forest model.")

    encoded_names = get_feature_names(model)
    encoded = pd.DataFrame(
        {"feature": encoded_names, "gini_importance": model_importance}
    )

    perm = permutation_importance(
        model,
        x_test,
        y_test,
        n_repeats=20,
        scoring="roc_auc",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    permuted = pd.DataFrame(
        {
            "feature": FEATURE_COLUMNS,
            "permutation_importance_mean": perm.importances_mean,
            "permutation_importance_std": perm.importances_std,
        }
    )

    # Aggregate one-hot subregion importances back to the raw feature name for
    # the app and presentation.
    encoded["raw_feature"] = encoded["feature"].where(
        ~encoded["feature"].str.startswith("subregion_"), "subregion"
    )
    gini_raw = (
        encoded.groupby("raw_feature", as_index=False)["gini_importance"]
        .sum()
        .rename(columns={"raw_feature": "feature"})
    )

    out = gini_raw.merge(permuted, on="feature", how="outer").fillna(0.0)
    out = out.sort_values("permutation_importance_mean", ascending=False).reset_index(drop=True)
    return out


def save_evaluation_charts(
    model: Pipeline,
    x_test: pd.DataFrame,
    y_test: pd.Series,
    y_prob: np.ndarray,
    importance: pd.DataFrame,
) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    y_pred = (y_prob >= 0.50).astype(int)

    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    ConfusionMatrixDisplay.from_predictions(y_test, y_pred, cmap="Blues", colorbar=False, ax=ax)
    ax.set_title("Random Forest Confusion Matrix (2020-2024)")
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "ml_confusion_matrix.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 4.5))
    RocCurveDisplay.from_predictions(y_test, y_prob, ax=ax)
    ax.plot([0, 1], [0, 1], linestyle="--", color="gray", linewidth=1)
    ax.set_title("Random Forest ROC Curve (2020-2024)")
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "ml_roc_curve.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 4.5))
    PrecisionRecallDisplay.from_predictions(y_test, y_prob, ax=ax)
    ax.set_title("Random Forest Precision-Recall Curve (2020-2024)")
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "ml_precision_recall_curve.png", dpi=180)
    plt.close(fig)

    top = importance.head(10).sort_values("permutation_importance_mean")
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.barh(top["feature"], top["permutation_importance_mean"], color="#6B1C2E")
    ax.set_xlabel("Permutation importance (ROC-AUC decrease)")
    ax.set_title("Top Model Drivers")
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "ml_feature_importance.png", dpi=180)
    plt.close(fig)

    # Simple calibration by predicted probability decile.
    cal = pd.DataFrame({"y": y_test.to_numpy(), "p": y_prob})
    cal["bin"] = pd.qcut(cal["p"], q=min(8, cal["p"].nunique()), duplicates="drop")
    cal_plot = cal.groupby("bin", observed=True).agg(mean_pred=("p", "mean"), observed=("y", "mean"))

    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    ax.plot([0, 1], [0, 1], linestyle="--", color="gray", linewidth=1)
    ax.plot(cal_plot["mean_pred"], cal_plot["observed"], marker="o", color="#6B1C2E")
    ax.set_xlabel("Mean predicted probability")
    ax.set_ylabel("Observed stress rate")
    ax.set_title("Calibration Check (2020-2024)")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "ml_calibration_curve.png", dpi=180)
    plt.close(fig)


def train_and_evaluate() -> dict[str, Any]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    df = add_trigger_diagnostics(load_dataset())
    train_mask = df["year"] <= TRAIN_END_YEAR
    test_mask = df["year"] >= TEST_START_YEAR

    train_df = df.loc[train_mask].copy()
    test_df = df.loc[test_mask].copy()

    x_train = train_df[FEATURE_COLUMNS]
    y_train = train_df[TARGET]
    x_test = test_df[FEATURE_COLUMNS]
    y_test = test_df[TARGET]

    models = make_models()
    metrics: dict[str, Any] = {
        "dataset": {
            "path": str(DATA_PATH.relative_to(REPO_ROOT)),
            "rows": int(len(df)),
            "columns": int(len(df.columns) - 3),  # exclude three diagnostic triggers
            "locations": int(df["location_id"].nunique()),
            "years": [int(df["year"].min()), int(df["year"].max())],
            "positive_class_share": round(float(df[TARGET].mean()), 4),
        },
        "split": {
            "type": "chronological holdout",
            "train_years": [int(train_df["year"].min()), int(train_df["year"].max())],
            "test_years": [int(test_df["year"].min()), int(test_df["year"].max())],
            "train_rows": int(len(train_df)),
            "test_rows": int(len(test_df)),
        },
        "models": {},
    }

    fitted: dict[str, Pipeline] = {}
    for name, model in models.items():
        model.fit(x_train, y_train)
        y_prob = model.predict_proba(x_test)[:, 1]
        metrics["models"][name] = metric_dict(y_test, y_prob)
        fitted[name] = model

    group_cv = GroupKFold(n_splits=5)
    cv_scores = cross_val_score(
        make_models()["random_forest"],
        df[FEATURE_COLUMNS],
        df[TARGET],
        groups=df["location_id"],
        cv=group_cv,
        scoring="roc_auc",
        n_jobs=-1,
    )
    metrics["models"]["random_forest"]["group_kfold_location_roc_auc"] = {
        "mean": round(float(np.mean(cv_scores)), 4),
        "std": round(float(np.std(cv_scores)), 4),
        "folds": [round(float(v), 4) for v in cv_scores],
    }

    best_name = "random_forest"
    best_model = fitted[best_name]
    best_prob = best_model.predict_proba(x_test)[:, 1]
    importance = compute_feature_importance(best_model, x_test, y_test)
    save_evaluation_charts(best_model, x_test, y_test, best_prob, importance)

    # Refit the deployable model on all available rows after evaluation.
    deploy_model = make_models()[best_name]
    deploy_model.fit(df[FEATURE_COLUMNS], df[TARGET])

    df_for_app = df.copy()
    df_for_app["model_stress_probability"] = deploy_model.predict_proba(df[FEATURE_COLUMNS])[:, 1]

    artifact = {
        "model": deploy_model,
        "model_name": best_name,
        "feature_columns": FEATURE_COLUMNS,
        "categorical_features": CATEGORICAL_FEATURES,
        "numeric_features": NUMERIC_FEATURES,
        "target": TARGET,
        "train_end_year": TRAIN_END_YEAR,
        "test_start_year": TEST_START_YEAR,
        "dataset_path": str(DATA_PATH.relative_to(REPO_ROOT)),
        "training_rows": int(len(df)),
        "training_years": [int(df["year"].min()), int(df["year"].max())],
    }
    joblib.dump(artifact, ARTIFACT_DIR / "risk_model.joblib")

    df_for_app.to_csv(ARTIFACT_DIR / "scored_history.csv", index=False)
    importance.to_csv(ARTIFACT_DIR / "feature_importance.csv", index=False)
    (ARTIFACT_DIR / "feature_columns.json").write_text(
        json.dumps(FEATURE_COLUMNS, indent=2), encoding="utf-8"
    )
    (ARTIFACT_DIR / "metrics.json").write_text(
        json.dumps(metrics, indent=2), encoding="utf-8"
    )

    print("VinhaGuard ML training complete")
    print(f"Rows: {len(df):,}; target rate: {df[TARGET].mean():.1%}")
    print(f"Saved model: {ARTIFACT_DIR / 'risk_model.joblib'}")
    print("\nChronological holdout metrics:")
    for name, values in metrics["models"].items():
        print(f"  {name}:")
        for key in ["roc_auc", "average_precision", "brier_score", "accuracy", "precision", "recall", "f1"]:
            if key in values:
                print(f"    {key}: {values[key]}")
    print("\nTop feature drivers:")
    print(importance.head(10).to_string(index=False))

    return metrics


def main() -> None:
    train_and_evaluate()


if __name__ == "__main__":
    main()
