"""app.py — AIttorney v6"""
import streamlit as st
from config import APP_NAME, APP_TAGLINE, APP_VERSION
from styles import get_css
from utils.database import init_db
import pages.login as login_page
import pages.case_mirror as case_mirror
import pages.contract_audit as contract_audit
import pages.notice_drafter as notice_drafter
import pages.roadmap as roadmap
import pages.history as history

st.set_page_config(page_title=f"{APP_NAME} | {APP_TAGLINE}",
    layout="wide", page_icon="⚖️", initial_sidebar_state="expanded")
st.markdown(f"<style>{get_css()}</style>", unsafe_allow_html=True)
init_db()

DEFAULTS = {
    "logged_in":False,"username":"","chat_history":[],"notice_output":"",
    "notice_tone":"Professional","notice_meta":{},"audit_score":None,
    "audit_gemini":"","audit_role":"","audit_text":"","audit_file":"",
    "roadmap_steps":[],"roadmap_raw":"","vector_doc_id":"","main_query":"",
    # module results
    "opp":None,"ev":None,"set":None,"jur":None,"tl":None,
    "brief":None,"fir":None,"med":None,"lim":None,"cmp":None,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k] = v

if not st.session_state.logged_in:
    login_page.render(); st.stop()

name = st.session_state.username.split("@")[0].title()

with st.sidebar:
    st.markdown(f"""
    <div class="sb-logo">
        <div class="sb-logo-mark">
            <div class="sb-logo-icon">⚖️</div>
            <div class="sb-logo-name">AI<span>ttorney</span></div>
        </div>
        <div class="sb-logo-sub">{APP_TAGLINE} · v{APP_VERSION}</div>
    </div>
    <div class="sb-user">
        <div class="sb-av">👤</div>
        <div><div class="sb-uname">{name}</div>
        <div class="sb-urole">Pro Workspace · Active</div></div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sb-sec">', unsafe_allow_html=True)
    st.markdown('<span class="sb-lbl">⚙️ Settings</span>', unsafe_allow_html=True)
    language = st.radio("Lang", ["English","Hinglish (Mix)"], label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

    from utils.vector_store import is_available as vec_ok
    vd = ("dot-g","Semantic Search · Active") if vec_ok() else ("dot-a","Semantic Search · Optional")
    st.markdown(f"""
    <div class="sb-sec" style="margin-top:4px;">
        <span class="sb-lbl">System Status</span>
        <div class="sb-stat"><div class="dot dot-g"></div><span class="sb-stat-txt">Gemini API · Connected</span></div>
        <div class="sb-stat"><div class="dot dot-g"></div><span class="sb-stat-txt">18-Source Search · Live</span></div>
        <div class="sb-stat"><div class="dot dot-g"></div><span class="sb-stat-txt">11 AI Modules · Ready</span></div>
        <div class="sb-stat"><div class="dot dot-g"></div><span class="sb-stat-txt">NLP Scorer · Active</span></div>
        <div class="sb-stat"><div class="dot dot-g"></div><span class="sb-stat-txt">SQLite · Persistent</span></div>
        <div class="sb-stat"><div class="dot {vd[0]}"></div><span class="sb-stat-txt">{vd[1]}</span></div>
    </div>
    <div class="sb-dis">⚠️ Educational information only. Not legal advice. Always consult a licensed advocate.</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Sign Out", use_container_width=True):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

st.markdown('<div class="disc">⚠️ <strong>Educational Use Only.</strong> AIttorney is not a law firm. Always consult a licensed attorney for your specific situation.</div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏛️  Case Mirror", "📄  Contract Audit",
    "✍️  Notice Drafter", "📍  Legal Roadmap", "📂  My History"
])
with tab1: case_mirror.render(language)
with tab2: contract_audit.render()
with tab3: notice_drafter.render()
with tab4: roadmap.render()
with tab5: history.render()