"""
Neighborhood insights module — matches Property Finder / Bayut style.
Provides: schools, hospitals, malls, transport, walk score, price history.
"""
import json
from pathlib import Path
import pandas as pd
import streamlit as st

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"


@st.cache_data
def _load_map_data():
    f = DATA / "real_data" / "map_data.csv"
    if f.exists():
        return pd.read_csv(f)
    return pd.DataFrame()


def get_neighborhood_data(city, district):
    """Return neighborhood stats for a given location."""
    df = _load_map_data()
    if df.empty:
        return None
    
    # Filter
    mask = (df['city'] == city)
    sub = df[mask]
    if len(sub) == 0:
        return None
    
    # Filter by district if provided
    if 'district' in df.columns:
        d = sub[sub['district'] == district]
        if len(d) > 0:
            sub = d
    
    avg_price = sub['price_m'].mean() if 'price_m' in sub.columns else 0
    avg_size = sub['size'].mean() if 'size' in sub.columns else 0
    
    return {
        'listings': len(sub),
        'avg_price_m': avg_price,
        'avg_size': avg_size,
        'lat': sub['latitude'].mean() if 'latitude' in sub.columns else None,
        'lng': sub['longitude'].mean() if 'longitude' in sub.columns else None,
    }


def get_walk_score(district, city):
    """Calculate walk score — realistic values for Egyptian districts."""
    # قاموس كامل لجميع الأحياء الـ43
    WALK_SCORES = {
        'Zamalek': 95, 'Dokki': 92, 'Mohandessin': 90,
        'Al Agouza': 90, 'Hay El Manial': 88, 'Hay Sharq': 86,
        'El Nozha': 85, 'Heliopolis - Masr El Gedida': 85,
        'Hay El Maadi': 82, 'Nasr City': 80, 'Mokattam': 75,
        'El Khalifa': 78, 'Al Mansoura': 80, 'Hay Torah': 70,
        'Hay Wasat': 75, 'Hay Awal El Montazah': 72,
        'Hay Than El Montazah': 70, 'Ganoub El Giza': 65,
        'Hadayek El Ahram': 60, 'Meet Okba': 70,
        'Madinaty': 70, 'New Cairo City': 65, 'New Heliopolis': 70,
        'Shorouk City': 62, 'Obour City': 58, 'New Obour City': 60,
        'Sheikh Zayed City': 60, '6 October City': 55,
        'New Capital City': 50, 'Mostakbal City - Future City': 48,
        'Hurghada': 70, 'Al Ain Al Sokhna': 45, 'Al Alamein': 40,
        'Marsa Matrouh': 65, 'Qesm Marsa Matrouh': 65,
        'Qesm Ad Dabaah': 40, 'Ras Al Hekma': 45,
        'Sidi Abdel Rahman': 55, 'North Coast': 50,
        'Noor City': 45, 'New Mansoura': 55,
        'Ring Road': 70, 'Cairo Alexandria Desert Road': 55,
        'Alexandria Compounds': 60,
    }
    
    walk = WALK_SCORES.get(district, 60)
    # Transit دايماً أقل من Walk
    transit = max(25, int(walk * 0.75))
    # Amenities
    amenities = max(35, int(walk * 0.85))
    
    return {
        'walk': walk,
        'transit': transit,
        'amenities': amenities,
    }


def get_price_history(city, district):
    """Realistic price history for last 6 years."""
    # معدلات النمو السنوية لكل حي
    growth_rates = {
        'New Cairo City': 0.14, 'Sheikh Zayed City': 0.15,
        '6 October City': 0.13, 'Madinaty': 0.12,
        'Hay El Maadi': 0.11, 'Zamalek': 0.10,
        'Hurghada': 0.09, 'Al Agouza': 0.11,
        'Hay Sharq': 0.12, 'Hay El Manial': 0.10,
        'El Nozha': 0.11, 'Nasr City': 0.12,
        'Mokattam': 0.10, 'Dokki': 0.10,
        'Mohandessin': 0.09, 'Heliopolis - Masr El Gedida': 0.11,
    }
    rate = growth_rates.get(district, 0.11)
    
    # نجيب السعر من البيانات
    df = _load_map_data()
    base = 30000.0
    if not df.empty and 'price_per_sqm' in df.columns:
        sub = df[df['district'] == district] if 'district' in df.columns else df
        if len(sub) > 0:
            base = float(sub['price_per_sqm'].mean())
    
    # 6 سنوات من 2021 لـ 2026
    years = [2021, 2022, 2023, 2024, 2025, 2026]
    current_year = 2026
    # نرجع للخلف بنسبة النمو
    prices = []
    for y in years:
        years_back = current_year - y
        price_at_year = base / ((1 + rate) ** years_back)
        prices.append(round(price_at_year))
    
    return {
        'years': years,
        'prices': prices,
        'rate': rate,
        'current': base,
        'past': prices[0],
        'growth_5y': round((base - prices[0]) / prices[0] * 100, 1),
    }


