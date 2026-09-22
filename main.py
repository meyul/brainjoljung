import streamlit as st
import pandas as pd

# ── 페이지 기본 설정 ──────────────────────────────────────────
st.set_page_config(
    page_title="뇌졸중 예측 실습실",
    page_icon="🧠",
    layout="wide",
)

# ── 데이터 불러오기 ───────────────────────────────────────────
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/stroke.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL, encoding="utf-8")
    return df

df = load_data()

# ── 앱 제목 ───────────────────────────────────────────────────
st.title("🧠 뇌졸중 예측 실습실")
st.markdown("---")

# ── 요약 카드 4개 ─────────────────────────────────────────────
total_people   = len(df)
total_cols     = len(df.columns)
stroke_count   = int(df["stroke"].sum())
stroke_ratio   = stroke_count / total_people * 100

c1, c2, c3, c4 = st.columns(4)
c1.metric("👥 전체 사람 수",  f"{total_people:,} 명")
c2.metric("📋 열 개수",       f"{total_cols} 개")
c3.metric("⚠️ 뇌졸중 환자 수", f"{stroke_count:,} 명")
c4.metric("📊 뇌졸중 비율",   f"{stroke_ratio:.2f} %")

st.markdown("---")

# ── 열 정보 표 ────────────────────────────────────────────────
st.subheader("📌 데이터 열 정보")
st.caption("💡 '우리말 뜻' 칸은 교재를 참고하여 직접 채워 보세요.")

col_info = []
for col in df.columns:
    dtype     = str(df[col].dtype)
    null_cnt  = int(df[col].isna().sum())
    unique    = df[col].dropna().unique()

    if len(unique) <= 6:
        val_desc = " / ".join([str(v) for v in sorted(unique)])
    else:
        val_desc = f"수치형 ({df[col].dropna().min():.1f} ~ {df[col].dropna().max():.1f})"

    col_info.append({
        "열 이름"    : col,
        "우리말 뜻"  : "",          # 학습자가 직접 채우는 칸
        "자료형"     : dtype,
        "값의 종류"  : val_desc,
        "빈 값 개수" : null_cnt,
    })

info_df = pd.DataFrame(col_info)
st.dataframe(info_df, use_container_width=True, hide_index=True)

st.markdown("---")

# ── 데이터 미리보기 ───────────────────────────────────────────
st.subheader("🔍 데이터 미리보기 (처음 5행)")
st.dataframe(df.head(), use_container_width=True, hide_index=True)

st.markdown("---")

# ── 데이터 출처 ───────────────────────────────────────────────
st.subheader("📎 데이터 출처")
source_text = st.text_area(
    label="교재를 참고하여 데이터 출처를 직접 입력하세요.",
    placeholder="예) Kaggle - Stroke Prediction Dataset ...",
    height=80,
)
if source_text.strip():
    st.info(f"**출처:** {source_text.strip()}")
