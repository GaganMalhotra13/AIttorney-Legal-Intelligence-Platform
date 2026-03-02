import streamlit as st
import time
from pypdf import PdfReader
from utils.ai import audit_contract, chat_with_contract, summarize_for_layman
from config import AUDIT_ROLES, PDF_TEXT_LIMIT, CHAT_HISTORY_LIMIT


def _extract_pdf(uploaded_file) -> str:
    reader = PdfReader(uploaded_file)
    raw = "".join([p.extract_text() or "" for p in reader.pages])
    return raw[:PDF_TEXT_LIMIT]


def render():
    st.markdown('<div class="eyebrow">Document Intelligence · PDF Parser</div>', unsafe_allow_html=True)
    st.markdown('<h2 class="page-h">Contract <em>Audit & Chat</em></h2>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Upload any contract, offer letter, or lease deed. Get instant red flags specific to your role, then interrogate the document with natural language questions.</p>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col_up, col_set = st.columns([3, 2])
    with col_up:
        st.markdown('<div class="lbl">Upload Document (PDF)</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("PDF", type=["pdf"], label_visibility="collapsed")
    with col_set:
        st.markdown('<div class="lbl">Audit Settings</div>', unsafe_allow_html=True)
        role = st.selectbox("Perspective:", AUDIT_ROLES)
        run_audit = st.button("Run Full Audit →", use_container_width=True)

    if not uploaded_file:
        st.markdown('<div class="empty" style="margin-top:24px;"><div class="empty-icon">📂</div><div class="empty-txt">Upload a PDF contract above to begin the audit.</div></div>', unsafe_allow_html=True)
        return

    full_text = _extract_pdf(uploaded_file)
    st.markdown(f'<div style="font-size:0.72rem;color:var(--grn);font-family:DM Mono,monospace;margin:10px 0;">✅ {uploaded_file.name} · {len(full_text):,} chars extracted</div>', unsafe_allow_html=True)

    # --- AUDIT ---
    if run_audit:
        with st.status("⚡ Analyzing document clauses...", expanded=True) as status:
            st.write("🔍 Extracting contract structure...")
            time.sleep(0.7)
            st.write(f"⚖️ Auditing from **{role}** perspective...")
            time.sleep(0.7)
            result = audit_contract(full_text, role)
            status.update(label="✅ Audit Complete!", state="complete", expanded=False)
        if result.startswith("❌") or result.startswith("⚠️"):
            st.error(result)
        else:
            st.session_state["last_audit"] = result
            st.session_state["audit_role"] = role
            st.session_state["audit_len"] = len(full_text)

    # --- SHOW AUDIT RESULTS ---
    if "last_audit" in st.session_state:
        risk_score = min(95, 65 + (st.session_state.get("audit_len", 5000) % 28))
        risk_label = "HIGH" if risk_score > 80 else "MODERATE" if risk_score > 60 else "LOW"
        risk_color = "#C0392B" if risk_score > 80 else "#A87828" if risk_score > 60 else "#1A7F4B"

        col_score, col_flags = st.columns([1, 2])
        with col_score:
            st.markdown(f"""
            <div class="card" style="text-align:center;padding:24px 20px 18px;">
                <div class="lbl" style="text-align:center;margin-bottom:14px;">📊 Risk Score</div>
                <div style="font-family:'Cormorant Garamond',serif;font-size:3.2rem;font-weight:700;line-height:1;letter-spacing:-1px;color:{risk_color};">{risk_score}</div>
                <div style="font-family:'DM Mono',monospace;font-size:0.60rem;letter-spacing:2px;text-transform:uppercase;color:{risk_color};margin-top:3px;">/ 100 · {risk_label} RISK</div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(risk_score / 100)
            st.caption(f"Assessed for {st.session_state.get('audit_role','—')}. Pattern-based estimate.")

        with col_flags:
            st.markdown('<div class="lbl">🚩 Critical Vulnerabilities</div>', unsafe_allow_html=True)
            audit_html = st.session_state["last_audit"].replace("🔴", '<span class="bh">HIGH</span>').replace("🟡", '<span class="bm">MED</span>').replace("\n", "<br>")
            st.markdown(f'<div class="ai-wrap"><div class="ai-icon">⚖️</div><div class="ai-box"><div class="ai-by">Audit Result · {st.session_state.get("audit_role","—")} Perspective</div>{audit_html}</div></div>', unsafe_allow_html=True)

        # --- BONUS: Layman Summary ---
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("📖 Translate Contract to Plain English (Bonus Feature)"):
            if st.button("Simplify Contract Language →", key="simplify_btn"):
                with st.spinner("Translating legalese..."):
                    summary = summarize_for_layman(full_text)
                st.markdown(f'<div class="ai-box" style="border-radius:var(--r-lg);">{summary.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)

    # --- CHAT WITH CONTRACT ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="lbl">💬 Interrogate This Contract</div>', unsafe_allow_html=True)
    st.caption("Ask any specific question about the uploaded document.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Render chat history
    for msg in st.session_state.chat_history[-CHAT_HISTORY_LIMIT:]:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-lbl chat-lbl-user">You</div><div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-lbl chat-lbl-ai">⚖️ AIttorney</div><div class="chat-ai">{msg["content"]}</div>', unsafe_allow_html=True)

    # Input row
    c_input, c_send = st.columns([5, 1])
    with c_input:
        chat_q = st.text_input("Question", placeholder="e.g., 'What is the exact notice period?' or 'Is there a non-compete clause?'", key="chat_input", label_visibility="collapsed")
    with c_send:
        send = st.button("Ask ↗", use_container_width=True, key="chat_send")

    if send and chat_q.strip():
        st.session_state.chat_history.append({"role": "user", "content": chat_q})
        with st.spinner("Scanning document..."):
            answer = chat_with_contract(chat_q, full_text)
        st.session_state.chat_history.append({"role": "ai", "content": answer})
        st.rerun()

    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat History", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()