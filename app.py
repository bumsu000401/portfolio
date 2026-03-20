import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="포트폴리오",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── CSS — dark card UI ───────────────────────────────────────────────────────
st.markdown("""
<style>
/* Dark background */
[data-testid="stAppViewContainer"] { background-color: #111111; }
[data-testid="stHeader"]           { background-color: #111111; }
[data-testid="stSidebar"]          { background-color: #1a1a1a; }

/* Hide default padding */
.block-container { padding-top: 1.5rem; }

/* Tab bar */
.stTabs [data-baseweb="tab-list"] {
    background-color: #1c1c1c;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    color: #888888;
    border-radius: 8px;
    font-weight: 500;
    font-size: 14px;
}
.stTabs [aria-selected="true"] {
    background-color: #2a2a2a !important;
    color: #ffffff !important;
}

/* Expander */
[data-testid="stExpander"] {
    background-color: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 10px;
}

/* Inputs */
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input {
    background-color: #1e1e1e;
    color: #f0f0f0;
    border: 1px solid #333;
}

/* Metric */
[data-testid="stMetric"] {
    background-color: #1a1a1a;
    border-radius: 10px;
    padding: 12px 16px;
}
[data-testid="stMetricLabel"] { color: #888888 !important; font-size: 13px; }
[data-testid="stMetricValue"] { color: #ffffff !important; }

/* Dataframe */
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }

/* ── Asset card styles ── */
.asset-card-wrap {
    background: #1a1a1a;
    border-radius: 14px;
    padding: 0 18px;
    margin: 8px 0 20px 0;
}
.asset-row {
    display: flex;
    align-items: center;
    padding: 14px 0;
    border-bottom: 1px solid #252525;
}
.asset-row:last-child { border-bottom: none; }

.asset-icon {
    width: 46px;
    height: 46px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    font-weight: 700;
    color: white;
    flex-shrink: 0;
    margin-right: 14px;
}
.asset-name   { font-size: 16px; font-weight: 600; color: #f0f0f0; }
.asset-detail { font-size: 13px; color: #777; margin-top: 3px; }
.asset-krw    { font-size: 16px; font-weight: 500; color: #f0f0f0; text-align: right; }

.total-num  { font-size: 38px; font-weight: 700; color: #fff; letter-spacing: -1px; margin: 6px 0 2px; }
.total-lbl  { font-size: 13px; color: #777; margin-bottom: 20px; }
.section-hd { font-size: 18px; font-weight: 600; color: #f0f0f0; margin: 20px 0 10px; }
</style>
""", unsafe_allow_html=True)

# ─── Constants ────────────────────────────────────────────────────────────────
ICON_COLORS = [
    "#4e9af1", "#ff6b6b", "#f7b731", "#26de81",
    "#a55eea", "#fd9644", "#45aaf2", "#fc5c65",
    "#2bcbba", "#eb3b5a",
]
DEFAULTS = {
    "QLD":     {"qty": 0.0, "price": 0.0, "currency": "USD", "ratio": 30.0},
    "SCHD":    {"qty": 0.0, "price": 0.0, "currency": "USD", "ratio": 30.0},
    "Bitcoin": {"qty": 0.0, "price": 0.0, "currency": "USD", "ratio": 15.0},
}

# ─── Session state ─────────────────────────────────────────────────────────────
if "assets" not in st.session_state:
    st.session_state["assets"] = list(DEFAULTS.keys())

if "exchange_rate" not in st.session_state:
    st.session_state["exchange_rate"] = 1380.0

if "new_asset_name" not in st.session_state:
    st.session_state["new_asset_name"] = ""


def _init_asset(name: str, qty=0.0, price=0.0, currency="USD", ratio=0.0):
    """Initialize per-asset session_state keys (only if not already set)."""
    for key, val in [(f"qty_{name}", qty), (f"price_{name}", price),
                     (f"ratio_{name}", ratio)]:
        if key not in st.session_state:
            st.session_state[key] = val
    if f"cur_{name}" not in st.session_state:
        st.session_state[f"cur_{name}"] = currency


for asset, d in DEFAULTS.items():
    _init_asset(asset, **d)

