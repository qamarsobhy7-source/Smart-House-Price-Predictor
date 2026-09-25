"""
AraBERT Sentiment Analysis for Real Estate
============================================
Smart hybrid sentiment analysis for Arabic real-estate descriptions.

Combines:
1. Real-estate domain keywords (MSA + Egyptian colloquial)
2. AraBERT Transformer for colloquial expressions
"""
import re
from transformers import pipeline


MODEL_NAME = "CAMeL-Lab/bert-base-arabic-camelbert-da-sentiment"
_sentiment_pipeline = None
ARABERT_CONFIDENCE_THRESHOLD = 0.85


_load_attempted = False


def _load_pipeline():
    """Lazy-load AraBERT on first call. Falls back gracefully if loading fails."""
    global _sentiment_pipeline, _load_attempted
    if _load_attempted:
        return _sentiment_pipeline
    _load_attempted = True
    try:
        _sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model=MODEL_NAME,
            tokenizer=MODEL_NAME,
            device=-1,  # CPU
        )
        print("✅ AraBERT loaded successfully")
    except Exception as e:
        print(f"⚠️  AraBERT unavailable, using keywords: {e}")
        _sentiment_pipeline = None
    return _sentiment_pipeline


# ==========================================================
# Keywords (sorted by length for proper negation handling)
# ==========================================================
POSITIVE_KEYWORDS = {
    # Longest matches first
    "فيو مفتوح": 1.3, "سوبر لوكس": 1.5, "حمام سباحة": 1.2,
    "بتجنن": 1.5, "يجنن": 1.5, "تجنن": 1.5, "جنان": 1.4,
    "تحفة": 1.4, "زي الفل": 1.4, "جمدة": 1.3,
    "رائع": 1.2, "رائعة": 1.2, "ممتاز": 1.3, "ممتازة": 1.3,
    "جميل": 1.0, "جميلة": 1.0, "مريح": 0.9, "مريحة": 0.9,
    "أنيق": 1.0, "أنيقة": 1.0, "مثالي": 1.2, "مثالية": 1.2,
    "راقي": 1.2, "راقية": 1.2, "فاخر": 1.4, "فاخرة": 1.4,
    "نظيف": 1.0, "نظيفة": 1.0, "واسع": 1.1, "واسعة": 1.1,
    "هادئ": 1.0, "هادئة": 1.0, "جديد": 1.0, "جديدة": 1.0,
    "روف": 1.1, "دوبلكس": 1.2, "بحرية": 1.5, "بحر": 1.2,
    "فيو": 1.0, "حديقة": 1.0, "جاردن": 1.0,
    "مفروش": 1.0, "مفروشة": 1.0,
    "قريب": 0.8, "قريبة": 0.8, "مترو": 0.7,
    "جراج": 0.8, "باركنج": 0.8, "اسانسير": 0.7,
    "مصعد": 0.7, "جيم": 0.8, "نادي": 0.7,
    "حلو": 0.8, "حلوة": 0.8, "لذيذ": 0.9, "عسل": 1.0,
    "خطير": 1.2, "شيخ": 0.9, "روعة": 1.3,
}

NEGATIVE_KEYWORDS = {
    # Longest matches first
    "بدون تشطيب": 1.3, "نصف تشطيب": 1.0, "طابق أرضي": 0.8,
    "بدون اسانسير": 1.2, "مش حلو": 1.3, "مش حلوة": 1.3,
    "مش نظيف": 1.3, "مش نظيفة": 1.3,
    "وحش": 1.4, "وحشة": 1.4, "زفت": 1.5, "زبالة": 1.5,
    "معفن": 1.5, "معفنة": 1.5, "ملخبط": 1.2, "ملخبطة": 1.2,
    "وسخ": 1.4, "وسخة": 1.4, "مقرف": 1.3, "مقرفة": 1.3,
    "خربان": 1.3, "خربانة": 1.3,
    "سيء": 1.5, "سيئة": 1.5, "قديم": 1.3, "قديمة": 1.3,
    "متهالك": 1.5, "متهالكة": 1.5, "ضيق": 1.2, "ضيقة": 1.2,
    "بعيد": 1.2, "بعيدة": 1.2, "مزدحم": 1.0, "مزدحمة": 1.0,
    "معزول": 1.1, "معزولة": 1.1, "مهجور": 1.4, "مهجورة": 1.4,
}


