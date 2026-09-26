"""Theme system — Light + Dark mode like Property Finder."""


# ═══════════════════════════════════════════════════════
# LIGHT THEME
# ═══════════════════════════════════════════════════════
LIGHT_THEME = {
    "bg": "#ffffff",
    "bg_soft": "#f9fafb",
    "bg_card": "#ffffff",
    "text": "#1f2937",
    "text_muted": "#6b7280",
    "border": "#e5e7eb",
    "primary": "#6366f1",
    "shadow": "rgba(0,0,0,0.04)",
    "hero_from": "#667eea",
    "hero_via": "#764ba2",
    "hero_to": "#f093fb",
}

# ═══════════════════════════════════════════════════════
# DARK THEME
# ═══════════════════════════════════════════════════════
DARK_THEME = {
    "bg": "#0f172a",
    "bg_soft": "#1e293b",
    "bg_card": "#1e293b",
    "text": "#f1f5f9",
    "text_muted": "#94a3b8",
    "border": "#334155",
    "primary": "#818cf8",
    "shadow": "rgba(0,0,0,0.3)",
    "hero_from": "#1e1b4b",
    "hero_via": "#4c1d95",
    "hero_to": "#831843",
}


def get_theme(dark=False):
    """Return theme dict."""
    return DARK_THEME if dark else LIGHT_THEME


