# Smart House Price Predictor

An end-to-end machine learning web application for estimating apartment sale prices in Egyptian pounds (EGP).

## Project Overview

This project predicts residential apartment sale prices in Egypt using property characteristics and location information.

The project includes data cleaning, feature engineering, leakage prevention, model comparison, hyperparameter tuning, evaluation, and a Flask web application.

## Dataset

The project uses the Egypt Real Estate Data 2026 dataset collected from PropertyFinder Egypt.

Original dataset size: approximately 39,713 listings and 53 columns.

Final modeling dataset: 1,130 high-confidence apartment sale listings.

## Target

The target is the full apartment sale price in Egyptian pounds (EGP).

| Statistic | Value |
|---|---:|
| Records | 1,130 |
| Mean | 9,931,202 EGP |
| Median | 8,500,000 EGP |
| Minimum | 1,848,000 EGP |
| Maximum | 39,083,760 EGP |

## Features

The final model uses 13 features.

### Numerical Features

- Area
- Bedrooms
- Bathrooms
- Studio indicator
- Reception indicator
- Living-room indicator
- Kitchen indicator

### Categorical Features

- City
- Town
- District
- Subdistrict
- Furnished status
- Completion status

Target-derived information was not used as an input feature.

Price per square meter was excluded from the model to prevent target leakage.

## Data Preparation

- Data cleaning
- Missing-value handling
- Studio detection
- Text-based feature extraction
- Location normalization
- Area validation
- Duplicate analysis
- Near-duplicate investigation
- Data leakage prevention

## Train/Test Split

A group-aware split was used to reduce the risk of similar properties appearing in both training and testing data.

- Training records: 888
- Test records: 242
- Total groups: 764
- Shared groups between train and test: 0

## Preprocessing

Numerical features use median imputation and standard scaling.

Categorical features use missing-value handling and one-hot encoding with unknown-category support.

## Model Comparison

| Model | MAE (EGP) | RMSE (EGP) | R2 |
|---|---:|---:|---:|
| Linear Regression | 2,673,435 | 3,685,172 | 0.5684 |
| Random Forest | 2,416,804 | 3,491,584 | 0.6126 |
| Gradient Boosting | 2,432,338 | 3,344,718 | 0.6445 |
| Tuned Gradient Boosting | 2,342,225 | 3,321,893 | 0.6493 |

The tuned Gradient Boosting model achieved the best overall test performance.

## Hyperparameter Tuning

RandomizedSearchCV with GroupKFold cross-validation was used to tune the Gradient Boosting model.

Best parameters:

- Number of estimators: 400
- Learning rate: 0.08
- Maximum depth: 4
- Minimum samples split: 15
- Minimum samples leaf: 1
- Subsample: 1.0
- Random state: 42

## Final Performance

- MAE: 2,342,225 EGP
- RMSE: 3,321,893 EGP
- R2: 0.6493
- Mean absolute percentage error: approximately 27.77%

The model provides useful estimates but predictions should not be treated as exact market valuations.

## Feature Importance

Area is the strongest individual predictor of apartment price.

Location-related features are also highly important, especially subdistrict information.

## Ablation Study

| Feature Set | MAE (EGP) | RMSE (EGP) | R2 |
|---|---:|---:|---:|
| Full Model | 2,342,225 | 3,321,893 | 0.6493 |
| Without Furnished | 2,459,874 | 3,459,324 | 0.6197 |
| Without Subdistrict | 2,438,399 | 3,567,475 | 0.5956 |
| Without Both | 2,511,112 | 3,623,684 | 0.5827 |

## Model Verification

The saved model was reloaded and evaluated again.

The reloaded model produced identical predictions to the original evaluated model.

Maximum prediction difference: 0.0 EGP

## Web Application

The project includes a Flask web application for estimating apartment prices.

Users can enter area, bedrooms, bathrooms, location, furnished status, completion status, reception, living room, and kitchen information.

The application returns the estimated apartment sale price in Egyptian pounds.

## Architecture

User Input -> Flask Application -> Preprocessing -> Machine Learning Model -> Predicted Price

## Project Structure

Smart-House-Price-Predictor/
|-- app.py
|-- README.md
|-- requirements.txt
|-- .gitignore
|-- models/
|   |-- egypt_real_estate_price_model.joblib
|   |-- model_metadata.joblib
|-- templates/
|   |-- index.html
|-- static/
|   |-- style.css
|-- assets/
|   |-- app_screenshot.png

## Technologies

Python, Pandas, NumPy, Scikit-learn, Joblib, Flask, HTML5, CSS3, Matplotlib, Seaborn, Google Colab, Git, GitHub, and Gunicorn.

## Installation

```bash
git clone https://github.com/qamarsobhy7-source/Smart-House-Price-Predictor.git
cd Smart-House-Price-Predictor
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## Production Deployment

The application can be deployed using Gunicorn:

```bash
gunicorn app:app
```

The deployed application does not depend on Google Colab.

## Limitations

- The dataset represents online property listings rather than every property transaction in Egypt.
- The final target dataset contains 1,130 high-confidence listings.
- Some locations have relatively few examples.
- Luxury and unusual properties may produce larger errors.
- Predictions are estimates and are not official property valuations.

## Future Improvements

- Expand the verified training dataset
- Add more property attributes
- Add richer amenities
- Add geographic features
- Test advanced boosting models
- Add prediction intervals
- Improve the location interface
- Add automated model retraining
- Add production monitoring

## Author

Qamar Sobhy

## License

This project is provided for educational and portfolio purposes.
