import pandas as pd
import streamlit as st
import joblib

# ── 상수 ───────────────────────────────────────────────────────────────────
# 전체 객실 수 (KPI 계산에 사용 / 현재 이 파일에서는 직접 사용하지 않지만
# main_board.py와 일관성을 위해 선언해 둠)
TOTAL_ROOMS = 100


# ── 리소스 캐싱 ────────────────────────────────────────────────────────────
# @st.cache_resource : 앱 재실행(rerun)이 발생해도 모델 객체를 메모리에 유지.
#   ML 모델처럼 직렬화/역직렬화 비용이 큰 객체에 적합.
#   (cache_data는 데이터를 깊은 복사해서 반환하지만, cache_resource는 원본 참조 반환)
@st.cache_resource
def load_model():
    return joblib.load('model&preprocessing/best_model.pkl')


# @st.cache_data : DataFrame처럼 직렬화 가능한 데이터에 사용.
#   반환값을 내부적으로 pickle 직렬화 → 캐시 저장 → 다음 호출 시 역직렬화해서 반환.
#   원본 변형을 막기 위해 호출부에서 .copy()를 추가로 호출하는 것이 권장됨.
@st.cache_data
def load_data():
    df = pd.read_csv('Dataset/mock_dataset.csv')
    # arrival_date를 문자열 → datetime으로 변환: 날짜 필터링·정렬·포맷팅에 필요
    df['arrival_date'] = pd.to_datetime(df['arrival_date'])
    return df


