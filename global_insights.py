"""Compute global model insights: SHAP, learning curves, per-city metrics."""
import sys
from pathlib import Path
import joblib
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
sys.path.insert(0, str(BASE_DIR))

from predictor import load_artifacts


def compute_global_shap(sample_size=200, random_state=42):
    """Compute SHAP values on a sample of training data."""
    import shap
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler, OneHotEncoder
    from sklearn.compose import ColumnTransformer

    model, metadata, mappings = load_artifacts()
    df = pd.read_csv(BASE_DIR / "data" / "features_data_v3.csv")

    CATEGORICAL = metadata["features"]["categorical"]
    NUMERICAL = metadata["features"]["numerical"]

    X = df[NUMERICAL + CATEGORICAL].copy()
    if len(X) > sample_size:
        X_sample = X.sample(n=sample_size, random_state=random_state)
    else:
        X_sample = X

    prep = model.named_steps["prep"]
    X_enc = prep.transform(X_sample)

    # TreeExplainer on the inner model
    inner = model.named_steps["model"]
    explainer = shap.TreeExplainer(inner)
    shap_values = explainer.shap_values(X_enc)

    feature_names = list(prep.get_feature_names_out())

    # Mean absolute SHAP per feature
    mean_abs = np.abs(shap_values).mean(axis=0)
    order = np.argsort(mean_abs)[::-1][:20]

    result = {
        "feature_names": [feature_names[i] for i in order],
        "mean_abs_shap": [float(mean_abs[i]) for i in order],
        "shap_values_sample": shap_values.tolist(),
        "X_sample_encoded": X_enc.tolist(),
        "all_feature_names": feature_names,
    }
    return result


def compute_per_city_metrics():
    """Compute R2 per city on test split."""
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import r2_score, mean_absolute_error

    model, metadata, mappings = load_artifacts()
    df = pd.read_csv(BASE_DIR / "data" / "features_data_v3.csv")

    CATEGORICAL = metadata["features"]["categorical"]
    NUMERICAL = metadata["features"]["numerical"]

    X = df[NUMERICAL + CATEGORICAL]
    y_log = np.log1p(df["price"])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_log, test_size=0.2, random_state=42
    )

    y_pred = model.predict(X_test)
    y_test_real = np.expm1(y_test)
    y_pred_real = np.expm1(y_pred)

    cities = X_test["city"].values
    metrics = {}
    for city in sorted(set(cities)):
        mask = cities == city
        if mask.sum() < 5:
            continue
        r2 = r2_score(y_test_real[mask], y_pred_real[mask])
        mae = mean_absolute_error(y_test_real[mask], y_pred_real[mask])
        mape = np.mean(np.abs((y_test_real[mask] - y_pred_real[mask]) /
                                y_test_real[mask])) * 100
        metrics[city] = {
            "r2": float(r2),
            "mae": float(mae),
            "mape": float(mape),
            "n": int(mask.sum()),
        }
    return metrics


def compute_learning_curves():
    """Learning curve: R2 vs training set size."""
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import r2_score

    model, metadata, _ = load_artifacts()
    df = pd.read_csv(BASE_DIR / "data" / "features_data_v3.csv")

    CATEGORICAL = metadata["features"]["categorical"]
    NUMERICAL = metadata["features"]["numerical"]

    X = df[NUMERICAL + CATEGORICAL]
    y_log = np.log1p(df["price"])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_log, test_size=0.2, random_state=42
    )

    sizes = [500, 1000, 2000, 3000, 4000, 5000, len(X_train)]
    results = {"sizes": [], "train_r2": [], "test_r2": []}

    for n in sizes:
        if n > len(X_train):
            continue
        X_sub = X_train.iloc[:n]
        y_sub = y_train.iloc[:n]

        # Refit only the inner model on the sub-sample using the fitted pipeline's prep
        prep = model.named_steps["prep"]
        X_sub_enc = prep.transform(X_sub)
        X_test_enc = prep.transform(X_test)

        from sklearn.ensemble import GradientBoostingRegressor
        inner = GradientBoostingRegressor(
            n_estimators=192, max_depth=3, learning_rate=0.075,
            subsample=0.873, random_state=42,
        )
        inner.fit(X_sub_enc, y_sub)

        train_r2 = r2_score(y_sub, inner.predict(X_sub_enc))
        test_r2 = r2_score(y_test, inner.predict(X_test_enc))

        results["sizes"].append(int(n))
        results["train_r2"].append(float(train_r2))
        results["test_r2"].append(float(test_r2))

    return results


def compute_residuals():
    """Compute test-set residuals for analysis."""
    from sklearn.model_selection import train_test_split

    model, metadata, _ = load_artifacts()
    df = pd.read_csv(BASE_DIR / "data" / "features_data_v3.csv")

    CATEGORICAL = metadata["features"]["categorical"]
    NUMERICAL = metadata["features"]["numerical"]

    X = df[NUMERICAL + CATEGORICAL]
    y_log = np.log1p(df["price"])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_log, test_size=0.2, random_state=42
    )

    y_pred = np.expm1(model.predict(X_test))
    y_test_real = np.expm1(y_test)
    residuals = y_test_real - y_pred

    return {
        "y_true": y_test_real.tolist()[:500],
        "y_pred": y_pred.tolist()[:500],
        "residuals": residuals.tolist()[:500],
    }


def build_all_insights():
    """Generate all insight artifacts and save them."""
    print("🔄 Computing global SHAP...")
    shap_data = compute_global_shap()

    print("🔄 Computing per-city metrics...")
    city_metrics = compute_per_city_metrics()

    print("🔄 Computing learning curves...")
    lc_data = compute_learning_curves()

    print("🔄 Computing residuals...")
    residual_data = compute_residuals()

    payload = {
        "global_shap": shap_data,
        "city_metrics": city_metrics,
        "learning_curves": lc_data,
        "residuals": residual_data,
    }

    out_path = MODELS_DIR / "global_insights.joblib"
    joblib.dump(payload, out_path)
    print(f"✅ Saved: {out_path}")
    return payload


if __name__ == "__main__":
    build_all_insights()
