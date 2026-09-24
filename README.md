<div align="center">

# 🏠 Smart House Price Predictor

### AI-powered property price estimation for the Egyptian real estate market

[![Live Demo](https://img.shields.io/badge/TRY_THE_LIVE_APP-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://smart-house-price-predictor.streamlit.app)
[![GitHub](https://img.shields.io/badge/View_on_GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/qamarsobhy7-source/Smart-House-Price-Predictor)

**Live App:** [https://smart-house-price-predictor.streamlit.app](https://smart-house-price-predictor.streamlit.app)

</div>

---

## 📖 About

**Smart House Price Predictor** is an end-to-end Machine Learning system that estimates apartment prices in Egypt, trained on **7,749 real property listings** from PropertyFinder Egypt.

Unlike many academic projects, this model is trained on **real market data** and delivers **honest performance metrics** that reflect true market complexity.

| Metric | Value |
|:------:|:-----:|
| Accuracy (R²) | **0.6843** |
| Avg Error (MAPE) | **18.39%** |
| Cities | **9** |
| Districts | **43** |
| Listings | **7,749** |

---

## ✨ Features

### 🎨 Modern UI
- **4-step wizard** form (Location → Size → Features → Description)
- **Live property preview** card that updates in real time
- **Zillow-style price card** with confidence range
- **Monthly payment calculator**
- **100% mobile responsive** design
- **Inter font** with modern gradients

### 🧠 AI Capabilities
- **XGBoost regressor** (best of 4 models tested)
- **SHAP explainability** — see why each price was predicted
- **NLP sentiment analysis** on property descriptions
- **Smart similar properties** (cosine similarity + price filter)
- **Investment ROI calculator** (1/5/10 years)
- **Market trend insights** (12-month forecast)

### 🛠️ Developer Tools
- **Flask REST API** with Swagger documentation
- **28 unit tests** (100% passing)
- **Docker container** ready for deployment
- **GitHub Actions CI/CD** pipeline
- **Model Card + Data Card** (Responsible AI)

### 📊 Data Quality
- **Real listings** from PropertyFinder Egypt (CC0-1.0)
- **64 engineered features** (GPS, amenities, NLP)
- **890 unique compounds** with search
- **42 real amenities** (pool, gym, security)
- **Multi-city coverage** (Cairo, Giza, Alexandria, Red Sea, North Coast)

---

## 📸 Screenshots

### 🏠 Homepage — 4-Step Wizard

![Homepage](screenshots/01_hero.png)

### 💰 Price Prediction Result

![Prediction](screenshots/02_prediction.png)

### 🧠 AI Explainability (SHAP)

![SHAP](screenshots/03_shap.png)

### 🗺️ Real Property Map

![Map](screenshots/04_map.png)

### 🏘️ Similar Properties

![Recommendations](screenshots/05_recommendations.png)

### 💰 Investment ROI Analysis

![ROI](screenshots/06_roi.png)

---

## 🚀 Quick Start

### Option 1 — Use the Live App (recommended)

Open: **https://smart-house-price-predictor.streamlit.app**

No installation required. Works on desktop and mobile.

### Option 2 — Run Locally

```bash
git clone https://github.com/qamarsobhy7-source/Smart-House-Price-Predictor.git
cd Smart-House-Price-Predictor
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Or run Flask API:

```bash
python app.py
```

- API: http://localhost:5000
- Docs: http://localhost:5000/apidocs/

### Option 3 — Docker

```bash
docker build -t house-price .
docker run -p 8501:8501 house-price
```

---

## 🧪 Testing

```bash
pytest tests/ -v
```

Result: **28 passed in 2.4s**

All tests cover:
- Model loading and metadata validation
- Input validation (15 edge cases)
- Feature engineering (64 features)
- NLP extraction (12 keywords)
- Predictions (realistic price ranges)
- ROI calculations
- Recommendation system
- Category management

---

## 🧠 Model Details

### Algorithm Selection

We tested **4 different models** with 3-fold cross-validation:

| Rank | Model | R² (CV) |
|:----:|-------|:-------:|
| 🥇 | **XGBoost** | **0.6874** |
| 🥈 | LightGBM | 0.6826 |
| 🥉 | Gradient Boosting | 0.6647 |
| 4 | Ridge | 0.6378 |

**XGBoost** achieved the best performance and was selected as the final model.

### Feature Engineering (64 features)

| Category | Count | Examples |
|----------|:-----:|----------|
| GPS | 4 | latitude, longitude, geo_cluster, distance_to_cairo |
| Amenities | 32 | pool, gym, garden, parking, security |
| NLP from title | 12 | sea_view, luxury, furnished, garden |
| Interactions | 8 | area_per_bedroom, bed_bath_ratio |
| Target Encoding | 5 | city_ppm, district_ppm, compound_ppm |
| Categorical | 3 | city, district, compound |

### Why R² = 0.68 is a Good Result

On **real** real estate data, R² values of **0.6–0.75 are considered excellent**. Real market prices depend on factors not in the listing (condition, floor, view, negotiation), making perfect prediction impossible.

**We chose honest numbers on real data over inflated numbers on synthetic data.**

---

## 📂 Project Structure

```
Smart-House-Price-Predictor/
├── README.md
├── MODEL_CARD.md
├── DATA_CARD.md
├── LICENSE
├── requirements.txt
├── Dockerfile
├── Procfile
├── .github/workflows/ci.yml
│
├── predictor.py               # Core ML prediction logic
├── streamlit_app.py           # Modern UI (757 lines)
├── app.py                     # Flask REST API + Swagger
├── monitoring.py              # Prediction logging
├── sentiment_helper.py        # NLP sentiment
├── pdf_report.py              # PDF generator
├── global_insights.py         # SHAP + learning curves
│
├── models/
│   ├── real_model.joblib
│   ├── real_model_metadata.joblib
│   ├── real_feature_mappings.joblib
│   └── global_insights.joblib
│
├── data/real_data/
│   ├── model_ready_clean.csv
│   ├── processed/buy.csv
│   └── metadata/
│
├── tests/test_predictor.py    # 28 tests
│
├── screenshots/                # 6 UI screenshots
│
└── monitoring/                 # Predictions log
```

---

## 🌍 Data Source

Our model is trained on **real, publicly available listings** from:

**🔗 PropertyFinder Egypt** — the largest real estate platform in Egypt

### Data Funnel

| Stage | Records |
|-------|--------:|
| Raw scrape (buy + rent) | 64,106 |
| Buy listings only | 19,967 |
| Apartments only | 10,277 |
| After filtering | 9,089 |
| **Final cleaned dataset** | **7,749** |

### Cities Covered

Cairo · Giza · Alexandria · Red Sea · North Coast · Suez · Qalyubia · Matrouh · Al Daqahlya

---

## 🛠️ Tech Stack

| Category | Technologies |
|:--------:|:------------:|
| **Language** | Python 3.10+ |
| **ML** | XGBoost, scikit-learn, LightGBM |
| **Data** | pandas, numpy |
| **NLP** | Custom keyword-based + sentiment |
| **Visualization** | Plotly, matplotlib, Folium |
| **Explainability** | SHAP |
| **UI** | Streamlit |
| **API** | Flask + Flasgger (Swagger) |
| **Testing** | pytest (28 tests) |
| **Deployment** | Streamlit Cloud, Docker |
| **CI/CD** | GitHub Actions |

---

## 📝 API Usage

### Python

```python
from predictor import load_artifacts, build_features, predict_price, format_price

model, metadata, mappings = load_artifacts()

features = build_features(
    area=150, bedrooms="3", bathrooms=2,
    city="Cairo", district="New Cairo City", compound="Madinaty",
    amenities=["BA", "SE", "PG"],
    description="Luxury sea view apartment",
    mappings=mappings,
)

price = predict_price(model, features)
print(format_price(price))  # 6.83M EGP
```

### REST API

```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"area": 150, "bedrooms": "3", "bathrooms": 2,
       "city": "Cairo", "district": "New Cairo City",
       "compound": "Madinaty", "amenities": ["BA", "SE"]}'
```

**Response:**
```json
{
  "success": true,
  "prediction": {
    "price": 6825000,
    "price_formatted": "6.83M EGP",
    "lower_bound": 5568000,
    "upper_bound": 8082000,
    "currency": "EGP",
    "confidence_level": "81.61%"
  }
}
```

---

> **Note:** The Streamlit Cloud app hosts the UI only. The REST API requires running the Flask server (`app.py`) locally or deploying to a service like Render/Railway.

---

## ⚠️ Limitations

- **Asking prices, not transaction prices** — Listings are what sellers want, not what they get
- **Single snapshot in time** — Scraped in early 2026
- **Apartments only** — Villas, chalets, and commercial properties not yet supported
- **9 cities** — Coverage limited to major Egyptian cities
- **AI estimation** — Not a substitute for certified appraisal

---

## 🔮 Roadmap

- [ ] Expand to 15+ Egyptian cities
- [ ] Support villas, chalets, and commercial units
- [ ] Integrate Arabic NLP transformer (AraBERT)
- [ ] Add time-series price forecasting per district
- [ ] Computer vision for property image analysis
- [ ] User accounts with saved properties

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- **Data source:** [PropertyFinder Egypt](https://www.propertyfinder.eg) (CC0-1.0 license)
- **Deployment:** [Streamlit Cloud](https://share.streamlit.io)
- **Kaggle dataset:** [mohammedhassan1112/egypt-property-finder](https://www.kaggle.com/datasets/mohammedhassan1112/egypt-property-finder)

---

<div align="center">

### ⭐ If you found this project helpful, please give it a star!

**Made with ❤️ for the Egyptian real estate market**

[⬆ Back to top](#-smart-house-price-predictor)

</div>
