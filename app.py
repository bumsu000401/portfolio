import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="포트폴리오",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS — iOS Light Mode ─────────────────────────────────────────────────────
st.markdown("""
<style>
/* ══════════════════════════════════════════════
   FONT — SF Pro (Apple system)
   ══════════════════════════════════════════════ */
* { font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display",
    "SF Pro Text", "Helvetica Neue", Arial, sans-serif !important; }

/* ══════════════════════════════════════════════
   BACKGROUNDS
   ══════════════════════════════════════════════ */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(160deg, #F0F2FF 0%, #F5F5F7 40%, #F5F0FF 100%);
    min-height: 100vh;
}
[data-testid="stHeader"] { background: transparent; }

.block-container { padding-top: 2rem !important; }

/* ══════════════════════════════════════════════
   SIDEBAR
   ══════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.75) !important;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-right: 1px solid rgba(0,0,0,0.07);
}

[data-testid="stSidebar"] .stRadio > div { gap: 3px; }
[data-testid="stSidebar"] .stRadio > div > label {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 13px 16px;
    border-radius: 12px;
    font-size: 15px;
    font-weight: 500;
    color: #3A3A3C;
    cursor: pointer;
    transition: background 0.15s, color 0.15s;
}
[data-testid="stSidebar"] .stRadio > div > label:hover {
    background: rgba(110,106,219,0.08);
}
[data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] {
    background: linear-gradient(135deg, rgba(110,106,219,0.15), rgba(90,200,250,0.10));
    color: #5856D6;
    font-weight: 700;
}
[data-testid="stSidebar"] .stRadio input[type="radio"] { accent-color: #5856D6; }

/* ── Fix: sidebar toggle button — do NOT override ── */
[data-testid="stSidebar"] button,
[data-testid="collapsedControl"] button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #3A3A3C !important;
    padding: 4px !important;
}

/* ══════════════════════════════════════════════
   CARDS (glass morphism)
   ══════════════════════════════════════════════ */
.glass-card {
    background: rgba(255,255,255,0.78);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.6);
    box-shadow: 0 4px 24px rgba(88,86,214,0.07),
                0 1px 4px rgba(0,0,0,0.05);
    padding: 24px;
    margin-bottom: 16px;
}

/* ══════════════════════════════════════════════
   EXPANDER
   ══════════════════════════════════════════════ */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.75);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255,255,255,0.6) !important;
    border-radius: 16px !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
[data-testid="stExpander"] summary {
    font-weight: 600;
    font-size: 15px;
    color: #1D1D1F;
    padding: 14px 18px;
}

/* ══════════════════════════════════════════════
   INPUTS
   ══════════════════════════════════════════════ */
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.9) !important;
    color: #1D1D1F !important;
    border: 1.5px solid #E5E5EA !important;
    border-radius: 12px !important;
    padding: 10px 14px !important;
    font-size: 15px !important;
    transition: border-color 0.15s, box-shadow 0.15s;
}
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextInput"] input:focus {
    border-color: #5856D6 !important;
    box-shadow: 0 0 0 3px rgba(88,86,214,0.15) !important;
    outline: none !important;
}

/* ══════════════════════════════════════════════
   METRIC TILES
   ══════════════════════════════════════════════ */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.78);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-radius: 16px;
    padding: 18px 20px;
    border: 1px solid rgba(255,255,255,0.7);
    box-shadow: 0 2px 12px rgba(88,86,214,0.08);
}
[data-testid="stMetricLabel"] {
    color: #86868B !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.6px;
}
[data-testid="stMetricValue"] {
    color: #1D1D1F !important;
    font-size: 24px !important;
    font-weight: 700 !important;
    letter-spacing: -0.5px;
}

/* ══════════════════════════════════════════════
   DATAFRAME
   ══════════════════════════════════════════════ */
[data-testid="stDataFrame"] {
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 2px 16px rgba(0,0,0,0.07);
    border: 1px solid rgba(255,255,255,0.5);
}

/* ══════════════════════════════════════════════
   SLIDER
   ══════════════════════════════════════════════ */
[data-testid="stSlider"] [role="slider"] { background: #5856D6 !important; }

/* ══════════════════════════════════════════════
   BUTTONS — only app-level buttons, NOT system UI
   ══════════════════════════════════════════════ */
[data-testid="stMain"] [data-testid="stButton"] > button {
    background: linear-gradient(135deg, #5856D6, #007AFF);
    color: #ffffff;
    border: none;
    border-radius: 12px;
    font-weight: 600;
    font-size: 15px;
    padding: 10px 22px;
    transition: opacity 0.15s, transform 0.1s;
    box-shadow: 0 2px 8px rgba(88,86,214,0.3);
}
[data-testid="stMain"] [data-testid="stButton"] > button:hover {
    opacity: 0.88;
    transform: translateY(-1px);
}
[data-testid="stMain"] [data-testid="stButton"] > button:active {
    transform: translateY(0);
}

/* ══════════════════════════════════════════════
   ALERTS
   ══════════════════════════════════════════════ */
[data-testid="stAlert"] {
    border-radius: 14px;
    border: none;
    backdrop-filter: blur(8px);
}

/* ══════════════════════════════════════════════
   ASSET CARDS
   ══════════════════════════════════════════════ */
.asset-card-wrap {
    background: rgba(255,255,255,0.78);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-radius: 20px;
    padding: 0 20px;
    margin: 8px 0 20px 0;
    border: 1px solid rgba(255,255,255,0.6);
    box-shadow: 0 4px 24px rgba(88,86,214,0.07), 0 1px 4px rgba(0,0,0,0.04);
}
.asset-row {
    display: flex;
    align-items: center;
    padding: 15px 0;
    border-bottom: 1px solid rgba(0,0,0,0.05);
}
.asset-row:last-child { border-bottom: none; }

.asset-icon {
    width: 46px;
    height: 46px;
    border-radius: 13px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    font-weight: 800;
    color: white;
    flex-shrink: 0;
    margin-right: 15px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.18);
}
.asset-name   { font-size: 16px; font-weight: 600; color: #1D1D1F; }
.asset-detail { font-size: 13px; color: #86868B; margin-top: 2px; }
.asset-krw    { font-size: 16px; font-weight: 600; color: #1D1D1F; text-align: right; }
.asset-pct    { font-size: 12px; color: #86868B; text-align: right; margin-top: 2px; }

/* ══════════════════════════════════════════════
   HERO — 총 자산
   ══════════════════════════════════════════════ */
.total-num {
    font-size: 42px;
    font-weight: 800;
    background: linear-gradient(135deg, #5856D6 0%, #007AFF 60%, #5AC8FA 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -2px;
    margin: 10px 0 4px;
    line-height: 1.1;
}
.total-lbl  { font-size: 13px; color: #86868B; margin-bottom: 22px; font-weight: 500; }
.section-hd { font-size: 19px; font-weight: 700; color: #1D1D1F;
              margin: 24px 0 12px; letter-spacing: -0.3px; }
</style>
""", unsafe_allow_html=True)

