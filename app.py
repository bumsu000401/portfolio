import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf

# ─── Page config ────────────────────────────────────────────────────────────
st.set_page_config(page_title="포트폴리오 투자 계산기", page_icon="📈", layout="wide")

# ─── Constants ──────────────────────────────────────────────────────────────
DEFAULT_ASSETS = ["QLD", "SCHD", "Bitcoin"]
DEFAULT_RATIOS = {"QLD": 30.0, "SCHD": 30.0, "Bitcoin": 15.0}
TICKER_MAP = {
    "QLD": "QLD",
    "SCHD": "SCHD",
    "Bitcoin": "BTC-USD",
}
# Assets that are cash (no ticker, KRW direct input)
CASH_ASSETS = set()

# ─── Session state init ──────────────────────────────────────────────────────
if "assets" not in st.session_state:
    st.session_state["assets"] = list(DEFAULT_ASSETS)

if "target_ratios" not in st.session_state:
    st.session_state["target_ratios"] = dict(DEFAULT_RATIOS)

if "holdings_qty" not in st.session_state:
    # Quantity held (shares, BTC amount, or KRW for cash)
    st.session_state["holdings_qty"] = {a: 0.0 for a in DEFAULT_ASSETS}

if "holdings_krw" not in st.session_state:
    # Computed KRW value per asset (updated on each render)
    st.session_state["holdings_krw"] = {a: 0.0 for a in DEFAULT_ASSETS}

if "asset_tickers" not in st.session_state:
    # Ticker symbol for each asset (editable by user)
    st.session_state["asset_tickers"] = dict(TICKER_MAP)

if "asset_is_cash" not in st.session_state:
    # Whether this asset uses direct KRW input instead of qty × price
    st.session_state["asset_is_cash"] = {a: False for a in DEFAULT_ASSETS}

if "new_asset_name" not in st.session_state:
    st.session_state["new_asset_name"] = ""

# ─── Price fetching ──────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def get_price(ticker: str) -> float | None:
    """Fetch latest USD price via yfinance. Returns None on failure."""
    try:
        data = yf.Ticker(ticker)
        price = data.fast_info["last_price"]
        return float(price) if price else None
    except Exception:
        return None


@st.cache_data(ttl=300)
def get_usdkrw() -> float | None:
    """Fetch USD/KRW exchange rate. Returns None on failure."""
    return get_price("USDKRW=X")


def asset_krw_value(asset: str, qty: float) -> tuple[float | None, str]:
    """
    Compute KRW value for an asset given its quantity.
    Returns (krw_value, status_message).
    status_message is '' on success, or an error hint.
    """
    if st.session_state["asset_is_cash"].get(asset, False):
        return qty, ""  # qty IS the KRW amount

    ticker = st.session_state["asset_tickers"].get(asset)
    if not ticker:
        return None, "티커 없음 — 직접 KRW 입력 필요"

    usd_price = get_price(ticker)
    if usd_price is None:
        return None, f"{ticker} 가격 조회 실패"

    usdkrw = get_usdkrw()
    if usdkrw is None:
        return None, "환율 조회 실패"

    return qty * usd_price * usdkrw, ""


# ─── Asset management callbacks ──────────────────────────────────────────────
def add_asset():
    name = st.session_state["new_asset_name"].strip()
    if name and name not in st.session_state["assets"]:
        st.session_state["assets"].append(name)
        st.session_state["target_ratios"][name] = 0.0
        st.session_state["holdings_qty"][name] = 0.0
        st.session_state["holdings_krw"][name] = 0.0
        st.session_state["asset_tickers"][name] = ""
        st.session_state["asset_is_cash"][name] = False
    st.session_state["new_asset_name"] = ""


def delete_asset(asset: str):
    if asset in st.session_state["assets"]:
        st.session_state["assets"].remove(asset)
        for d in ["target_ratios", "holdings_qty", "holdings_krw",
                  "asset_tickers", "asset_is_cash"]:
            st.session_state[d].pop(asset, None)


