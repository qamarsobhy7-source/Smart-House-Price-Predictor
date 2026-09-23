# 🏠 Smart House Price Predictor

> **An end-to-end Machine Learning system for predicting residential property prices in the Egyptian real estate market.**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.6.1-orange.svg)](https://scikit-learn.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![R²](https://img.shields.io/badge/R²-0.9721-success.svg)]()
[![MAPE](https://img.shields.io/badge/MAPE-6.50%25-brightgreen.svg)]()
[![Tests](https://img.shields.io/badge/Tests-25%20passing-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

🔗 **[Live Demo →](https://smart-house-price-predictor.streamlit.app)**

---

## 📌 Overview

A complete AI/ML pipeline for predicting apartment prices in Egypt, from data generation through cloud deployment. Combines classical machine learning, Arabic NLP, explainable AI, and modern MLOps practices.

### 🎯 Key Results

| Metric | Value |
|--------|-------|
| **R² Score** | **0.9721** |
| **MAPE** | **6.50%** |
| **MAE** | 305,835 EGP |
| **RMSE** | 445,558 EGP |
| **Features** | 38 (incl. 10 NLP) |
| **Models Trained** | 7 + Optuna tuning |
| **Tests** | 25 passing |

### 🚀 Feature Highlights

- ✅ **7 ML models** compared with Optuna hyperparameter tuning
- ✅ **38 engineered features** (interaction, binary, target encoding, Arabic NLP)
- ✅ **Explainable AI** with SHAP per-prediction contributions
- ✅ **Arabic NLP** on property descriptions (10 binary features)
- ✅ **Modern Streamlit UI** with 4 tabs (Prediction / Explanation / Map / What-If)
- ✅ **REST API** with Swagger documentation
- ✅ **25 unit tests** (100% pass rate)
- ✅ **Docker** container + GitHub Actions CI
- ✅ **Deployed on Streamlit Cloud**

---

## 📊 Version Comparison

| Metric | v1.0 | **v3.0** | Improvement |
|--------|------|----------|-------------|
| R² | 0.6493 | **0.9721** | **+49.7%** |
| MAPE | 27.77% | **6.50%** | **−76.6%** |
| Features | 13 | **38** | 3× |
| Models | 3 | **7 + Optuna** | Advanced |
| Arabic NLP | ❌ | ✅ | Added |
| SHAP | ❌ | ✅ | Added |
| Interactive Map | ❌ | ✅ | Added |
| REST API | Basic | **Swagger** | Upgraded |

---

## ❓ Why the Dataset Was Reduced from 39,000 to 5,000 Records

This was a **deliberate engineering decision**, not a random choice.

### 🔍 Issues in the Original Data

| Issue | Share | Action Taken |
|-------|-------|--------------|
| Missing values in critical columns | **72%** | Dropped |
| Data leakage (pre-computed `price_per_sqm`) | 15% | Excluded |
| Extreme outliers (< 100K or > 50M EGP) | 8% | IQR filtering |
| Exact duplicates | 21% | Deduplicated |
| Mixed property types | — | Apartments only |

### ✅ Engineering Decision

Instead of cleaning every category (which fragments the model), we focused on **high-confidence residential apartments**, raising data quality from **34% to 98%**.

### 📈 Why the Smaller Dataset Performs Better

> **Data quality > Data quantity**

- Noise removed from input errors and duplicates
- Homogeneous target (only apartments)
- Stronger **feature engineering** compensated for fewer rows
- **Target encoding** turned location into a powerful numeric signal (correlation **+0.72**)

---

## 🗂️ Project Structure
