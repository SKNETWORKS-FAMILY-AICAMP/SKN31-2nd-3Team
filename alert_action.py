import datetime
import joblib
import pandas as pd
import streamlit as st

st.set_page_config(page_title="알림 / 액션", page_icon="🔔", layout="wide")

# ── 모델 / 데이터 로드 ────────────────────────────────

@st.cache_resource
def load_model():
    return joblib.load('model&preprocessing/best_model.pkl')

@st.cache_data
def load_data():
    return pd.read_csv('Dataset/mock_dataset.csv')


# 메인 화면 실행 함수
def run():
    # 1. 안전하게 데이터를 받아오기 위해 빈 변수 준비
    model = None
    df = None

    # 2. 에러 방지 안전장치 작동
    try:
        model = load_model()
        df = load_data().copy() # 복사본 사용
        
    except FileNotFoundError as e:
        st.error(f"파일을 찾을 수 없습니다: {e}\n\n경로를 확인해 주세요.")
        st.stop()
        
    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")
        st.stop()

# ── 스타일 (기존 디자인 유지 + 새 컴포넌트 커스텀 태그 추가) ───────────────────────────
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
        html, body, [class*="css"] { font-family: 'DM Sans', 'Pretendard', sans-serif; }

        /* 상단 헤더 바 */
        .app-header {
            display: flex; align-items: center; gap: 10px;
            font-size: 1.5rem; font-weight: 700; color: #1f2937;
            padding-bottom: 16px; margin-bottom: 4px;
            border-bottom: 1px solid #ececec;
        }

        /* 섹션 제목 */
        .sec-title { font-weight: 700; font-size: 1.05rem; margin: 4px 0 14px 0; }
        .sec-red   { color: #dc2626; }
        .sec-amber { color: #d4881f; }

        /* 확률 배지 및 원인 태그 */
        .badge-txt-red { background: #fde4e4; color: #c0392b; font-weight: 700; padding: 3px 10px; border-radius: 99px; }
        .badge-txt-amber { background: #fef3c7; color: #b45309; font-weight: 700; padding: 3px 10px; border-radius: 99px; }
        
        .reason-tag {
            display: inline-block; background: #f3f4f6; color: #4b5563; 
            font-size: 0.75rem; padding: 2px 8px; border-radius: 6px; margin-right: 4px; margin-top: 5px;
        }

        /* 빈 상태 */
        .empty {
            color: #9ca3af; text-align: center; padding: 32px 10px;
            border: 1px dashed #e5e7eb; border-radius: 14px;
        }

        /* 조치 완료 배지 */
        .done-badge {
            display: inline-block; background: #dcfce7; color: #166534;
            font-size: 0.75rem; font-weight: 700; padding: 2px 10px;
            border-radius: 99px; margin-left: 4px;
        }
    </style>
    """, unsafe_allow_html=True)




    # ── 취소확률 예측 (df가 정상 로드된 경우에만 실행 보장) ─────────────────────────
    if df is not None and model is not None:
        feature_cols = [c for c in df.columns if c not in ['customer_name', 'status', 'is_canceled']]
        proba = model.predict_proba(df[feature_cols])[:, 1]
        df['cancel_proba'] = (proba * 100).round(0).astype(int)
        df['arrival_dt'] = pd.to_datetime(df['arrival_date'], errors='coerce')
    else:
        st.error("모델 또는 데이터가 올바르게 로드되지 않아 예측을 수행할 수 없습니다.")
        st.stop()

    # ── 액션 상태 저장을 위한 세션 상태 초기화 ──────────────────────────────────────────
    if 'actioned_customers' not in st.session_state:
        st.session_state['actioned_customers'] = set()

    # ── 사이드바 ─────────────────────────────────────────────────────────
    # with st.sidebar:
    #     st.markdown("### 🏨 Resort OBM")
    #     nav = st.radio(
    #         "메뉴",
    #         ["📊 현황판", "📋 예약 리스트", "📈 오버부킹 추천", "🔔 알림 / 액션"],
    #         index=3,
    #         label_visibility="collapsed",
    #     )

    # 알림/액션 외 메뉴 안내 처리
    # if not nav.endswith("알림 / 액션"):
    #     st.markdown(f'<div class="app-header">🏨 &nbsp;Resort Overbooking Manager</div>', unsafe_allow_html=True)
    #     st.info(f"**{nav}** 화면은 다른 담당자가 구축 중입니다. 좌측에서 **🔔 알림 / 액션** 을 선택해 주세요.")
    #     st.stop()

    # ── 메인 화면 상단 레이아웃 ───────────────────────────────────────────────────
    st.markdown('<div class="app-header">🏨 &nbsp;Resort Overbooking Manager</div>', unsafe_allow_html=True)

    # ── 기준일 선택 (사이드바 권한이 없어 화면 본문에 배치) ──────────────────────────
    date_col, _ = st.columns([0.25, 0.75])
    with date_col:
        base_date = st.date_input("📅 기준일", value=datetime.date(2026, 5, 29))

    # ── 다가오는 체크인 + 위험도 분류 ─────────────────────────────────────────────
    base_ts = pd.Timestamp(base_date)
    upcoming = df[df['arrival_dt'] >= base_ts].copy()

    # 데이터 처리 안정성을 위해 결측치(NaN)가 있으면 0일로 기본 처리
    if not upcoming.empty:
        upcoming['dday'] = (upcoming['arrival_dt'] - base_ts).dt.days.fillna(0).astype(int)
    else:
        upcoming['dday'] = 0

    # 이미 조치 완료한 고객도 목록에 남기되, 렌더 단계에서 맨 아래로 정렬한다

    # 상단 미니 대시보드 (KPI Metrics) 생성
    total_upcoming = len(upcoming)
    immediate_pool = upcoming[upcoming['cancel_proba'] >= 70]
    monitor_pool = upcoming[(upcoming['cancel_proba'] >= 50) & (upcoming['cancel_proba'] < 70)]

    m1, m2, m3 = st.columns(3)
    m1.metric("총 체크인 예정", f"{total_upcoming}건")
    m2.metric("즉시 연락 필요", f"{len(immediate_pool)}건", delta="조치 시급", delta_color="inverse")
    m3.metric("모니터링 필요", f"{len(monitor_pool)}건")

    st.write("")

    # 정렬 필터 컨트롤러 박스 추가
    sort_col1, sort_col2 = st.columns([0.25, 0.75])
    with sort_col1:
        sort_option = st.selectbox(
            "📋 리스트 정렬 기준",
            ["취소 확률 높은 순", "체크인 임박 순"],
            index=0
        )

    # 선택된 기준에 맞게 데이터 정렬 구조 재정의
    if sort_option == "취소 확률 높은 순":
        immediate = immediate_pool.sort_values('cancel_proba', ascending=False)
        monitor = monitor_pool.sort_values('cancel_proba', ascending=False)
    else:
        immediate = immediate_pool.sort_values(['dday', 'cancel_proba'], ascending=[True, False])
        monitor = monitor_pool.sort_values(['dday', 'cancel_proba'], ascending=[True, False])


    # 인터랙티브 카드 컴포넌트 함수 정의
    def render_interactive_column(frame, kind):
        if frame.empty:
            st.markdown('<div class="empty">해당 리스크 그룹에 고객이 없습니다 🎉</div>', unsafe_allow_html=True)
            return

        # 조치 완료된 고객은 맨 아래로 내린다 (stable 정렬 → 기존 정렬 순서는 유지)
        frame = frame.copy()
        frame['is_done'] = frame['customer_name'].isin(st.session_state['actioned_customers'])
        frame = frame.sort_values('is_done', kind='stable')

        for idx, row in frame.iterrows():
            name = row['customer_name']
            is_done = name in st.session_state['actioned_customers']

            with st.container(border=True):
                col_info, col_action = st.columns([0.7, 0.3])

                with col_info:
                    mmdd = row['arrival_dt'].strftime('%m/%d') if not pd.isnull(row['arrival_dt']) else "미정"
                    nights = int(row.get('total_stay_nights', 0))
                    dday = int(row.get('dday', 0))

                    if dday == 0:
                        dlabel = "🚨 오늘 체크인"
                    elif dday == 1:
                        dlabel = "⏳ 내일 체크인"
                    else:
                        dlabel = f"D-{dday}"

                    badge_style = "badge-txt-red" if kind == "immediate" else "badge-txt-amber"

                    # 완료된 카드는 회색으로 흐리게 + 완료 배지 표시
                    name_color = "#9ca3af" if is_done else "#1f2937"
                    done_badge = "<span class='done-badge'>✅ 조치 완료</span>" if is_done else ""
                    opacity = "opacity:0.55;" if is_done else ""

                    st.markdown(
                        f"<h5 style='{opacity}'><b style='color:{name_color}'>{name}</b> "
                        f"&nbsp;&nbsp;<span class='{badge_style}'>{int(row['cancel_proba'])}%</span>"
                        f"{done_badge}</h5>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"<p style='color:#6b7280; font-size:0.85rem; margin-bottom:4px; {opacity}'>"
                        f"{mmdd} 입실 · {nights}박 · {dlabel}</p>",
                        unsafe_allow_html=True,
                    )

                    # 피처 기반 원인 분석 태그 시스템
                    tags = []
                    if row.get('lead_time', 0) > 200:
                        tags.append(f"🏷️ 장기 예약 ({int(row['lead_time'])}일 전)")
                    if row.get('previous_cancellations', 0) > 0:
                        tags.append(f"⚠️ 과거 취소 이력 ({int(row['previous_cancellations'])}회)")
                    # if row.get('deposit_type') == 'Non Refund':
                    #     tags.append("💳 환불불가 상품")
                    # elif row.get('deposit_type') == 'No Deposit':
                    #     tags.append("🛑 보증금 없음 (위험 고조)")
                    if row.get('total_of_special_requests', 0) == 0:
                        tags.append("💬 특별 요청 사항 없음")

                    if tags:
                        tag_html = "".join([f"<span class='reason-tag'>{t}</span>" for t in tags])
                        st.markdown(f"<div style='{opacity}'>{tag_html}</div>", unsafe_allow_html=True)

                with col_action:
                    st.write("")
                    if st.button("✉️ 안내 발송", key=f"msg_{name}", use_container_width=True):
                        st.toast(f"✉️ {name} 고객님께 예약 재확인 알림톡이 발송되었습니다.")

                    # 체크하면 완료 처리 → 맨 아래로 이동, 해제하면 원위치로 복구
                    checked = st.checkbox("조치 완료", value=is_done, key=f"chk_{name}")
                    if checked and not is_done:
                        st.session_state['actioned_customers'].add(name)
                        st.rerun()
                    elif not checked and is_done:
                        st.session_state['actioned_customers'].discard(name)
                        st.rerun()


    # ── 화면 2분할 시각화 부 ───────────────────────────────────────────────────────────
    col_left, col_right = st.columns(2, gap="large")

    with col_left:
        st.markdown(
            f'<div class="sec-title sec-red">🔴 즉시 연락 필요 (70% 이상) · {len(immediate)}명</div>',
            unsafe_allow_html=True,
        )
        render_interactive_column(immediate, "immediate")

    with col_right:
        st.markdown(
            f'<div class="sec-title sec-amber">🟡 모니터링 필요 (50~70%) · {len(monitor)}명</div>',
            unsafe_allow_html=True,
        )
        render_interactive_column(monitor, "monitor")