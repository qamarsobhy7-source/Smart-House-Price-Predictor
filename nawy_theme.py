
"""
Nawy-inspired Professional Theme
Clean, minimal, no emojis, blue + white palette
"""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
TRANS_DIR = BASE / "translations"

# ═══════════════════════════════════════════════════════
# COLORS — Nawy Professional Palette
# ═══════════════════════════════════════════════════════
LIGHT = {
    "primary": "#0066FF",
    "primary_dark": "#0052CC",
    "primary_light": "#4D94FF",
    "primary_soft": "#EBF2FF",
    "accent": "#FF6B35",
    "accent_soft": "#FFF0EB",
    "success": "#059669",
    "success_soft": "#ECFDF5",
    "warning": "#D97706",
    "warning_soft": "#FFFBEB",
    "danger": "#DC2626",
    "danger_soft": "#FEF2F2",
    "text": "#0A0F1C",
    "text_soft": "#334155",
    "text_muted": "#64748B",
    "bg": "#FFFFFF",
    "bg_soft": "#F8FAFC",
    "bg_card": "#FFFFFF",
    "border": "#E2E8F0",
    "border_soft": "#F1F5F9",
    "shadow_sm": "0 1px 2px rgba(15,23,42,0.04)",
    "shadow_md": "0 4px 12px rgba(15,23,42,0.06)",
    "shadow_lg": "0 12px 32px rgba(15,23,42,0.10)",
    "hero_from": "#0A2540",
    "hero_to": "#0066FF",
}

DARK = {
    "primary": "#4D94FF",
    "primary_dark": "#0066FF",
    "primary_light": "#80B3FF",
    "primary_soft": "#0A2540",
    "accent": "#FF8555",
    "accent_soft": "#3D1F0F",
    "success": "#10B981",
    "success_soft": "#064E3B",
    "warning": "#F59E0B",
    "warning_soft": "#451A03",
    "danger": "#EF4444",
    "danger_soft": "#450A0A",
    "text": "#F8FAFC",
    "text_soft": "#CBD5E1",
    "text_muted": "#94A3B8",
    "bg": "#0A0F1C",
    "bg_soft": "#111827",
    "bg_card": "#1A2332",
    "border": "#1E293B",
    "border_soft": "#0F172A",
    "shadow_sm": "0 1px 2px rgba(0,0,0,0.4)",
    "shadow_md": "0 4px 12px rgba(0,0,0,0.5)",
    "shadow_lg": "0 12px 32px rgba(0,0,0,0.6)",
    "hero_from": "#0A0F1C",
    "hero_to": "#0A2540",
}


def get_theme(dark=False):
    return DARK if dark else LIGHT


# ═══════════════════════════════════════════════════════
# TRANSLATIONS
# ═══════════════════════════════════════════════════════
_TRANS_CACHE = {}

def load_translations(lang="en"):
    if lang in _TRANS_CACHE:
        return _TRANS_CACHE[lang]
    path = TRANS_DIR / f"{lang}.json"
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    _TRANS_CACHE[lang] = data
    return data


def t(section, key, lang="en"):
    trans = load_translations(lang)
    return trans.get(section, {}).get(key, f"{section}.{key}")


# ═══════════════════════════════════════════════════════
# CSS TEMPLATE — Nawy Professional
# ═══════════════════════════════════════════════════════
CSS_TEMPLATE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Cairo:wght@400;500;600;700;800;900&display=swap');

* { font-family: FONT !important; -webkit-font-smoothing: antialiased; }

.stApp { background: BG !important; color: TEXT !important; }

.main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
    direction: RTL;
}

#MainMenu, footer, header { visibility: hidden; }

/* ═══════════ NAVBAR ═══════════ */
.navbar {
    background: BG_CARD;
    border-bottom: 1px solid BORDER;
    padding: 14px 40px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 999;
}
.navbar-logo {
    font-size: 22px;
    font-weight: 800;
    color: TEXT;
    letter-spacing: -0.4px;
}
.navbar-logo span { color: PRIMARY; }

