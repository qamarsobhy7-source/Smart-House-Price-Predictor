# Technical Notes

Deep-dive into the technical architecture and implementation details.

---

## 1. System Architecture

```
+--------------------------------------------------------------+
|                     USER INTERFACE LAYER                     |
|  Streamlit 1.31+ | Custom CSS (nawy_theme.py) | Plotly       |
+--------------------------------------------------------------+
                              |
                              v
+--------------------------------------------------------------+
|                    BUSINESS LOGIC LAYER                      |
|  streamlit_app.py (2,800+ lines)                             |
|  - Form handling  - Data processing  - Chart rendering       |
|  - Session state  - PDF generation   - Map rendering         |
+--------------------------------------------------------------+
                              |
                              v
+--------------------------------------------------------------+
|                     ML MODEL LAYER                           |
|  predictor.py                                                |
|  - load_artifacts()                                          |
|  - build_features()                                          |
|  - predict_with_confidence()                                 |
+--------------------------------------------------------------+
                              |
                              v
+--------------------------------------------------------------+
|                      DATA LAYER                              |
|  - FINAL_DATASET_v9.csv (46 MB, 119,916 listings)            |
|  - egypt_hierarchy.json (299 KB, 27 governorates)            |
|  - FINAL_MODEL_v9.pkl (12 MB, trained CatBoost)              |
+--------------------------------------------------------------+
```

---

## 2. Data Pipeline

### Data Collection

Sources scraped from:
1. PropertyFinder Egypt
2. Bayut Egypt
3. Egyptian Real Estate Listings
4. OLX Mining
5. GitHub: Real-Estate-Intelligence
6. GitHub: Scraping-Predictive

### Data Cleaning

- Removed duplicates
- Handled missing values
- Validated coordinates (lat/lon)
- Standardized location names
- Filtered outliers (0.5% - 99.5% quantile)

### Feature Engineering

**Numeric Features (20):**
- `size` - Property size in sqm
- `bedrooms` - Number of bedrooms
- `bathrooms` - Number of bathrooms
- `images_count` - Number of listing images
- `latitude`, `longitude` - GPS coordinates
- `amenity_count` - Number of amenities
- `distance_to_cairo` - Distance from Cairo center
- `distance_to_coast` - Distance from coastline
- `is_premium`, `is_featured`, `is_luxury` - Boolean flags
- `is_compound` - Is inside a compound
- `walk_score`, `transit_score`, `amenity_score` - Location scores
- `area_per_room` - sqm per room
- `total_rooms` - Bedrooms + bathrooms + living + kitchen
- `bed_bath_ratio` - Bedrooms / bathrooms
- `lat_x_lon` - Location interaction feature

**Categorical Features (12):**
- `property_type` - Apartment, Villa, Duplex, etc.
- `governorate` - Cairo, Giza, etc.
- `district` - Specific neighborhood
- `compound` - Building complex name
- `town` - Township
- `completion_status` - Ready, Off-plan, Under construction
- `furnished` - Unfurnished, Partly, Furnished
- `seller_type` - Broker, Owner, Developer
- `developer_name` - Developer name
- `view` - Garden, Pool, Sea, etc.
- `finishing_type` - Core & Shell, Semi, Finished, Super Lux
- `payment_method` - Cash, Installments

---

## 3. Model Training

### CatBoost Configuration

```python
from catboost import CatBoostRegressor

model = CatBoostRegressor(
    iterations=1000,
    learning_rate=0.05,
    depth=6,
    loss_function='RMSE',
    random_seed=42,
    verbose=100,
)

model.fit(
    X_train, y_train,
    cat_features=categorical_indices,
    eval_set=(X_test, y_test),
    early_stopping_rounds=50,
)
```

### Why CatBoost?

1. **Native categorical handling** - Best for our 12 categorical features
2. **Built-in regularization** - Prevents overfitting
3. **Handles missing values** - No need for imputation
4. **Fast inference** - <2s per prediction
5. **Outperformed XGBoost/LightGBM** on this dataset

---

## 4. Prediction Flow

```
User Input (Form)
        |
        v
Validation + Feature Construction
        |
        v
build_features(input_data)
        |
        v
CatBoost Model Prediction
        |
        v
Confidence Interval Calculation
        |
        v
Market Comparison
        |
        v
Display Result + Charts + Map + ROI
```

---

## 5. UI/UX Design Principles

### Inspiration

- **Nawy** - Clean minimalism, blue palette
- **Aqarmap** - Arabic RTL support
- **Zillow** - Zestimate-style valuation
- **Property Finder** - Search-led experience

### Color Palette

| Color | Hex | Usage |
|:---:|:---:|:---:|
| Primary Blue | #0066FF | Buttons, links |
| Accent Orange | #FF6B35 | Highlights, forecasts |
| Success Green | #059669 | Positive metrics |
| Danger Red | #DC2626 | Warnings |
| Dark Text | #0A0F1C | Body text |
| Light BG | #F8FAFC | Backgrounds |

### Typography

- **Arabic:** Cairo font
- **English:** Inter font

---

## 6. Performance

| Metric | Value |
|:---:|:---:|
| Model Size | 12 MB |
| Dataset Size | 46 MB |
| First Load | ~30s |
| Cached Load | <2s |
| Prediction Time | <2s |
| Memory Usage | ~500 MB |

### Optimization Strategies

- `@st.cache_resource` for model
- `@st.cache_data` for datasets
- Session state for UI persistence
- Lazy loading of heavy components

---

## 7. Security & Privacy

- No user authentication required
- No personal data collection
- All processing in browser session
- Data is public (scraped from public listings)
- HTTPS via Streamlit Cloud

---

## 8. Deployment

### Streamlit Cloud

```
Repository: qamarsobhy7-source/Smart-House-Price-Predictor
Branch: main
Main file: streamlit_app.py
Python: 3.11
Region: US-East
```

### Auto-Deploy

- Push to `main` triggers rebuild
- Average rebuild time: 2-3 minutes
- Zero-downtime deployment

---

## 9. Testing

### Manual Tests

- Tested on Chrome, Safari, Firefox
- Tested on iOS, Android
- Tested with 50+ prediction scenarios
- Verified all 6 tabs
- Verified bilingual switch
- Verified dark mode

### Test Locations

- Cairo -> New Cairo -> Fifth Settlement
- Giza -> Sheikh Zayed -> Sheikh Zayed Compounds
- Alexandria -> Smouha
- Red Sea -> Hurghada

---

## 10. Known Limitations

1. **Sample Images** - Not real property photos
2. **Estimated Data** - Neighborhood info is template-based
3. **No Real-time Updates** - Data is static
4. **Chat UI Only** - No real backend
5. **R2 = 0.7061** - Prediction error 30%

### Improvement Plans

- Scrape real property images
- Integrate Google Places API for neighborhood
- Add webhooks for real-time updates
- Integrate Chatbase or similar for real chat
- Ensemble multiple models for better R2

---

## 11. File Reference

| File | Purpose | Lines |
|:---:|:---:|:---:|
| `streamlit_app.py` | Main application | 2,800+ |
| `nawy_theme.py` | Custom CSS theme | 1,300+ |
| `predictor.py` | Model logic | 200 |
| `PROJECT_OVERVIEW.md` | Technical doc | 337 |
| `CHANGELOG.md` | Version history | 150+ |
| `README.md` | Main doc | 350+ |