# ─── Constants ────────────────────────────────────────────────────────────────
ICON_COLORS = [
    "#007AFF", "#FF3B30", "#FF9500", "#34C759",
    "#AF52DE", "#FF2D55", "#5AC8FA", "#FFCC00",
    "#00C7BE", "#30B0C7",
]
DEFAULTS = {
    "QLD":     {"qty": 0.0, "price": 0.0, "ratio": 30.0, "priority": 1},
    "Bitcoin": {"qty": 0.0, "price": 0.0, "ratio": 15.0, "priority": 2},
    "SCHD":    {"qty": 0.0, "price": 0.0, "ratio": 30.0, "priority": 3},
    "원화":    {"qty": 0.0, "price": 0.0, "ratio": 15.0, "priority": 4, "asset_type": "현금"},
    "달러":    {"qty": 0.0, "price": 0.0, "ratio": 10.0, "priority": 4, "asset_type": "현금"},
}

# ─── Session state ─────────────────────────────────────────────────────────────
if "assets" not in st.session_state:
    st.session_state["assets"] = list(DEFAULTS.keys())


if "new_asset_name" not in st.session_state:
    st.session_state["new_asset_name"] = ""


def _init_asset(name: str, qty=0.0, price=0.0, ratio=0.0, asset_type="투자", priority=99):
    """Initialize per-asset session_state keys (only if not already set)."""
    for key, val in [(f"qty_{name}", qty), (f"price_{name}", price),
                     (f"ratio_{name}", ratio), (f"priority_{name}", priority)]:
        if key not in st.session_state:
            st.session_state[key] = val
    if f"type_{name}" not in st.session_state:
        st.session_state[f"type_{name}"] = asset_type


for asset, d in DEFAULTS.items():
    _init_asset(asset, qty=d.get("qty", 0.0), price=d.get("price", 0.0),
                ratio=d.get("ratio", 0.0), priority=d.get("priority", 99),
                asset_type=d.get("asset_type", "투자"))

