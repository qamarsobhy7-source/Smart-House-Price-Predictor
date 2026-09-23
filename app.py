"""Smart House Price Predictor - Flask REST API with Swagger (v3.0)"""
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from flasgger import Swagger
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from predictor import (
    load_artifacts, get_category_values, validate_input,
    build_features, predict_price, predict_with_confidence, format_price,
)

app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'Smart House Price Predictor API',
    'uiversion': 3,
    'description': 'AI-powered REST API for Egyptian real estate price prediction',
    'version': '3.0.0',
}
swagger = Swagger(app)


# ---------- Load model ----------
model = None
metadata = {}
mappings = {}
category_values = {}
load_error = None

try:
    model, metadata, mappings = load_artifacts()
    category_values = get_category_values(mappings)
    app.logger.info(f"Model loaded: {metadata['model_name']}")
except Exception as e:
    load_error = str(e)
    app.logger.exception("Model loading failed")


# ============================================================
# HOME
# ============================================================
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "service": "Smart House Price Predictor API",
        "version": "3.0.0",
        "status": "running",
        "endpoints": {
            "predict": "POST /api/predict",
            "health": "GET /api/health",
            "categories": "GET /api/categories",
            "docs": "GET /apidocs/",
        },
    })


# ============================================================
# HEALTH
# ============================================================
@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint.
    ---
    tags:
      - System
    responses:
      200:
        description: Service health status
    """
    status = "healthy" if model is not None else "unhealthy"
    return jsonify({
        "status": status,
        "model_loaded": model is not None,
        "model_name": metadata.get("model_name", "unknown"),
        "r2_score": metadata.get("metrics", {}).get("r2"),
        "mape": metadata.get("metrics", {}).get("mape"),
        "error": load_error,
    }), (200 if model is not None else 503)


# ============================================================
# CATEGORIES
# ============================================================
@app.route("/api/categories", methods=["GET"])
def get_categories_route():
    """Get all available categorical values.
    ---
    tags:
      - Metadata
    responses:
      200:
        description: Available categories for prediction inputs
    """
    return jsonify(category_values)


# ============================================================
# PREDICT
# ============================================================
@app.route("/api/predict", methods=["POST"])
def api_predict():
    """Predict property price.
    ---
    tags:
      - Prediction
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [area, bedrooms, bathrooms, city, town, district, subdistrict, furnished, completion_status]
          properties:
            area:
              type: number
              example: 150
            bedrooms:
              type: string
              example: "3"
            bathrooms:
              type: integer
              example: 2
            city:
              type: string
              example: Cairo
            town:
              type: string
              example: New Cairo
            district:
              type: string
              example: Madinaty
            subdistrict:
              type: string
              example: "1st"
            furnished:
              type: string
              example: "No"
            completion_status:
              type: string
              example: completed
            description:
              type: string
              example: "شقة بحرية مفروشة سوبر لوكس"
            has_reception:
              type: boolean
              example: true
            has_living:
              type: boolean
              example: true
            has_kitchen:
              type: boolean
              example: true
    responses:
      200:
        description: Prediction result
      400:
        description: Validation error
      503:
        description: Model unavailable
    """
    if model is None:
        return jsonify({"error": "Model unavailable"}), 503

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        errors = validate_input(
            area=data.get("area"),
            bedrooms=str(data.get("bedrooms")),
            bathrooms=data.get("bathrooms"),
            city=data.get("city"),
            town=data.get("town"),
            district=data.get("district"),
            subdistrict=data.get("subdistrict"),
            furnished=data.get("furnished"),
            completion_status=data.get("completion_status"),
        )
        if errors:
            return jsonify({"errors": errors}), 400

        features = build_features(
            area=data.get("area"),
            bedrooms=str(data.get("bedrooms")),
            bathrooms=data.get("bathrooms"),
            city=data.get("city"),
            town=data.get("town"),
            district=data.get("district"),
            subdistrict=data.get("subdistrict"),
            furnished=data.get("furnished"),
            completion_status=data.get("completion_status"),
            has_reception=data.get("has_reception", False),
            has_living=data.get("has_living", False),
            has_kitchen=data.get("has_kitchen", False),
            description=data.get("description", ""),
            mappings=mappings,
        )

        mape = metadata["metrics"]["mape"]
        result = predict_with_confidence(model, features, mape)

        return jsonify({
            "success": True,
            "prediction": {
                "price": round(result["price"], 2),
                "price_formatted": format_price(result["price"]),
                "lower_bound": round(result["lower_bound"], 2),
                "upper_bound": round(result["upper_bound"], 2),
                "currency": "EGP",
                "confidence_level": f"{100 - mape:.2f}%",
            },
            "model": {
                "name": metadata["model_name"],
                "r2": metadata["metrics"]["r2"],
                "mape": metadata["metrics"]["mape"],
            },
        })

    except Exception as e:
        app.logger.exception("Prediction error")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
