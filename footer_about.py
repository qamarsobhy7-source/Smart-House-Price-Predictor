"""Footer, About, Trust sections — like Property Finder."""


def render_trust_badges(lang="en"):
    """Render 'Why Choose Us' trust badges."""
    import streamlit as st

    if lang == "ar":
        title = "🏆 لماذا SmartPrice؟"
        sub = "مميزات تجعلنا الخيار الأول"
        badges = [
            ("🎯", "دقة عالية", "R² = 0.70 على 7,711 عقار حقيقي"),
            ("⚡", "نتائج فورية", "توقع السعر في ثوانٍ"),
            ("🌍", "تغطية كاملة", "27 محافظة + 43 حي"),
            ("🔬", "شفافية كاملة", "شرح كل توقع بـ SHAP"),
            ("🌐", "لغتين", "العربية والإنجليزية"),
            ("📱", "كل الأجهزة", "موبايل + تابلت + لابتوب"),
        ]
    else:
        title = "🏆 Why SmartPrice?"
        sub = "What makes us the smart choice"
        badges = [
            ("🎯", "High Accuracy", "R² = 0.70 on 7,711 real listings"),
            ("⚡", "Instant Results", "Price prediction in seconds"),
            ("🌍", "Full Coverage", "27 governorates + 43 districts"),
            ("🔬", "Full Transparency", "SHAP explanation for every prediction"),
            ("🌐", "Bilingual", "Arabic and English"),
            ("📱", "All Devices", "Mobile + Tablet + Laptop"),
        ]

    st.markdown(
        '<div style="margin:36px 0 18px 0;">'
        '<div style="display:flex;align-items:center;gap:12px;">'
        '<div style="font-size:26px;">🏆</div>'
        '<div>'
        f'<div style="font-size:20px;font-weight:900;color:#1f2937;">{title}</div>'
        f'<div style="font-size:12px;color:#6b7280;margin-top:2px;">{sub}</div>'
        '</div></div></div>',
        unsafe_allow_html=True,
    )

    cols = st.columns(3)
    for i, (icon, title_i, desc) in enumerate(badges):
        with cols[i % 3]:
            html = (
                '<div style="background:white;border:1px solid #e5e7eb;'
                'border-radius:14px;padding:16px 12px;margin-bottom:10px;'
                'box-shadow:0 2px 8px rgba(0,0,0,0.04);'
                'display:flex;gap:10px;align-items:flex-start;">'
                '<div style="font-size:24px;flex-shrink:0;">' + icon + '</div>'
                '<div>'
                '<div style="font-size:13px;font-weight:800;color:#1f2937;">'
                + title_i + '</div>'
                '<div style="font-size:11px;color:#6b7280;margin-top:3px;'
                'line-height:1.4;">' + desc + '</div>'
                '</div></div>'
            )
            st.markdown(html, unsafe_allow_html=True)


def render_footer(lang="en"):
    """Render professional footer."""
    import streamlit as st
    from datetime import datetime

    year = datetime.now().year

    if lang == "ar":
        tagline = "منصة تقييم العقارات بالذكاء الاصطناعي في مصر"
        sections = {
            "المنتج": ["الميزات", "الأسعار", "الـ API"],
            "الشركة": ["عننا", "فريقنا", "وظائف"],
            "القانوني": ["سياسة الخصوصية", "شروط الاستخدام", "ملفات تعريف الارتباط"],
            "المساعدة": ["الأسئلة الشائعة", "اتصل بنا", "توثيق"],
        }
        rights = f"© {year} SmartPrice — جميع الحقوق محفوظة"
        disclaimer = "⚠️ أداة تقدير بالذكاء الاصطناعي — مش تقييم رسمي"
    else:
        tagline = "AI-powered real estate valuation for Egypt"
        sections = {
            "Product": ["Features", "Pricing", "API"],
            "Company": ["About", "Team", "Careers"],
            "Legal": ["Privacy", "Terms", "Cookies"],
            "Support": ["FAQ", "Contact", "Docs"],
        }
        rights = f"© {year} SmartPrice — All rights reserved"
        disclaimer = "⚠️ AI estimation tool — not a certified appraisal"

    # Build footer HTML
    cols_html = ""
    for sec_title, links in sections.items():
        links_html = "".join(
            f'<div style="font-size:12px;color:#9ca3af;margin-bottom:6px;'
            f'cursor:pointer;">{link}</div>'
            for link in links
        )
        cols_html += (
            f'<div>'
            f'<div style="font-size:12px;font-weight:800;color:white;'
            f'margin-bottom:10px;text-transform:uppercase;letter-spacing:0.5px;">'
            f'{sec_title}</div>'
            f'{links_html}</div>'
        )

    footer_html = (
        '<div style="background:linear-gradient(135deg,#1f2937,#111827);'
        'border-radius:20px;padding:32px 24px 20px;margin:36px 0 16px;'
        'color:white;">'
        # Top: Brand + columns
        '<div style="display:grid;grid-template-columns:2fr 1fr 1fr 1fr 1fr;'
        'gap:20px;margin-bottom:24px;" class="footer-grid">'
        '<div>'
        '<div style="font-size:20px;font-weight:900;margin-bottom:6px;">'
        '🏠 Smart<span style="color:#818cf8;">Price</span></div>'
        f'<div style="font-size:11px;color:#9ca3af;line-height:1.5;'
        f'margin-bottom:14px;">{tagline}</div>'
        '<div style="display:flex;gap:8px;">'
        '<div style="width:30px;height:30px;background:rgba(255,255,255,0.1);'
        'border-radius:8px;display:flex;align-items:center;justify-content:center;'
        'font-size:14px;">📱</div>'
        '<div style="width:30px;height:30px;background:rgba(255,255,255,0.1);'
        'border-radius:8px;display:flex;align-items:center;justify-content:center;'
        'font-size:14px;">📧</div>'
        '<div style="width:30px;height:30px;background:rgba(255,255,255,0.1);'
        'border-radius:8px;display:flex;align-items:center;justify-content:center;'
        'font-size:14px;">🌐</div>'
        '</div>'
        '</div>'
        + cols_html +
        '</div>'
        # Divider
        '<div style="border-top:1px solid rgba(255,255,255,0.1);'
        'padding-top:14px;display:flex;justify-content:space-between;'
        'align-items:center;flex-wrap:wrap;gap:8px;">'
        f'<div style="font-size:11px;color:#9ca3af;">{rights}</div>'
        f'<div style="font-size:10px;color:#6b7280;">{disclaimer}</div>'
        '</div>'
        '</div>'
        '<style>@media (max-width:768px){'
        '.footer-grid{grid-template-columns:1fr 1fr !important;gap:16px !important;}'
        '}</style>'
    )
    st.markdown(footer_html, unsafe_allow_html=True)
