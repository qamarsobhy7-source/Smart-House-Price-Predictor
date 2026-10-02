
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import folium
from streamlit_folium import folium_static
from datetime import datetime

# PDF Report
try:
    import reportlab
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import cm
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Custom modules
try:
    from mock_images import get_property_images
    from favorites import add_favorite, remove_favorite, get_favorites, is_favorite
    from neighborhood import render_neighborhood_info
    CUSTOM_MODULES = True
except ImportError:
    CUSTOM_MODULES = False

st.set_page_config(
    page_title="Egypt Real Estate AI",
    page_icon="🏠",
    layout="wide",
)

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    .hero {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem; border-radius: 20px; color: white;
        margin-bottom: 2rem; box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    .hero h1 { margin: 0; font-size: 2.5rem; font-weight: 800; }
    .hero p { margin: 0.5rem 0 0 0; opacity: 0.95; }
    .metric-card {
        background: white; padding: 1.5rem; border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
        transition: transform 0.3s;
    }
    .metric-card:hover { transform: translateY(-5px); }
    .metric-card h3 {
        margin: 0; font-size: 0.9rem; color: #667eea;
        text-transform: uppercase; letter-spacing: 1px;
    }
    .metric-card .value {
        font-size: 2rem; font-weight: 800; color: #2d3748;
        margin: 0.5rem 0;
    }
    .result-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 2.5rem; border-radius: 20px; color: white;
        text-align: center; box-shadow: 0 10px 40px rgba(245, 87, 108, 0.3);
    }
    .result-card .price { font-size: 3.5rem; font-weight: 900; margin: 1rem 0; }
    .section-header {
        font-size: 1.5rem; font-weight: 700; color: #2d3748;
        margin: 1.5rem 0 1rem 0; padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea; display: inline-block;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; border: none; padding: 0.75rem 2rem;
        border-radius: 10px; font-weight: 600; width: 100%;
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# LOAD MODEL
# ═══════════════════════════════════════════════════════════════
@st.cache_resource
def load_model():
    base = Path(__file__).resolve().parent
    model = joblib.load(base / "models" / "FINAL_MODEL_v9.pkl")
    features = joblib.load(base / "models" / "FINAL_FEATURES_v9.pkl")
    cat_features = joblib.load(base / "models" / "FINAL_CAT_FEATURES_v9.pkl")
    return model, features, cat_features

@st.cache_data
def load_data():
    base = Path(__file__).resolve().parent
    return pd.read_csv(base / "data" / "processed" / "FINAL_DATASET_v9.csv")

try:
    model, features, cat_features = load_model()
    df = load_data()
    loaded = True
except Exception as e:
    loaded = False
    st.error(f"Error loading: {e}")

# Initialize session state
if "favorites" not in st.session_state:
    st.session_state.favorites = []
if "current_prediction" not in st.session_state:
    st.session_state.current_prediction = None

# ═══════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
    <h1>🏠 Egypt Real Estate AI</h1>
    <p>🤖 توقع ذكي لأسعار العقارات في مصر</p>
    <p style="font-size:0.9rem; opacity:0.8;">
        📊 119,916 إعلان | 🏙️ 6 محافظات | 🎯 R² = 0.71
    </p>
</div>
""", unsafe_allow_html=True)

if not loaded:
    st.stop()

# ═══════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🎯 التوقع",
    "📊 تحليل السوق",
    "🗺️ الخريطة",
    "🧮 حاسبة الرهن",
    "⭐ العقارات المميزة",
    "❤️ المفضلة",
    "ℹ️ عن المشروع"
])


# ═══════════════════════════════════════════════════════════════
# TAB 1: PREDICTION
# ═══════════════════════════════════════════════════════════════
with tab1:
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        st.markdown('<div class="section-header">📝 مواصفات العقار</div>', unsafe_allow_html=True)
        
        governorate = st.selectbox(
            "🏙️ المحافظة",
            ["Cairo", "Giza", "Matrouh", "Red Sea", "Alexandria", "Suez"]
        )
        
        districts_available = sorted(
            df[df['governorate'] == governorate]['district'].unique().tolist()
        )
        district = st.selectbox("📍 المنطقة", districts_available)
        
        property_type = st.selectbox(
            "🏢 نوع العقار",
            ["Apartment", "Villa", "Townhouse", "Duplex", "Penthouse",
             "Twin House", "iVilla", "Hotel Apartment", "Chalet"]
        )
        
        col_a, col_b = st.columns(2)
        with col_a:
            size = st.number_input("📐 المساحة (م²)", 20, 5000, 200, 10)
        with col_b:
            bedrooms = st.number_input("🛏️ غرف", 0, 15, 3)
        
        col_c, col_d = st.columns(2)
        with col_c:
            bathrooms = st.number_input("🚿 حمامات", 1, 15, 2)
        with col_d:
            amenity_count = st.number_input("✨ كماليات", 0, 20, 5)
        
        col_e, col_f = st.columns(2)
        with col_e:
            completion = st.selectbox(
                "🏗️ حالة الإنشاء",
                ["completed", "off_plan", "completed_primary", "off_plan_primary"]
            )
        with col_f:
            furnished = st.selectbox(
                "🛋️ الفرش",
                ["Unfurnished", "Furnished", "PARTLY"]
            )
        
        images_count = st.slider("📸 عدد الصور", 0, 30, 10)
        
        predict_btn = st.button("🔮 توقع السعر", type="primary", use_container_width=True)
    
    with col2:
        if predict_btn:
            sample = df[(df['governorate'] == governorate) & (df['district'] == district)]
            lat = sample['latitude'].median() if len(sample) > 0 else 30.0444
            lon = sample['longitude'].median() if len(sample) > 0 else 31.2357
            
            input_data = {}
            for f in features:
                if f in cat_features:
                    input_data[f] = 'Unknown'
                else:
                    input_data[f] = 0
            
            input_data.update({
                'size': size, 'bedrooms': bedrooms, 'bathrooms': bathrooms,
                'amenity_count': amenity_count, 'images_count': images_count,
                'latitude': lat, 'longitude': lon,
                'property_type': property_type, 'governorate': governorate,
                'district': district, 'compound': 'No Compound',
                'completion_status': completion, 'furnished': furnished,
                'seller_type': 'Broker', 'developer_name': 'Unknown',
                'view': 'Unknown', 'finishing_type': 'Unknown',
                'payment_method': 'Unknown', 'town': governorate,
                'area_per_room': size / max(bedrooms, 1),
                'total_rooms': bedrooms + bathrooms,
                'bed_bath_ratio': bedrooms / max(bathrooms, 1),
                'amenity_per_room': amenity_count / max(bedrooms + bathrooms, 1),
                'images_per_room': images_count / max(bedrooms + bathrooms, 1),
                'lat_x_lon': lat * lon,
                'distance_to_cairo': 0, 'distance_to_coast': 0,
                'distance_cairo_sq': 0, 'is_coastal': 0, 'is_cairo_center': 0,
                'is_high_end': 1 if property_type in ['Villa', 'Palace'] else 0,
                'is_luxury': 1 if property_type in ['Villa', 'Penthouse', 'Twin House'] else 0,
                'is_compound': 0, 'is_premium': 0, 'is_featured': 0,
                'walk_score': 50, 'transit_score': 50,
                'amenity_score': amenity_count / 20,
                'floor_level': 3, 'year_built': 2024, 'has_premium_info': 0,
            })
            
            X_input = pd.DataFrame([input_data])[features]
            log_price = model.predict(X_input)[0]
            price = np.expm1(log_price)
            ppm2 = price / size
            
            st.markdown(f"""
            <div class="result-card">
                <div style="font-size:1.1rem;">💰 السعر المتوقع</div>
                <div class="price">{price:,.0f}</div>
                <div style="font-size:1.2rem;">جنيه مصري</div>
                <div style="background:rgba(255,255,255,0.2);padding:0.75rem 1.5rem;border-radius:10px;display:inline-block;margin-top:1rem;">
                    💵 سعر المتر: {ppm2:,.0f} EGP/m²
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # نحفظ التوقع في session state
            st.session_state.current_prediction = {
                "id": f"pred_{len(st.session_state.favorites)}",
                "governorate": governorate,
                "district": district,
                "property_type": property_type,
                "size": size,
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "price": price,
                "ppm2": ppm2,
            }
            
            # أزرار الإجراءات
            col_b1, col_b2, col_b3, col_b4 = st.columns(4)
            with col_b1:
                if st.button("❤️ حفظ", use_container_width=True):
                    add_favorite(st.session_state.current_prediction)
                    st.success("✅ اتحفظ!")
            with col_b2:
                st.markdown(f"""
                <a href="https://wa.me/201001234567?text=مرحباً، مهتم بـ {property_type} في {district}" 
                   target="_blank" style="text-decoration:none;">
                    <button style="width:100%; padding:0.5rem; background:#25D366; color:white; border:none; border-radius:8px; cursor:pointer; font-weight:600;">
                        📱 WhatsApp
                    </button>
                </a>
                """, unsafe_allow_html=True)
            with col_b3:
                st.markdown(f"""
                <a href="tel:+201001234567" style="text-decoration:none;">
                    <button style="width:100%; padding:0.5rem; background:#667eea; color:white; border:none; border-radius:8px; cursor:pointer; font-weight:600;">
                        📞 اتصل
                    </button>
                </a>
                """, unsafe_allow_html=True)
            with col_b4:
                if PDF_AVAILABLE:
                    pdf_bytes = generate_property_pdf(st.session_state.current_prediction)
                    if pdf_bytes:
                        st.download_button(
                            "📄 PDF",
                            data=pdf_bytes,
                            file_name=f"property_{district}_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                        )
            
            # الصور
            st.markdown("### 📸 صور العقار")
            if CUSTOM_MODULES:
                images = get_property_images(
                    st.session_state.current_prediction["id"],
                    property_type,
                    count=5
                )
                
                # نعرض الصور في slider
                img_cols = st.columns(5)
                for i, img_url in enumerate(images):
                    with img_cols[i]:
                        st.image(img_url, use_container_width=True)
            
            # مقارنة مع السوق
            market_median = df[(df['governorate'] == governorate) &
                                (df['property_type'] == property_type)]['price'].median()
            
            if pd.notna(market_median):
                diff_pct = (price - market_median) / market_median * 100
                col_x, col_y = st.columns(2)
                with col_x:
                    st.metric("📊 متوسط السوق", f"{market_median:,.0f} EGP")
                with col_y:
                    st.metric("📈 الفرق", f"{diff_pct:+.1f}%")
            
            # معلومات الحي
            if CUSTOM_MODULES:
                st.markdown("---")
                render_neighborhood_info(district)
        else:
            st.markdown("""
            <div style="text-align:center;padding:4rem 2rem;color:#999;">
                <div style="font-size:5rem;">🏠</div>
                <h3 style="color:#667eea;">احسب سعر عقارك الآن</h3>
                <p>ادخل المواصفات واضغط "توقع السعر"</p>
            </div>
            """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# TAB 2: MARKET ANALYSIS
# ═══════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">📊 تحليل السوق الشامل</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📊 إعلانات</h3>
            <div class="value">{len(df):,}</div>
            <small>في 6 محافظات</small>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>💰 متوسط السعر</h3>
            <div class="value">{df['price'].median()/1e6:.1f}M</div>
            <small>EGP</small>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📐 متوسط المساحة</h3>
            <div class="value">{df['size'].median():.0f}</div>
            <small>m²</small>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🏙️ مناطق</h3>
            <div class="value">{df['district'].nunique()}</div>
            <small>منطقة</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(df, names='property_type', hole=0.4,
                     title='🏢 توزيع أنواع العقارات',
                     color_discrete_sequence=px.colors.qualitative.Set3)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        avg = df.groupby('governorate')['price'].median().sort_values()
        fig = px.bar(x=avg.values, y=avg.index, orientation='h',
                     title='💰 متوسط السعر حسب المحافظة',
                     labels={'x': 'السعر (EGP)', 'y': ''},
                     color=avg.values, color_continuous_scale='Viridis')
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        fig = px.histogram(df.sample(min(5000, len(df))), x='price', nbins=50,
                           title='📊 توزيع الأسعار',
                           color_discrete_sequence=['#667eea'])
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col4:
        sample = df.sample(min(2000, len(df)))
        fig = px.scatter(sample, x='size', y='price', color='property_type',
                         title='📐 المساحة vs السعر', opacity=0.6)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('<div class="section-header">📋 جدول تفصيلي</div>', unsafe_allow_html=True)
    
    table = df.groupby('governorate').agg({
        'price': ['count', 'median', 'mean', 'min', 'max'],
        'size': 'median',
        'district': 'nunique',
        'compound': 'nunique',
    }).round(0)
    table.columns = ['إعلانات', 'متوسط', 'معدل', 'أدنى', 'أقصى', 'مساحة', 'مناطق', 'كمبوندات']
    st.dataframe(table, use_container_width=True)


# ═══════════════════════════════════════════════════════════════
# TAB 3: MAP
# ═══════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">🗺️ خريطة العقارات التفاعلية</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        map_gov = st.selectbox("المحافظة", df['governorate'].unique(), key='map_g')
    with col2:
        map_type = st.selectbox("النوع", ['الكل'] + list(df['property_type'].unique()), key='map_t')
    with col3:
        max_points = st.slider("عدد النقاط", 100, 2000, 500, key='map_p')
    with col4:
        map_view = st.selectbox("طريقة العرض", ['عادي', '🔥 خريطة حرارية'], key='map_v')
    
    filtered = df[df['governorate'] == map_gov]
    if map_type != 'الكل':
        filtered = filtered[filtered['property_type'] == map_type]
    
    sample = filtered.sample(min(max_points, len(filtered)))
    
    if len(sample) > 0:
        center_lat = sample['latitude'].median()
        center_lon = sample['longitude'].median()
        
        m = folium.Map(location=[center_lat, center_lon], zoom_start=11,
                       tiles='CartoDB positron')
        
        if map_view == '🔥 خريطة حرارية':
            # Heatmap
            from folium.plugins import HeatMap
            heat_data = [[row['latitude'], row['longitude'], 
                          min(row['price'] / 1e7, 1)] for _, row in sample.iterrows()]
            HeatMap(heat_data, radius=15, blur=20, max_zoom=13).add_to(m)
        else:
            # Normal markers
            for _, row in sample.iterrows():
                color = 'red' if row['price'] > sample['price'].median() else 'blue'
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=5,
                    popup=f"<b>{row['property_type']}</b><br>💰 {row['price']:,.0f} EGP<br>📐 {row['size']:.0f} م²<br>📍 {row['district']}",
                    color=color, fill=True, fillOpacity=0.6
                ).add_to(m)
        
        folium_static(m, width=1200, height=600)
        
        st.markdown(f"""
        <div style="margin-top:1rem; padding:1rem; background:white; border-radius:10px;">
            <b>📊 الإحصائيات:</b> {len(sample)} عقار معروض | 
            🔴 غالي عن المتوسط | 🔵 أرخص من المتوسط
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("مفيش بيانات للعرض")


# ═══════════════════════════════════════════════════════════════
# TAB 4: MORTGAGE CALCULATOR
# ═══════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">🧮 حاسبة الرهن العقاري</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        property_price = st.number_input(
            "💰 سعر العقار (EGP)",
            min_value=500_000, max_value=100_000_000,
            value=5_000_000, step=100_000
        )
        down_pct = st.slider("📊 المقدم (%)", 5, 50, 20)
        years = st.slider("📅 عدد السنوات", 5, 30, 20)
        rate = st.slider("📈 سعر الفائدة السنوي (%)", 5.0, 25.0, 15.0, 0.5)
    
    with col2:
        down_payment = property_price * down_pct / 100
        loan_amount = property_price - down_payment
        monthly_rate = (rate / 100) / 12
        n_months = years * 12
        
        if monthly_rate > 0:
            monthly = loan_amount * (monthly_rate * (1 + monthly_rate) ** n_months) / ((1 + monthly_rate) ** n_months - 1)
        else:
            monthly = loan_amount / n_months
        
        total_paid = monthly * n_months
        total_interest = total_paid - loan_amount
        
        st.markdown(f"""
        <div class="result-card">
            <div style="font-size:1.1rem;">💵 القسط الشهري</div>
            <div class="price">{monthly:,.0f}</div>
            <div style="font-size:1.2rem;">جنيه مصري</div>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.metric("💰 المقدم", f"{down_payment:,.0f}")
            st.metric("📊 إجمالي الفوائد", f"{total_interest:,.0f}")
        with c2:
            st.metric("🏦 التمويل", f"{loan_amount:,.0f}")
            st.metric("💸 إجمالي المدفوع", f"{total_paid:,.0f}")
    
    st.markdown('<div class="section-header">📅 جدول الدفع (أول 12 شهر)</div>', unsafe_allow_html=True)
    
    schedule = []
    balance = loan_amount
    for month in range(1, min(13, n_months + 1)):
        interest = balance * monthly_rate
        principal = monthly - interest
        balance -= principal
        schedule.append({
            'الشهر': month,
            'القسط': f'{monthly:,.0f}',
            'الفوائد': f'{interest:,.0f}',
            'الأصل': f'{principal:,.0f}',
            'الرصيد المتبقي': f'{max(0, balance):,.0f}',
        })
    
    st.dataframe(pd.DataFrame(schedule), use_container_width=True, hide_index=True)
    
    # Pie chart
    fig = go.Figure(data=[go.Pie(
        labels=['المقدم', 'التمويل', 'الفوائد'],
        values=[down_payment, loan_amount, total_interest],
        hole=0.4,
        marker=dict(colors=['#667eea', '#764ba2', '#f5576c'])
    )])
    fig.update_layout(title='📊 توزيع التكاليف', height=400)
    st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════
# TAB 5: FEATURED PROPERTIES
# ═══════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-header">⭐ عقارات مميزة</div>', unsafe_allow_html=True)
    
    # فلاتر
    col1, col2 = st.columns(2)
    with col1:
        gov_filter = st.selectbox("المحافظة", ['الكل'] + list(df['governorate'].unique()), key='feat_gov')
    with col2:
        type_filter = st.selectbox("النوع", ['الكل'] + list(df['property_type'].unique()), key='feat_type')
    
    feat_df = df[df['is_premium'] == 1] if 'is_premium' in df.columns else df.head(20)
    
    if gov_filter != 'الكل':
        feat_df = feat_df[feat_df['governorate'] == gov_filter]
    if type_filter != 'الكل':
        feat_df = feat_df[feat_df['property_type'] == type_filter]
    
    feat_sample = feat_df.sample(min(12, len(feat_df))) if len(feat_df) > 0 else feat_df
    
    if len(feat_sample) > 0:
        cols = st.columns(3)
        for i, (_, row) in enumerate(feat_sample.iterrows()):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="metric-card" style="margin-bottom:1rem;">
                    <h3>{row['property_type']}</h3>
                    <div class="value" style="font-size:1.3rem;">{row['price']:,.0f} EGP</div>
                    <p style="color:#666; margin:0.5rem 0;">
                        📍 {row['district']}<br>
                        🏙️ {row['governorate']}<br>
                        📐 {row['size']:.0f} م² | 🛏️ {row['bedrooms']:.0f}BR | 🚿 {row['bathrooms']:.0f}BA
                    </p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("مفيش عقارات مميزة بالفلاتر دي")


# ═══════════════════════════════════════════════════════════════
# TAB 6: FAVORITES
# ═══════════════════════════════════════════════════════════════
with tab6:
    st.markdown('<div class="section-header">❤️ العقارات المفضلة</div>', unsafe_allow_html=True)
    
    favorites = get_favorites()
    
    if len(favorites) == 0:
        st.markdown("""
        <div style="text-align:center;padding:4rem 2rem;color:#999;">
            <div style="font-size:5rem;">💔</div>
            <h3 style="color:#667eea;">مفيش عقارات في المفضلة</h3>
            <p>اذهب لصفحة التوقع وأضف عقارات للمفضلة</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"### عندك {len(favorites)} عقار في المفضلة")
        
        cols = st.columns(3)
        for i, fav in enumerate(favorites):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="metric-card" style="margin-bottom:1rem;">
                    <h3>{fav['property_type']}</h3>
                    <div class="value" style="font-size:1.3rem;">{fav['price']:,.0f} EGP</div>
                    <p style="color:#666;margin:0.5rem 0;">
                        📍 {fav['district']}<br>
                        🏙️ {fav['governorate']}<br>
                        📐 {fav['size']:.0f} م² | 🛏️ {fav['bedrooms']:.0f}BR
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"🗑️ احذف", key=f"del_{i}", use_container_width=True):
                    remove_favorite(fav['id'])
                    st.rerun()

# ═══════════════════════════════════════════════════════════════
# TAB 7: ABOUT
# ═══════════════════════════════════════════════════════════════
with tab7:
    st.markdown('<div class="section-header">ℹ️ عن المشروع</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        ### 📊 البيانات
        
        | المقياس | القيمة |
        |---------|--------|
        | إعلانات | **{len(df):,}** |
        | محافظات | **{df['governorate'].nunique()}** |
        | أنواع عقارات | **{df['property_type'].nunique()}** |
        | مناطق | **{df['district'].nunique()}** |
        | كمبوندات | **{df['compound'].nunique()}** |
        
        ### 🎯 الموديل
        
        | المقياس | القيمة |
        |---------|--------|
        | الخوارزمية | **CatBoost** |
        | R² | **0.7061** |
        | MAPE | **40.52%** |
        | Features | **{len(features)}** |
        """)
    
    with col2:
        st.markdown("""
        ### 🛠️ التقنيات
        
        - **Python** + Streamlit
        - **CatBoost** + XGBoost + LightGBM
        - **Plotly** + Folium
        - **Pandas** + NumPy
        
        ### 📍 المحافظات المدعومة
        
        1. 🏙️ القاهرة
        2. 🏙️ الجيزة
        3. 🌊 الإسكندرية
        4. 🏖️ مطروح
        5. 🌊 البحر الأحمر
        6. 🚢 السويس
        """)
    
    # جدول المحافظات
    st.markdown('<div class="section-header">📊 إحصائيات المحافظات</div>', unsafe_allow_html=True)
    
    gov_stats = df.groupby('governorate').agg({
        'price': ['count', 'median'],
        'district': 'nunique',
        'compound': 'nunique',
    }).round(0)
    gov_stats.columns = ['إعلانات', 'متوسط السعر', 'مناطق', 'كمبوندات']
    st.dataframe(gov_stats, use_container_width=True)

# ═══════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<div style="text-align:center; color:#666; padding:2rem 0 1rem 0; margin-top:3rem; border-top:1px solid #e2e8f0;">
    <p>🏠 <b>Egypt Real Estate AI</b> | Built with ❤️ using CatBoost + Streamlit</p>
    <p style="font-size:0.85rem;">119,916 إعلان | 6 محافظات | R² = 0.7061</p>
</div>
""", unsafe_allow_html=True)
