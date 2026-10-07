"""Model bundle, simulator labels and SHAP attribution.

The metric floors below are regression guards on the synthetic training data.
They do not show real-world predictive power: labels are a deterministic
function of the simulator's wear level.
"""
import numpy as np

from app.etl.simulator.services import (
    FAILURE_WEAR_THRESHOLD,
    RUL_HOURS_AT_NEW,
    sample_readings,
)
from app.ml.models import COMPONENTS, FEATURE_COLUMNS, attribute, feature_row, get_bundle


def test_simulator_labels_follow_wear_rules():
    rng = np.random.default_rng(0)
    wear = np.array([0.0, 0.5, FAILURE_WEAR_THRESHOLD + 0.01, 1.0])
    out = sample_readings(wear, rng)
    assert out["failure_risk_7_day"].tolist() == [0, 0, 1, 1]
    # RUL is linear in wear (1200h new -> 0h fully worn), truncated to whole hours.
    expected = RUL_HOURS_AT_NEW * (1 - wear)
    assert np.all(np.abs(out["rul_hours"] - expected) < 1)
    assert out["rul_hours"][0] == RUL_HOURS_AT_NEW and out["rul_hours"][-1] == 0


def test_bundle_metrics_meet_regression_floors():
    m = get_bundle().metrics
    assert m["risk_roc_auc"] > 0.95
    assert m["risk_accuracy"] > 0.90
    assert 0.80 <= m["rul_interval_coverage_90"] <= 1.0


def test_bundle_is_cached_and_versioned():
    assert get_bundle() is get_bundle()
    assert get_bundle().version.startswith("xgb-")
    assert "synthetic" in get_bundle().version


def test_attribution_shape_and_normalisation():
    bundle = get_bundle()
    x = feature_row({name: 1.0 for name in FEATURE_COLUMNS})
    per_feature, shares, top = attribute(bundle, x)
    assert set(per_feature) == set(FEATURE_COLUMNS)
    assert set(shares) == set(COMPONENTS)
    assert abs(sum(shares.values()) - 1.0) < 1e-3
    assert top in COMPONENTS


def test_high_wear_window_scores_higher_risk_than_healthy():
    bundle = get_bundle()
    healthy = feature_row(
        {"vibration_mean": 2.5, "vibration_std": 0.2, "temperature_mean": 65.0,
         "temperature_std": 1.5, "pressure_mean": 600.0, "pressure_std": 10.0,
         "motor_current_mean": 120.0}
    )
    failing = feature_row(
        {"vibration_mean": 2.5 + 6.5, "vibration_std": 0.2, "temperature_mean": 65.0 + 35.0,
         "temperature_std": 1.5, "pressure_mean": 600.0 - 80.0, "pressure_std": 10.0,
         "motor_current_mean": 120.0 + 45.0}
    )
    p_healthy = bundle.risk.predict_proba(healthy)[0, 1]
    p_failing = bundle.risk.predict_proba(failing)[0, 1]
    assert p_failing > 0.5 > p_healthy
