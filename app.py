"""
AIV 생명 보호 실드 대시보드
지역별 의료 취약성 분석 및 정책 의사결정 지원 시스템
"""

import streamlit as st
import pandas as pd

# ─────────────────────────────────────────────────
# 설정 상수
# ─────────────────────────────────────────────────

PAGE_CONFIG = {
    "page_title": "AIV 정책 의사결정 대시보드",
    "page_icon": "🛡️",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

RISK_THRESHOLDS = {
    "fatality_high": 9.0,    # 치명률 고위험 기준 (%)
    "fatality_mid": 6.0,     # 치명률 중위험 기준 (%)
    "access_time": 6.0,      # 접근시간 위험 기준 (시간)
    "aging_rate": 20.0,      # 고령화율 위험 기준 (%)
}

RISK_LABELS = {
    0: ("안전", "🟢"),
    1: ("보통", "🟡"),
    2: ("주의", "🟠"),
    3: ("위험", "🔴"),
    4: ("고위험", "🔴"),
    5: ("긴급", "🚨"),
    6: ("긴급", "🚨"),
}


# ─────────────────────────────────────────────────
# 데이터 로드
# ─────────────────────────────────────────────────

@st.cache_data
def load_data() -> pd.DataFrame:
    """지역별 의료 취약성 데이터를 로드합니다."""
    raw = {
        "지역":        ["서울",  "경기",  "강원",  "전북",  "경북",  "전남"],
        "치명률(%)":   [ 4.26,   5.96,   11.02,   9.89,   9.52,   9.37],
        "접근시간(시간)": [ 2.0,  2.5,    8.4,     7.5,    7.8,    8.0],
        "고령화율(%)": [16.1,   17.5,   22.3,    21.8,   22.0,   22.5],
    }
    df = pd.DataFrame(raw)
    df["위험도 점수"] = df.apply(_calculate_risk, axis=1)
    df["위험 등급"]  = df["위험도 점수"].map(lambda s: RISK_LABELS.get(s, ("긴급", "🚨"))[0])
    return df


# ─────────────────────────────────────────────────
# 비즈니스 로직
# ─────────────────────────────────────────────────

def _calculate_risk(row: pd.Series) -> int:
    """
    지역별 위험도 점수를 계산합니다. (최대 6점)

    채점 기준:
    - 치명률 > 9%   → +2점
    - 치명률 > 6%   → +1점
    - 접근시간 > 6h → +2점
    - 고령화율 > 20% → +2점
    """
    score = 0
    fatality = row["치명률(%)"]
    if fatality > RISK_THRESHOLDS["fatality_high"]:
        score += 2
    elif fatality > RISK_THRESHOLDS["fatality_mid"]:
        score += 1

    if row["접근시간(시간)"] > RISK_THRESHOLDS["access_time"]:
        score += 2

    if row["고령화율(%)"] > RISK_THRESHOLDS["aging_rate"]:
        score += 2

    return score


def get_policy_recommendations(region_row: pd.Series) -> list[str]:
    """지역 데이터를 기반으로 정책 추천 목록을 반환합니다."""
    recommendations = []

    if region_row["접근시간(시간)"] > RISK_THRESHOLDS["access_time"]:
        recommendations.append("🚑 모바일 ICU 우선 배치 필요")

    if region_row["치명률(%)"] > RISK_THRESHOLDS["fatality_high"]:
        recommendations.append("⚠️ 고위험군 집중 관리 프로그램 운영")

    if region_row["고령화율(%)"] > RISK_THRESHOLDS["aging_rate"]:
        recommendations.append("👴 방문 검진 및 실버 핫라인 강화")

    return recommendations


# ─────────────────────────────────────────────────
# UI 컴포넌트
# ─────────────────────────────────────────────────

def render_sidebar(df: pd.DataFrame) -> str:
    """사이드바를 렌더링하고 선택된 지역을 반환합니다."""
    st.sidebar.header("⚙️ 분석 설정")
    selected_region = st.sidebar.selectbox("지역 선택", df["지역"])
    st.sidebar.markdown("---")
    st.sidebar.caption("AIV 정책 의사결정 시스템 v1.0")
    return selected_region


def render_overview(df: pd.DataFrame) -> None:
    """지역별 전체 현황 테이블을 렌더링합니다."""
    st.subheader("📊 지역별 현황")
    st.dataframe(
        df.style.background_gradient(subset=["위험도 점수"], cmap="RdYlGn_r"),
        use_container_width=True,
        hide_index=True,
    )


def render_region_analysis(region_row: pd.Series) -> None:
    """선택된 지역의 상세 분석을 렌더링합니다."""
    st.subheader(f"🚨 {region_row['지역']} 위험도 분석")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("치명률",   f"{region_row['치명률(%)']}%")
    col2.metric("접근시간", f"{region_row['접근시간(시간)']}시간")
    col3.metric("고령화율", f"{region_row['고령화율(%)']}%")

    risk_score = region_row["위험도 점수"]
    label, icon = RISK_LABELS.get(risk_score, ("긴급", "🚨"))
    col4.metric("위험도 점수", f"{icon} {risk_score}점 ({label})")


def render_policy_recommendations(region_row: pd.Series) -> None:
    """정책 추천 사항을 렌더링합니다."""
    st.subheader("🏥 정책 추천")
    recommendations = get_policy_recommendations(region_row)

    if not recommendations:
        st.success("✅ 현재 위험도 낮음 — 기존 정책 유지 권고")
    else:
        for rec in recommendations:
            st.warning(rec)


def render_top_risk_regions(df: pd.DataFrame, top_n: int = 3) -> None:
    """위험도 상위 지역을 렌더링합니다."""
    st.subheader(f"📌 고위험 지역 TOP {top_n}")
    top = (
        df.sort_values("위험도 점수", ascending=False)
        .head(top_n)[["지역", "위험도 점수", "위험 등급"]]
        .reset_index(drop=True)
    )
    top.index += 1
    st.table(top)


# ─────────────────────────────────────────────────
# 앱 진입점
# ─────────────────────────────────────────────────

def main() -> None:
    st.set_page_config(**PAGE_CONFIG)
    st.title("🛡️ AIV 생명 보호 실드 대시보드")
    st.caption("지역별 의료 취약성 분석 및 정책 의사결정 지원 시스템")
    st.divider()

    df = load_data()
    selected_region = render_sidebar(df)
    region_row = df[df["지역"] == selected_region].iloc[0]

    render_overview(df)
    st.divider()
    render_region_analysis(region_row)
    st.divider()
    render_policy_recommendations(region_row)
    st.divider()
    render_top_risk_regions(df)


if __name__ == "__main__":
    main()
