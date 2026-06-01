import pandas as pd
import streamlit as st
DEMO_TODAY = pd.Timestamp('2017-08-14')

@st.cache_data
def load_data():
    df = pd.read_csv('Dataset/demo_data.csv')
    df['arrival_date'] = pd.to_datetime(df['arrival_date'])
    df['arrival_date_month_num'] = df['arrival_date'].dt.month
    df['checkout_date'] = df['arrival_date'] + pd.to_timedelta(df['total_stay_nights'], unit='D')

    # 기본값 Expected
    df['status'] = 'Expected'

    # In-House: 13일 이전 체크인 + 체크아웃 14일 이후 + 취소 안 함
    df.loc[
        (df['arrival_date'] < DEMO_TODAY) &
        (df['checkout_date'] > DEMO_TODAY) &
        (df['is_canceled'] == 0), 'status'] = 'In-House'

    # Checked-Out: 체크아웃 14일 이전 + 취소 안 함
    df.loc[
        (df['checkout_date'] <= DEMO_TODAY) &
        (df['is_canceled'] == 0), 'status'] = 'Checked-Out'

    # Canceled: 14일 이전 체크인인데 취소된 것만
    df.loc[
        (df['arrival_date'] < DEMO_TODAY) &
        (df['is_canceled'] == 1), 'status'] = 'Canceled'

    return df