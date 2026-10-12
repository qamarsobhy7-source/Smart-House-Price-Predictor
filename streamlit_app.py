"""
Egypt Real Estate AI - Clean Rebuild
Design: Nawy-inspired
Rules: No emojis | Full language separation
"""
import streamlit as st
import pandas as pd
import numpy as np
import json
import io
import sys
from pathlib import Path
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))

from nawy_theme import get_css, get_theme
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import HexColor
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

from predictor import (
    load_artifacts, get_category_values, validate_input,
    build_features, predict_with_confidence, format_price,
    calculate_roi, recommend_similar_properties,
)

st.set_page_config(
    page_title="Egypt Real Estate AI",
    layout="wide",
    initial_sidebar_state="collapsed",
)

_defaults = {
    "lang": "en", "dark": False, "favorites": [],
    "selected_features": [], "current_prediction": None,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

lang = st.session_state.lang
dark = st.session_state.dark

TEXTS = {
    "en": {
        "brand_prefix": "Egypt", "brand_suffix": "Real Estate AI",
        "hero_title": "Real Estate Price Estimator",
        "hero_sub": "Instant valuations for the Egyptian real estate market",
        "stat_accuracy": "Accuracy", "stat_error": "Avg Error",
        "stat_gov": "Governorates", "stat_listings": "Listings",
        "nav_lang": "AR",
        "theme_dark": "Dark", "theme_light": "Light",
        "section_types": "Browse by Property Type",
        "section_areas": "Popular Areas",
        "section_compounds": "Latest Compounds",
        "show_more": "Show More",
        "tab_estimator": "Price Estimator",
        "tab_market": "Market Analysis",
        "tab_mortgage": "Mortgage Calculator",
        "tab_compare": "Compare",
        "tab_favorites": "Favorites",
        "location": "Location", "details": "Details", "features": "Features",
        "governorate": "Governorate", "city": "City",
        "district": "District", "compound": "Compound",
        "no_compound": "None",
        "property_type": "Property Type",
        "town": "Town", "view": "View",
        "developer": "Developer", "seller_type": "Seller Type",
        "completion": "Completion Status",
        "seller_broker": "Broker", "seller_owner": "Owner", "seller_developer": "Developer",
        "comp_ready": "Ready", "comp_offplan": "Off-Plan", "comp_under": "Under Construction",
        "view_unknown": "No Specific View", "view_garden": "Garden View",
        "view_pool": "Pool View", "view_sea": "Sea View", "view_city": "City View",
        "view_street": "Street View", "view_lake": "Lake View",
        "export_favs": "Export Favorites", "import_favs": "Import Favorites",
        "export_help": "Download favorites as JSON file", "import_help": "Upload favorites from JSON file",
        "import_success": "Favorites imported successfully", "import_error": "Invalid file format",
        "comp_title": "Compare Properties",
        "comp_subtitle": "Add 2 to 4 properties and compare them side by side",
        "comp_add": "Add Property",
        "comp_clear": "Clear All",
        "comp_empty": "No properties to compare yet. Save favorites first.",
        "comp_property": "Property",
        "comp_price": "Price",
        "comp_size": "Size",
        "comp_bedrooms": "Bedrooms",
        "comp_bathrooms": "Bathrooms",
        "comp_location": "Location",
        "comp_type": "Type",
        "comp_ppm2": "Price / sqm",
        "comp_max": "Maximum 4 properties can be compared",
        "comp_need_two": "Need at least 2 properties to compare",
        "comp_title_col": "Feature",
        "size": "Size (sqm)", "bedrooms": "Bedrooms",
        "bathrooms": "Bathrooms", "floor": "Floor",
        "living_rooms": "Living Rooms", "kitchens": "Kitchens",
        "finishing": "Finishing", "furnished": "Furnished",
        "additional_features": "Additional Features",
        "select_features": "Select available features",
        "calculate": "Calculate Price",
        "calculating": "Calculating...",
        "result_title": "Estimated Price",
        "per_sqm": "Price per sqm",
        "confidence": "Confidence",
        "price_range": "Range",
        "vs_market": "vs. Market",
        "save": "Save", "saved": "Saved", "share": "Share",
        "whatsapp": "WhatsApp", "call": "Call", "pdf": "PDF Report",
        "above_market": "above market",
        "below_market": "below market",
        "at_market": "at market level",
        "empty_title": "No favorites yet",
        "empty_desc": "Save properties to see them here",
        "pt_apartment": "Apartments", "pt_villa": "Villas",
        "pt_duplex": "Duplexes", "pt_townhouse": "Townhouses",
        "pt_penthouse": "Penthouses", "pt_chalet": "Chalets",
        "fin_core": "Core & Shell", "fin_semi": "Semi Finished",
        "fin_finished": "Finished", "fin_super": "Super Lux",
        "fur_no": "Unfurnished", "fur_partly": "Partly Furnished",
        "fur_yes": "Furnished",
        "feat_garden": "Garden", "feat_pool": "Pool",
        "feat_garage": "Garage", "feat_security": "Security 24/7",
        "feat_gym": "Gym", "feat_elevator": "Elevator",
        "feat_balcony": "Balcony", "feat_view": "View",
        "feat_mall": "Mall", "feat_mosque": "Mosque",
        "feat_club": "Sports Club", "feat_sea": "Sea Front",
        "mortgage_loan": "Loan Amount (EGP)",
        "mortgage_rate": "Annual Interest Rate (%)",
        "mortgage_years": "Years",
        "mortgage_monthly": "Monthly Payment",
        "mortgage_total": "Total Payment",
        "mortgage_interest": "Total Interest",
        "footer_tagline": "AI-powered real estate valuation for Egypt",
        "footer_rights": "All rights reserved",
        "currency": "EGP",
    },
    "ar": {
        "brand_prefix": "الذكاء", "brand_suffix": "العقاري",
        "hero_title": "حاسبة أسعار العقارات",
        "hero_sub": "تقديرات فورية لسوق العقارات المصري",
        "stat_accuracy": "الدقة", "stat_error": "متوسط الخطأ",
        "stat_gov": "محافظة", "stat_listings": "إعلان",
        "nav_lang": "EN",
        "theme_dark": "داكن", "theme_light": "فاتح",
        "section_types": "تصفح حسب نوع العقار",
        "section_areas": "أشهر المناطق",
        "section_compounds": "أحدث الكمبوندات",
        "show_more": "أظهر المزيد",
        "tab_estimator": "حاسبة الأسعار",
        "tab_market": "تحليل السوق",
        "tab_mortgage": "حاسبة الرهن",
        "tab_compare": "مقارنة العقارات",
        "tab_favorites": "المفضلة",
        "location": "الموقع", "details": "التفاصيل", "features": "المميزات",
        "governorate": "المحافظة", "city": "المدينة",
        "district": "الحي", "compound": "كمبوند",
        "no_compound": "لا يوجد",
        "property_type": "نوع العقار",
        "town": "المنطقة", "view": "الإطلالة",
        "developer": "المطور", "seller_type": "نوع البائع",
        "completion": "حالة التسليم",
        "seller_broker": "وسيط", "seller_owner": "مالك", "seller_developer": "مطور",
        "comp_ready": "جاهز للاستلام", "comp_offplan": "على الخريطة", "comp_under": "تحت الإنشاء",
        "view_unknown": "بدون إطلالة محددة", "view_garden": "إطلالة حديقة",
        "view_pool": "إطلالة حمام سباحة", "view_sea": "إطلالة بحر", "view_city": "إطلالة مدينة",
        "view_street": "إطلالة شارع", "view_lake": "إطلالة بحيرة",
        "export_favs": "تصدير المفضلات", "import_favs": "استيراد المفضلات",
        "export_help": "حفظ المفضلات في ملف JSON", "import_help": "استرجاع المفضلات من ملف JSON",
        "import_success": "تم استيراد المفضلات", "import_error": "صيغة الملف غير صحيحة",
        "comp_title": "مقارنة العقارات",
        "comp_subtitle": "أضف 2 إلى 4 عقارات وقارنهم جنب بعض",
        "comp_add": "أضف عقار",
        "comp_clear": "مسح الكل",
        "comp_empty": "مفيش عقارات للمقارنة. احفظ مفضلات الأول.",
        "comp_property": "العقار",
        "comp_price": "السعر",
        "comp_size": "المساحة",
        "comp_bedrooms": "غرف النوم",
        "comp_bathrooms": "الحمامات",
        "comp_location": "الموقع",
        "comp_type": "النوع",
        "comp_ppm2": "سعر المتر",
        "comp_max": "أقصى عدد 4 عقارات للمقارنة",
        "comp_need_two": "محتاج عقارين على الأقل للمقارنة",
        "comp_title_col": "الخاصية",
        "size": "المساحة (م²)", "bedrooms": "غرف النوم",
        "bathrooms": "الحمامات", "floor": "الطابق",
        "living_rooms": "الصالونات", "kitchens": "المطابخ",
        "finishing": "التشطيب", "furnished": "الفرش",
        "additional_features": "مميزات إضافية",
        "select_features": "اختر المميزات المتاحة",
        "calculate": "احسب السعر",
        "calculating": "جاري الحساب...",
        "result_title": "السعر المتوقع",
        "per_sqm": "سعر المتر",
        "confidence": "نسبة الثقة",
        "price_range": "النطاق السعري",
        "vs_market": "مقارنة بالسوق",
        "save": "حفظ", "saved": "تم الحفظ", "share": "مشاركة",
        "whatsapp": "واتساب", "call": "اتصال", "pdf": "تقرير PDF",
        "above_market": "أعلى من السوق",
        "below_market": "أقل من السوق",
        "at_market": "في مستوى السوق",
        "empty_title": "لا توجد مفضلات بعد",
        "empty_desc": "احفظ العقارات لتظهر هنا",
        "pt_apartment": "شقق", "pt_villa": "فيلل",
        "pt_duplex": "دوبلكس", "pt_townhouse": "تاون هاوس",
        "pt_penthouse": "بنتهاوس", "pt_chalet": "شاليهات",
        "fin_core": "طوب أحمر", "fin_semi": "نصف تشطيب",
        "fin_finished": "تشطيب كامل", "fin_super": "سوبر لوكس",
        "fur_no": "غير مفروش", "fur_partly": "مفروش جزئياً",
        "fur_yes": "مفروش",
        "feat_garden": "حديقة", "feat_pool": "حمام سباحة",
        "feat_garage": "جراج", "feat_security": "أمن 24/7",
        "feat_gym": "جيم", "feat_elevator": "أسانسير",
        "feat_balcony": "بلكونة", "feat_view": "إطلالة",
        "feat_mall": "مول تجاري", "feat_mosque": "مسجد",
        "feat_club": "نادي رياضي", "feat_sea": "على البحر",
        "mortgage_loan": "مبلغ التمويل (جنيه)",
        "mortgage_rate": "سعر الفائدة السنوي (%)",
        "mortgage_years": "عدد السنوات",
        "mortgage_monthly": "القسط الشهري",
        "mortgage_total": "إجمالي المدفوع",
        "mortgage_interest": "إجمالي الفوائد",
        "footer_tagline": "تقدير أسعار العقارات بالذكاء الاصطناعي لمصر",
        "footer_rights": "جميع الحقوق محفوظة",
        "currency": "ج.م",
    },
}
T = TEXTS[lang]

st.markdown(get_css(dark=dark, lang=lang), unsafe_allow_html=True)

@st.cache_resource
def _load_model():
    return load_artifacts()

@st.cache_data
def _load_df():
    return pd.read_csv(BASE / "data" / "processed" / "FINAL_DATASET_v9.csv")

@st.cache_data
def _load_hierarchy():
    with open(BASE / "data" / "egypt_hierarchy.json", "r", encoding="utf-8") as f:
        return json.load(f)

try:
    model, metadata, mappings = _load_model()
    df = _load_df()
    hierarchy = _load_hierarchy()
except Exception as e:
    st.error(f"Load error: {e}")
    st.stop()

_AR_NAMES = {
    # ═══ المدن (Cities) ═══
    "New Cairo City": "القاهرة الجديدة", "New Cairo": "القاهرة الجديدة",
    "El Khalifa": "الخليفة", "New Capital City": "العاصمة الإدارية الجديدة",
    "New Capital": "العاصمة الإدارية", "New Administrative Capital": "العاصمة الإدارية",
    "Sheikh Zayed City": "مدينة الشيخ زايد", "Sheikh Zayed": "الشيخ زايد",
    "6 October City": "مدينة 6 أكتوبر", "6th of October": "6 أكتوبر",
    "6th October City": "مدينة 6 أكتوبر", "6 October": "6 أكتوبر",
    "Hay El Haram": "حي الهرم", "El Haram": "الهرم", "Haram": "الهرم",
    "Al Haram": "الهرم", "Hay Helwan": "حي حلوان", "Helwan": "حلوان",
    "Alexandria Compounds": "كمبوندات الإسكندرية",
    "Alexandria": "الإسكندرية",
    "Hay Sharq": "الحي الشرقي", "Hay Wasat": "الحي الأوسط",
    "Hay Gharb": "الحي الغربي", "Hay El Gomrok": "حي الجمرك",
    "Cairo": "القاهرة", "Giza": "الجيزة", "Hurghada": "الغردقة",
    "Matrouh": "مطروح", "Marsa Matrouh": "مرسى مطروح",
    "Suez": "السويس", "Ismailia": "الإسماعيلية",
    "Port Said": "بورسعيد", "Damietta": "دمياط",
    "Tanta": "طنطا", "Mansoura": "المنصورة",
    "Zagazig": "الزقازيق", "Damanhour": "دمنهور",
    "Aswan": "أسوان", "Luxor": "الأقصر",
    "Sohag": "سوهاج", "Qena": "قنا",
    "Beni Suef": "بني سويف", "Fayoum": "الفيوم",
    "Minya": "المنيا", "Asyut": "أسيوط",
    "Sharm El Sheikh": "شرم الشيخ",
    "Dahab": "دهب", "Nuweiba": "نويبع",
    "El Tor": "الطور", "Ras Sedr": "رأس سدر",
    "Al Arish": "العريش", "Rafah": "رفح",
    "Sheikh Zowayed": "الشيخ زويد",

    # ═══ الأحياء (Districts) - القاهرة ═══
    "The 5th Settlement": "التجمع الخامس", "5th Settlement": "التجمع الخامس",
    "The First Settlement": "التجمع الأول", "First Settlement": "التجمع الأول",
    "The Third Settlement": "التجمع الثالث", "Third Settlement": "التجمع الثالث",
    "El Katameya": "القطامية", "Katameya": "القطامية",
    "Al Rehab": "الرحاب", "Rehab": "الرحاب",
    "Madinaty": "مدينتي", "Al Shorouk": "الشروق",
    "Shorouk City": "مدينة الشروق", "Shorouk": "الشروق",
    "Nasr City": "مدينة نصر", "Heliopolis": "مصر الجديدة",
    "New Heliopolis": "هليوبوليس الجديدة",
    "Maadi": "المعادي", "Zamalek": "الزمالك",
    "Downtown": "وسط البلد", "Mohandessin": "المهندسين",
    "Dokki": "الدقي", "Agouza": "العجوزة",
    "Al Agouza": "العجوزة", "Abdeen": "عابدين",
    "Hay El Zaytoun": "حي الزيتون", "El Zaytoun": "الزيتون",
    "Garden City": "جاردن سيتي", "Hay El Manial": "حي المنيل",
    "El Manial": "المنيل", "Al Manial": "المنيل",
    "Al Salam City": "مدينة السلام", "Salam City": "مدينة السلام",
    "Al Abageyah": "الأباجية", "Al Khalifa": "الخليفة",
    "Shubra": "شبرا", "Shubra El Kheima": "شبرا الخيمة",
    "Matariya": "المطرية", "Ain Shams": "عين شمس",
    "Abbasiya": "العباسية", "Roxy": "روكسي",
    "Sheraton": "شيراتون", "Almaza": "الماظة",
    "Ard El Golf": "أرض الجولف", "Korba": "الكوربة",
    "Nozha": "النزهة", "El Nozha": "النزهة",
    "New Nozha": "النزهة الجديدة",
    "Marg": "المرج", "El Marg": "المرج",
    "Alf Maskan": "ألف مسكن", "Gesr El Suez": "جسر السويس",
    "Ezbet El Nakhl": "عزبة النخل",
    "Badr": "بدر", "Badr City": "مدينة بدر",
    "Obour": "العبور", "Obour City": "مدينة العبور",
    "Al Obour": "العبور",
    "New Cairo Compounds": "كمبوندات القاهرة الجديدة",
    "New Capital Compounds": "كمبوندات العاصمة الإدارية",
    "New Cairo Districts": "أحياء القاهرة الجديدة",
    "DeJoya 4": "ديچويا 4", "DeJoya": "ديچويا",
    "Nile Corniche": "كورنيش النيل",
    "Nile Corniche St.": "كورنيش النيل",
    "Corniche El Nil": "كورنيش النيل",

    # ═══ الجيزة ═══
    "Sheikh Zayed Compounds": "كمبوندات الشيخ زايد",
    "12th District": "الحي الثاني عشر",
    "6 October Compounds": "كمبوندات 6 أكتوبر",
    "Hadayek October": "حدائق أكتوبر",
    "Hadayek El Ahram": "حدائق الأهرام",
    "Hadayek Al Ahram": "حدائق الأهرام",
    "Faisal": "فيصل", "Imbaba": "إمبابة",
    "Boulaq": "بولاق", "Bulaq": "بولاق",
    "Dahshur": "دهشور", "Saqqara": "سقارة",
    "Awsim": "أوسيم", "Kerdasa": "كرداسة",
    "Abu Rawash": "أبو رواش",
    "Al Lebeny Axis": "محور اللبيني",

    # ═══ الإسكندرية ═══
    "Sidi Gaber": "سيدي جابر", "Smouha": "سموحة",
    "Stanley": "ستانلي", "Miami": "ميامي",
    "Sidi Bishr": "سيدي بشر", "Montazah": "المنتزه",
    "Maamoura": "المعمورة", "Abu Qir": "أبو قير",
    "Raml Station": "محطة الرمل", "Anfushi": "الأنفوشي",
    "Manshiya": "المنشية", "Attarin": "العطارين",
    "Labban": "اللبان", "Gomrok": "الجمرك",
    "Agami": "العجمي", "Borg El Arab": "برج العرب",
    "King Mariout": "كينج مريوط",
    "Janaklees": "جناكليس", "Camp Chezar": "كامب شيزار",
    "Ibrahimia": "الإبراهيمية", "Sawary": "السواري",
    "Palm Hills": "بالم هيلز",

    # ═══ الساحل الشمالي ═══
    "North Coast": "الساحل الشمالي",
    "Marina": "مارينا", "Marina El Alamein": "مارينا العلمين",
    "New Alamein": "العلمين الجديدة",
    "Alamein": "العلمين", "El Alamein": "العلمين",
    "Ras El Hekma": "رأس الحكمة",
    "Sidi Abdel Rahman": "سيدي عبد الرحمن",
    "Hacienda Bay": "هاسيندا باي",
    "Marassi": "مراسي", "Fouka Bay": "فوكا باي",
    "Telal": "تلال", "Silver Sands": "سيلفر ساندز",
    "Diplo": "دبلو", "Amwaj": "أمواج",

    # ═══ العين السخنة ═══
    "Ain Sokhna": "العين السخنة", "Al Sokhna": "العين السخنة",
    "Sokhna": "السخنة", "Zafarana": "الزعفرانة",
    "Stella": "ستيلا", "Porto Sokhna": "بورتو السخنة",
    "Jefaira": "جفيرا", "Il Monte Galala": "إل مونتي جالالا",

    # ═══ البحر الأحمر ═══
    "El Gouna": "الجونة", "Sahl Hasheesh": "سهل حشيش",
    "Makadi": "مكادي", "Makadi Heights": "مكادي هايتس",
    "Marsa Alam": "مرسى علم", "Soma Bay": "سوما باي",
    "Safaga": "سفاجا", "Quseir": "القصير",

    # ═══ الكمبوندات الشائعة ═══
    "Mountain View": "ماونتن فيو",
    "Mountain View 1.1": "ماونتن فيو 1.1",
    "Mountain View Ras El Hekma": "ماونتن فيو رأس الحكمة",
    "Mountain View iCity": "ماونتن فيو آي سيتي",
    "Sodic": "سوديك", "SODIC": "سوديك",
    "Hyde Park": "هايد بارك",
    "The Lakes": "ذا ليكس", "Lake View": "ليك فيو",
    "Lake West": "ليك ويست", "Villette": "فيلlette",
    "Mivida": "ميفيدا", "Uptown Cairo": "أبتاون القاهرة",
    "Cairo Festival City": "كايرو فيستيفال سيتي",
    "Mall of Egypt": "مول مصر",
    "Allegria": "أليجريا", "Swan Lake": "سوان ليك",
    "Hacienda": "هاسيندا",
    "Home Residence": "هوم ريزيدنس",
    "Eastown": "إيستاون", "Westown": "ويستاون",
    "New Giza": "نيو جيزة", "Lotus": "لوتس",
    "Al Maqsad": "المقصد", "Village West": "فيلدج ويست",
    "Lake West 2": "ليك ويست 2",
    "Bloomfields": "بلومفيلدز",
    "Palm Hills October": "بالم هيلز أكتوبر",
    "Palm Hills New Cairo": "بالم هيلز القاهرة الجديدة",
    "Zed East": "زيد إيست", "Zed West": "زيد ويست",
    "Zed Towers": "زيد تاورز",
    "Mountain View Hyde Park": "ماونتن فيو هايد بارك",
    "Palm Valley": "بالم فالي",
    "Cairo Gate": "كايرو جيت",
    "Madinaty": "مدينتي",
    "Rehab": "الرحاب",
    "R8": "R8", "RI8 New Capital": "RI8 العاصمة",
    "The Waterway": "ذا ووتر واي",
    "Sarai": "سراي", "Taj City": "تاج سيتي",
    "La Vista": "لافيستا", "La Vista City": "لافيستا سيتي",
    "Ora": "أورا", "Ora Developers": "أورا للتطوير",

    # ═══ المطورين ═══
    "Sodic": "سوديك", "Palm Hills": "بالم هيلز",
    "Mountain View": "ماونتن فيو",
    "Emaar": "إعمار", "Misr Italia": "مصر إيطاليا",
    "Ora Developers": "أورا للتطوير",
    "Hyde Park": "هايد بارك",
    "Tatweer Misr": "تطوير مصر",
    "MNHD": "مدينة نصر للإسكان",
    "Amer Group": "عامر جروب",
    "Orascom": "أوراسكوم",
    "Orascom Development": "أوراسكوم للتطوير",
    "Al Futtaim": "الفطيم",
    "Al Ahly Sabbour": "الأهلي صبور",
    "Iwan": "إيوان",
    "Al Marasem": "المراسم",
    "New Plan": "نيو بلان",
    "Al Attal": "العتال",

    # ═══ كلمات عامة ═══
    "Compound": "كمبوند", "Compounds": "كمبوندات",
    "City": "مدينة", "District": "منطقة", "Area": "منطقة",
    "Village": "قرية", "Heights": "هايتس",
    "Gardens": "جاردنز", "Park": "بارك",
    "Plaza": "بلازا", "Tower": "برج", "Towers": "أبراج",
    "Bay": "باي", "View": "فيو", "Lake": "ليك",
    "West": "ويست", "East": "إيست",
    "North": "شمال", "South": "جنوب",
    "New": "جديد", "Old": "قديم",
    "St.": "شارع", "Street": "شارع",
    "Square": "ميدان", "Midan": "ميدان",
    "Axis": "محور", "Road": "طريق",
    "Desert Road": "الطريق الصحراوي",
    "Cairo Alexandria Desert Road": "طريق مصر إسكندرية الصحراوي",
}


def ar_name(name):
    """ترجمة الاسم من الإنجليزي للعربي"""
    if not name:
        return name
    name_str = str(name).strip()
    
    # 1. بحث مباشر
    if name_str in _AR_NAMES:
        return _AR_NAMES[name_str]
    
    # 2. بحث بدون حساسية
    lower = name_str.lower()
    for k, v in _AR_NAMES.items():
        if k.lower() == lower:
            return v
    
    # 3. تجريب بعض الاستبدالات الجزئية
    # "Al X Compound" -> "كمبوند الـ X"
    replacements = [
        (" Compounds", " كمبوندات"),
        (" Compound", " كمبوند"),
        (" City", " مدينة"),
        (" District", " منطقة"),
        (" Area", " منطقة"),
        (" Village", " قرية"),
        (" Heights", " هايتس"),
        (" Gardens", " جاردنز"),
        (" Park", " بارك"),
        (" Plaza", " بلازا"),
        (" Towers", " أبراج"),
        (" Tower", " برج"),
        (" West", " ويست"),
        (" East", " إيست"),
        (" Bay", " باي"),
        (" View", " فيو"),
        (" Lake", " ليك"),
        (" St.", " شارع"),
        (" Street", " شارع"),
        (" Square", " ميدان"),
        (" Axis", " محور"),
        (" Road", " طريق"),
    ]
    result = name_str
    for en_s, ar_s in replacements:
        if result.endswith(en_s):
            result = result[:-len(en_s)] + ar_s
            break
    
    # بادئات
    prefixes = [
        ("Al ", "ال"),
        ("El ", "ال"),
        ("Hay ", "حي "),
        ("New ", "جديد "),
        ("Old ", "قديم "),
        ("North ", "شمال "),
        ("South ", "جنوب "),
    ]
    for en_p, ar_p in prefixes:
        if result.startswith(en_p):
            result = ar_p + result[len(en_p):]
            break
    
    return result


def nm(obj):
    """الحصول على الاسم باللغة الحالية"""
    if obj is None:
        return ""
    if isinstance(obj, str):
        return ar_name(obj) if lang == "ar" else obj
    
    en = obj.get("en", "")
    ar_val = obj.get("ar", "")
    
    if lang == "ar":
        # لو الـ ar فاضي أو نفسه الـ en → نستخدم القاموس
        if not ar_val or ar_val == en or ar_val.strip() == "":
            return ar_name(en)
        # لو الـ ar مختلف فعلاً → نستخدمه
        return ar_val
    
    return en




# ═══ PROPERTY IMAGES ═══
_PROPERTY_IMAGES = {
    "Apartment": [
        "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1484154218962-a197022b5858?w=800&h=500&fit=crop",
    ],
    "Villa": [
        "https://images.unsplash.com/photo-1613977257363-707ba9348227?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=800&h=500&fit=crop",
    ],
    "Townhouse": [
        "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1600566753086-00f18fb6b3ea?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=800&h=500&fit=crop",
    ],
    "Duplex": [
        "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1600566753086-00f18fb6b3ea?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800&h=500&fit=crop",
    ],
    "Penthouse": [
        "https://images.unsplash.com/photo-1600566753086-00f18fb6b3ea?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1567496898669-ee935f5f647a?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=800&h=500&fit=crop",
    ],
    "Chalet": [
        "https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1582268611958-ebfd161ef9cf?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800&h=500&fit=crop",
        "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800&h=500&fit=crop",
    ],
}


def render_property_gallery(property_type, district_name, price_text, key_prefix="gal"):
    """عرض معرض صور للعقار"""
    images = _PROPERTY_IMAGES.get(property_type, _PROPERTY_IMAGES["Apartment"])
    
    if f"{key_prefix}_idx" not in st.session_state:
        st.session_state[f"{key_prefix}_idx"] = 0
    
    current_idx = st.session_state[f"{key_prefix}_idx"]
    current_img = images[current_idx]
    
    gallery_title = "Property Gallery" if lang == "en" else "صور العقار"
    gallery_note = "Sample images for reference" if lang == "en" else "صور توضيحية للمرجعية"
    st.markdown(
        '<div class="section-title" style="font-size:20px;margin:24px 0 4px;">' + gallery_title + '</div>'
        '<div style="color:#64748B;font-size:12px;margin-bottom:16px;font-style:italic;">' + gallery_note + '</div>',
        unsafe_allow_html=True,
    )
    
    # الصورة الرئيسية
    main_html = (
        '<div class="gallery-main">'
        '<img src="' + current_img + '" alt="Property">'
        '<div class="gallery-badge">' + str(current_idx + 1) + ' / ' + str(len(images)) + '</div>'
        '</div>'
    )
    st.markdown(main_html, unsafe_allow_html=True)
    
    # Thumbnails
    thumb_cols = st.columns(len(images))
    for i, img in enumerate(images):
        with thumb_cols[i]:
            if st.button(
                str(i + 1),
                key=key_prefix + "_thumb_" + str(i),
                use_container_width=True,
                type="primary" if i == current_idx else "secondary",
            ):
                st.session_state[f"{key_prefix}_idx"] = i
                st.rerun()




# ═══ NEIGHBORHOOD INFO ═══
def get_neighborhood_info(district_name_en, governorate_en):
    """معلومات تقديرية عن الحي حسب المنطقة"""
    
    # معلومات مخصصة لبعض المناطق الشهيرة
    DISTRICT_SPECIFIC = {
        "The 5th Settlement": {
            "schools": [("Cairo English School", "مدرسة القاهرة الإنجليزية", 1.5),
                       ("British International School", "المدرسة البريطانية الدولية", 2.8)],
            "hospitals": [("Al Salam International Hospital", "مستشفى السلام الدولي", 1.2),
                         ("Cleopatra Hospital", "مستشفى كليوباترا", 2.1)],
            "transport": [("Metro Station", "محطة مترو", 2.4), ("Bus Stop", "موقف أتوبيس", 0.6)],
            "shopping": [("Downtown Mall", "داون تاون مول", 1.8), ("Point 90 Mall", "بوينت 90 مول", 2.5)],
            "restaurants": [("Local Egyptian", "مطعم مصري", 0.5), ("Italian", "مطعم إيطالي", 1.0)],
        },
        "Sheikh Zayed Compounds": {
            "schools": [("Beverly Hills Schools", "مدارس بيفرلي هيلز", 1.8),
                       ("American International School", "المدرسة الأمريكية الدولية", 3.2)],
            "hospitals": [("Dar Al Fouad Hospital", "مستشفى دار الفؤاد", 4.5),
                         ("Sheikh Zayed Specialized", "مستشفى الشيخ زايد التخصصي", 2.0)],
            "transport": [("Bus Stop", "موقف أتوبيس", 0.5), ("Taxi Stand", "موقف تاكسي", 0.3)],
            "shopping": [("Mall of Arabia", "مول العرب", 4.2), ("Mall of Egypt", "مول مصر", 8.5)],
            "restaurants": [("Local", "مطعم محلي", 0.4), ("Cafe", "كافيه", 0.7)],
        },
        "Hadayek El Ahram": {
            "schools": [("Modern English School", "المدرسة الإنجليزية الحديثة", 2.0),
                       ("Dream International School", "مدرسة دريم الدولية", 3.5)],
            "hospitals": [("Haram Hospital", "مستشفى الهرم", 3.8),
                         ("Al Salam Hospital", "مستشفى السلام", 5.2)],
            "transport": [("Bus Stop", "موقف أتوبيس", 0.6), ("Microbus", "ميكروباص", 0.3)],
            "shopping": [("Mall of Egypt", "مول مصر", 5.5), ("Local Market", "سوق محلي", 0.8)],
            "restaurants": [("Local Egyptian", "مطعم مصري", 0.5)],
        },
        "El Katameya": {
            "schools": [("British International School", "المدرسة البريطانية الدولية", 2.5),
                       ("Cairo British School", "مدرسة القاهرة البريطانية", 3.0)],
            "hospitals": [("Cleopatra Hospital", "مستشفى كليوباترا", 3.5)],
            "transport": [("Bus Stop", "موقف أتوبيس", 0.8), ("Taxi", "تاكسي", 0.4)],
            "shopping": [("Point 90 Mall", "بوينت 90 مول", 2.0)],
            "restaurants": [("Local", "مطعم محلي", 0.6), ("Cafe", "كافيه", 0.9)],
        },
    }
    
    # لو المنطقة ليها معلومات مخصصة
    if district_name_en in DISTRICT_SPECIFIC:
        specific = DISTRICT_SPECIFIC[district_name_en]
        return {
            "schools": [(n, a, "School", d) for n, a, d in specific["schools"]],
            "hospitals": [(n, a, "Hospital", d) for n, a, d in specific["hospitals"]],
            "transport": [(n, a, "Transport", d) for n, a, d in specific["transport"]],
            "shopping": [(n, a, "Mall", d) for n, a, d in specific["shopping"]],
            "restaurants": [(n, a, "Restaurant", d) for n, a, d in specific["restaurants"]],
        }
    
    # قوالب عامة حسب المحافظة
    info = {"schools": [], "hospitals": [], "transport": [], "shopping": [], "restaurants": []}
    
    if governorate_en == "Cairo":
        info["schools"] = [
            ("Cairo English School", "مدرسة القاهرة الإنجليزية", "International", 2.1),
            ("British International School", "المدرسة البريطانية الدولية", "British", 3.4),
            ("Modern English School", "المدرسة الإنجليزية الحديثة", "Private", 1.8),
        ]
        info["hospitals"] = [
            ("Cairo Medical Center", "مركز القاهرة الطبي", "Hospital", 1.5),
            ("Cleopatra Hospital", "مستشفى كليوباترا", "Hospital", 2.7),
        ]
        info["transport"] = [
            ("Metro Station", "محطة مترو", "Metro", 1.2),
            ("Bus Stop", "موقف أتوبيس", "Bus", 0.4),
        ]
        info["shopping"] = [
            ("Mall of Egypt", "مول مصر", "Mall", 12.0),
            ("City Stars Mall", "سيتي ستارز", "Mall", 8.5),
        ]
        info["restaurants"] = [
            ("Local Restaurant", "مطعم محلي", "Egyptian", 0.6),
            ("Italian Restaurant", "مطعم إيطالي", "Italian", 1.1),
        ]
    elif governorate_en == "Giza":
        info["schools"] = [
            ("Giza International School", "مدرسة الجيزة الدولية", "International", 2.5),
            ("Nile English School", "مدرسة النيل الإنجليزية", "Private", 1.9),
        ]
        info["hospitals"] = [
            ("Giza Hospital", "مستشفى الجيزة", "Hospital", 2.0),
            ("Dar Al Fouad Hospital", "مستشفى دار الفؤاد", "Hospital", 5.0),
        ]
        info["transport"] = [
            ("Metro Station", "محطة مترو", "Metro", 1.8),
            ("Bus Stop", "موقف أتوبيس", "Bus", 0.5),
        ]
        info["shopping"] = [
            ("Mall of Arabia", "مول العرب", "Mall", 5.0),
            ("Local Market", "سوق محلي", "Market", 0.7),
        ]
        info["restaurants"] = [
            ("Local Restaurant", "مطعم محلي", "Egyptian", 0.4),
        ]
    elif governorate_en == "Alexandria":
        info["schools"] = [
            ("Alexandria International School", "مدرسة الإسكندرية الدولية", "International", 2.3),
        ]
        info["hospitals"] = [
            ("Alexandria University Hospital", "مستشفى جامعة الإسكندرية", "University", 1.5),
            ("Smouha Hospital", "مستشفى سموحة", "Hospital", 2.8),
        ]
        info["transport"] = [
            ("Tram Station", "محطة ترام", "Tram", 0.6),
            ("Bus Stop", "موقف أتوبيس", "Bus", 0.3),
        ]
        info["shopping"] = [
            ("City Center Alexandria", "سيتي سنتر الإسكندرية", "Mall", 4.5),
        ]
        info["restaurants"] = [
            ("Seafood Restaurant", "مطعم أسماك", "Seafood", 0.8),
        ]
    else:
        info["schools"] = [("International School", "مدرسة دولية", "International", 3.0)]
        info["hospitals"] = [("General Hospital", "مستشفى عام", "General", 2.5)]
        info["transport"] = [("Bus Stop", "موقف أتوبيس", "Bus", 0.6)]
        info["shopping"] = [("Local Market", "سوق محلي", "Market", 0.5)]
        info["restaurants"] = [("Local Restaurant", "مطعم محلي", "Egyptian", 0.4)]
    
    return info


def render_neighborhood_section(district_name_en, governorate_en):
    """عرض معلومات الحي"""
    info = get_neighborhood_info(district_name_en, governorate_en)
    
    title = "Neighborhood Insights" if lang == "en" else "معلومات الحي"
    subtitle = ("What's around " + district_name_en) if lang == "en" else ("ما يحيط بـ " + nm({"en": district_name_en, "ar": district_name_en}))
    note = "Estimated data - actual distances may vary" if lang == "en" else "بيانات تقديرية - المسافات الفعلية قد تختلف"
    
    st.markdown(
        '<div class="section-title" style="font-size:20px;margin:24px 0 4px;">' + title + '</div>'
        '<div style="color:#64748B;font-size:13px;margin-bottom:4px;">' + subtitle + '</div>'
        '<div style="color:#94A3B8;font-size:11px;margin-bottom:20px;font-style:italic;">' + note + '</div>',
        unsafe_allow_html=True,
    )
    
    categories = [
        ("schools", "Schools" if lang == "en" else "مدارس", "SCH"),
        ("hospitals", "Hospitals" if lang == "en" else "مستشفيات", "HOS"),
        ("transport", "Transport" if lang == "en" else "مواصلات", "TRA"),
        ("shopping", "Shopping" if lang == "en" else "تسوق", "SHO"),
        ("restaurants", "Restaurants" if lang == "en" else "مطاعم", "RES"),
    ]
    
    for cat_key, cat_title, cat_icon in categories:
        items = info.get(cat_key, [])
        if not items:
            continue
        
        cols = st.columns(len(items))
        for i, item in enumerate(items):
            with cols[i]:
                name_en, name_ar, category, distance = item
                item_name = name_en if lang == "en" else name_ar
                distance_text = f"{distance} km" if lang == "en" else f"{distance} كم"
                
                card_html = (
                    '<div class="neighborhood-card">'
                    '<div class="neighborhood-header">'
                    '<span class="neighborhood-icon">' + cat_icon + '</span>'
                    '<span class="neighborhood-distance">' + distance_text + '</span>'
                    '</div>'
                    '<div class="neighborhood-name">' + item_name + '</div>'
                    '<div class="neighborhood-cat">' + category + '</div>'
                    '</div>'
                )
                st.markdown(card_html, unsafe_allow_html=True)




def generate_pdf_report(pred_data, lang="en"):
    """توليد تقرير PDF كامل"""
    if not PDF_AVAILABLE:
        return None
    
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    
    # الهيدر
    primary = HexColor("#0066FF")
    dark = HexColor("#0A0F1C")
    muted = HexColor("#64748B")
    
    c.setFillColor(primary)
    c.rect(0, h - 90, w, 90, fill=1, stroke=0)
    
    c.setFillColor(HexColor("#FFFFFF"))
    c.setFont("Helvetica-Bold", 24)
    c.drawString(40, h - 50, "Egypt Real Estate AI")
    c.setFont("Helvetica", 11)
    c.drawString(40, h - 72, "Property Valuation Report" if lang == "en" else "تقرير تقييم عقار")
    
    y = h - 130
    
    # السعر المتوقع
    c.setFillColor(HexColor("#EBF2FF"))
    c.rect(40, y - 90, w - 80, 90, fill=1, stroke=0)
    
    c.setFillColor(primary)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(60, y - 25, "ESTIMATED PRICE" if lang == "en" else "السعر المتوقع")
    
    c.setFillColor(dark)
    c.setFont("Helvetica-Bold", 32)
    price_text = f"{pred_data.get('price', 0):,.0f} EGP"
    c.drawString(60, y - 65, price_text)
    
    c.setFillColor(muted)
    c.setFont("Helvetica", 11)
    ppm2 = pred_data.get("ppm2", 0)
    c.drawString(60, y - 82, f"Price per sqm: {ppm2:,.0f} EGP")
    
    y -= 130
    
    # تفاصيل العقار
    c.setFillColor(dark)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, y, "Property Details" if lang == "en" else "تفاصيل العقار")
    y -= 25
    
    details = [
        ("Property Type", pred_data.get("property_type", "-")),
        ("Governorate", pred_data.get("governorate", "-")),
        ("District", pred_data.get("district", "-")),
        ("Size", f"{pred_data.get('size', 0):.0f} sqm"),
        ("Bedrooms", str(pred_data.get("bedrooms", 0))),
        ("Bathrooms", str(pred_data.get("bathrooms", 0))),
    ]
    
    c.setFont("Helvetica", 11)
    c.setFillColor(dark)
    for label, value in details:
        c.setFillColor(muted)
        c.drawString(60, y, label + ":")
        c.setFillColor(dark)
        c.drawString(200, y, str(value))
        y -= 20
    
    y -= 20
    
    # Investment Analysis
    c.setFillColor(dark)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, y, "Investment Analysis" if lang == "en" else "تحليل الاستثمار")
    y -= 25
    
    price = pred_data.get("price", 0)
    annual_rent = price * 0.055
    monthly_rent = annual_rent / 12
    annual_yield = (annual_rent / price) * 100 if price else 0
    payback = price / annual_rent if annual_rent else 0
    future_5y = price * (1.08 ** 5)
    
    inv_details = [
        ("Monthly Rent", f"{monthly_rent:,.0f} EGP"),
        ("Annual Yield", f"{annual_yield:.2f}%"),
        ("Payback Period", f"{payback:.1f} years"),
        ("5Y Future Value", f"{future_5y/1e6:.2f}M EGP"),
    ]
    
    c.setFont("Helvetica", 11)
    for label, value in inv_details:
        c.setFillColor(muted)
        c.drawString(60, y, label + ":")
        c.setFillColor(dark)
        c.drawString(200, y, value)
        y -= 20
    
    # الفوتر
    c.setFillColor(muted)
    c.setFont("Helvetica", 8)
    c.drawString(40, 40, "Egypt Real Estate AI - AI-powered valuation")
    c.drawString(40, 28, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    c.save()
    buf.seek(0)
    return buf.getvalue()


# ═══ NAVBAR ═══
nav1, nav2, nav3 = st.columns([6, 1, 1])
with nav1:
    st.markdown(
        f'<div class="navbar-logo">{T["brand_prefix"]} <span>{T["brand_suffix"]}</span></div>',
        unsafe_allow_html=True,
    )
with nav2:
    if st.button(T["nav_lang"], key="lang_btn"):
        st.session_state.lang = "ar" if lang == "en" else "en"
        st.rerun()
with nav3:
    theme_label = T["theme_light"] if dark else T["theme_dark"]
    if st.button(theme_label, key="theme_btn"):
        st.session_state.dark = not dark
        st.rerun()

# ═══ HERO ═══
metrics = metadata["metrics"]
training = metadata["training_info"]
n_gov = sum(1 for g in hierarchy["governorates"] if g["listings"] > 0)

st.markdown(
    '<div class="hero">'
    '<div class="hero-title">' + T["hero_title"] + '</div>'
    '<div class="hero-subtitle">' + T["hero_sub"] + '</div>'
    '<div class="hero-stats">'
    '<div class="hero-stat"><div class="hero-stat-value">' + f'{metrics["r2"]:.4f}' + '</div><div class="hero-stat-label">' + T["stat_accuracy"] + '</div></div>'
    '<div class="hero-stat"><div class="hero-stat-value">' + f'{metrics["mape"]:.1f}%' + '</div><div class="hero-stat-label">' + T["stat_error"] + '</div></div>'
    '<div class="hero-stat"><div class="hero-stat-value">' + str(n_gov) + '</div><div class="hero-stat-label">' + T["stat_gov"] + '</div></div>'
    '<div class="hero-stat"><div class="hero-stat-value">' + f'{training["n_total"]:,}' + '</div><div class="hero-stat-label">' + T["stat_listings"] + '</div></div>'
    '</div></div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="content-area">', unsafe_allow_html=True)

# ═══ PROPERTY TYPES ═══
st.markdown(
    '<div class="section-head">'
    '<div class="section-title">' + T["section_types"] + '</div>'
    '<a class="section-link">' + T["show_more"] + '</a>'
    '</div>',
    unsafe_allow_html=True,
)

ptype_items = [
    (T["pt_apartment"], "45,200", "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=400&h=280&fit=crop"),
    (T["pt_villa"], "8,500", "https://images.unsplash.com/photo-1613977257363-707ba9348227?w=400&h=280&fit=crop"),
    (T["pt_townhouse"], "2,100", "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=400&h=280&fit=crop"),
    (T["pt_duplex"], "3,200", "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=400&h=280&fit=crop"),
    (T["pt_penthouse"], "950", "https://images.unsplash.com/photo-1600566753086-00f18fb6b3ea?w=400&h=280&fit=crop"),
    (T["pt_chalet"], "12,800", "https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=400&h=280&fit=crop"),
]
pt_cols = st.columns(6)
for i, (name, count, img) in enumerate(ptype_items):
    with pt_cols[i]:
        pt_html = (
            '<div class="ptype-card-img">'
            '<img class="ptype-thumb" src="' + img + '" alt="' + name + '">'
            '<div class="ptype-info">'
            '<div class="ptype-name">' + name + '</div>'
            '<div class="ptype-count">' + count + '</div>'
            '</div></div>'
        )
        st.markdown(pt_html, unsafe_allow_html=True)

# ═══ AREAS ═══
st.markdown(
    '<div class="section-head">'
    '<div class="section-title">' + T["section_areas"] + '</div>'
    '<a class="section-link">' + T["show_more"] + '</a>'
    '</div>',
    unsafe_allow_html=True,
)

if lang == "ar":
    areas = [
        ("القاهرة الجديدة", "365 كمبوند", "https://images.unsplash.com/photo-1548013146-72479768bada?w=400&h=280&fit=crop"),
        ("مدينة 6 أكتوبر", "163 كمبوند", "https://images.unsplash.com/photo-1493246507139-91e8fad9978e?w=400&h=280&fit=crop"),
        ("العاصمة الإدارية", "245 كمبوند", "https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=400&h=280&fit=crop"),
        ("مدينة المستقبل", "98 كمبوند", "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=400&h=280&fit=crop"),
        ("الساحل الشمالي", "210 كمبوند", "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400&h=280&fit=crop"),
        ("العين السخنة", "78 كمبوند", "https://images.unsplash.com/photo-1582268611958-ebfd161ef9cf?w=400&h=280&fit=crop"),
    ]
else:
    areas = [
        ("New Cairo", "365 compounds", "https://images.unsplash.com/photo-1548013146-72479768bada?w=400&h=280&fit=crop"),
        ("6 October City", "163 compounds", "https://images.unsplash.com/photo-1493246507139-91e8fad9978e?w=400&h=280&fit=crop"),
        ("New Capital", "245 compounds", "https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=400&h=280&fit=crop"),
        ("Mostakbal City", "98 compounds", "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=400&h=280&fit=crop"),
        ("North Coast", "210 compounds", "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400&h=280&fit=crop"),
        ("Ain Sokhna", "78 compounds", "https://images.unsplash.com/photo-1582268611958-ebfd161ef9cf?w=400&h=280&fit=crop"),
    ]

area_cols = st.columns(6)
for i, (name, count, img) in enumerate(areas):
    with area_cols[i]:
        area_html = (
            '<div class="area-card-img">'
            '<img class="area-thumb" src="' + img + '" alt="' + name + '">'
            '<div class="area-info">'
            '<div class="area-name">' + name + '</div>'
            '<div class="area-count">' + count + '</div>'
            '</div></div>'
        )
        st.markdown(area_html, unsafe_allow_html=True)

# ═══ COMPOUNDS ═══
st.markdown(
    '<div class="section-head">'
    '<div class="section-title">' + T["section_compounds"] + '</div>'
    '<a class="section-link">' + T["show_more"] + '</a>'
    '</div>',
    unsafe_allow_html=True,
)

if lang == "ar":
    compounds = [
        ("ماونتن فيو 1.1 - التجمع", "14 وحدة", "14,500,000", "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=600&h=400&fit=crop"),
        ("ماونتن فيو رأس الحكمة", "32 وحدة", "8,200,000", "https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=600&h=400&fit=crop"),
        ("مكادي هايتس - مكادي", "70 وحدة", "6,900,000", "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=600&h=400&fit=crop"),
    ]
    price_prefix = "يبدأ من"
else:
    compounds = [
        ("Mountain View 1.1 - Fifth Settlement", "14 units", "14,500,000", "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=600&h=400&fit=crop"),
        ("Mountain View Ras El Hekma", "32 units", "8,200,000", "https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=600&h=400&fit=crop"),
        ("Makadi Heights - Makadi", "70 units", "6,900,000", "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=600&h=400&fit=crop"),
    ]
    price_prefix = "From"

comp_cols = st.columns(3)
for i, (name, units, price, img) in enumerate(compounds):
    with comp_cols[i]:
        comp_html = (
            '<div class="comp-card-img">'
            '<img class="comp-thumb" src="' + img + '" alt="' + name + '">'
            '<div class="comp-info">'
            '<div class="comp-title">' + name + '</div>'
            '<div class="comp-units">' + units + '</div>'
            '<div class="comp-price">' + price_prefix + ' ' + price + ' ' + T["currency"] + '</div>'
            '</div></div>'
        )
        st.markdown(comp_html, unsafe_allow_html=True)

# ═══ TABS ═══
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    T["tab_estimator"],
    T["tab_market"],
    T["tab_mortgage"],
    T["tab_favorites"],
    T["tab_compare"],
])


