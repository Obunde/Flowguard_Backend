"""Model bundle for failure risk, RUL and SHAP attribution.

Trained on synthetic windows from the ETL simulator (`app.etl.simulator`),
because the repo has no historical failure data. Features are the Gold
`PumpFeatureWindow` columns so training and serving see the same inputs.

Labels are a deterministic function of the simulator's wear level, so the
metrics here measure the pipeline, not real-world predictive power.
"""
from dataclasses import dataclass
from functools import lru_cache

import numpy as np
import shap
import xgboost as xgb

from app.etl.simulator.services import FAILURE_WEAR_THRESHOLD, RUL_HOURS_AT_NEW, sample_readings

SEED = 42
WINDOW_READINGS = 60  # matches the sample_count the Gold layer writes per window
N_WINDOWS = 6000
QUANTILES = (0.05, 0.5, 0.95)

# Order matters: this is the column order every model is trained and scored on.
FEATURE_COLUMNS: tuple[str, ...] = (
    "vibration_mean",
    "vibration_std",
    "temperature_mean",
    "temperature_std",
    "pressure_mean",
    "pressure_std",
    "motor_current_mean",
)

# Component each feature belongs to, for sub-assembly attribution.
COMPONENT_OF = {
    "vibration_mean": "bearing",
    "vibration_std": "bearing",
    "temperature_mean": "seal",
    "temperature_std": "seal",
    "pressure_mean": "impeller",
    "pressure_std": "impeller",
    "motor_current_mean": "motor",
}
COMPONENTS = ("bearing", "impeller", "seal", "motor")


@dataclass(frozen=True)
class ModelBundle:
    version: str
    risk: xgb.XGBClassifier
    rul: dict[float, xgb.XGBRegressor]
    explainer: shap.TreeExplainer
    metrics: dict[str, float]


def _window_features(
    rng: np.random.Generator, wear: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Per window: mean/std over WINDOW_READINGS simulated readings at one wear level."""
    flat = np.repeat(wear, WINDOW_READINGS)
    sampled = sample_readings(flat, rng)

    def stats(name: str) -> tuple[np.ndarray, np.ndarray]:
        block = sampled[name].reshape(len(wear), WINDOW_READINGS)
        return block.mean(axis=1), block.std(axis=1, ddof=1)

    vib_m, vib_s = stats("vibration_axial_mm_s")
    tmp_m, tmp_s = stats("temperature_bearing_c")
    prs_m, prs_s = stats("pressure_discharge_psi")
    mot_m = sampled["motor_current_amps"].reshape(len(wear), WINDOW_READINGS).mean(axis=1)
    X = np.column_stack([vib_m, vib_s, tmp_m, tmp_s, prs_m, prs_s, mot_m])
    return X, wear


def _auc(y: np.ndarray, score: np.ndarray) -> float:
    """Rank-based ROC AUC (Mann-Whitney U), no sklearn dependency."""
    order = np.argsort(score)
    ranks = np.empty(len(score), dtype=float)
    ranks[order] = np.arange(1, len(score) + 1)
    pos = y == 1
    n_pos, n_neg = pos.sum(), (~pos).sum()
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    return float((ranks[pos].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))


@lru_cache(maxsize=1)
def get_bundle() -> ModelBundle:
    rng = np.random.default_rng(SEED)
    wear = rng.uniform(0.0, 1.0, size=N_WINDOWS)
    X, _ = _window_features(rng, wear)
    y_fail = (wear > FAILURE_WEAR_THRESHOLD).astype(int)
    y_rul_h = np.maximum(0.0, RUL_HOURS_AT_NEW - wear * RUL_HOURS_AT_NEW)

    split = int(N_WINDOWS * 0.8)
    Xtr, Xte = X[:split], X[split:]
    ftr, fte = y_fail[:split], y_fail[split:]
    rtr, rte = y_rul_h[:split], y_rul_h[split:]

    risk = xgb.XGBClassifier(
        n_estimators=200, max_depth=4, learning_rate=0.1, random_state=SEED, eval_metric="logloss"
    )
    risk.fit(Xtr, ftr)
    p_te = risk.predict_proba(Xte)[:, 1]
    pred_te = (p_te >= 0.5).astype(int)
    tp = int(((pred_te == 1) & (fte == 1)).sum())
    fp = int(((pred_te == 1) & (fte == 0)).sum())
    fn = int(((pred_te == 0) & (fte == 1)).sum())

    rul: dict[float, xgb.XGBRegressor] = {}
    for q in QUANTILES:
        m = xgb.XGBRegressor(
            objective="reg:quantileerror",
            quantile_alpha=q,
            n_estimators=300,
            max_depth=4,
            learning_rate=0.05,
            random_state=SEED,
        )
        m.fit(Xtr, rtr)
        rul[q] = m

    lo, mid, hi = (rul[q].predict(Xte) for q in QUANTILES)
    coverage = float(np.mean((rte >= lo) & (rte <= hi)))

    metrics = {
        "risk_accuracy": float((pred_te == fte).mean()),
        "risk_precision": tp / (tp + fp) if tp + fp else float("nan"),
        "risk_recall": tp / (tp + fn) if tp + fn else float("nan"),
        "risk_roc_auc": _auc(fte, p_te),
        "rul_mae_hours": float(np.mean(np.abs(rte - mid))),
        "rul_interval_coverage_90": coverage,
        "train_windows": float(split),
        "test_windows": float(N_WINDOWS - split),
    }
    return ModelBundle(
        version=f"xgb-{xgb.__version__}-synthetic-seed{SEED}",
        risk=risk,
        rul=rul,
        explainer=shap.TreeExplainer(risk),
        metrics=metrics,
    )


def feature_row(features: dict[str, float]) -> np.ndarray:
    """Order a feature dict (from build_feature_vector) into model input."""
    return np.array([[features[name] for name in FEATURE_COLUMNS]], dtype=float)


def attribute(bundle: ModelBundle, x: np.ndarray) -> tuple[dict[str, float], dict[str, float], str]:
    """SHAP attribution for one row.

    Returns (per-feature SHAP in log-odds, component shares summing to 1,
    top component). Component share = summed |SHAP| of its features.
    """
    raw = bundle.explainer.shap_values(x)
    values = raw[1] if isinstance(raw, list) else raw
    row = np.asarray(values).reshape(-1)
    per_feature = {name: float(row[i]) for i, name in enumerate(FEATURE_COLUMNS)}

    magnitude = {c: 0.0 for c in COMPONENTS}
    for name, value in per_feature.items():
        magnitude[COMPONENT_OF[name]] += abs(value)
    total = sum(magnitude.values()) or 1.0
    shares = {c: round(v / total, 4) for c, v in magnitude.items()}
    top = max(shares, key=shares.get)
    return per_feature, shares, top