def _keyword_detail(text: str) -> dict:
    """Return detailed keyword analysis with pos/neg scores."""
    if not text:
        return {"score": 0.0, "pos": 0.0, "neg": 0.0}

    text_lower = text.lower()
    pos_score = 0.0
    neg_score = 0.0
    remaining = text_lower

    # Match NEGATIVE first (longer phrases take priority)
    for kw, weight in sorted(NEGATIVE_KEYWORDS.items(), key=lambda x: -len(x[0])):
        if kw in remaining:
            neg_score += weight
            remaining = remaining.replace(kw, " ")

    # Then POSITIVE
    for kw, weight in sorted(POSITIVE_KEYWORDS.items(), key=lambda x: -len(x[0])):
        if kw in remaining:
            pos_score += weight
            remaining = remaining.replace(kw, " ")

    total = pos_score + neg_score
    score = (pos_score - neg_score) / total if total > 0 else 0.0
    return {"score": score, "pos": pos_score, "neg": neg_score}


def keyword_sentiment(text: str) -> float:
    """Backward-compatible wrapper."""
    return _keyword_detail(text)["score"]


def analyze_sentiment(text: str) -> dict:
    """
    Smart hybrid sentiment for real-estate descriptions.

    Rules:
    1. Empty → neutral
    2. Both positive AND negative keywords (conflict) → neutral
    3. Strong single-side keywords (|score| > 0.3) → use keywords
    4. No keywords → neutral (no real-estate signal)
    5. Weak keywords → blend with AraBERT
    """
    if not text or not text.strip():
        return {
            "score": 0.0, "label": "neutral",
            "source": "empty", "keyword_score": 0.0,
        }

    kw = _keyword_detail(text)
    kw_score = kw["score"]
    kw_pos = kw["pos"]
    kw_neg = kw["neg"]

    # Rule 2: Conflicting keywords (both positive and negative present)
    # → sentiment is unclear → neutral
    if kw_pos > 0 and kw_neg > 0:
        return {
            "score": 0.0,
            "label": "neutral",
            "source": "conflict",
            "keyword_score": round(kw_score, 3),
        }

    # Rule 3: Strong single-side keywords
    if abs(kw_score) > 0.3:
        return {
            "score": round(kw_score, 3),
            "label": "positive" if kw_score > 0 else "negative",
            "source": "keywords",
            "keyword_score": round(kw_score, 3),
        }

    # Rule 4: No keywords → neutral
    if kw_pos == 0 and kw_neg == 0:
        return {
            "score": 0.0,
            "label": "neutral",
            "source": "no_signal",
            "keyword_score": 0.0,
        }

    # Rule 5: Weak keywords → blend with AraBERT
    pipe = _load_pipeline()
    if pipe is not None:
        try:
            result = pipe(text[:512])[0]
            arabert = (
                result["score"]
                if result["label"].lower() == "positive"
                else -result["score"]
            )
            final_score = 0.6 * arabert + 0.4 * kw_score
            return {
                "score": round(final_score, 3),
                "label": (
                    "positive" if final_score > 0.2
                    else "negative" if final_score < -0.2
                    else "neutral"
                ),
                "source": "blended",
                "keyword_score": round(kw_score, 3),
            }
        except Exception:
            pass

    return {
        "score": round(kw_score, 3),
        "label": "positive" if kw_score > 0 else "negative",
        "source": "keywords",
        "keyword_score": round(kw_score, 3),
    }


def get_sentiment_emoji(label: str) -> str:
    """Return emoji for sentiment label."""
    return {"positive": "😊", "negative": "😟", "neutral": "😐"}.get(label, "😐")
