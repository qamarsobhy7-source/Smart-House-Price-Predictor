
from flask import Flask, render_template, request

from predictor import (
    load_artifacts,
    get_category_values,
    validate_prediction_input,
    build_features,
    predict_price,
    format_price,
)

app = Flask(__name__)

model = None
metadata = {}
category_values = {}
load_error = None

try:
    model, metadata = load_artifacts()
    category_values = get_category_values(model)
except Exception as error:
    load_error = str(error)
    app.logger.exception("Model loading error")


@app.route("/", methods=["GET", "POST"])
def home():
    prediction = None
    error_message = None
    form_data = request.form.to_dict() if request.method == "POST" else {}

    if request.method == "POST":
        errors = validate_prediction_input(
            area=form_data.get("area"),
            bedrooms=form_data.get("bedrooms"),
            bathrooms=form_data.get("bathrooms"),
            city=form_data.get("city"),
            town=form_data.get("town"),
            district=form_data.get("district"),
            subdistrict=form_data.get("subdistrict"),
            furnished=form_data.get("furnished"),
            completion_status=form_data.get("completion_status"),
        )

        if not errors and category_values:
            fields = {
                "city": "City",
                "town": "Town",
                "district": "District",
                "subdistrict": "Subdistrict",
                "furnished": "Furnished status",
                "completion_status": "Completion status",
            }

            for field, label in fields.items():
                if form_data.get(field) not in category_values[field]:
                    errors.append(
                        f"{label} must be selected from the available options."
                    )

        if errors:
            error_message = " ".join(errors)

        elif model is None:
            error_message = "The prediction model could not be loaded."

        else:
            try:
                features = build_features(
                    area=form_data.get("area"),
                    bedrooms=form_data.get("bedrooms"),
                    bathrooms=form_data.get("bathrooms"),
                    city=form_data.get("city"),
                    town=form_data.get("town"),
                    district=form_data.get("district"),
                    subdistrict=form_data.get("subdistrict"),
                    furnished=form_data.get("furnished"),
                    completion_status=form_data.get("completion_status"),
                    has_reception=form_data.get("has_reception") == "yes",
                    has_living=form_data.get("has_living") == "yes",
                    has_kitchen=form_data.get("has_kitchen") == "yes",
                )

                prediction = format_price(
                    predict_price(model, features)
                )

            except Exception:
                error_message = (
                    "An error occurred while generating the prediction."
                )
                app.logger.exception("Prediction error")

    return render_template(
        "index.html",
        prediction=prediction,
        error_message=error_message,
        form_data=form_data,
        category_values=category_values,
        model_metadata=metadata,
    )


if __name__ == "__main__":
    import os

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False,
    )
