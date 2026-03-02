"""pages/roadmap.py — Tab 4: Procedural Legal Roadmap."""
import streamlit as st
from utils.ai import generate_roadmap
from config import JURISDICTIONS


QUICK_REF = [
    ("Consumer Forum",    "0 – 3 months"),
    ("Civil Court",       "6 – 18 months"),
    ("NI Act §138",       "3 – 12 months"),
    ("Labour Tribunal",   "3 – 6 months"),
    ("High Court Writ",   "6 – 24 months"),
    ("Lok Adalat",        "1 – 2 hearings"),
]


def _parse_steps(raw: str) -> list[dict]:
    """Parse AI output into structured step dicts."""
    steps = []
    blocks = raw.strip().split("STEP ")
    for block in blocks:
        if not block.strip():
            continue
        lines = [l.strip() for l in block.strip().splitlines() if l.strip()]
        if not lines:
            continue
        title   = lines[0].lstrip("1234567890.:— ").strip()
        action  = next((l.replace("Action:", "").strip() for l in lines if l.startswith("Action:")), "")
        law     = next((l.replace("Law:", "").strip() for l in lines if l.startswith("Law:")), "")
        timeline= next((l.replace("Timeline:", "").strip() for l in lines if l.startswith("Timeline:")), "")
        steps.append({"title": title, "action": action, "law": law, "timeline": timeline})
    return steps


def render():
    st.markdown('<div class="eyebrow">Procedural Intelligence · India-Specific</div>', unsafe_allow_html=True)
    st.markdown('<h2 class="page-h">Legal <em>Roadmap</em></h2>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Don\'t know what to do next? Describe your situation and AIttorney will map out an exact 4-step procedural action plan with applicable laws and timelines.</p>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col_in, col_map = st.columns([1, 2])

    with col_in:
        st.markdown('<div class="lbl">Your Situation</div>', unsafe_allow_html=True)
        query = st.text_area(
            "Situation",
            placeholder="e.g., 'I want to file a case for a bounced cheque of ₹2 lakhs against a business partner who has been avoiding me for 2 months.'",
            height=130,
            label_visibility="collapsed",
        )
        jurisdiction = st.selectbox("Jurisdiction", JURISDICTIONS)
        get_map = st.button("Generate Roadmap →", use_container_width=True)

        # Quick Reference Card
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="lbl">⚡ Typical Timelines</div>', unsafe_allow_html=True)
        qref_html = ""
        for label, val in QUICK_REF:
            qref_html += f'<div class="qref"><span class="qref-l">{label}</span><span class="qref-r">{val}</span></div>'
        st.markdown(f'<div class="card" style="padding:14px 16px;">{qref_html}</div>', unsafe_allow_html=True)

    with col_map:
        st.markdown('<div class="lbl">🗺️ Your 4-Step Action Plan</div>', unsafe_allow_html=True)

        if get_map:
            if not query.strip():
                st.warning("Please describe your situation first.")
            else:
                with st.spinner("⚡ Mapping legal procedures..."):
                    raw = generate_roadmap(query, jurisdiction)

                if raw.startswith("❌") or raw.startswith("⚠️"):
                    st.error(raw)
                else:
                    st.session_state["roadmap_steps"] = _parse_steps(raw)
                    st.session_state["roadmap_raw"] = raw

        if "roadmap_steps" in st.session_state and st.session_state["roadmap_steps"]:
            steps = st.session_state["roadmap_steps"]
            roadmap_html = '<div class="roadmap">'
            for i, step in enumerate(steps, 1):
                law_badge = f'<span class="rm-law">⚖️ {step["law"]}</span>' if step["law"] and step["law"].lower() != "n/a" else ""
                roadmap_html += f"""
                <div class="rm {'active' if i == 1 else ''}">
                    <div style="position:absolute;left:-39px;top:15px;
                        width:22px;height:22px;background:{'var(--gold)' if i==1 else 'var(--gold-dim)'};
                        border:1px solid var(--bdr-g);border-radius:50%;
                        font-family:DM Mono,monospace;font-size:0.62rem;
                        color:{'white' if i==1 else 'var(--gold)'};font-weight:600;
                        display:flex;align-items:center;justify-content:center;">
                        {i}
                    </div>
                    <div class="rm-title">Step {i}: {step['title']}</div>
                    <div class="rm-desc">{step['action']}</div>
                    {law_badge}
                    <div class="rm-time">⏱ {step['timeline']}</div>
                </div>
                """
            roadmap_html += "</div>"
            st.markdown(roadmap_html, unsafe_allow_html=True)

            with st.expander("📄 View Raw AI Output"):
                st.code(st.session_state.get("roadmap_raw", ""), language=None)
        else:
            st.markdown('<div class="empty"><div class="empty-icon">📍</div><div class="empty-txt">Describe your situation and click Generate Roadmap.<br>Your step-by-step action plan will appear here.</div></div>', unsafe_allow_html=True)