/* ═══════════ HERO ═══════════ */
.hero {
    background: linear-gradient(120deg, HERO_FROM 0%, HERO_TO 100%);
    padding: 88px 40px 96px;
    color: white;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: "";
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse at 30% 30%, rgba(255,255,255,0.06) 0%, transparent 60%);
    pointer-events: none;
}
.hero-eyebrow {
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    opacity: 0.7;
    margin-bottom: 20px;
    color: white;
    position: relative;
    z-index: 1;
}
.hero-title {
    font-size: 56px;
    font-weight: 800;
    margin: 0 0 20px 0;
    line-height: 1.08;
    letter-spacing: -1.5px;
    color: white;
    position: relative;
    z-index: 1;
}
.hero-subtitle {
    font-size: 18px;
    opacity: 0.82;
    max-width: 640px;
    margin: 0 auto 40px;
    font-weight: 400;
    line-height: 1.6;
    color: white;
    position: relative;
    z-index: 1;
}
.hero-stats {
    display: flex;
    justify-content: center;
    gap: 56px;
    flex-wrap: wrap;
    position: relative;
    z-index: 1;
    margin-top: 8px;
}
.hero-stat {
    text-align: center;
}
.hero-stat-value {
    font-size: 32px;
    font-weight: 800;
    color: white;
    letter-spacing: -0.8px;
}
.hero-stat-label {
    font-size: 12px;
    font-weight: 500;
    opacity: 0.65;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-top: 6px;
    color: white;
}

/* ═══════════ CONTENT ═══════════ */
.content-area {
    max-width: 1280px;
    margin: 0 auto;
    padding: 64px 40px;
}

/* ═══════════ SECTION ═══════════ */
.section-head {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    margin-bottom: 28px;
    padding-bottom: 16px;
    border-bottom: 1px solid BORDER_SOFT;
}
.section-title {
    font-size: 26px;
    font-weight: 800;
    color: TEXT;
    margin: 0;
    letter-spacing: -0.6px;
}
.section-link {
    font-size: 13px;
    font-weight: 700;
    color: PRIMARY;
    text-decoration: none;
    letter-spacing: 0.3px;
    cursor: pointer;
}
.section-link:hover { color: PRIMARY_DARK; }

/* ═══════════ PROPERTY TYPE CARD ═══════════ */
.ptype-card {
    background: BG_CARD;
    border: 1px solid BORDER;
    border-radius: 12px;
    padding: 28px 16px;
    text-align: center;
    transition: all 0.25s ease;
    cursor: pointer;
    height: 100%;
}
.ptype-card:hover {
    border-color: PRIMARY;
    transform: translateY(-3px);
    box-shadow: SHADOW_MD;
}
.ptype-icon {
    font-size: 28px;
    font-weight: 900;
    color: PRIMARY;
    margin-bottom: 14px;
    letter-spacing: -1px;
}
.ptype-name {
    font-size: 15px;
    font-weight: 700;
    color: TEXT;
    margin-bottom: 6px;
}
.ptype-count {
    font-size: 12px;
    color: TEXT_MUTED;
    font-weight: 500;
}

/* ═══════════ AREA CIRCLE CARD ═══════════ */
.area-card {
    background: BG_CARD;
    border: 1px solid BORDER;
    border-radius: 16px;
    padding: 24px 14px;
    text-align: center;
    transition: all 0.25s ease;
    cursor: pointer;
}
.area-card:hover {
    border-color: PRIMARY;
    transform: translateY(-3px);
    box-shadow: SHADOW_MD;
}
.area-img {
    width: 92px;
    height: 92px;
    border-radius: 50%;
    overflow: hidden;
    margin: 0 auto 16px;
    border: 2px solid BORDER;
}
.area-img img { width: 100%; height: 100%; object-fit: cover; }
.area-name {
    font-size: 14px;
    font-weight: 700;
    color: TEXT;
    margin-bottom: 4px;
}
.area-count {
    font-size: 12px;
    color: TEXT_MUTED;
    font-weight: 500;
}

