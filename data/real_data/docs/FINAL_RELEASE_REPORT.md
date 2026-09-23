# Final Release Report

## Dataset Statistics
- Total Package Size: 182.49 MB
- buy_clean.jsonl Recovered Records: 19966
- Duplicates: 0% 
- Missing Values: ~10% global

## Included Files
- `raw/` JSONL datasets (Master and Categorical subsets)
- `processed/` CSV flattened representations
- `dataset-metadata.json` for Kaggle API initialization

## Excluded Files
- Broken `buy.jsonl` (Replaced by `buy_clean.jsonl`)
- `catboost_info/` and model weight directories.

## Privacy Audit Summary
- Street names retained.
- Exact doors/buildings absent.
- PII (emails/phones) absent from root schema.
- Verdict: Safe for public distribution.

## Kaggle Readiness
- 100% Ready.
