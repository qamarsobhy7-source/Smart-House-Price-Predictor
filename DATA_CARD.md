# Data Card — Smart House Price Predictor

## Dataset Overview

| Field | Value |
|-------|-------|
| **Name** | Egypt Property Finder Real Estate Dataset |
| **Source** | PropertyFinder Egypt (public listings) |
| **Platform** | Kaggle: mohammedhassan1112/egypt-property-finder |
| **License** | CC0-1.0 |
| **Size (raw)** | 64106 listings |
| **Size (final training)** | 7749 apartments |
| **Scrape Date** | 2026-02-19 |
| **Format** | CSV / JSONL |

---

## Motivation

We chose to use **real scraped listings** instead of synthetic data because:

- Real listings reflect actual market conditions
- Amenities, GPS, and titles are genuine
- The model becomes credible for real-world use
- Avoids misleading "high accuracy on fake data" pitfalls

---

## Composition

### Data Funnel

| Stage | Records | Removed |
|-------|---------|---------|
| Raw scrape (buy + rent + commercial) | 64106 | - |
| Buy only (residential + commercial) | 19967 | 44139 |
| Apartments only | 10277 | 9690 |
| Remove suspicious_low price flag | 10276 | 1 |
| Price 500K-50M filter | 10248 | 28 |
| Size 40-500 sqm filter | 9459 | 789 |
| Bedrooms 1-6 filter | 9089 | 370 |
| 5th-95th percentile on price & price/sqm | 7749 | 1340 |

### Cities (9)

| City | Listings |
|------|----------|
| Cairo | 5504 |
| Giza | 2259 |
| Red Sea | 855 |
| Alexandria | 236 |
| North Coast | 104 |
| Suez | 85 |
| Qalyubia | 36 |
| Matrouh | 4 |
| Al Daqahlya | 3 |

### Top Districts (43 total)

New Cairo City, Sheikh Zayed City, 6 October City, Hurghada, Mostakbal City, New Capital City, Madinaty, Shorouk City, Hay Sharq, Hay El Maadi, etc.

### Price Statistics (after cleaning)

- **Min:** about 650000 EGP
- **Median:** 7500000 EGP
- **Max:** about 18500000 EGP
- **Median price/sqm:** 52398 EGP/sqm

### Features (64 total)

#### Numeric (61)

- latitude, longitude, size, log_size, sqrt_size
- bedrooms, bathrooms, bed_bath_ratio, area_per_bedroom, rooms_total
- amenity_* (32 flags): balcony, pool, garden, security, gym, etc.
- nlp_* (12 flags from titles): sea_view, garden, luxury, etc.
- title_length, title_word_count
- geo_cluster (15 clusters via KMeans on GPS)
- distance_to_cairo
- amenity_count

#### Categorical (3)

- city, district, compound

---

## Preprocessing

1. Filtered to apartments only
2. Removed suspicious_low price flags
3. Price range limited to 500K-50M EGP
4. Size range limited to 40-500 sqm
5. Bedrooms limited to 1-6
6. IQR outlier removal on price and price/sqm
7. Location parsing - split location string into city/district/compound
8. Amenity decoding - codes (BA, SE) to binary features
9. NLP feature extraction - keyword matching on titles
10. Target encoding - median price/sqm per city, district, compound

---

## Biases & Limitations

### Known Biases

- **Geographic:** Cairo + Giza = 77% of listings
- **Property type:** Apartments only (villas, chalets, land excluded)
- **Listing bias:** Asking prices, not final sale prices
- **Time snapshot:** All listings scraped on 2026-02-19
- **Platform bias:** Only PropertyFinder Egypt listings

### Not Represented

- Off-market sales
- Distressed sales
- Older buildings (many listings are new developments)
- Informal settlements

---

## Ethical Review

| Aspect | Status |
|--------|--------|
| Personal data | None |
| Data source | Public listings |
| Consent | Public web scrape (ToS-compliant) |
| Transparency | Full funnel documented |
| Reproducibility | random_state=42 |

---

## Splits

| Split | Records | Purpose |
|-------|---------|---------|
| Train | 6199 | Model fitting + CV |
| Test | 1550 | Held-out evaluation |

---

## Citation

Egypt Property Finder Dataset (2026)
Source: PropertyFinder Egypt
Kaggle: mohammedhassan1112/egypt-property-finder