/* ═══════════ PROPERTY CARD ═══════════ */
.prop-card {
    background: BG_CARD;
    border: 1px solid BORDER;
    border-radius: 14px;
    overflow: hidden;
    transition: all 0.3s ease;
    margin-bottom: 20px;
    box-shadow: SHADOW_SM;
}
.prop-card:hover {
    transform: translateY(-4px);
    box-shadow: SHADOW_LG;
    border-color: PRIMARY_LIGHT;
}
.prop-img-wrap {
    position: relative;
    height: 260px;
    overflow: hidden;
    background: BG_SOFT;
}
.prop-img-wrap img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.6s ease;
}
.prop-card:hover .prop-img-wrap img { transform: scale(1.06); }
.prop-badge {
    position: absolute;
    top: 14px;
    left: 14px;
    background: rgba(255,255,255,0.96);
    color: TEXT;
    padding: 6px 14px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    backdrop-filter: blur(8px);
}
.prop-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 20px;
    background: linear-gradient(to top, rgba(10,15,28,0.88) 0%, rgba(10,15,28,0.35) 60%, transparent 100%);
    color: white;
}
.prop-title {
    font-size: 16px;
    font-weight: 700;
    color: white;
    margin-bottom: 6px;
    line-height: 1.35;
}
.prop-location {
    font-size: 12px;
    opacity: 0.85;
    color: white;
    margin-bottom: 10px;
    font-weight: 500;
}
.prop-price {
    font-size: 20px;
    font-weight: 800;
    color: white;
    letter-spacing: -0.4px;
}
.prop-meta {
    font-size: 11px;
    opacity: 0.85;
    color: white;
    margin-top: 6px;
    font-weight: 500;
}

/* ═══════════ RECOMMENDATION CARD ═══════════ */
.rec-card {
    background: BG_CARD;
    border-radius: 14px;
    overflow: hidden;
    box-shadow: SHADOW_MD;
    transition: all 0.3s ease;
    margin-bottom: 20px;
    border: 1px solid BORDER;
}
.rec-card:hover { transform: translateY(-4px); box-shadow: SHADOW_LG; }
.rec-img-wrap {
    position: relative;
    height: 260px;
    overflow: hidden;
}
.rec-img-wrap img { width: 100%; height: 100%; object-fit: cover; }
.rec-delivery {
    position: absolute;
    bottom: 14px;
    left: 14px;
    background: rgba(0,0,0,0.72);
    color: white;
    padding: 8px 14px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    backdrop-filter: blur(8px);
}
.rec-body { padding: 16px 20px; }
.rec-title { font-size: 15px; font-weight: 700; color: TEXT; }

/* ═══════════ STAT CARD ═══════════ */
.stat-card {
    background: BG_CARD;
    border: 1px solid BORDER;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    transition: all 0.25s ease;
}
.stat-card:hover { border-color: PRIMARY; box-shadow: SHADOW_MD; }
.stat-card-value {
    font-size: 24px;
    font-weight: 800;
    color: PRIMARY;
    letter-spacing: -0.5px;
    margin-bottom: 4px;
}
.stat-card-label {
    font-size: 11px;
    color: TEXT_MUTED;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* ═══════════ BUTTONS ═══════════ */
.stButton > button {
    background: PRIMARY !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 12px 24px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    letter-spacing: 0.2px !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: PRIMARY_DARK !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="secondary"] {
    background: BG_CARD !important;
    color: TEXT !important;
    border: 1.5px solid BORDER !important;
    border-radius: 8px !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: PRIMARY !important;
    color: PRIMARY !important;
    background: PRIMARY_SOFT !important;
}

/* ═══════════ TABS ═══════════ */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px !important;
    background: transparent !important;
    padding: 0 !important;
    border-radius: 0 !important;
    border-bottom: 1px solid BORDER !important;
    margin-bottom: 28px !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 0 !important;
    padding: 14px 20px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    color: TEXT_MUTED !important;
    background: transparent !important;
    border-bottom: 2px solid transparent !important;
}
.stTabs [data-baseweb="tab"]:hover { color: TEXT !important; }
.stTabs [aria-selected="true"] {
    color: PRIMARY !important;
    border-bottom: 2px solid PRIMARY !important;
    background: transparent !important;
    box-shadow: none !important;
}

