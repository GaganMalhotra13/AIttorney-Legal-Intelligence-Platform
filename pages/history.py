"""
pages/history.py — Tab 5: Case History & Saved Work Dashboard
Shows all past searches, audits, notices from SQLite.
"""
import streamlit as st
from utils.database import get_case_history, get_audit_history, get_notice_history, get_user_stats


def _grade_color(grade: str) -> str:
    return {"HIGH": "var(--red)", "MODERATE": "var(--gold)", "LOW": "var(--grn)",
            "Strong": "var(--grn)", "Moderate": "var(--gold)", "Weak": "var(--red)"}.get(grade, "var(--txt-s)")


def render():
    st.markdown('<div class="eyebrow">Persistent Storage · SQLite</div>', unsafe_allow_html=True)
    st.markdown('<h2 class="page-h">Your <em>History</em></h2>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">All your past case searches, contract audits, and generated notices — saved locally and accessible across sessions.</p>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    username = st.session_state.get("username", "")
    stats    = get_user_stats(username)

    # ── Stats Row ─────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cases Analyzed",   stats["total_cases"])
    c2.metric("Avg. Win Prob.",    f"{stats['avg_win_prob']}%")
    c3.metric("Contracts Audited", stats["total_audits"])
    c4.metric("Notices Drafted",   stats["total_notices"])

    st.markdown("<br>", unsafe_allow_html=True)

    htab1, htab2, htab3 = st.tabs(["🏛️  Case Searches", "📄  Contract Audits", "✍️  Notices"])

    # ── Case History ──────────────────────────────────────────
    with htab1:
        history = get_case_history(username)
        if not history:
            st.markdown('<div class="empty"><div class="empty-icon">🏛️</div><div class="empty-txt">No case searches yet.<br>Run a Case Mirror analysis to see history here.</div></div>', unsafe_allow_html=True)
        else:
            for item in history:
                gc = _grade_color(item.get("grade", ""))
                st.markdown(f"""
                <div class="card" style="margin-bottom:10px;padding:14px 18px;">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;">
                        <div style="font-size:0.86rem;color:var(--txt);font-weight:500;flex:1;line-height:1.5;">{item['query'][:120]}...</div>
                        <div style="text-align:right;flex-shrink:0;">
                            <div style="font-family:'Cormorant Garamond',serif;font-size:1.5rem;font-weight:700;color:{gc};line-height:1;">{item['win_prob']}%</div>
                            <div style="font-family:'DM Mono',monospace;font-size:0.58rem;color:var(--txt-s);letter-spacing:1px;">{item.get('grade','').upper()} · {item['date']}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── Audit History ─────────────────────────────────────────
    with htab2:
        audits = get_audit_history(username)
        if not audits:
            st.markdown('<div class="empty"><div class="empty-icon">📄</div><div class="empty-txt">No audits yet.<br>Upload a contract in the Contract Audit tab.</div></div>', unsafe_allow_html=True)
        else:
            for item in audits:
                gc = _grade_color(item.get("grade", ""))
                st.markdown(f"""
                <div class="card" style="margin-bottom:10px;padding:14px 18px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;">
                        <div>
                            <div style="font-size:0.88rem;font-weight:600;color:var(--txt);">{item['filename'] or 'Unnamed Contract'}</div>
                            <div style="font-size:0.72rem;color:var(--txt-s);margin-top:2px;">Assessed as {item['role']} · {item['date']}</div>
                        </div>
                        <div style="text-align:right;">
                            <div style="font-family:'Cormorant Garamond',serif;font-size:1.5rem;font-weight:700;color:{gc};line-height:1;">{item['score']}</div>
                            <div style="font-family:'DM Mono',monospace;font-size:0.58rem;color:var(--txt-s);letter-spacing:1px;">{item.get('grade','').upper()} RISK</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── Notice History ────────────────────────────────────────
    with htab3:
        notices = get_notice_history(username)
        if not notices:
            st.markdown('<div class="empty"><div class="empty-icon">✍️</div><div class="empty-txt">No notices drafted yet.<br>Use the Notice Drafter tab to generate one.</div></div>', unsafe_allow_html=True)
        else:
            for item in notices:
                with st.expander(f"📋 {item['tone']} Notice  ·  {item['date']}  —  {item['context'][:60]}..."):
                    st.code(item["output"], language=None)
                    st.download_button(
                        "📥 Re-download",
                        data=item["output"],
                        file_name=f"Notice_{item['tone']}_{item['date']}.txt",
                        mime="text/plain",
                        key=f"dl_{item['date']}_{item['tone']}"
                    )