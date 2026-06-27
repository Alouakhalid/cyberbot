import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from auth.session import load_session, is_admin, clear_session
from auth.auth_manager import get_all_users, toggle_user_status
from database.logger import get_all_logs, get_topic_stats

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif; box-sizing: border-box; }
#MainMenu, footer, header, [data-testid="stToolbar"] { visibility: hidden !important; }
.stApp { background: #0d0d0d; }
[data-testid="stSidebar"] { background: #111 !important; border-right: 1px solid #2a2a2a; }

.stDataFrame { border: 1px solid #2a2a2a !important; border-radius: 12px !important; overflow: hidden !important; }
.stDataFrame thead tr th { background: #1a1a1a !important; color: #8e8ea0 !important; font-size: 12px !important; font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 0.5px !important; }
.stDataFrame tbody tr:hover { background: rgba(16,163,127,0.05) !important; }
.stDataFrame tbody tr td { color: #ececec !important; font-size: 13px !important; }

.stButton > button { background: transparent !important; border: 1px solid #3a3a3a !important; color: #8e8ea0 !important; border-radius: 8px !important; font-size: 12px !important; padding: 6px 14px !important; transition: all 0.2s !important; }
.stButton > button:hover { border-color: #ef4444 !important; color: #ef4444 !important; background: rgba(239,68,68,0.08) !important; }

[data-testid="stSelectbox"] > div > div { background: #1a1a1a !important; border: 1px solid #3a3a3a !important; border-radius: 8px !important; color: #ececec !important; }
[data-testid="stTextInput"] > div > div > input { background: #1a1a1a !important; border: 1px solid #3a3a3a !important; border-radius: 8px !important; color: #ececec !important; }

@keyframes fadeIn { from { opacity:0; transform:translateY(10px); } to { opacity:1; transform:translateY(0); } }

.admin-header {
    padding: 28px 0 20px;
    border-bottom: 1px solid #2a2a2a;
    margin-bottom: 28px;
    animation: fadeIn 0.4s ease;
}
.admin-title { font-size: 26px; font-weight: 700; color: #ececec; margin-bottom: 4px; }
.admin-sub   { font-size: 13px; color: #6b7280; }

.stat-card {
    background: #141414; border: 1px solid #2a2a2a; border-radius: 14px;
    padding: 24px 20px; text-align: center;
    transition: all 0.3s; animation: fadeIn 0.5s ease;
}
.stat-card:hover { border-color: #10a37f; transform: translateY(-2px); box-shadow: 0 8px 24px rgba(16,163,127,0.12); }
.stat-num   { font-size: 36px; font-weight: 800; color: #10a37f; margin-bottom: 4px; }
.stat-label { font-size: 12px; color: #8e8ea0; font-weight: 500; text-transform: uppercase; letter-spacing: 0.6px; }

.section-title { font-size: 16px; font-weight: 600; color: #ececec; margin: 28px 0 14px; padding-bottom: 10px; border-bottom: 1px solid #2a2a2a; }
.badge-active   { background: rgba(16,163,127,0.15); color: #34d399; padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }
.badge-banned   { background: rgba(239,68,68,0.15);  color: #f87171; padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }
.badge-admin    { background: rgba(245,158,11,0.15); color: #fbbf24; padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }
</style>
"""

PLOTLY_THEME = dict(
    paper_bgcolor="#141414",
    plot_bgcolor="#141414",
    font=dict(family="Inter", color="#8e8ea0", size=12),
    margin=dict(l=16, r=16, t=30, b=16),
)


def show():
    st.set_page_config(page_title="CyberEdu — Admin", page_icon="⚙️", layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)

    user = load_session()
    if not user or not is_admin():
        st.error("⛔ غير مصرح لك بالدخول.")
        st.stop()

    with st.sidebar:
        st.markdown("### ⚙️ Admin Panel")
        st.markdown("---")
        if st.button("💬  العودة للـ Chat"):
            st.session_state["page"] = "chat"
            st.rerun()
        if st.button("🚪  تسجيل الخروج"):
            clear_session()
            st.session_state["page"] = "login"
            st.rerun()

    st.markdown(f"""
    <div class="admin-header">
        <div class="admin-title">⚙️ لوحة تحكم الأدمن</div>
        <div class="admin-sub">مرحباً {user['username']} — مراقبة المستخدمين والمحادثات والإحصائيات</div>
    </div>
    """, unsafe_allow_html=True)

    all_users = get_all_users()
    all_logs  = get_all_logs(limit=500)
    topics    = get_topic_stats()

    active_count = sum(1 for u in all_users if u["is_active"])
    banned_count = len(all_users) - active_count

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="stat-num">{len(all_users)}</div><div class="stat-label">إجمالي المستخدمين</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card"><div class="stat-num">{active_count}</div><div class="stat-label">مستخدمون نشطون</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-card"><div class="stat-num">{banned_count}</div><div class="stat-label">محظورون</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="stat-card"><div class="stat-num">{len(all_logs)}</div><div class="stat-label">إجمالي المحادثات</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">👥 إدارة المستخدمين</div>', unsafe_allow_html=True)

    if all_users:
        search_user = st.text_input("🔍 بحث بالاسم", placeholder="اكتب اسم المستخدم...", label_visibility="collapsed")
        filtered = [u for u in all_users if search_user.lower() in u["username"].lower()] if search_user else all_users

        for u in filtered:
            col_name, col_email, col_role, col_status, col_action = st.columns([2, 3, 1.2, 1.2, 1.5])
            with col_name:
                st.markdown(f"**{u['username']}**")
            with col_email:
                st.caption(u["email"])
            with col_role:
                badge = "badge-admin" if u["role"] == "admin" else "badge-active"
                st.markdown(f'<span class="{badge}">{u["role"]}</span>', unsafe_allow_html=True)
            with col_status:
                status_badge = "badge-active" if u["is_active"] else "badge-banned"
                status_text  = "نشط ✅" if u["is_active"] else "محظور ⛔"
                st.markdown(f'<span class="{status_badge}">{status_text}</span>', unsafe_allow_html=True)
            with col_action:
                btn_label = "⛔ حظر" if u["is_active"] else "✅ تفعيل"
                if u["role"] != "admin":
                    if st.button(btn_label, key=f"toggle_{u['id']}"):
                        result = toggle_user_status(u["id"])
                        if result["success"]:
                            st.success(result["message"])
                            st.rerun()
            st.divider()

    col_chart1, col_chart2 = st.columns([1.6, 1])

    with col_chart1:
        st.markdown('<div class="section-title">💬 سجل المحادثات</div>', unsafe_allow_html=True)
        if all_logs:
            mode_filter = st.selectbox("فلتر بالـ Mode", ["الكل", "general", "red_team", "blue_team", "soc"], label_visibility="collapsed")
            logs_to_show = all_logs if mode_filter == "الكل" else [l for l in all_logs if l["mode"] == mode_filter]
            df_logs = pd.DataFrame(logs_to_show)[["username", "message", "mode", "timestamp"]]
            df_logs.columns = ["المستخدم", "الرسالة", "الـ Mode", "الوقت"]
            df_logs["الرسالة"] = df_logs["الرسالة"].str[:80] + "..."
            st.dataframe(df_logs, use_container_width=True, hide_index=True)
        else:
            st.info("لا توجد محادثات بعد.")

    with col_chart2:
        st.markdown('<div class="section-title">📊 أكثر المواضيع</div>', unsafe_allow_html=True)
        if topics:
            df_topics = pd.DataFrame(topics)
            fig = go.Figure(go.Bar(
                x=df_topics["count"],
                y=df_topics["topic"],
                orientation="h",
                marker=dict(
                    color=df_topics["count"],
                    colorscale=[[0, "#10a37f"], [0.5, "#0891b2"], [1, "#6366f1"]],
                    showscale=False,
                ),
            ))
            fig.update_layout(
                **PLOTLY_THEME,
                xaxis=dict(showgrid=False, color="#4b5563"),
                yaxis=dict(showgrid=False, color="#ececec"),
                height=320,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("لا توجد بيانات كويز بعد.")

    st.markdown('<div class="section-title">📈 توزيع الـ Modes</div>', unsafe_allow_html=True)
    if all_logs:
        mode_counts = pd.DataFrame(all_logs)["mode"].value_counts().reset_index()
        mode_counts.columns = ["mode", "count"]
        color_map = {"general": "#10a37f", "red_team": "#ef4444", "blue_team": "#3b82f6", "soc": "#f59e0b"}
        fig2 = px.pie(
            mode_counts, values="count", names="mode",
            color="mode", color_discrete_map=color_map,
            hole=0.55,
        )
        fig2.update_layout(**PLOTLY_THEME, height=300, showlegend=True,
                           legend=dict(font=dict(color="#ececec"), bgcolor="rgba(0,0,0,0)"))
        fig2.update_traces(textfont_color="#ececec", textfont_size=13)
        st.plotly_chart(fig2, use_container_width=True)
