"""Lightweight model monitoring for Smart House Price Predictor v7.0."""
import json
from datetime import datetime
from pathlib import Path
import numpy as np

BASE_DIR = Path(__file__).resolve().parent
MONITORING_DIR = BASE_DIR / "monitoring"
MONITORING_DIR.mkdir(exist_ok=True)
LOG_PATH = MONITORING_DIR / "predictions_log.json"
MAX_LOG_ENTRIES = 500


def _load_log():
    if LOG_PATH.exists():
        try:
            with open(LOG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"total_predictions": 0, "predictions": [], "last_updated": None}


def _save_log(log):
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)


def log_prediction(area, bedrooms, bathrooms, city, district=None,
                    compound=None, town=None, predicted_price=None,
                    confidence_lower=None, confidence_upper=None, **kwargs):
    """Log a single prediction for monitoring.

    Accepts legacy kwargs (town, district) for backward compatibility.
    """
    log = _load_log()

    log["predictions"].append({
        "timestamp": datetime.now().isoformat(),
        "area": float(area),
        "bedrooms": str(bedrooms),
        "bathrooms": int(bathrooms),
        "city": str(city),
        "district": str(district or town or "Unknown"),
        "compound": str(compound or "None"),
        "predicted_price": float(predicted_price) if predicted_price else 0,
        "confidence_lower": float(confidence_lower) if confidence_lower else None,
        "confidence_upper": float(confidence_upper) if confidence_upper else None,
    })

    if len(log["predictions"]) > MAX_LOG_ENTRIES:
        log["predictions"] = log["predictions"][-MAX_LOG_ENTRIES:]

    log["total_predictions"] = len(log["predictions"])
    log["last_updated"] = datetime.now().isoformat()
    _save_log(log)


def get_monitoring_stats():
    """Compute distribution statistics."""
    log = _load_log()
    preds = log.get("predictions", [])

    if not preds:
        return {"total_predictions": 0, "has_data": False}

    prices = np.array([p["predicted_price"] for p in preds if p["predicted_price"] > 0])
    areas = np.array([p["area"] for p in preds])

    if len(prices) == 0:
        return {"total_predictions": len(preds), "has_data": False}

    city_counts = {}
    for p in preds:
        c = p["city"]
        city_counts[c] = city_counts.get(c, 0) + 1

    return {
        "total_predictions": len(preds),
        "has_data": True,
        "mean_price": float(prices.mean()),
        "median_price": float(np.median(prices)),
        "min_price": float(prices.min()),
        "max_price": float(prices.max()),
        "std_price": float(prices.std()),
        "mean_area": float(areas.mean()),
        "city_distribution": city_counts,
        "recent": preds[-10:][::-1],
        "all_prices": prices.tolist(),
    }


def clear_log():
    _save_log({"total_predictions": 0, "predictions": [], "last_updated": None})