# ─── Helpers ──────────────────────────────────────────────────────────────────
def get_krw(asset: str) -> float:
    qty  = float(st.session_state.get(f"qty_{asset}", 0.0))
    price = float(st.session_state.get(f"price_{asset}", 0.0))
    cur  = st.session_state.get(f"cur_{asset}", "USD")
    rate = float(st.session_state.get("exchange_rate", 1380.0))
    val  = qty * price
    return val * rate if cur == "USD" else val


def all_krw() -> dict[str, float]:
    return {a: get_krw(a) for a in st.session_state["assets"]}


def all_ratios() -> dict[str, float]:
    return {a: float(st.session_state.get(f"ratio_{a}", 0.0))
            for a in st.session_state["assets"]}


def icon_color(i: int) -> str:
    return ICON_COLORS[i % len(ICON_COLORS)]

# ─── Callbacks ────────────────────────────────────────────────────────────────
def add_asset():
    name = st.session_state["new_asset_name"].strip()
    if name and name not in st.session_state["assets"]:
        st.session_state["assets"].append(name)
        _init_asset(name, currency="KRW")
    st.session_state["new_asset_name"] = ""


def delete_asset(name: str):
    if name in st.session_state["assets"]:
        st.session_state["assets"].remove(name)

# ─── Algorithms ───────────────────────────────────────────────────────────────
def calculate_investment(holdings, target_ratios, budget):
    """Greedy deficit-fill: invest where the gap to target is largest first."""
    total = sum(holdings.values()) + budget
    result = {a: 0.0 for a in holdings}
    remaining = budget
    deficits = {a: (target_ratios.get(a, 0) / 100) * total - holdings.get(a, 0)
                for a in holdings}
    sorted_assets = sorted(deficits, key=lambda x: deficits[x], reverse=True)
    for a in sorted_assets:
        if remaining <= 0:
            break
        invest = min(max(deficits[a], 0.0), remaining)
        result[a] = invest
        remaining -= invest
    if remaining > 0:
        result[sorted_assets[0]] = result.get(sorted_assets[0], 0.0) + remaining
    return result


def calculate_rebalance(holdings, target_ratios):
    """Positive = sell, Negative = buy."""
    total = sum(holdings.values())
    if total == 0:
        return {a: 0.0 for a in holdings}
    return {a: holdings.get(a, 0) - (target_ratios.get(a, 0) / 100) * total
            for a in holdings}


def project_portfolio(initial: float, monthly: float,
                      annual_rate: float, years: int) -> list[float]:
    """Compound growth: monthly compounding with monthly additions."""
    r = annual_rate / 100 / 12
    values = [initial]
    cur = initial
    for _ in range(years):
        for _ in range(12):
            cur = cur * (1 + r) + monthly if r != 0 else cur + monthly
        values.append(cur)
    return values

# ─── Chart helpers ────────────────────────────────────────────────────────────
_DARK = dict(paper_bgcolor="#1e1e1e", plot_bgcolor="#1e1e1e",
             font=dict(color="#e0e0e0"))


def make_pie(labels, values, title):
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.38,
        textinfo="label+percent",
        hovertemplate="%{label}<br>%{value:,.0f}원<br>%{percent}<extra></extra>",
        marker=dict(colors=ICON_COLORS[:len(labels)]),
    ))
    fig.update_layout(title_text=title, title_x=0.5,
                      margin=dict(t=50, b=20, l=20, r=20),
                      height=370, showlegend=False, **_DARK)
    return fig

# ════════════════════════════════════════════════════════════════════════════
#  TABS
# ════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "💼 포트폴리오",
    "💰 월 투자 배분",
    "⚖️ 리밸런싱",
    "📈 미래 예측",
])

