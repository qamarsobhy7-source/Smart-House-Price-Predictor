"""
Design system v3.0 — Property Finder style.
"""
COLORS = {
    "primary": "#6366f1", "primary_dark": "#4f46e5", "primary_light": "#818cf8",
    "success": "#10b981", "warning": "#f59e0b", "danger": "#ef4444",
    "text": "#1f2937", "text_muted": "#6b7280",
    "bg": "#ffffff", "bg_soft": "#f9fafb", "border": "#e5e7eb",
}
GRADIENT_PRIMARY = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
GRADIENT_HERO = "linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)"

def get_global_css(lang="en"):
    rtl = "rtl" if lang == "ar" else "ltr"
    font = "'Cairo','Tajawal',sans-serif" if lang == "ar" else "'Inter',sans-serif"
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Cairo:wght@400;500;600;700;800;900&display=swap');
    * { font-family: FONT_PLACEHOLDER !important; direction: RTL_PLACEHOLDER; }
    .main .block-container { padding-top: 1rem; padding-bottom: 3rem; max-width: 1200px; }
    
    .hero-section {
        background: HERO_GRAD;
        border-radius: 24px; padding: 40px 32px; color: white;
        text-align: center; margin-bottom: 24px;
        box-shadow: 0 20px 60px rgba(102,126,234,0.25);
        position: relative; overflow: hidden;
    }
    .hero-badge {
        display: inline-block; background: rgba(255,255,255,0.2);
        border: 1px solid rgba(255,255,255,0.3); backdrop-filter: blur(10px);
        padding: 6px 16px; border-radius: 100px;
        font-size: 12px; font-weight: 700; letter-spacing: 0.5px; margin-bottom: 16px;
    }
    .hero-title { font-size: 38px; font-weight: 900; margin: 0 0 12px 0; line-height: 1.2; }
    .hero-subtitle { font-size: 15px; opacity: 0.95; max-width: 600px; margin: 0 auto 24px; font-weight: 500; }
    .stats-bar { display: grid; grid-template-columns: repeat(4,1fr); gap: 12px; margin-top: 24px; }
    .stat-item {
        background: rgba(255,255,255,0.15); backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2); border-radius: 14px;
        padding: 12px 8px; text-align: center;
    }
    .stat-value { font-size: 20px; font-weight: 900; line-height: 1.1; }
    .stat-label { font-size: 10px; opacity: 0.85; font-weight: 600; letter-spacing: 0.4px; text-transform: uppercase; margin-top: 2px; }
    
    .form-card {
        background: white; border: 1px solid BORDER_PLACEHOLDER;
        border-radius: 18px; padding: 22px; margin-bottom: 18px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }
    .metric-card {
        background: white; border: 1px solid BORDER_PLACEHOLDER;
        border-radius: 14px; padding: 18px 12px; text-align: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }
    .metric-value { font-size: 22px; font-weight: 900; color: PRIMARY_PLACEHOLDER; line-height: 1.1; }
    .metric-label { font-size: 11px; color: MUTED_PLACEHOLDER; font-weight: 600; letter-spacing: 0.3px; text-transform: uppercase; margin-top: 6px; }
    
    .stButton > button {
        background: PRIMARY_GRAD !important; color: white !important;
        border: none !important; border-radius: 14px !important;
        padding: 14px 24px !important; font-weight: 800 !important;
        font-size: 15px !important;
        box-shadow: 0 8px 20px rgba(102,126,234,0.3) !important;
    }
    
    .stTabs [data-baseweb="tab-list"] { gap: 6px; background: BGSOFT_PLACEHOLDER; padding: 6px; border-radius: 14px; }
    .stTabs [data-baseweb="tab"] { border-radius: 10px !important; padding: 10px 16px !important; font-weight: 700 !important; font-size: 13px !important; }
    .stTabs [aria-selected="true"] { background: white !important; box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important; }
    
    .section-header { display: flex; align-items: center; gap: 12px; margin: 24px 0 16px; }
    .section-icon {
        width: 40px; height: 40px; border-radius: 12px;
        background: PRIMARY_GRAD; color: white;
        display: flex; align-items: center; justify-content: center;
        font-size: 20px; flex-shrink: 0;
    }
    .section-title { font-size: 20px; font-weight: 800; color: TEXT_PLACEHOLDER; margin: 0; }
    .section-subtitle { font-size: 12px; color: MUTED_PLACEHOLDER; margin-top: 2px; }
    
    .property-preview { background: PRIMARY_GRAD; border-radius: 20px; overflow: hidden; color: white; box-shadow: 0 12px 32px rgba(102,126,234,0.3); }
    .property-image {
        height: 140px; background: rgba(255,255,255,0.1);
        display: flex; align-items: center; justify-content: center;
        font-size: 60px; position: relative;
    }
    .property-badge {
        position: absolute; top: 12px; right: 12px;
        background: rgba(255,255,255,0.25); backdrop-filter: blur(10px);
        padding: 4px 10px; border-radius: 100px;
        font-size: 10px; font-weight: 800; letter-spacing: 0.5px;
    }
    .property-content { padding: 16px; }
    .property-title { font-size: 16px; font-weight: 800; margin-bottom: 4px; }
    .property-location { font-size: 12px; opacity: 0.9; margin-bottom: 12px; }
    .property-stats { display: grid; grid-template-columns: repeat(4,1fr); gap: 8px; }
    .property-stat { background: rgba(255,255,255,0.15); border-radius: 10px; padding: 8px 4px; text-align: center; }
    .property-stat-value { font-size: 15px; font-weight: 900; }
    .property-stat-label { font-size: 9px; opacity: 0.8; margin-top: 2px; text-transform: uppercase; letter-spacing: 0.3px; }
    
    .sim-card {
        background: white; border: 1px solid BORDER_PLACEHOLDER;
        border-radius: 14px; padding: 16px; margin-bottom: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }
    .sim-match { background: #ede9fe; color: PRIMARY_PLACEHOLDER; padding: 3px 10px; border-radius: 100px; font-size: 11px; font-weight: 800; }
    
    .market-strip {
        display: grid; grid-template-columns: repeat(3,1fr); gap: 10px;
        background: linear-gradient(135deg,#dbeafe,#e0e7ff);
        border-radius: 14px; padding: 14px; margin-top: 16px;
    }
    .market-item { text-align: center; }
    .market-label { font-size: 10px; color: #1e40af; font-weight: 800; letter-spacing: 0.4px; text-transform: uppercase; }
    .market-value { font-size: 15px; font-weight: 900; color: #1e3a8a; margin-top: 4px; }
    
    @media (max-width: 768px) {
        .hero-section { padding: 28px 20px; }
        .hero-title { font-size: 26px; }
        .hero-subtitle { font-size: 13px; }
        .stats-bar { grid-template-columns: repeat(2,1fr); }
        .stat-value { font-size: 17px; }
        .property-stats { grid-template-columns: repeat(2,1fr); }
        .market-strip { grid-template-columns: 1fr; }
    }
    </style>
    """
    css = css.replace("FONT_PLACEHOLDER", font)
    css = css.replace("RTL_PLACEHOLDER", rtl)
    css = css.replace("HERO_GRAD", GRADIENT_HERO)
    css = css.replace("PRIMARY_GRAD", GRADIENT_PRIMARY)
    css = css.replace("BORDER_PLACEHOLDER", COLORS["border"])
    css = css.replace("PRIMARY_PLACEHOLDER", COLORS["primary"])
    css = css.replace("MUTED_PLACEHOLDER", COLORS["text_muted"])
    css = css.replace("TEXT_PLACEHOLDER", COLORS["text"])
    css = css.replace("BGSOFT_PLACEHOLDER", COLORS["bg_soft"])
    return css


def get_hero_html(lang="en", accuracy="0.6843", error="18.39%",
                  cities=27, listings=7749):
    if lang == "ar":
        badge = "✨ مدعوم بالذكاء الاصطناعي"
        title = "اكتشف القيمة الحقيقية لعقارك"
        subtitle = "تقديرات ذكية لسوق العقارات المصري — بمستوى احترافي"
        labels = {"acc": "الدقة", "err": "متوسط الخطأ", "cities": "محافظة", "listings": "إعلان"}
    else:
        badge = "✨ AI-Powered"
        title = "Find Your Property's True Value"
        subtitle = "Smart estimates for the Egyptian real estate market"
        labels = {"acc": "Accuracy", "err": "Avg Error", "cities": "Governorates", "listings": "Listings"}

    html = '<div class="hero-section">'
    html += '<div class="hero-badge">' + badge + '</div>'
    html += '<h1 class="hero-title">' + title + '</h1>'
    html += '<p class="hero-subtitle">' + subtitle + '</p>'
    html += '<div class="stats-bar">'
    html += '<div class="stat-item"><div class="stat-value">' + accuracy + '</div><div class="stat-label">🎯 ' + labels["acc"] + '</div></div>'
    html += '<div class="stat-item"><div class="stat-value">' + error + '</div><div class="stat-label">📊 ' + labels["err"] + '</div></div>'
    html += '<div class="stat-item"><div class="stat-value">' + str(cities) + '</div><div class="stat-label">🏛️ ' + labels["cities"] + '</div></div>'
    html += '<div class="stat-item"><div class="stat-value">' + format(listings, ",") + '</div><div class="stat-label">📊 ' + labels["listings"] + '</div></div>'
    html += '</div></div>'
    return html


def get_section_header_html(icon, title, subtitle=""):
    sub = '<div class="section-subtitle">' + subtitle + '</div>' if subtitle else ""
    html = '<div class="section-header">'
    html += '<div class="section-icon">' + icon + '</div>'
    html += '<div><h2 class="section-title">' + title + '</h2>' + sub + '</div>'
    html += '</div>'
    return html


def get_step_header_html(step_num, icon, title, subtitle=""):
    """Return numbered step header (1, 2, 3, 4) — Property Finder style."""
    sub = '<div style="font-size:11px;color:#6b7280;margin-top:2px;">' + subtitle + '</div>' if subtitle else ""
    html = (
        '<div style="display:flex;align-items:center;gap:12px;'
        'margin:18px 0 12px 0;">'
        '<div style="background:linear-gradient(135deg,#667eea,#764ba2);'
        'color:white;width:34px;height:34px;border-radius:50%;'
        'display:flex;align-items:center;justify-content:center;'
        'font-weight:800;font-size:14px;flex-shrink:0;">' + str(step_num) + '</div>'
        '<div>'
        '<div style="font-weight:800;font-size:16px;color:#1f2937;">' + icon + ' ' + title + '</div>'
        + sub +
        '</div></div>'
    )
    return html