# ─── Helpers ──────────────────────────────────────────────────────────────────
def get_krw(asset: str) -> float:
    return float(st.session_state.get(f"price_{asset}", 0.0))


def get_unit_price(asset: str) -> float | None:
    """평가금 ÷ 수량 = 주당 단가. 수량이 0이면 None."""
    qty = float(st.session_state.get(f"qty_{asset}", 0.0))
    krw = get_krw(asset)
    return krw / qty if qty > 0 else None


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
        _init_asset(name, asset_type="투자")
    st.session_state["new_asset_name"] = ""


def delete_asset(name: str):
    if name in st.session_state["assets"]:
        st.session_state["assets"].remove(name)

# ─── Algorithms ───────────────────────────────────────────────────────────────
def calculate_investment(holdings, target_ratios, budget, priority_order=None):
    """Greedy deficit-fill in priority order (lowest number = first)."""
    total = sum(holdings.values()) + budget
    result = {a: 0.0 for a in holdings}
    remaining = budget
    deficits = {a: (target_ratios.get(a, 0) / 100) * total - holdings.get(a, 0)
                for a in holdings}
    if priority_order:
        sorted_assets = priority_order
    else:
        sorted_assets = sorted(deficits, key=lambda x: deficits[x], reverse=True)
    for a in sorted_assets:
        if remaining <= 0:
            break
        invest = min(max(deficits.get(a, 0.0), 0.0), remaining)
        result[a] = invest
        remaining -= invest
    if remaining > 0:
        result[sorted_assets[0]] = result.get(sorted_assets[0], 0.0) + remaining
    return result