# ─── Investment algorithm ────────────────────────────────────────────────────
def calculate_investment(
    holdings: dict[str, float],
    target_ratios: dict[str, float],
    monthly_budget: float,
) -> dict[str, float]:
    """
    Allocate monthly_budget across assets to bring portfolio closest to target.

    Strategy: fill the largest deficit first (greedy), then assign any
    remainder to the still-most-underweight asset.

    Args:
        holdings:      {asset: current_krw_value}
        target_ratios: {asset: target_pct}  (should sum to 100)
        monthly_budget: total KRW to invest this month

    Returns:
        {asset: krw_to_invest}  — values sum to monthly_budget
    """
    total = sum(holdings.values()) + monthly_budget
    result = {asset: 0.0 for asset in holdings}
    remaining = monthly_budget

    # How much each asset needs to reach its target amount
    deficits = {
        asset: (target_ratios.get(asset, 0) / 100) * total - holdings[asset]
        for asset in holdings
    }

    # Sort by largest deficit first
    sorted_assets = sorted(deficits, key=lambda x: deficits[x], reverse=True)

    for asset in sorted_assets:
        if remaining <= 0:
            break
        invest = min(max(deficits[asset], 0.0), remaining)
        result[asset] = invest
        remaining -= invest

    # Any leftover goes to the most underweight asset
    if remaining > 0:
        top_asset = sorted_assets[0]
        result[top_asset] = result.get(top_asset, 0.0) + remaining

    return result


# ─── Rebalancing algorithm ───────────────────────────────────────────────────
def calculate_rebalance(
    holdings: dict[str, float],
    target_ratios: dict[str, float],
) -> dict[str, float]:
    """
    Compute buy/sell amounts to rebalance to target ratios.
    Positive = sell, Negative = buy.
    """
    total = sum(holdings.values())
    if total == 0:
        return {asset: 0.0 for asset in holdings}
    return {
        asset: holdings[asset] - (target_ratios.get(asset, 0) / 100) * total
        for asset in holdings
    }


# ─── Chart helpers ────────────────────────────────────────────────────────────
def make_pie(labels: list[str], values: list[float], title: str) -> go.Figure:
    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.35,
            textinfo="label+percent",
            hovertemplate="%{label}<br>%{value:,.0f}원<br>%{percent}<extra></extra>",
        )
    )
    fig.update_layout(
        title_text=title,
        title_x=0.5,
        margin=dict(t=50, b=20, l=20, r=20),
        height=380,
        showlegend=False,
    )
    return fig


# ════════════════════════════════════════════════════════════════════════════
#  SIDEBAR — 정기 리밸런싱 계산기
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.header("📊 정기 리밸런싱 계산기")
    st.caption("현재 보유 금액 기준으로 매수/매도 금액을 계산합니다.")

    holdings_krw = st.session_state["holdings_krw"]
    target_ratios = st.session_state["target_ratios"]

    if sum(holdings_krw.values()) == 0:
        st.info("메인 화면에서 보유 수량을 입력하면 자동으로 반영됩니다.")
    else:
        rebalance = calculate_rebalance(holdings_krw, target_ratios)
        total_assets = sum(holdings_krw.values())

        rows = []
        for asset in st.session_state["assets"]:
            current = holdings_krw.get(asset, 0.0)
            target_pct = target_ratios.get(asset, 0.0)
            target_amt = (target_pct / 100) * total_assets
            diff = rebalance.get(asset, 0.0)
            rows.append({
                "자산": asset,
                "현재 금액 (원)": current,
                "목표 금액 (원)": target_amt,
                "매수/매도 (원)": diff,
            })

        df_reb = pd.DataFrame(rows)

        def color_rebalance(val):
            if isinstance(val, float):
                if val > 0:
                    return "color: #e74c3c"   # 매도 → 빨강
                elif val < 0:
                    return "color: #27ae60"   # 매수 → 녹색
            return ""

        styled = df_reb.style.format({
            "현재 금액 (원)": "{:,.0f}",
            "목표 금액 (원)": "{:,.0f}",
            "매수/매도 (원)": "{:+,.0f}",
        }).applymap(color_rebalance, subset=["매수/매도 (원)"])

        st.dataframe(styled, use_container_width=True, hide_index=True)

        buy_total = sum(-v for v in rebalance.values() if v < 0)
        sell_total = sum(v for v in rebalance.values() if v > 0)
        st.caption(f"총 매수: **{buy_total:,.0f}원** | 총 매도: **{sell_total:,.0f}원**")


# ════════════════════════════════════════════════════════════════════════════
#  MAIN PAGE
# ════════════════════════════════════════════════════════════════════════════
st.title("📈 포트폴리오 투자 계산기")
st.caption("직장인을 위한 월 투자 배분 & 리밸런싱 도우미")

