import datetime
import pandas as pd
import streamlit as st
from utils.utils import get_predictions   # util에서 가져오기

st.set_page_config(page_title="알림 / 액션", page_icon="🔔", layout="wide")

def run():
    try:
        # 캐싱된 예측 결과 포함된 df 가져오기
        df = get_predictions(return_df=True)
    except FileNotFoundError as e:
        st.error(f"파일을 찾을 수 없습니다: {e}\n\n경로를 확인해 주세요.")
        st.stop()
    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")
        st.stop()

    # ── 스타일 (기존 디자인 유지) ───────────────────────────
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
        html, body, [class*="css"] { font-family: 'DM Sans', 'Pretendard', sans-serif; }
        .app-header { display:flex; align-items:center; gap:10px; font-size:1.5rem; font-weight:700; color:#1f2937;
                      padding-bottom:16px; margin-bottom:4px; border-bottom:1px solid #ececec; }
        .sec-title { font-weight:700; font-size:1.05rem; margin:4px 0 14px 0; }
        .sec-red   { color:#dc2626; }
        .sec-amber { color:#d4881f; }
        .badge-txt-red { background:#fde4e4; color:#c0392b; font-weight:700; padding:3px 10px; border-radius:99px; }
        .badge-txt-amber { background:#fef3c7; color:#b45309; font-weight:700; padding:3px 10px; border-radius:99px; }
        .reason-tag { display:inline-block; background:#f3f4f6; color:#4b5563; font-size:0.75rem; padding:2px 8px;
                      border-radius:6px; margin-right:4px; margin-top:5px; }
        .empty { color:#9ca3af; text-align:center; padding:32px 10px; border:1px dashed #e5e7eb; border-radius:14px; }
        .done-badge { display:inline-block; background:#dcfce7; color:#166534; font-size:0.75rem; font-weight:700;
                      padding:2px 10px; border-radius:99px; margin-left:4px; }
    </style>
    """, unsafe_allow_html=True)

    # ── 액션 상태 저장 ───────────────────────────
    if 'actioned_customers' not in st.session_state:
        st.session_state['actioned_customers'] = set()

    # ── 헤더 ───────────────────────────
    st.title("🔔 알림 / 액션")

    # ── 기준일 선택 ───────────────────────────
    date_col, _ = st.columns([0.25, 0.75])
    with date_col:
        base_date = st.date_input("📅 기준일", value=datetime.date(2017, 8, 14))

    base_ts = pd.Timestamp(base_date)

    upcoming = df[
        df['arrival_dt'].dt.date == base_date
    ].copy()

    if not upcoming.empty:
        upcoming['dday'] = (upcoming['arrival_dt'] - base_ts).dt.days.fillna(0).astype(int)
    else:
        upcoming['dday'] = 0

    # ── KPI ───────────────────────────
    total_upcoming = len(upcoming)
    immediate_pool = upcoming[upcoming['cancel_proba'] >= 70]
    monitor_pool = upcoming[(upcoming['cancel_proba'] >= 50) & (upcoming['cancel_proba'] < 70)]

    m1, m2, m3 = st.columns(3)
    m1.metric("총 체크인 예정", f"{total_upcoming}건")
    m2.metric("즉시 연락 필요", f"{len(immediate_pool)}건", delta="조치 시급", delta_color="inverse")
    m3.metric("모니터링 필요", f"{len(monitor_pool)}건")

    st.write("")

    # ── 정렬 옵션 ───────────────────────────
    st.info("📌 아래 고객 목록은 취소 확률이 높은 순으로 정렬되어 있습니다.")

    immediate = immediate_pool.sort_values(
        'cancel_proba',
        ascending=False
    )

    monitor = monitor_pool.sort_values(
        'cancel_proba',
        ascending=False
    )

    # ── 카드 렌더링 함수 ───────────────────────────
    def render_interactive_column(frame, kind):
        if frame.empty:
            st.markdown('<div class="empty">해당 리스크 그룹에 고객이 없습니다 🎉</div>', unsafe_allow_html=True)
            return

        frame = frame.copy()
        frame['is_done'] = frame['customer_name'].isin(st.session_state['actioned_customers'])
        frame = frame.sort_values('is_done', kind='stable')

        for _, row in frame.iterrows():
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
                    name_color = "#9ca3af" if is_done else "#1f2937"
                    done_badge = "<span class='done-badge'>✅ 조치 완료</span>" if is_done else ""
                    opacity = "opacity:0.55;" if is_done else ""

                    st.markdown(
                        f"<h5 style='{opacity}'><b style='color:{name_color}'>{name}</b> "
                        f"&nbsp;&nbsp;<span class='{badge_style}'>{int(row['cancel_proba'])}%</span>{done_badge}</h5>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"<p style='color:#6b7280; font-size:0.85rem; margin-bottom:4px; {opacity}'>"
                        f"{mmdd} 입실 · {nights}박 · {dlabel}</p>",
                        unsafe_allow_html=True,
                    )

                    tags = []
                    if row.get('lead_time', 0) > 200:
                        tags.append(f"🏷️ 장기 예약 ({int(row['lead_time'])}일 전)")
                    if row.get('previous_cancellations', 0) > 0:
                        tags.append(f"⚠️ 과거 취소 이력 ({int(row['previous_cancellations'])}회)")
                    if row.get('total_of_special_requests', 0) == 0:
                        tags.append("💬 특별 요청 사항 없음")

                    if tags:
                        tag_html = "".join([f"<span class='reason-tag'>{t}</span>" for t in tags])
                        st.markdown(f"<div style='{opacity}'>{tag_html}</div>", unsafe_allow_html=True)

                with col_action:
                    if st.button("✉️ 안내 발송", key=f"msg_{name}", use_container_width=True):
                        st.toast(f"✉️ {name} 고객님께 예약 재확인 알림톡이 발송되었습니다.")

                    checked = st.checkbox("조치 완료", value=is_done, key=f"chk_{name}")
                    if checked and not is_done:
                        st.session_state['actioned_customers'].add(name)
                        st.rerun()
                    elif not checked and is_done:
                        st.session_state['actioned_customers'].discard(name)
                        

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