def calculate_rebalance(holdings, target_ratios):
    """Positive = buy, Negative = sell."""
    total = sum(holdings.values())
    if total == 0:
        return {a: 0.0 for a in holdings}
    return {a: (target_ratios.get(a, 0) / 100) * total - holdings.get(a, 0)
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
_DARK = dict(paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
             font=dict(color="#000000", family="-apple-system, BlinkMacSystemFont, Helvetica Neue, Arial"))


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
#  SIDEBAR NAVIGATION
# ════════════════════════════════════════════════════════════════════════════
PAGES = ["💼 포트폴리오", "💰 월 투자 배분", "⚖️ 리밸런싱", "📈 미래 예측"]

with st.sidebar:
    st.markdown(
        "<div style='padding:16px 4px 4px;font-size:22px;font-weight:800;"
        "background:linear-gradient(135deg,#5856D6,#007AFF);-webkit-background-clip:text;"
        "-webkit-text-fill-color:transparent;background-clip:text;letter-spacing:-0.5px'>"
        "📈 포트폴리오</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='font-size:12px;color:#86868B;padding:2px 4px 14px;margin:0;"
        "font-weight:500'>내 투자 현황</p>"
        "<hr style='border:none;border-top:1px solid rgba(0,0,0,0.07);margin:0 0 14px'>",
        unsafe_allow_html=True,
    )
    page = st.radio("페이지", PAGES, label_visibility="collapsed")

# ════════════════════════════════════════════════════════════════════════════
#  PAGE 1 — 포트폴리오
# ════════════════════════════════════════════════════════════════════════════
if page == PAGES[0]:
    st.markdown(
        '<h1 style="color:#1a1a1a;font-size:26px;font-weight:700;margin:0">'
        '포트폴리오</h1>',
        unsafe_allow_html=True,
    )

    holdings = all_krw()
    total = sum(holdings.values())

    st.markdown(f'<div class="total-num">{total:,.0f}원</div>', unsafe_allow_html=True)
    st.markdown('<div class="total-lbl">총 자산</div>', unsafe_allow_html=True)

    # ── Asset cards ──────────────────────────────────────────────────────
    assets = st.session_state["assets"]
    st.markdown('<div class="section-hd">내 포트폴리오</div>', unsafe_allow_html=True)

    html = '<div class="asset-card-wrap">'
    for i, asset in enumerate(assets):
        krw     = holdings.get(asset, 0.0)
        color   = icon_color(i)
        pct_str = f"{krw / total * 100:.1f}%" if total > 0 else "0%"
        atype   = st.session_state.get(f"type_{asset}", "투자")

        if atype == "현금":
            detail_str = f"{krw:,.0f}원"
        else:
            qty = float(st.session_state.get(f"qty_{asset}", 0.0))
            if "bitcoin" in asset.lower() or "btc" in asset.lower():
                qty_str = f"{qty:.6f} BTC"
            else:
                qty_str = f"{qty:,.4g}주"
            detail_str = f"{qty_str} · {krw:,.0f}원"

        html += f"""
<div class="asset-row">
  <div class="asset-icon" style="background:{color}">{asset[0].upper()}</div>
  <div style="flex:1;min-width:0">
    <div class="asset-name">{asset}</div>
    <div class="asset-detail">{detail_str}</div>
  </div>
  <div>
    <div class="asset-krw">{krw:,.0f}원</div>
    <div class="asset-pct">{pct_str}</div>
  </div>
</div>"""
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

    # ── Edit expander ─────────────────────────────────────────────────────
    with st.expander("✏️ 자산 편집"):
        for asset in list(assets):
            atype = st.session_state.get(f"type_{asset}", "투자")
            tc1, tc2 = st.columns([3, 2])
            with tc1:
                st.markdown(f"**{asset}**")
            with tc2:
                st.radio("유형", ["투자", "현금"], horizontal=True,
                         key=f"type_{asset}",
                         index=0 if atype == "투자" else 1,
                         label_visibility="collapsed")
            atype = st.session_state.get(f"type_{asset}", "투자")  # re-read after radio

            if atype == "현금":
                cc1, cc2 = st.columns([4, 0.7], vertical_alignment="bottom")
                with cc1:
                    st.number_input("금액 (원)", min_value=0.0, step=1000.0,
                                    format="%.0f", key=f"price_{asset}")
                with cc2:
                    st.button("🗑️", key=f"del_{asset}",
                              on_click=delete_asset, args=(asset,))
            else:
                unit = get_unit_price(asset)
                lc1, lc2, _ = st.columns([2, 3, 0.7])
                lc1.caption("수량")
                lc2.caption(f"평가금 (원)  |  단가 ≈ {unit:,.0f}원" if unit else "평가금 (원)")

                ic1, ic2, ic3 = st.columns([2, 3, 0.7], vertical_alignment="center")
                with ic1:
                    st.number_input("수량", min_value=0.0, step=0.0001,
                                    format="%.4f", key=f"qty_{asset}",
                                    label_visibility="collapsed")
                with ic2:
                    st.number_input("평가금 (원)", min_value=0.0, step=10000.0,
                                    format="%.0f", key=f"price_{asset}",
                                    label_visibility="collapsed")
                with ic3:
                    st.button("🗑️", key=f"del_{asset}",
                              on_click=delete_asset, args=(asset,))
            st.divider()

        st.markdown("---")
        a1, a2 = st.columns([4, 1], vertical_alignment="bottom")
        with a1:
            st.text_input("새 자산 이름",
                          placeholder="예: 원화 현금, TQQQ, 달러 현금 ...",
                          key="new_asset_name")
        with a2:
            st.button("＋ 추가", on_click=add_asset, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
#  PAGE 2 — 월 투자 배분
# ════════════════════════════════════════════════════════════════════════════
elif page == PAGES[1]:
    st.header("💰 이번 달 투자금 배분")
    assets = st.session_state["assets"]

    # Target ratio + priority inputs
    st.subheader("🎯 목표 비율 & 투자 우선순위")
    st.caption("우선순위: 숫자가 낮을수록 먼저 채웁니다. 예산이 부족할 때 순서대로 배분됩니다.")
    hc1, hc2, hc3 = st.columns([3, 2, 1])
    hc1.markdown("**자산**")
    hc2.markdown("**목표 비율 (%)**")
    hc3.markdown("**우선순위**")
    for asset in assets:
        c1, c2, c3 = st.columns([3, 2, 1])
        c1.markdown(f"<div style='padding-top:8px'>{asset}</div>", unsafe_allow_html=True)
        with c2:
            st.number_input("비율", min_value=0.0, max_value=100.0,
                            step=1.0, key=f"ratio_{asset}",
                            label_visibility="collapsed")
        with c3:
            st.number_input("순위", min_value=1, max_value=99,
                            step=1, key=f"priority_{asset}",
                            label_visibility="collapsed")

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
                key="pie_tab1_current",
            )
        with pc2:
            st.plotly_chart(
                make_pie(assets, [ratios.get(a, 0) for a in assets], "목표 비율"),
                use_container_width=True,
                key="pie_tab1_target",
            )

    st.markdown("---")
    st.subheader("📥 투자금 배분 계산")
    budget = st.number_input("이번 달 투자 금액 (원)", min_value=0.0,
                             step=100_000.0, format="%.0f",
                             key="monthly_budget")

    if budget > 0 and abs(total_ratio - 100.0) <= 0.01:
        priority_order = sorted(assets, key=lambda a: st.session_state.get(f"priority_{a}", 99))
        alloc      = calculate_investment(holdings, ratios, budget, priority_order)
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
                key="pie_tab1_after",
            )
    elif budget > 0:
        st.warning("목표 비율 합계가 100%가 아닙니다. 위에서 비율을 조정해주세요.")
    else:
        st.info("투자 금액을 입력하면 자산별 배분 금액이 계산됩니다.")

