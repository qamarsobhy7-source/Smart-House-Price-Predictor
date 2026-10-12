"""
Modern Theme v3 — Beautiful UI/UX
Property Finder + Bayut + Zillow + Aqarmap + Nawy inspired
"""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
TRANS_DIR = BASE / "translations"

# ═══════════════════════════════════════════════════════
# COLORS
# ═══════════════════════════════════════════════════════
LIGHT = {
    "primary": "#6366F1",
    "primary_dark": "#4F46E5",
    "primary_light": "#A5B4FC",
    "primary_soft": "#EEF2FF",
    "accent": "#8B5CF6",
    "success": "#10B981",
    "success_soft": "#D1FAE5",
    "warning": "#F59E0B",
    "warning_soft": "#FEF3C7",
    "danger": "#EF4444",
    "danger_soft": "#FEE2E2",
    "text": "#111827",
    "text_soft": "#374151",
    "text_muted": "#6B7280",
    "bg": "#FFFFFF",
    "bg_soft": "#F9FAFB",
    "bg_card": "#FFFFFF",
    "border": "#E5E7EB",
    "border_soft": "#F3F4F6",
    "shadow_sm": "0 1px 3px rgba(0,0,0,0.05)",
    "shadow_md": "0 4px 14px rgba(0,0,0,0.08)",
    "shadow_lg": "0 12px 40px rgba(0,0,0,0.12)",
    "hero_from": "#6366F1",
    "hero_via": "#8B5CF6",
    "hero_to": "#EC4899",
}

DARK = {
    "primary": "#818CF8",
    "primary_dark": "#6366F1",
    "primary_light": "#A5B4FC",
    "primary_soft": "#1E1B4B",
    "accent": "#A78BFA",
    "success": "#34D399",
    "success_soft": "#064E3B",
    "warning": "#FBBF24",
    "warning_soft": "#78350F",
    "danger": "#F87171",
    "danger_soft": "#7F1D1D",
    "text": "#F9FAFB",
    "text_soft": "#E5E7EB",
    "text_muted": "#9CA3AF",
    "bg": "#0F172A",
    "bg_soft": "#1E293B",
    "bg_card": "#1E293B",
    "border": "#334155",
    "border_soft": "#1E293B",
    "shadow_sm": "0 1px 3px rgba(0,0,0,0.3)",
    "shadow_md": "0 4px 14px rgba(0,0,0,0.4)",
    "shadow_lg": "0 12px 40px rgba(0,0,0,0.5)",
    "hero_from": "#1E1B4B",
    "hero_via": "#4C1D95",
    "hero_to": "#831843",
}


def get_theme(dark=False):
    return DARK if dark else LIGHT


# ═══════════════════════════════════════════════════════
# TRANSLATIONS
# ═══════════════════════════════════════════════════════
_TRANS_CACHE = {}

def load_translations(lang="ar"):
    if lang in _TRANS_CACHE:
        return _TRANS_CACHE[lang]
    path = TRANS_DIR / f"{lang}.json"
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    _TRANS_CACHE[lang] = data
    return data


def t(section, key, lang="ar"):
    trans = load_translations(lang)
    return trans.get(section, {}).get(key, f"{section}.{key}")


# ═══════════════════════════════════════════════════════
# CSS TEMPLATE
# ═══════════════════════════════════════════════════════
CSS_TEMPLATE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Cairo:wght@400;500;600;700;800;900&display=swap');

* { font-family: FONT !important; }

/* APP */
.stApp {
    background: BG !important;
    color: TEXT !important;
}

.main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
    direction: RTL;
}

/* Hide Streamlit default elements */
#MainMenu, footer, header { visibility: hidden; }

/* NAVBAR */
.navbar {
    background: BG_CARD;
    border-bottom: 1px solid BORDER;
    padding: 16px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 999;
    box-shadow: SHADOW_SM;
}

.navbar-logo {
    font-size: 24px;
    font-weight: 900;
    color: PRIMARY;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* HERO */
.hero {
    background: linear-gradient(135deg, HERO_FROM 0%, HERO_VIA 50%, HERO_TO 100%);
    padding: 64px 32px;
    color: white;
    text-align: center;
    position: relative;
    overflow: hidden;
}

.hero::before {
    content: "";
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
}

.hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.2);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.3);
    padding: 8px 20px;
    border-radius: 100px;
    font-size: 13px;
    font-weight: 700;
    margin-bottom: 20px;
    color: white;
    position: relative;
    z-index: 1;
}

