import streamlit as st
from scraper import get_intel_reports
from analyzer import analyze_article_intelligence
import datetime
import os

# ── إعداد المفتاح ──────────────────────────────────────────────────────────
try:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
except:
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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Tajawal:wght@400;500;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Tajawal', 'Inter', sans-serif;
    direction: rtl;
}

.stApp {
    background: #f0f4f8;
    color: #1a202c;
}

/* Header */
.hub-header {
    background: linear-gradient(135deg, #1a1f2e 0%, #16213e 50%, #0f3460 100%);
    border-radius: 20px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 1rem;
    box-shadow: 0 10px 40px rgba(15,52,96,0.3);
}

.hub-title {
    font-size: 1.8rem;
    font-weight: 800;
    color: #ffffff;
    margin: 0;
    letter-spacing: -0.5px;
}

.hub-subtitle {
    color: #94a3b8;
    font-size: 0.85rem;
    margin: 0.3rem 0 0;
}

.hub-badge {
    background: rgba(99,179,237,0.15);
    border: 1px solid rgba(99,179,237,0.3);
    color: #63b3ed;
    padding: 0.4rem 1rem;
    border-radius: 50px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.5px;
}

/* Controls card */
.controls-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 20px rgba(0,0,0,0.06);
    border: 1px solid #e2e8f0;
}

