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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Tajawal:wght@400;500;700;800&display=swap');

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
.field-value        { font-size:0.93rem; color:#2d3748; line-height:1.6; }
.field-value.orange { color:#c05621; }
.field-value.blue   { color:#2c5282; }
.card-title         { font-size:1.05rem; font-weight:700; color:#1a202c; line-height:1.4; }

.card-footer {
    border-top:1px solid #f0f4f8;
    padding-top:0.8rem;
    margin-top:0.8rem;
    display:flex;
    justify-content:space-between;
    flex-wrap:wrap;
    gap:0.5rem;
}
.source-link { color:#4078f2; font-size:0.8rem; text-decoration:none; font-weight:600; }
.section-divider { height:1px; background:linear-gradient(90deg,#e2e8f0,transparent); margin:0.8rem 0; }

.awaiting-box {
    background:#fff;
    border-radius:20px;
    padding:5rem 2rem;
    text-align:center;
    box-shadow:0 2px 20px rgba(0,0,0,0.06);
    border:2px dashed #e2e8f0;
}

#MainMenu {visibility:hidden;} footer {visibility:hidden;} header {visibility:hidden;}

.stButton > button {
    background:linear-gradient(135deg,#1a1f2e,#0f3460) !important;
    color:white !important;
    border:none !important;
    border-radius:10px !important;
    font-weight:700 !important;
    font-family:'Tajawal',sans-serif !important;
    font-size:0.95rem !important;
    padding:0.6rem 1.5rem !important;
}
.stButton > button:hover { opacity:0.85 !important; }

.stTabs [data-baseweb="tab-list"] {
    background:#fff;
    border-radius:12px;
    padding:4px;
    border:1px solid #e2e8f0;
    gap:4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius:8px !important;
    font-weight:600 !important;
    font-family:'Tajawal',sans-serif !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
for key, default in [("intel_data", []), ("last_updated", "لم يتم الجلب بعد")]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hub-header">
    <div>
        <div class="hub-title">🛰️ OSINT Intelligence Hub</div>
        <div class="hub-subtitle">منصة تحليل استخباراتي جيوسياسي — Llama 3.3-70B × قنوات وصحف ومراكز قرار عالمية</div>
    </div>
    <div class="hub-badge">🔴 رصد ومتابعة حية</div>
</div>
""", unsafe_allow_html=True)

# ── Controls ──────────────────────────────────────────────────────────────────
st.markdown('<div class="controls-card">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    filter_signal = st.multiselect(
        "🔍 إشارة الرادار الاستخباراتي",
        ["أزمة", "تصعيد", "مراقبة", "مستقر", "فرصة"],
        default=["أزمة", "تصعيد", "مراقبة", "مستقر", "فرصة"]
    )
with col2:
    filter_threat = st.multiselect(
        "⚠️ مستوى الخطورة الجيوسياسية",
        ["حرج", "عالي", "متوسط", "منخفض"],
        default=["حرج", "عالي", "متوسط", "منخفض"]
    )
with col3:
    limit = st.slider("📡 بحوث / مصدر", 1, 8, 3)

col_info, col_btn = st.columns([3, 1])
with col_info:
    st.markdown(
        f"<p style='color:#718096;font-size:0.83rem;margin:0.5rem 0 0;'>⏱️ آخر تحديث: <b>{st.session_state.last_updated}</b></p>",
        unsafe_allow_html=True
    )
with col_btn:
    fetch = st.button("🔄 جلب وتحليل الأخبار", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── Fetch ─────────────────────────────────────────────────────────────────────
if fetch:
    with st.spinner("🌍 جاري جلب البحوث والدراسات العسكرية من خطوط الرصد..."):
        raw = get_intel_reports(limit_per_source=limit)
        
    if raw:
        with st.spinner("🧠 عملاق Llama 3.3-70B يفكك شفرات وموازين القوى كاملة بطلقة واحدة..."):
            results = analyze_all_articles_at_once(raw)
            
        st.session_state.intel_data = results
        st.session_state.last_updated = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
        st.rerun()
    else:
        st.warning("⚠️ فشل جلب أي أخبار من المصادر حالياً، تأكد من اتصال الإنترنت بالسيرفر.")

# ── Dashboard ─────────────────────────────────────────────────────────────────
data = st.session_state.intel_data

if data:
    analyzed = [r for r in data if not r.get("filtered", False)]
    
    filtered = [
        r for r in analyzed
        if r.get("intel_signal", "مراقبة") in filter_signal
        and r.get("threat_level", "متوسط") in filter_threat
    ]

    # ── Stat Cards ────────────────────────────────────────────────────────────
    stats = [
        ("إجمالي التقارير", len(filtered), "#2563eb"),
        ("🔴 أزمة", sum(1 for r in filtered if r.get("intel_signal") == "أزمة"), "#dc2626"),
        ("🟡 تصعيد", sum(1 for r in filtered if r.get("intel_signal") == "تصعيد"), "#d97706"),
        ("⚠️ عالية الخطورة", sum(1 for r in filtered if r.get("threat_level") in ["عالي","حرج"]), "#ea580c"),
        ("🔺 حرجة جداً", sum(1 for r in filtered if r.get("threat_level") == "حرج"), "#dc2626"),
    ]

    st.markdown('<div class="stat-grid">', unsafe_allow_html=True)
    scols = st.columns(5)
    for col, (label, val, color) in zip(scols, stats):
        with col:
            st.markdown(f"""
            <div class="stat-card" style="--accent:{color};">
                <div class="stat-num" style="color:{color};">{val}</div>
                <div class="stat-label">{label}</div>
            </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Visualization Hub ─────────────────────────────────────────────────────
    st.markdown('<div class="viz-card">', unsafe_allow_html=True)
    st.markdown('<div class="viz-title">📊 Visualization Hub — توزيع التهديدات وخريطة الأزمات</div>', unsafe_allow_html=True)

    vcol1, vcol2 = st.columns([1, 1])

    # Chart 1: Threat Level Donut
    with vcol1:
        threat_counts = {}
        for r in filtered:
            t = r.get("threat_level", "منخفض")
            threat_counts[t] = threat_counts.get(t, 0) + 1

        if threat_counts:
            df_threat = pd.DataFrame(list(threat_counts.items()), columns=["مستوى الخطورة", "العدد"])
            color_map = {"حرج": "#e53e3e", "عالي": "#f7b731", "متوسط": "#4078f2", "منخفض": "#26de81"}
            fig_pie = px.pie(
                df_threat, names="مستوى الخطورة", values="العدد", hole=0.55,
                color="مستوى الخطورة", color_discrete_map=color_map, title="توزيع مستويات الخطورة"
            )
            fig_pie.update_traces(
                textposition="outside", textinfo="percent+label",
                hovertemplate="<b>%{label}</b><br>العدد: %{value}<br>النسبة: %{percent}<extra></extra>"
            )
            fig_pie.update_layout(
                height=300, margin=dict(t=40, b=10, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Tajawal, Inter, sans-serif", size=13),
                showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    # Chart 2: Geopolitical Heatmap
    with vcol2:
        threat_weight = {"حرج": 4, "عالي": 3, "متوسط": 2, "منخفض": 1}
        country_scores = {}
        for r in filtered:
            weight = threat_weight.get(r.get("threat_level", "منخفض"), 1)
            for country in r.get("countries_involved", []):
                country = country.strip()
                if country and country.lower() not in ("unknown", "global", "عالمي", ""):
                    country_scores[country] = country_scores.get(country, 0) + weight

        if country_scores:
            df_map = pd.DataFrame(list(country_scores.items()), columns=["Country", "Crisis Score"])
            fig_map = px.choropleth(
                df_map, locations="Country", locationmode="country names", color="Crisis Score",
                color_continuous_scale=[[0.0, "#e8f5e9"], [0.25, "#80deea"], [0.5, "#f7b731"], [0.75, "#e53e3e"], [1.0, "#7b0000"]],
                title="خريطة الأزمات الجيوسياسية المعنية", labels={"Crisis Score": "مؤشر الأزمة"}
            )
            fig_map.update_layout(
                height=300, margin=dict(t=40, b=10, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)",
                geo=dict(showframe=False, showcoastlines=True, coastlinecolor="#cbd5e0", showland=True, landcolor="#f7fafc", showocean=True, oceancolor="#ebf8ff", projection_type="natural earth"),
                coloraxis_colorbar=dict(title="مؤشر", thickness=12, len=0.7), font=dict(family="Tajawal, Inter, sans-serif", size=12)
            )
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("لا توجد بيانات جغرافية كافية لعرض الخريطة حالياً.")

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Report Renderer Function ─────────────────────────────────────────────
    def render_report(report):
        threat = report.get("threat_level", "منخفض")
        signal = report.get("intel_signal", "مراقبة")
        hidden = report.get("hidden_actors", [])
        hidden_str = " · ".join(hidden) if hidden else "—"
        
        signal_class = f"sig-{signal}"
        badge_threat_class = f"badge-threat-{threat}"

        # تم تحديث السطر لقراءة العنوان المعرب arabic_title القادم من الـ AI
        st.markdown(f"""
        <div class="intel-card {threat}">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:0.5rem; margin-bottom:0.8rem;">
                <div class="card-title" style="max-width:75%; font-size:1.15rem; color:#1a202c; font-weight:700;">{report.get('arabic_title', report['title'])}</div>
                <div style="display:flex; gap:6px; flex-wrap:wrap;">
                    <span class="signal-badge {signal_class}">{signal}</span>
                    <span class="signal-badge {badge_threat_class}">{threat}</span>
                </div>
            </div>
            <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:1rem;">
                <span class="source-chip">📰 {report.get('source_name','')}</span>
                <span class="source-chip">🗂️ {report.get('category','')}</span>
                <span class="source-chip">🌐 {', '.join(report.get('countries_involved',[])[:3])}</span>
            </div>
            <div class="section-divider"></div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:1.5rem; margin-bottom:0.8rem;">
                <div>
                    <div class="field-label">📝 الملخص التكتيكي للمشهد</div>
                    <div class="field-value">{report.get('arabic_summary','')}</div>
                </div>
                <div>
                    <div class="field-label">🎯 الدافع الحقيقي وغير المعلن</div>
                    <div class="field-value orange">{report.get('real_driver','')}</div>
                </div>
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:1.5rem; margin-bottom:0.8rem;">
                <div>
                    <div class="field-label">🔮 التوقع الاستراتيجي المستقبلي (30-90 يوم)</div>
                    <div class="field-value blue">{report.get('strategic_forecast','')}</div>
                </div>
                <div>
                    <div class="field-label">🌍 الأثر على توازنات القوى والشؤون الدفاعية</div>
                    <div class="field-value">{report.get('geopolitical_impact','')}</div>
                </div>
            </div>
            <div class="card-footer">
                <span style="color:#94a3b8; font-size:0.75rem;">🕵️ فاعلون خفيون وجهات تورط محتملة: <b>{hidden_str}</b></span>
                <a class="source-link" href="{report.get('link','#')}" target="_blank">🔗 المصدر الأصلي للدراسة ↗</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tabs = st.tabs(["📋 كل التقارير", "🚨 ملف الأزمات والتصعيد", "🔍 بحث فرعي"])
    priority = {"حرج": 0, "عالي": 1, "متوسط": 2, "منخفض": 3}

    with tabs[0]:
        st.markdown(f"<p style='color:#718096;font-size:0.85rem;'><b>{len(filtered)}</b> تقرير استراتيجي — مرتب حسب الخطورة</p>", unsafe_allow_html=True)
        for r in sorted(filtered, key=lambda x: priority.get(x.get("threat_level", "منخفض"), 3)):
            render_report(r)

    with tabs[1]:
        crisis = [r for r in filtered if r.get("intel_signal") in ["أزمة", "تصعيد"]]
        st.markdown(f"<p style='color:#718096;font-size:0.85rem;'><b>{len(crisis)}</b> تقرير يستدعي المراقبة والدراسة الفورية</p>", unsafe_allow_html=True)
        for r in crisis:
            render_report(r)

    with tabs[2]:
        search_q = st.text_input("", placeholder="🔍 ابحث بالعنوان أو الملخص... مثال: صواريخ، مضيق، تسليح، الناتو")
        search_results = [
            r for r in filtered
            if not search_q
            or search_q.lower() in r.get("title", "").lower()
            or search_q in r.get("arabic_summary", "")
        ]
        st.markdown(f"<p style='color:#718096;font-size:0.85rem;'><b>{len(search_results)}</b> نتيجة مطابقة</p>", unsafe_allow_html=True)
        for r in search_results:
            render_report(r)

else:
    st.markdown("""
    <div class="awaiting-box">
        <div style="font-size:4rem;margin-bottom:1rem;">🛰️</div>
        <h2 style="color:#1a202c;font-weight:800;margin-bottom:0.5rem;">في انتظار البيانات الجيوسياسية</h2>
        <p style="color:#718096;font-size:1rem;">اضغط على <b>جلب وتحليل الأخبار</b> أعلاه لبدء رصد غرف العمليات الدولية</p>
        <div style="margin-top:1.5rem;display:flex;justify-content:center;gap:1rem;flex-wrap:wrap;">
            <span style="background:#ebf8ff;color:#2b6cb0;padding:6px 16px;border-radius:50px;font-size:0.8rem;font-weight:600;">مراكز أبحاث الحروب</span>
            <span style="background:#f0fff4;color:#276749;padding:6px 16px;border-radius:50px;font-size:0.8rem;font-weight:600;">Llama 3.3-70B</span>
            <span style="background:#faf5ff;color:#6b46c1;padding:6px 16px;border-radius:50px;font-size:0.8rem;font-weight:600;">تحليل استخباري معمق</span>
            <span style="background:#fff0f0;color:#e53e3e;padding:6px 16px;border-radius:50px;font-size:0.8rem;font-weight:600;">🔔 Telegram Alerts</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