/* ═══════════ INPUTS ═══════════ */
.stSelectbox > div > div,
.stNumberInput > div > div > input,
.stTextInput > div > div > input,
.stTextArea textarea {
    background: BG_CARD !important;
    color: TEXT !important;
    border: 1.5px solid BORDER !important;
    border-radius: 8px !important;
    padding: 11px 14px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
}
.stSelectbox > div > div:focus-within,
.stNumberInput > div > div > input:focus,
.stTextInput > div > div > input:focus {
    border-color: PRIMARY !important;
    box-shadow: 0 0 0 3px PRIMARY_SOFT !important;
}
.stSelectbox label, .stNumberInput label, .stSlider label, .stTextInput label {
    color: TEXT_SOFT !important;
    font-weight: 600 !important;
    font-size: 12px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    margin-bottom: 6px !important;
}

/* ═══════════ METRICS ═══════════ */
[data-testid="stMetricValue"] {
    color: TEXT !important;
    font-weight: 800 !important;
    font-size: 26px !important;
    letter-spacing: -0.4px !important;
}
[data-testid="stMetricLabel"] {
    color: TEXT_MUTED !important;
    font-weight: 600 !important;
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
}

/* ═══════════ SLIDER ═══════════ */
.stSlider > div > div > div > div { background: PRIMARY !important; }

/* ═══════════ SIDEBAR ═══════════ */
section[data-testid="stSidebar"] {
    background: BG_SOFT !important;
    border-right: 1px solid BORDER !important;
}
section[data-testid="stSidebar"] * { color: TEXT !important; }

/* ═══════════ PRICE CARD ═══════════ */
.price-card {
    background: linear-gradient(135deg, HERO_FROM 0%, HERO_TO 100%);
    border-radius: 20px;
    padding: 48px 40px;
    color: white;
    text-align: center;
    box-shadow: 0 20px 60px rgba(0,102,255,0.25);
    position: relative;
    overflow: hidden;
}
.price-card::before {
    content: "";
    position: absolute;
    top: -50%;
    right: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle at 70% 30%, rgba(255,255,255,0.08) 0%, transparent 60%);
}
.price-label {
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 3px;
    opacity: 0.75;
    color: white;
    position: relative;
    z-index: 1;
}
.price-value {
    font-size: 68px;
    font-weight: 800;
    margin: 20px 0 8px;
    line-height: 1;
    color: white;
    letter-spacing: -2.5px;
    position: relative;
    z-index: 1;
}
.price-currency {
    font-size: 18px;
    font-weight: 600;
    opacity: 0.85;
    color: white;
    position: relative;
    z-index: 1;
    letter-spacing: 1px;
}
.price-per-m2 {
    display: inline-block;
    background: rgba(255,255,255,0.14);
    border: 1px solid rgba(255,255,255,0.2);
    padding: 12px 24px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 14px;
    margin-top: 24px;
    color: white;
    position: relative;
    z-index: 1;
    letter-spacing: 0.3px;
}

/* ═══════════ FOOTER ═══════════ */
.footer {
    background: BG_SOFT;
    border-top: 1px solid BORDER;
    padding: 48px 40px 32px;
    text-align: center;
    color: TEXT_MUTED;
    margin-top: 64px;
    font-size: 13px;
}
.footer-brand {
    font-size: 18px;
    font-weight: 800;
    color: TEXT;
    margin-bottom: 10px;
    letter-spacing: -0.3px;
}