/* Stat cards */
.stat-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 1.2rem 1rem;
    text-align: center;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    border: 1px solid #e2e8f0;
    border-top: 4px solid var(--accent);
    transition: transform 0.2s;
}
.stat-card:hover { transform: translateY(-2px); }
.stat-num {
    font-size: 2.2rem;
    font-weight: 800;
    color: var(--accent);
    line-height: 1;
    font-family: 'Inter', sans-serif;
}
.stat-label {
    font-size: 0.75rem;
    color: #718096;
    font-weight: 600;
    margin-top: 0.3rem;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Intel cards */
.intel-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 16px rgba(0,0,0,0.06);
    border: 1px solid #e2e8f0;
    border-right: 5px solid var(--card-accent, #cbd5e0);
    transition: box-shadow 0.2s, transform 0.2s;
}
.intel-card:hover {
    box-shadow: 0 8px 30px rgba(0,0,0,0.1);
    transform: translateY(-1px);
}
.intel-card.critical { --card-accent: #fc5c65; }
.intel-card.high     { --card-accent: #f7b731; }
.intel-card.medium   { --card-accent: #4078f2; }
.intel-card.low      { --card-accent: #26de81; }

/* Signal badges */
.signal-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 12px;
    border-radius: 50px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.8px;
    font-family: 'Inter', sans-serif;
}
.sig-CRISIS     { background:#fff0f0; color:#e53e3e; border:1.5px solid #fc8181; }
.sig-ESCALATING { background:#fffbeb; color:#d69e2e; border:1.5px solid #f6e05e; }
.sig-WATCH      { background:#ebf8ff; color:#2b6cb0; border:1.5px solid #90cdf4; }
.sig-STABLE     { background:#f0fff4; color:#276749; border:1.5px solid #9ae6b4; }
.sig-OPPORTUNITY{ background:#faf5ff; color:#6b46c1; border:1.5px solid #d6bcfa; }

/* Threat colors */
.threat-Critical { color:#e53e3e; font-weight:700; }
.threat-High     { color:#d69e2e; font-weight:700; }
.threat-Medium   { color:#2b6cb0; font-weight:600; }
.threat-Low      { color:#276749; font-weight:600; }

/* Section labels */
.field-label {
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #a0aec0;
    font-weight: 700;
    margin-bottom: 0.25rem;
    font-family: 'Inter', sans-serif;
}

.field-value { font-size: 0.95rem; color: #2d3748; line-height: 1.6; }
.field-value.orange { color: #c05621; }
.field-value.blue   { color: #2c5282; }

.card-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #1a202c;
    line-height: 1.4;
}

.card-meta span {
    font-size: 0.75rem;
    color: #718096;
    font-weight: 500;
}

.card-footer {
    border-top: 1px solid #f0f4f8;
    padding-top: 0.8rem;
    margin-top: 0.8rem;
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.source-link {
    color: #4078f2;
    font-size: 0.8rem;
    text-decoration: none;
    font-weight: 600;
}

/* Divider */
.section-divider {
    height: 1px;
    background: linear-gradient(90deg, #e2e8f0, transparent);
    margin: 1rem 0;
}

/* Awaiting */
.awaiting-box {
    background: #ffffff;
    border-radius: 20px;
    padding: 5rem 2rem;
    text-align: center;
    box-shadow: 0 2px 20px rgba(0,0,0,0.06);
    border: 2px dashed #e2e8f0;
}

/* Hide streamlit default elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Streamlit button override */
.stButton > button {
    background: linear-gradient(135deg, #1a1f2e, #0f3460) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-family: 'Tajawal', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 0.6rem 1.5rem !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #ffffff;
    border-radius: 12px;
    padding: 4px;
    border: 1px solid #e2e8f0;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-family: 'Tajawal', sans-serif !important;
}

/* Multiselect */
.stMultiSelect [data-baseweb="tag"] {
    background: #ebf8ff !important;
    color: #2b6cb0 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session State ────────────────────────────────────────────────────────────
for key, default in [("intel_data", []), ("last_updated", "لم يتم الجلب بعد")]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hub-header">
    <div>
        <div class="hub-title">🛰️ OSINT Intelligence Hub</div>
        <div class="hub-subtitle">منصة تحليل استخباراتي جيوسياسي — Llama 3.3-70B × 20+ مصدر دولي</div>
    </div>
    <div class="hub-badge">🔴 LIVE MONITORING</div>
</div>
""", unsafe_allow_html=True)

# ── Controls ─────────────────────────────────────────────────────────────────
with st.container():
    st.markdown('<div class="controls-card">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        filter_signal = st.multiselect(
            "🔍 Intel Signal",
            ["CRISIS", "ESCALATING", "WATCH", "STABLE", "OPPORTUNITY"],
            default=["CRISIS", "ESCALATING", "WATCH", "STABLE", "OPPORTUNITY"]
        )
    with col2:
        filter_threat = st.multiselect(
            "⚠️ مستوى الخطورة",
            ["Critical", "High", "Medium", "Low"],
            default=["Critical", "High", "Medium", "Low"]
        )
    with col3:
        limit = st.slider("📡 أخبار / مصدر", 1, 8, 3)

    col_info, col_btn = st.columns([3, 1])
    with col_info:
        st.markdown(f"<p style='color:#718096; font-size:0.83rem; margin:0.5rem 0 0;'>⏱️ آخر تحديث: <b>{st.session_state.last_updated}</b> &nbsp;|&nbsp; 📊 متوقع: ~{limit * 20} خبر من 20 مصدر</p>", unsafe_allow_html=True)
    with col_btn:
        fetch = st.button("🔄 جلب وتحليل الأخبار", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Fetch ─────────────────────────────────────────────────────────────────────
if fetch:
    with st.spinner("🌐 جاري جلب الأخبار من 20 مصدر عالمي..."):
        raw = get_intel_reports(limit_per_source=limit)
    results = []
    bar = st.progress(0, text="🤖 تحليل الأخبار بالذكاء الاصطناعي...")
    for i, art in enumerate(raw):
        analysis = analyze_article_intelligence(art["title"], art["full_text"])
        results.append({**art, **analysis})
        bar.progress((i + 1) / len(raw), text=f"🤖 تحليل {i+1} من {len(raw)}...")
    st.session_state.intel_data = results
    st.session_state.last_updated = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
    st.rerun()

# ── Dashboard ─────────────────────────────────────────────────────────────────
data = st.session_state.intel_data

if data:
    filtered = [
        r for r in data
        if r.get("intel_signal", "WATCH") in filter_signal
        and r.get("threat_level", "Medium") in filter_threat
    ]

    # Stats
    stats = [
        ("التقارير الكلية",  len(filtered),                                                            "#4078f2"),
        ("🔴 CRISIS",        sum(1 for r in filtered if r.get("intel_signal") == "CRISIS"),             "#e53e3e"),
        ("🟡 ESCALATING",    sum(1 for r in filtered if r.get("intel_signal") == "ESCALATING"),         "#d69e2e"),
        ("خطورة عالية",     sum(1 for r in filtered if r.get("threat_level") in ["High","Critical"]),   "#d69e2e"),
        ("خطورة حرجة",     sum(1 for r in filtered if r.get("threat_level") == "Critical"),             "#e53e3e"),
    ]
    cols = st.columns(5)
    for col, (label, val, color) in zip(cols, stats):
        col.markdown(f"""
        <div class="stat-card" style="--accent:{color}">
            <div class="stat-num">{val}</div>
            <div class="stat-label">{label}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Render function
    def render_report(report):
        threat = report.get("threat_level", "Low")
        signal = report.get("intel_signal", "WATCH")
        hidden = report.get("hidden_actors", [])
        hidden_str = " — ".join(hidden) if hidden else "—"

        st.markdown(f"""
        <div class="intel-card {threat.lower()}">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:0.5rem; margin-bottom:0.8rem;">
                <div class="card-title">{report.get('title','')}</div>
                <span class="signal-badge sig-{signal}">● {signal}</span>
            </div>
            <div class="card-meta" style="display:flex; gap:1.2rem; flex-wrap:wrap; margin-bottom:1rem;">
                <span>📰 {report.get('source_name','')}</span>
                <span>🗂️ {report.get('category','')}</span>
                <span class="threat-{threat}">⚠️ {threat}</span>
            </div>
            <div class="section-divider"></div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin:0.8rem 0;">
                <div>
                    <div class="field-label">📝 الملخص التكتيكي</div>
                    <div class="field-value">{report.get('arabic_summary','')}</div>
                </div>
                <div>
                    <div class="field-label">🎯 الدافع الحقيقي</div>
                    <div class="field-value orange">{report.get('real_driver','')}</div>
                </div>
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-bottom:0.8rem;">
                <div>
                    <div class="field-label">🔮 التوقع الاستراتيجي (30-90 يوم)</div>
                    <div class="field-value blue">{report.get('strategic_forecast','')}</div>
                </div>
                <div>
                    <div class="field-label">🌍 الأثر الجيوسياسي</div>
                    <div class="field-value">{report.get('geopolitical_impact','')}</div>
                </div>
            </div>
            <div class="card-footer">
                <span style="color:#718096; font-size:0.78rem;">🌐 {', '.join(report.get('countries_involved',[]))}</span>
                <span style="color:#718096; font-size:0.78rem;">🕵️ {hidden_str}</span>
                <a href="{report.get('link','#')}" target="_blank" class="source-link">🔗 المصدر الأصلي ↗</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    tabs = st.tabs(["📋 كل التقارير", "🚨 CRISIS & ESCALATING", "🔍 بحث"])

    priority = {"Critical":0,"High":1,"Medium":2,"Low":3}

    with tabs[0]:
        st.markdown(f"<p style='color:#718096; font-size:0.85rem;'><b>{len(filtered)}</b> تقرير — مرتب حسب الخطورة</p>", unsafe_allow_html=True)
        for r in sorted(filtered, key=lambda x: priority.get(x.get("threat_level","Low"), 3)):
            render_report(r)

    with tabs[1]:
        crisis = [r for r in filtered if r.get("intel_signal") in ["CRISIS","ESCALATING"]]
        st.markdown(f"<p style='color:#718096; font-size:0.85rem;'><b>{len(crisis)}</b> تقرير يستدعي الانتباه الفوري</p>", unsafe_allow_html=True)
        for r in crisis:
            render_report(r)

    with tabs[2]:
        search_q = st.text_input("", placeholder="🔍 ابحث: إيران، الناتو، النفط، الصين...")
        results_s = [
            r for r in filtered
            if not search_q or search_q.lower() in r.get("title","").lower() or search_q in r.get("arabic_summary","")
        ]
        st.markdown(f"<p style='color:#718096; font-size:0.85rem;'><b>{len(results_s)}</b> نتيجة</p>", unsafe_allow_html=True)
        for r in results_s:
            render_report(r)

else:
    st.markdown("""
    <div class="awaiting-box">
        <div style="font-size:4rem; margin-bottom:1rem;">🛰️</div>
        <h2 style="color:#1a202c; font-weight:800; margin-bottom:0.5rem;">في انتظار البيانات</h2>
        <p style="color:#718096; font-size:1rem;">اضغط على <b>جلب وتحليل الأخبار</b> أعلاه لبدء الرصد الاستخباراتي</p>
        <div style="margin-top:1.5rem; display:flex; justify-content:center; gap:1rem; flex-wrap:wrap;">
            <span style="background:#ebf8ff; color:#2b6cb0; padding:6px 16px; border-radius:50px; font-size:0.8rem; font-weight:600;">20+ مصدر دولي</span>
            <span style="background:#f0fff4; color:#276749; padding:6px 16px; border-radius:50px; font-size:0.8rem; font-weight:600;">Llama 3.3-70B</span>
            <span style="background:#faf5ff; color:#6b46c1; padding:6px 16px; border-radius:50px; font-size:0.8rem; font-weight:600;">تحليل جيوسياسي عميق</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
