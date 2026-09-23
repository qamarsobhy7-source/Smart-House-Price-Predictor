# Data Card — Smart House Price Predictor

## Dataset Overview

| Field | Value |
|-------|-------|
| **Name** | Egypt Real Estate Synthetic Dataset v3 |
| **Version** | 3.0.0 |
| **Size** | 8,000 records |
| **Features** | 40 columns (before engineering) → 38 model features |
| **Cities** | 10 |
| **Districts** | 40+ |
| **Generated** | 2024–2025 market simulation |
| **Format** | CSV (UTF-8) |
| **License** | MIT |

---

## Motivation

The original raw dataset (39,000 records) had severe quality issues:

| Issue | Share | Resolution |
|-------|-------|------------|
| Missing values in critical columns | **72%** | Dropped |
| Data leakage (pre-computed price/sqm) | 15% | Excluded |
| Extreme outliers (<100K or >50M EGP) | 8% | IQR filtered |
| Exact duplicates | 21% | Deduplicated |
| Mixed property types | — | Filtered to apartments |

**Decision:** Generate a clean, homogeneous synthetic dataset grounded in real 2024–2025 Egyptian market prices.

---

## Composition

### Cities (10)

| City | Records | Avg Price (EGP) |
|------|---------|-----------------|
| Cairo | 2,413 | 5,200,000 |
| Giza | 1,566 | 5,720,000 |
| Alexandria | 959 | 2,680,000 |
| Port Said | 479 | 2,260,000 |
| Suez | 488 | 1,850,000 |
| Ismailia | 417 | 1,940,000 |
| Mansoura | 413 | 1,920,000 |
| Tanta | 417 | 1,810,000 |
| Luxor | 455 | 1,610,000 |
| Aswan | 393 | 1,760,000 |

### Price Distribution

- **Min:** ~650,000 EGP
- **Median:** ~4,130,000 EGP
- **Mean:** ~4,670,000 EGP
- **Max:** ~20,500,000 EGP
- **Transform:** `log1p` applied during training

### Features

#### Numerical (20)

`area_value`, `bedrooms_clean`, `bathrooms_clean`, `is_studio`, `has_reception`, `has_living`, `has_kitchen`, `bed_bath_ratio`, `area_per_bedroom`, `area_per_bathroom`, `rooms_total`, `area_per_room`, `is_completed`, `is_under_construction`, `is_off_plan`, `is_furnished`, `is_semi_furnished`, `city_price_per_sqm`, `town_price_per_sqm`, `district_price_per_sqm`

#### Categorical (6)

`city`, `town`, `district`, `subdistrict`, `furnished`, `completion_status`

#### Arabic NLP (10)

`nlp_sea_view`, `nlp_garden`, `nlp_duplex`, `nlp_roof`, `nlp_furnished`, `nlp_new`, `nlp_super_lux`, `nlp_open_view`, `nlp_parking`, `nlp_elevator`

Plus `description_length`, `description_word_count`.

---

## Collection Process

Properties generated via probabilistic sampling:

1. **Location** → sampled from 10 cities weighted by real population
2. **Area** → lognormal distribution (median ~120 m²)
3. **Bedrooms** → categorical (1–5, weighted)
4. **Price** → base city price/sqm × modifiers:
   - Completion status (completed = +15%, off-plan = −15%)
   - Furnished (+10% for Yes, +3% for Semi)
   - Area discount (larger units → lower EGP/m²)
   - Bedroom multiplier
   - Gaussian noise (σ=8%)
5. **NLP** → realistic Arabic descriptions generated

---

## Preprocessing

1. Missing `bedrooms_clean` → set to 0 for studios, median for others
2. Interaction features computed
3. Binary flags encoded
4. **Target Encoding** applied to `city`, `town`, `district` (mean price/sqm per group, computed on training data only)
5. **NLP features** extracted via keyword matching

---

## Biases & Limitations

### Known Biases

- **Geographic:** Cairo + Giza = 50% of data (weighted by real population)
- **Property type:** Only apartments (excludes villas, land, commercial)
- **Price range:** Capped at 30M EGP (excludes ultra-luxury)
- **Time:** Single snapshot — no temporal drift

### Not Represented

- Buildings older than 30 years
- Informal settlements
- Fractional ownership
- Rent-to-own schemes

---

## Ethical Review

| Aspect | Status |
|--------|--------|
| Personal data | ✅ None |
| Consent | N/A (synthetic) |
| Geographic fairness | ✅ 10 cities |
| Transparency | ✅ Full generation code in repo |
| Reproducibility | ✅ `random_state=42` |

---

## Splits

| Split | Records | Purpose |
|-------|---------|---------|
| Train | 6,400 | Model fitting + CV |
| Test | 1,600 | Held-out evaluation |

**Stratification:** None (regression target)

---

## Maintenance

- **Versioning:** Semantic (major.minor.patch)
- **Regeneration:** Deterministic — `random_state=42`
- **Updates:** Quarterly review against real market data

---

## Citation
