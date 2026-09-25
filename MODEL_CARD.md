# Model Card — Smart House Price Predictor v11.0

## Model Details

| Field | Value |
|-------|-------|
| **Project Name** | Smart House Price Predictor |
| **Version** | 11.0.0 |
| **Type** | Multi-Model AI System |
| **Last Updated** | 2026 |
| **License** | MIT |

### Systems Overview

This project uses **three complementary AI models**:

| # | Model | Purpose | Technology |
|---|-------|---------|------------|
| 1 | **XGBoost Regressor** | Property price prediction | Gradient Boosting |
| 2 | **AraBERT Transformer** | Arabic sentiment analysis | BERT-based |
| 3 | **Prophet** | Time series forecasting | Bayesian time series |

---

## Model 1: XGBoost Regressor

### Purpose

Predict apartment prices in Egypt based on property features.

### Architecture

- **Algorithm:** Gradient Boosted Decision Trees
- **Target:** `log(1 + price)` for normality
- **Pipeline:** ColumnTransformer + XGBoost
- **Features:** 64 engineered features

### Hyperparameters

```python
{
    'n_estimators': 192,
    'max_depth': 3,
    'learning_rate': 0.075,
    'subsample': 0.873,
}
```

### Performance (Test Set)

| Metric | Value |
|--------|-------|
| R² | 0.6843 |
| MAPE | 18.39% |
| MAE | ~300K EGP |

---

## Model 2: AraBERT Sentiment

### Purpose

Analyze sentiment of Arabic property descriptions (both MSA and colloquial Egyptian).

### Architecture

- **Base Model:** `CAMeL-Lab/bert-base-arabic-camelbert-da-sentiment`
- **Type:** BERT-based Transformer
- **Training:** Fine-tuned on Arabic dialect sentiment

### Hybrid Approach

1. **Primary:** Real-estate keyword matching (MSA + colloquial)
2. **Fallback:** AraBERT for texts without clear keywords
3. **Conflict Resolution:** Neutral when keywords conflict

### Performance

| Metric | Value |
|--------|-------|
| Accuracy | 17/17 test cases (100%) |
| Handles MSA | ✅ |
| Handles colloquial | ✅ |
| Handles negations | ✅ |
| Handles conflicts | ✅ |

---

## Model 3: Prophet Time Series

### Purpose

Forecast 12-month apartment prices per city.

### Architecture

- **Algorithm:** Prophet (Facebook Meta)
- **Model:** Additive time series with yearly seasonality
- **Configuration:**

```python
Prophet(
    yearly_seasonality=True,
    weekly_seasonality=False,
    changepoint_prior_scale=0.05,
    interval_width=0.80,
)
```

### Data

- **Historical Window:** 36 months
- **Forecast Horizon:** 12 months
- **Coverage:** 9 Egyptian cities
- **Confidence:** 80% interval

### Performance

| City | Current (EGP/m²) | +12M Forecast | Growth |
|------|-----------------:|--------------:|-------:|
| Al Daqahlya | 39,913 | 46,534 | +16.6% |
| Suez | 86,062 | 99,950 | +16.1% |
| North Coast | 64,890 | 75,278 | +16.0% |
| Cairo | 50,770 | 58,608 | +15.4% |
| Alexandria | 40,814 | 46,763 | +14.6% |
| Giza | 50,885 | 58,123 | +14.2% |
| Qalyubia | 25,168 | 28,418 | +12.9% |
| Matrouh | 31,031 | 34,740 | +12.0% |
| Red Sea | 59,870 | 65,189 | +8.9% |

---

## Intended Use

### Primary Use Cases

- **Buyers:** Reference prices before viewing properties
- **Sellers:** Sanity check before listing
- **Investors:** Market analysis and ROI calculation
- **Researchers:** Benchmark for Egyptian real-estate ML

### Out-of-Scope

- ❌ Not a formal property appraisal
- ❌ Not for villas, chalets, or commercial
- ❌ Not for cities outside the 9 covered

---

## Training Data

- **Source:** PropertyFinder Egypt (public listings, CC0-1.0)
- **Raw:** 64,106 listings
- **Clean:** 7,749 apartments
- **Cities:** 9
- **Districts:** 43
- **Compounds:** 890

See [DATA_CARD.md](DATA_CARD.md) for details.

---

## Limitations

1. **Asking prices, not transaction prices** — Listings ≠ final sale prices
2. **Single snapshot** — Data from early 2026
3. **Apartments only** — Villas excluded
4. **9 cities only** — Small cities not covered
5. **Estimation tool only** — Not a certified appraisal

---

## Ethical Considerations

- ✅ No personal data used
- ✅ Only public listings
- ✅ SHAP explanations for every prediction
- ✅ Confidence intervals always shown
- ✅ Clear disclaimer about limitations

---

## Citation

```bibtex
@misc{smart_house_price_predictor_2026,
  title={Smart House Price Predictor: AI-powered apartment price estimation for the Egyptian real estate market},
  author={Qamar Sobhy},
  year={2026},
  publisher={GitHub},
  howpublished={\url{https://github.com/qamarsobhy7-source/Smart-House-Price-Predictor}}
}
```
