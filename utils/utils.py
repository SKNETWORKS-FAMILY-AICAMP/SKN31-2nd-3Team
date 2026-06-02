import pandas as pd
import streamlit as st
import joblib

DEMO_TODAY = pd.Timestamp('2017-08-14')

@st.cache_resource
def load_model():
    return joblib.load('model&preprocessing/best_model.pkl')

@st.cache_data
def get_predictions(return_df=True):
    """
    return_df=True → cancel_proba 컬럼이 붙은 df 반환
    return_df=False → cancel_proba 배열(proba)만 반환
    """
    # 데이터 로드 및 기본 전처리
    df = pd.read_csv('Dataset/demo_data.csv')
    df = df[df['hotel'] == 'Resort Hotel']  # 리조트 호텔만 시연
    df['arrival_date'] = pd.to_datetime(df['arrival_date'])
    df['arrival_date_month_num'] = df['arrival_date'].dt.month
    df['checkout_date'] = df['arrival_date'] + pd.to_timedelta(df['total_stay_nights'], unit='D')

    # 상태(status) 정의
    df['status'] = 'Expected'
    df.loc[
        (df['arrival_date'] < DEMO_TODAY) &
        (df['checkout_date'] > DEMO_TODAY) &
        (df['is_canceled'] == 0), 'status'
    ] = 'In-House'
    df.loc[
        (df['checkout_date'] <= DEMO_TODAY) &
        (df['is_canceled'] == 0), 'status'
    ] = 'Checked-Out'
    df.loc[
        (df['arrival_date'] < DEMO_TODAY) &
        (df['is_canceled'] == 1), 'status'
    ] = 'Canceled'

    # 모델 예측 추가
    model = load_model()
    feature_cols = [c for c in df.columns if c not in ['customer_name','status','is_canceled','arrival_date']]
    proba = model.predict_proba(df[feature_cols])[:, 1]
    df['cancel_proba'] = (proba * 100).round(0).astype(int)
    df['arrival_dt'] = pd.to_datetime(df['arrival_date'], errors='coerce')

    if return_df:
        return df
    else:
        return proba
