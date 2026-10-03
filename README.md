<div align="center">

# 🏠 SmartPrice

### **AI-powered apartment price estimation for the Egyptian real estate market**

[![Live Demo](https://img.shields.io/badge/🚀_LIVE_DEMO-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://smart-house-price-predictor-77.streamlit.app)
[![GitHub Stars](https://img.shields.io/github/stars/qamarsobhy7-source/Smart-House-Price-Predictor?style=for-the-badge&logo=github&color=yellow)](https://github.com/qamarsobhy7-source/Smart-House-Price-Predictor/stargazers)

<br/>

<img src="screenshots/01_homepage_en.png" alt="SmartPrice Homepage" width="100%" />

<br/>

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![XGBoost](https://img.shields.io/badge/XGBoost-v2.0-FF6600?style=flat-square)](https://xgboost.readthedocs.io)
[![AraBERT](https://img.shields.io/badge/AraBERT-8B5CF6?style=flat-square)](https://huggingface.co/aubmindlab/bert-base-arabertv02)
[![Prophet](https://img.shields.io/badge/Prophet-10B981?style=flat-square)](https://facebook.github.io/prophet)
[![SHAP](https://img.shields.io/badge/SHAP-EC4899?style=flat-square)](https://shap.readthedocs.io)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-22C55E?style=flat-square)](LICENSE)

<br/>

[📖 About](#-about) · [✨ Features](#-features) · [📸 Screenshots](#-screenshots) · [🧠 AI Models](#-ai-models) · [🚀 Quick Start](#-quick-start)

</div>

---

## 📖 About

**SmartPrice** is a bilingual (English / Arabic) AI-powered web application that estimates apartment prices in the **Egyptian real estate market**. It uses a **gradient-boosted machine learning model** trained on **7,749 real property listings** scraped from PropertyFinder Egypt.

Unlike traditional real-estate platforms that focus on listings, SmartPrice focuses on **valuation intelligence** — similar to Zillow's Zestimate — with **full Arabic support**, **explainable AI**, and **time-series forecasting**.

### 🎯 Key Metrics

| Metric | Value |
|:---:|:---:|
| **R² Score** | **0.6843** |
| **MAPE** (avg error) | **18.39%** |
| **Training listings** | **7,749** real properties |
| **Governorates** | **27** (full Egypt coverage) |
| **Districts** | **43** |
| **Compounds** | **890** |
| **Engineered features** | **64** |

---


## 📚 Documentation

Complete project documentation:

| Document | Description |
|---|---|
| 📖 **[README](README.md)** | Project overview (this file) |
| 📊 **[Data Card](DATA_CARD.md)** | Dataset details, sources, limitations |
| 🧠 **[Model Card](MODEL_CARD.md)** | Model architecture, performance, ethics |
| 📓 **[Notebooks](notebooks/)** | Step-by-step ML pipeline |
| 🧪 **[Tests](tests/)** | Automated test suite (43 tests) |
| 🤝 **[Contributing](CONTRIBUTING.md)** | How to contribute |
| 📜 **[Changelog](CHANGELOG.md)** | Version history |
| 🔒 **[Security](SECURITY.md)** | Security policy |

---

## 📸 Screenshots

<div align="center">

### 🌐 Bilingual — One App, Two Languages

<table>
<tr>
<td width="50%" align="center">
<b>🇬🇧 English (LTR)</b><br/>
<img src="screenshots/01_homepage_en.png" width="100%" />
</td>
<td width="50%" align="center">
<b>🇸🇦 Arabic (RTL)</b><br/>
<img src="screenshots/06_homepage_ar.png" width="100%" />
</td>
</tr>
</table>

<br/>

### 📊 Prediction Result & Analysis

<img src="screenshots/02_result_en.png" alt="Prediction Result" width="85%" />

<br/><br/>

### 🔬 SHAP Feature Explanation

<img src="screenshots/03_shap_en.png" alt="SHAP Explanation" width="85%" />

<br/><br/>

### 🏘️ Neighborhood Insights

<img src="screenshots/04_neighborhood_en.png" alt="Neighborhood Insights" width="85%" />

<br/><br/>

### 🌙 Dark Mode

<img src="screenshots/05_dark_mode.png" alt="Dark Mode" width="85%" />

<br/><br/>

### 📱 Mobile Responsive

<img src="screenshots/07_mobile.png" alt="Mobile View" width="40%" />

</div>

---

## ✨ Features

### 🌍 Location & Coverage

- ✅ **27 Egyptian governorates** with 5-level cascading dropdowns
- ✅ Hierarchy: **Governorate → City → District → Area → Compound**
- ✅ **Data coverage indicators** (🟢 high · 🟡 medium · 🟠 low · 🔴 minimal · ⚪ coming soon)
- ✅ Fully **bilingual** (English + Arabic with RTL)

### 📝 Property Input (12 fields)

- Property type (Apartment, Villa, Duplex, Penthouse, Townhouse, Studio)
- Area (20–600 m²), Bedrooms (Studio–10), Bathrooms (1–8)
- Reception, Kitchen, Floor, Parking
- Furnishing, Finishing, View, Year Built
- **12 amenity checkboxes**
- Free-text description (analyzed by **AraBERT**)

### 📈 Analysis Dashboard (9 tabs)

| Tab | What it shows |
|---|---|
| 🧠 **Why This Price** | SHAP feature importance |
| 🗺️ **Market** | District price ranking |
| 🏘️ **Similar** | Comparable real listings |
| ⚖️ **Compare** | Two-property comparison |
| 💰 **Investment** | 5-year ROI projection |
| 📈 **Forecast** | 12-month Prophet forecast |
| 📍 **Map** | Interactive Folium map |
| 🏘️ **Neighborhood** | Walk · Transit · Safety · Schools |
| 🏦 **Mortgage** | Payment calculator + yearly schedule |

### 🎨 UX & Interface

- ✅ **Dark Mode** / Light Mode toggle
- ✅ **Mobile responsive** — tested on 6 devices
- ✅ **Loading animations** — skeleton loaders
- ✅ **PDF report** — downloadable valuation
- ✅ **Featured properties** with sort controls
- ✅ **Popular areas** grid (8 top neighborhoods)
- ✅ **6 property type cards**
- ✅ **Quick filter chips**
- ✅ **Trust badges** section
- ✅ **Legal pages** (Privacy · Terms · Contact)
- ✅ **Professional footer**

---

## 🧠 AI Models

### 1️⃣ XGBoost Regressor — Price Prediction

Gradient boosted trees trained on **7,749 listings** with **64 engineered features**:

- **Location:** city, district, compound, GPS coordinates
- **Property:** area, bedrooms, bathrooms, amenities count
- **Engineered:** bed/bath ratio, area per bedroom, rooms total, log/sqrt size
- **NLP:** title length, word count, sentiment, keyword flags
- **Geo:** distance to Cairo, cluster assignment

### 2️⃣ AraBERT Transformer — Arabic NLP

Fine-tuned `aubmindlab/bert-base-arabertv02` for **Arabic text understanding**:

- Sentiment analysis of property descriptions
- Semantic feature extraction
- Graceful fallback to keyword-based sentiment

### 3️⃣ Prophet — Time Series Forecasting

Facebook Prophet for **12-month price forecasts** per city:

- Trend + seasonality decomposition
- Based on historical market data
- Confidence intervals

### 4️⃣ SHAP — Explainable AI

SHAP (SHapley Additive exPlanations) explains every prediction:

- Feature-by-feature impact
- Green = increases price · Red = decreases price
- Full transparency

### 📊 Model Comparison (Cross-Validation)

| Model | CV R² | Notes |
|---|:---:|---|
| Ridge | 0.42 | Baseline linear |
| Gradient Boosting | 0.65 | Strong baseline |
| **XGBoost** ⭐ | **0.68** | **Selected** |
| LightGBM | 0.67 | Close second |

---


## 📓 Notebooks

Step-by-step ML pipeline — fully reproducible:

| # | Notebook | What it does |
|---|---|---|
| 1 | **[01_data_exploration.ipynb](notebooks/01_data_exploration.ipynb)** | EDA, distributions, correlations |
| 2 | **[02_feature_engineering.ipynb](notebooks/02_feature_engineering.ipynb)** | Cleaning, engineered features, encoding |
| 3 | **[03_model_training.ipynb](notebooks/03_model_training.ipynb)** | Train 4 models, CV, save best |
| 4 | **[04_evaluation_shap.ipynb](notebooks/04_evaluation_shap.ipynb)** | Metrics, residuals, SHAP analysis |

### 🎯 Reproduce the Full Pipeline

```bash
jupyter notebook notebooks/
```

Each notebook is self-contained and loads data from `data/`.

---

## 🏗️ Architecture

```
Smart-House-Price-Predictor/
│
├── streamlit_app.py              # Main Streamlit app
├── predictor.py                  # ML model loading & prediction
├── arabert_helper.py             # AraBERT integration
├── sentiment_helper.py           # Fallback sentiment
├── monitoring.py                 # Prediction logging
│
├── location_selector.py          # 5-level cascading dropdowns
├── translations.py               # EN/AR translations
├── theme.py + dark_theme.py      # Design system
│
├── featured_properties.py        # Featured cards + sort
├── popular_areas.py              # Top 8 districts
├── property_types.py             # 6 property type cards
├── filters_chips.py              # Quick filter chips
│
├── neighborhood_insights.py      # Walk/Price/Tax
├── nearby_transport.py           # Metro/Bus/Airport
├── safety_schools.py             # Safety + Schools
├── mortgage_calculator.py        # Payment calculator
│
├── footer_about.py               # Trust badges
├── loading_ui.py                 # Skeleton loaders
├── pdf_report.py                 # PDF generator
│
├── notebooks/                    # 📓 ML Pipeline
│   ├── 01_data_exploration.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_model_training.ipynb
│   └── 04_evaluation_shap.ipynb
│
├── tests/                        # 🧪 Test suite (43 tests)
│   ├── test_data.py
│   ├── test_model.py
│   ├── test_predictor.py
│   └── test_app.py
│
├── data/
│   ├── egypt_hierarchy.json      # 27 governorates × 151 cities
│   ├── place_translations.json   # 1,126 EN ↔ AR names
│   ├── nearby_transport.json
│   ├── safety_schools.json
│   ├── real_data/
│   │   └── model_ready_clean.csv # 7,749 real listings
│   └── processed/
│       └── features.csv          # 64 engineered features
│
├── models/
│   ├── real_model.joblib         # Trained XGBoost pipeline
│   ├── real_model_metadata.joblib
│   ├── real_feature_mappings.joblib
│   └── time_series_forecasts.joblib
│
├── screenshots/                  # App screenshots
├── .github/                      # Issue + PR templates
│
├── DATA_CARD.md                  # 📊 Data documentation
├── MODEL_CARD.md                 # 🧠 Model documentation
├── CHANGELOG.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── README.md
├── requirements.txt
└── runtime.txt                   # Python 3.11
```

---

## 🛠️ Tech Stack

| Layer | Technologies |
|---|---|
| **ML** | XGBoost · scikit-learn · LightGBM · NumPy · pandas |
| **NLP** | AraBERT (Transformers) · PyTorch · SentencePiece |
| **Time Series** | Prophet |
| **XAI** | SHAP |
| **UI** | Streamlit · Plotly · Folium |
| **PDF** | ReportLab |
| **Auth** | streamlit-authenticator · bcrypt · PyYAML |
| **Fonts** | Cairo (Arabic) · Inter (English) |
| **i18n** | Custom (EN + AR with RTL) |

---

## 🌍 Data Source

Training data scraped from **[PropertyFinder Egypt](https://www.propertyfinder.eg)** in September 2025:

| Metric | Value |
|---|:---:|
| **Total listings** | **7,749** |
| **Governorates with data** | 9 |
| **Districts** | 43 |
| **Compounds** | 890 |
| **Columns** | 79 |

### 🏙️ Coverage by Governorate

| Governorate | Listings | Status |
|---|:---:|:---:|
| Cairo | 4,861 | 🟢 |
| Giza | 1,874 | 🟢 |
| Red Sea | 641 | 🟢 |
| Alexandria | 210 | 🟡 |
| Matrouh | 75 | 🟡 |
| Suez | 69 | 🟡 |
| Qalyubia | 16 | 🟠 |
| Al Daqahlya | 3 | 🔴 |

---

## 🚀 Quick Start

### 📱 Option 1 — Use the Live App *(recommended)*

👉 **https://smart-house-price-predictor-77.streamlit.app**

### 💻 Option 2 — Run Locally

```bash
# Clone the repository
git clone https://github.com/qamarsobhy7-source/Smart-House-Price-Predictor.git
cd Smart-House-Price-Predictor

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app.py
```

App runs at **http://localhost:8501**

---

## ⚠️ Limitations

### ✅ Real & Production-Ready

- AI price prediction (XGBoost + AraBERT + SHAP)
- Prophet 12-month forecast
- 27-governorate hierarchy
- 9 analysis tabs
- Neighborhood insights (Walk · Transit · Safety · Schools)
- Mortgage calculator
- PDF report
- EN/AR + Dark Mode
- Mobile responsive (6 devices tested)

### 🟡 Demo Features (Local Storage Only)

- **Login/Signup** — stored locally, not a real auth server
- **Save Property** — saved to local file, not tied to account
- **Saved Searches** — same as above
- **User Dashboard** — based on local data

> These features require a backend (Supabase/Firebase). Streamlit is frontend-first. For production, migrate to a full stack.

### ❌ Not Included

- Real-time listing updates
- Cloud photo upload
- Email notifications
- Payment processing
- Native mobile apps
- Agent messaging

---

## 🔮 Roadmap

### 🎯 High Priority

- [ ] Migrate authentication to Supabase
- [ ] Add property comparison table (multi-property)
- [ ] Implement email alerts for saved searches
- [ ] Add property photo upload (Cloudinary)

### 🔧 Medium Priority

- [ ] Expand training data to 18 more governorates
- [ ] Add property age/depreciation model
- [ ] Interactive street-level maps
- [ ] Multi-language support (FR, DE)

### 💡 Future Ideas

- [ ] Native mobile apps (iOS / Android)
- [ ] Agent marketplace integration
- [ ] Mortgage pre-approval flow
- [ ] Real-time chat with agents

---

## 📊 Project Statistics

<div align="center">

| | |
|:---:|:---:|
| **7,749** | Real property listings |
| **64** | Engineered features |
| **27** | Egyptian governorates |
| **9** | Analysis tabs |
| **2** | Languages (EN + AR) |
| **6** | Devices tested |
| **0.68** | R² score |

</div>

---

## 🧪 Testing

### Local Testing

```bash
# Run all tests
pytest tests/

# Compile check
python -m py_compile streamlit_app.py
python -m py_compile predictor.py
python -m py_compile location_selector.py
```

### CI/CD

GitHub Actions automatically runs on every push:
- ✅ Compile check
- ✅ Import check
- ✅ Run tests

---

## 📚 Citation

If you use this project in academic work, please cite:

```bibtex
@software{smartprice2026,
  author       = {Qamar Sobhy},
  title        = {SmartPrice: AI-Powered Real Estate Valuation for Egypt},
  year         = {2026},
  publisher    = {GitHub},
  url          = {https://github.com/qamarsobhy7-source/Smart-House-Price-Predictor}
}
```

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **[PropertyFinder Egypt](https://www.propertyfinder.eg)** — data source
- **[AraBERT](https://huggingface.co/aubmindlab/bert-base-arabertv02)** — Arabic NLP model
- **[Streamlit](https://streamlit.io)** — UI framework
- **[XGBoost](https://xgboost.readthedocs.io)** · **[Prophet](https://facebook.github.io/prophet)** · **[SHAP](https://shap.readthedocs.io)** — core ML libraries
- **[Folium](https://python-visualization.github.io/folium/)** — interactive maps
- **[ReportLab](https://www.reportlab.com/)** — PDF generation

---

<div align="center">

### ⭐ Support the Project

If you find this project useful, please consider giving it a star!

<br/>

[![⭐ Star](https://img.shields.io/badge/⭐_Star_the_Repo-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/qamarsobhy7-source/Smart-House-Price-Predictor/stargazers)
[![🍴 Fork](https://img.shields.io/badge/🍴_Fork_the_Repo-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/qamarsobhy7-source/Smart-House-Price-Predictor/fork)
[![🚀 Live Demo](https://img.shields.io/badge/🚀_Try_the_App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://smart-house-price-predictor-77.streamlit.app)

<br/><br/>

**🏠 SmartPrice v12.0** — Built with ❤️ for the Egyptian real estate market

</div>
