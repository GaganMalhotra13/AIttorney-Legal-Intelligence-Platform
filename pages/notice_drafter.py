"""pages/notice_drafter.py — Tab 3: AI Notice Drafter."""
import streamlit as st
from utils.ai import draft_notice
from config import NOTICE_TONES


def render():
    st.markdown('<div class="eyebrow">Automated Drafting · Legal Writing</div>', unsafe_allow_html=True)
    st.markdown('<h2 class="page-h">Notice <em>Drafter</em></h2>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Fill in the details below and AIttorney will generate a formal legal notice draft. Choose your tone, download, and hand to an advocate to review before sending.</p>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col_params, col_out = st.columns([1, 1])

    with col_params:
        st.markdown('<div class="lbl">Draft Parameters</div>', unsafe_allow_html=True)

        context = st.text_area(
            "Issue Description",
            placeholder="Describe the dispute in 2-3 sentences.\ne.g., 'Landlord refused to return ₹50,000 security deposit after I vacated the property on agreed date with 30-day written notice. It has been 3 months.'",
            height=120,
        )
        sender = st.text_input("Your Name / Sender", placeholder="Full Name or Law Firm Name")
        recipient = st.text_input("Recipient Name", placeholder="Opposite Party's Full Name")

        st.markdown('<div class="lbl" style="margin-top:14px;">Legal Tone</div>', unsafe_allow_html=True)
        tone = st.radio(
            "Tone",
            list(NOTICE_TONES.keys()),
            horizontal=True,
            label_visibility="collapsed",
        )
        st.caption(f"📋 {NOTICE_TONES[tone]}")

        generate = st.button("Generate Notice →", use_container_width=True)

    with col_out:
        st.markdown('<div class="lbl">Generated Draft</div>', unsafe_allow_html=True)

        if generate:
            if not context.strip():
                st.warning("Please describe the issue before generating.")
            else:
                with st.spinner("✍️ Drafting formal notice..."):
                    output = draft_notice(context, sender, recipient, tone)
                if output.startswith("❌") or output.startswith("⚠️"):
                    st.error(output)
                else:
                    st.session_state["notice_output"] = output
                    st.session_state["notice_tone"] = tone

        if "notice_output" in st.session_state and st.session_state["notice_output"]:
            st.markdown(f'<div class="notice-box">{st.session_state["notice_output"].replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            col_dl, col_copy = st.columns(2)
            with col_dl:
                st.download_button(
                    "📥 Download as TXT",
                    data=st.session_state["notice_output"],
                    file_name=f"Legal_Notice_{st.session_state.get('notice_tone','Draft').replace(' ','_')}.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
            with col_copy:
                if st.button("📋 View Raw Text", use_container_width=True):
                    st.code(st.session_state["notice_output"], language=None)
        else:
            st.markdown('<div class="empty"><div class="empty-icon">✍️</div><div class="empty-txt">Your generated notice will appear here.<br>Fill in the parameters and click Generate.</div></div>', unsafe_allow_html=True)