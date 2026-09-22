import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── 페이지 기본 설정 ──────────────────────────────────────────
st.set_page_config(
    page_title="탐색 | 뇌졸중 예측 실습실",
    page_icon="🔎",
    layout="wide",
)

# ── 데이터 불러오기 ───────────────────────────────────────────
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/stroke.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL, encoding="utf-8")
    return df

df = load_data()

# 뇌졸중 레이블 열 추가 (그래프 범례용)
df["뇌졸중"] = df["stroke"].map({0: "없음", 1: "있음"})

# ── 제목 ─────────────────────────────────────────────────────
st.title("🔎 데이터 탐색")
st.markdown("---")

# ══════════════════════════════════════════════════════════════
# 1. 나이 · 평균 혈당 히스토그램
# ══════════════════════════════════════════════════════════════
st.subheader("📊 나이와 평균 혈당의 분포")

fig_hist = make_subplots(
    rows=1, cols=2,
    subplot_titles=("나이 (age) 분포", "평균 혈당 (avg_glucose_level) 분포"),
)

fig_hist.add_trace(
    go.Histogram(x=df["age"], nbinsx=30, marker_color="#4C9BE8", name="나이"),
    row=1, col=1,
)
fig_hist.add_trace(
    go.Histogram(x=df["avg_glucose_level"], nbinsx=30, marker_color="#F28B50", name="평균 혈당"),
    row=1, col=2,
)
fig_hist.update_layout(showlegend=False, height=400)
fig_hist.update_xaxes(title_text="나이", row=1, col=1)
fig_hist.update_xaxes(title_text="평균 혈당", row=1, col=2)
fig_hist.update_yaxes(title_text="인원 수", row=1, col=1)
fig_hist.update_yaxes(title_text="인원 수", row=1, col=2)

st.plotly_chart(fig_hist, use_container_width=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════
# 2. 뇌졸중 유무별 나이 · 평균 혈당 상자그림 + 평균값 표
# ══════════════════════════════════════════════════════════════
st.subheader("📦 뇌졸중 유무별 나이·평균 혈당 비교 (상자그림)")

color_map = {"없음": "#4C9BE8", "있음": "#E8534C"}

fig_box = make_subplots(
    rows=1, cols=2,
    subplot_titles=("나이 (age)", "평균 혈당 (avg_glucose_level)"),
)

for group in ["없음", "있음"]:
    sub = df[df["뇌졸중"] == group]
    fig_box.add_trace(
        go.Box(
            y=sub["age"],
            name=f"뇌졸중 {group}",
            marker_color=color_map[group],
            boxmean=True,
        ),
        row=1, col=1,
    )
    fig_box.add_trace(
        go.Box(
            y=sub["avg_glucose_level"],
            name=f"뇌졸중 {group}",
            marker_color=color_map[group],
            boxmean=True,
            showlegend=False,
        ),
        row=1, col=2,
    )

fig_box.update_layout(height=450, legend_title_text="뇌졸중")
fig_box.update_yaxes(title_text="나이", row=1, col=1)
fig_box.update_yaxes(title_text="평균 혈당", row=1, col=2)

st.plotly_chart(fig_box, use_container_width=True)

# 평균값 표
mean_df = (
    df.groupby("뇌졸중")[["age", "avg_glucose_level"]]
    .mean()
    .round(2)
    .reset_index()
    .rename(columns={"뇌졸중": "뇌졸중 유무", "age": "나이 평균", "avg_glucose_level": "평균 혈당 평균"})
)
st.markdown("**두 그룹의 평균값**")
st.dataframe(mean_df, use_container_width=True, hide_index=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════
# 3. 고혈압·심장병 유무별 뇌졸중 비율 막대그래프
# ══════════════════════════════════════════════════════════════
st.subheader("📈 고혈압·심장병 유무별 뇌졸중 비율")

def stroke_ratio_bar(col, col_label, label_map):
    """그룹별 뇌졸중 비율 막대그래프를 반환하는 함수"""
    ratio = (
        df.groupby(col)["stroke"]
        .mean()
        .mul(100)
        .round(2)
        .reset_index()
        .rename(columns={col: col_label, "stroke": "뇌졸중 비율 (%)"})
    )
    ratio[col_label] = ratio[col_label].map(label_map)
    fig = px.bar(
        ratio,
        x=col_label,
        y="뇌졸중 비율 (%)",
        text="뇌졸중 비율 (%)",
        color=col_label,
        color_discrete_sequence=["#4C9BE8", "#E8534C"],
        title=f"{col_label}별 뇌졸중 비율",
    )
    fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
    fig.update_layout(showlegend=False, height=380, yaxis_range=[0, ratio["뇌졸중 비율 (%)"].max() * 1.3])
    return fig

col_left, col_right = st.columns(2)

with col_left:
    fig_hyp = stroke_ratio_bar(
        "hypertension", "고혈압",
        {0: "없음", 1: "있음"},
    )
    st.plotly_chart(fig_hyp, use_container_width=True)

with col_right:
    fig_heart = stroke_ratio_bar(
        "heart_disease", "심장병",
        {0: "없음", 1: "있음"},
    )
    st.plotly_chart(fig_heart, use_container_width=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════
# 4. BMI 결측자 뇌졸중 비율 vs 전체 비율
# ══════════════════════════════════════════════════════════════
st.subheader("🔍 BMI 결측자와 전체의 뇌졸중 비율 비교")

bmi_null_mask = df["bmi"].isna()
bmi_null_count    = int(bmi_null_mask.sum())
bmi_null_stroke   = df.loc[bmi_null_mask, "stroke"].mean() * 100
overall_stroke    = df["stroke"].mean() * 100

bmi_compare = pd.DataFrame({
    "구분"          : ["BMI 결측자", "전체"],
    "인원 수 (명)"  : [bmi_null_count, len(df)],
    "뇌졸중 비율(%)": [round(bmi_null_stroke, 2), round(overall_stroke, 2)],
})

st.dataframe(bmi_compare, use_container_width=True, hide_index=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════
# 5. 흡연 상태별 인원 수 표
# ══════════════════════════════════════════════════════════════
st.subheader("🚬 흡연 상태별 인원 수")

smoking_count = (
    df["smoking_status"]
    .value_counts()
    .reset_index()
    .rename(columns={"smoking_status": "흡연 상태", "count": "인원 수 (명)"})
)
# 비율 열 추가
smoking_count["비율 (%)"] = (smoking_count["인원 수 (명)"] / len(df) * 100).round(2)

st.dataframe(smoking_count, use_container_width=True, hide_index=True)