/* ═══════════ EMPTY STATE ═══════════ */
.empty-state {
    text-align: center;
    padding: 72px 32px;
    background: BG_SOFT;
    border-radius: 16px;
    border: 1px dashed BORDER;
}
.empty-title {
    font-size: 20px;
    font-weight: 700;
    color: TEXT;
    margin-bottom: 8px;
}
.empty-desc { font-size: 14px; color: TEXT_MUTED; }

/* ═══════════ RESPONSIVE ═══════════ */
@media (max-width: 768px) {
    .hero { padding: 56px 20px 64px; }
    .hero-title { font-size: 32px; letter-spacing: -0.8px; }
    .hero-subtitle { font-size: 15px; }
    .hero-stats { gap: 24px; }
    .hero-stat-value { font-size: 22px; }
    .content-area { padding: 32px 20px; }
    .section-title { font-size: 20px; }
    .price-value { font-size: 42px; letter-spacing: -1.5px; }
    .price-card { padding: 32px 24px; }
    .navbar { padding: 12px 20px; }
    .prop-img-wrap { height: 200px; }
    .rec-img-wrap { height: 200px; }
}

/* COMPOUND CARD */
.comp-card {
    background: BG_CARD;
    border: 1px solid BORDER;
    border-radius: 12px;
    padding: 24px 20px;
    transition: all 0.25s ease;
    cursor: pointer;
    height: 100%;
}
.comp-card:hover {
    border-color: PRIMARY;
    transform: translateY(-3px);
    box-shadow: SHADOW_MD;
}
.comp-title {
    font-size: 15px;
    font-weight: 700;
    color: TEXT;
    margin-bottom: 10px;
    line-height: 1.4;
}
.comp-units {
    font-size: 12px;
    color: TEXT_MUTED;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 8px;
}
.comp-price {
    font-size: 16px;
    font-weight: 800;
    color: PRIMARY;
    letter-spacing: -0.3px;
}

/* FORM SECTION HEADER */
.form-section {
    font-size: 12px;
    font-weight: 700;
    color: TEXT_MUTED;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 20px 0 12px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid BORDER_SOFT;
}

/* FAVORITE ITEM */
.fav-item {
    background: BG_CARD;
    border: 1px solid BORDER;
    border-radius: 10px;
    padding: 18px 20px;
    margin-bottom: 12px;
}
.fav-title {
    font-size: 15px;
    font-weight: 700;
    color: TEXT;
    margin-bottom: 6px;
}
.fav-detail {
    font-size: 13px;
    color: TEXT_MUTED;
    margin-bottom: 8px;
}
.fav-price {
    font-size: 18px;
    font-weight: 800;
    color: PRIMARY;
    letter-spacing: -0.3px;
}


/* PROPERTY TYPE CARD WITH IMAGE */
.ptype-card-img {
    background: BG_CARD;
    border: 1px solid BORDER;
    border-radius: 12px;
    overflow: hidden;
    transition: all 0.25s ease;
    cursor: pointer;
    height: 100%;
}
.ptype-card-img:hover {
    border-color: PRIMARY;
    transform: translateY(-3px);
    box-shadow: SHADOW_MD;
}
.ptype-card-img .ptype-thumb {
    width: 100%;
    height: 110px;
    object-fit: cover;
    display: block;
}
.ptype-card-img .ptype-info {
    padding: 12px 10px;
    text-align: center;
}
.ptype-card-img .ptype-name {
    font-size: 13px;
    font-weight: 700;
    color: TEXT;
    margin-bottom: 3px;
}
.ptype-card-img .ptype-count {
    font-size: 11px;
    color: TEXT_MUTED;
    font-weight: 500;
}

