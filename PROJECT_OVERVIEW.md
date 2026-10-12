# Project Overview

Complete technical documentation for **Egypt Real Estate AI**.

---

## 1. Project Summary

| Item | Value |
|:---:|:---:|
| **Project Name** | Egypt Real Estate AI |
| **Type** | AI-Powered Web Application |
| **Domain** | Real Estate / PropTech |
| **Language** | Python 3.11 |
| **Deployment** | Streamlit Cloud |
| **Live URL** | https://da.gd/AOPPkw |
| **GitHub** | https://github.com/qamarsobhy7-source/Smart-House-Price-Predictor |
| **License** | MIT |

---

## 2. Problem Statement

### The Challenge

In Egypt, property valuation is difficult because:

1. **No Standardization** - No reference pricing system
2. **Market Opacity** - Prices vary wildly by district
3. **Language Barrier** - Most tools are English-only
4. **No AI Solution** - Egypt lacks a Zestimate-like tool

### Impact

- Buyers overpay by 15-30% on average
- Sellers struggle to price competitively
- Market inefficiency costs billions annually

---

## 3. Our Solution

An AI-powered bilingual web application that:

1. **Predicts** property prices using CatBoost (R2 = 0.7061)
2. **Supports** Arabic (RTL) + English
3. **Provides** comprehensive market analysis
4. **Includes** investment ROI and mortgage tools
5. **Works** on desktop and mobile

---

## 4. Dataset

### Sources

- PropertyFinder Egypt
- Bayut Egypt
- Egyptian Real Estate Listings
- OLX Mining (GitHub)
- Real-Estate-Intelligence (GitHub)
- Scraping-Predictive (GitHub)

### Statistics

| Metric | Value |
|:---:|:---:|
| Total Listings | 119,916 |
| Governorates | 6 (with data) |
| Districts | 573 |
| Compounds | 881 |
| Numeric Features | 20 |
| Categorical Features | 12 |
| Total Features | 32 |

### Coverage by Governorate

| Governorate | Listings | % |
|:---:|:---:|:---:|
| Cairo | 65,674 | 54.8% |
| Giza | 30,374 | 25.3% |
| Matrouh | 10,545 | 8.8% |
| Red Sea | 6,253 | 5.2% |
| Alexandria | 4,122 | 3.4% |
| Suez | 2,948 | 2.5% |

---

## 5. Machine Learning Model

### Algorithm

**CatBoost Regressor** - Gradient Boosting on Decision Trees

### Why CatBoost?

- Best for categorical features (property_type, governorate, etc.)
- Handles missing values natively
- No need for extensive feature engineering
- Outperforms XGBoost and LightGBM on this dataset

### Training Configuration

| Parameter | Value |
|:---:|:---:|
| Training Set | 95,932 (80%) |
| Test Set | 23,984 (20%) |
| Iterations | 1000 |
| Learning Rate | 0.05 |
| Depth | 6 |
| Loss Function | RMSE |

### Performance Metrics

| Metric | Value | Meaning |
|:---:|:---:|:---:|
| **R2 Score** | 0.7061 | 70.6% of variance explained |
| **MAPE** | 40.52% | Average error margin |
| **RMSE** | (see training) | Root mean squared error |
| **MAE** | (see training) | Mean absolute error |

### Feature Importance (Top 10)

1. size (property size)
2. latitude + longitude (location)
3. district (specific area)
4. compound (building complex)
5. bedrooms + bathrooms
6. amenity_count
7. property_type
8. finishing_type
9. is_compound (boolean)
10. area_per_room

---

## 6. Features

### Tab 1: Price Estimator

- 5-level location input (governorate -> city -> district -> compound -> town)
- 8 property detail fields
- 12 interactive amenity pills
- Instant price prediction with confidence interval
- Data quality indicator
- Market comparison
- Property gallery (5 sample images)
- Price history + forecast (2020-2027)
- Interactive map with property marker
- Investment analysis (ROI, yield, payback)
- Neighborhood insights (schools, hospitals, transport)
- Save, PDF report, and share buttons
- Save search + price alerts

### Tab 2: Market Analysis

- 6 KPIs (listings, governorates, avg, median)
- 3 advanced filters
- 7 interactive charts:
  1. Top 10 areas by listings
  2. Property type distribution
  3. Average price by governorate
  4. Price distribution histogram
  5. Price vs size scatter plot
  6. Top 10 compounds
  7. Median price per sqm by governorate

### Tab 3: Mortgage Calculator

