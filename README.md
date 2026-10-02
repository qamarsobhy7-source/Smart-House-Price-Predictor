# 🏠 Egypt Real Estate AI Predictor

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

AI-powered web application for predicting real estate prices in Egypt using machine learning.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31-red)
![CatBoost](https://img.shields.io/badge/CatBoost-1.2-green)

## 📊 Dataset

| Metric | Value |
|--------|-------|
| **Listings** | 119,916 |
| **Governorates** | 6 |
| **Property Types** | 19 |
| **Districts** | 573 |
| **Compounds** | 881 |

### 📍 Supported Governorates

- 🏙️ Cairo (65,674 listings)
- 🏙️ Giza (30,374 listings)
- 🏖️ Matrouh (10,545 listings)
- 🌊 Red Sea (6,253 listings)
- 🌊 Alexandria (4,122 listings)
- 🚢 Suez (2,948 listings)

## 🎯 Model Performance

| Metric | Value |
|--------|-------|
| **Algorithm** | CatBoost |
| **R² Score** | 0.7061 |
| **MAPE** | 40.52% |
| **Features** | 32 |

## ✨ Features

- 🎯 **Price Prediction** — Instant price estimate for any property
- 📊 **Market Analysis** — Interactive charts and statistics
- 🗺️ **Interactive Map** — Browse properties on Folium map
- 🧮 **Mortgage Calculator** — Calculate monthly payments
- ⭐ **Featured Properties** — Premium listings showcase
- ℹ️ **About** — Project details and statistics

## 🚀 Live Demo

🔗 **[Open App](https://share.streamlit.io)**

## 📦 Run Locally

```bash
git clone https://github.com/qamarsobhy7-source/Smart-House-Price-Predictor.git
cd Smart-House-Price-Predictor
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## 🛠️ Tech Stack

- **Frontend**: Streamlit, Plotly, Folium
- **ML**: CatBoost, XGBoost, LightGBM
- **Data**: Pandas, NumPy
- **Deployment**: Streamlit Cloud

## 📁 Project Structure

```
.
├── streamlit_app.py       # Main application
├── requirements.txt       # Dependencies
├── LICENSE                # MIT License
├── README.md              # Documentation
├── .streamlit/
│   └── config.toml        # Streamlit config
├── models/
│   ├── FINAL_MODEL_v9.pkl
│   ├── FINAL_FEATURES_v9.pkl
│   └── FINAL_CAT_FEATURES_v9.pkl
└── data/
    └── processed/
        └── FINAL_DATASET_v9.csv
```

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

## 👨‍💻 Author

**qamarsobhy7-source**

---

⭐ **If you like this project, give it a star!**