import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
from datetime import date
from utils import load_data

TOTAL_ROOMS = 100

@st.cache_resource
def load_model():
    return joblib.load('model&preprocessing/best_model.pkl')

def run():
    df = load_data()
    df["arrival_date"] = pd.to_datetime(df["arrival_date"])

    model = joblib.load(
        "model&preprocessing/best_model.pkl"
    )

    selected_date = st.date_input(
        "날짜 선택"
    )

    selected_df = df[
        (df["arrival_date"].dt.date == selected_date)
        &
        (df["status"] == "Expected")
    ].copy()

    if len(selected_df) == 0:
        st.warning(
            "해당 날짜 예약 데이터가 없습니다."
        )
        return
# 모델 fit하기 위한 컬럼 drop
    X = selected_df.drop(
        columns=[
            "customer_name",
            "status"
        ],
        errors="ignore"
    )
    cancel_prob = model.predict_proba(X)[:, 1]

    # 기대 취소 인원
    expected_cancel = cancel_prob.sum()

    total_reservations = len(selected_df)

    # 기대 실제 투숙 인원
    predicted_stay = (
        total_reservations
        - expected_cancel
    )

    # KPI 계산
    current_occupied = len(
        df[df["status"] == "In-House"]
    )

    current_occupancy_rate = (
        current_occupied
        / TOTAL_ROOMS
    ) * 100

    predicted_occupancy_rate = (
        predicted_stay
        / TOTAL_ROOMS
    ) * 100

    recommended_overbooking = int(
        round(expected_cancel)
    )

    st.title(
        "🏨 호텔 오버부킹 추천 시스템"
    )

    col1, col2 = st.columns(
        [1.3, 1]
    )

#왼쪽
    with col1:

        st.subheader(
            f"{selected_date} 체크인 예정 현황"
        )

        kpi1, kpi2, kpi3 = st.columns(3)

        kpi1.metric(
            "선택일 예약 건수",
            total_reservations
        )

        kpi2.metric(
            "선택일 예상 취소",
            f"{expected_cancel:.1f}"
        )

        kpi3.metric(
            "선택일 예상 체크인",
            f"{predicted_stay:.1f}"
        )

        kpi4, kpi5, kpi6 = st.columns(3)

        kpi4.metric(
            "현재 객실 점유율",
            f"{current_occupancy_rate:.1f}%"
        )

        kpi5.metric(
            "선택일 예상 체크인 객실 비율",
            f"{predicted_occupancy_rate:.1f}%"
        )

        kpi6.metric(
            "추천 오버부킹 수",
            recommended_overbooking
        )

    # 오른쪽
    with col2:

        st.subheader(
            "추천 결과"
        )

        st.success(
            f"""
            추가 예약 권장: **{recommended_overbooking}건**

            취소 가능성이 높은 고객을 기반으로
            추가 예약 가능 수를 계산했습니다.
            """
        )

        st.markdown(
            f"**신규 체크인 기준 예상 점유율 ({selected_date})**"
        )

        st.progress(float(
            min(
                predicted_occupancy_rate / 100,
                1.0
            )
        )
        )

        st.write(
            f"{predicted_occupancy_rate:.1f}%"
        )
    # 향후 7일 추천 예약

    st.divider()
    st.caption(
        f"기준일: {date.today()}"
    )
    st.subheader(
        "향후 7일 추천 추가 예약 수"
    )

    future_result = []

    future_dates = pd.date_range(
        start=date.today(),
        periods=7,
        freq="D"
    )

    for day in future_dates:

        day_df = df[
            (df["arrival_date"].dt.date
            == day.date()) & (df['status'] == 'Expected')
        ].copy()

        if len(day_df) == 0:

            future_result.append({
                "date": day.strftime("%m/%d"),
                "recommend": 0
            })

            continue

        X_day = day_df.drop(
            columns=[
                "customer_name",
                "status",
            ],
            errors="ignore"
        )

        cancel_prob_day = (
            model.predict_proba(X_day)[:, 1]
        )

        expected_cancel_day = (
            cancel_prob_day.sum()
        )

        recommend_day = int(
            round(expected_cancel_day)
        )

        future_result.append({
            "date": day.strftime("%m/%d"),
            "recommend": recommend_day
        })

    future_df = pd.DataFrame(
        future_result
    )

    fig_bar = px.bar(
        future_df,
        x="date",
        y="recommend",
        text="recommend",
        title="향후 7일 추천 오버부킹 수"
    )

    fig_bar.update_layout(
        showlegend=False,
        height=350
    )

    st.plotly_chart(
        fig_bar,
        use_container_width=True
    )

    # Feature Importance

    st.divider()

    st.subheader(
        "취소 예측 중요 변수 TOP 5"
    )

    try:

        classifier = (
            model.named_steps[
                "classifier"
            ]
        )

        preprocessor = (
            model.named_steps[
                "preprocessor"
            ]
        )

        feature_names = (
            preprocessor
            .get_feature_names_out()
        )

        importance_df = pd.DataFrame({
            "feature":
                feature_names,
            "importance":
                classifier.feature_importances_
        })

        importance_df = (
            importance_df
            .sort_values(
                "importance",
                ascending=False
            )
            .head(5)
        )

        fig_pie = px.pie(
            importance_df,
            names="feature",
            values="importance",
            hole=0.5,
            title="TOP5 중요 변수"
        )

        st.plotly_chart(
            fig_pie,
            use_container_width=True
        )

        st.dataframe(
            importance_df,
            use_container_width=True,
            hide_index=True
        )

    except Exception as e:

        st.warning(
            f"Feature Importance 추출 실패\n\n{e}"
        )