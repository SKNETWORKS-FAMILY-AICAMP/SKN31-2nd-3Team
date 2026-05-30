import pandas as pd
import streamlit as st
import joblib
 
@st.cache_resource
def load_model():
    return joblib.load('model&preprocessing/best_model.pkl')
 
@st.cache_data
def load_data():
    df = pd.read_csv('Dataset/mock_dataset.csv')
    df['arrival_date'] = pd.to_datetime(df['arrival_date'])
    return df
 
def run():
    model = load_model()
    df = load_data()
 
    # 예측
    feature_cols = [c for c in df.columns if c not in ['customer_name', 'status', 'is_canceled']]
    proba = model.predict_proba(df[feature_cols])[:, 1]
    df['취소확률'] = (proba * 100).round(1)
    df['위험등급'] = df['취소확률'].apply(lambda x: '⚠️ 경고' if x >= 70 else '✅ 정상')
 
    st.title("🚨 예약 취소 위험 예측")
    st.caption("취소 확률 70% 이상 고객은 경고로 표시됩니다")
    st.divider()
 
    # 필터
    df['_ym'] = df['arrival_date'].dt.to_period('M')
    
    month_labels = [str(m) for m in sorted(df['_ym'].unique())]
 
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        show_only_warn = st.toggle("⚠️ 위험 고객만 보기", value=False)
    with col_f2:
        default_status = [s for s in df['status'].unique() if s != 'Checked-Out']
        status_filter  = st.multiselect("상태", df['status'].unique(), default=default_status)
    with col_f3:
        selected_months = st.multiselect("체크인 월", options=month_labels, default=month_labels)
 
    filtered = df[
        df['status'].isin(status_filter) &
        df['_ym'].astype(str).isin(selected_months)
    ]
    if show_only_warn:
        filtered = filtered[filtered['취소확률'] >= 70]
    filtered = filtered.sort_values('취소확률', ascending=False)
 
    st.markdown(f"**{len(filtered)}건** 표시 중")
 
    # 테이블
    display_cols = ['customer_name', 'status', 'hotel', 'arrival_date',
                    'total_stay_nights', 'adults', 'market_segment',
                    'adr', '취소확률', '위험등급']
 
    def highlight_warn(row):
        if row['취소확률'] >= 70:
            return ['background-color: #fff7f7'] * len(row)
        return [''] * len(row)
 
    styled = (
        filtered[display_cols]
        .reset_index(drop=True)
        .style
        .apply(highlight_warn, axis=1)
        .format({'취소확률': '{:.1f}%', 'adr': '{:.0f}'})
        .bar(subset=['취소확률'], color=['#86efac', '#fca5a5'], vmin=0, vmax=100)
    )
    st.dataframe(styled, use_container_width=True, height=500)