def get_nearby_amenities(district):
    """Mock nearby amenities — realistic for Cairo areas."""
    amenities_map = {
        'New Cairo City': {
            'schools': 45, 'hospitals': 12, 'malls': 8, 'restaurants': 120,
            'banks': 25, 'pharmacies': 30, 'parks': 5, 'gyms': 15,
        },
        'Sheikh Zayed City': {
            'schools': 35, 'hospitals': 8, 'malls': 5, 'restaurants': 80,
            'banks': 18, 'pharmacies': 22, 'parks': 4, 'gyms': 10,
        },
        '6 October City': {
            'schools': 40, 'hospitals': 10, 'malls': 6, 'restaurants': 90,
            'banks': 20, 'pharmacies': 25, 'parks': 3, 'gyms': 12,
        },
        'Zamalek': {
            'schools': 20, 'hospitals': 15, 'malls': 3, 'restaurants': 200,
            'banks': 30, 'pharmacies': 15, 'parks': 4, 'gyms': 20,
        },
        'Hay El Maadi': {
            'schools': 25, 'hospitals': 12, 'malls': 5, 'restaurants': 150,
            'banks': 22, 'pharmacies': 20, 'parks': 6, 'gyms': 15,
        },
        'Hurghada': {
            'schools': 15, 'hospitals': 8, 'malls': 4, 'restaurants': 100,
            'banks': 10, 'pharmacies': 15, 'parks': 3, 'gyms': 8,
        },
    }
    
    default = {
        'schools': 20, 'hospitals': 8, 'malls': 4, 'restaurants': 60,
        'banks': 12, 'pharmacies': 15, 'parks': 3, 'gyms': 8,
    }
    
    return amenities_map.get(district, default)


def estimate_taxes(price, area, is_new=True):
    """Estimate property tax + insurance + maintenance."""
    # Egypt real estate tax (تقديري)
    # سعر المتر × المساحة × 0.1% تقريباً (بعد الإعفاءات)
    annual_rent = price * 0.045  # 4.5% عائد إيجاري
    exempt = 24000  # إعفاء سنوي
    taxable = max(0, annual_rent - exempt)
    tax = taxable * 0.10  # 10% من الإيجار
    tax = max(1500, tax)  # حد أدنى
    
    # Insurance
    insurance = price * 0.0015  # 0.15% من قيمة العقار
    
    # Maintenance (annual)
    maintenance = area * 180  # 180 ج/م² سنوي
    
    return {
        'tax': round(tax),
        'insurance': round(insurance),
        'maintenance': round(maintenance),
        'total_annual': round(tax + insurance + maintenance),
    }


# ═══════════════════════════════════════════════════════
# UI RENDERING FUNCTIONS
# ═══════════════════════════════════════════════════════

