"""Property description sentiment analysis (English, real-estate tuned)."""

POSITIVE_KEYWORDS = {
    "sea view": 1.5, "ocean view": 1.4, "waterfront": 1.4,
    "garden": 1.0, "private garden": 1.2, "backyard": 1.0,
    "duplex": 1.2, "roof": 1.1, "penthouse": 1.4,
    "furnished": 1.0, "fully furnished": 1.3,
    "new": 1.0, "brand new": 1.3, "modern": 1.2,
    "luxury": 1.4, "luxurious": 1.4, "premium": 1.3, "high-end": 1.4,
    "elegant": 1.2, "spacious": 1.2, "bright": 1.0,
    "quiet": 1.0, "safe": 1.0, "peaceful": 1.0,
    "renovated": 1.2, "upgraded": 1.0, "well-maintained": 1.1,
    "central": 0.8, "close to": 0.6, "convenient": 0.8,
    "parking": 0.8, "garage": 0.8, "elevator": 0.7,
    "balcony": 0.8, "terrace": 0.9, "pool": 1.2,
}

NEGATIVE_KEYWORDS = {
    "old": 1.3, "outdated": 1.4, "needs work": 1.5, "fixer-upper": 1.4,
    "small": 1.0, "narrow": 1.2, "cramped": 1.4,
    "noisy": 1.3, "crowded": 1.1, "busy": 0.8,
    "far": 1.2, "remote": 1.0, "isolated": 1.1,
    "bad": 1.5, "poor": 1.4, "damaged": 1.5,
    "no finishing": 1.3, "unfinished": 1.2, "under construction": 0.7,
    "ground floor": 0.5, "basement": 1.0, "no elevator": 1.0,
    "expensive": 0.8, "overpriced": 1.3,
}


def analyze_sentiment(text: str) -> dict:
    """Analyze real-estate description sentiment.

    Returns:
        dict with 'score' (-1 to +1), 'label' (positive/neutral/negative),
        and 'matched_keywords' list.
    """
    if not text or not text.strip():
        return {"score": 0.0, "label": "neutral", "matched_keywords": []}

    text_lower = text.lower()
    pos_score = 0.0
    neg_score = 0.0
    matched = []

    for kw, weight in POSITIVE_KEYWORDS.items():
        if kw in text_lower:
            pos_score += weight
            matched.append((kw, "+", weight))

    for kw, weight in NEGATIVE_KEYWORDS.items():
        if kw in text_lower:
            neg_score += weight
            matched.append((kw, "-", weight))

    total = pos_score + neg_score
    if total == 0:
        return {"score": 0.0, "label": "neutral", "matched_keywords": []}

    normalized = (pos_score - neg_score) / total
    normalized = max(-1.0, min(1.0, normalized))
    label = "positive" if normalized > 0.2 else "negative" if normalized < -0.2 else "neutral"

    return {
        "score": round(normalized, 3),
        "label": label,
        "matched_keywords": matched,
    }
