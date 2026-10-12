"""Tests for the Streamlit app."""
import pytest
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
APP_FILE = BASE / "streamlit_app.py"


def test_app_file_exists():
    """Main app file should exist."""
    assert APP_FILE.exists(), f"Missing: {APP_FILE}"


def test_app_compiles():
    """App should compile without syntax errors."""
    result = subprocess.run(
        ["python", "-m", "py_compile", str(APP_FILE)],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"Compile error: {result.stderr}"


def test_app_has_streamlit_import():
    """App should import streamlit."""
    content = APP_FILE.read_text()
    assert "import streamlit" in content


def test_app_has_main_sections():
    """App should have key sections."""
    content = APP_FILE.read_text()
    sections = ["Hero", "Form", "Result"]
    for s in sections:
        assert s.lower() in content.lower() or s in content, f"Missing: {s}"


def test_key_modules_compile():
    """Key modules should compile."""
    modules = [
        "predictor.py",
        "translations.py",
        "location_selector.py",
        "popular_areas.py",
        "property_types.py",
        "featured_properties.py",
        "filters_chips.py",
        "neighborhood_insights.py",
        "mortgage_calculator.py",
    ]
    for m in modules:
        path = BASE / m
        if not path.exists():
            continue
        result = subprocess.run(
            ["python", "-m", "py_compile", str(path)],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"{m} compile error: {result.stderr}"


def test_translations_complete():
    """Translations should have EN and AR."""
    sys.path.insert(0, str(BASE))
    from translations import TRANSLATIONS
    assert "en" in TRANSLATIONS
    assert "ar" in TRANSLATIONS
    assert len(TRANSLATIONS["en"]) > 100
    assert len(TRANSLATIONS["ar"]) > 100


def test_translations_keys_match():
    """EN and AR should have same keys."""
    sys.path.insert(0, str(BASE))
    from translations import TRANSLATIONS
    en_keys = set(TRANSLATIONS["en"].keys())
    ar_keys = set(TRANSLATIONS["ar"].keys())
    missing = en_keys - ar_keys
    assert len(missing) == 0, f"Missing in AR: {missing}"
