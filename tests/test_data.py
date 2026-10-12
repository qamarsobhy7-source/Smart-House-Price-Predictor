"""Tests for data quality and structure."""
import pytest
import pandas as pd
import numpy as np
from pathlib import Path

# Paths
BASE = Path(__file__).resolve().parent.parent
DATA_FILE = BASE / "data" / "real_data" / "model_ready_clean.csv"
FEATURES_FILE = BASE / "data" / "processed" / "features.csv"


@pytest.fixture(scope="module")
def raw_data():
    """Load raw listings data."""
    if not DATA_FILE.exists():
        pytest.skip("Raw data not found")
    return pd.read_csv(DATA_FILE)


@pytest.fixture(scope="module")
def features_data():
    """Load engineered features data."""
    if not FEATURES_FILE.exists():
        pytest.skip("Features not found")
    return pd.read_csv(FEATURES_FILE)


# ═══════════════════════════════════════════════════════
# RAW DATA TESTS
# ═══════════════════════════════════════════════════════

def test_raw_data_exists():
    """Raw data file should exist."""
    assert DATA_FILE.exists(), f"Missing: {DATA_FILE}"


def test_raw_data_not_empty(raw_data):
    """Raw data should have rows."""
    assert len(raw_data) > 0, "Dataset is empty"


def test_raw_data_shape(raw_data):
    """Raw data should have expected size."""
    assert raw_data.shape[0] >= 7000, f"Too few rows: {raw_data.shape[0]}"
    assert raw_data.shape[1] >= 50, f"Too few cols: {raw_data.shape[1]}"


def test_raw_data_has_target(raw_data):
    """Raw data should have 'price' column."""
    assert "price" in raw_data.columns, "Missing target column: price"


def test_raw_data_has_location(raw_data):
    """Raw data should have location columns."""
    for col in ["city", "district"]:
        assert col in raw_data.columns, f"Missing column: {col}"


def test_price_positive(raw_data):
    """All prices should be positive."""
    assert (raw_data["price"] > 0).all(), "Negative or zero prices found"


def test_size_range(raw_data):
    """Sizes should be in reasonable range."""
    if "size" in raw_data.columns:
        valid = raw_data["size"].dropna()
        assert valid.min() >= 10, f"Size too small: {valid.min()}"
        assert valid.max() <= 5000, f"Size too large: {valid.max()}"


def test_city_coverage(raw_data):
    """Should have at least 5 governorates."""
    if "city" in raw_data.columns:
        assert raw_data["city"].nunique() >= 5, "Too few governorates"


def test_no_duplicate_ids(raw_data):
    """Listing IDs should be unique."""
    if "id" in raw_data.columns:
        assert raw_data["id"].nunique() == len(raw_data), "Duplicate IDs found"


# ═══════════════════════════════════════════════════════
# FEATURES DATA TESTS
# ═══════════════════════════════════════════════════════

def test_features_exist():
    """Features file should exist after engineering."""
    assert FEATURES_FILE.exists(), f"Missing: {FEATURES_FILE}"


def test_features_have_target(features_data):
    """Features should include target."""
    assert "price" in features_data.columns


def test_features_no_missing(features_data):
    """Features should have no missing values."""
    missing = features_data.isnull().sum().sum()
    assert missing == 0, f"Found {missing} missing values"


def test_features_are_numeric(features_data):
    """All features should be numeric (for ML)."""
    non_numeric = features_data.select_dtypes(exclude=[np.number]).columns
    assert len(non_numeric) == 0, f"Non-numeric: {list(non_numeric)}"


def test_features_count(features_data):
    """Should have enough features."""
    assert features_data.shape[1] >= 30, f"Too few features: {features_data.shape[1]}"