def get_css(dark=False, lang="en"):
    """Generate CSS based on theme + language."""
    t = get_theme(dark)
    rtl = "rtl" if lang == "ar" else "ltr"
    font = "'Cairo','Tajawal',sans-serif" if lang == "ar" else "'Inter',sans-serif"

    # Base CSS
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Cairo:wght@400;500;600;700;800;900&display=swap');

    * { font-family: FONT !important; }
    body, .main, .stApp { background: BG !important; }
    .main .block-container { padding-top: 1rem; max-width: 1200px; }
    html, body, [class*="css"] { direction: RTL; color: TEXT; }

    /* Streamlit overrides */
    .stSelectbox label, .stSlider label, .stTextArea label, .stCheckbox label {
        color: TEXT !important;
    }
    .stSelectbox > div > div, .stNumberInput input, .stTextInput input, .stTextArea textarea {
        background: BG_SOFT !important;
        color: TEXT !important;
        border-color: BORDER !important;
    }
    div[data-baseweb="select"] > div {
        background: BG_SOFT !important;
        color: TEXT !important;
        border-color: BORDER !important;
    }
    .stMarkdown, .stCaption, p, h1, h2, h3, h4, h5, h6, span, label {
        color: TEXT !important;
    }
    div[data-baseweb="tab-list"] {
        background: BG_SOFT !important;
    }
    div[data-baseweb="tab"] {
        color: TEXT_MUTED !important;
    }
    div[aria-selected="true"][data-baseweb="tab"] {
        background: BG_CARD !important;
        color: PRIMARY !important;
    }
    .stDataFrame { background: BG_CARD !important; }
    section[data-testid="stSidebar"] { background: BG_SOFT !important; }

    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, HF 0%, HV 50%, HT 100%);
        border-radius: 24px; padding: 40px 32px; color: white;
        text-align: center; margin-bottom: 24px;
        box-shadow: 0 20px 60px rgba(102,126,234,0.25);
    }
    .hero-badge {
        display: inline-block; background: rgba(255,255,255,0.2);
        border: 1px solid rgba(255,255,255,0.3); backdrop-filter: blur(10px);
        padding: 6px 16px; border-radius: 100px;
        font-size: 12px; font-weight: 700; margin-bottom: 16px;
    }
    .hero-title { font-size: 38px; font-weight: 900; margin: 0 0 12px 0; }
    .hero-subtitle { font-size: 15px; opacity: 0.95; max-width: 600px;
                     margin: 0 auto 24px; font-weight: 500; }
    .stats-bar { display: grid; grid-template-columns: repeat(4,1fr);
                 gap: 12px; margin-top: 24px; }
    .stat-item { background: rgba(255,255,255,0.15); backdrop-filter: blur(10px);
                 border: 1px solid rgba(255,255,255,0.2); border-radius: 14px;
                 padding: 12px 8px; text-align: center; color: white; }
    .stat-value { font-size: 20px; font-weight: 900; color: white; }
    .stat-label { font-size: 10px; opacity: 0.85; font-weight: 600;
                  margin-top: 2px; text-transform: uppercase; color: white; }

    /* Cards */
    .form-card, .metric-card, .sim-card {
        background: BG_CARD !important;
        border: 1px solid BORDER !important;
        border-radius: 16px; padding: 18px;
        box-shadow: 0 2px 8px SHADOW;
        color: TEXT !important;
    }
    .metric-value { font-size: 22px; font-weight: 900;
                    color: PRIMARY !important; }
    .metric-label { font-size: 11px; color: TEXT_MUTED !important;
                    font-weight: 600; text-transform: uppercase; }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, HF 0%, HV 100%) !important;
        color: white !important; border: none !important;
        border-radius: 14px !important; padding: 14px 24px !important;
        font-weight: 800 !important; font-size: 15px !important;
    }

    /* Property preview */
    .property-preview {
        background: linear-gradient(135deg, HF 0%, HV 100%);
        border-radius: 20px; overflow: hidden; color: white;
    }

    /* Section headers */
    .section-icon {
        background: linear-gradient(135deg, HF 0%, HV 100%);
    }
    .section-title { color: TEXT !important; }
    .section-subtitle { color: TEXT_MUTED !important; }

    /* Step header */
    div[style*="border-radius:50%"] {
        background: linear-gradient(135deg, HF 0%, HV 100%) !important;
    }

    /* ═══════════════════════════════════════════════ */
    /* MOBILE OPTIMIZATION                             */
    /* ═══════════════════════════════════════════════ */
    @media (max-width: 768px) {
        /* Container */
        .main .block-container {
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
            padding-top: 0.5rem !important;
        }

        /* Hero */
        .hero-section {
            padding: 24px 16px !important;
            border-radius: 18px !important;
            margin-bottom: 16px !important;
        }
        .hero-title { font-size: 22px !important; line-height: 1.25 !important; }
        .hero-subtitle { font-size: 12px !important; margin-bottom: 16px !important; }
        .hero-badge { font-size: 10px !important; padding: 4px 10px !important; }

        /* Stats — 2 columns */
        .stats-bar {
            grid-template-columns: repeat(2,1fr) !important;
            gap: 8px !important;
        }
        .stat-item { padding: 10px 6px !important; }
        .stat-value { font-size: 16px !important; }
        .stat-label { font-size: 9px !important; }

        /* Streamlit columns — stack */
        section[data-testid="stMain"] > div > div > div[data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
            gap: 8px !important;
        }
        div[data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }

        /* Forms */
        .form-card { padding: 14px !important; border-radius: 14px !important; }
        .metric-card { padding: 12px 8px !important; }
        .metric-value { font-size: 18px !important; }
        .metric-label { font-size: 10px !important; }

        /* Inputs & Sliders */
        .stSelectbox label, .stSlider label, .stTextArea label,
        .stCheckbox label, .stNumberInput label {
            font-size: 13px !important;
        }
        .stSlider { padding: 4px 0 !important; }

        /* Buttons — full width + touch-friendly */
        .stButton > button {
            width: 100% !important;
            min-height: 44px !important;
            font-size: 14px !important;
            padding: 12px 16px !important;
            border-radius: 12px !important;
        }

        /* Tabs — scroll horizontally */
        div[data-baseweb="tab-list"] {
            overflow-x: auto !important;
            white-space: nowrap !important;
            padding: 4px !important;
            scrollbar-width: none !important;
        }
        div[data-baseweb="tab-list"]::-webkit-scrollbar { display: none !important; }
        div[data-baseweb="tab"] {
            font-size: 12px !important;
            padding: 8px 12px !important;
        }

        /* Tables */
        .stDataFrame { font-size: 12px !important; }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            width: 280px !important;
        }

        /* Header */
        header[data-testid="stHeader"] { height: 40px !important; }

        /* Section headers */
        .section-icon {
            width: 32px !important;
            height: 32px !important;
            font-size: 16px !important;
        }
        .section-title { font-size: 16px !important; }
        .section-subtitle { font-size: 10px !important; }

        /* Property card preview */
        .property-preview { border-radius: 16px !important; }
        .property-stats { grid-template-columns: repeat(2,1fr) !important; }

        /* Similar properties */
        .sim-card { padding: 12px !important; }
    }

    /* Small phones (≤ 480px) */
    @media (max-width: 480px) {
        .main .block-container {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }
        .hero-section { padding: 18px 12px !important; }
        .hero-title { font-size: 19px !important; }
        .hero-subtitle { font-size: 11px !important; }
        .stat-value { font-size: 14px !important; }
        .stat-label { font-size: 8px !important; }
        .stButton > button { font-size: 13px !important; }
        div[data-baseweb="tab"] { font-size: 11px !important; padding: 6px 10px !important; }
    }

    /* Tablets (769-1024px) */
    @media (min-width: 769px) and (max-width: 1024px) {
        .main .block-container { max-width: 960px !important; }
        .hero-title { font-size: 30px !important; }
    }

    /* Touch devices — bigger hit areas */
    @media (hover: none) and (pointer: coarse) {
        .stButton > button { min-height: 44px !important; }
        div[data-baseweb="tab"] { min-height: 40px !important; }
        .stSelectbox > div > div { min-height: 40px !important; }
    }
    </style>
    """

    css = css.replace("FONT", font)
    css = css.replace("RTL", rtl)
    css = css.replace("BG_SOFT", t["bg_soft"])
    css = css.replace("BG_CARD", t["bg_card"])
    css = css.replace("BG", t["bg"])
    css = css.replace("TEXT_MUTED", t["text_muted"])
    css = css.replace("TEXT", t["text"])
    css = css.replace("BORDER", t["border"])
    css = css.replace("PRIMARY", t["primary"])
    css = css.replace("SHADOW", t["shadow"])
    css = css.replace("HF", t["hero_from"])
    css = css.replace("HV", t["hero_via"])
    css = css.replace("HT", t["hero_to"])

    return css
