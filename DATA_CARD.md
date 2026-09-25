# Data Card — Smart House Price Predictor

## Dataset Overview

| Field | Value |
|-------|-------|
| **Name** | Egypt Property Finder Real Estate Dataset |
| **Source** | PropertyFinder Egypt (public listings) |
| **Platform** | Kaggle: `mohammedhassan1112/egypt-property-finder` |
| **License** | CC0-1.0 |
| **Raw Size** | 64,106 listings |
| **Final Size** | 7,749 apartments |
| **Scrape Date** | February 2026 |
| **Format** | CSV, JSONL |

---

## Motivation

We chose to use **real scraped listings** instead of synthetic data because:

- Real listings reflect actual market conditions
- Amenities, GPS, and titles are genuine
- The model becomes credible for real-world use
- Avoids misleading "high accuracy on fake data" pitfalls

---

## Data Funnel

| Stage | Records | Filter Applied |
|-------|--------:|----------------|
| Raw scrape | 64,106 | All buy + rent listings |
| Buy only | 19,967 | Excluded rentals |
| Apartments only | 10,277 | Excluded villas, chalets, commercial |
| Price filter | 10,248 | 500K - 50M EGP |
| Size filter | 9,459 | 40 - 500 m² |
| Bedroom filter | 9,089 | 1-6 bedrooms |
| **Final cleaned** | **7,749** | IQR outlier removal |

---

## Composition

### Cities (9)

| City | Listings |
|------|---------:|
| Cairo | 5,504 |
| Giza | 2,259 |
| Red Sea | 855 |
| Alexandria | 236 |
| North Coast | 104 |
| Suez | 85 |
| Qalyubia | 36 |
| Matrouh | 4 |
| Al Daqahlya | 3 |

### Geographic Coverage

- **Cities:** 9
- **Districts:** 43
- **Compounds:** 890
- **All with GPS coordinates**

### Price Statistics

| Metric | Value |
|--------|-------|
| Minimum | ~650,000 EGP |
| Median | 7,500,000 EGP |
| Mean | 6,736,055 EGP |
| Maximum | ~18,500,000 EGP |
| Median price/m² | 52,398 EGP/m² |

---

### Features (64 total)

#### Numeric (61)

- **GPS:** latitude, longitude, geo_cluster, distance_to_cairo
- **Core:** size, log_size, sqrt_size, bedrooms, bathrooms
- **Interactions:** bed_bath_ratio, area_per_bedroom, rooms_total, area_per_room
- **Amenities:** 32 binary flags (pool, gym, garden, parking, security)
- **NLP:** 12 features (sea_view, garden, luxury, furnished)
- **Target Encodings:** city_ppm, district_ppm, compound_ppm

#### Categorical (3)

- city, district, compound

---

## Preprocessing

1. **Filtered** to apartments only
2. **Removed** suspicious_low price flags
3. **Price range** 500K - 50M EGP
4. **Size range** 40 - 500 m²
5. **Bedrooms** 1-6
6. **IQR outlier removal** on price and price/sqm
7. **Location parsing** — split into city/district/compound
8. **Amenity decoding** — codes → binary features
9. **NLP extraction** — keyword matching on titles
10. **Target encoding** — median price/sqm per group

---

## Data Sources

| Source | Purpose |
|--------|---------|
| [PropertyFinder Egypt](https://www.propertyfinder.eg) | Primary listings |
| [Kaggle](https://www.kaggle.com/datasets/mohammedhassan1112/egypt-property-finder) | Dataset hosting |

---

## Biases & Limitations

### Known Biases

- **Geographic:** Cairo + Giza = 77% of data
- **Property type:** Apartments only
- **Listing bias:** Asking prices, not final sales
- **Time snapshot:** All scraped in Feb 2026
- **Platform bias:** Only PropertyFinder listings

### Not Represented

- Off-market sales
- Distressed sales
- Informal settlements
- Buildings older than 30 years

---

## Ethical Review

| Aspect | Status |
|--------|--------|
| Personal data | ✅ None |
| Source | ✅ Public listings |
| Transparency | ✅ Full funnel documented |
| Reproducibility | ✅ Fixed random seeds |

---

## Splits

| Split | Records | Purpose |
|-------|--------:|---------|
| Train | 6,199 | Model fitting |
| Test | 1,550 | Held-out evaluation |

---

## Citation

```bibtex
@misc{egypt_property_finder_2026,
  title={Egypt Property Finder Dataset},
  author={PropertyFinder Egypt},
  year={2026},
  publisher={Kaggle},
  howpublished={\url{https://www.kaggle.com/datasets/mohammedhassan1112/egypt-property-finder}}
}
```