/* AREA CARD WITH IMAGE */
.area-card-img {
    background: BG_CARD;
    border: 1px solid BORDER;
    border-radius: 14px;
    overflow: hidden;
    transition: all 0.25s ease;
    cursor: pointer;
    height: 100%;
}
.area-card-img:hover {
    border-color: PRIMARY;
    transform: translateY(-3px);
    box-shadow: SHADOW_MD;
}
.area-card-img .area-thumb {
    width: 100%;
    height: 130px;
    object-fit: cover;
    display: block;
}
.area-card-img .area-info {
    padding: 12px 10px;
    text-align: center;
}
.area-card-img .area-name {
    font-size: 13px;
    font-weight: 700;
    color: TEXT;
    margin-bottom: 3px;
}
.area-card-img .area-count {
    font-size: 11px;
    color: TEXT_MUTED;
    font-weight: 500;
}

/* COMPOUND CARD WITH IMAGE */
.comp-card-img {
    background: BG_CARD;
    border: 1px solid BORDER;
    border-radius: 14px;
    overflow: hidden;
    transition: all 0.25s ease;
    cursor: pointer;
    height: 100%;
    margin-bottom: 16px;
}
.comp-card-img:hover {
    border-color: PRIMARY;
    transform: translateY(-3px);
    box-shadow: SHADOW_MD;
}
.comp-card-img .comp-thumb {
    width: 100%;
    height: 200px;
    object-fit: cover;
    display: block;
}
.comp-card-img .comp-info {
    padding: 16px 18px;
}
.comp-card-img .comp-title {
    font-size: 14px;
    font-weight: 700;
    color: TEXT;
    margin-bottom: 6px;
    line-height: 1.4;
}
.comp-card-img .comp-units {
    font-size: 11px;
    color: TEXT_MUTED;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-bottom: 8px;
}
.comp-card-img .comp-price {
    font-size: 15px;
    font-weight: 800;
    color: PRIMARY;
    letter-spacing: -0.3px;
}

/* FEATURE PILL BUTTONS - FULL WIDTH TEXT */
.stButton > button[kind="secondary"],
.stButton > button[kind="primary"] {
    min-height: 42px !important;
    white-space: normal !important;
    font-size: 13px !important;
    padding: 8px 12px !important;
    line-height: 1.3 !important;
}


/* FIX: Full text on pills - no truncation */
.stButton > button {
    min-height: 44px !important;
    height: auto !important;
    white-space: normal !important;
    word-break: keep-all !important;
    overflow-wrap: break-word !important;
    text-overflow: clip !important;
    font-size: 13px !important;
    padding: 10px 14px !important;
    line-height: 1.35 !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
}

/* Remove ellipsis */
.stButton > button > div,
.stButton > button > div > p,
.stButton > button p {
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
    word-break: keep-all !important;
    margin: 0 !important;
}


/* FIX: Prevent word breaking in feature pills */
.stButton > button {
    word-break: keep-all !important;
    overflow-wrap: normal !important;
    hyphens: none !important;
    min-height: 46px !important;
    height: auto !important;
    white-space: nowrap !important;
    padding: 12px 16px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    letter-spacing: 0 !important;
    line-height: 1.2 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
}

.stButton > button > div,
.stButton > button > div > p,
.stButton > button p {
    word-break: keep-all !important;
    overflow-wrap: normal !important;
    white-space: nowrap !important;
    text-overflow: clip !important;
    overflow: visible !important;
    margin: 0 !important;
    letter-spacing: 0 !important;
}