assets = st.session_state["assets"]

# ────────────────────────────────────────────────────────────────────────────
#  섹션 A: 목표 비율 설정
# ────────────────────────────────────────────────────────────────────────────
st.subheader("🎯 섹션 A — 목표 비율 설정")

ratio_cols = st.columns(min(len(assets), 4))
for i, asset in enumerate(assets):
    col = ratio_cols[i % len(ratio_cols)]
    with col:
        new_ratio = st.number_input(
            f"{asset} (%)",
            min_value=0.0,
            max_value=100.0,
            value=float(st.session_state["target_ratios"].get(asset, 0.0)),
            step=1.0,
            key=f"ratio_{asset}",
        )
        st.session_state["target_ratios"][asset] = new_ratio

total_ratio = sum(st.session_state["target_ratios"].get(a, 0) for a in assets)
if abs(total_ratio - 100.0) > 0.01:
    st.warning(f"⚠️ 목표 비율 합계가 {total_ratio:.1f}%입니다. 100%가 되어야 합니다.")
else:
    st.success(f"✅ 목표 비율 합계: {total_ratio:.1f}%")

# Asset add UI
st.markdown("---")
add_col1, add_col2 = st.columns([3, 1])
with add_col1:
    st.text_input(
        "새 자산 이름",
        placeholder="예: 원화 현금 비상금, 달러 현금, TQQQ ...",
        key="new_asset_name",
    )
with add_col2:
    st.write("")  # vertical align
    st.write("")
    st.button("＋ 자산 추가", on_click=add_asset, use_container_width=True)

# Delete buttons
if assets:
    st.markdown("**자산 삭제:**")
    del_cols = st.columns(min(len(assets), 6))
    for i, asset in enumerate(list(assets)):
        with del_cols[i % len(del_cols)]:
            st.button(
                f"🗑️ {asset}",
                key=f"del_{asset}",
                on_click=delete_asset,
                args=(asset,),
                use_container_width=True,
            )

# ────────────────────────────────────────────────────────────────────────────
#  섹션 B: 현재 보유 금액 입력
# ────────────────────────────────────────────────────────────────────────────
st.subheader("💼 섹션 B — 현재 보유 수량/금액 입력")
st.caption("미국 주식/BTC: 수량 입력 → 실시간 USD 가격 × 환율로 KRW 자동 계산  |  현금 자산: KRW 직접 입력")

# Fetch exchange rate once
usdkrw_rate = get_usdkrw()
rate_display = f"{usdkrw_rate:,.1f}" if usdkrw_rate else "조회 실패"
st.caption(f"현재 USD/KRW: **{rate_display}**")

holdings_krw_updated = {}

for asset in assets:
    is_cash = st.session_state["asset_is_cash"].get(asset, False)

    b_col1, b_col2, b_col3, b_col4 = st.columns([2, 2, 2, 2])

    with b_col1:
        st.markdown(f"**{asset}**")
        cash_toggle = st.checkbox(
            "현금 직접입력",
            value=is_cash,
            key=f"cash_{asset}",
        )
        st.session_state["asset_is_cash"][asset] = cash_toggle

    with b_col2:
        if not cash_toggle:
            ticker_val = st.text_input(
                "티커",
                value=st.session_state["asset_tickers"].get(asset, ""),
                key=f"ticker_{asset}",
                placeholder="예: QLD",
            )
            st.session_state["asset_tickers"][asset] = ticker_val.strip().upper()

    with b_col3:
        if cash_toggle:
            qty = st.number_input(
                "보유 금액 (KRW)",
                min_value=0.0,
                value=float(st.session_state["holdings_qty"].get(asset, 0.0)),
                step=10000.0,
                format="%.0f",
                key=f"qty_{asset}",
            )
        else:
            qty = st.number_input(
                "보유 수량",
                min_value=0.0,
                value=float(st.session_state["holdings_qty"].get(asset, 0.0)),
                step=0.001,
                format="%.4f",
                key=f"qty_{asset}",
            )
        st.session_state["holdings_qty"][asset] = qty

    with b_col4:
        krw_val, err_msg = asset_krw_value(asset, qty)
        if krw_val is not None:
            st.metric("KRW 평가액", f"{krw_val:,.0f}원")
            holdings_krw_updated[asset] = krw_val
        else:
            st.warning(err_msg)
            # Fallback: manual KRW input
            fallback = st.number_input(
                "수동 입력 (KRW)",
                min_value=0.0,
                value=float(st.session_state["holdings_krw"].get(asset, 0.0)),
                step=10000.0,
                format="%.0f",
                key=f"fallback_krw_{asset}",
            )
            holdings_krw_updated[asset] = fallback

    st.divider()

