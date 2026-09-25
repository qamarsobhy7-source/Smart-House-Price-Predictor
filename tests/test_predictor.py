"""Comprehensive test suite for Smart House Price Predictor v11.0"""
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
from arabert_helper import (
    analyze_sentiment, get_sentiment_emoji, keyword_sentiment,
)


class TestArtifactsLoading(unittest.TestCase):
    """Test model loading and metadata."""

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
    """Test input validation."""

    def test_valid_input(self):
        errors = validate_input(150, "3", 2, "Cairo", "Madinaty", "None")
        self.assertEqual(errors, [])

    def test_negative_area(self):
        errors = validate_input(-50, "3", 2, "Cairo", "Madinaty", "None")
        self.assertTrue(any("Area" in e for e in errors))

    def test_too_small_area(self):
        errors = validate_input(10, "3", 2, "Cairo", "Madinaty", "None")
        self.assertTrue(any("Area" in e for e in errors))

    def test_too_big_area(self):
        errors = validate_input(600, "3", 2, "Cairo", "Madinaty", "None")
        self.assertTrue(any("Area" in e for e in errors))

    def test_invalid_bedrooms(self):
        errors = validate_input(150, "99", 2, "Cairo", "Madinaty", "None")
        self.assertTrue(len(errors) > 0)

    def test_missing_city(self):
        errors = validate_input(150, "3", 2, "", "Madinaty", "None")
        self.assertTrue(any("City" in e for e in errors))

    def test_studio_valid(self):
        errors = validate_input(80, "studio", 1, "Cairo", "Madinaty", "None")
        self.assertEqual(errors, [])


class TestFeatureBuilding(unittest.TestCase):
    """Test feature building."""

    def setUp(self):
        _, _, self.mappings = load_artifacts()

    def test_returns_dataframe(self):
        import pandas as pd
        feat = build_features(
            area=150, bedrooms="3", bathrooms=2,
            city="Cairo", district="Madinaty", compound="None",
            description="Luxury apartment", amenities=["BA", "SE"],
            mappings=self.mappings,
        )
        self.assertIsInstance(feat, pd.DataFrame)
        self.assertEqual(len(feat), 1)

    def test_feature_count_matches_model(self):
        _, metadata, self.mappings = load_artifacts()
        feat = build_features(
            area=150, bedrooms="3", bathrooms=2,
            city="Cairo", district="Madinaty", compound="None",
            mappings=self.mappings,
        )
        self.assertEqual(feat.shape[1], metadata["features"]["total"])

    def test_amenities_encoded(self):
        feat = build_features(
            area=150, bedrooms="3", bathrooms=2,
            city="Cairo", district="Madinaty", compound="None",
            amenities=["BA", "SE", "PG"],
            mappings=self.mappings,
        )
        self.assertEqual(feat["amenity_count"].iloc[0], 3)

    def test_studio_features(self):
        """Studio should have bedrooms = 0 (no bedrooms)."""
        feat = build_features(
            area=80, bedrooms="studio", bathrooms=1,
            city="Cairo", district="Madinaty", compound="None",
            mappings=self.mappings,
        )
        # Studio → bedrooms = 0 (has no separate bedrooms)
        self.assertEqual(feat["bedrooms"].iloc[0], 0)

    def test_nlp_features_present(self):
        feat = build_features(
            area=150, bedrooms="3", bathrooms=2,
            city="Cairo", district="Madinaty", compound="None",
            description="Sea view luxury apartment",
            mappings=self.mappings,
        )
        nlp_cols = [c for c in feat.columns if c.startswith("nlp_")]
        self.assertGreater(len(nlp_cols), 5)


class TestNLP(unittest.TestCase):
    """Test English NLP extraction."""

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

    def test_luxury(self):
        r = extract_nlp_features("luxury super lux villa")
        self.assertEqual(r["nlp_luxury"], 1)


class TestAraBERTSentiment(unittest.TestCase):
    """Test Arabic sentiment analysis (AraBERT + Keywords)."""

    def test_positive_mSA(self):
        r = analyze_sentiment("شقة بحرية مفروشة سوبر لوكس")
        self.assertEqual(r["label"], "positive")

    def test_negative_mSA(self):
        r = analyze_sentiment("شقة قديمة متهالكة")
        self.assertEqual(r["label"], "negative")

    def test_positive_colloquial(self):
        r = analyze_sentiment("الشقة بتجنن والمنظر يجنن")
        self.assertEqual(r["label"], "positive")

    def test_negative_colloquial(self):
        r = analyze_sentiment("مش حلو خالص المكان دة")
        self.assertEqual(r["label"], "negative")

    def test_neutral_no_signal(self):
        r = analyze_sentiment("شقة للبيع")
        self.assertEqual(r["label"], "neutral")

    def test_empty_input(self):
        r = analyze_sentiment("")
        self.assertEqual(r["label"], "neutral")

    def test_conflicting_keywords(self):
        r = analyze_sentiment("الشقة واسعة بس بعيدة")
        self.assertEqual(r["label"], "neutral")

    def test_emoji_mapping(self):
        self.assertEqual(get_sentiment_emoji("positive"), "😊")
        self.assertEqual(get_sentiment_emoji("negative"), "😟")
        self.assertEqual(get_sentiment_emoji("neutral"), "😐")

    def test_keyword_sentiment_range(self):
        score = keyword_sentiment("شقة جميلة")
        self.assertGreaterEqual(score, -1.0)
        self.assertLessEqual(score, 1.0)


