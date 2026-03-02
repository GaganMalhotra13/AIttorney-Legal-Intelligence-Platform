import streamlit as st
import time
from config import APP_NAME, APP_VERSION, APP_TAGLINE

DEMO_EMAIL    = "test123@testing.com"
DEMO_PASSWORD = "test123"


def render():
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown(f"""
        <div class="login-hero">
            <div class="login-logo">AI<span>ttorney</span></div>
            <div class="login-tagline">{APP_TAGLINE} &nbsp;·&nbsp; v{APP_VERSION}</div>
            <p class="login-desc">
                Plain language in. Full legal intelligence out.<br>
                Live court precedents, real scoring, actual PDF notices.
            </p>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        for col_obj, (icon, lbl, desc) in zip([c1, c2, c3], [
            ("🏛️", "Case Mirror", "Live RAG from IndianKanoon"),
            ("📄", "Contract Audit", "NLP clause detection"),
            ("📍", "Legal Roadmap", "Step-by-step action plan"),
        ]):
            with col_obj:
                st.markdown(f'<div class="feat"><div class="feat-icon">{icon}</div><div class="feat-label">{lbl}</div><div class="feat-desc">{desc}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="lbl">Access</div>', unsafe_allow_html=True)

        email = st.text_input(
            "Email",
            placeholder=f"Enter demo email: {DEMO_EMAIL}",
            key="login_email"
        )

        auto_password = DEMO_PASSWORD if email.strip() == DEMO_EMAIL else ""

        password = st.text_input(
            "Password",
            value=auto_password,
            type="password",
            placeholder="Auto-filled when correct email entered",
            key="login_pass"
        )

        st.markdown("<br>", unsafe_allow_html=True)
        login_btn = st.button("Enter Workspace →", use_container_width=True)

        if login_btn:
            if email.strip() != DEMO_EMAIL:
                st.markdown(f"""
                <div style="background:rgba(196,71,42,0.10);border:1px solid rgba(196,71,42,0.35);
                border-left:3px solid #C4472A;border-radius:8px;padding:12px 16px;margin-top:8px;">
                    <div style="font-size:0.78rem;color:#E8886E;font-weight:600;margin-bottom:3px;">
                        🔒 Access Restricted
                    </div>
                    <div style="font-size:0.74rem;color:#A8B4C0;line-height:1.6;">
                        Only the demo account can access this workspace.<br>
                        Use: <span style="font-family:'DM Mono',monospace;color:#E8886E;">{DEMO_EMAIL}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            elif password != DEMO_PASSWORD:
                st.markdown("""
                <div style="background:rgba(196,71,42,0.10);border:1px solid rgba(196,71,42,0.35);
                border-left:3px solid #C4472A;border-radius:8px;padding:12px 16px;margin-top:8px;">
                    <div style="font-size:0.78rem;color:#E8886E;font-weight:600;">
                        🔒 Incorrect Password
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.session_state.logged_in = True
                st.session_state.username  = email.strip()
                st.toast("Welcome to AIttorney!", icon="⚖️")
                time.sleep(0.3)
                st.rerun()

        st.markdown(f"""
        <div style="text-align:center;margin-top:14px;font-size:0.63rem;
             color:var(--txt-f);font-family:'DM Mono',monospace;line-height:1.8;">
            Demo access only &nbsp;·&nbsp;
            <span style="color:var(--red-pale);">{DEMO_EMAIL}</span>
            &nbsp;·&nbsp; Educational Use Only
        </div>
        """, unsafe_allow_html=True)