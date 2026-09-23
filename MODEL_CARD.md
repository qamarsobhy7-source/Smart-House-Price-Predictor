# Model Card — Smart House Price Predictor

## Model Details

| Field | Value |
|-------|-------|
| **Model Name** | Gradient Boosting Regressor (v3) |
| **Version** | 3.0.0 |
| **Type** | Supervised Regression |
| **Target** | Property price (EGP) |
| **Developed by** | AI Engineering Team |
| **Date** | 2026 |
| **Framework** | scikit-learn 1.6.1 |
| **License** | MIT |

### Architecture

- **Algorithm:** Gradient Boosting Regressor
- **Target Transform:** `log(1 + price)` for normality
- **Hyperparameters:**
  - `n_estimators`: 192
  - `max_depth`: 3
  - `learning_rate`: 0.075
  - `subsample`: 0.873
- **Tuning:** Optuna (TPE sampler)
- **Preprocessing:** ColumnTransformer + StandardScaler + OneHotEncoder

### Ensemble Alternative

An optional **Stacking Regressor** is also included:
- **Base models:** Gradient Boosting, XGBoost, LightGBM, Random Forest
- **Meta-learner:** Ridge (alpha=1.0)
- **Cross-validation:** 3-fold

---

## Intended Use

### Primary Use Cases

- **Buyers:** Estimate fair market value before negotiations
- **Sellers:** Determine competitive listing prices
- **Investors:** Evaluate ROI and compare properties
- **Researchers:** Benchmark Egyptian real estate ML models

### Out-of-Scope Use

- ❌ **Not** a formal appraisal — does not replace certified property evaluators
- ❌ **Not** for villas, land, or commercial properties
- ❌ **Not** for cities outside the 10 covered

---

## Training Data

- **Source:** Synthetic dataset simulating Egyptian market (2024–2025 prices)
- **Size:** 8,000 records
- **Cities:** 10 (Cairo, Giza, Alexandria, Mansoura, Tanta, Port Said, Suez, Ismailia, Luxor, Aswan)
- **Split:** 80% train / 20% test

Full details in [DATA_CARD.md](DATA_CARD.md).

---

## Performance Metrics

### Test Set Performance

| Metric | Value |
|--------|-------|
| **R²** | 0.9784 |
| **MAPE** | 6.61% |
| **MAE** | ~300,000 EGP |
| **RMSE** | ~440,000 EGP |

### Per-Model Comparison (CV R²)

| Model | R² (CV) |
|-------|---------|
| **Ensemble Stacking** | **0.9784** |
| Gradient Boosting | 0.9781 |
| XGBoost | 0.9760 |
| LightGBM | 0.9756 |
| Random Forest | 0.9672 |
| Ridge / Lasso | 0.9571 |
| Linear Regression | 0.9567 |

---

## Limitations

1. **Synthetic data** — Generated from real market patterns but not actual transactions
2. **Limited geography** — 10 cities only
3. **Single property type** — Residential apartments only
4. **Temporal** — No time-varying effects modeled (handled separately via Prophet)
5. **Feature coverage** — Missing: floor number, building age, exact coordinates

---

## Ethical Considerations

- **No personal data** collected or used
- **No geographic bias** introduced by protected attributes
- **Transparency:** SHAP explanations provided for every prediction
- **Confidence intervals** always shown alongside point estimates

---

## Recommendation

**Use as a decision-support tool.** Always combine with:
- Physical inspection
- Comparable market listings
- Professional appraisal for transactions over 5M EGP

---

## Citation