def render_walk_scores(district, city, lang="en"):
    """Render walk score, transit score, amenity score cards."""
    scores = get_walk_score(district, city)
    
    labels = {
        "ar": {"walk": "مشي", "transit": "مواصلات", "amenities": "مرافق"},
        "en": {"walk": "Walk Score", "transit": "Transit Score", "amenities": "Amenity Score"},
    }[lang]
    
    def color(v):
        if v >= 80: return "#10b981"
        if v >= 60: return "#84cc16"
        if v >= 40: return "#f59e0b"
        return "#ef4444"
    
    html = '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:14px 0;">'
    for key, label in labels.items():
        v = scores[key]
        c = color(v)
        html += (
            '<div style="background:white;border:2px solid ' + c + ';border-radius:14px;'
            'padding:14px 8px;text-align:center;">'
            '<div style="font-size:28px;font-weight:900;color:' + c + ';">' + str(v) + '</div>'
            '<div style="font-size:10px;color:#6b7280;font-weight:700;'
            'text-transform:uppercase;letter-spacing:0.5px;margin-top:4px;">' + label + '</div>'
            '</div>'
        )
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_nearby_amenities(district, lang="en"):
    """Render nearby amenities grid."""
    am = get_nearby_amenities(district)
    
    icons = {
        'schools': ('🏫', 'مدارس', 'Schools'),
        'hospitals': ('🏥', 'مستشفيات', 'Hospitals'),
        'malls': ('🛍️', 'مولات', 'Malls'),
        'restaurants': ('🍽️', 'مطاعم', 'Restaurants'),
        'banks': ('🏦', 'بنوك', 'Banks'),
        'pharmacies': ('💊', 'صيدليات', 'Pharmacies'),
        'parks': ('🌳', 'حدائق', 'Parks'),
        'gyms': ('💪', 'صالات رياضية', 'Gyms'),
    }
    
    html = '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:14px 0;">'
    for key, (icon, ar, en) in icons.items():
        label = ar if lang == "ar" else en
        count = am.get(key, 0)
        html += (
            '<div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:12px;'
            'padding:12px 6px;text-align:center;">'
            '<div style="font-size:24px;margin-bottom:4px;">' + icon + '</div>'
            '<div style="font-size:18px;font-weight:900;color:#1f2937;">' + str(count) + '</div>'
            '<div style="font-size:10px;color:#6b7280;font-weight:600;margin-top:2px;">' + label + '</div>'
            '</div>'
        )
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_price_history(city, district, lang="en"):
    """Render 6-year price history chart with KPIs."""
    import plotly.graph_objects as go
    
    hist = get_price_history(city, district)
    
    title = "📈 تاريخ الأسعار (6 سنوات)" if lang == "ar" else "📈 Price History (6 Years)"
    xlabel = "السنة" if lang == "ar" else "Year"
    ylabel = "السعر (جنيه/م²)" if lang == "ar" else "Price (EGP/m²)"
    
    # KPIs
    kpi1_lbl = "قبل 5 سنوات" if lang == "ar" else "5 Years Ago"
    kpi2_lbl = "السنة الحالية" if lang == "ar" else "Current"
    kpi3_lbl = "النمو الإجمالي" if lang == "ar" else "Total Growth"
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(kpi1_lbl, f"{hist['past']:,} EGP/m²")
    with c2:
        st.metric(kpi2_lbl, f"{hist['current']:,.0f} EGP/m²",
                  delta=f"+{hist['growth_5y']}%")
    with c3:
        st.metric(kpi3_lbl, f"+{hist['growth_5y']}%",
                  delta=f"+{hist['rate']*100:.1f}%/yr")
    
    st.markdown(f"### {title}")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hist['years'],
        y=hist['prices'],
        mode='lines+markers',
        line=dict(color='#6366f1', width=3),
        marker=dict(size=12, color='#6366f1', line=dict(color='white', width=2)),
        fill='tozeroy',
        fillcolor='rgba(99,102,241,0.15)',
        hovertemplate='<b>%{x}</b><br>%{y:,.0f} EGP/m²<extra></extra>',
    ))
    fig.update_layout(
        height=320,
        margin=dict(l=10, r=10, t=20, b=20),
        xaxis_title=xlabel,
        yaxis_title=ylabel,
        plot_bgcolor='white',
        showlegend=False,
        xaxis=dict(tickmode='array', tickvals=hist['years'], ticktext=[str(y) for y in hist['years']]),
        yaxis=dict(tickformat=',.0f'),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_tax_estimate(price, area, lang="en"):
    """Render tax, insurance, maintenance estimates."""
    est = estimate_taxes(price, area)
    
    labels = {
        "ar": {
            "title": "💰 التكاليف السنوية المتوقعة",
            "tax": "ضريبة عقارية",
            "insurance": "تأمين",
            "maintenance": "صيانة",
            "total": "الإجمالي السنوي",
            "note": "تقديري — قد يختلف حسب تفاصيل العقار",
        },
        "en": {
            "title": "💰 Estimated Annual Costs",
            "tax": "Property Tax",
            "insurance": "Insurance",
            "maintenance": "Maintenance",
            "total": "Total Annual",
            "note": "Estimates — actual may vary",
        },
    }[lang]
    
    st.markdown(f"### {labels['title']}")
    
    cols = st.columns(4)
    items = [
        ("🏛️", labels['tax'], est['tax']),
        ("🛡️", labels['insurance'], est['insurance']),
        ("🔧", labels['maintenance'], est['maintenance']),
        ("💵", labels['total'], est['total_annual']),
    ]
    for col, (icon, label, value) in zip(cols, items):
        with col:
            st.markdown(
                '<div style="background:white;border:1px solid #e5e7eb;'
                'border-radius:12px;padding:14px 8px;text-align:center;">'
                '<div style="font-size:22px;margin-bottom:4px;">' + icon + '</div>'
                '<div style="font-size:16px;font-weight:900;color:#6366f1;">'
                + f'{value:,}' + '</div>'
                '<div style="font-size:10px;color:#6b7280;font-weight:600;'
                'margin-top:4px;text-transform:uppercase;">' + label + '</div>'
                '</div>',
                unsafe_allow_html=True,
            )
    
    st.caption(labels['note'])


def render_neighborhood_insights(city, district, price, area, lang="en"):
    """Render all neighborhood insights in one place."""
    title = "🏘️ معلومات الحي" if lang == "ar" else "🏘️ Neighborhood Insights"
    st.markdown(f"## {title}")
    
    # Walk scores
    walk_title = "🚶 مؤشرات التنقل" if lang == "ar" else "🚶 Mobility Scores"
    st.markdown(f"#### {walk_title}")
    render_walk_scores(district, city, lang)
    
    # Nearby amenities
    amen_title = "📍 المرافق القريبة" if lang == "ar" else "📍 Nearby Amenities"
    st.markdown(f"#### {amen_title}")
    render_nearby_amenities(district, lang)
    
    # Price history
    render_price_history(city, district, lang)
    
    # Tax estimate
    render_tax_estimate(price, area, lang)
