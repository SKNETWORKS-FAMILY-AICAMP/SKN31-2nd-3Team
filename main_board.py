import pandas as pd
import streamlit as st
import joblib

from utils import load_data, DEMO_TODAY

# ── 설정 ───────────────────────────────────────────────────────────────────
TOTAL_ROOMS = 200   # 전체 객실 수 (대형 리조트호텔 기준)

# ── 모델 로드 (캐싱) ────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    return joblib.load('model&preprocessing/best_model.pkl')


def run():
    model = load_model()
    df = load_data().copy()

    # ── 예측 ───────────────────────────────────────────────────────────────
    # 모델 입력에서 제외할 컬럼 이름/상태/정답/utils이 만든 파생 컬럼
    drop_cols = ['customer_name', 'status', 'is_canceled', 'checkout_date']
    feature_cols = [c for c in df.columns if c not in drop_cols]
    df['취소확률'] = (model.predict_proba(df[feature_cols])[:, 1] * 100).round(1)

    # ── 식사 코드를 설명 붙은 라벨로 변환 ───────────────────────────────────
    meal_labels = {
        'BB': 'BB (조식)',
        'HB': 'HB (조식+석식)',
        'FB': 'FB (3식)',
        'SC': 'SC (객실만)',
        'Undefined': '미정',
    }
    df['meal'] = df['meal'].map(meal_labels).fillna(df['meal'])

    # ── 기준일 (util.py의 DEMO_TODAY 사용) ──────────────────────────────────
    today_ts  = DEMO_TODAY
    today     = today_ts.date()

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

    # ── KPI 계산 (util이 만든 status 기준) ──────────────────────────────────
    # 현재 투숙 중 = status가 In-House
    inhouse_cnt  = int((df['status'] == 'In-House').sum())
    occupancy    = inhouse_cnt / TOTAL_ROOMS * 100

    # 오늘 체크아웃 예정 = 체크아웃일이 오늘
    checkout_cnt = int((df['checkout_date'] == today_ts).sum())

    # 가용 객실 = (전체 - 현재 투숙) + 오늘 체크아웃으로 빌 방
    available_rooms = TOTAL_ROOMS - inhouse_cnt
    total_available = available_rooms + checkout_cnt

    # 오늘 체크인 예정 전체 (취소 포함)
    checkin_all = df[df['arrival_date'] == today_ts]
    # 실제 올 사람 = 오늘 체크인 예정 중 취소 안 된 건
    checkin_today = checkin_all[checkin_all['is_canceled'] == 0]
    checkin_cnt   = len(checkin_today)
    # 오늘 취소 = 오늘 체크인 예정 중 실제 취소된 건
    cancel_today_cnt = int((checkin_all['is_canceled'] == 1).sum())

    # 예측 취소 = 오늘 체크인 예정 전체(취소 포함)의 취소확률 기댓값 합산 (모델 예측)
    # 실제 취소(오늘 취소)와 같은 모집단(전체 165건)
    expected_cancel = (checkin_all['취소확률'] / 100).sum()

    # ── KPI 표시 ────────────────────────────────────────────────────────────
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

    # ── 객실 점유율 바 ───────────────────────────────────────────────────────
    st.markdown(f"**객실 점유율** &nbsp; {occupancy:.0f}%", unsafe_allow_html=True)
    st.progress(min(occupancy / 100, 1.0))

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 오늘 체크인 예정 고객 테이블 ────────────────────────────────────────
    st.markdown(f"**🔸 오늘 체크인 예정 고객 (취소 제외)** &nbsp; {checkin_cnt}건")

    if checkin_cnt == 0:
        st.info("오늘 체크인 예정인 고객이 없습니다.")
    else:
        view = checkin_today[['customer_name', 'total_stay_nights', 'adults',
                              'meal', '취소확률']].copy()
        view = view.rename(columns={
            'customer_name':    '고객명',
            'total_stay_nights':'투숙일',
            'adults':           '인원',
            'meal':             '식사',
        })
        view = view.sort_values('취소확률', ascending=False).reset_index(drop=True)

        def risk_color(val):
            # 취소확률에 따라 빨강/노랑/초록
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