# ════════════════════════════════════════════════════════════════════════════
#  TAB 1 — 포트폴리오 (dark card view)
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    hdr_col, rate_col = st.columns([4, 1])
    with hdr_col:
        st.markdown(
            '<h1 style="color:#f0f0f0;font-size:26px;font-weight:700;margin:0">'
            '포트폴리오</h1>',
            unsafe_allow_html=True,
        )
    with rate_col:
        # key binds directly to session_state["exchange_rate"]
        st.number_input("💱 USD/KRW", min_value=100.0, max_value=5000.0,
                        step=1.0, format="%.0f", key="exchange_rate",
                        label_visibility="collapsed",
                        help="USD/KRW 환율 수동 입력")
        st.caption(f"환율: {st.session_state['exchange_rate']:,.0f}")

    holdings = all_krw()
    total = sum(holdings.values())

    st.markdown(f'<div class="total-num">{total:,.0f}원</div>', unsafe_allow_html=True)
    st.markdown('<div class="total-lbl">총 자산</div>', unsafe_allow_html=True)

    # ── Asset cards ──────────────────────────────────────────────────────
    assets = st.session_state["assets"]
    st.markdown('<div class="section-hd">내 포트폴리오</div>', unsafe_allow_html=True)

    html = '<div class="asset-card-wrap">'
    for i, asset in enumerate(assets):
        qty      = float(st.session_state.get(f"qty_{asset}", 0.0))
        price    = float(st.session_state.get(f"price_{asset}", 0.0))
        cur      = st.session_state.get(f"cur_{asset}", "USD")
        krw      = holdings.get(asset, 0.0)
        color    = icon_color(i)
        pct_str  = f"{krw / total * 100:.1f}%" if total > 0 else "0%"

        price_str = f"${price:,.2f}" if cur == "USD" else f"{price:,.0f}원"
        if "bitcoin" in asset.lower() or "btc" in asset.lower():
            qty_str = f"{qty:.6f} BTC"
        elif cur == "KRW":
            qty_str = f"직접입력"
        else:
            qty_str = f"{qty:,.4g}주"

        html += f"""
<div class="asset-row">
  <div class="asset-icon" style="background:{color}">{asset[0].upper()}</div>
  <div style="flex:1;min-width:0">
    <div class="asset-name">{asset}</div>
    <div class="asset-detail">{qty_str} · {price_str}</div>
  </div>
  <div>
    <div class="asset-krw">{krw:,.0f}원</div>
    <div style="font-size:12px;color:#777;text-align:right">{pct_str}</div>
  </div>
</div>"""
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

    # ── Edit expander ─────────────────────────────────────────────────────
    with st.expander("✏️ 수량 · 현재가 편집"):
        for asset in list(assets):
            c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 1.5, 0.7])
            with c1:
                st.markdown(f"**{asset}**")
            with c2:
                st.number_input("수량", min_value=0.0, step=0.0001,
                                format="%.4f", key=f"qty_{asset}",
                                label_visibility="collapsed")
                st.caption("수량")
            with c3:
                st.number_input("현재가", min_value=0.0, step=1.0,
                                format="%.2f", key=f"price_{asset}",
                                label_visibility="collapsed")
                st.caption("현재가")
            with c4:
                options = ["USD", "KRW"]
                # selectbox needs index; read current value from session_state
                cur_now = st.session_state.get(f"cur_{asset}", "USD")
                idx = options.index(cur_now) if cur_now in options else 0
                selected = st.selectbox("통화", options, index=idx,
                                        key=f"cur_{asset}",
                                        label_visibility="collapsed")
            with c5:
                st.write("")
                st.button("🗑️", key=f"del_{asset}",
                          on_click=delete_asset, args=(asset,))

        st.markdown("---")
        a1, a2 = st.columns([4, 1])
        with a1:
            st.text_input("새 자산 이름",
                          placeholder="예: 원화 현금, TQQQ, 달러 현금 ...",
                          key="new_asset_name")
        with a2:
            st.write("")
            st.button("＋ 추가", on_click=add_asset, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
#  TAB 2 — 월 투자 배분
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    st.header("💰 이번 달 투자금 배분")
    assets = st.session_state["assets"]

    # Target ratio inputs
    st.subheader("🎯 목표 비율 설정")
    ratio_cols = st.columns(min(len(assets), 4))
    for i, asset in enumerate(assets):
        with ratio_cols[i % len(ratio_cols)]:
            st.number_input(f"{asset} (%)", min_value=0.0, max_value=100.0,
                            step=1.0, key=f"ratio_{asset}")

    total_ratio = sum(float(st.session_state.get(f"ratio_{a}", 0)) for a in assets)
    if abs(total_ratio - 100.0) > 0.01:
        st.warning(f"⚠️ 목표 비율 합계: {total_ratio:.1f}% — 100%가 되어야 합니다.")
    else:
        st.success(f"✅ 목표 비율 합계: {total_ratio:.1f}%")

    holdings = all_krw()
    total    = sum(holdings.values())
    ratios   = all_ratios()

    if total > 0:
        pc1, pc2 = st.columns(2)
        with pc1:
            st.plotly_chart(
                make_pie(assets, [holdings.get(a, 0) for a in assets], "현재 비율"),
                use_container_width=True,
            )
        with pc2:
            st.plotly_chart(
                make_pie(assets, [ratios.get(a, 0) for a in assets], "목표 비율"),
                use_container_width=True,
            )

    st.markdown("---")
    st.subheader("📥 투자금 배분 계산")
    budget = st.number_input("이번 달 투자 금액 (원)", min_value=0.0,
                             step=100_000.0, format="%.0f",
                             key="monthly_budget")

    if budget > 0 and abs(total_ratio - 100.0) <= 0.01:
        alloc      = calculate_investment(holdings, ratios, budget)
        post       = {a: holdings.get(a, 0) + alloc.get(a, 0) for a in assets}
        post_total = sum(post.values())

        rows = [{
            "자산": a,
            "투자 금액 (원)":      alloc.get(a, 0),
            "투자 후 금액 (원)":   post[a],
            "투자 후 비율 (%)":    post[a] / post_total * 100 if post_total > 0 else 0,
            "목표 비율 (%)":       ratios.get(a, 0),
        } for a in assets]

        df = pd.DataFrame(rows)
        st.dataframe(
            df.style.format({
                "투자 금액 (원)":    "{:,.0f}",
                "투자 후 금액 (원)": "{:,.0f}",
                "투자 후 비율 (%)":  "{:.1f}",
                "목표 비율 (%)":     "{:.1f}",
            }).background_gradient(subset=["투자 금액 (원)"], cmap="Greens"),
            use_container_width=True, hide_index=True,
        )
        alloc_sum = sum(alloc.values())
        st.caption(f"배분 합계: **{alloc_sum:,.0f}원** (투자금 {budget:,.0f}원)")

        if post_total > 0:
            st.plotly_chart(
                make_pie(assets, [post.get(a, 0) for a in assets], "투자 후 예상 비율"),
                use_container_width=True,
            )
    elif budget > 0:
        st.warning("목표 비율 합계가 100%가 아닙니다. 위에서 비율을 조정해주세요.")
    else:
        st.info("투자 금액을 입력하면 자산별 배분 금액이 계산됩니다.")

# ════════════════════════════════════════════════════════════════════════════
#  TAB 3 — 리밸런싱
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    st.header("⚖️ 정기 리밸런싱 계산기")
    st.caption("현재 포트폴리오를 목표 비율로 맞추기 위한 매수/매도 금액을 계산합니다.")

    holdings = all_krw()
    ratios   = all_ratios()
    total    = sum(holdings.values())
    assets   = st.session_state["assets"]

    if total == 0:
        st.info("💼 포트폴리오 탭에서 수량과 현재가를 먼저 입력해주세요.")
    else:
        rebalance = calculate_rebalance(holdings, ratios)

        rows = [{
            "자산":           a,
            "현재 금액 (원)": holdings.get(a, 0),
            "현재 비율 (%)":  holdings.get(a, 0) / total * 100,
            "목표 비율 (%)":  ratios.get(a, 0),
            "목표 금액 (원)": (ratios.get(a, 0) / 100) * total,
            "매수/매도 (원)": rebalance.get(a, 0),
        } for a in assets]

        df_reb = pd.DataFrame(rows)

        def color_rebalance(val):
            if isinstance(val, (int, float)):
                if val > 500:   return "color: #e74c3c"   # 매도 → 빨강
                if val < -500:  return "color: #27ae60"   # 매수 → 녹색
            return ""

        st.dataframe(
            df_reb.style.format({
                "현재 금액 (원)": "{:,.0f}",
                "현재 비율 (%)":  "{:.1f}",
                "목표 비율 (%)":  "{:.1f}",
                "목표 금액 (원)": "{:,.0f}",
                "매수/매도 (원)": "{:+,.0f}",
            }).applymap(color_rebalance, subset=["매수/매도 (원)"]),
            use_container_width=True, hide_index=True,
        )

        buy_total  = sum(-v for v in rebalance.values() if v < 0)
        sell_total = sum( v for v in rebalance.values() if v > 0)
        m1, m2, m3 = st.columns(3)
        m1.metric("총 매수 필요", f"{buy_total:,.0f}원")
        m2.metric("총 매도 필요", f"{sell_total:,.0f}원")
        m3.metric("총 자산",      f"{total:,.0f}원")

        rc1, rc2 = st.columns(2)
        with rc1:
            st.plotly_chart(
                make_pie(assets, [holdings.get(a, 0) for a in assets], "현재 비율"),
                use_container_width=True,
            )
        with rc2:
            st.plotly_chart(
                make_pie(assets, [ratios.get(a, 0) for a in assets], "목표 비율"),
                use_container_width=True,
            )

# ════════════════════════════════════════════════════════════════════════════
#  TAB 4 — 미래 수익 예측
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    st.header("📈 미래 수익 예측")
    st.caption("현재 자산 기준으로 최대 10년 뒤 예상 자산을 시뮬레이션합니다.")

    holdings = all_krw()
    total    = sum(holdings.values())

    fc1, fc2 = st.columns(2)
    with fc1:
        st.metric("현재 총 자산", f"{total:,.0f}원")
    with fc2:
        monthly_add = st.number_input(
            "월 추가 투자금 (원)", min_value=0.0, step=100_000.0,
            format="%.0f", key="future_monthly",
        )

    st.markdown("---")
    st.subheader("📊 시나리오별 연간 수익률 설정")

    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        sc_name1 = st.text_input("시나리오 1 이름", value="보수적", key="sc_name1")
        sc_rate1 = st.number_input("연간 수익률 (%)", min_value=-50.0, max_value=200.0,
                                   value=7.0, step=0.5, key="sc_rate1",
                                   help="예) S&P500 역사적 평균 ~7%")
    with sc2:
        sc_name2 = st.text_input("시나리오 2 이름", value="기본",   key="sc_name2")
        sc_rate2 = st.number_input("연간 수익률 (%)", min_value=-50.0, max_value=200.0,
                                   value=15.0, step=0.5, key="sc_rate2",
                                   help="예) 나스닥 장기 평균 ~15%")
    with sc3:
        sc_name3 = st.text_input("시나리오 3 이름", value="낙관적", key="sc_name3")
        sc_rate3 = st.number_input("연간 수익률 (%)", min_value=-50.0, max_value=200.0,
                                   value=25.0, step=0.5, key="sc_rate3",
                                   help="예) QLD 레버리지 기대치 ~25%")

    years = st.slider("예측 기간 (년)", min_value=1, max_value=10, value=10,
                      key="forecast_years")

    v1 = project_portfolio(total, monthly_add, sc_rate1, years)
    v2 = project_portfolio(total, monthly_add, sc_rate2, years)
    v3 = project_portfolio(total, monthly_add, sc_rate3, years)

    year_labels = [f"{y}년" for y in range(years + 1)]

    fig = go.Figure()
    for name, values, color in [
        (sc_name1, v1, "#4e9af1"),
        (sc_name2, v2, "#26de81"),
        (sc_name3, v3, "#f7b731"),
    ]:
        fig.add_trace(go.Bar(
            name=name,
            x=year_labels,
            y=values,
            marker_color=color,
            hovertemplate=f"<b>{name}</b><br>%{{x}}: %{{y:,.0f}}원<extra></extra>",
        ))

    fig.update_layout(
        barmode="group",
        title="연도별 예상 자산 (원)",
        xaxis_title="기간",
        yaxis_title="자산 (원)",
        legend=dict(bgcolor="#2a2a2a", bordercolor="#444", borderwidth=1),
        height=500,
        hovermode="x unified",
        **_DARK,
    )
    fig.update_xaxes(gridcolor="#2a2a2a")
    fig.update_yaxes(gridcolor="#2a2a2a", tickformat=",d")
    st.plotly_chart(fig, use_container_width=True)

    # Summary table
    st.subheader("📋 연도별 요약")
    df_summary = pd.DataFrame([{
        "기간":               f"{y}년",
        f"{sc_name1} (원)":  v1[y],
        f"{sc_name2} (원)":  v2[y],
        f"{sc_name3} (원)":  v3[y],
    } for y in range(years + 1)])

    st.dataframe(
        df_summary.style.format({
            f"{sc_name1} (원)": "{:,.0f}",
            f"{sc_name2} (원)": "{:,.0f}",
            f"{sc_name3} (원)": "{:,.0f}",
        }),
        use_container_width=True, hide_index=True,
    )

    # Note on formula used
    st.caption(
        "계산 방식: 월 복리 적용 (연 수익률 ÷ 12) + 매월 추가 투자금. "
        "과거 수익률이 미래를 보장하지 않습니다."
    )
