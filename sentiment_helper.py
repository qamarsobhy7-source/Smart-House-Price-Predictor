"""Arabic sentiment analysis tuned for real estate descriptions."""
import re


POSITIVE_KEYWORDS = {
    "بحرية": 1.5, "بحر": 1.2, "فيو مفتوح": 1.3, "فيو": 1.0,
    "حديقة": 1.0, "جاردن": 1.0, "دوبلكس": 1.2, "روف": 1.1,
    "مفروش": 1.0, "مفروشة": 1.0, "جديد": 1.0, "جديدة": 1.0,
    "سوبر لوكس": 1.5, "الترا": 1.3, "فاخر": 1.4, "راقي": 1.2,
    "هادئ": 1.0, "نظيف": 1.0, "واسع": 1.1, "مميز": 1.2,
    "قريب": 0.8, "تشطيب": 1.0, "استلام": 0.5,
    "sea view": 1.5, "garden": 1.0, "luxury": 1.4, "furnished": 1.0,
    "new": 1.0, "duplex": 1.2, "roof": 1.1, "quiet": 1.0,
    "spacious": 1.1, "premium": 1.3, "modern": 1.0,
}

NEGATIVE_KEYWORDS = {
    "قديم": 1.3, "قديمة": 1.3, "متهالك": 1.5, "متهالكة": 1.5,
    "ضيق": 1.2, "ضيقة": 1.2, "مزدحم": 1.0, "مزدحمة": 1.0,
    "بعيد": 1.2, "بعيدة": 1.2, "سيء": 1.5, "سيئة": 1.5,
    "بدون تشطيب": 1.2, "نصف تشطيب": 0.8, "طابق أرضي": 0.5,
    "old": 1.3, "narrow": 1.2, "crowded": 1.0, "far": 1.2,
    "bad": 1.5, "no finishing": 1.2,
}


def analyze_sentiment(text: str) -> dict:
    """Analyze real-estate description sentiment."""
    if not text or not text.strip():
        return {"score": 0.0, "label": "neutral", "matched_keywords": []}

    text_lower = text.lower()
    pos_score = 0.0
    neg_score = 0.0
    matched = []

    for kw, weight in POSITIVE_KEYWORDS.items():
        if kw.lower() in text_lower:
            pos_score += weight
            matched.append((kw, "+", weight))

    for kw, weight in NEGATIVE_KEYWORDS.items():
        if kw.lower() in text_lower:
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
