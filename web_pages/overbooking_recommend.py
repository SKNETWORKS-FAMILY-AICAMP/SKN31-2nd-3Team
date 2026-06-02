import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
import plotly.graph_objects as go
from utils.utils import DEMO_TODAY, get_predictions, load_model

model = load_model()

def run():
    # 캐싱된 예측 결과 포함된 df 가져오기
    df = get_predictions(return_df=True)

    st.title("📈 오버부킹 추천 시스템")
    st.caption(f"기준일: {DEMO_TODAY.strftime('%Y년 %m월 %d일')}")
    st.divider()

    # ── 향후 7일 전체 계산 ───────────────────────────────────────────────────
    future_dates = pd.date_range(start=DEMO_TODAY, periods=18, freq="D")
    future_result = []

    for day in future_dates:
        day_df = df[
            (df["arrival_dt"].dt.date == day.date()) &
            (df["status"] == "Expected")
        ].copy()

        if len(day_df) == 0:
            future_result.append({
                "date": day.strftime("%m/%d"),
                "full_date": day,
                "예약수": 0,
                "예측취소": 0.0,
                "추천추가": 0,
                "예상투숙": 0.0,
            })
            continue

        # cancel_proba 컬럼을 그대로 활용
        exp_cancel = (day_df['cancel_proba'] / 100).sum()
        exp_stay   = len(day_df) - exp_cancel

        future_result.append({
            "date":     day.strftime("%m/%d"),
            "full_date": day,
            "예약수":   len(day_df),
            "예측취소": round(exp_cancel, 1),
            "추천추가": int(round(exp_cancel)),
            "예상투숙": round(exp_stay, 1),
        })

    future_df = pd.DataFrame(future_result)


    # ── 날짜 필터 ────────────────────────────────────────────────────────────
    col_filter, col_info = st.columns([2, 3])
    with col_filter:
        selected_date = st.selectbox(
            "📅 날짜 선택",
            options=future_df["date"].tolist(),
            index=0
        )

    selected = future_df[future_df["date"] == selected_date].iloc[0]

    with col_info:
        st.write("")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("예약 건수",  f"{int(selected['예약수'])}건")
        c2.metric("예측 취소",  f"{selected['예측취소']:.1f}명")
        c3.metric("예상 투숙",  f"{selected['예상투숙']:.1f}명")
        c4.metric("추천 추가",  f"{int(selected['추천추가'])}건",
                  delta="추가 예약 가능" if selected['추천추가'] > 0 else "추가 불필요",
                  delta_color="normal" if selected['추천추가'] > 0 else "off")

    st.divider()

    # ── 그래프 2개 나란히 ─────────────────────────────────────────────────────
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.subheader("📊 날짜별 예약 vs 예측 취소")
        colors = ["#F09595" if d == selected_date else "#85B7EB" for d in future_df["date"]]
        fig1 = go.Figure()
        fig1.add_bar(
            x=future_df["date"], y=future_df["예약수"],
            name="전체 예약수", marker_color=colors,
            text=future_df["예약수"], textposition="outside"
        )
        fig1.add_scatter(
            x=future_df["date"], y=future_df["예측취소"],
            name="예측 취소", mode="lines+markers+text",
            line=dict(color="#E24B4A", width=2),
            marker=dict(size=8),
            text=[f"{x:.1f}" for x in future_df["예측취소"]],
            textposition="top center",
            textfont=dict(size=10)
        )
        fig1.update_layout(
            height=320, margin=dict(t=20,b=20,l=0,r=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(gridcolor="#f0f0f0"),
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col_g2:
        st.subheader("🟢 날짜별 추천 추가 예약 수")
        bar_colors = ["#639922" if d == selected_date else "#C0DD97" for d in future_df["date"]]
        fig2 = go.Figure()
        fig2.add_bar(
            x=future_df["date"], y=future_df["추천추가"],
            marker_color=bar_colors,
            text=future_df["추천추가"], textposition="outside"
        )
        fig2.update_layout(
            height=320, margin=dict(t=20,b=20,l=0,r=0),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(gridcolor="#f0f0f0"),
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── 선택 날짜 상세 파이 차트 ─────────────────────────────────────────────
    st.subheader(f"🔎 {selected_date} 상세 — 예약 구성")
    col_pie, col_fi = st.columns(2)

    with col_pie:
        if selected["예약수"] > 0:
            pie_df = pd.DataFrame({
                "구분": ["예상 실제 투숙", "예측 취소"],
                "인원": [selected["예상투숙"], selected["예측취소"]]
            })
            fig_pie = px.pie(
                pie_df, names="구분", values="인원",
                color="구분",
                color_discrete_map={"예상 실제 투숙": "#85B7EB", "예측 취소": "#F09595"},
                hole=0.45
            )
            fig_pie.update_layout(height=280, margin=dict(t=20,b=20,l=0,r=0))
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("해당 날짜 예약 데이터가 없습니다.")

    # ── Feature Importance ────────────────────────────────────────────────────
    with col_fi:
        st.subheader("🔍 취소 예측 중요 변수 TOP 5")
        try:
            importance_df = pd.DataFrame({
                "feature":    model.named_steps["preprocessor"].get_feature_names_out(),
                "importance": model.named_steps["classifier"].feature_importances_
            }).sort_values("importance", ascending=False).head(5)

            importance_df["feature"] = importance_df["feature"].str.replace(r"^(num__|cat__)", "", regex=True)

            fig_fi = px.bar(
                importance_df, x="importance", y="feature",
                orientation="h",
                color="importance",
                color_continuous_scale=["#B5D4F4", "#185FA5"],
                text=importance_df["importance"].apply(lambda x: f"{x:.3f}")
            )
            fig_fi.update_layout(
                height=280, margin=dict(t=20,b=20,l=0,r=0),
                showlegend=False, coloraxis_showscale=False,
                yaxis=dict(autorange="reversed"),
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(gridcolor="#f0f0f0")
            )
            fig_fi.update_traces(textposition="outside")
            st.plotly_chart(fig_fi, use_container_width=True)

        except Exception as e:
            st.warning(f"Feature Importance 추출 실패: {e}")