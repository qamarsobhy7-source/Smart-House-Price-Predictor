"""Comprehensive test suite for Smart House Price Predictor v7.0 (Real Data)"""
import sys
import unittest
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from predictor import (
    load_artifacts, get_category_values, validate_input,
    build_features, predict_price, predict_with_confidence,
    format_price, extract_nlp_features, calculate_roi,
)


class TestArtifactsLoading(unittest.TestCase):
    def test_load_artifacts(self):
        model, metadata, mappings = load_artifacts()
        self.assertIsNotNone(model)
        self.assertIn("model_name", metadata)
        self.assertIn("price_mappings", mappings)

    def test_metadata_metrics(self):
        _, metadata, _ = load_artifacts()
        m = metadata["metrics"]
        self.assertGreater(m["r2"], 0.5)
        self.assertLess(m["mape"], 30)

    def test_data_source_is_real(self):
        _, metadata, _ = load_artifacts()
        source = metadata["training_info"].get("source", "")
        self.assertIn("PropertyFinder", source)


class TestValidation(unittest.TestCase):
    def test_valid_input(self):
        errors = validate_input(150, "3", 2, "Cairo", "New Cairo City", "Madinaty")
        self.assertEqual(errors, [])

    def test_negative_area(self):
        errors = validate_input(-50, "3", 2, "Cairo", "New Cairo City", "None")
        self.assertTrue(any("Area" in e for e in errors))

    def test_too_small_area(self):
        errors = validate_input(10, "3", 2, "Cairo", "New Cairo City", "None")
        self.assertTrue(any("Area" in e for e in errors))

    def test_invalid_bedrooms(self):
        errors = validate_input(150, "99", 2, "Cairo", "New Cairo City", "None")
        self.assertTrue(len(errors) > 0)

    def test_missing_city(self):
        errors = validate_input(150, "3", 2, "", "New Cairo City", "None")
        self.assertTrue(any("City" in e for e in errors))

    def test_studio_valid(self):
        errors = validate_input(80, "studio", 1, "Cairo", "New Cairo City", "None")
        self.assertEqual(errors, [])


class TestFeatureBuilding(unittest.TestCase):
    def setUp(self):
        _, _, self.mappings = load_artifacts()

    def test_returns_dataframe(self):
        import pandas as pd
        feat = build_features(
            area=150, bedrooms="3", bathrooms=2,
            city="Cairo", district="New Cairo City", compound="Madinaty",
            description="Luxury apartment", amenities=["BA", "SE"],
            mappings=self.mappings,
        )
        self.assertIsInstance(feat, pd.DataFrame)
        self.assertEqual(len(feat), 1)

    def test_feature_count_matches_model(self):
        _, metadata, self.mappings = load_artifacts()
        feat = build_features(
            area=150, bedrooms="3", bathrooms=2,
            city="Cairo", district="New Cairo City", compound="None",
            mappings=self.mappings,
        )
        expected = metadata["features"]["total"]
        self.assertEqual(feat.shape[1], expected)

    def test_amenities_encoded(self):
        feat = build_features(
            area=150, bedrooms="3", bathrooms=2,
            city="Cairo", district="New Cairo City", compound="None",
            amenities=["BA", "SE", "PG"],
            mappings=self.mappings,
        )
        self.assertEqual(feat["amenity_count"].iloc[0], 3)

    def test_studio_features(self):
        feat = build_features(
            area=80, bedrooms="studio", bathrooms=1,
            city="Cairo", district="New Cairo City", compound="None",
            mappings=self.mappings,
        )
        self.assertEqual(feat["bedrooms"].iloc[0], 0)

    def test_nlp_features_present(self):
        feat = build_features(
            area=150, bedrooms="3", bathrooms=2,
            city="Cairo", district="New Cairo City", compound="None",
            description="Sea view luxury apartment",
            mappings=self.mappings,
        )
        nlp_cols = [c for c in feat.columns if c.startswith("nlp_")]
        self.assertGreater(len(nlp_cols), 5)


class TestNLP(unittest.TestCase):
    def test_sea_view(self):
        r = extract_nlp_features("sea view apartment")
        self.assertEqual(r["nlp_sea_view"], 1)

    def test_garden(self):
        r = extract_nlp_features("apartment with garden")
        self.assertEqual(r["nlp_garden"], 1)

    def test_furnished(self):
        r = extract_nlp_features("fully furnished flat")
        self.assertEqual(r["nlp_furnished"], 1)

    def test_empty(self):
        r = extract_nlp_features("")
        self.assertEqual(r["nlp_sea_view"], 0)
        self.assertEqual(r["title_length"], 0)

    def test_luxury(self):
        r = extract_nlp_features("luxury super lux villa")
        self.assertEqual(r["nlp_luxury"], 1)


class TestPrediction(unittest.TestCase):
    def setUp(self):
        self.model, self.metadata, self.mappings = load_artifacts()

    def test_positive_price(self):
        feat = build_features(
            area=150, bedrooms="3", bathrooms=2,
            city="Cairo", district="New Cairo City", compound="None",
            mappings=self.mappings,
        )
        price = predict_price(self.model, feat)
        self.assertGreater(price, 0)

    def test_realistic_range(self):
        feat = build_features(
            area=150, bedrooms="3", bathrooms=2,
            city="Cairo", district="New Cairo City", compound="None",
            mappings=self.mappings,
        )
        price = predict_price(self.model, feat)
        self.assertGreater(price, 500_000)
        self.assertLess(price, 50_000_000)

    def test_confidence_interval(self):
        feat = build_features(
            area=150, bedrooms="3", bathrooms=2,
            city="Cairo", district="New Cairo City", compound="None",
            mappings=self.mappings,
        )
        result = predict_with_confidence(self.model, feat, mape=18.0)
        self.assertLess(result["lower_bound"], result["price"])
        self.assertGreater(result["upper_bound"], result["price"])

    def test_larger_is_more_expensive(self):
        small = build_features(
            area=80, bedrooms="2", bathrooms=1,
            city="Cairo", district="New Cairo City", compound="None",
            mappings=self.mappings,
        )
        large = build_features(
            area=300, bedrooms="4", bathrooms=3,
            city="Cairo", district="New Cairo City", compound="None",
            mappings=self.mappings,
        )
        price_small = predict_price(self.model, small)
        price_large = predict_price(self.model, large)
        self.assertGreater(price_large, price_small)


class TestFormatting(unittest.TestCase):
    def test_millions(self):
        result = format_price(7_500_000)
        self.assertIn("M", result)
        self.assertIn("EGP", result)

    def test_thousands(self):
        result = format_price(500_000)
        self.assertIn("EGP", result)


class TestCategories(unittest.TestCase):
    def test_categories_loaded(self):
        _, _, mappings = load_artifacts()
        cats = get_category_values(mappings)
        self.assertIn("city", cats)
        self.assertIn("district", cats)
        self.assertIn("compound", cats)
        self.assertGreater(len(cats["city"]), 5)


class TestROI(unittest.TestCase):
    def test_roi_calculation(self):
        roi = calculate_roi(5_000_000, years=5)
        self.assertGreater(roi["roi_pct"], 0)
        self.assertGreater(roi["future_value"], 5_000_000)

    def test_roi_years(self):
        roi_5 = calculate_roi(5_000_000, years=5)
        roi_10 = calculate_roi(5_000_000, years=10)
        self.assertGreater(roi_10["total_return"], roi_5["total_return"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
