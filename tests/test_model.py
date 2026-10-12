"""Tests for the trained model."""
import pytest
import joblib
import numpy as np
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE / "models" / "real_model.joblib"
METADATA_PATH = BASE / "models" / "real_model_metadata.joblib"
FEATURES_PATH = BASE / "data" / "processed" / "features.csv"


@pytest.fixture(scope="module")
def model():
    """Load trained model."""
    if not MODEL_PATH.exists():
        pytest.skip(f"Model not found: {MODEL_PATH}")
    return joblib.load(MODEL_PATH)


@pytest.fixture(scope="module")
def metadata():
    """Load model metadata."""
    if not METADATA_PATH.exists():
        pytest.skip(f"Metadata not found: {METADATA_PATH}")
    return joblib.load(METADATA_PATH)


@pytest.fixture(scope="module")
def test_features():
    """Load feature data for inference."""
    if not FEATURES_PATH.exists():
        pytest.skip("Features not found")
    df = pd.read_csv(FEATURES_PATH)
    return df.drop("price", axis=1).head(10)


# ═══════════════════════════════════════════════════════
# MODEL LOADING
# ═══════════════════════════════════════════════════════

def test_model_file_exists():
    """Model file should exist."""
    assert MODEL_PATH.exists()


def test_model_loads(model):
    """Model should load without errors."""
    assert model is not None


def test_model_has_predict(model):
    """Model should have predict method."""
    assert hasattr(model, "predict")


def test_metadata_loads(metadata):
    """Metadata should load."""
    assert metadata is not None
    assert "metrics" in metadata
    assert "training_info" in metadata


# ═══════════════════════════════════════════════════════
# PREDICTIONS
# ═══════════════════════════════════════════════════════

def test_prediction_works(model, test_features):
    """Model should produce predictions."""
    preds = model.predict(test_features)
    assert len(preds) == len(test_features)


def test_predictions_positive(model, test_features):
    """Predictions should be positive."""
    preds = model.predict(test_features)
    assert (preds > 0).all(), "Negative predictions found"


def test_predictions_reasonable(model, test_features):
    """Predictions should be in reasonable range."""
    preds = model.predict(test_features)
    assert preds.min() > 100_000, f"Too low: {preds.min()}"
    assert preds.max() < 500_000_000, f"Too high: {preds.max()}"


def test_predictions_deterministic(model, test_features):
    """Same input → same output."""
    p1 = model.predict(test_features)
    p2 = model.predict(test_features)
    np.testing.assert_array_equal(p1, p2)


# ═══════════════════════════════════════════════════════
# METRICS
# ═══════════════════════════════════════════════════════

def test_r2_reasonable(metadata):
    """R² should meet threshold."""
    r2 = metadata["metrics"]["r2"]
    assert r2 >= 0.5, f"R² too low: {r2}"
    assert r2 <= 1.0, f"R² invalid: {r2}"


def test_mape_reasonable(metadata):
    """MAPE should be acceptable."""
    mape = metadata["metrics"]["mape"]
    assert mape < 30, f"MAPE too high: {mape}%"
    assert mape > 0, f"MAPE invalid: {mape}"


def test_training_info_complete(metadata):
    """Training info should be complete."""
    info = metadata["training_info"]
    assert info["n_total"] > 0
    assert info["n_features"] > 0
