import streamlit as st
import pandas as pd

st.set_page_config(page_title="AIV 정책 의사결정 대시보드", layout="wide")

st.title("🛡️ AIV 생명 보호 실드 대시보드")

# -------------------------
# 데이터 (간단 샘플)
# -------------------------
data = {
    "지역": ["서울", "경기", "강원", "전북", "경북", "전남"],
    "치명률(%)": [4.26, 5.96, 11.02, 9.89, 9.52, 9.37],
    "접근시간(시간)": [2.0, 2.5, 8.4, 7.5, 7.8, 8.0],
    "고령화율(%)": [16.1, 17.5, 22.3, 21.8, 22.0, 22.5]
}

df = pd.DataFrame(data)

# -------------------------
# 사이드바
# -------------------------
st.sidebar.header("⚙️ 분석 설정")

selected_region = st.sidebar.selectbox(
    "지역 선택",
    df["지역"]
)

# -------------------------
# 1. 기본 현황
# -------------------------
st.subheader("📊 지역별 현황")

st.dataframe(df, use_container_width=True)

# -------------------------
# 2. 위험도 평가 함수
# -------------------------
def calculate_risk(row):
    score = 0
    
    if row["치명률(%)"] > 9:
        score += 2
    elif row["치명률(%)"] > 6:
        score += 1
        
    if row["접근시간(시간)"] > 6:
        score += 2
        
    if row["고령화율(%)"] > 20:
        score += 2
        
    return score

df["위험도 점수"] = df.apply(calculate_risk, axis=1)

# -------------------------
# 3. 선택 지역 분석
# -------------------------
st.subheader("🚨 지역 위험도 분석")

region_data = df[df["지역"] == selected_region].iloc[0]

st.write(f"### 📍 {selected_region}")

col1, col2, col3 = st.columns(3)

col1.metric("치명률", f"{region_data['치명률(%)']}%")
col2.metric("접근시간", f"{region_data['접근시간(시간)']}시간")
col3.metric("고령화율", f"{region_data['고령화율(%)']}%")

st.write("### 🔥 위험도 점수:", region_data["위험도 점수"])

# -------------------------
# 4. 정책 추천 로직
# -------------------------
st.subheader("🚑 정책 추천")

recommendations = []

if region_data["접근시간(시간)"] > 6:
    recommendations.append("모바일 ICU 우선 배치 필요")

if region_data["치명률(%)"] > 9:
    recommendations.append("고위험군 집중 관리 필요")

if region_data["고령화율(%)"] > 20:
    recommendations.append("방문 검진 및 실버 핫라인 강화")

if len(recommendations) == 0:
    st.success("현재 위험도 낮음 (기존 정책 유지)")
else:
    for rec in recommendations:
        st.warning(rec)

# -------------------------
# 5. 전체 위험 지역
# -------------------------
st.subheader("📌 고위험 지역 TOP")

top_regions = df.sort_values("위험도 점수", ascending=False).head(3)

st.table(top_regions[["지역", "위험도 점수"]])