# ═══ TAB 1: ESTIMATOR ═══
with tab1:
    col_form, col_result = st.columns([5, 7], gap="large")

    with col_form:
        st.markdown('<div class="form-section">' + T["location"] + '</div>', unsafe_allow_html=True)

        gov_options = [g for g in hierarchy["governorates"] if g["listings"] > 0]
        gov_labels = [nm(g) + " (" + f'{g["listings"]:,}' + ")" for g in gov_options]
        gov_idx = st.selectbox(T["governorate"], range(len(gov_options)),
                                format_func=lambda i: gov_labels[i], key="sel_gov")
        selected_gov = gov_options[gov_idx]

        # فلتر: نستبعد المناطق بأقل من 5 إعلانات
        MIN_LISTINGS = 5

        cities = [c for c in selected_gov.get("cities", []) if c.get("listings", 0) >= MIN_LISTINGS]
        if cities:
            city_labels = [nm(c) + " (" + f'{c["listings"]:,}' + ")" for c in cities]
            city_idx = st.selectbox(T["city"], range(len(cities)),
                                     format_func=lambda i: city_labels[i], key="sel_city")
            selected_city = cities[city_idx]
        else:
            # لو المدينة مفيش فيها بيانات كفاية، ناخد كل الإعلانات
            cities_all = selected_gov.get("cities", [])
            if cities_all:
                city_labels = [nm(c) + " (" + f'{c["listings"]:,}' + ")" for c in cities_all]
                city_idx = st.selectbox(T["city"], range(len(cities_all)),
                                         format_func=lambda i: city_labels[i], key="sel_city")
                selected_city = cities_all[city_idx]
            else:
                selected_city = {"districts": [], "compounds": []}

        districts = [d for d in selected_city.get("districts", []) if d.get("listings", 0) >= MIN_LISTINGS]
        if districts:
            dist_labels = [nm(d) + " (" + f'{d["listings"]:,}' + ")" for d in districts]
            dist_idx = st.selectbox(T["district"], range(len(districts)),
                                     format_func=lambda i: dist_labels[i], key="sel_dist")
            selected_district = districts[dist_idx]
        else:
            districts_all = selected_city.get("districts", [])
            if districts_all:
                dist_labels = [nm(d) + " (" + f'{d["listings"]:,}' + ")" for d in districts_all]
                dist_idx = st.selectbox(T["district"], range(len(districts_all)),
                                         format_func=lambda i: dist_labels[i], key="sel_dist")
                selected_district = districts_all[dist_idx]
            else:
                selected_district = {"en": "Unknown", "ar": "غير معروف"}

        compounds_list = selected_city.get("compounds", [])
        comp_labels = ["-- " + T["no_compound"] + " --"] + [nm(c) for c in compounds_list]
        comp_idx = st.selectbox(T["compound"], range(len(comp_labels)),
                                 format_func=lambda i: comp_labels[i], key="sel_comp")
        selected_compound = compounds_list[comp_idx - 1] if comp_idx > 0 else {"en": "No Compound", "ar": "لا يوجد"}

        town_val = st.text_input(T["town"], value="", key="inp_town")

        st.markdown('<div class="form-section">' + T["details"] + '</div>', unsafe_allow_html=True)

        ptype_keys = ["Apartment", "Villa", "Townhouse", "Duplex", "Penthouse", "Chalet"]
        ptype_labels = {
            "Apartment": T["pt_apartment"], "Villa": T["pt_villa"],
            "Townhouse": T["pt_townhouse"], "Duplex": T["pt_duplex"],
            "Penthouse": T["pt_penthouse"], "Chalet": T["pt_chalet"],
        }
        selected_ptype = st.selectbox(
            T["property_type"], ptype_keys,
            format_func=lambda k: ptype_labels[k], key="sel_ptype"
        )

        c1, c2 = st.columns(2)
        with c1:
            size = st.number_input(T["size"], 30, 5000, 200, 10, key="inp_size")
            bathrooms = st.number_input(T["bathrooms"], 1, 15, 2, key="inp_baths")
            living_rooms = st.number_input(T["living_rooms"], 0, 5, 1, key="inp_living")
        with c2:
            bedrooms = st.number_input(T["bedrooms"], 0, 15, 3, key="inp_beds")
            kitchens = st.number_input(T["kitchens"], 0, 3, 1, key="inp_kitchen")
            floor = st.number_input(T["floor"], 0, 50, 3, key="inp_floor")

        st.markdown('<div class="form-section">' + T["features"] + '</div>', unsafe_allow_html=True)

        fin_keys = ["Core & Shell", "Semi Finished", "Finished", "Super Lux"]
        fin_labels = {"Core & Shell": T["fin_core"], "Semi Finished": T["fin_semi"],
                      "Finished": T["fin_finished"], "Super Lux": T["fin_super"]}
        finishing = st.selectbox(T["finishing"], fin_keys,
                                  format_func=lambda k: fin_labels[k], key="inp_finishing")

        fur_keys = ["Unfurnished", "PARTLY", "Furnished"]
        fur_labels = {"Unfurnished": T["fur_no"], "PARTLY": T["fur_partly"], "Furnished": T["fur_yes"]}
        furnished = st.selectbox(T["furnished"], fur_keys,
                                  format_func=lambda k: fur_labels[k], key="inp_furnished")

        c_view, c_dev = st.columns(2)
        with c_view:
            view_keys = ["Unknown", "Garden", "Pool", "Sea", "City", "Street", "Lake"]
            view_labels = {
                "Unknown": T["view_unknown"], "Garden": T["view_garden"],
                "Pool": T["view_pool"], "Sea": T["view_sea"],
                "City": T["view_city"], "Street": T["view_street"],
                "Lake": T["view_lake"],
            }
            selected_view = st.selectbox(T["view"], view_keys,
                                          format_func=lambda k: view_labels[k], key="inp_view")
        with c_dev:
            selected_developer = st.text_input(T["developer"], value="", key="inp_dev")

        c_seller, c_comp = st.columns(2)
        with c_seller:
            seller_keys = ["Broker", "Owner", "Developer"]
            seller_labels = {
                "Broker": T["seller_broker"], "Owner": T["seller_owner"],
                "Developer": T["seller_developer"],
            }
            selected_seller = st.selectbox(T["seller_type"], seller_keys,
                                            format_func=lambda k: seller_labels[k], key="inp_seller")
        with c_comp:
            comp_keys = ["Ready", "Off-Plan", "Under Construction"]
            comp_labels = {
                "Ready": T["comp_ready"], "Off-Plan": T["comp_offplan"],
                "Under Construction": T["comp_under"],
            }
            selected_completion = st.selectbox(T["completion"], comp_keys,
                                                format_func=lambda k: comp_labels[k], key="inp_comp")

        st.markdown('<div class="form-section">' + T["additional_features"] + '</div>', unsafe_allow_html=True)
        st.caption(T["select_features"])

        feat_items = [
            ("garden", T["feat_garden"]), ("pool", T["feat_pool"]),
            ("garage", T["feat_garage"]), ("security", T["feat_security"]),
            ("gym", T["feat_gym"]), ("elevator", T["feat_elevator"]),
            ("balcony", T["feat_balcony"]), ("view", T["feat_view"]),
            ("mall", T["feat_mall"]), ("mosque", T["feat_mosque"]),
            ("club", T["feat_club"]), ("sea", T["feat_sea"]),
        ]
        feat_cols = st.columns(2)
        for i, (fkey, flabel) in enumerate(feat_items):
            with feat_cols[i % 2]:
                active = fkey in st.session_state.selected_features
                if st.button(flabel, key="feat_" + fkey, use_container_width=True,
                             type="primary" if active else "secondary"):
                    if active:
                        st.session_state.selected_features.remove(fkey)
                    else:
                        st.session_state.selected_features.append(fkey)
                    st.rerun()

        amenity_count = 5 + len(st.session_state.selected_features)

        st.markdown("---")
        predict_btn = st.button(T["calculate"], type="primary", use_container_width=True, key="predict_btn")


    with col_result:
        if predict_btn:
            with st.spinner(T["calculating"]):
                sample = df[
                    (df["governorate"] == selected_gov["en"]) &
                    (df["district"] == selected_district["en"])
                ]
                lat = sample["latitude"].median() if len(sample) > 0 else 30.0444
                lon = sample["longitude"].median() if len(sample) > 0 else 31.2357

                input_data = {}
                for f in metadata["features"]:
                    if f in metadata["cat_features"]:
                        input_data[f] = "Unknown"
                    else:
                        input_data[f] = 0

                input_data["size"] = size
                input_data["bedrooms"] = bedrooms
                input_data["bathrooms"] = bathrooms
                input_data["amenity_count"] = amenity_count
                input_data["images_count"] = 10
                input_data["latitude"] = lat
                input_data["longitude"] = lon
                input_data["property_type"] = selected_ptype
                input_data["governorate"] = selected_gov["en"]
                input_data["district"] = selected_district["en"]
                input_data["compound"] = selected_compound["en"]
                input_data["completion_status"] = selected_completion.lower() if selected_completion != "Ready" else "completed"
                input_data["furnished"] = furnished
                input_data["seller_type"] = selected_seller
                input_data["developer_name"] = selected_developer if selected_developer else "Unknown"
                input_data["view"] = selected_view
                input_data["finishing_type"] = finishing
                input_data["payment_method"] = "Unknown"
                input_data["town"] = town_val if town_val else selected_gov["en"]
                input_data["area_per_room"] = size / max(bedrooms, 1)
                input_data["total_rooms"] = bedrooms + bathrooms + living_rooms + kitchens
                input_data["bed_bath_ratio"] = bedrooms / max(bathrooms, 1)
                input_data["amenity_per_room"] = amenity_count / max(bedrooms + bathrooms, 1)
                input_data["images_per_room"] = 10 / max(bedrooms + bathrooms, 1)
                input_data["lat_x_lon"] = lat * lon
                input_data["distance_to_cairo"] = 0
                input_data["distance_to_coast"] = 0
                input_data["distance_cairo_sq"] = 0
                input_data["is_coastal"] = 0
                input_data["is_cairo_center"] = 0
                input_data["is_high_end"] = 1 if selected_ptype in ["Villa", "Penthouse"] else 0
                input_data["is_luxury"] = 1 if selected_ptype in ["Villa", "Penthouse", "Townhouse"] else 0
                input_data["is_compound"] = 0 if selected_compound["en"] == "No Compound" else 1
                input_data["is_premium"] = 0
                input_data["is_featured"] = 0
                input_data["walk_score"] = 50
                input_data["transit_score"] = 50
                input_data["amenity_score"] = amenity_count / 20
                input_data["floor_level"] = floor
                input_data["year_built"] = 2024
                input_data["has_premium_info"] = 0

                X = build_features(input_data, metadata["features"], metadata["cat_features"])
                result = predict_with_confidence(model, X, metadata["features"], metadata["cat_features"])
                price = result["price"]
                ppm2 = price / size

                st.session_state.current_prediction = {
                    "governorate": selected_gov["en"],
                    "district": selected_district["en"],
                    "property_type": selected_ptype,
                    "size": size, "bedrooms": bedrooms, "bathrooms": bathrooms,
                    "price": price, "ppm2": ppm2,
                }

            price_html = (
                '<div class="price-card">'
                '<div class="price-label">' + T["result_title"] + '</div>'
                '<div class="price-value">' + f'{price:,.0f}' + '</div>'
                '<div class="price-currency">' + T["currency"] + '</div>'
                '<div class="price-per-m2">' + T["per_sqm"] + ': ' + f'{ppm2:,.0f}' + '</div>'
                '</div>'
            )
            st.markdown(price_html, unsafe_allow_html=True)

            # ═══ PROPERTY GALLERY ═══
            st.markdown("---")
            render_property_gallery(selected_ptype, nm(selected_district), f"{price:,.0f}", key_prefix="result_gal")

            # مؤشر جودة البيانات: نفس نوع العقار في نفس الحي فقط
            similar_data = df[
                (df["governorate"] == selected_gov["en"]) &
                (df["district"] == selected_district["en"]) &
                (df["property_type"] == selected_ptype)
            ]
            sample_count = len(similar_data)
            sample_scope = "in this district" if lang == "en" else "في هذا الحي"
            
            # لو أقل من 5، نقارن بالمحافظة
            if sample_count < 5:
                similar_data = df[
                    (df["governorate"] == selected_gov["en"]) &
                    (df["property_type"] == selected_ptype)
                ]
                sample_count = len(similar_data)
                sample_scope = "in this governorate" if lang == "en" else "في المحافظة"
            
            if sample_count >= 50:
                quality_label = "High" if lang == "en" else "عالية"
                quality_color = "green"
            elif sample_count >= 15:
                quality_label = "Medium" if lang == "en" else "متوسطة"
                quality_color = "yellow"
            elif sample_count >= 5:
                quality_label = "Low" if lang == "en" else "منخفضة"
                quality_color = "orange"
            else:
                quality_label = "Very Low" if lang == "en" else "ضعيفة جداً"
                quality_color = "red"
            
            row1_c1, row1_c2 = st.columns(2)
            row1_c1.metric(T["price_range"], f'{result["price_low"]/1e6:.1f}M - {result["price_high"]/1e6:.1f}M')
            row1_c2.metric(T["confidence"], f'{result["confidence"]*100:.0f}%')
            m3 = None
            m4 = None
            color_hex = {"green": "#059669", "yellow": "#D97706", "orange": "#EA580C", "red": "#DC2626"}.get(quality_color, "#64748B")
            quality_html = (
                '<div style="font-size:22px;font-weight:800;color:' + color_hex + ';letter-spacing:-0.5px;">'
                '● ' + quality_label +
                '</div>'
                '<div style="font-size:11px;color:#64748B;font-weight:600;margin-top:4px;">'
                + str(sample_count) + ' ' + sample_scope +
                '</div>'
            )
            row2_c1, row2_c2 = st.columns(2)
            with row2_c1:
                st.markdown(
                    '<div style="padding:8px 0;">'
                    '<div style="font-size:11px;color:#64748B;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px;">'
                    + ("Data Quality" if lang == "en" else "جودة البيانات") +
                    '</div>' + quality_html + '</div>',
                    unsafe_allow_html=True,
                )

            # نقارن بالحي الأول، لو مفيش بيانات كفاية نقارن بالمدينة
            district_data = df[
                (df["governorate"] == selected_gov["en"]) &
                (df["district"] == selected_district["en"]) &
                (df["property_type"] == selected_ptype)
            ]["price"]
            
            if len(district_data) >= 10:
                market_median = district_data.median()
                market_scope = "district" if lang == "en" else "الحي"
            else:
                market_median = df[
                    (df["governorate"] == selected_gov["en"]) &
                    (df["property_type"] == selected_ptype)
                ]["price"].median()
                market_scope = "governorate" if lang == "en" else "المحافظة"

            if pd.notna(market_median):
                diff = ((price - market_median) / market_median) * 100
                if diff > 10:
                    vs_label = f'{diff:.0f}% ' + T["above_market"]
                elif diff < -10:
                    vs_label = f'{abs(diff):.0f}% ' + T["below_market"]
                else:
                    vs_label = T["at_market"]
                with row2_c2:
                    market_html = (
                        '<div style="padding:8px 0;">'
                        '<div style="font-size:11px;color:#64748B;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px;">'
                        + T["vs_market"] + ' (' + market_scope + ')'
                        + '</div>'
                        '<div style="font-size:22px;font-weight:800;color:#0A0F1C;letter-spacing:-0.5px;">'
                        + vs_label.split()[0] +
                        '</div>'
                        '<div style="font-size:11px;color:#64748B;font-weight:600;margin-top:4px;">'
                        + ' '.join(vs_label.split()[1:]) +
                        '</div>'
                        '</div>'
                    )
                    st.markdown(market_html, unsafe_allow_html=True)


            st.markdown("---")
            b1, b2, b3 = st.columns(3)
            with b1:
                if st.button(T["save"], use_container_width=True, key="save_pred"):
                    st.session_state.favorites.append(st.session_state.current_prediction)
                    st.success(T["saved"])

            with b2:
                # PDF
                if PDF_AVAILABLE:
                    pdf_bytes = generate_pdf_report(st.session_state.current_prediction, lang)
                    if pdf_bytes:
                        st.download_button(
                            label=T["pdf"],
                            data=pdf_bytes,
                            file_name="property_report_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".pdf",
                            mime="application/pdf",
                            use_container_width=True,
                            key="pdf_download",
                        )
                else:
                    if st.button(T["pdf"], use_container_width=True, key="pdf_btn_disabled"):
                        st.warning("PDF library not available" if lang == "en" else "مكتبة PDF غير متاحة")

            with b3:
                # Share
                share_text = (
                    f"Egypt Real Estate AI - " + 
                    (f"{price:,.0f} EGP for {size:.0f} sqm in {nm(selected_district)}" if lang == "en" else f"{price:,.0f} ج.م لشقة {size:.0f} م² في {nm(selected_district)}")
                )
                st.markdown(
                    '<div style="text-align:center;">'
                    '<a href="https://wa.me/?text=' + share_text.replace(' ', '%20').replace('&', '%26') + '" target="_blank" '
                    'style="text-decoration:none;display:block;">'
                    '<button style="width:100%;padding:12px;background:' + get_theme(dark)["primary"] + ';'
                    'color:white;border:none;border-radius:8px;font-weight:700;'
                    'font-size:14px;cursor:pointer;">' + ("Share" if lang == "en" else "مشاركة") + '</button></a>'
                    '</div>',
                    unsafe_allow_html=True,
                )

            st.markdown("---")

            # ═══ PRICE HISTORY & FORECAST ═══
            price_hist_title = "Price History & Forecast" if lang == "en" else "تاريخ وتوقع السعر"
            st.markdown(
                '<div class="section-title" style="font-size:20px;margin-bottom:20px;">' + price_hist_title + '</div>',
                unsafe_allow_html=True,
            )

            annual_growth = 0.08
            price_1y_ago = price / (1 + annual_growth)
            price_6m_ago = price / (1 + annual_growth) ** 0.5
            price_6m_future = price * (1 + annual_growth) ** 0.5
            price_1y_future = price * (1 + annual_growth)
            price_3y_future = price * (1 + annual_growth) ** 3

            # 4 كروت للمؤشرات
            c1, c2, c3, c4 = st.columns(4)

            labels_ar = ["السعر قبل سنة", "السعر الآن", "السعر بعد سنة", "السعر بعد 3 سنوات"]
            labels_en = ["1 Year Ago", "Current Price", "Price in 1 Year", "Price in 3 Years"]
            labels = labels_ar if lang == "ar" else labels_en

            values = [
                (f"{price_1y_ago/1e6:.2f}M", "down", f"{(price - price_1y_ago)/price_1y_ago*100:.1f}%", "growth"),
                (f"{price/1e6:.2f}M", "now", "", ""),
                (f"{price_1y_future/1e6:.2f}M", "up", f"+{annual_growth*100:.1f}%", "forecast"),
                (f"{price_3y_future/1e6:.2f}M", "up", f"+{(price_3y_future/price - 1)*100:.1f}%", "forecast"),
            ]

            cols = [c1, c2, c3, c4]
            for i, (col, label, (val, trend, pct, badge)) in enumerate(zip(cols, labels, values)):
                with col:
                    badge_html = ""
                    if badge == "growth":
                        badge_html = '<div class="price-card-badge badge-gray">' + pct + " " + ("since last year" if lang == "en" else "خلال سنة") + '</div>'
                    elif badge == "forecast":
                        badge_html = '<div class="price-card-badge badge-green">' + pct + " " + ("forecast" if lang == "en" else "متوقع") + '</div>'
                    elif trend == "now":
                        badge_html = '<div class="price-card-badge badge-blue">' + ("Current" if lang == "en" else "الحالي") + '</div>'

                    border_color = "#0066FF" if trend == "now" else "#E2E8F0"

                    st.markdown(
                        '<div class="price-history-card" style="border-top:3px solid ' + border_color + ';">'
                        '<div class="price-history-label">' + label + '</div>'
                        '<div class="price-history-value">' + val + '</div>'
                        '<div class="price-history-unit">' + ("M EGP" if lang == "en" else "مليون ج.م") + '</div>'
                        + badge_html +
                        '</div>',
                        unsafe_allow_html=True,
                    )

            # رسم بياني محسّن
            st.markdown("")
            years_ar_chart = ["2020", "2021", "2022", "2023", "2024", "2025", "2026", "2027"]
            years_en_chart = ["2020", "2021", "2022", "2023", "2024", "2025", "2026", "2027"]
            years_chart = years_ar_chart if lang == "ar" else years_en_chart

            prices_chart = [
                price / (1 + annual_growth) ** 4,
                price / (1 + annual_growth) ** 3,
                price / (1 + annual_growth) ** 2,
                price / (1 + annual_growth) ** 1,
                price,
                price * (1 + annual_growth) ** 1,
                price * (1 + annual_growth) ** 2,
                price * (1 + annual_growth) ** 3,
            ]
            prices_chart_m = [p / 1e6 for p in prices_chart]

            fig_ts = go.Figure()
            fig_ts.add_trace(go.Scatter(
                x=years_chart[:5], y=prices_chart_m[:5],
                mode='lines+markers',
                name=('Historical' if lang == 'en' else 'تاريخي'),
                line=dict(color=get_theme(dark)["primary"], width=4),
                marker=dict(size=12, line=dict(color='white', width=2)),
                fill='tozeroy',
                fillcolor='rgba(0,102,255,0.08)',
                hovertemplate=('%{x}: %{y:.2f}M EGP<extra></extra>' if lang == 'en' else '%{x}: %{y:.2f} مليون ج.م<extra></extra>'),
            ))
            fig_ts.add_trace(go.Scatter(
                x=years_chart[4:], y=prices_chart_m[4:],
                mode='lines+markers',
                name=('Forecast' if lang == 'en' else 'توقع'),
                line=dict(color=get_theme(dark)["accent"], width=4, dash='dash'),
                marker=dict(size=12, symbol='diamond', line=dict(color='white', width=2)),
                fill='tozeroy',
                fillcolor='rgba(255,107,53,0.08)',
                hovertemplate=('%{x}: %{y:.2f}M EGP<extra></extra>' if lang == 'en' else '%{x}: %{y:.2f} مليون ج.م<extra></extra>'),
            ))
            fig_ts.update_layout(
                height=380,
                margin=dict(l=20, r=20, t=20, b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                yaxis_title=("Price (M EGP)" if lang == "en" else "السعر (مليون ج.م)"),
                xaxis=dict(type='category', showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(226,232,240,0.5)'),
                hovermode='x unified',
            )
            st.plotly_chart(fig_ts, use_container_width=True)

            # ═══ MAP ═══
            st.markdown("---")
            map_title = "Property Location" if lang == "en" else "موقع العقار"
            st.markdown(
                '<div class="section-title" style="font-size:20px;margin-bottom:20px;">' + map_title + '</div>',
                unsafe_allow_html=True,
            )

            import folium
            from streamlit_folium import folium_static

            m = folium.Map(location=[lat, lon], zoom_start=13)
            folium.Marker(
                [lat, lon],
                popup=(nm(selected_district) + " - " + f"{price:,.0f} EGP"),
                icon=folium.Icon(color='blue', icon='home', prefix='fa'),
            ).add_to(m)
            folium_static(m, width=None, height=420)

            # ═══ INVESTMENT ANALYSIS ═══
            st.markdown("---")
            roi_title = "Investment Analysis" if lang == "en" else "تحليل الاستثمار"
            st.markdown(
                '<div class="section-title" style="font-size:20px;margin-bottom:20px;">' + roi_title + '</div>',
                unsafe_allow_html=True,
            )

            annual_rent = price * 0.055
            monthly_rent = annual_rent / 12
            annual_yield = (annual_rent / price) * 100
            roi_5y = ((price * (1.08 ** 5) - price) / price) * 100
            payback_years = price / annual_rent
            future_5y = price * (1.08 ** 5)

            roi_items_ar = [
                ("الإيجار الشهري", f"{monthly_rent:,.0f}", "ج.م", "monthly"),
                ("العائد السنوي", f"{annual_yield:.2f}", "%", "yield"),
                ("فترة الاسترداد", f"{payback_years:.1f}", "سنة", "payback"),
                ("نمو رأس المال (5 سنوات)", f"{roi_5y:.1f}", "%", "growth"),
                ("القيمة المستقبلية (5 سنوات)", f"{future_5y/1e6:.2f}", "مليون ج.م", "future"),
                ("سعر المتر", f"{ppm2:,.0f}", "ج.م", "sqm"),
            ]
            roi_items_en = [
                ("Monthly Rent", f"{monthly_rent:,.0f}", "EGP", "monthly"),
                ("Annual Yield", f"{annual_yield:.2f}", "%", "yield"),
                ("Payback Period", f"{payback_years:.1f}", "years", "payback"),
                ("5Y Capital Growth", f"{roi_5y:.1f}", "%", "growth"),
                ("5Y Future Value", f"{future_5y/1e6:.2f}", "M EGP", "future"),
                ("Price per sqm", f"{ppm2:,.0f}", "EGP", "sqm"),
            ]
            roi_items = roi_items_ar if lang == "ar" else roi_items_en

            roi_cols_row1 = st.columns(3)
            roi_cols_row2 = st.columns(3)
            all_roi_cols = list(roi_cols_row1) + list(roi_cols_row2)

            for col, (label, value, unit, icon_key) in zip(all_roi_cols, roi_items):
                with col:
                    st.markdown(
                        '<div class="roi-card">'
                        '<div class="roi-label">' + label + '</div>'
                        '<div class="roi-value">' + value + ' <span class="roi-unit">' + unit + '</span></div>'
                        '</div>',
                        unsafe_allow_html=True,
                    )


            # ═══ NEIGHBORHOOD INSIGHTS ═══
            st.markdown("---")
            render_neighborhood_section(selected_district["en"], selected_gov["en"])



        else:
            empty_html = (
                '<div class="empty-state">'
                '<div class="empty-title">' + T["hero_title"] + '</div>'
                '<div class="empty-desc">' + T["hero_sub"] + '</div>'
                '</div>'
            )
            st.markdown(empty_html, unsafe_allow_html=True)


# ═══ TAB 2: MARKET ANALYSIS ═══
with tab2:
    st.markdown('<div class="section-title">' + T["tab_market"] + '</div>', unsafe_allow_html=True)
    st.markdown("")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(T["stat_listings"], f'{len(df):,}')
    c2.metric(T["stat_gov"], str(n_gov))
    c3.metric("Avg Price", f'{df["price"].mean()/1e6:.1f}M')
    c4.metric("Median Price", f'{df["price"].median()/1e6:.1f}M')

    st.markdown("---")
    col_a, col_b = st.columns(2)

    with col_a:
        gov_counts = df["governorate"].value_counts().head(6)
        fig = px.pie(values=gov_counts.values, names=gov_counts.index,
                     title="Listings by Governorate")
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        ptype_counts = df["property_type"].value_counts().head(6)
        fig = px.bar(x=ptype_counts.values, y=ptype_counts.index, orientation="h",
                     title="Property Types",
                     color_discrete_sequence=[get_theme(dark)["primary"]])
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    price_data = df[df["price"] < df["price"].quantile(0.95)]
    fig = px.histogram(price_data, x="price", nbins=50,
                       title="Price Distribution",
                       color_discrete_sequence=[get_theme(dark)["primary"]])
    st.plotly_chart(fig, use_container_width=True)

# ═══ TAB 3: MORTGAGE ═══
with tab3:
    st.markdown('<div class="section-title">' + T["tab_mortgage"] + '</div>', unsafe_allow_html=True)
    st.markdown("")

    c1, c2 = st.columns(2)
    with c1:
        loan = st.number_input(T["mortgage_loan"], 100000, 100000000, 2000000, 100000, key="m_loan")
        rate = st.number_input(T["mortgage_rate"], 1.0, 30.0, 12.0, 0.25, key="m_rate")
        years = st.number_input(T["mortgage_years"], 1, 30, 10, key="m_years")

    monthly_rate = rate / 100 / 12
    n_payments = years * 12

    if monthly_rate > 0:
        monthly = loan * monthly_rate * (1 + monthly_rate) ** n_payments / ((1 + monthly_rate) ** n_payments - 1)
    else:
        monthly = loan / n_payments

    total = monthly * n_payments
    interest = total - loan

    with c2:
        m1, m2, m3 = st.columns(3)
        m1.metric(T["mortgage_monthly"], f'{monthly:,.0f}')
        m2.metric(T["mortgage_total"], f'{total:,.0f}')
        m3.metric(T["mortgage_interest"], f'{interest:,.0f}')

# ═══ TAB 5: COMPARE ═══
with tab5:
    st.markdown('<div class="section-title">' + T["comp_title"] + '</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#64748B;font-size:14px;margin-bottom:24px;">' + T["comp_subtitle"] + '</div>', unsafe_allow_html=True)

    if not st.session_state.favorites:
        comp_empty = (
            '<div class="empty-state">'
            '<div class="empty-title">' + T["comp_empty"] + '</div>'
            '<div class="empty-desc">' + T["empty_desc"] + '</div>'
            '</div>'
        )
        st.markdown(comp_empty, unsafe_allow_html=True)
    else:
        # عرض قائمة المفضلة للاختيار
        st.markdown('<div class="form-section">' + ("Select properties to compare" if lang == "en" else "اختر العقارات للمقارنة") + '</div>', unsafe_allow_html=True)

        if len(st.session_state.favorites) < 2:
            st.info(T["comp_need_two"])

        selected_indices = []
        for i, fav in enumerate(st.session_state.favorites):
            checkbox_label = (
                str(fav.get("property_type", "")) + " | " +
                str(fav.get("district", "")) + " | " +
                f'{fav.get("size", 0):.0f}m2 | ' +
                f'{fav.get("price", 0):,.0f} EGP'
            )
            if st.checkbox(checkbox_label, key="cmp_" + str(i)):
                selected_indices.append(i)

        if len(selected_indices) > 4:
            st.warning(T["comp_max"])
            selected_indices = selected_indices[:4]

        if len(selected_indices) >= 2:
            st.markdown("---")
            # بناء جدول المقارنة
            compare_data = {
                T["comp_property"]: [],
                T["comp_type"]: [],
                T["comp_location"]: [],
                T["comp_size"]: [],
                T["comp_bedrooms"]: [],
                T["comp_bathrooms"]: [],
                T["comp_price"]: [],
                T["comp_ppm2"]: [],
            }

            for idx in selected_indices:
                fav = st.session_state.favorites[idx]
                compare_data[T["comp_property"]].append("Property " + str(idx + 1))
                compare_data[T["comp_type"]].append(str(fav.get("property_type", "-")))
                compare_data[T["comp_location"]].append(str(fav.get("district", "-")))
                compare_data[T["comp_size"]].append(f'{fav.get("size", 0):.0f} m2')
                compare_data[T["comp_bedrooms"]].append(str(fav.get("bedrooms", 0)))
                compare_data[T["comp_bathrooms"]].append(str(fav.get("bathrooms", 0)))
                compare_data[T["comp_price"]].append(f'{fav.get("price", 0):,.0f} EGP')
                compare_data[T["comp_ppm2"]].append(f'{fav.get("ppm2", 0):,.0f} EGP')

            # عرض كجدول
            import pandas as pd
            df_compare = pd.DataFrame(compare_data)
            st.dataframe(df_compare, use_container_width=True, hide_index=True)

            # رسم بياني للمقارنة
            st.markdown("---")
            chart_data = {
                "Property": ["Property " + str(i + 1) for i in selected_indices],
                "Price (M EGP)": [st.session_state.favorites[i].get("price", 0) / 1e6 for i in selected_indices],
                "Size (sqm)": [st.session_state.favorites[i].get("size", 0) for i in selected_indices],
            }
            df_chart = pd.DataFrame(chart_data)

            c1, c2 = st.columns(2)
            with c1:
                fig_price = px.bar(df_chart, x="Property", y="Price (M EGP)",
                                    title=("Price Comparison" if lang == "en" else "مقارنة السعر"),
                                    color_discrete_sequence=[get_theme(dark)["primary"]])
                st.plotly_chart(fig_price, use_container_width=True)
            with c2:
                fig_size = px.bar(df_chart, x="Property", y="Size (sqm)",
                                    title=("Size Comparison" if lang == "en" else "مقارنة المساحة"),
                                    color_discrete_sequence=[get_theme(dark)["accent"]])
                st.plotly_chart(fig_size, use_container_width=True)

        elif len(selected_indices) == 1:
            st.info(T["comp_need_two"])


# ═══ TAB 4: FAVORITES ═══
with tab4:
    st.markdown('<div class="section-title">' + T["tab_favorites"] + '</div>', unsafe_allow_html=True)
    st.markdown("")

    # أزرار Export/Import
    if st.session_state.favorites:
        c_exp, c_imp = st.columns(2)
        with c_exp:
            favs_json = json.dumps(st.session_state.favorites, ensure_ascii=False, indent=2)
            st.download_button(
                label=T["export_favs"],
                data=favs_json,
                file_name="favorites_" + datetime.now().strftime("%Y%m%d") + ".json",
                mime="application/json",
                use_container_width=True,
                key="export_favs_btn",
                help=T["export_help"],
            )
        with c_imp:
            uploaded = st.file_uploader(
                T["import_favs"],
                type=["json"],
                key="import_favs_file",
                help=T["import_help"],
                label_visibility="collapsed",
            )
            if uploaded is not None:
                try:
                    imported = json.loads(uploaded.read().decode("utf-8"))
                    if isinstance(imported, list) and len(imported) > 0:
                        st.session_state.favorites = imported
                        st.success(T["import_success"])
                        st.rerun()
                    else:
                        st.error(T["import_error"])
                except Exception:
                    st.error(T["import_error"])
        st.markdown("---")

    if not st.session_state.favorites:
        empty_html = (
            '<div class="empty-state">'
            '<div class="empty-title">' + T["empty_title"] + '</div>'
            '<div class="empty-desc">' + T["empty_desc"] + '</div>'
            '</div>'
        )
        st.markdown(empty_html, unsafe_allow_html=True)
    else:
        for i, fav in enumerate(st.session_state.favorites):
            c1, c2 = st.columns([5, 1])
            with c1:
                fav_html = (
                    '<div class="fav-item">'
                    '<div class="fav-title">' + str(fav.get("property_type", "")) + " in " + str(fav.get("district", "")) + '</div>'
                    '<div class="fav-detail">' + f'{fav.get("size", 0):.0f} sqm | {fav.get("bedrooms", 0)} beds | {fav.get("bathrooms", 0)} baths' + '</div>'
                    '<div class="fav-price">' + f'{fav.get("price", 0):,.0f}' + " " + T["currency"] + '</div>'
                    '</div>'
                )
                st.markdown(fav_html, unsafe_allow_html=True)
            with c2:
                if st.button("X", key="del_" + str(i), use_container_width=True):
                    st.session_state.favorites.pop(i)
                    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ═══ FOOTER ═══
footer_html = (
    '<div class="footer">'
    '<div class="footer-brand">' + T["brand_prefix"] + " " + T["brand_suffix"] + '</div>'
    '<div>' + T["footer_tagline"] + '</div>'
    '<div style="margin-top:16px;font-size:12px;opacity:0.7;">'
    + f'{training["n_total"]:,}' + " listings | " + str(n_gov) + " governorates | R2 = " + f'{metrics["r2"]:.4f}'
    + '</div>'
    '<div style="margin-top:8px;font-size:11px;opacity:0.5;">'
    '2026 Egypt Real Estate AI - ' + T["footer_rights"] +
    '</div>'
    '</div>'
)
st.markdown(footer_html, unsafe_allow_html=True)
