import streamlit as st

st.set_page_config(
    page_title="예약 전쟁",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# 스타일
# ─────────────────────────────────────────────
st.markdown("""
<style>

/* 상단 Streamlit 헤더/툴바 제거 */
header[data-testid="stHeader"]{
    display:none;
}
div[data-testid="stToolbar"]{
    display:none;
}

/* 본문 여백 */
.block-container{
    padding-top:0.8rem;
    padding-bottom:1rem;
}

/* 사이드바 */
section[data-testid="stSidebar"]{
    background: linear-gradient(
        180deg,
        #183153 0%,
        #234A73 100%
    );
}

/* 사이드바 전체 글씨 */
section[data-testid="stSidebar"] *{
    color:white !important;
}

/* 메뉴 버튼 */
div[data-testid="stRadio"] label{
    background: rgba(255,255,255,0.08);
    border-radius:12px;
    padding:12px;
    margin-bottom:8px;
}
div[data-testid="stRadio"] label:hover{
    background: rgba(255,255,255,0.18);
}

/* 메인 배너 */
.main-banner{
    background: linear-gradient(
        90deg,
        #183153,
        #2F5D8A
    );
    padding:20px;
    border-radius:16px;
    color:white;
    margin-bottom:15px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 메인 상단 배너
# ─────────────────────────────────────────────
st.markdown("""
<div class="main-banner">
    <h1 style="margin:0;">
        ⚔️ 예약 전쟁
    </h1>
    <p style="margin-top:8px;font-size:16px;">
        AI 노쇼 예측 기반 호텔 수익 최적화 시스템
    </p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 사이드바
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:10px 0'>
        <h1 style='margin-bottom:0'>⚔️ 예약 전쟁</h1>
        <p style='font-size:13px;color:#D6E4F0'>
            AI 노쇼 예측 기반<br>호텔 운영 관리 시스템
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    page = st.radio(
        "",
        ["📊 현황판","📋 예약 리스트","📈 오버부킹 추천","🔔 알림 / 액션"]
    )

    st.markdown("---")

    st.markdown("""
    <div style="background:rgba(255,255,255,0.08);padding:14px;border-radius:12px;font-size:14px;">
        <b>🎯 AI 분석 기능</b><br><br>
        • 노쇼 확률 예측<br>
        • 예상 취소 인원 계산<br>
        • 오버부킹 추천<br>
        • 객실 운영 최적화
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("SKN31 2차 프로젝트")

# ─────────────────────────────────────────────
# 페이지 라우팅
# ─────────────────────────────────────────────
if page == "📊 현황판":
    import main_board
    main_board.run()
elif page == "📋 예약 리스트":
    import reservation_list
    reservation_list.run()
elif page == "📈 오버부킹 추천":
    import overbooking_recommend
    overbooking_recommend.run()
elif page == "🔔 알림 / 액션":
    import alert_action
    alert_action.run()
