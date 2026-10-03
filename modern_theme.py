"""
Modern Theme v2 — Light + Dark mode with Property Finder style.
"""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
TRANS_DIR = BASE / "translations"

# COLORS
LIGHT = {
    "primary": "#6366F1",
    "primary_dark": "#4F46E5",
    "primary_light": "#A5B4FC",
    "success": "#10B981",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "text": "#1F2937",
    "text_muted": "#6B7280",
    "bg": "#FFFFFF",
    "bg_soft": "#F9FAFB",
    "bg_card": "#FFFFFF",
    "border": "#E5E7EB",
    "shadow": "rgba(0,0,0,0.04)",
    "hero_from": "#667EEA",
    "hero_via": "#764BA2",
    "hero_to": "#F093FB",
}

DARK = {
    "primary": "#818CF8",
    "primary_dark": "#6366F1",
    "primary_light": "#A5B4FC",
    "success": "#34D399",
    "warning": "#FBBF24",
    "danger": "#F87171",
    "text": "#F1F5F9",
    "text_muted": "#94A3B8",
    "bg": "#0F172A",
    "bg_soft": "#1E293B",
    "bg_card": "#1E293B",
    "border": "#334155",
    "shadow": "rgba(0,0,0,0.3)",
    "hero_from": "#1E1B4B",
    "hero_via": "#4C1D95",
    "hero_to": "#831843",
}


def get_theme(dark=False):
    return DARK if dark else LIGHT


# TRANSLATIONS
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


# CSS TEMPLATE — uses placeholders instead of f-string
CSS_TEMPLATE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Cairo:wght@400;500;600;700;800;900&display=swap');

* { font-family: FONT !important; }

.stApp {
    background: BG !important;
    color: TEXT !important;
}

.main .block-container {
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    max-width: 1200px !important;
    direction: RTL;
}

h1, h2, h3, h4, h5, h6, p, span, label, div { color: TEXT; }

.hero {
    background: linear-gradient(135deg, HERO_FROM 0%, HERO_VIA 50%, HERO_TO 100%);
    border-radius: 24px;
    padding: 48px 32px;
    color: white;
    text-align: center;
    margin-bottom: 24px;
    box-shadow: 0 20px 60px rgba(102,126,234,0.25);
}

.hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.2);
    border: 1px solid rgba(255,255,255,0.3);
    backdrop-filter: blur(10px);
    padding: 8px 18px;
    border-radius: 100px;
    font-size: 13px;
    font-weight: 700;
    margin-bottom: 16px;
    color: white;
}

.hero-title {
    font-size: 42px;
    font-weight: 900;
    margin: 0 0 12px 0;
    line-height: 1.2;
    color: white;
}

.hero-subtitle {
    font-size: 16px;
    opacity: 0.95;
    max-width: 600px;
    margin: 0 auto;
    font-weight: 500;
    color: white;
}

.stats-bar {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-top: 32px;
}

.stat-item {
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 14px;
    padding: 16px 12px;
    text-align: center;
}

.stat-value {
    font-size: 24px;
    font-weight: 900;
    line-height: 1.1;
    color: white;
}

.stat-label {
    font-size: 11px;
    opacity: 0.85;
    font-weight: 600;
    text-transform: uppercase;
    margin-top: 4px;
    color: white;
}

.card {
    background: BG_CARD;
    border: 1px solid BORDER;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 2px 8px SHADOW;
    transition: all 0.3s;
}

.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px SHADOW;
}

.card-title {
    font-size: 14px;
    font-weight: 700;
    color: TEXT_MUTED;
    text-transform: uppercase;
    margin: 0 0 8px 0;
}

.card-value {
    font-size: 28px;
    font-weight: 900;
    color: PRIMARY;
    margin: 0;
    line-height: 1.1;
}

.card-subtitle {
    font-size: 12px;
    color: TEXT_MUTED;
    margin-top: 4px;
}

.section-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 32px 0 16px 0;
}

.section-icon {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    background: linear-gradient(135deg, PRIMARY 0%, PRIMARY_DARK 100%);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    flex-shrink: 0;
}

.section-title {
    font-size: 24px;
    font-weight: 800;
    color: TEXT;
    margin: 0;
}

