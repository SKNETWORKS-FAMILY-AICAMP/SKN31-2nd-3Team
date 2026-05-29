import streamlit as st
 
st.set_page_config(page_title="Resort Overbooking Manager", page_icon="🏨", layout="wide")
 
# ── 사이드바 네비게이션 ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏨 Resort Manager")
    st.divider()
    page = st.radio(
        "페이지 선택",
        ["📊 현황판", "📋 예약 리스트", "📈 오버부킹 추천", "🔔 알림 / 액션"],
        label_visibility="collapsed"
    )
    st.divider()
    st.caption("SKN31 2차 프로젝트")
 
# ── 페이지 라우팅 ────────────────────────────────────────────────────────────
if page == "📊 현황판":
    import main_board
    main_board.run()
 
elif page == "📋 예약 리스트":
    import reservation_list
    reservation_list.run()
 
elif page == "📈 오버부킹 추천":
    # import overbooking_recommend
    # overbooking_recommend.run()
    st.title("📈 오버부킹 추천")
    st.info("🚧 페이지 준비 중입니다.")
 
elif page == "🔔 알림 / 액션":
    # import alert_action
    # alert_action.run()
    st.title("🔔 알림 / 액션")
    st.info("🚧 페이지 준비 중입니다.")