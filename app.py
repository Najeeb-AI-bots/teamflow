"""
TeamFlow — a lightweight Team-Management CRM for operations leaders (Streamlit).

Six modules:
  📊 Dashboard        — team health at a glance (headcount, quality, charts)
  👥 Team Roster      — add / view / manage team members
  📈 Performance      — weekly OA% · IR% · NRR% · ACHT per member, with trends
  🗒️ 1x1 & Coaching   — log coaching conversations and track action items
  🌴 Attendance & Leave — leave requests and status
  ✅ Tasks            — assign and track tasks / escalations

Free, no-key, CSV-backed demo seeded with SYNTHETIC data (no real people).
Built by Mohammed Abdul Najeeb · deploys on Streamlit Community Cloud.
"""

import datetime as dt
import pandas as pd
import streamlit as st

import data as db

st.set_page_config(page_title="TeamFlow CRM", page_icon="👥", layout="wide")

# ---------- styling (matches the VoiceCoach / portfolio look) ----------
st.markdown("""
<style>
  .stApp { background: linear-gradient(160deg, #0f1420 0%, #1b2a3a 100%); }
  .block-container { padding-top: 2rem; }
  h1,h2,h3,h4,p,label,.stMarkdown { color:#e8ecf3 !important; }
  .hero { background: linear-gradient(135deg,#1B2A3A 0%,#2d6a4f 100%);
    border-radius:18px; padding:24px 30px; margin-bottom:20px;
    box-shadow:0 10px 30px rgba(0,0,0,.35); }
  .hero h1 { color:#fff !important; margin:0; font-size:28px; font-weight:800; }
  .hero p { color:rgba(255,255,255,.9)!important; margin:6px 0 0; font-size:13px; }
  .card { background:rgba(255,255,255,.05); border:1px solid rgba(255,255,255,.12);
    border-radius:14px; padding:16px 18px; margin-bottom:14px; }
  div[data-testid="stMetric"] { background:rgba(255,255,255,.06);
    border:1px solid rgba(255,255,255,.1); border-radius:12px; padding:10px 14px; }
  .stButton>button { background:linear-gradient(135deg,#2d6a4f,#0b84ff); color:#fff;
    border:none; border-radius:10px; font-weight:700; padding:9px 18px; }
  .badge { display:inline-block; background:rgba(45,106,79,.25); color:#9fe0bf;
    border:1px solid rgba(45,106,79,.5); border-radius:100px; padding:3px 12px;
    font-size:12px; font-weight:600; margin-right:6px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>👥 TeamFlow</h1>
  <p>A lightweight team-management CRM for operations leaders — roster, performance,
  coaching, leave, and tasks in one place. Demo data is synthetic.</p>
</div>
""", unsafe_allow_html=True)

PAGES = ["📊 Dashboard", "👥 Team Roster", "📈 Performance",
         "🗒️ 1x1 & Coaching", "🌴 Attendance & Leave", "✅ Tasks"]
with st.sidebar:
    st.header("TeamFlow")
    page = st.radio("Go to", PAGES, index=0)
    st.markdown("---")
    st.caption("CSV-backed demo · synthetic data · no API key needed. "
               "Built by Mohammed Abdul Najeeb.")


def _member_options():
    m = db.members()
    return {int(r["id"]): r["name"] for _, r in m.iterrows()}


