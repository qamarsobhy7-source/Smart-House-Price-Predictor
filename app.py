"""Smart House Price Predictor - Flask REST API (v7.0, Real Data)"""
from pathlib import Path
from flask import Flask, request, jsonify
from flasgger import Swagger
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from predictor import (
    load_artifacts, get_category_values, validate_input,
    build_features, predict_with_confidence, format_price,
)

app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'Smart House Price Predictor API',
    'uiversion': 3,
    'description': 'AI-powered property price prediction based on real Egyptian real estate data',
    'version': '7.0.0',
}
swagger = Swagger(app)

# Load model
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


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "service": "Smart House Price Predictor API",
        "version": "7.0.0",
        "source": "PropertyFinder Egypt (real listings)",
        "status": "running",
        "endpoints": {
            "predict": "POST /api/predict",
            "health": "GET /api/health",
            "categories": "GET /api/categories",
            "docs": "GET /apidocs/",
        },
    })


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
        "source": metadata.get("training_info", {}).get("source"),
        "error": load_error,
    }), (200 if model is not None else 503)


@app.route("/api/categories", methods=["GET"])
def get_categories_route():
    """Get all available categorical values.
    ---
    tags:
      - Metadata
    responses:
      200:
        description: Available cities, districts, compounds
    """
    return jsonify({
        "city": category_values.get("city", []),
        "district": category_values.get("district", []),
        "compound": category_values.get("compound", []),  # limit
    })


@app.route("/api/predict", methods=["POST"])
def api_predict():
    """Predict property price based on real Egyptian market data.
    ---
    tags:
      - Prediction
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [area, bedrooms, bathrooms, city, district]
          properties:
            area: {type: number, example: 150}
            bedrooms: {type: string, example: "3"}
            bathrooms: {type: integer, example: 2}
            city: {type: string, example: Cairo}
            district: {type: string, example: "New Cairo City"}
            compound: {type: string, example: Madinaty}
            description: {type: string, example: "Luxury sea view apartment"}
            amenities: {type: array, items: {type: string}, example: ["BA", "SE"]}
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
            district=data.get("district"),
            compound=data.get("compound", "None"),
        )
        if errors:
            return jsonify({"errors": errors}), 400

        features = build_features(
            area=data.get("area"),
            bedrooms=str(data.get("bedrooms")),
            bathrooms=data.get("bathrooms"),
            city=data.get("city"),
            district=data.get("district"),
            compound=data.get("compound", "None"),
            description=data.get("description", ""),
            amenities=data.get("amenities", []),
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
                "data_source": metadata["training_info"].get("source", "Unknown"),
            },
        })

    except Exception as e:
        app.logger.exception("Prediction error")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
