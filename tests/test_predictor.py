"""Comprehensive test suite for Smart House Price Predictor v3.0"""
import sys
import unittest
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from predictor import (
    load_artifacts,
    get_category_values,
    validate_input,
    build_features,
    predict_price,
    predict_with_confidence,
    format_price,
    extract_nlp_features,
)


class TestArtifactsLoading(unittest.TestCase):
    """Test artifact loading."""

    def test_load_artifacts(self):
        model, metadata, mappings = load_artifacts()
        self.assertIsNotNone(model)
        self.assertIn("model_name", metadata)
        self.assertIn("price_mappings", mappings)

    def test_metadata_metrics(self):
        _, metadata, _ = load_artifacts()
        metrics = metadata["metrics"]
        self.assertGreater(metrics["r2"], 0.9)
        self.assertLess(metrics["mape"], 15)


class TestValidation(unittest.TestCase):
    """Test input validation."""

    def test_valid_input(self):
        errors = validate_input(
            area=150, bedrooms="3", bathrooms=2,
            city="Cairo", town="New Cairo", district="Madinaty",
            subdistrict="1st", furnished="No", completion_status="completed",
        )
        self.assertEqual(errors, [])

    def test_negative_area(self):
        errors = validate_input(
            area=-50, bedrooms="3", bathrooms=2,
            city="Cairo", town="New Cairo", district="Madinaty",
            subdistrict="1st", furnished="No", completion_status="completed",
        )
        self.assertTrue(any("Area" in e for e in errors))

    def test_too_small_area(self):
        errors = validate_input(
            area=10, bedrooms="3", bathrooms=2,
            city="Cairo", town="New Cairo", district="Madinaty",
            subdistrict="1st", furnished="No", completion_status="completed",
        )
        self.assertTrue(any("Area" in e for e in errors))

    def test_invalid_bedrooms(self):
        errors = validate_input(
            area=150, bedrooms="99", bathrooms=2,
            city="Cairo", town="New Cairo", district="Madinaty",
            subdistrict="1st", furnished="No", completion_status="completed",
        )
        self.assertTrue(len(errors) > 0)

    def test_missing_city(self):
        errors = validate_input(
            area=150, bedrooms="3", bathrooms=2,
            city="", town="New Cairo", district="Madinaty",
            subdistrict="1st", furnished="No", completion_status="completed",
        )
        self.assertTrue(any("City" in e for e in errors))

    def test_studio_bedrooms(self):
        errors = validate_input(
            area=80, bedrooms="studio", bathrooms=1,
            city="Cairo", town="New Cairo", district="Madinaty",
            subdistrict="1st", furnished="No", completion_status="completed",
        )
        self.assertEqual(errors, [])


class TestFeatureBuilding(unittest.TestCase):
    """Test feature building."""

    def setUp(self):
        _, _, self.mappings = load_artifacts()

    def test_build_features_returns_dataframe(self):
        import pandas as pd
        features = build_features(
            area=150, bedrooms="3", bathrooms=2,
            city="Cairo", town="New Cairo", district="Madinaty",
            subdistrict="1st", furnished="No", completion_status="completed",
            mappings=self.mappings,
        )
        self.assertIsInstance(features, pd.DataFrame)
        self.assertEqual(len(features), 1)

    def test_all_features_present(self):
        features = build_features(
            area=150, bedrooms="3", bathrooms=2,
            city="Cairo", town="New Cairo", district="Madinaty",
            subdistrict="1st", furnished="No", completion_status="completed",
            mappings=self.mappings,
        )
        expected = ["area_value", "bedrooms_clean", "bathrooms_clean",
                    "city_price_per_sqm", "district_price_per_sqm",
                    "town_price_per_sqm", "city", "town", "district",
                    "nlp_sea_view", "nlp_garden", "nlp_furnished"]
        for col in expected:
            self.assertIn(col, features.columns)

    def test_total_feature_count(self):
        features = build_features(
            area=150, bedrooms="3", bathrooms=2,
            city="Cairo", town="New Cairo", district="Madinaty",
            subdistrict="1st", furnished="No", completion_status="completed",
            mappings=self.mappings,
        )
        self.assertEqual(features.shape[1], 38)

    def test_studio_features(self):
        features = build_features(
            area=80, bedrooms="studio", bathrooms=1,
            city="Cairo", town="New Cairo", district="Madinaty",
            subdistrict="1st", furnished="No", completion_status="completed",
            mappings=self.mappings,
        )
        self.assertEqual(features["is_studio"].iloc[0], 1)
        self.assertEqual(features["bedrooms_clean"].iloc[0], 0)