# ============================= DASHBOARD =============================
if page == "📊 Dashboard":
    st.subheader("📊 Team Health")
    m = db.members(); mt = db.metrics(); tk = db.tasks(); lv = db.leave()
    active = m[m["status"] == "Active"]
    latest_week = sorted(mt["week"].unique())[-1] if len(mt) else None
    latest = mt[mt["week"] == latest_week] if latest_week else mt

    c = st.columns(4)
    c[0].metric("Active members", len(active))
    c[1].metric("Avg OA%", f"{latest['oa_pct'].mean():.1f}%" if len(latest) else "—")
    c[2].metric("Avg IR%", f"{latest['ir_pct'].mean():.1f}%" if len(latest) else "—")
    c[3].metric("Open tasks", int((tk["status"] != "Done").sum()))

    st.markdown(f"<span class='badge'>Latest week: {latest_week}</span>", unsafe_allow_html=True)

    left, right = st.columns(2)
    with left:
        st.markdown("**Quality by member (latest week)**")
        if len(latest):
            q = latest.merge(m[["id", "name"]], left_on="member_id", right_on="id")
            chart = q.set_index("name")[["oa_pct", "ir_pct"]]
            st.bar_chart(chart)
    with right:
        st.markdown("**ACHT trend (team avg, sec)**")
        if len(mt):
            trend = mt.groupby("week")["acht_sec"].mean()
            st.line_chart(trend)

    st.markdown("**Upcoming / pending leave**")
    if len(lv):
        lv2 = lv.copy()
        lv2["member"] = lv2["member_id"].map(db.member_name)
        st.dataframe(lv2[["member", "type", "start_date", "end_date", "status"]],
                     use_container_width=True, hide_index=True)

# ============================= TEAM ROSTER =============================
elif page == "👥 Team Roster":
    st.subheader("👥 Team Roster")
    m = db.members()
    st.dataframe(m, use_container_width=True, hide_index=True)

    with st.expander("➕ Add a team member"):
        with st.form("add_member"):
            cc = st.columns(2)
            name = cc[0].text_input("Name")
            email = cc[1].text_input("Email")
            role = cc[0].selectbox("Role", ["Associate", "SME", "Team Lead", "Trainer"])
            tier = cc[1].selectbox("Tier", ["Tier 1", "Tier 2", "Tier 3"])
            start = cc[0].date_input("Start date", dt.date.today())
            if st.form_submit_button("Add member"):
                if name.strip():
                    db.add_member(name.strip(), role, tier, start, email.strip())
                    st.success(f"Added {name}."); st.rerun()
                else:
                    st.warning("Name is required.")

    with st.expander("✏️ Change a member's status"):
        opts = _member_options()
        if opts:
            mid = st.selectbox("Member", list(opts), format_func=lambda i: opts[i])
            new_status = st.selectbox("Status", ["Active", "On Leave", "Inactive"])
            if st.button("Update status"):
                db.update_member_status(mid, new_status)
                st.success("Updated."); st.rerun()

# ============================= PERFORMANCE =============================
elif page == "📈 Performance":
    st.subheader("📈 Performance Tracking")
    m = db.members(); mt = db.metrics()
    opts = _member_options()
    mid = st.selectbox("Member", list(opts), format_func=lambda i: opts[i])
    sub = mt[mt["member_id"] == mid].sort_values("week")

    if len(sub):
        latest = sub.iloc[-1]
        c = st.columns(4)
        c[0].metric("OA%", f"{latest['oa_pct']}%")
        c[1].metric("IR%", f"{latest['ir_pct']}%")
        c[2].metric("NRR%", f"{latest['nrr_pct']}%")
        c[3].metric("ACHT", f"{int(latest['acht_sec'])}s")
        st.markdown("**Quality trend (OA% / IR%)**")
        st.line_chart(sub.set_index("week")[["oa_pct", "ir_pct"]])
        st.markdown("**NRR% & ACHT trend**")
        st.line_chart(sub.set_index("week")[["nrr_pct"]])
        st.line_chart(sub.set_index("week")[["acht_sec"]])
        st.dataframe(sub[["week", "oa_pct", "ir_pct", "nrr_pct", "acht_sec"]],
                     use_container_width=True, hide_index=True)
    else:
        st.info("No metrics yet for this member.")

    with st.expander("➕ Log a weekly metric"):
        with st.form("add_metric"):
            wk = st.text_input("Week (e.g. 2026-W40)", "2026-W40")
            cc = st.columns(4)
            oa = cc[0].number_input("OA%", 0.0, 100.0, 92.0, 0.1)
            ir = cc[1].number_input("IR%", 0.0, 100.0, 90.0, 0.1)
            nrr = cc[2].number_input("NRR%", 0.0, 100.0, 5.0, 0.1)
            acht = cc[3].number_input("ACHT (sec)", 0, 3600, 480, 10)
            if st.form_submit_button("Save metric"):
                db.add_metric(mid, wk, oa, ir, nrr, int(acht))
                st.success("Metric saved."); st.rerun()