class TestTimeSeries(unittest.TestCase):
    """Test time series forecasts."""

    def test_forecasts_loaded(self):
        import joblib
        path = PROJECT_DIR / "models" / "time_series_forecasts.joblib"
        self.assertTrue(path.exists(), "Forecasts file not found")
        forecasts = joblib.load(path)
        self.assertIsInstance(forecasts, dict)
        self.assertGreater(len(forecasts), 5)

    def test_forecast_structure(self):
        import joblib
        forecasts = joblib.load(PROJECT_DIR / "models" / "time_series_forecasts.joblib")
        for city, data in forecasts.items():
            self.assertIn("current_price", data)
            self.assertIn("forecast_12m", data)
            self.assertIn("growth_12m_pct", data)
            self.assertGreater(data["current_price"], 0)
            self.assertGreater(data["forecast_12m"], 0)

    def test_positive_growth(self):
        import joblib
        forecasts = joblib.load(PROJECT_DIR / "models" / "time_series_forecasts.joblib")
        for city, data in forecasts.items():
            self.assertGreater(
                data["growth_12m_pct"], 0,
                f"{city} should have positive growth"
            )


class TestMapData(unittest.TestCase):
    """Test interactive map data."""

    def test_map_data_exists(self):
        path = PROJECT_DIR / "data" / "real_data" / "map_data.csv"
        self.assertTrue(path.exists(), "Map data file not found")

    def test_map_data_structure(self):
        import pandas as pd
        df = pd.read_csv(PROJECT_DIR / "data" / "real_data" / "map_data.csv")
        required = ["latitude", "longitude", "city", "district", "price_m"]
        for col in required:
            self.assertIn(col, df.columns)
        self.assertGreater(len(df), 100)

    def test_map_coordinates_valid(self):
        import pandas as pd
        df = pd.read_csv(PROJECT_DIR / "data" / "real_data" / "map_data.csv")
        # Egypt coordinates range
        self.assertTrue((df["latitude"] > 22).all())
        self.assertTrue((df["latitude"] < 32).all())
        self.assertTrue((df["longitude"] > 24).all())
        self.assertTrue((df["longitude"] < 36).all())


class TestPrediction(unittest.TestCase):
    """Test prediction pipeline."""

    def setUp(self):
        self.model, self.metadata, self.mappings = load_artifacts()

    def test_positive_price(self):
        feat = build_features(
            area=150, bedrooms="3", bathrooms=2,
            city="Cairo", district="Madinaty", compound="None",
            mappings=self.mappings,
        )
        price = predict_price(self.model, feat)
        self.assertGreater(price, 0)

    def test_realistic_range(self):
        feat = build_features(
            area=150, bedrooms="3", bathrooms=2,
            city="Cairo", district="Madinaty", compound="None",
            mappings=self.mappings,
        )
        price = predict_price(self.model, feat)
        self.assertGreater(price, 500_000)
        self.assertLess(price, 50_000_000)

    def test_confidence_interval(self):
        feat = build_features(
            area=150, bedrooms="3", bathrooms=2,
            city="Cairo", district="Madinaty", compound="None",
            mappings=self.mappings,
        )
        result = predict_with_confidence(self.model, feat, mape=18.39)
        self.assertLess(result["lower_bound"], result["price"])
        self.assertGreater(result["upper_bound"], result["price"])

    def test_larger_is_more_expensive(self):
        small = build_features(
            area=80, bedrooms="2", bathrooms=1,
            city="Cairo", district="Madinaty", compound="None",
            mappings=self.mappings,
        )
        large = build_features(
            area=300, bedrooms="4", bathrooms=3,
            city="Cairo", district="Madinaty", compound="None",
            mappings=self.mappings,
        )
        self.assertGreater(
            predict_price(self.model, large),
            predict_price(self.model, small)
        )


class TestFormatting(unittest.TestCase):
    """Test price formatting."""

    def test_millions(self):
        result = format_price(6_920_000)
        self.assertIn("M", result)
        self.assertIn("EGP", result)

    def test_thousands(self):
        result = format_price(500_000)
        self.assertIn("EGP", result)


class TestCategories(unittest.TestCase):
    """Test category values."""

    def test_categories_loaded(self):
        _, _, mappings = load_artifacts()
        cats = get_category_values(mappings)
        self.assertIn("city", cats)
        self.assertIn("district", cats)
        self.assertIn("compound", cats)
        self.assertGreater(len(cats["city"]), 5)


class TestROI(unittest.TestCase):
    """Test ROI calculations."""

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
