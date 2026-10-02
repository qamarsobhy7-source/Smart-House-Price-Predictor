"""Loading animations & skeleton loaders — for professional UX."""
import streamlit as st


def loading_spinner(text_ar="جاري التحليل...", text_en="Analyzing..."):
    """Return a context manager with custom spinner."""
    return st.spinner(text_ar if st.session_state.get("lang") == "ar" else text_en)


def skeleton_card(height=140):
    """Render a shimmer skeleton card."""
    html = (
        '<div style="background:linear-gradient(90deg,#f3f4f6 25%,#e5e7eb 50%,#f3f4f6 75%);'
        'background-size:200% 100%;animation:shimmer 1.5s infinite;'
        f'border-radius:16px;height:{height}px;margin-bottom:12px;"></div>'
        '<style>@keyframes shimmer {'
        '0% { background-position: 200% 0; }'
        '100% { background-position: -200% 0; }'
        '}</style>'
    )
    st.markdown(html, unsafe_allow_html=True)


def skeleton_grid(n=4):
    """Render a grid of skeleton cards."""
    cols = st.columns(n)
    for c in cols:
        with c:
            skeleton_card(180)


def progress_bar(steps=4):
    """Render an animated progress bar."""
    html = (
        '<div style="height:4px;background:#e5e7eb;border-radius:2px;'
        'margin:8px 0;overflow:hidden;">'
        '<div style="height:100%;width:30%;'
        'background:linear-gradient(90deg,#6366f1,#ec4899);'
        'animation:progress-anim 2s infinite;border-radius:2px;"></div></div>'
        '<style>@keyframes progress-anim {'
        '0% { margin-left: 0; width: 30%; }'
        '50% { margin-left: 40%; width: 40%; }'
        '100% { margin-left: 100%; width: 30%; }'
        '}</style>'
    )
    st.markdown(html, unsafe_allow_html=True)


def typing_effect(text, delay=0.05):
    """Return typing dots animation HTML."""
    html = (
        '<span style="display:inline-block;">' + text + '</span>'
        '<span style="display:inline-block;margin-left:2px;">'
        '<span style="animation:dot 1s infinite;display:inline-block;">.</span>'
        '<span style="animation:dot 1s 0.2s infinite;display:inline-block;">.</span>'
        '<span style="animation:dot 1s 0.4s infinite;display:inline-block;">.</span>'
        '</span>'
        '<style>@keyframes dot {'
        '0%, 20% { opacity: 0.2; } 50% { opacity: 1; }'
        '80%, 100% { opacity: 0.2; }'
        '}</style>'
    )
    return html


def ai_thinking_indicator(lang="en"):
    """Show AI thinking animation before prediction."""
    text = "🤖 النموذج بيحسب..." if lang == "ar" else "🤖 AI is analyzing..."
    html = (
        '<div style="background:linear-gradient(135deg,#eef2ff,#e0e7ff);'
        'border:1px solid #c7d2fe;border-radius:12px;padding:16px;'
        'text-align:center;margin:12px 0;">'
        '<div style="font-size:14px;font-weight:700;color:#6366f1;'
        'margin-bottom:8px;">' + typing_effect(text) + '</div>'
        '<div style="display:flex;justify-content:center;gap:6px;">'
        '<div style="width:8px;height:8px;border-radius:50%;'
        'background:#6366f1;animation:bounce 1.4s infinite;"></div>'
        '<div style="width:8px;height:8px;border-radius:50%;'
        'background:#818cf8;animation:bounce 1.4s 0.2s infinite;"></div>'
        '<div style="width:8px;height:8px;border-radius:50%;'
        'background:#a5b4fc;animation:bounce 1.4s 0.4s infinite;"></div>'
        '</div>'
        '<style>@keyframes bounce {'
        '0%, 80%, 100% { transform: scale(0.6); opacity: 0.5; }'
        '40% { transform: scale(1); opacity: 1; }'
        '}</style>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def metric_skeleton():
    """Skeleton for metric cards."""
    html = (
        '<div style="background:linear-gradient(90deg,#f3f4f6 25%,#e5e7eb 50%,#f3f4f6 75%);'
        'background-size:200% 100%;animation:shimmer 1.5s infinite;'
        'border-radius:12px;height:80px;margin-bottom:8px;"></div>'
    )
    st.markdown(html, unsafe_allow_html=True)