# Update session_state with computed KRW values
st.session_state["holdings_krw"] = holdings_krw_updated

total_assets_krw = sum(holdings_krw_updated.values())
st.metric("📦 총 자산 (KRW)", f"{total_assets_krw:,.0f}원")

# ────────────────────────────────────────────────────────────────────────────
#  섹션 C: 현재 포트폴리오 파이차트
# ────────────────────────────────────────────────────────────────────────────
st.subheader("📊 섹션 C — 현재 포트폴리오 현황")

if total_assets_krw > 0:
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        current_values = [holdings_krw_updated.get(a, 0.0) for a in assets]
        fig_current = make_pie(assets, current_values, "현재 실제 비율")
        st.plotly_chart(fig_current, use_container_width=True)

    with chart_col2:
        target_values = [st.session_state["target_ratios"].get(a, 0.0) for a in assets]
        fig_target = make_pie(assets, target_values, "목표 비율")
        st.plotly_chart(fig_target, use_container_width=True)
else:
    st.info("섹션 B에서 보유 수량을 입력하면 차트가 표시됩니다.")

# ────────────────────────────────────────────────────────────────────────────
#  섹션 D: 월 투자금 배분
# ────────────────────────────────────────────────────────────────────────────
st.subheader("💰 섹션 D — 이번 달 투자금 배분")

monthly_budget = st.number_input(
    "이번 달 투자 금액 (KRW)",
    min_value=0.0,
    value=0.0,
    step=100000.0,
    format="%.0f",
    help="이번 달 새로 투자할 총 금액을 입력하세요.",
)

if monthly_budget > 0 and abs(total_ratio - 100.0) <= 0.01:
    allocation = calculate_investment(
        holdings=holdings_krw_updated,
        target_ratios=st.session_state["target_ratios"],
        monthly_budget=monthly_budget,
    )

    # Build result dataframe
    post_holdings = {
        asset: holdings_krw_updated.get(asset, 0.0) + allocation.get(asset, 0.0)
        for asset in assets
    }
    post_total = sum(post_holdings.values())

    rows = []
    for asset in assets:
        invest_amt = allocation.get(asset, 0.0)
        post_amt = post_holdings[asset]
        post_pct = (post_amt / post_total * 100) if post_total > 0 else 0.0
        rows.append({
            "자산": asset,
            "투자 금액 (원)": invest_amt,
            "투자 후 예상 금액 (원)": post_amt,
            "투자 후 예상 비율 (%)": post_pct,
            "목표 비율 (%)": st.session_state["target_ratios"].get(asset, 0.0),
        })

    df_alloc = pd.DataFrame(rows)
    styled_alloc = df_alloc.style.format({
        "투자 금액 (원)": "{:,.0f}",
        "투자 후 예상 금액 (원)": "{:,.0f}",
        "투자 후 예상 비율 (%)": "{:.1f}",
        "목표 비율 (%)": "{:.1f}",
    }).background_gradient(subset=["투자 금액 (원)"], cmap="Greens")

    st.dataframe(styled_alloc, use_container_width=True, hide_index=True)

    # Verify allocation sums match budget
    alloc_sum = sum(allocation.values())
    st.caption(f"배분 합계 확인: **{alloc_sum:,.0f}원** (투자금 {monthly_budget:,.0f}원)")

    # Post-investment pie chart
    if post_total > 0:
        st.markdown("**투자 후 예상 포트폴리오:**")
        post_values = [post_holdings.get(a, 0.0) for a in assets]
        fig_post = make_pie(assets, post_values, "투자 후 예상 비율")
        st.plotly_chart(fig_post, use_container_width=True)

elif monthly_budget > 0 and abs(total_ratio - 100.0) > 0.01:
    st.warning("목표 비율 합계가 100%가 아니라 배분 계산을 실행할 수 없습니다. 섹션 A를 확인하세요.")
else:
    st.info("투자 금액을 입력하면 자산별 배분 금액이 계산됩니다.")
