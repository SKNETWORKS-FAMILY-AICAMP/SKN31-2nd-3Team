import pandas as pd
import streamlit as st
import joblib
from datetime import date

# ── 설정 ───────────────────────────────────────────────────────────────────
TOTAL_ROOMS = 200   # 전체 객실 수

# ── 모델 / 데이터 로드 (캐싱) ───────────────────────────────────────────────
@st.cache_resource
def load_model():
    return joblib.load('model&preprocessing/best_model.pkl')

@st.cache_data
def load_data():
    return pd.read_csv('Dataset/mock_dataset.csv')


def run():
    model = load_model()
    df = load_data().copy()

    # ── 예측 ───────────────────────────────────────────────────────────────
    feature_cols = [c for c in df.columns if c not in ['customer_name', 'status', 'is_canceled']]
    df['취소확률'] = (model.predict_proba(df[feature_cols])[:, 1] * 100).round(1)

    # ── 기준일 (컴퓨터 오늘 날짜) ───────────────────────────────────────────
    today = date.today()
    today_str = today.strftime('%Y-%m-%d')

    # ── 헤더 ───────────────────────────────────────────────────────────────
    col_title, col_info = st.columns([2, 1])
    with col_title:
        st.markdown('<p style="font-size:28px; font-weight:700; margin:0;">Resort Overbooking Manager</p>',
                    unsafe_allow_html=True)
    with col_info:
        st.markdown(
            f'<p style="text-align:right; color:#9E9890; font-size:13px; padding-top:12px;">'
            f'기준일: {today.strftime("%Y년 %m월 %d일")} &nbsp;|&nbsp; 전체 객실: {TOTAL_ROOMS}실</p>',
            unsafe_allow_html=True
        )

    st.divider()

    # ── KPI 계산 ────────────────────────────────────────────────────────────
    active_cnt    = int((df['status'] != 'Checked-Out').sum())   # 활성 예약 (체크아웃 제외)
    inhouse_cnt   = int((df['status'] == 'In-House').sum())      # 현재 투숙 중
    occupancy     = inhouse_cnt / TOTAL_ROOMS * 100              # 점유율
    checkin_today = df[df['arrival_date'] == today_str]          # 오늘 체크인 예정
    checkin_cnt   = len(checkin_today)
    highrisk_cnt  = int((df['취소확률'] >= 70).sum())            # 고위험 예약 (전체 기준)
    expected_cancel = (checkin_today['취소확률'] / 100).sum()    # 예측 취소 인원 (오늘 체크인 기준)

    # ── KPI 표시 ────────────────────────────────────────────────────────────
    def kpi(col, label, value, sub=None):
        col.markdown(f"""
        <p style="font-size:12px; color:#9E9890; margin:0; letter-spacing:0.06em;">{label}</p>
        <p style="font-size:32px; font-weight:400; color:#1A1A1A; margin:4px 0 2px 0;">{value}</p>
        <p style="font-size:12px; color:#9E9890; margin:0;">{sub if sub else '&nbsp;'}</p>
        """, unsafe_allow_html=True)

    k1, k2, k3, k4, k5 = st.columns(5)
    kpi(k1, "활성 예약",      f"{active_cnt}건",           "Checked-Out 제외")
    kpi(k2, "현재 투숙 중",   f"{inhouse_cnt}명",           f"점유율 {occupancy:.0f}%")
    kpi(k3, "오늘 체크인",    f"{checkin_cnt}명",           "arrival_date 기준")
    kpi(k4, "고위험 예약",    f"{highrisk_cnt}건",          "취소확률 70% 이상")
    kpi(k5, "예측 취소 인원", f"{expected_cancel:.1f}명",   "오늘 체크인 기준")

    st.divider()

    # ── 객실 점유율 바 ───────────────────────────────────────────────────────
    st.markdown(f"**객실 점유율** &nbsp; {occupancy:.0f}%", unsafe_allow_html=True)
    st.progress(min(occupancy / 100, 1.0))

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 오늘 체크인 예정 고객 테이블 ────────────────────────────────────────
    st.markdown("**오늘 체크인 예정 고객**")

    if checkin_cnt == 0:
        st.info("오늘 체크인 예정인 고객이 없습니다.")
    else:
        view = checkin_today[['customer_name', 'status', 'total_stay_nights',
                               'adults', 'meal', '취소확률']].copy()
        view = view.rename(columns={
            'customer_name':    '고객명',
            'status':           '상태',
            'total_stay_nights':'투숙일',
            'adults':           '인원',
            'meal':             '식사',
        })
        view = view.sort_values('취소확률', ascending=False).reset_index(drop=True)

        def risk_color(val):
            # 취소확률에 따라 빨강/노랑/초록 배지
            if val >= 70:
                return 'background-color: #fee2e2; color: #991b1b; font-weight:600; border-radius:4px;'
            elif val >= 40:
                return 'background-color: #fef9c3; color: #854d0e; font-weight:600; border-radius:4px;'
            else:
                return 'background-color: #dcfce7; color: #166534; font-weight:600; border-radius:4px;'

        styled = (
            view.style
            .map(risk_color, subset=['취소확률'])
            .format({'투숙일': '{:.0f}박', '취소확률': '{:.0f}%'})
        )
        st.dataframe(styled, use_container_width=True, hide_index=True)