# Egypt Property Finder Dataset

## Overview

The Egypt Property Finder Dataset is a large-scale collection of real estate listings from Egypt, containing residential and commercial properties available for sale and rent.

The dataset includes property characteristics, pricing information, geographic location data, amenities, and listing metadata, making it suitable for machine learning, data analysis, geospatial analytics, and real estate research.

### Dataset Size

* Total Listings: 64,106
* Residential Buy Listings: 19,966
* Commercial Buy Listings: 8,959
* Commercial Rent Listings: 14,080
* Format: JSONL and CSV
* Total Package Size: ~182 MB

---

## Directory Structure

```text
Egypt_Property_Finder_Kaggle/
├── raw/
│   ├── all_egypt.jsonl
│   ├── buy_clean.jsonl
│   ├── commercial_buy.jsonl
│   └── commercial_rent.jsonl
│
├── processed/
│   ├── all_egypt.csv
│   ├── buy.csv
│   ├── commercial_buy.csv
│   └── commercial_rent.csv
│
├── metadata/
│   ├── schema.json
│   └── data_dictionary.csv
│
└── docs/
```

---

## Available Features

Typical fields include:

* id
* title
* price
* currency
* property_type
* category
* bedrooms
* bathrooms
* size
* location
* latitude
* longitude
* amenities
* images
* share_url
* scraped_at_utc

Some fields may contain missing values depending on listing completeness.

---

## Potential Use Cases

### Machine Learning

* Property price prediction
* Rent estimation
* Property valuation models
* Feature engineering exercises

### Data Science

* Exploratory data analysis
* Missing-value handling
* Data cleaning pipelines
* Outlier detection

### Geospatial Analytics

* Real estate heatmaps
* Location-based pricing analysis
* Neighborhood comparison studies

### Recommendation Systems

* Property recommendation engines
* Similar listing retrieval
* Search ranking experiments

---

## Data Quality

Audit Results:

* Duplicate Rate: 0%
* Consistent schema across subsets
* Residential and commercial property coverage
* JSONL and flattened CSV formats available

---

## Privacy & Ethics

A comprehensive audit was performed before publication.

Verified findings:

* No phone numbers detected
* No email addresses detected
* No WhatsApp links detected
* No apartment numbers detected
* No building numbers detected
* No exact private residential addresses detected

Location information is limited to publicly visible geographic descriptors such as neighborhoods, compounds, districts, cities, and street names commonly displayed in public real estate listings.

---

## Source

The dataset was collected from publicly accessible real estate listings on Property Finder Egypt and is provided for educational, research, and analytical purposes.

Users are responsible for ensuring compliance with applicable laws, regulations, and platform terms when using the data.

---

## Citation

If you use this dataset in research or projects, please cite:

Egypt Property Finder Dataset (2026)
64K+ Real Estate Listings Across Egypt
Kaggle Dataset


---

## License

Please refer to the license specified in dataset-metadata.json.
