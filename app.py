import streamlit as st
from scraper import get_intel_reports
from analyzer import analyze_article_intelligence
import datetime
import os

# ── إعداد المفتاح ──────────────────────────────────────────────────────────
os.environ["GROQ_API_KEY"] = "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"
# ── إعداد الصفحة ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="OSINT Intel Hub",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS مخصص ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Tajawal:wght@400;700;900&display=swap');

html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; direction: rtl; }
.stApp { background: #0a0d12; color: #c9d1d9; }
h1, h2, h3 { font-family: 'Share Tech Mono', monospace; }

.intel-card {
    background: #0d1117;
    border: 1px solid #21262d;
    border-radius: 8px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
    border-left: 3px solid #30363d;
    transition: border-color 0.2s;
}
.intel-card:hover { border-left-color: #58a6ff; }
.intel-card.critical { border-left-color: #f85149; }
.intel-card.high     { border-left-color: #e3b341; }
.intel-card.medium   { border-left-color: #388bfd; }
.intel-card.low      { border-left-color: #3fb950; }

.signal-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-family: 'Share Tech Mono', monospace;
    font-weight: bold;
    letter-spacing: 1px;
}
.sig-CRISIS     { background:#f85149; color:#fff; }
.sig-ESCALATING { background:#e3b341; color:#000; }
.sig-WATCH      { background:#388bfd; color:#fff; }
.sig-STABLE     { background:#3fb950; color:#000; }
.sig-OPPORTUNITY{ background:#bc8cff; color:#000; }

.threat-Critical { color: #f85149; font-weight: 900; }
.threat-High     { color: #e3b341; font-weight: 700; }
.threat-Medium   { color: #388bfd; }
.threat-Low      { color: #3fb950; }

.stat-box {
    background:#161b22;
    border:1px solid #21262d;
    border-radius:8px;
    padding:0.8rem 1rem;
    text-align:center;
}
.stat-num { font-size:2rem; font-weight:900; font-family:'Share Tech Mono',monospace; }

.section-label {
    font-size:0.75rem;
    text-transform:uppercase;
    letter-spacing:2px;
    color:#8b949e;
    font-family:'Share Tech Mono',monospace;
}
</style>
""", unsafe_allow_html=True)

# ── Session State ────────────────────────────────────────────────────────────
for key in ["intel_data", "last_updated", "is_loading"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key == "intel_data" else ("لم يتم الجلب بعد" if key == "last_updated" else False)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="border-bottom:1px solid #21262d; padding-bottom:1rem; margin-bottom:1.5rem;">
    <h1 style="color:#58a6ff; margin:0; font-size:1.6rem;">🛰️ OSINT INTELLIGENCE HUB</h1>
    <p style="color:#8b949e; margin:0.3rem 0 0; font-size:0.85rem; font-family:'Share Tech Mono',monospace;">
        منصة تحليل استخباراتي جيوسياسي مدعومة بـ Llama 3.3-70B — 20+ مصدر إعلامي دولي
    </p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ إعدادات الرصد")
    limit = st.slider("أخبار لكل مصدر", 1, 10, 5,
                      help="20 مصدر × هذا الرقم = إجمالي الأخبار")
    st.markdown(f"**📊 الإجمالي المتوقع:** ~{limit * 20} خبر")
    st.markdown("---")

    filter_signal = st.multiselect(
        "🔍 تصفية بـ Intel Signal",
        ["CRISIS", "ESCALATING", "WATCH", "STABLE", "OPPORTUNITY"],
        default=["CRISIS", "ESCALATING", "WATCH", "STABLE", "OPPORTUNITY"]
    )
    filter_threat = st.multiselect(
        "⚠️ تصفية بمستوى الخطورة",
        ["Critical", "High", "Medium", "Low"],
        default=["Critical", "High", "Medium", "Low"]
    )
    st.markdown("---")
    st.markdown(f"⏱️ **آخر تحديث**\n\n`{st.session_state.last_updated}`")

    if st.button("🔄 جلب وتحليل الأخبار", type="primary", use_container_width=True):
        with st.spinner("جاري جلب الأخبار من 20 مصدر وتحليلها..."):
            raw = get_intel_reports(limit_per_source=limit)
            results = []
            bar = st.progress(0, text="تحليل الأخبار...")
            for i, art in enumerate(raw):
                analysis = analyze_article_intelligence(art["title"], art["full_text"])
                results.append({**art, **analysis})
                bar.progress((i + 1) / len(raw), text=f"تحليل {i+1}/{len(raw)}")
            st.session_state.intel_data = results
            st.session_state.last_updated = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
            st.rerun()

# ── Dashboard Stats ──────────────────────────────────────────────────────────
data = st.session_state.intel_data
if data:
    filtered = [
        r for r in data
        if r.get("intel_signal", "WATCH") in filter_signal
        and r.get("threat_level", "Medium") in filter_threat
    ]

    c1, c2, c3, c4, c5 = st.columns(5)
    for col, label, val, color in [
        (c1, "إجمالي التقارير", len(filtered), "#58a6ff"),
        (c2, "🔴 CRISIS",       sum(1 for r in filtered if r.get("intel_signal") == "CRISIS"),      "#f85149"),
        (c3, "🟡 ESCALATING",   sum(1 for r in filtered if r.get("intel_signal") == "ESCALATING"),  "#e3b341"),
        (c4, "خطورة عالية",    sum(1 for r in filtered if r.get("threat_level") in ["High","Critical"]), "#e3b341"),
        (c5, "خطورة حرجة",    sum(1 for r in filtered if r.get("threat_level") == "Critical"),      "#f85149"),
    ]:
        col.markdown(f"""
        <div class="stat-box">
            <div class="stat-num" style="color:{color}">{val}</div>
            <div class="section-label">{label}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabs ─────────────────────────────────────────────────────────────────
    tabs = st.tabs(["📋 كل التقارير", "🚨 CRISIS & ESCALATING", "🔍 بحث وتصفية"])

    def render_report(report):
        threat = report.get("threat_level", "Low")
        signal = report.get("intel_signal", "WATCH")
        card_class = f"intel-card {threat.lower()}"

        hidden = report.get("hidden_actors", [])
        hidden_str = "، ".join(hidden) if hidden else "لا توجد بيانات"

        st.markdown(f"""
        <div class="{card_class}">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:0.4rem; margin-bottom:0.7rem;">
                <span style="font-weight:700; font-size:1.0rem; color:#e6edf3; max-width:75%;">{report['title']}</span>
                <span class="signal-badge sig-{signal}">{signal}</span>
            </div>
            <div style="display:flex; gap:1rem; flex-wrap:wrap; margin-bottom:0.8rem;">
                <span class="section-label">📰 {report.get('source_name','')}</span>
                <span class="section-label">🗂️ {report.get('category','')}</span>
                <span class="section-label threat-{threat}">⚠️ {threat}</span>
            </div>
            <div style="margin-bottom:0.5rem;">
                <span class="section-label">📝 الملخص التكتيكي</span><br>
                <span style="color:#c9d1d9;">{report.get('arabic_summary','')}</span>
            </div>
            <div style="margin-bottom:0.5rem;">
                <span class="section-label">🎯 الدافع الحقيقي</span><br>
                <span style="color:#ffa657;">{report.get('real_driver','')}</span>
            </div>
            <div style="margin-bottom:0.5rem;">
                <span class="section-label">🔮 التوقع الاستراتيجي (30-90 يوم)</span><br>
                <span style="color:#79c0ff;">{report.get('strategic_forecast','')}</span>
            </div>
            <div style="margin-bottom:0.7rem;">
                <span class="section-label">🌍 الأثر الجيوسياسي</span><br>
                <span style="color:#c9d1d9;">{report.get('geopolitical_impact','')}</span>
            </div>
            <div style="border-top:1px solid #21262d; padding-top:0.6rem; display:flex; justify-content:space-between; flex-wrap:wrap; gap:0.4rem;">
                <span style="color:#8b949e; font-size:0.8rem;">🌐 الدول: {', '.join(report.get('countries_involved',[]))}</span>
                <span style="color:#8b949e; font-size:0.8rem;">🕵️ فاعلون خفيون: {hidden_str}</span>
            </div>
            <div style="margin-top:0.5rem;">
                <a href="{report.get('link','#')}" target="_blank" style="color:#58a6ff; font-size:0.8rem; text-decoration:none;">🔗 المصدر الأصلي ↗</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tabs[0]:
        st.markdown(f"**{len(filtered)} تقرير** — مرتب حسب الخطورة")
        priority = {"Critical":0,"High":1,"Medium":2,"Low":3}
        sorted_data = sorted(filtered, key=lambda x: priority.get(x.get("threat_level","Low"), 3))
        for r in sorted_data:
            render_report(r)

    with tabs[1]:
        crisis_data = [r for r in filtered if r.get("intel_signal") in ["CRISIS","ESCALATING"]]
        st.markdown(f"**{len(crisis_data)} تقرير** يستدعي الانتباه الفوري")
        for r in crisis_data:
            render_report(r)

    with tabs[2]:
        search_q = st.text_input("🔍 ابحث في العناوين والملخصات", placeholder="مثال: إيران، الناتو، النفط...")
        cat_filter = st.multiselect("تصفية حسب الفئة", list({r.get("category","") for r in filtered}))
        search_results = [
            r for r in filtered
            if (not search_q or search_q.lower() in r.get("title","").lower() or search_q in r.get("arabic_summary",""))
            and (not cat_filter or r.get("category","") in cat_filter)
        ]
        st.markdown(f"**{len(search_results)} نتيجة**")
        for r in search_results:
            render_report(r)

else:
    st.markdown("""
    <div style="text-align:center; padding:4rem 0; color:#8b949e;">
        <div style="font-size:3rem;">🛰️</div>
        <h3 style="color:#58a6ff; font-family:'Share Tech Mono',monospace;">AWAITING INTEL FEED</h3>
        <p>اضغط على <strong>جلب وتحليل الأخبار</strong> من القائمة الجانبية لبدء الرصد</p>
    </div>
    """, unsafe_allow_html=True)