def run():
    model = load_model()
    # load_data()는 캐시된 원본을 반환하므로 .copy()로 독립 복사본 생성.
    # 이후 df에 새 컬럼('취소확률', 'meal' 변환 등)을 추가해도 캐시가 오염되지 않음.
    df = load_data().copy()

    # ── 취소확률 계산 (Expected 상태 행에만 적용) ──────────────────────────
    # 취소확률은 "아직 체크인하지 않은(Expected)" 고객에게만 의미가 있음.
    # In-House(투숙 중)·Checked-Out(퇴실 완료) 고객은 이미 행동이 확정되었으므로
    # 취소 예측 자체가 불필요 → 해당 행은 None(→ 화면에서 '—')으로 유지.

    # 모델 입력에서 제외할 컬럼:
    #   - customer_name : 고유 식별자, 예측에 의미 없음
    #   - status        : 예측 대상(label과 직결되는 정보 누수 방지)
    #   - is_canceled   : 실제 취소 여부(정답 레이블), 추론 시에는 미존재
    feature_cols = [c for c in df.columns if c not in ['customer_name', 'status', 'is_canceled']]

    # Boolean Series: Expected 행만 True
    expected_mask = df['status'] == 'Expected'

    # 전체 행을 None으로 초기화 → In-House 등은 그대로 None 유지
    df['취소확률'] = None

    if expected_mask.any():
        # predict_proba 반환 형태: [[p_0, p_1], ...] (클래스 0=유지, 1=취소)
        # [:, 1] → 취소(클래스 1)일 확률만 추출
        proba = model.predict_proba(df.loc[expected_mask, feature_cols])[:, 1]
        # 0~1 확률을 0~100% 스케일로 변환, 소수점 1자리 반올림
        df.loc[expected_mask, '취소확률'] = (proba * 100).round(1)

    # ── 식사 코드 → 표시 라벨 변환 ────────────────────────────────────────
    # 데이터셋의 meal 컬럼은 약어 코드로 저장되어 있음.
    # map()으로 치환하되, 정의되지 않은 값은 fillna로 원래 값 유지.
    meal_labels = {
        'BB': 'BB',          # Bed & Breakfast (조식 포함)
        'HB': 'HB',          # Half Board (조식 + 석식)
        'FB': 'FB',          # Full Board (3식 포함)
        'SC': 'SC',          # Self Catering (식사 없음)
        'Undefined': '-',    # 미정 → '-' 표시
    }
    df['meal'] = df['meal'].map(meal_labels).fillna(df['meal'])

    # ── 헤더: 타이틀 + 액션 버튼 ──────────────────────────────────────────
    # 비율 [3, 1] → 왼쪽 타이틀이 넓고 오른쪽 버튼 영역은 좁게
    col_title, col_btn = st.columns([3, 1])
    with col_title:
        st.markdown("## 예약 리스트")
    with col_btn:
        # Streamlit 컬럼 안에 다시 컬럼을 중첩해서 버튼 2개를 나란히 배치
        st.markdown("<div style='display:flex; gap:8px; justify-content:flex-end; padding-top:8px;'>", unsafe_allow_html=True)
        bcol1, bcol2 = st.columns(2)
        with bcol1:
            # type="primary" → 파란색 강조 버튼 (Streamlit 기본 primary 스타일)
            # 현재는 클릭 이벤트 미연결 — UI 목업 용도
            st.button("＋ 예약 추가", use_container_width=True, type="primary")
        with bcol2:
            st.button("✏️ 예약 수정", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── 위험 고객 배너 ─────────────────────────────────────────────────────
    # Expected 행 중 취소확률 >= 70% 인 고객 수를 집계해서 상단 경고 배너로 표시.
    # expected_mask.any() 가드: Expected 행이 아예 없으면 연산 자체를 건너뜀.
    high_risk_cnt = int((df.loc[expected_mask, '취소확률'] >= 70).sum()) if expected_mask.any() else 0
    if high_risk_cnt > 0:
        # unsafe_allow_html=True : Streamlit은 기본적으로 HTML을 이스케이프하므로
        # 커스텀 스타일 배너를 렌더링하려면 이 옵션이 필요.
        st.markdown(
            f"""<div style="background:#fff1f2; border:1px solid #fecdd3; border-radius:8px;
                padding:10px 16px; margin-bottom:12px; color:#be123c; font-size:14px;">
                ⚠️ &nbsp; <b>취소 위험 고객 {high_risk_cnt}명</b> — Expected 중 취소확률 70% 이상
            </div>""",
            unsafe_allow_html=True
        )

    # ── 상태 필터(라디오) + 고객명 검색 인풋 ─────────────────────────────
    # 비율 [3, 1] → 필터 탭이 넓고 검색창은 오른쪽 끝에 작게
    filter_col, search_col = st.columns([3, 1])
    with filter_col:
        # horizontal=True : 라디오 버튼을 가로로 배치 (탭 스타일처럼 보이게)
        # label_visibility="collapsed" : 라벨 텍스트를 화면에서 숨김 (접근성은 유지)
        status_tab = st.radio(
            "상태 필터",
            ["전체", "In-House", "Expected", "위험만"],
            horizontal=True,
            label_visibility="collapsed"
        )
    with search_col:
        # placeholder는 입력 전 회색 힌트 텍스트
        search_query = st.text_input(
            "고객명 검색",
            placeholder="🔍 고객명 검색",
            label_visibility="collapsed"
        )

    # ── 상태 필터 적용 ─────────────────────────────────────────────────────
    # 각 탭에 맞게 df를 슬라이싱. .copy()로 SettingWithCopyWarning 방지.
    if status_tab == "전체":
        filtered = df.copy()                                          # 모든 상태 포함
    elif status_tab == "In-House":
        filtered = df[df['status'] == 'In-House'].copy()              # 현재 투숙 중
    elif status_tab == "Expected":
        filtered = df[df['status'] == 'Expected'].copy()              # 체크인 예정
    elif status_tab == "위험만":
        # Expected 이면서 취소확률 70% 이상인 고위험 고객만
        filtered = df[(df['status'] == 'Expected') & (df['취소확률'] >= 70)].copy()

    # ── 고객명 검색 필터 (선택적 추가 필터) ──────────────────────────────
    if search_query:
        # str.contains : 대소문자 무시(case=False), NaN 무시(na=False)로 부분 일치 검색
        filtered = filtered[filtered['customer_name'].str.contains(search_query, case=False, na=False)]

    # ── 정렬 ──────────────────────────────────────────────────────────────
    # Expected / 위험만 탭: 취소 위험이 높은 고객을 먼저 확인할 수 있도록 내림차순
    # 나머지(전체, In-House): 체크인 날짜 오름차순 (시간 순서대로 파악)
    if status_tab in ["Expected", "위험만"]:
        filtered = filtered.sort_values('취소확률', ascending=False)
    else:
        filtered = filtered.sort_values('arrival_date')

    # ── 표시할 컬럼 선택 및 한글 컬럼명 매핑 ─────────────────────────────
    display_cols = [
        'customer_name',    # 고객명
        'status',           # 상태 (In-House / Expected)
        'arrival_date',     # 체크인 예정일
        'total_stay_nights',# 총 투숙 박수
        'adults',           # 성인 인원
        'meal',             # 식사 옵션
        'market_segment',   # 예약 채널 (Online TA, Direct 등)
        '취소확률',          # 모델 예측 취소 확률 (Expected만 값 존재)
    ]

    rename_map = {
        'customer_name':    '고객명',
        'status':           '상태',
        'arrival_date':     '체크인',
        'total_stay_nights':'박수',
        'adults':           '인원',
        'meal':             '식사',
        'market_segment':   '마켓',
        '취소확률':          '취소확률',
    }

    view = filtered[display_cols].copy()
    view = view.rename(columns=rename_map)

    # 날짜를 'MM/DD' 형식 문자열로 변환 (테이블에서 간결하게 표시)
    view['체크인'] = view['체크인'].dt.strftime('%m/%d')

    # 상태 코드에 이모지 아이콘을 붙여 시각적으로 구분
    # fillna: 매핑에 없는 상태값(예: Checked-Out)은 원래 텍스트 유지
    status_icon = {
        'In-House':    '🟢 In-House',
        'Expected':    '🔵 Expected',
        'Checked-Out': '⚫ Checked-Out',
    }
    view['상태'] = view['상태'].map(status_icon).fillna(view['상태'])

    # ── 스타일 함수 정의 ──────────────────────────────────────────────────

    def style_row(row):
        """
        행(row) 단위 배경색 지정.
        취소확률 >= 70% 인 행 전체를 연한 빨강 배경으로 강조.
        In-House 등 취소확률이 None인 행은 스타일 없음.
        반환: 각 셀에 적용할 CSS 문자열 리스트 (길이 = 컬럼 수)
        """
        if pd.isna(row['취소확률']):
            return [''] * len(row)          # 취소확률 없음 → 스타일 없음
        elif row['취소확률'] >= 70:
            return ['background-color:#fff7f7'] * len(row)  # 고위험: 연한 빨강 배경
        return [''] * len(row)              # 저위험 → 스타일 없음

    def style_cancel(val):
        """
        취소확률 셀 단위 배지 스타일.
        값이 없으면(In-House 등) 회색 텍스트로 표시.
        위험도에 따라 3단계 색상 배지:
          - 70% 이상 : 빨강 (고위험)
          - 40~69%   : 노랑 (중위험)
          - 40% 미만 : 초록 (저위험)
        """
        if pd.isna(val):
            return 'color: #ccc;'                                                           # 값 없음: 회색
        if val >= 70:
            return 'background-color:#fecaca; color:#991b1b; font-weight:700; border-radius:4px;'   # 고위험
        elif val >= 40:
            return 'background-color:#fef9c3; color:#854d0e; font-weight:600; border-radius:4px;'   # 중위험
        else:
            return 'background-color:#dcfce7; color:#166534; font-weight:600; border-radius:4px;'   # 저위험

    # ── 스타일 체인 조립 ──────────────────────────────────────────────────
    styled = (
        view.reset_index(drop=True)     # 필터링 후 인덱스를 0부터 재설정
        .style
        .apply(style_row, axis=1)       # 행 단위 배경색 (axis=1 → 각 row를 Series로 전달)
        .map(style_cancel, subset=['취소확률'])  # 취소확률 셀만 배지 스타일 적용
        .format({
            '박수':    '{:.0f}박',       # 예: 3.0 → "3박"
            # 취소확률: 값 있으면 정수% 표시, None이면 '—' 표시
            '취소확률': lambda v: f'{v:.0f}%' if pd.notna(v) else '—',
        })
        # 취소확률 셀 내부에 수평 바 차트 추가 (0~100 기준)
        # subset에서 취소확률이 None인 행(In-House 등)을 제외하기 위해 pd.IndexSlice 사용:
        #   view['취소확률'].notna().values → Boolean 배열로 유효 행만 선택
        # color: [낮은값 색, 높은값 색] 순서로 그라데이션
        .bar(
            subset=pd.IndexSlice[view['취소확률'].notna().values, ['취소확률']],
            color=['#86efac', '#fca5a5'],   # 초록(낮음) → 빨강(높음)
            vmin=0, vmax=100
        )
    )

    # ── 테이블 렌더링 ─────────────────────────────────────────────────────
    st.markdown(f"**{len(filtered)}건** 표시 중")
    # height=500: 스크롤 가능한 고정 높이
    # hide_index=True: 0, 1, 2... 숫자 인덱스 컬럼 숨김
    st.dataframe(styled, use_container_width=True, height=500, hide_index=True)