.hero-title {
    font-size: 48px;
    font-weight: 900;
    margin: 0 0 16px 0;
    line-height: 1.15;
    color: white;
    position: relative;
    z-index: 1;
}

.hero-subtitle {
    font-size: 18px;
    opacity: 0.95;
    max-width: 700px;
    margin: 0 auto 32px;
    font-weight: 500;
    color: white;
    position: relative;
    z-index: 1;
}

.stats-bar {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    max-width: 900px;
    margin: 0 auto;
    position: relative;
    z-index: 1;
}

.stat-item {
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255,255,255,0.25);
    border-radius: 16px;
    padding: 20px 12px;
    text-align: center;
    transition: all 0.3s;
}

.stat-item:hover {
    background: rgba(255,255,255,0.25);
    transform: translateY(-4px);
}

.stat-value {
    font-size: 28px;
    font-weight: 900;
    color: white;
    line-height: 1.1;
}

.stat-label {
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    opacity: 0.9;
    margin-top: 6px;
    color: white;
}

/* CONTENT AREA */
.content-area {
    max-width: 1300px;
    margin: 0 auto;
    padding: 32px;
}

/* SECTION */
.section {
    margin: 48px 0;
}

.section-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 24px;
}

.section-icon {
    width: 52px;
    height: 52px;
    border-radius: 14px;
    background: linear-gradient(135deg, PRIMARY 0%, PRIMARY_DARK 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    color: white;
    box-shadow: 0 8px 20px rgba(99,102,241,0.3);
}

.section-title {
    font-size: 28px;
    font-weight: 900;
    color: TEXT;
    margin: 0;
    line-height: 1.2;
}

.section-subtitle {
    font-size: 14px;
    color: TEXT_MUTED;
    margin-top: 4px;
}

/* CARDS */
.card {
    background: BG_CARD;
    border: 1px solid BORDER;
    border-radius: 18px;
    padding: 24px;
    box-shadow: SHADOW_SM;
    transition: all 0.3s;
    height: 100%;
}

.card:hover {
    border-color: PRIMARY;
    transform: translateY(-4px);
    box-shadow: SHADOW_MD;
}

.card-icon {
    font-size: 36px;
    margin-bottom: 12px;
}

.card-title {
    font-size: 12px;
    font-weight: 700;
    color: TEXT_MUTED;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin: 0 0 8px 0;
}

.card-value {
    font-size: 32px;
    font-weight: 900;
    color: PRIMARY;
    margin: 0;
    line-height: 1.1;
}

.card-subtitle {
    font-size: 13px;
    color: TEXT_MUTED;
    margin-top: 6px;
}

.card-desc {
    font-size: 14px;
    color: TEXT_SOFT;
    margin-top: 12px;
    line-height: 1.5;
}

/* PRICE CARD */
.price-card {
    background: linear-gradient(135deg, PRIMARY 0%, ACCENT 100%);
    border-radius: 24px;
    padding: 40px 32px;
    color: white;
    text-align: center;
    box-shadow: 0 24px 60px rgba(99,102,241,0.35);
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
    background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%);
}

.price-label {
    font-size: 14px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    opacity: 0.9;
    color: white;
    position: relative;
    z-index: 1;
}

.price-value {
    font-size: 64px;
    font-weight: 900;
    margin: 20px 0 8px;
    line-height: 1;
    color: white;
    position: relative;
    z-index: 1;
}

.price-currency {
    font-size: 20px;
    font-weight: 600;
    opacity: 0.9;
    color: white;
    position: relative;
    z-index: 1;
}

.price-per-m2 {
    display: inline-block;
    background: rgba(255,255,255,0.2);
    backdrop-filter: blur(10px);
    padding: 12px 24px;
    border-radius: 100px;
    font-weight: 700;
    font-size: 15px;
    margin-top: 20px;
    color: white;
    position: relative;
    z-index: 1;
}

/* PROPERTY CARD */
.property-card {
    background: BG_CARD;
    border: 1px solid BORDER;
    border-radius: 16px;
    overflow: hidden;
    transition: all 0.3s;
    margin-bottom: 16px;
}

.property-card:hover {
    transform: translateY(-4px);
    box-shadow: SHADOW_MD;
    border-color: PRIMARY;
}

.property-card-body {
    padding: 16px;
}

.property-price {
    font-size: 20px;
    font-weight: 900;
    color: PRIMARY;
    margin: 0 0 4px 0;
}

