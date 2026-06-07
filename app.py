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
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Tajawal:wght@400;500;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Tajawal', sans-serif;
    direction: rtl;
}

.stApp {
    background: #F0F4F8;
    color: #1a202c;
}

section[data-testid="stSidebar"] { display: none; }

/* ── Header ── */
.hub-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f172a 100%);
    border-radius: 20px;
    padding: 2.5rem 2rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.hub-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle at 30% 50%, rgba(56,139,253,0.15) 0%, transparent 50%),
                radial-gradient(circle at 70% 50%, rgba(139,92,246,0.1) 0%, transparent 50%);
    pointer-events: none;
}
.hub-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.9rem;
    font-weight: 800;
    color: #ffffff;
    margin: 0 0 0.3rem 0;
    letter-spacing: -0.5px;
}
.hub-subtitle {
    color: #94a3b8;
    font-size: 0.9rem;
    margin: 0;
}
.hub-badge {
    display: inline-block;
    background: rgba(56,139,253,0.2);
    border: 1px solid rgba(56,139,253,0.4);
    color: #60a5fa;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-family: 'Plus Jakarta Sans', monospace;
    margin-bottom: 0.8rem;
    letter-spacing: 1px;
}

/* ── Controls Card ── */
.controls-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
    border: 1px solid #e2e8f0;
}