.section-subtitle {
    font-size: 13px;
    color: TEXT_MUTED;
    margin-top: 2px;
}

.stButton > button {
    background: linear-gradient(135deg, PRIMARY 0%, PRIMARY_DARK 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    box-shadow: 0 4px 14px rgba(99,102,241,0.3) !important;
    width: 100% !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(99,102,241,0.4) !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 4px !important;
    background: BG_SOFT !important;
    padding: 6px !important;
    border-radius: 14px !important;
    border: 1px solid BORDER !important;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    padding: 10px 18px !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    color: TEXT_MUTED !important;
}

.stTabs [aria-selected="true"] {
    background: BG_CARD !important;
    color: PRIMARY !important;
}

.stSelectbox > div > div,
.stNumberInput > div > div > input,
.stTextInput > div > div > input {
    background: BG_SOFT !important;
    color: TEXT !important;
    border: 1.5px solid BORDER !important;
    border-radius: 12px !important;
    padding: 10px 14px !important;
    font-size: 14px !important;
}

[data-testid="stMetricValue"] {
    color: PRIMARY !important;
    font-weight: 900 !important;
    font-size: 26px !important;
}

[data-testid="stMetricLabel"] {
    color: TEXT_MUTED !important;
    font-weight: 700 !important;
    font-size: 12px !important;
}

section[data-testid="stSidebar"] {
    background: BG_SOFT !important;
    border-right: 1px solid BORDER !important;
}

.footer {
    background: BG_SOFT;
    border-top: 1px solid BORDER;
    padding: 32px 20px;
    margin-top: 48px;
    border-radius: 16px;
    text-align: center;
    color: TEXT_MUTED;
}

.empty-state {
    text-align: center;
    padding: 64px 24px;
    color: TEXT_MUTED;
}

.empty-icon {
    font-size: 80px;
    margin-bottom: 16px;
    opacity: 0.4;
}

.empty-title {
    font-size: 20px;
    font-weight: 800;
    color: PRIMARY;
    margin-bottom: 8px;
}

.price-card {
    background: linear-gradient(135deg, PRIMARY 0%, PRIMARY_DARK 100%);
    border-radius: 20px;
    padding: 28px;
    color: white;
    text-align: center;
    box-shadow: 0 16px 40px rgba(99,102,241,0.35);
    margin: 16px 0;
}

.price-label {
    font-size: 14px;
    font-weight: 700;
    text-transform: uppercase;
    opacity: 0.9;
}

.price-value {
    font-size: 48px;
    font-weight: 900;
    margin: 12px 0 4px 0;
    line-height: 1;
}

.price-currency {
    font-size: 16px;
    opacity: 0.95;
}

.price-per-m2 {
    display: inline-block;
    background: rgba(255,255,255,0.2);
    padding: 8px 18px;
    border-radius: 100px;
    font-weight: 700;
    margin-top: 16px;
}

@media (max-width: 768px) {
    .hero-title { font-size: 28px; }
    .hero { padding: 32px 20px; }
    .stats-bar { grid-template-columns: repeat(2, 1fr); }
    .price-value { font-size: 36px; }
}
</style>
"""


def get_css(dark=False, lang="ar"):
    c = get_theme(dark)
    rtl = "rtl" if lang == "ar" else "ltr"
    font = "'Cairo','Tajawal',sans-serif" if lang == "ar" else "'Inter',sans-serif"
    
    css = CSS_TEMPLATE
    css = css.replace("FONT", font)
    css = css.replace("RTL", rtl)
    css = css.replace("BG_SOFT", c["bg_soft"])
    css = css.replace("BG_CARD", c["bg_card"])
    css = css.replace("BG", c["bg"])
    css = css.replace("TEXT_MUTED", c["text_muted"])
    css = css.replace("TEXT", c["text"])
    css = css.replace("BORDER", c["border"])
    css = css.replace("PRIMARY_DARK", c["primary_dark"])
    css = css.replace("PRIMARY", c["primary"])
    css = css.replace("SHADOW", c["shadow"])
    css = css.replace("HERO_FROM", c["hero_from"])
    css = css.replace("HERO_VIA", c["hero_via"])
    css = css.replace("HERO_TO", c["hero_to"])
    
    return css