# ============================= 1x1 & COACHING =============================
elif page == "🗒️ 1x1 & Coaching":
    st.subheader("🗒️ 1x1 & Coaching Log")
    oo = db.one_on_ones()
    if len(oo):
        show = oo.copy(); show["member"] = show["member_id"].map(db.member_name)
        st.dataframe(show[["date", "member", "topic", "notes", "action_item", "status"]],
                     use_container_width=True, hide_index=True)
    opts = _member_options()
    with st.expander("➕ Log a 1x1 / coaching note"):
        with st.form("add_oo"):
            mid = st.selectbox("Member", list(opts), format_func=lambda i: opts[i])
            date = st.date_input("Date", dt.date.today())
            topic = st.text_input("Topic", "Quality coaching")
            notes = st.text_area("Notes")
            action = st.text_input("Action item")
            status = st.selectbox("Status", ["Open", "Done"])
            if st.form_submit_button("Save log"):
                db.add_one_on_one(mid, date, topic, notes, action, status)
                st.success("Logged."); st.rerun()

# ============================= ATTENDANCE & LEAVE =============================
elif page == "🌴 Attendance & Leave":
    st.subheader("🌴 Attendance & Leave")
    lv = db.leave()
    if len(lv):
        show = lv.copy(); show["member"] = show["member_id"].map(db.member_name)
        st.dataframe(show[["member", "type", "start_date", "end_date", "status"]],
                     use_container_width=True, hide_index=True)
    opts = _member_options()
    with st.expander("➕ Request / log leave"):
        with st.form("add_leave"):
            mid = st.selectbox("Member", list(opts), format_func=lambda i: opts[i])
            ltype = st.selectbox("Type", ["Annual Leave", "Sick Leave", "Unpaid Leave", "Comp Off"])
            cc = st.columns(2)
            start = cc[0].date_input("Start", dt.date.today())
            end = cc[1].date_input("End", dt.date.today())
            status = st.selectbox("Status", ["Pending", "Approved", "Rejected"])
            if st.form_submit_button("Save leave"):
                db.add_leave(mid, ltype, start, end, status)
                st.success("Leave saved."); st.rerun()

# ============================= TASKS =============================
elif page == "✅ Tasks":
    st.subheader("✅ Tasks & Escalations")
    tk = db.tasks()
    if len(tk):
        show = tk.copy(); show["assignee"] = show["assignee_id"].map(db.member_name)
        order = {"High": 0, "Medium": 1, "Low": 2}
        show["_p"] = show["priority"].map(order).fillna(9)
        show = show.sort_values(["status", "_p"])
        st.dataframe(show[["title", "assignee", "priority", "due_date", "status"]],
                     use_container_width=True, hide_index=True)

    opts = _member_options()
    cols = st.columns(2)
    with cols[0].expander("➕ Add a task"):
        with st.form("add_task"):
            title = st.text_input("Title")
            aid = st.selectbox("Assignee", list(opts), format_func=lambda i: opts[i])
            prio = st.selectbox("Priority", ["High", "Medium", "Low"])
            due = st.date_input("Due date", dt.date.today())
            if st.form_submit_button("Add task"):
                if title.strip():
                    db.add_task(title.strip(), aid, prio, due)
                    st.success("Task added."); st.rerun()
                else:
                    st.warning("Title is required.")
    with cols[1].expander("✏️ Update task status"):
        if len(tk):
            tid = st.selectbox("Task", list(tk["id"]),
                               format_func=lambda i: tk[tk["id"] == i].iloc[0]["title"])
            ns = st.selectbox("New status", ["Open", "In Progress", "Done"])
            if st.button("Update task"):
                db.set_task_status(tid, ns)
                st.success("Updated."); st.rerun()

st.markdown("---")
st.caption("TeamFlow · a portfolio CRM demo · synthetic data, no data stored server-side.")