/* ── Stat Cards ── */
.stat-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 0.8rem;
    margin-bottom: 1.5rem;
}
@media (max-width: 768px) {
    .stat-grid { grid-template-columns: repeat(2, 1fr); }
    .hub-title { font-size: 1.3rem; }
}
.stat-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 1.1rem 1rem;
    text-align: center;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    transition: transform 0.15s, box-shadow 0.15s;
}
.stat-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}
.stat-num {
    font-size: 1.9rem;
    font-weight: 800;
    font-family: 'Plus Jakarta Sans', sans-serif;
    line-height: 1;
    margin-bottom: 0.3rem;
}
.stat-label {
    font-size: 0.72rem;
    color: #64748b;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* ── Intel Card ── */
.intel-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 1.4rem 1.5rem;
    margin-bottom: 1rem;
    border: 1px solid #e2e8f0;
    border-top: 4px solid #e2e8f0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    transition: box-shadow 0.2s, transform 0.2s;
}
.intel-card:hover {
    box-shadow: 0 8px 30px rgba(0,0,0,0.1);
    transform: translateY(-1px);
}
.intel-card.critical { border-top-color: #ef4444; }
.intel-card.high     { border-top-color: #f59e0b; }
.intel-card.medium   { border-top-color: #3b82f6; }
.intel-card.low      { border-top-color: #10b981; }

.intel-title {
    font-size: 1rem;
    font-weight: 700;
    color: #0f172a;
    line-height: 1.4;
    margin-bottom: 0.8rem;
}

/* ── Badges ── */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    font-family: 'Plus Jakarta Sans', sans-serif;
}
.badge-crisis     { background:#fef2f2; color:#dc2626; border:1px solid #fecaca; }
.badge-escalating { background:#fffbeb; color:#d97706; border:1px solid #fde68a; }
.badge-watch      { background:#eff6ff; color:#2563eb; border:1px solid #bfdbfe; }
.badge-stable     { background:#f0fdf4; color:#16a34a; border:1px solid #bbf7d0; }
.badge-opportunity{ background:#faf5ff; color:#7c3aed; border:1px solid #ddd6fe; }

.badge-threat-critical { background:#fef2f2; color:#dc2626; border:1px solid #fecaca; }
.badge-threat-high     { background:#fffbeb; color:#d97706; border:1px solid #fde68a; }
.badge-threat-medium   { background:#eff6ff; color:#2563eb; border:1px solid #bfdbfe; }
.badge-threat-low      { background:#f0fdf4; color:#16a34a; border:1px solid #bbf7d0; }

/* ── Section Labels ── */
.field-label {
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #94a3b8;
    margin-bottom: 3px;
    font-family: 'Plus Jakarta Sans', sans-serif;
}
.field-value {
    font-size: 0.88rem;
    color: #334155;
    line-height: 1.6;
}
.field-value.orange { color: #c2410c; }
.field-value.blue   { color: #1d4ed8; }

.divider { border: none; border-top: 1px solid #f1f5f9; margin: 0.8rem 0; }

.source-chip {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.72rem;
    color: #64748b;
    font-weight: 500;
}

.stButton > button {
    background: linear-gradient(135deg, #1e3a5f, #2563eb) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Tajawal', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 0.6rem 1.5rem !important;
    transition: opacity 0.2s !important;
    box-shadow: 0 4px 12px rgba(37,99,235,0.3) !important;
}
.stButton > button:hover { opacity: 0.9 !important; }

[data-testid="stTabs"] button {
    font-family: 'Tajawal', sans-serif !important;
    font-weight: 600 !important;
}

.empty-state {
    text-align: center;
    padding: 4rem 0;
    background: #ffffff;
    border-radius: 20px;
    border: 2px dashed #e2e8f0;
}
.empty-icon { font-size: 3.5rem; margin-bottom: 1rem; }
.empty-title {
    font-size: 1.3rem;
    font-weight: 800;
    color: #1e3a5f;
    font-family: 'Plus Jakarta Sans', sans-serif;
    margin-bottom: 0.5rem;
}
.empty-sub { color: #94a3b8; font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

# ── Session State ────────────────────────────────────────────────────────────
for key in ["intel_data", "last_updated"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key == "intel_data" else "لم يتم الجلب بعد"

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hub-header">
    <div class="hub-badge">🛰️ OSINT INTELLIGENCE PLATFORM</div>
    <h1 class="hub-title">مركز الاستخبارات مفتوحة المصدر</h1>
    <p class="hub-subtitle">تحليل جيوسياسي واستراتيجي فوري — Llama 3.3-70B × 20+ مصدر إعلامي دولي رفيع المصداقية</p>
</div>
""", unsafe_allow_html=True)

# ── Controls ─────────────────────────────────────────────────────────────────
with st.container():
    st.markdown('<div class="controls-card">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        filter_signal = st.multiselect(
            "📡 Intel Signal",
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
        limit = st.selectbox("📰 أخبار/مصدر", [2, 3, 5, 7, 10], index=1)

    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        fetch = st.button("🔄 جلب وتحليل الأخبار", use_container_width=True)
    with col_info:
        st.markdown(f"<p style='color:#64748b; font-size:0.82rem; margin-top:0.7rem;'>⏱️ آخر تحديث: <strong>{st.session_state.last_updated}</strong> &nbsp;|&nbsp; 📊 الإجمالي المتوقع: <strong>~{limit * 20} خبر</strong></p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Fetch ─────────────────────────────────────────────────────────────────────
if fetch:
    with st.spinner("🌍 جاري جلب الأخبار من 20 مصدر دولي..."):
        raw = get_intel_reports(limit_per_source=limit)
    bar = st.progress(0, text="🧠 تحليل الأخبار بالذكاء الاصطناعي...")
    results = []
    for i, art in enumerate(raw):
        analysis = analyze_article_intelligence(art["title"], art["full_text"])
        results.append({**art, **analysis})
        bar.progress((i + 1) / len(raw), text=f"🧠 تحليل {i+1} من {len(raw)}...")
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
        ("إجمالي التقارير", len(filtered), "#2563eb"),
        ("🔴 CRISIS", sum(1 for r in filtered if r.get("intel_signal") == "CRISIS"), "#dc2626"),
        ("🟡 ESCALATING", sum(1 for r in filtered if r.get("intel_signal") == "ESCALATING"), "#d97706"),
        ("⚠️ عالية الخطورة", sum(1 for r in filtered if r.get("threat_level") in ["High","Critical"]), "#ea580c"),
        ("🔺 حرجة", sum(1 for r in filtered if r.get("threat_level") == "Critical"), "#dc2626"),
    ]

    cols = st.columns(5)
    for col, (label, val, color) in zip(cols, stats):
        col.markdown(f"""
        <div class="stat-card">
            <div class="stat-num" style="color:{color}">{val}</div>
            <div class="stat-label">{label}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    def render_report(report):
        threat = report.get("threat_level", "Low")
        signal = report.get("intel_signal", "WATCH")
        hidden = report.get("hidden_actors", [])
        hidden_str = " · ".join(hidden) if hidden else "—"
        signal_class = f"badge-{signal.lower()}"
        threat_class = f"badge-threat-{threat.lower()}"

        st.markdown(f"""
        <div class="intel-card {threat.lower()}">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:0.5rem; margin-bottom:0.8rem;">
                <div class="intel-title" style="max-width:75%;">{report['title']}</div>
                <div style="display:flex; gap:6px; flex-wrap:wrap;">
                    <span class="badge {signal_class}">{signal}</span>
                    <span class="badge {threat_class}">{threat}</span>
                </div>
            </div>
            <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:1rem;">
                <span class="source-chip">📰 {report.get('source_name','')}</span>
                <span class="source-chip">🗂️ {report.get('category','')}</span>
                <span class="source-chip">🌐 {', '.join(report.get('countries_involved',[])[:3])}</span>
            </div>
            <hr class="divider">
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-bottom:0.8rem;">
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
            <hr class="divider">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem;">
                <span style="color:#94a3b8; font-size:0.75rem;">🕵️ فاعلون خفيون: {hidden_str}</span>
                <a href="{report.get('link','#')}" target="_blank"
                   style="color:#2563eb; font-size:0.8rem; font-weight:600; text-decoration:none;">
                    🔗 المصدر الأصلي ↗
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    tabs = st.tabs(["📋 كل التقارير", "🚨 CRISIS & ESCALATING", "🔍 بحث"])

    with tabs[0]:
        priority = {"Critical":0,"High":1,"Medium":2,"Low":3}
        sorted_data = sorted(filtered, key=lambda x: priority.get(x.get("threat_level","Low"), 3))
        st.markdown(f"<p style='color:#64748b; font-size:0.85rem; margin-bottom:1rem;'>📊 {len(sorted_data)} تقرير مرتب حسب الخطورة</p>", unsafe_allow_html=True)
        for r in sorted_data:
            render_report(r)

    with tabs[1]:
        crisis_data = [r for r in filtered if r.get("intel_signal") in ["CRISIS","ESCALATING"]]
        st.markdown(f"<p style='color:#dc2626; font-size:0.85rem; margin-bottom:1rem; font-weight:700;'>🚨 {len(crisis_data)} تقرير يستدعي الانتباه الفوري</p>", unsafe_allow_html=True)
        for r in crisis_data:
            render_report(r)

    with tabs[2]:
        search_q = st.text_input("", placeholder="🔍 ابحث بالعنوان أو الملخص... مثال: إيران، الناتو، النفط")
        search_results = [
            r for r in filtered
            if not search_q or search_q.lower() in r.get("title","").lower() or search_q in r.get("arabic_summary","")
        ]
        st.markdown(f"<p style='color:#64748b; font-size:0.85rem; margin-bottom:1rem;'>🔍 {len(search_results)} نتيجة</p>", unsafe_allow_html=True)
        for r in search_results:
            render_report(r)

else:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">🛰️</div>
        <div class="empty-title">AWAITING INTEL FEED</div>
        <div class="empty-sub">اضغط على <strong>جلب وتحليل الأخبار</strong> أعلاه لبدء رصد العالم</div>
    </div>
    """, unsafe_allow_html=True)
