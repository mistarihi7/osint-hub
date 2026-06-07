import streamlit as st
from scraper import get_intel_reports
from analyzer import analyze_all_articles_at_once
import datetime
import os
import pandas as pd
import plotly.express as px

# ── إعداد المفتاح بأمان في السحاب ──────────────────────────────────────────
if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
else:
    os.environ["GROQ_API_KEY"] = "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"

# ── إعداد الصفحة ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="OSINT Intel Hub",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght=400;500;600;700;800&family=Tajawal:wght=400;500;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Tajawal', 'Inter', sans-serif;
    direction: rtl;
}
.stApp { background: #f0f4f8; color: #1a202c; }

.hub-header {
    background: linear-gradient(135deg, #1a1f2e 0%, #16213e 50%, #0f3460 100%);
    border-radius: 20px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 1rem;
    box-shadow: 0 10px 40px rgba(15,52,96,0.3);
}
.hub-title    { font-size:1.8rem; font-weight:800; color:#fff; margin:0; letter-spacing:-0.5px; }
.hub-subtitle { color:#94a3b8; font-size:0.85rem; margin:0.3rem 0 0; }
.hub-badge {
    background:rgba(99,179,237,0.15);
    border:1px solid rgba(99,179,237,0.3);
    color:#63b3ed;
    padding:0.4rem 1rem;
    border-radius:50px;
    font-size:0.78rem;
    font-weight:600;
}

.controls-card {
    background:#fff;
    border-radius:16px;
    padding:1.5rem 2rem;
    margin-bottom:1.5rem;
    box-shadow:0 2px 20px rgba(0,0,0,0.06);
    border:1px solid #e2e8f0;
}

.stat-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 0.8rem;
    margin-bottom: 1.5rem;
}
@media (max-width: 768px) {
    .stat-grid { grid-template-columns: repeat(2, 1fr); }
}

.stat-card {
    background:#fff;
    border-radius:14px;
    padding:1.2rem 1rem;
    text-align:center;
    box-shadow:0 2px 12px rgba(0,0,0,0.06);
    border:1px solid #e2e8f0;
    transition:transform 0.2s;
}
.stat-card:hover { transform:translateY(-2px); }
.stat-num {
    font-size:2.2rem;
    font-weight:800;
    line-height:1;
    font-family:'Inter',sans-serif;
}
.stat-label {
    font-size:0.72rem;
    color:#718096;
    font-weight:600;
    margin-top:0.3rem;
    text-transform:uppercase;
    letter-spacing:1px;
}

.viz-card {
    background:#fff;
    border-radius:16px;
    padding:1.2rem 1.5rem;
    box-shadow:0 2px 16px rgba(0,0,0,0.06);
    border:1px solid #e2e8f0;
    margin-bottom:1.5rem;
}
.viz-title {
    font-size:0.8rem;
    font-weight:700;
    text-transform:uppercase;
    letter-spacing:1.5px;
    color:#718096;
    margin-bottom:0.5rem;
    font-family:'Inter',sans-serif;
}

.intel-card {
    background:#fff;
    border-radius:16px;
    padding:1.5rem;
    margin-bottom:1rem;
    box-shadow:0 2px 16px rgba(0,0,0,0.06);
    border:1px solid #e2e8f0;
    border-right:5px solid #cbd5e0;
    transition:box-shadow 0.2s, transform 0.2s;
}
.intel-card:hover { box-shadow:0 8px 30px rgba(0,0,0,0.1); transform:translateY(-1px); }

/* ربط الألوان العربية بالـ CSS مباشرة */
.intel-card.حرج    { border-right-color:#fc5c65; }
.intel-card.عالي    { border-right-color:#f7b731; }
.intel-card.متوسط  { border-right-color:#4078f2; }
.intel-card.منخفض   { border-right-color:#26de81; }

.signal-badge {
    display:inline-flex;
    align-items:center;
    gap:4px;
    padding:4px 12px;
    border-radius:50px;
    font-size:0.7rem;
    font-weight:700;
    letter-spacing:0.8px;
    font-family:'Inter',sans-serif;
}
.sig-أزمة       { background:#fff0f0; color:#e53e3e; border:1.5px solid #fc8181; }
.sig-تصعيد   { background:#fffbeb; color:#d69e2e; border:1.5px solid #f6e05e; }
.sig-مراقبة    { background:#ebf8ff; color:#2b6cb0; border:1.5px solid #90cdf4; }
.sig-مستقر    { background:#f0fff4; color:#276749; border:1.5px solid #9ae6b4; }
.sig-فرصة  { background:#faf5ff; color:#6b46c1; border:1.5px solid #d6bcfa; }

.badge-threat-حرج    { background:#fff0f0; color:#e53e3e; border:1.5px solid #fc8181; }
.badge-threat-عالي    { background:#fffbeb; color:#d69e2e; border:1.5px solid #f6e05e; }
.badge-threat-متوسط  { background:#ebf8ff; color:#2b6cb0; border:1.5px solid #90cdf4; }
.badge-threat-منخفض   { background:#f0fff4; color:#276749; border:1.5px solid #9ae6b4; }

.field-label {
    font-size:0.68rem;
    text-transform:uppercase;
    letter-spacing:1.5px;
    color:#a0aec0;
    font-weight:700;
    margin-bottom:0.25rem;
    font-family:'Inter',sans-serif;
}
.field-value        { font-size:0.93rem; color:#2d374