class TestNLPFeatures(unittest.TestCase):
    """Test Arabic NLP feature extraction."""

    def test_sea_view_detection(self):
        result = extract_nlp_features("شقة بحرية جميلة")
        self.assertEqual(result["nlp_sea_view"], 1)

    def test_garden_detection(self):
        result = extract_nlp_features("شقة مع حديقة خاصة")
        self.assertEqual(result["nlp_garden"], 1)

    def test_furnished_detection(self):
        result = extract_nlp_features("شقة مفروشة بالكامل")
        self.assertEqual(result["nlp_furnished"], 1)

    def test_empty_description(self):
        result = extract_nlp_features("")
        self.assertEqual(result["nlp_sea_view"], 0)
        self.assertEqual(result["nlp_garden"], 0)
        self.assertEqual(result["description_length"], 0)

    def test_english_keywords(self):
        result = extract_nlp_features("sea view furnished apartment")
        self.assertEqual(result["nlp_sea_view"], 1)
        self.assertEqual(result["nlp_furnished"], 1)

    def test_all_features_returned(self):
        result = extract_nlp_features("test")
        expected_keys = ["nlp_sea_view", "nlp_garden", "nlp_duplex",
                         "nlp_roof", "nlp_furnished", "nlp_new",
                         "nlp_super_lux", "nlp_open_view", "nlp_parking",
                         "nlp_elevator", "description_length",
                         "description_word_count"]
        for key in expected_keys:
            self.assertIn(key, result)


class TestPrediction(unittest.TestCase):
    """Test prediction."""

    def setUp(self):
        self.model, self.metadata, self.mappings = load_artifacts()

    def test_prediction_positive(self):
        features = build_features(
            area=150, bedrooms="3", bathrooms=2,
            city="Cairo", town="New Cairo", district="Madinaty",
            subdistrict="1st", furnished="No", completion_status="completed",
            mappings=self.mappings,
        )
        price = predict_price(self.model, features)
        self.assertGreater(price, 0)

    def test_prediction_realistic_range(self):
        features = build_features(
            area=150, bedrooms="3", bathrooms=2,
            city="Cairo", town="New Cairo", district="Madinaty",
            subdistrict="1st", furnished="No", completion_status="completed",
            mappings=self.mappings,
        )
        price = predict_price(self.model, features)
        self.assertGreater(price, 500_000)
        self.assertLess(price, 50_000_000)

    def test_confidence_interval(self):
        features = build_features(
            area=150, bedrooms="3", bathrooms=2,
            city="Cairo", town="New Cairo", district="Madinaty",
            subdistrict="1st", furnished="No", completion_status="completed",
            mappings=self.mappings,
        )
        result = predict_with_confidence(self.model, features, mape=6.52)
        self.assertLess(result["lower_bound"], result["price"])
        self.assertGreater(result["upper_bound"], result["price"])

    def test_different_areas_different_prices(self):
        small = build_features(
            area=80, bedrooms="2", bathrooms=1,
            city="Cairo", town="New Cairo", district="Madinaty",
            subdistrict="1st", furnished="No", completion_status="completed",
            mappings=self.mappings,
        )
        large = build_features(
            area=300, bedrooms="4", bathrooms=3,
            city="Cairo", town="New Cairo", district="Madinaty",
            subdistrict="1st", furnished="No", completion_status="completed",
            mappings=self.mappings,
        )
        price_small = predict_price(self.model, small)
        price_large = predict_price(self.model, large)
        self.assertGreater(price_large, price_small)


class TestFormatting(unittest.TestCase):
    """Test price formatting."""

    def test_format_millions(self):
        result = format_price(6_920_000)
        self.assertIn("M", result)
        self.assertIn("EGP", result)

    def test_format_thousands(self):
        result = format_price(500_000)
        self.assertIn("EGP", result)


class TestCategories(unittest.TestCase):
    """Test category values."""

    def test_categories_loaded(self):
        _, _, mappings = load_artifacts()
        cats = get_category_values(mappings)
        self.assertIn("city", cats)
        self.assertIn("district", cats)
        self.assertGreater(len(cats["city"]), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
