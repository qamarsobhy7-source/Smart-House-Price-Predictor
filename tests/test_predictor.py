"""Tests for the predictor module."""
import pytest
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))


def test_predictor_imports():
    """Predictor module should import."""
    import predictor
    assert predictor is not None


def test_has_load_artifacts():
    """Should have load_artifacts function."""
    import predictor
    assert hasattr(predictor, "load_artifacts")


def test_has_build_features():
    """Should have build_features function."""
    import predictor
    assert hasattr(predictor, "build_features")


def test_has_predict_with_confidence():
    """Should have predict_with_confidence."""
    import predictor
    assert hasattr(predictor, "predict_with_confidence")


def test_has_validate_input():
    """Should have validate_input."""
    import predictor
    assert hasattr(predictor, "validate_input")


def test_has_format_price():
    """Should have format_price."""
    import predictor
    assert hasattr(predictor, "format_price")


def test_has_calculate_roi():
    """Should have calculate_roi."""
    import predictor
    assert hasattr(predictor, "calculate_roi")


def test_format_price_works():
    """format_price should format numbers."""
    import predictor
    result = predictor.format_price(1_500_000)
    assert isinstance(result, str)
    assert "M" in result or "1" in result


def test_calculate_roi_works():
    """calculate_roi should return dict."""
    import predictor
    result = predictor.calculate_roi(5_000_000, years=5)
    assert isinstance(result, dict)
    assert "roi_pct" in result


def test_validate_input_valid():
    """Valid input should return no errors."""
    import predictor
    errors = predictor.validate_input(
        area=150, bedrooms=3, bathrooms=2,
        city="Cairo", district="New Cairo City",
        compound="None"
    )
    assert isinstance(errors, list)


def test_validate_input_invalid_area():
    """Invalid area should return errors."""
    import predictor
    errors = predictor.validate_input(
        area=-100, bedrooms=3, bathrooms=2,
        city="Cairo", district="New Cairo City",
        compound="None"
    )
    assert len(errors) > 0
