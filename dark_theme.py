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
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=block');

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
    /* MOBILE OPTIMIZATION — v4 (fix sidebar)          */
    /* ═══════════════════════════════════════════════ */
    @media (max-width: 768px) {
        /* Container */
        .main .block-container {
            padding-left: 0.6rem !important;
            padding-right: 0.6rem !important;
            padding-top: 0.5rem !important;
            max-width: 100% !important;
            width: 100% !important;
        }

        /* ─── SIDEBAR — HIDDEN BY DEFAULT ─── */
        section[data-testid="stSidebar"] {
            min-width: 260px !important;
            max-width: 85vw !important;
            width: 85vw !important;
            z-index: 9999 !important;
            position: fixed !important;
            top: 0 !important;
            bottom: 0 !important;
            transition: transform 0.3s ease !important;
        }
        /* Hide when collapsed */
        section[data-testid="stSidebar"][aria-expanded="false"] {
            transform: translateX(-100%) !important;
        }
        section[data-testid="stSidebar"][aria-expanded="false"] ~ div,
        section[data-testid="stSidebar"][aria-expanded="false"] + div {
            margin-left: 0 !important;
            width: 100% !important;
        }
        /* Ensure main content is full width */
        section.main, .main, main {
            margin-left: 0 !important;
            width: 100% !important;
            max-width: 100% !important;
        }
        /* Hide resize handle */
        [data-testid="stSidebarResizeHandle"],
        [data-testid="stSidebarCollapseButton"] {
            display: none !important;
        }
        /* ─── SIDEBAR TOGGLE BUTTON ─── */
        [data-testid="stSidebarCollapsedControl"] {
            position: fixed !important;
            top: 8px !important;
            left: 8px !important;
            z-index: 1000 !important;
        }
        [data-testid="stSidebarCollapsedControl"] button {
            width: 40px !important;
            height: 40px !important;
            padding: 0 !important;
            background: white !important;
            border: 1px solid #e5e7eb !important;
            border-radius: 10px !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
            color: #6366f1 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            font-size: 0 !important;
            text-indent: -9999px !important;
            overflow: hidden !important;
        }
        /* Hide ALL text content inside (the icon name text) */
        [data-testid="stSidebarCollapsedControl"] * {
            font-size: 0 !important;
            color: transparent !important;
            visibility: hidden !important;
        }
        /* Then show the button itself */
        [data-testid="stSidebarCollapsedControl"] button {
            visibility: visible !important;
        }
        [data-testid="stSidebarCollapsedControl"] button::before {
            content: "☰" !important;
            font-size: 20px !important;
            color: #6366f1 !important;
            visibility: visible !important;
            font-family: Arial, sans-serif !important;
        }
        [data-testid="stSidebarCollapsedControl"] button::after {
            display: none !important;
        }

        /* Hide any stray material icons globally */
        .material-symbols-rounded,
        span[data-testid="stIconMaterial"] {
            font-family: inherit !important;
        }

        /* Hero */
        .hero-section {
            padding: 22px 14px !important;
            border-radius: 18px !important;
            margin-bottom: 14px !important;
        }
        .hero-title { font-size: 22px !important; line-height: 1.3 !important; }
        .hero-subtitle { font-size: 12px !important; margin-bottom: 14px !important; }
        .hero-badge { font-size: 10px !important; padding: 4px 10px !important; }
        .stats-bar { grid-template-columns: repeat(2,1fr) !important; gap: 8px !important; }
        .stat-item { padding: 10px 6px !important; }
        .stat-value { font-size: 15px !important; }
        .stat-label { font-size: 9px !important; }

        /* Sections */
        .section-icon { width: 32px !important; height: 32px !important; font-size: 16px !important; }
        .section-title { font-size: 16px !important; }
        .section-subtitle { font-size: 11px !important; }

        /* Form cards */
        .form-card { padding: 14px 10px !important; border-radius: 14px !important; }

        /* Buttons */
        .stButton > button {
            width: 100% !important;
            min-height: 42px !important;
            font-size: 13px !important;
            padding: 8px 12px !important;
            border-radius: 10px !important;
            white-space: normal !important;
            height: auto !important;
            line-height: 1.3 !important;
        }

        /* Tabs */
        div[data-baseweb="tab-list"] {
            overflow-x: auto !important;
            white-space: nowrap !important;
            padding: 4px !important;
            scrollbar-width: none !important;
        }
        div[data-baseweb="tab-list"]::-webkit-scrollbar { display: none !important; }
        div[data-baseweb="tab"] {
            font-size: 11px !important;
            padding: 6px 10px !important;
            min-height: 38px !important;
        }

        /* Selectboxes */
        div[data-baseweb="select"] > div {
            min-height: 40px !important;
            padding: 4px 8px !important;
        }
        div[data-baseweb="select"] span { font-size: 12px !important; }

        /* Sliders */
        .stSlider label { font-size: 12px !important; }

        /* Metrics */
        .metric-value { font-size: 18px !important; }
        .metric-label { font-size: 10px !important; }

        /* Market strip */
        .market-strip { grid-template-columns: 1fr !important; gap: 6px !important; }

        /* Property preview */
        .property-preview { border-radius: 16px !important; }
        .property-title { font-size: 15px !important; }
        .property-stats { grid-template-columns: repeat(2,1fr) !important; }

        /* FAQ */
        [data-testid="stExpander"] summary {
            font-size: 12px !important;
            padding: 10px 12px !important;
            min-height: 44px !important;
        }
        [data-testid="stExpander"] p { font-size: 12px !important; }

        /* Checkboxes */
        .stCheckbox label { font-size: 12px !important; line-height: 1.3 !important; }

        /* Featured + Popular — 2 columns */
        div[style*="grid-template-columns: repeat(4"] {
            grid-template-columns: repeat(2, 1fr) !important;
        }
        div[style*="grid-template-columns:repeat(4"] {
            grid-template-columns: repeat(2, 1fr) !important;
        }

        /* Two-column HTML grids → single */
        div[style*="grid-template-columns:1fr 1fr"] {
            grid-template-columns: 1fr !important;
        }
    }

    /* Small phones */
    @media (max-width: 480px) {
        .main .block-container { padding-left: 0.4rem !important; padding-right: 0.4rem !important; }
        .hero-title { font-size: 18px !important; }
        .hero-subtitle { font-size: 11px !important; }
        .stat-value { font-size: 13px !important; }
        .stButton > button { font-size: 12px !important; }
        div[data-baseweb="tab"] { font-size: 10px !important; padding: 5px 8px !important; }
    }
        
    /* ═══════════════════════════════════════════════ */
    /* HIDE MATERIAL ICON TEXT (fallback)              */
    /* ═══════════════════════════════════════════════ */
    button[kind="headerNoPadding"],
    button[kind="header"] {
        font-size: 0 !important;
    }
    button[kind="headerNoPadding"] span,
    button[kind="header"] span {
        font-size: 14px !important;
    }
    /* ═══════════════════════════════════════════════ */
    /* STREAMLIT ICON FIX — hide material text          */
    /* ═══════════════════════════════════════════════ */
    /* Hide the raw icon text everywhere */
    [data-testid="stIconMaterial"] {
        font-size: 0 !important;
        color: transparent !important;
        width: 20px !important;
        height: 20px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        vertical-align: middle !important;
        overflow: hidden !important;
        position: relative !important;
    }
    /* Replace with custom symbol */
    [data-testid="stIconMaterial"]::before {
        content: "" !important;
        display: block !important;
        width: 18px !important;
        height: 18px !important;
        background-size: contain !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
    }

    /* Sidebar collapse button — hamburger */
    [data-testid="stSidebarCollapsedControl"] [data-testid="stIconMaterial"]::before {
        content: "☰" !important;
        font-size: 20px !important;
        color: #6366f1 !important;
        font-family: Arial, sans-serif !important;
        font-weight: 900 !important;
        width: auto !important;
        height: auto !important;
        background: none !important;
        line-height: 1 !important;
    }
    [data-testid="stSidebarCollapsedControl"] {
        z-index: 10000 !important;
    }
    [data-testid="stSidebarCollapsedControl"] button {
        width: 42px !important;
        height: 42px !important;
        padding: 0 !important;
        background: white !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* When sidebar is open — show X icon */
    section[data-testid="stSidebar"] [data-testid="stIconMaterial"]::before {
        content: "✕" !important;
        font-size: 18px !important;
        color: #6366f1 !important;
        font-family: Arial, sans-serif !important;
        font-weight: 900 !important;
        width: auto !important;
        height: auto !important;
        background: none !important;
        line-height: 1 !important;
    }


    /* ═══════════════════════════════════════════════ */
    /* FORCE HIDE ICON TEXT — strong override          */
    /* ═══════════════════════════════════════════════ */
    /* Force Material Icons font on ALL icon spans */
    span[data-testid="stIconMaterial"],
    span[class*="st-emotion-cache"] span[data-testid="stIconMaterial"],
    [data-testid="stIconMaterial"] {
        font-family: 'Material Icons', 'Material Symbols Rounded' !important;
        font-size: 24px !important;
        font-weight: normal !important;
        font-style: normal !important;
        line-height: 1 !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        word-wrap: normal !important;
        direction: ltr !important;
        -webkit-font-feature-settings: 'liga' !important;
        -webkit-font-smoothing: antialiased !important;
        text-rendering: optimizeLegibility !important;
        color: inherit !important;
    }

    /* Load font via @font-face in CSS */
    @font-face {
        font-family: 'Material Icons';
        font-style: normal;
        font-weight: 400;
        src: url(https://fonts.gstatic.com/s/materialicons/v140/flUhRq6tzZclQEJ-Vdg-IuiaDsNc.woff2) format('woff2');
    }
    @font-face {
        font-family: 'Material Symbols Rounded';
        font-style: normal;
        font-weight: 400;
        src: url(https://fonts.gstatic.com/s/materialsymbolsrounded/v211/syl0-zNym6YjUruM-QrEh7-nyTnjDwKNJ_190FjpZIvDmUSVOK7BDB_Qb9vUSzq3wzLK-P0J-V_Zs-QtQth3-jOcbTCVpeRL2w5rwZu2rIelXxGJKJBiCa8.woff2) format('woff2');
    }

    /* ═══════════════════════════════════════════════ */
    /* SIDEBAR TOGGLE — final styling                   */
    /* ═══════════════════════════════════════════════ */
    [data-testid="stSidebarCollapsedControl"] {
        position: fixed !important;
        top: 12px !important;
        left: 12px !important;
        z-index: 1000 !important;
    }
    [data-testid="stSidebarCollapsedControl"] button {
        width: 44px !important;
        height: 44px !important;
        padding: 0 !important;
        background: white !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.2s !important;
    }
    [data-testid="stSidebarCollapsedControl"] button:hover {
        box-shadow: 0 4px 16px rgba(99,102,241,0.2) !important;
        border-color: #6366f1 !important;
    }
    [data-testid="stSidebarCollapsedControl"] [data-testid="stIconMaterial"] {
        font-size: 22px !important;
        color: #6366f1 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* ═══════════════════════════════════════════════ */
    /* QUICK FILTER CHIPS — responsive sizing          */
    /* ═══════════════════════════════════════════════ */
    /* Make chip buttons smaller + wrap text */
    div[data-testid="column"] .stButton > button {
        padding: 8px 6px !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        line-height: 1.25 !important;
        white-space: normal !important;
        word-break: break-word !important;
        height: auto !important;
        min-height: 42px !important;
    }

    /* On mobile — even smaller */
    @media (max-width: 768px) {
        div[data-testid="column"] .stButton > button {
            font-size: 11px !important;
            padding: 6px 4px !important;
            min-height: 40px !important;
            border-radius: 10px !important;
        }
    }
    @media (max-width: 480px) {
        div[data-testid="column"] .stButton > button {
            font-size: 10px !important;
            padding: 5px 3px !important;
            min-height: 38px !important;
        }
    }

        /* ═══════════════════════════════════════════════ */
    /* HIDE SIDEBAR TOGGLE COMPLETELY                  */
    /* ═══════════════════════════════════════════════ */
    /* Hide the toggle button in header */
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarCollapseButton"],
    button[kind="header"],
    button[kind="headerNoPadding"] {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
        overflow: hidden !important;
        position: absolute !important;
        left: -9999px !important;
    }

    /* Hide any icon-related text */
    span[data-testid="stIconMaterial"],
    span[class*="material"] {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
        font-size: 0 !important;
        color: transparent !important;
    }

    /* Sidebar default hidden on mobile */
    @media (max-width: 768px) {
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        /* Show sidebar only when opened via custom button */
        section[data-testid="stSidebar"][aria-expanded="true"] {
            display: block !important;
        }
    }

    /* ═══════════════════════════════════════════════ */
    /* KILL ALL MATERIAL ICONS (they show as text)    */
    /* ═══════════════════════════════════════════════ */
    
    /* Hide ALL icon elements completely */
    [data-testid="stIconMaterial"],
    [data-testid="stIconMaterial"] *,
    span[class*="stIconMaterial"],
    .material-symbols-rounded,
    .material-symbols-outlined,
    .material-icons,
    i.material-icons {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
        font-size: 0 !important;
        line-height: 0 !important;
        opacity: 0 !important;
        pointer-events: none !important;
        position: absolute !important;
        left: -99999px !important;
    }

    /* Hide the sidebar toggle button */
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarCollapseButton"],
    button[kind="header"],
    button[kind="headerNoPadding"] {
        display: none !important;
        visibility: hidden !important;
    }

    /* Hide expender default arrows (use custom) */
    [data-testid="stExpander"] summary svg,
    [data-testid="stExpander"] summary [data-testid="stIconMaterial"] {
        display: none !important;
    }
    [data-testid="stExpander"] summary::before {
        content: "▼" !important;
        font-size: 10px !important;
        color: #6b7280 !important;
        margin-right: 8px !important;
        transition: transform 0.2s !important;
        display: inline-block !important;
    }
    [data-testid="stExpander"][open] summary::before {
        transform: rotate(-180deg) !important;
    }

    /* ═══════════════════════════════════════════════ */
    /* KILL SIDEBAR COMPLETELY                         */
    /* ═══════════════════════════════════════════════ */
    section[data-testid="stSidebar"] {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        min-width: 0 !important;
        max-width: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        overflow: hidden !important;
    }
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarContent"],
    [data-testid="stSidebarUserContent"] {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
    }

    /* Ensure main content takes full width */
    section.main,
    .main,
    main,
    [data-testid="stMain"] {
        margin-left: 0 !important;
        width: 100% !important;
        max-width: 100% !important;
        padding-left: 0 !important;
    }
    .main .block-container {
        margin-left: auto !important;
        margin-right: auto !important;
    }

    /* Fix RTL — prevent any vertical text */
    [dir="rtl"] *,
    body[dir="rtl"] * {
        writing-mode: horizontal-tb !important;
        text-orientation: mixed !important;
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


def get_icon_fix_js():
    """Return JavaScript to fix material icons showing as text."""
    return """
    <script>
    (function() {
        function fixIcons() {
            // Fix all stIconMaterial elements
            const icons = document.querySelectorAll('[data-testid="stIconMaterial"]');
            icons.forEach(function(icon) {
                const text = icon.textContent.trim();
                if (text && text.includes('_')) {
                    // Replace with proper symbol
                    let symbol = '•';
                    if (text.includes('double_arrow_right') || text.includes('arrow_right')) {
                        symbol = '☰';
                    } else if (text.includes('double_arrow_left') || text.includes('arrow_left')) {
                        symbol = '✕';
                    } else if (text.includes('keyboard')) {
                        symbol = '☰';
                    } else if (text.includes('expand_more')) {
                        symbol = '▼';
                    } else if (text.includes('expand_less')) {
                        symbol = '▲';
                    } else if (text.includes('close')) {
                        symbol = '✕';
                    } else if (text.includes('search')) {
                        symbol = '🔍';
                    } else if (text.includes('menu')) {
                        symbol = '☰';
                    } else if (text.includes('check')) {
                        symbol = '✓';
                    }
                    icon.textContent = symbol;
                    icon.style.fontFamily = 'Arial, sans-serif';
                    icon.style.fontSize = '18px';
                    icon.style.color = '#6366f1';
                    icon.style.fontWeight = '900';
                    icon.style.lineHeight = '1';
                }
            });
        }

        // Run on load
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', fixIcons);
        } else {
            fixIcons();
        }

        // Run after delays (Streamlit re-renders)
        setTimeout(fixIcons, 500);
        setTimeout(fixIcons, 1500);
        setTimeout(fixIcons, 3000);

        // Watch for DOM changes
        const observer = new MutationObserver(function(mutations) {
            fixIcons();
        });
        observer.observe(document.body, { childList: true, subtree: true });

    })();
    </script>
    """
