"""Lightweight model monitoring: log predictions and detect drift."""
import json
from datetime import datetime
from pathlib import Path
import numpy as np
import joblib

BASE_DIR = Path(__file__).resolve().parent
MONITORING_DIR = BASE_DIR / "monitoring"
MONITORING_DIR.mkdir(exist_ok=True)
LOG_PATH = MONITORING_DIR / "predictions_log.json"
BASELINE_PATH = BASE_DIR / "models" / "monitoring_baseline.joblib"
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


def log_prediction(area, bedrooms, bathrooms, city, town, district,
                    predicted_price, confidence_lower=None, confidence_upper=None):
    """Log a single prediction for monitoring."""
    log = _load_log()

    log["predictions"].append({
        "timestamp": datetime.now().isoformat(),
        "area": float(area),
        "bedrooms": str(bedrooms),
        "bathrooms": int(bathrooms),
        "city": str(city),
        "town": str(town),
        "district": str(district),
        "predicted_price": float(predicted_price),
        "confidence_lower": float(confidence_lower) if confidence_lower else None,
        "confidence_upper": float(confidence_upper) if confidence_upper else None,
    })

    # Cap log size
    if len(log["predictions"]) > MAX_LOG_ENTRIES:
        log["predictions"] = log["predictions"][-MAX_LOG_ENTRIES:]

    log["total_predictions"] = len(log["predictions"])
    log["last_updated"] = datetime.now().isoformat()
    _save_log(log)


def get_monitoring_stats():
    """Compute drift and distribution statistics."""
    log = _load_log()
    preds = log.get("predictions", [])

    if not preds:
        return {
            "total_predictions": 0,
            "has_data": False,
            "baseline": _load_baseline(),
        }

    prices = np.array([p["predicted_price"] for p in preds])
    areas = np.array([p["area"] for p in preds])

    city_counts = {}
    for p in preds:
        city_counts[p["city"]] = city_counts.get(p["city"], 0) + 1

    baseline = _load_baseline()
    drift = _detect_drift(prices, baseline)

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
        "baseline": baseline,
        "drift": drift,
        "recent": preds[-10:][::-1],
        "all_prices": prices.tolist(),
    }


def _load_baseline():
    if BASELINE_PATH.exists():
        try:
            return joblib.load(BASELINE_PATH)
        except Exception:
            return {}
    return {}


def _detect_drift(current_prices, baseline):
    """Simple drift detection: z-score of mean vs baseline."""
    if not baseline or "mean_price" not in baseline:
        return {"status": "no_baseline"}

    base_mean = baseline["mean_price"]
    base_std = baseline.get("std_price", 1)
    current_mean = float(np.mean(current_prices))

    if base_std == 0:
        z = 0
    else:
        z = abs(current_mean - base_mean) / base_std

    if z < 0.5:
        status = "healthy"
    elif z < 1.0:
        status = "warning"
    else:
        status = "drift_detected"

    return {
        "status": status,
        "z_score": float(z),
        "baseline_mean": float(base_mean),
        "current_mean": float(current_mean),
    }


def clear_log():
    """Reset the predictions log (admin action)."""
    _save_log({"total_predictions": 0, "predictions": [], "last_updated": None})
