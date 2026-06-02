import streamlit as st
import pandas as pd
from utils.utils import get_predictions   # util에서 가져오기

def run():
    # 캐싱된 예측 결과 포함된 df 가져오기
    df = get_predictions(return_df=True)

    # 화면 표시용으로 한글 컬럼명으로 바꿔주기
    df['취소확률'] = df['cancel_proba']

    # ── 식사 코드 → 표시 라벨 변환 ────────────────────────────────────────
    meal_labels = {
        'BB': 'BB',          # Bed & Breakfast (조식 포함)
        'HB': 'HB',          # Half Board (조식 + 석식)
        'FB': 'FB',          # Full Board (3식 포함)
        'SC': 'SC',          # Self Catering (식사 없음)
        'Undefined': '-',    # 미정 → '-' 표시
    }
    df['meal'] = df['meal'].map(meal_labels).fillna(df['meal'])

    # ── 헤더: 타이틀 + 액션 버튼 ──────────────────────────────────────────
    col_title, col_btn = st.columns([3, 1])
    with col_title:
        st.title("📋 예약 리스트")
    with col_btn:
        st.markdown("<div style='display:flex; gap:8px; justify-content:flex-end; padding-top:8px;'>", unsafe_allow_html=True)
        bcol1, bcol2 = st.columns(2)
        with bcol1:
            st.button("＋ 예약 추가", use_container_width=True, type="primary")
        with bcol2:
            st.button("✏️ 예약 수정", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── 위험 고객 배너 ─────────────────────────────────────────────────────
    high_risk_cnt = int((df.loc[df['status'] == 'Expected', '취소확률'] >= 70).sum())
    if high_risk_cnt > 0:
        st.markdown(
            f"""<div style="background:#fff1f2; border:1px solid #fecdd3; border-radius:8px;
                padding:10px 16px; margin-bottom:12px; color:#be123c; font-size:14px;">
                ⚠️ &nbsp; <b>취소 위험 고객 {high_risk_cnt}명</b> — Expected 중 취소확률 70% 이상
            </div>""",
            unsafe_allow_html=True
        )

    # ── 상태 필터 + 고객명 검색 ─────────────────────────────────────────────
    filter_col, search_col = st.columns([3, 1])
    with filter_col:
        status_tab = st.radio(
            "상태 필터",
            ["전체", "In-House", "Expected", "위험만"],
            horizontal=True,
            label_visibility="collapsed"
        )
    with search_col:
        search_query = st.text_input(
            "고객명 검색",
            placeholder="🔍 고객명 검색",
            label_visibility="collapsed"
        )

    # ── 상태 필터 적용 ─────────────────────────────────────────────────────
    if status_tab == "전체":
        filtered = df.copy()
    elif status_tab == "In-House":
        filtered = df[df['status'] == 'In-House'].copy()
    elif status_tab == "Expected":
        filtered = df[df['status'] == 'Expected'].copy()
    elif status_tab == "위험만":
        filtered = df[(df['status'] == 'Expected') & (df['취소확률'] >= 70)].copy()

    # ── 고객명 검색 필터 ──────────────────────────────────────────────
    if search_query:
        filtered = filtered[filtered['customer_name'].str.contains(search_query, case=False, na=False)]

    # ── 정렬 ──────────────────────────────────────────────────────────────
    if status_tab in ["Expected", "위험만"]:
        filtered = filtered.sort_values('취소확률', ascending=False)
    else:
        filtered = filtered.sort_values('arrival_date')

    # ── 표시할 컬럼 선택 및 한글 컬럼명 매핑 ─────────────────────────────
    display_cols = [
        'customer_name', 'status', 'arrival_date', 'total_stay_nights',
        'adults', 'meal', 'market_segment', '취소확률'
    ]
    rename_map = {
        'customer_name': '고객명',
        'status': '상태',
        'arrival_date': '체크인',
        'total_stay_nights': '박수',
        'adults': '인원',
        'meal': '식사',
        'market_segment': '마켓',
        '취소확률': '취소확률',
    }

    view = filtered[display_cols].copy().rename(columns=rename_map)
    view['체크인'] = view['체크인'].dt.strftime('%m/%d')

    status_icon = {
        'In-House': '🟢 In-House',
        'Expected': '🔵 Expected',
        'Checked-Out': '⚫ Checked-Out',
    }
    view['상태'] = view['상태'].map(status_icon).fillna(view['상태'])

    # ── 스타일 적용 ──────────────────────────────────────────────────
    def style_row(row):
        if pd.isna(row['취소확률']):
            return [''] * len(row)
        elif row['취소확률'] >= 70:
            return ['background-color:#fff7f7'] * len(row)
        return [''] * len(row)

    def style_cancel(val):
        if pd.isna(val):
            return 'color: #ccc;'
        if val >= 70:
            return 'background-color:#fecaca; color:#991b1b; font-weight:700; border-radius:4px;'
        elif val >= 40:
            return 'background-color:#fef9c3; color:#854d0e; font-weight:600; border-radius:4px;'
        else:
            return 'background-color:#dcfce7; color:#166534; font-weight:600; border-radius:4px;'

    styled = (
        view.reset_index(drop=True)
        .style
        .apply(style_row, axis=1)
        .map(style_cancel, subset=['취소확률'])
        .format({
            '박수': '{:.0f}박',
            '취소확률': lambda v: f'{v:.0f}%' if pd.notna(v) else '—',
        })
        .bar(
            subset=pd.IndexSlice[view['취소확률'].notna().values, ['취소확률']],
            color=['#86efac', '#fca5a5'],
            vmin=0, vmax=100
        )
    )

    st.markdown(f"**{len(filtered)}건** 표시 중")
    st.dataframe(styled, use_container_width=True, height=500, hide_index=True)