.property-title {
    font-size: 14px;
    font-weight: 700;
    color: TEXT;
    margin: 0 0 8px 0;
}

.property-meta {
    font-size: 12px;
    color: TEXT_MUTED;
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
}

/* BUTTONS */
.stButton > button {
    background: linear-gradient(135deg, PRIMARY 0%, PRIMARY_DARK 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    letter-spacing: 0.3px !important;
    box-shadow: 0 4px 14px rgba(99,102,241,0.3) !important;
    transition: all 0.3s !important;
    width: 100% !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(99,102,241,0.4) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
}

/* TABS */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px !important;
    background: BG_SOFT !important;
    padding: 8px !important;
    border-radius: 16px !important;
    border: 1px solid BORDER !important;
    margin-bottom: 24px !important;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 12px !important;
    padding: 12px 20px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    color: TEXT_MUTED !important;
    background: transparent !important;
    transition: all 0.3s !important;
}

.stTabs [data-baseweb="tab"]:hover {
    color: PRIMARY !important;
}

.stTabs [aria-selected="true"] {
    background: BG_CARD !important;
    color: PRIMARY !important;
    box-shadow: SHADOW_SM !important;
}

/* INPUTS */
.stSelectbox > div > div,
.stNumberInput > div > div > input,
.stTextInput > div > div > input,
.stTextArea textarea {
    background: BG_SOFT !important;
    color: TEXT !important;
    border: 1.5px solid BORDER !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    transition: all 0.3s !important;
}

.stSelectbox > div > div:focus-within,
.stNumberInput > div > div > input:focus,
.stTextInput > div > div > input:focus {
    border-color: PRIMARY !important;
    box-shadow: 0 0 0 3px PRIMARY_SOFT !important;
}

.stSelectbox label, .stNumberInput label, .stSlider label, .stTextInput label {
    color: TEXT !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    margin-bottom: 6px !important;
}

/* METRICS */
[data-testid="stMetricValue"] {
    color: PRIMARY !important;
    font-weight: 900 !important;
    font-size: 28px !important;
}

[data-testid="stMetricLabel"] {
    color: TEXT_MUTED !important;
    font-weight: 700 !important;
    font-size: 12px !important;
}

/* SLIDER */
.stSlider > div > div > div > div {
    background: PRIMARY !important;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: BG_SOFT !important;
    border-right: 1px solid BORDER !important;
}

/* FOOTER */
.footer {
    background: BG_SOFT;
    border-top: 1px solid BORDER;
    padding: 48px 32px 32px;
    text-align: center;
    color: TEXT_MUTED;
    margin-top: 64px;
}

.footer-title {
    font-size: 24px;
    font-weight: 900;
    color: PRIMARY;
    margin: 0 0 12px 0;
}

.footer-text {
    font-size: 14px;
    margin: 8px 0;
}

/* EMPTY STATE */
.empty-state {
    text-align: center;
    padding: 80px 32px;
    background: BG_SOFT;
    border-radius: 24px;
    border: 2px dashed BORDER;
}

.empty-icon {
    font-size: 80px;
    margin-bottom: 20px;
    opacity: 0.5;
}

.empty-title {
    font-size: 24px;
    font-weight: 900;
    color: TEXT;
    margin-bottom: 8px;
}

.empty-desc {
    font-size: 15px;
    color: TEXT_MUTED;
    max-width: 500px;
    margin: 0 auto;
}

/* BADGE */
.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 100px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.badge-primary {
    background: PRIMARY_SOFT;
    color: PRIMARY;
}

.badge-success {
    background: SUCCESS_SOFT;
    color: SUCCESS;
}

.badge-warning {
    background: WARNING_SOFT;
    color: WARNING;
}

/* RESPONSIVE */
@media (max-width: 768px) {
    .hero { padding: 40px 20px; }
    .hero-title { font-size: 32px; }
    .hero-subtitle { font-size: 15px; }
    .stats-bar { grid-template-columns: repeat(2, 1fr); }
    .stat-value { font-size: 22px; }
    .price-value { font-size: 44px; }
    .section-title { font-size: 22px; }
    .section-icon { width: 44px; height: 44px; font-size: 20px; }
    .content-area { padding: 16px; }
    .card-value { font-size: 24px; }
}


/* ═══════════════════════════════════════════════════════ */
/* NEW COMPONENTS - Nawy + Aqarmap                          */
/* ═══════════════════════════════════════════════════════ */