- Property price + down payment slider
- Automatic loan amount calculation
- Monthly payment breakdown
- Pie chart (principal vs interest)
- Balance over time chart
- 12-month amortization schedule

### Tab 4: Favorites

- Saved properties list
- Export to JSON
- Import from JSON
- Delete individually or clear all

### Tab 5: Compare Properties

- Select 2-4 saved properties
- Side-by-side comparison table
- Bar charts for price and size

### Tab 6: Chat with Agent

- Agent profile card
- Message bubbles
- 4 quick questions
- Automatic response

### Global Features

- Full Arabic (RTL) + English support
- Dark mode + Light mode
- Responsive mobile design
- Nawy-inspired clean UI

---

## 7. Tech Stack

| Layer | Technology |
|:---:|:---:|
| Frontend | Streamlit 1.31+ |
| ML Model | CatBoost 1.2+ |
| Data | Pandas, NumPy |
| Charts | Plotly |
| Maps | Folium, streamlit-folium |
| PDF | ReportLab |
| Styling | Custom CSS |
| Deployment | Streamlit Cloud |

---

## 8. Project Structure

```
Smart-House-Price-Predictor/
|-- streamlit_app.py              # Main app (2,800+ lines)
|-- nawy_theme.py                 # Theme & CSS (1,300+ lines)
|-- predictor.py                  # Model loading & prediction
|-- requirements.txt              # Dependencies
|-- LICENSE                       # MIT
|-- README.md                     # Main documentation
|-- PROJECT_OVERVIEW.md           # This file
|-- CHANGELOG.md                  # Version history
|-- .streamlit/
|   `-- config.toml
|-- data/
|   |-- egypt_hierarchy.json      # Geography hierarchy
|   `-- processed/
|       `-- FINAL_DATASET_v9.csv  # 119,916 listings
|-- models/
|   |-- FINAL_MODEL_v9.pkl        # Trained model (12 MB)
|   |-- FINAL_FEATURES_v9.pkl     # Feature names
|   `-- FINAL_CAT_FEATURES_v9.pkl # Categorical features
|-- screenshots/                  # App screenshots (10 images)
|   |-- 01_homepage.png
|   |-- 02_hero_kpis.png
|   |-- 03_property_types.png
|   |-- 04_popular_areas.png
|   |-- 05_compounds.png
|   |-- 06_dark_mode.png
|   |-- 07_mobile.png
|   |-- 08_estimator_form.png
|   |-- 09_result_price.png
|   `-- 10_result_roi.png
`-- demo/
    |-- Egypt_Real_Estate_AI_Demo.mp4          # Video demo
    |-- Egypt_Real_Estate_AI_Presentation.pptx # PowerPoint
    `-- Egypt_Real_Estate_AI_Presentation.pdf  # PDF
```

---

## 9. Installation & Usage

### Prerequisites

- Python 3.11 or higher
- pip package manager

### Local Setup

```bash
# 1. Clone
git clone https://github.com/qamarsobhy7-source/Smart-House-Price-Predictor.git
cd Smart-House-Price-Predictor

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
streamlit run streamlit_app.py
```

### Access

- Local: http://localhost:8501
- Live: https://da.gd/AOPPkw

---

## 10. Competitive Analysis

| Feature | Zillow | Nawy | Aqarmap | PropertyFinder | Ours |
|:---:|:---:|:---:|:---:|:---:|:---:|
| AI Price Estimate | Yes | No | No | Yes | Yes |
| Price History | Yes | Yes | No | No | Yes |
| ROI Analysis | Yes | No | No | No | Yes |
| Arabic Support | No | Yes | Yes | Yes | Yes |
| Dark Mode | Yes | Yes | Yes | Yes | Yes |
| PDF Reports | Yes | No | No | No | Yes |
| Bilingual | No | Yes | Yes | Yes | Yes |
| Free | Yes | Yes | Yes | Yes | Yes |

---

## 11. Roadmap

### Phase 1 - DONE

- AI Price Estimator
- Property Gallery
- Price History
- ROI Analysis

### Phase 2 - DONE

- Market Analysis
- Mortgage Calculator
- Compare Properties
- Chat with Agent

### Phase 3 - NEXT

- Real Property Photos (from listings)
- Property Details Page
- 3D Virtual Tours
- Mobile App (PWA)

---

## 12. Contact

**Author:** Qamar Sobhy

- GitHub: [@qamarsobhy7-source](https://github.com/qamarsobhy7-source)
- Live App: [da.gd/AOPPkw](https://da.gd/AOPPkw)
- Email: qamarsobhy7@gmail.com
