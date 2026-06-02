import pandas as pd
import streamlit as st
import joblib

from utils.utils import DEMO_TODAY, get_predictions

TOTAL_ROOMS = 200   # 전체 객실 수 (대형 리조트호텔 기준)

def run():
    # 캐싱된 예측 결과 포함된 df 가져오기
    df = get_predictions(return_df=True)

    # ── 식사 코드 라벨 변환 ───────────────────────────────────
    meal_labels = {
        'BB': 'BB (조식)',
        'HB': 'HB (조식+석식)',
        'FB': 'FB (3식)',
        'SC': 'SC (객실만)',
        'Undefined': '미정',
    }
    df['meal'] = df['meal'].map(meal_labels).fillna(df['meal'])

    # ── 기준일 ──────────────────────────────────
    today_ts  = DEMO_TODAY
    today     = today_ts.date()

    # ── 헤더 ───────────────────────────────────
    col_title, col_info = st.columns([2, 1])
    with col_title:
        st.title("🏨 현황판")
    with col_info:
        st.markdown(
            f'<p style="text-align:right; color:#9E9890; font-size:13px; padding-top:12px;">'
            f'기준일: {today.strftime("%Y년 %m월 %d일")} &nbsp;|&nbsp; 전체 객실: {TOTAL_ROOMS}실</p>',
            unsafe_allow_html=True
        )

    st.divider()

    # ── KPI 계산 ──────────────────────────────────
    inhouse_cnt  = int((df['status'] == 'In-House').sum())
    occupancy    = inhouse_cnt / TOTAL_ROOMS * 100

    checkout_cnt = int((df['checkout_date'] == today_ts).sum())

    available_rooms = TOTAL_ROOMS - inhouse_cnt
    total_available = available_rooms + checkout_cnt

    # 오늘 체크인 예정 전체 (취소 포함)
    checkin_today = df[df['arrival_dt'].dt.date == today]
    checkin_cnt   = len(checkin_today)

    # 예측 취소 = 오늘 체크인 예정 전체의 취소확률 합산
    expected_cancel = (checkin_today['cancel_proba'] / 100).sum()

    # ── KPI 표시 ──────────────────────────────────
    def kpi(col, label, value, sub=None):
        col.markdown(f"""
        <p style="font-size:12px; color:#9E9890; margin:0; letter-spacing:0.06em;">{label}</p>
        <p style="font-size:32px; font-weight:400; color:#1A1A1A; margin:4px 0 2px 0;">{value}</p>
        <p style="font-size:12px; color:#9E9890; margin:0;">{sub if sub else '&nbsp;'}</p>
        """, unsafe_allow_html=True)

    k1, k2, k3, k4, k5 = st.columns(5)
    kpi(k1, "현재 투숙 중",  f"{inhouse_cnt}건",          f"점유율 {occupancy:.0f}%")
    kpi(k2, "오늘 체크아웃", f"{checkout_cnt}건",         "오후에 빌 예정")
    kpi(k3, "가용 객실",     f"{total_available}실",      f"빈방 {available_rooms} + 체크아웃 {checkout_cnt}")
    kpi(k4, "오늘 체크인",   f"{checkin_cnt}건",          "취소 제외, 실제 도착 예정")
    kpi(k5, "예측 취소",     f"{expected_cancel:.1f}건",  "모델 예측 (오늘 도착 기준)")

    st.divider()

    # ── 객실 점유율 바 ──────────────────────────────────
    st.markdown(f"**객실 점유율** &nbsp; {occupancy:.0f}%", unsafe_allow_html=True)
    st.progress(min(occupancy / 100, 1.0))

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 오늘 체크인 예정 고객 테이블 ──────────────────────────────────
    st.markdown(f"**🔸 오늘 체크인 예정 고객 (취소 제외)** &nbsp; {checkin_cnt}건")

    if checkin_cnt == 0:
        st.info("오늘 체크인 예정인 고객이 없습니다.")
    else:
        view = checkin_today[['customer_name', 'total_stay_nights', 'adults',
                              'meal', 'cancel_proba']].copy()
        view = view.rename(columns={
            'customer_name':    '고객명',
            'total_stay_nights':'투숙일',
            'adults':           '인원',
            'meal':             '식사',
            'cancel_proba':     '취소확률'
        })
        view = view.sort_values('취소확률', ascending=False).reset_index(drop=True)

        def risk_color(val):
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
