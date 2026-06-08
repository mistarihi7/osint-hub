import streamlit as st
from scraper import get_intel_reports
from analyzer import analyze_article_intelligence
import datetime, os, pandas as pd
import plotly.express as px

# ── API Key ───────────────────────────────────────────────────────────────────
try:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
except Exception:
    os.environ["GROQ_API_KEY"] = ""

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="OSINT Intel Hub", page_icon="🛰️",
                   layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Tajawal:wght@400;500;700;800&display=swap');
html,body,[class*="css"]{font-family:'Tajawal','Inter',sans-serif;direction:rtl;}
.stApp{background:#f0f4f8;color:#1a202c;}

.hub-header{
    background:linear-gradient(135deg,#1a1f2e 0%,#16213e 50%,#0f3460 100%);
    border-radius:20px;padding:2rem 2.5rem;margin-bottom:1.5rem;
    display:flex;align-items:center;justify-content:space-between;
    flex-wrap:wrap;gap:1rem;box-shadow:0 10px 40px rgba(15,52,96,0.3);
}
.hub-title{font-size:1.8rem;font-weight:800;color:#fff;margin:0;}
.hub-subtitle{color:#94a3b8;font-size:0.85rem;margin:0.3rem 0 0;}
.hub-badge{background:rgba(99,179,237,0.15);border:1px solid rgba(99,179,237,0.3);
    color:#63b3ed;padding:0.4rem 1rem;border-radius:50px;font-size:0.78rem;font-weight:600;}

.controls-card{background:#fff;border-radius:16px;padding:1.5rem 2rem;
    margin-bottom:1.5rem;box-shadow:0 2px 20px rgba(0,0,0,0.06);border:1px solid #e2e8f0;}

.stat-card{background:#fff;border-radius:14px;padding:1.2rem 1rem;text-align:center;
    box-shadow:0 2px 12px rgba(0,0,0,0.06);border:1px solid #e2e8f0;
    border-top:4px solid var(--accent);transition:transform 0.2s;}
.stat-card:hover{transform:translateY(-2px);}
.stat-num{font-size:2.2rem;font-weight:800;color:var(--accent);line-height:1;font-family:'Inter',sans-serif;}
.stat-label{font-size:0.72rem;color:#718096;font-weight:600;margin-top:0.3rem;
    text-transform:uppercase;letter-spacing:1px;}

.triage-bar{background:#f0fff4;border:1px solid #9ae6b4;border-radius:10px;
    padding:0.6rem 1.2rem;margin-bottom:1rem;font-size:0.83rem;color:#276749;}

.viz-card{background:#fff;border-radius:16px;padding:1.2rem 1.5rem;
    box-shadow:0 2px 16px rgba(0,0,0,0.06);border:1px solid #e2e8f0;margin-bottom:1.5rem;}
.viz-title{font-size:0.78rem;font-weight:700;text-transform:uppercase;
    letter-spacing:1.5px;color:#718096;margin-bottom:0.5rem;font-family:'Inter',sans-serif;}

.intel-card{background:#fff;border-radius:16px;padding:1.5rem;margin-bottom:1rem;
    box-shadow:0 2px 16px rgba(0,0,0,0.06);border:1px solid #e2e8f0;
    border-right:5px solid var(--ca,#cbd5e0);transition:box-shadow 0.2s,transform 0.2s;}
.intel-card:hover{box-shadow:0 8px 30px rgba(0,0,0,0.1);transform:translateY(-1px);}
.intel-card.critical{--ca:#fc5c65;}.intel-card.high{--ca:#f7b731;}
.intel-card.medium{--ca:#4078f2;}.intel-card.low{--ca:#26de81;}

.sig-badge{display:inline-flex;align-items:center;gap:4px;padding:4px 12px;
    border-radius:50px;font-size:0.7rem;font-weight:700;letter-spacing:0.8px;font-family:'Inter',sans-serif;}
.sig-CRISIS{background:#fff0f0;color:#e53e3e;border:1.5px solid #fc8181;}
.sig-ESCALATING{background:#fffbeb;color:#d69e2e;border:1.5px solid #f6e05e;}
.sig-WATCH{background:#ebf8ff;color:#2b6cb0;border:1.5px solid #90cdf4;}
.sig-STABLE{background:#f0fff4;color:#276749;border:1.5px solid #9ae6b4;}
.sig-OPPORTUNITY{background:#faf5ff;color:#6b46c1;border:1.5px solid #d6bcfa;}

.thr-Critical{color:#e53e3e;font-weight:700;}.thr-High{color:#d69e2e;font-weight:700;}
.thr-Medium{color:#2b6cb0;font-weight:600;}.thr-Low{color:#276749;font-weight:600;}

.fl{font-size:0.68rem;text-transform:uppercase;letter-spacing:1.5px;color:#a0aec0;
    font-weight:700;margin-bottom:0.25rem;font-family:'Inter',sans-serif;}
.fv{font-size:0.93rem;color:#2d3748;line-height:1.6;}
.fv.or{color:#c05621;}.fv.bl{color:#2c5282;}
.ct{font-size:1.05rem;font-weight:700;color:#1a202c;line-height:1.4;}
.cf{border-top:1px solid #f0f4f8;padding-top:0.8rem;margin-top:0.8rem;
    display:flex;justify-content:space-between;flex-wrap:wrap;gap:0.5rem;}
.sl{color:#4078f2;font-size:0.8rem;text-decoration:none;font-weight:600;}
.sd{height:1px;background:linear-gradient(90deg,#e2e8f0,transparent);margin:0.8rem 0;}

.awaiting{background:#fff;border-radius:20px;padding:5rem 2rem;text-align:center;
    box-shadow:0 2px 20px rgba(0,0,0,0.06);border:2px dashed #e2e8f0;}

#MainMenu{visibility:hidden;}footer{visibility:hidden;}header{visibility:hidden;}

.stButton>button{background:linear-gradient(135deg,#1a1f2e,#0f3460)!important;
    color:white!important;border:none!important;border-radius:10px!important;
    font-weight:700!important;font-family:'Tajawal',sans-serif!important;
    font-size:0.95rem!important;padding:0.6rem 1.5rem!important;}
.stButton>button:hover{opacity:0.85!important;}

.stTabs [data-baseweb="tab-list"]{background:#fff;border-radius:12px;
    padding:4px;border:1px solid #e2e8f0;gap:4px;}
.stTabs [data-baseweb="tab"]{border-radius:8px!important;font-weight:600!important;
    font-family:'Tajawal',sans-serif!important;}
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
for k, v in [("intel_data",[]),("last_updated","لم يتم الجلب بعد")]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hub-header">
  <div>
    <div class="hub-title">🛰️ OSINT Intelligence Hub</div>
    <div class="hub-subtitle">منصة تحليل استخباراتي جيوسياسي — Llama 3.3-70B × فلترة ذكية ثنائية المرحلة</div>
  </div>
  <div class="hub-badge">🔴 LIVE MONITORING</div>
</div>
""", unsafe_allow_html=True)

# ── Controls ──────────────────────────────────────────────────────────────────
st.markdown('<div class="controls-card">', unsafe_allow_html=True)
c1, c2, c3 = st.columns([2,2,1])
with c1:
    filter_signal = st.multiselect("🔍 Intel Signal",
        ["CRISIS","ESCALATING","WATCH","STABLE","OPPORTUNITY"],
        default=["CRISIS","ESCALATING","WATCH","STABLE","OPPORTUNITY"])
with c2:
    filter_threat = st.multiselect("⚠️ مستوى الخطورة",
        ["Critical","High","Medium","Low"],
        default=["Critical","High","Medium","Low"])
with c3:
    limit = st.slider("📡 أخبار / مصدر", 1, 8, 3)

ci, cb = st.columns([3,1])
with ci:
    st.markdown(
        f"<p style='color:#718096;font-size:0.83rem;margin:0.5rem 0 0;'>"
        f"⏱️ آخر تحديث: <b>{st.session_state.last_updated}</b> &nbsp;|&nbsp; "
        f"📊 متوقع: ~{limit*15} خبر من 15 مصدر</p>",
        unsafe_allow_html=True)
with cb:
    fetch = st.button("🔄 جلب وتحليل الأخبار", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── Fetch & Analyze ───────────────────────────────────────────────────────────
if fetch:
    with st.spinner("🌐 جاري جلب الأخبار..."):
        raw = get_intel_reports(limit_per_source=limit)

    results = []
    bar = st.progress(0, text="🤖 الفلترة والتحليل...")
    for i, art in enumerate(raw):
        result = analyze_article_intelligence(
            art["title"], art["full_text"], art.get("source_name",""))
        results.append({**art, **result})
        bar.progress((i+1)/len(raw), text=f"🤖 معالجة {i+1}/{len(raw)}...")

    st.session_state.intel_data   = results
    st.session_state.last_updated = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
    st.rerun()

# ── Dashboard ─────────────────────────────────────────────────────────────────
data = st.session_state.intel_data
if data:
    analyzed = [r for r in data if not r.get("filtered", False)]
    filtered = [r for r in analyzed
                if r.get("intel_signal","WATCH") in filter_signal
                and r.get("threat_level","Medium") in filter_threat]

    # Triage Info
    st.markdown(
        f'<div class="triage-bar">🤖 <b>الفلترة الذكية:</b> '
        f'جُلب <b>{len(data)}</b> خبر — '
        f'صُفِّي <b>{len(data)-len(analyzed)}</b> خبر غير مهم — '
        f'حُلِّل <b>{len(analyzed)}</b> خبر بعمق</div>',
        unsafe_allow_html=True)

    # Stat Cards
    stats = [
        ("التقارير المحللة", len(filtered), "#4078f2"),
        ("🔴 CRISIS",        sum(1 for r in filtered if r.get("intel_signal")=="CRISIS"), "#e53e3e"),
        ("🟡 ESCALATING",    sum(1 for r in filtered if r.get("intel_signal")=="ESCALATING"), "#d69e2e"),
        ("خطورة عالية",     sum(1 for r in filtered if r.get("threat_level") in ["High","Critical"]), "#d69e2e"),
        ("خطورة حرجة",     sum(1 for r in filtered if r.get("threat_level")=="Critical"), "#e53e3e"),
    ]
    cols = st.columns(5)
    for col,(lbl,val,clr) in zip(cols,stats):
        col.markdown(f'<div class="stat-card" style="--accent:{clr}"><div class="stat-num">{val}</div>'
                     f'<div class="stat-label">{lbl}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Visualization Hub ─────────────────────────────────────────────────────
    if filtered:
        st.markdown('<div class="viz-card">', unsafe_allow_html=True)
        st.markdown('<div class="viz-title">📊 Visualization Hub</div>', unsafe_allow_html=True)
        vc1, vc2 = st.columns(2)

        with vc1:
            tc = {}
            for r in filtered:
                t = r.get("threat_level","Low")
                tc[t] = tc.get(t,0)+1
            df_t = pd.DataFrame(list(tc.items()), columns=["Threat","Count"])
            fig1 = px.pie(df_t, names="Threat", values="Count", hole=0.55,
                          color="Threat",
                          color_discrete_map={"Critical":"#e53e3e","High":"#f7b731",
                                              "Medium":"#4078f2","Low":"#26de81"},
                          title="توزيع مستويات الخطورة")
            fig1.update_traces(textposition="outside", textinfo="percent+label")
            fig1.update_layout(height=300, margin=dict(t=40,b=10,l=10,r=10),
                paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
                font=dict(family="Tajawal,Inter,sans-serif",size=13),
                title_font=dict(size=13,color="#2d3748"))
            st.plotly_chart(fig1, use_container_width=True)

        with vc2:
            w = {"Critical":4,"High":3,"Medium":2,"Low":1}
            cs = {}
            for r in filtered:
                wt = w.get(r.get("threat_level","Low"),1)
                for c in r.get("countries_involved",[]):
                    c = c.strip()
                    if c and c.lower() not in ("unknown","global",""):
                        cs[c] = cs.get(c,0)+wt
            if cs:
                df_m = pd.DataFrame(list(cs.items()), columns=["Country","Score"])
                fig2 = px.choropleth(df_m, locations="Country",
                    locationmode="country names", color="Score",
                    color_continuous_scale=[[0,"#e8f5e9"],[0.3,"#80deea"],
                                            [0.6,"#f7b731"],[0.8,"#e53e3e"],[1,"#7b0000"]],
                    title="خريطة الأزمات الجيوسياسية")
                fig2.update_layout(height=300, margin=dict(t=40,b=10,l=0,r=0),
                    paper_bgcolor="rgba(0,0,0,0)",
                    geo=dict(showframe=False,showcoastlines=True,coastlinecolor="#cbd5e0",
                             showland=True,landcolor="#f7fafc",showocean=True,oceancolor="#ebf8ff",
                             projection_type="natural earth"),
                    font=dict(family="Tajawal,Inter,sans-serif",size=12),
                    title_font=dict(size=13,color="#2d3748"),
                    coloraxis_showscale=False)
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("لا توجد بيانات جغرافية كافية.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Report Renderer ───────────────────────────────────────────────────────
    def render_report(r):
        thr = r.get("threat_level","Low")
        sig = r.get("intel_signal","WATCH")
        hid = " — ".join(r.get("hidden_actors",[])) or "—"
        score_badge = (f'<span style="background:#edf2ff;color:#4078f2;padding:2px 8px;'
                       f'border-radius:20px;font-size:0.7rem;font-weight:700;font-family:Inter;">'
                       f'⭐ {r.get("triage_score","")}/10</span>'
                       if r.get("triage_score") else "")
        st.markdown(f"""
        <div class="intel-card {thr.lower()}">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:0.5rem;margin-bottom:0.8rem;">
            <div class="ct">{r.get('title','')}</div>
            <div style="display:flex;gap:0.4rem;flex-wrap:wrap;align-items:center;">
              {score_badge}
              <span class="sig-badge sig-{sig}">● {sig}</span>
            </div>
          </div>
          <div style="display:flex;gap:1.2rem;flex-wrap:wrap;margin-bottom:0.8rem;">
            <span style="font-size:0.75rem;color:#718096;">📰 {r.get('source_name','')}</span>
            <span style="font-size:0.75rem;color:#718096;">🗂️ {r.get('category','')}</span>
            <span class="thr-{thr}" style="font-size:0.75rem;">⚠️ {thr}</span>
          </div>
          <div class="sd"></div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin:0.8rem 0;">
            <div><div class="fl">📝 الملخص التكتيكي</div><div class="fv">{r.get('arabic_summary','')}</div></div>
            <div><div class="fl">🎯 الدافع الحقيقي</div><div class="fv or">{r.get('real_driver','')}</div></div>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:0.8rem;">
            <div><div class="fl">🔮 التوقع الاستراتيجي (30-90 يوم)</div><div class="fv bl">{r.get('strategic_forecast','')}</div></div>
            <div><div class="fl">🌍 الأثر الجيوسياسي</div><div class="fv">{r.get('geopolitical_impact','')}</div></div>
          </div>
          <div class="cf">
            <span style="color:#718096;font-size:0.78rem;">🌐 {', '.join(r.get('countries_involved',[]))}</span>
            <span style="color:#718096;font-size:0.78rem;">🕵️ {hid}</span>
            <a href="{r.get('link','#')}" target="_blank" class="sl">🔗 المصدر ↗</a>
          </div>
        </div>""", unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tabs = st.tabs(["📋 كل التقارير","🚨 CRISIS & ESCALATING","🔍 بحث"])
    pri  = {"Critical":0,"High":1,"Medium":2,"Low":3}

    with tabs[0]:
        st.markdown(f"<p style='color:#718096;font-size:0.85rem;'><b>{len(filtered)}</b> تقرير — مرتب حسب الخطورة</p>", unsafe_allow_html=True)
        for r in sorted(filtered, key=lambda x: pri.get(x.get("threat_level","Low"),3)):
            render_report(r)

    with tabs[1]:
        cr = [r for r in filtered if r.get("intel_signal") in ["CRISIS","ESCALATING"]]
        st.markdown(f"<p style='color:#718096;font-size:0.85rem;'><b>{len(cr)}</b> تقرير يستدعي الانتباه الفوري</p>", unsafe_allow_html=True)
        for r in cr:
            render_report(r)

    with tabs[2]:
        q = st.text_input("", placeholder="🔍 ابحث: إيران، الناتو، النفط، الصين...")
        sr = [r for r in filtered if not q
              or q.lower() in r.get("title","").lower()
              or q in r.get("arabic_summary","")]
        st.markdown(f"<p style='color:#718096;font-size:0.85rem;'><b>{len(sr)}</b> نتيجة</p>", unsafe_allow_html=True)
        for r in sr:
            render_report(r)

else:
    st.markdown("""
    <div class="awaiting">
      <div style="font-size:4rem;margin-bottom:1rem;">🛰️</div>
      <h2 style="color:#1a202c;font-weight:800;margin-bottom:0.5rem;">في انتظار البيانات</h2>
      <p style="color:#718096;">اضغط على <b>جلب وتحليل الأخبار</b> أعلاه لبدء الرصد</p>
      <div style="margin-top:1.5rem;display:flex;justify-content:center;gap:1rem;flex-wrap:wrap;">
        <span style="background:#ebf8ff;color:#2b6cb0;padding:6px 16px;border-radius:50px;font-size:0.8rem;font-weight:600;">15 مصدر دولي موثوق</span>
        <span style="background:#f0fff4;color:#276749;padding:6px 16px;border-radius:50px;font-size:0.8rem;font-weight:600;">فلترة ذكية ثنائية المرحلة</span>
        <span style="background:#faf5ff;color:#6b46c1;padding:6px 16px;border-radius:50px;font-size:0.8rem;font-weight:600;">Llama 3.3-70B</span>
        <span style="background:#fff0f0;color:#e53e3e;padding:6px 16px;border-radius:50px;font-size:0.8rem;font-weight:600;">🔔 Telegram Alerts</span>
      </div>
    </div>""", unsafe_allow_html=True)