/* PROPERTY CARD WITH OVERLAY */
.property-card-nawy {
    position: relative;
    border-radius: 18px;
    overflow: hidden;
    box-shadow: SHADOW_MD;
    transition: all 0.35s;
    margin-bottom: 16px;
    cursor: pointer;
}
.property-card-nawy:hover {
    transform: translateY(-4px);
    box-shadow: SHADOW_LG;
}
.property-card-img-wrap {
    position: relative;
    height: 320px;
    overflow: hidden;
}
.property-card-img-wrap img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.5s;
}
.property-card-nawy:hover img {
    transform: scale(1.08);
}
.property-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 20px;
    background: linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.4) 60%, transparent 100%);
    color: white;
}
.property-overlay-title {
    font-size: 18px;
    font-weight: 900;
    margin-bottom: 4px;
    text-shadow: 0 2px 8px rgba(0,0,0,0.5);
}
.property-overlay-location {
    font-size: 13px;
    opacity: 0.9;
    margin-bottom: 8px;
}
.property-overlay-price {
    font-size: 22px;
    font-weight: 900;
    color: #FFB800;
    text-shadow: 0 2px 8px rgba(0,0,0,0.5);
    margin-bottom: 4px;
}
.property-overlay-meta {
    font-size: 12px;
    opacity: 0.95;
}
.card-badge {
    position: absolute;
    top: 12px;
    right: 12px;
    background: rgba(255,255,255,0.95);
    color: PRIMARY;
    padding: 6px 14px;
    border-radius: 100px;
    font-size: 12px;
    font-weight: 800;
    z-index: 2;
}
.new-badge {
    position: absolute;
    top: 12px;
    right: 12px;
    background: white;
    color: TEXT;
    padding: 6px 14px;
    border-radius: 100px;
    font-size: 12px;
    font-weight: 700;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    z-index: 2;
}

/* PILLS LABEL */
.pills-label {
    font-size: 14px;
    font-weight: 800;
    color: TEXT;
    margin-bottom: 10px;
    margin-top: 8px;
}

/* PILLS BUTTONS - secondary becomes pill style */
.stButton > button[kind="secondary"] {
    background: BG_CARD !important;
    color: TEXT !important;
    border: 1.5px solid BORDER !important;
    border-radius: 100px !important;
    font-weight: 700 !important;
    padding: 10px 20px !important;
    font-size: 14px !important;
    box-shadow: none !important;
    transition: all 0.25s !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: PRIMARY !important;
    color: PRIMARY !important;
    background: PRIMARY_SOFT !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 12px rgba(0,106,255,0.15) !important;
}
.stButton > button[kind="primary"] {
    border-radius: 100px !important;
}

/* AREA CIRCLE CARD */
.area-circle-card {
    background: BG_CARD;
    border: 1px solid BORDER;
    border-radius: 20px;
    padding: 20px 12px;
    text-align: center;
    transition: all 0.3s;
    cursor: pointer;
    box-shadow: SHADOW_SM;
}
.area-circle-card:hover {
    border-color: PRIMARY;
    transform: translateY(-4px);
    box-shadow: SHADOW_MD;
}
.area-circle-img {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    overflow: hidden;
    margin: 0 auto 14px;
    border: 3px solid PRIMARY_SOFT;
}
.area-circle-img img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}
.area-circle-name {
    font-size: 15px;
    font-weight: 800;
    color: TEXT;
    margin-bottom: 4px;
}
.area-circle-count {
    font-size: 12px;
    color: TEXT_MUTED;
    font-weight: 500;
}

/* SECTION HEADER CUSTOM */
.section-header-custom {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 8px 0 12px;
}
.section-header-icon {
    font-size: 24px;
}
.section-header-title {
    font-size: 22px;
    font-weight: 900;
    color: TEXT;
    margin: 0;
    letter-spacing: -0.3px;
}