/* PRICE HISTORY CARDS */
.price-history-card {
    background: BG_CARD;
    border: 1px solid BORDER;
    border-radius: 14px;
    padding: 20px 18px;
    text-align: right;
    transition: all 0.25s ease;
    height: 100%;
    min-height: 130px;
}
.price-history-card:hover {
    transform: translateY(-3px);
    box-shadow: SHADOW_MD;
}
.price-history-label {
    font-size: 11px;
    font-weight: 700;
    color: TEXT_MUTED;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 10px;
}
.price-history-value {
    font-size: 26px;
    font-weight: 800;
    color: TEXT;
    letter-spacing: -0.5px;
    line-height: 1.1;
    margin-bottom: 2px;
}
.price-history-unit {
    font-size: 12px;
    color: TEXT_MUTED;
    font-weight: 600;
    margin-bottom: 8px;
}
.price-card-badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
    margin-top: 6px;
}
.badge-gray {
    background: BG_SOFT;
    color: TEXT_MUTED;
}
.badge-green {
    background: SUCCESS_SOFT;
    color: SUCCESS;
}
.badge-blue {
    background: PRIMARY_SOFT;
    color: PRIMARY;
}

/* ROI CARDS */
.roi-card {
    background: BG_CARD;
    border: 1px solid BORDER;
    border-radius: 14px;
    padding: 22px 20px;
    text-align: right;
    transition: all 0.25s ease;
    height: 100%;
    margin-bottom: 16px;
}
.roi-card:hover {
    border-color: PRIMARY;
    transform: translateY(-2px);
    box-shadow: SHADOW_MD;
}
.roi-label {
    font-size: 11px;
    font-weight: 700;
    color: TEXT_MUTED;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 10px;
}
.roi-value {
    font-size: 24px;
    font-weight: 800;
    color: TEXT;
    letter-spacing: -0.5px;
    line-height: 1.2;
}
.roi-unit {
    font-size: 13px;
    font-weight: 600;
    color: TEXT_MUTED;
}


/* MOBILE OPTIMIZATION */
@media (max-width: 768px) {
    .price-history-value {
        font-size: 20px !important;
    }
    .price-history-label {
        font-size: 10px !important;
    }
    .price-history-card {
        padding: 14px 12px !important;
        min-height: 110px !important;
    }
    .roi-value {
        font-size: 18px !important;
    }
    .roi-label {
        font-size: 10px !important;
    }
    .roi-card {
        padding: 16px 12px !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 20px !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 10px !important;
    }
    .stButton > button {
        font-size: 12px !important;
        padding: 10px 10px !important;
        min-height: 42px !important;
    }
}

/* Feature pills - wider on desktop */
.stButton > button {
    min-width: 90px !important;
}

</style>
"""


def get_css(dark=False, lang="en"):
    c = get_theme(dark)
    font = "'Cairo','Tajawal',sans-serif" if lang == "ar" else "'Inter',sans-serif"
    rtl = "rtl" if lang == "ar" else "ltr"

    css = CSS_TEMPLATE
    repls = {
        "FONT": font, "RTL": rtl,
        "BG_SOFT": c["bg_soft"], "BG_CARD": c["bg_card"], "BG": c["bg"],
        "TEXT_MUTED": c["text_muted"], "TEXT_SOFT": c["text_soft"], "TEXT": c["text"],
        "BORDER_SOFT": c["border_soft"], "BORDER": c["border"],
        "PRIMARY_SOFT": c["primary_soft"], "PRIMARY_DARK": c["primary_dark"],
        "PRIMARY_LIGHT": c["primary_light"], "PRIMARY": c["primary"],
        "ACCENT_SOFT": c["accent_soft"], "ACCENT": c["accent"],
        "SUCCESS_SOFT": c["success_soft"], "SUCCESS": c["success"],
        "WARNING_SOFT": c["warning_soft"], "WARNING": c["warning"],
        "DANGER_SOFT": c["danger_soft"], "DANGER": c["danger"],
        "SHADOW_LG": c["shadow_lg"], "SHADOW_MD": c["shadow_md"], "SHADOW_SM": c["shadow_sm"],
        "HERO_FROM": c["hero_from"], "HERO_TO": c["hero_to"],
    }
    for k, v in repls.items():
        css = css.replace(k, v)
    return css