# ════════════════════════════════════════════════════════════════════════════
#  PAGE 3 — 리밸런싱
# ════════════════════════════════════════════════════════════════════════════
elif page == PAGES[2]:
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

        def _shares_str(asset, amount_krw):
            """매수/매도 주 수. 투자형이고 수량>0일 때만 표시."""
            atype = st.session_state.get(f"type_{asset}", "투자")
            if atype != "투자":
                return "-"
            unit = get_unit_price(asset)
            if unit is None or unit == 0:
                return "-"
            shares = abs(amount_krw) / unit
            sign = "+" if amount_krw > 0 else "-"
            return f"{sign}{shares:.2f}주"

        rows = [{
            "자산":            a,
            "현재 금액 (원)":  holdings.get(a, 0),
            "현재 비율 (%)":   holdings.get(a, 0) / total * 100,
            "목표 비율 (%)":   ratios.get(a, 0),
            "목표 금액 (원)":  (ratios.get(a, 0) / 100) * total,
            "매수/매도 (원)":  rebalance.get(a, 0),
            "매수/매도 (주)":  _shares_str(a, rebalance.get(a, 0)),
        } for a in assets]

        df_reb = pd.DataFrame(rows)

        def color_rebalance(val):
            if isinstance(val, (int, float)):
                if val > 500:   return "color: #27ae60"   # 매수 → 녹색
                if val < -500:  return "color: #e74c3c"   # 매도 → 빨강
            return ""

        def color_shares(val):
            if isinstance(val, str):
                if val.startswith("+"):  return "color: #e74c3c"
                if val.startswith("-") and val != "-":  return "color: #27ae60"
            return ""

        st.dataframe(
            df_reb.style.format({
                "현재 금액 (원)":  "{:,.0f}",
                "현재 비율 (%)":   "{:.1f}",
                "목표 비율 (%)":   "{:.1f}",
                "목표 금액 (원)":  "{:,.0f}",
                "매수/매도 (원)":  "{:+,.0f}",
            }).applymap(color_rebalance, subset=["매수/매도 (원)"])
              .applymap(color_shares,    subset=["매수/매도 (주)"]),
            use_container_width=True, hide_index=True,
        )

        buy_total  = sum( v for v in rebalance.values() if v > 0)
        sell_total = sum(-v for v in rebalance.values() if v < 0)
        m1, m2, m3 = st.columns(3)
        m1.metric("총 매수 필요", f"{buy_total:,.0f}원")
        m2.metric("총 매도 필요", f"{sell_total:,.0f}원")
        m3.metric("총 자산",      f"{total:,.0f}원")

        rc1, rc2 = st.columns(2)
        with rc1:
            st.plotly_chart(
                make_pie(assets, [holdings.get(a, 0) for a in assets], "현재 비율"),
                use_container_width=True,
                key="pie_tab3_current",
            )
        with rc2:
            st.plotly_chart(
                make_pie(assets, [ratios.get(a, 0) for a in assets], "목표 비율"),
                use_container_width=True,
                key="pie_tab3_target",
            )

# ════════════════════════════════════════════════════════════════════════════
#  PAGE 4 — 미래 수익 예측
# ════════════════════════════════════════════════════════════════════════════
elif page == PAGES[3]:
    st.header("📈 미래 수익 예측")
    st.caption("현재 자산 기준으로 최대 10년 뒤 예상 자산을 시뮬레이션합니다.")

    holdings = all_krw()
    total    = sum(holdings.values())

    fc1, fc2 = st.columns(2)
    with fc1:
        st.metric("현재 총 자산", f"{total:,.0f}원")
    with fc2:
        monthly_add = st.number_input(
            "월 추가 투자금 (만원)", min_value=0.0, step=1.0,
            format="%.0f", key="future_monthly",
        ) * 10_000

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
        legend=dict(bgcolor="#f5f5f5", bordercolor="#ddd", borderwidth=1),
        height=500,
        hovermode="x unified",
        **_DARK,
    )
    fig.update_xaxes(gridcolor="#e8e8e8")
    fig.update_yaxes(gridcolor="#e8e8e8", tickformat=",d")
    st.plotly_chart(fig, use_container_width=True, key="chart_tab4_forecast")

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