/* PROMO BANNER */
.promo-banner {
    border-radius: 20px;
    padding: 28px 32px;
    margin: 20px 0;
    position: relative;
    overflow: hidden;
    cursor: pointer;
    transition: all 0.3s;
}
.promo-banner:hover {
    transform: translateY(-3px);
    box-shadow: SHADOW_LG;
}
.promo-blue {
    background: linear-gradient(135deg, #E8F1FF 0%, #D4E5FF 100%);
}
.promo-warm {
    background: linear-gradient(135deg, #FFF4E6 0%, #FFE0B2 100%);
}
.promo-pink {
    background: linear-gradient(135deg, #FFE8EE 0%, #FFD0DD 100%);
}
.promo-title {
    font-size: 24px;
    font-weight: 900;
    color: PRIMARY;
    margin-bottom: 8px;
}
.promo-warm .promo-title { color: #E65100; }
.promo-pink .promo-title { color: #C2185B; }
.promo-subtitle {
    font-size: 15px;
    color: TEXT_SOFT;
    margin-bottom: 14px;
    font-weight: 500;
}
.promo-cta {
    font-size: 14px;
    font-weight: 800;
    color: PRIMARY;
    display: inline-block;
}
.promo-warm .promo-cta { color: #E65100; }
.promo-pink .promo-cta { color: #C2185B; }

/* RECOMMENDATION CARD */
.rec-card {
    background: BG_CARD;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: SHADOW_MD;
    transition: all 0.35s;
    margin-bottom: 16px;
}
.rec-card:hover {
    transform: translateY(-4px);
    box-shadow: SHADOW_LG;
}
.rec-img-wrap {
    position: relative;
    height: 280px;
    overflow: hidden;
}
.rec-img-wrap img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.5s;
}
.rec-card:hover img {
    transform: scale(1.06);
}
.rec-actions {
    position: absolute;
    top: 14px;
    left: 14px;
    display: flex;
    gap: 8px;
}
.rec-action-btn {
    width: 38px;
    height: 38px;
    background: rgba(255,255,255,0.92);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.2s;
}
.rec-action-btn:hover {
    background: white;
    transform: scale(1.1);
}
.rec-delivery {
    position: absolute;
    bottom: 16px;
    right: 16px;
    background: rgba(0,0,0,0.75);
    color: white;
    padding: 8px 16px;
    border-radius: 100px;
    font-size: 13px;
    font-weight: 700;
}
.rec-body {
    padding: 16px 20px;
}
.rec-title {
    font-size: 17px;
    font-weight: 800;
    color: TEXT;
}

/* STAT CARD */
.stat-card {
    background: BG_CARD;
    border: 1px solid BORDER;
    border-radius: 18px;
    padding: 22px 20px;
    text-align: center;
    box-shadow: SHADOW_SM;
    transition: all 0.3s;
}
.stat-card:hover {
    transform: translateY(-3px);
    box-shadow: SHADOW_MD;
}
.stat-card-icon {
    font-size: 32px;
    margin-bottom: 8px;
}
.stat-card-value {
    font-size: 26px;
    font-weight: 900;
    color: PRIMARY;
    letter-spacing: -0.5px;
    margin-bottom: 4px;
}
.stat-card-label {
    font-size: 12px;
    color: TEXT_MUTED;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

</style>
"""


def get_css(dark=False, lang="ar"):
    c = get_theme(dark)
    rtl = "rtl" if lang == "ar" else "ltr"
    font = "'Cairo','Tajawal',sans-serif" if lang == "ar" else "'Inter',sans-serif"
    
    css = CSS_TEMPLATE
    replacements = {
        "FONT": font,
        "RTL": rtl,
        "BG_SOFT": c["bg_soft"],
        "BG_CARD": c["bg_card"],
        "BG": c["bg"],
        "TEXT_MUTED": c["text_muted"],
        "TEXT_SOFT": c["text_soft"],
        "TEXT": c["text"],
        "BORDER_SOFT": c["border_soft"],
        "BORDER": c["border"],
        "PRIMARY_SOFT": c["primary_soft"],
        "PRIMARY_DARK": c["primary_dark"],
        "PRIMARY_LIGHT": c["primary_light"],
        "PRIMARY": c["primary"],
        "ACCENT": c["accent"],
        "SUCCESS_SOFT": c["success_soft"],
        "SUCCESS": c["success"],
        "WARNING_SOFT": c["warning_soft"],
        "WARNING": c["warning"],
        "DANGER_SOFT": c["danger_soft"],
        "DANGER": c["danger"],
        "SHADOW_LG": c["shadow_lg"],
        "SHADOW_MD": c["shadow_md"],
        "SHADOW_SM": c["shadow_sm"],
        "HERO_FROM": c["hero_from"],
        "HERO_VIA": c["hero_via"],
        "HERO_TO": c["hero_to"],
    }
    
    for key, val in replacements.items():
        css = css.replace(key, val)
    
    return css
