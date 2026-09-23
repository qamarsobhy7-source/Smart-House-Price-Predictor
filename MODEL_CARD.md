# Model Card — Smart House Price Predictor

## Model Details

| Field | Value |
|-------|-------|
| **Model Name** | XGBoost Regressor (Real Data) |
| **Version** | 7.0.0 |
| **Type** | Supervised Regression |
| **Target** | Apartment price (EGP) |
| **Framework** | XGBoost 2.0+ / scikit-learn 1.6.1 |
| **License** | MIT |

### Architecture

- **Algorithm:** XGBoost (Gradient Boosted Trees)
- **Target Transform:** log(1 + price)
- **Hyperparameters:**
  - n_estimators: 200
  - max_depth: 6
  - learning_rate: 0.1
  - subsample: 0.9
  - tree_method: hist

---

## Intended Use

### Primary Use Cases

- Buyers: Reference price when comparing apartments
- Sellers: Sanity check before listing
- Investors: Initial market scan before visiting properties
- Researchers: Baseline benchmark for Egypt real estate ML

### Out-of-Scope Use

- Not a formal property appraisal
- Not for villas, chalets, or commercial
- Not for cities outside the training set

---

## Training Data

- **Source:** PropertyFinder Egypt (public listings)
- **Records:** 7,749 apartments after cleaning
- **Train/Test split:** 80/20 with random seed 42
- **Features:** 61 numeric + 3 categorical = 64 total

See DATA_CARD.md for full details.

---

## Performance Metrics

### Test Set Performance

| Metric | Value |
|--------|-------|
| **R-squared** | 0.6843 |
| **MAPE** | 18.39% |
| **MAE** | 1479340 EGP |
| **RMSE** | 2048059 EGP |

### Model Comparison (3-fold CV R-squared)

| Model | R-squared (CV) |
|-------|----------------|
| XGBoost | 0.6874 |
| LightGBM | 0.6826 |
| Gradient Boosting | 0.6647 |
| Ridge | 0.6378 |

---

## Interpretation of R-squared = 0.68

On real real estate data, R-squared values of 0.6-0.75 are typical and accepted. Reasons:

1. **Unobserved factors** - condition of property, floor, view, negotiation, seller motivation
2. **Listing prices vs. sale prices** - listings are asking prices, actual sales may differ
3. **Market noise** - supply/demand variations not captured
4. **Data limitations** - no historical price trends, no economic indicators

We report honest numbers on real data rather than inflated numbers on synthetic data.

---

## Limitations

1. Asking prices, not transaction prices
2. Single point in time (2026 scrape)
3. Apartment-only; no villas/chalets/commercial
4. No maintenance fees, installments plans, or future market factors
5. Geographic coverage limited to 9 cities

---

## Ethical Considerations

- No personal data collected
- Only public listings used
- SHAP explanations provided for every prediction
- Confidence intervals always shown
- Tool explicitly positioned as estimation, not appraisal

---

## Citation

Smart House Price Predictor v7.0 (2026)
Real data model trained on PropertyFinder Egypt listings
https://github.com/qamarsobhy7-source/Smart-House-Price-Predictor
