import pandas as pd
import streamlit as st
import joblib
from datetime import date

# ── 설정 ───────────────────────────────────────────────────────────────────
TOTAL_ROOMS = 100   # 전체 객실 수

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

    # 식사 코드를 설명 붙은 라벨로 변환 (BB -> "BB (조식)")
    meal_labels = {
        'BB': 'BB (조식)',
        'HB': 'HB (조식+석식)',
        'FB': 'FB (3식)',
        'SC': 'SC (객실만)',
        'Undefined': '미정',
    }
    df['meal'] = df['meal'].map(meal_labels).fillna(df['meal'])

    # ── 날짜 컬럼 준비 ──────────────────────────────────────────────────────
    # arrival_date(체크인일) + total_stay_nights(묵는 일수) = checkout_dt(체크아웃 예정일)
    df['arrival_dt']  = pd.to_datetime(df['arrival_date'])
    df['checkout_dt'] = df['arrival_dt'] + pd.to_timedelta(df['total_stay_nights'], unit='D')

    # ── 기준일 (컴퓨터 오늘 날짜) ───────────────────────────────────────────
    today = date.today()
    today_str = today.strftime('%Y-%m-%d')
    today_ts = pd.Timestamp(today)

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

    # ── KPI 계산 (현재 시점 기준) ──────────────────────────────────────────
    checkin_today = df[df['arrival_date'] == today_str]          # 오늘 체크인 예정
    checkin_cnt   = len(checkin_today)

    # 현재 투숙 중 = 체크인일 <= 오늘 < 체크아웃 예정일 (날짜 계산)
    staying_now  = df[(df['arrival_dt'] <= today_ts) & (today_ts < df['checkout_dt'])]
    inhouse_cnt  = len(staying_now)
    occupancy    = inhouse_cnt / TOTAL_ROOMS * 100              # 점유율

    # 가용 객실 = 전체 객실 - 현재 투숙 중
    available_rooms = TOTAL_ROOMS - inhouse_cnt

    # 오늘 체크아웃 예정 = 체크아웃 예정일이 오늘인 사람 (오늘 방이 빌 예정)
    checkout_today = df[df['checkout_dt'] == today_ts]
    checkout_cnt   = len(checkout_today)

    # 고위험 예약 = 오늘 체크인 예정(Expected) 중 취소확률 70% 이상
    today_expected = checkin_today[checkin_today['status'] == 'Expected']
    highrisk_cnt  = int((today_expected['취소확률'] >= 70).sum())

    # 예측 취소 인원 = 오늘 체크인 기준 기댓값 합산
    expected_cancel = (checkin_today['취소확률'] / 100).sum()

    # ── KPI 표시 ────────────────────────────────────────────────────────────
    def kpi(col, label, value, sub=None):
        col.markdown(f"""
        <p style="font-size:12px; color:#9E9890; margin:0; letter-spacing:0.06em;">{label}</p>
        <p style="font-size:32px; font-weight:400; color:#1A1A1A; margin:4px 0 2px 0;">{value}</p>
        <p style="font-size:12px; color:#9E9890; margin:0;">{sub if sub else '&nbsp;'}</p>
        """, unsafe_allow_html=True)

    k1, k2, k3, k4, k5 = st.columns(5)
    kpi(k1, "가용 객실",      f"{available_rooms} + {checkout_cnt}",
        f"전체 {TOTAL_ROOMS}실 중 · 오늘 총 {available_rooms + checkout_cnt}실")
    kpi(k2, "현재 투숙 중",   f"{inhouse_cnt}건",           f"점유율 {occupancy:.0f}% (날짜 기준)")
    kpi(k3, "오늘 체크인",    f"{checkin_cnt}건",           "arrival_date 기준")
    kpi(k4, "고위험 예약",    f"{highrisk_cnt}건",          "오늘 체크인 중 70% 이상")
    kpi(k5, "예측 취소",      f"{expected_cancel:.1f}건",   "오늘 체크인 기준")

    st.divider()

    # ── 객실 점유율 바 ───────────────────────────────────────────────────────
    st.markdown(
        f"**객실 점유율** &nbsp; {occupancy:.0f}% "
        f'<span style="color:#9E9890; font-size:13px;">&nbsp;|&nbsp; '
        f'오늘 체크아웃 예정 {checkout_cnt}실 (오후에 빌 예정)</span>',
        unsafe_allow_html=True
    )
    st.progress(min(occupancy / 100, 1.0))

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 오늘 체크인 예정 고객 ───────────────────────────────────────────────
    def risk_color(val):
        # 취소확률에 따라 빨강/노랑/초록 배지
        if val >= 70:
            return 'background-color: #fee2e2; color: #991b1b; font-weight:600; border-radius:4px;'
        elif val >= 40:
            return 'background-color: #fef9c3; color: #854d0e; font-weight:600; border-radius:4px;'
        else:
            return 'background-color: #dcfce7; color: #166534; font-weight:600; border-radius:4px;'

    rename_map = {
        'customer_name':    '고객명',
        'status':           '상태',
        'total_stay_nights':'투숙일',
        'adults':           '인원',
        'meal':             '식사',
    }
    show_cols = ['customer_name', 'total_stay_nights', 'adults',
                 'meal', '취소확률']

    def render_table(data):
        # 아직 안 온 고객용 테이블 (체크인일 = 모두 오늘이라 생략)
        view = data[show_cols].copy()
        view = view.rename(columns=rename_map)
        view = view.sort_values('취소확률', ascending=False).reset_index(drop=True)
        styled = (
            view.style
            .map(risk_color, subset=['취소확률'])
            .format({'투숙일': '{:.0f}박', '취소확률': '{:.0f}%'})
        )
        st.dataframe(styled, use_container_width=True, hide_index=True)

    def render_inhouse_table(data):
        # 이미 온 고객용 테이블 (체크인 완료라 취소확률은 제외, 체크아웃 임박순 정렬)
        cols = ['customer_name', 'arrival_dt', 'checkout_dt',
                'total_stay_nights', 'adults', 'meal']
        view = data[cols].copy()
        # 체크아웃 예정일 빠른 순 정렬 (곧 나갈 사람 먼저)
        view = view.sort_values('checkout_dt').reset_index(drop=True)
        # 날짜를 보기 좋게 문자열로
        view['arrival_dt']  = view['arrival_dt'].dt.strftime('%Y-%m-%d')
        view['checkout_dt'] = view['checkout_dt'].dt.strftime('%Y-%m-%d')
        view = view.rename(columns={
            'customer_name':    '고객명',
            'arrival_dt':       '체크인일',
            'checkout_dt':      '체크아웃 예정',
            'total_stay_nights':'투숙일',
            'adults':           '인원',
            'meal':             '식사',
        })
        styled = view.style.format({'투숙일': '{:.0f}박'})
        st.dataframe(styled, use_container_width=True, hide_index=True)

    # 아직 안 온 고객 = 오늘 체크인 예정 (정의상 모두 미도착)
    not_arrived = checkin_today
    # 이미 온 고객 = 현재 호텔에 투숙 중 (날짜 계산 기준, 어제 이전 체크인 포함)
    arrived     = staying_now

    # 아직 안 온 고객
    st.markdown(f"**🔸 아직 안 온 고객 (Expected)** &nbsp; {len(not_arrived)}명")
    if len(not_arrived) == 0:
        st.info("오늘 체크인 예정인 고객이 없습니다.")
    else:
        render_table(not_arrived)

    st.markdown("<br>", unsafe_allow_html=True)

    # 이미 온 고객
    st.markdown(f"**🔹 이미 온 고객 (In-House)** &nbsp; {len(arrived)}명")
    if len(arrived) == 0:
        st.info("현재 투숙 중인 고객이 없습니다.")
    else:
        render_inhouse_table(arrived)