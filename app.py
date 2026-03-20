import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import random

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="포트폴리오",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS — Figma Financial Dashboard (Community) ─────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

/* ── Global ── */
html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; }
[data-testid="stAppViewContainer"] { background: #f2f2f7; }
[data-testid="stHeader"]           { background: transparent !important; }
.block-container { padding-top: 2rem !important; max-width: 1100px; }

/* ── Sidebar ── */
[data-testid="stSidebar"] { background: #ffffff !important; border-right: 1px solid #e5e5ea; }

[data-testid="stSidebar"] .stRadio > div { gap: 2px; }
[data-testid="stSidebar"] .stRadio > div > label {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 10px;
    border-radius: 7px;
    font-size: 13px;
    font-weight: 500;
    color: #8e8e93;
    cursor: pointer;
    transition: background 0.1s ease, color 0.1s ease;
}
[data-testid="stSidebar"] .stRadio > div > label > div:first-child { display: none !important; }
[data-testid="stSidebar"] .stRadio > div > label:hover {
    background: #f2f2f7;
    color: #2c2c2e;
}
[data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] {
    background: #3a3a3c !important;
    color: #ffffff !important;
    font-weight: 500;
}
[data-testid="stSidebar"] h3 { color: #2c2c2e !important; font-size: 14px !important; font-weight: 600 !important; }
[data-testid="stSidebar"] hr { border-color: #e5e5ea !important; margin: 12px 0; }

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: #ffffff;
    border-radius: 12px;
    padding: 18px 20px;
    border: 1px solid #e5e5ea;
}
[data-testid="stMetricLabel"] { color: #8e8e93 !important; font-size: 10px !important; font-weight: 500 !important; letter-spacing: 1px !important; text-transform: uppercase !important; }
[data-testid="stMetricValue"] { color: #2c2c2e !important; font-size: 22px !important; font-weight: 600 !important; font-family: 'IBM Plex Mono', monospace !important; }

/* ── Inputs ── */
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input {
    background: #ffffff;
    border: 1px solid #e5e5ea;
    border-radius: 8px;
    color: #2c2c2e;
    font-size: 14px;
    font-family: 'Outfit', sans-serif;
}

[data-testid="stNumberInput"] input:focus,
[data-testid="stTextInput"] input:focus {
    outline: none;
    border-color: #3a3a3c;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #ffffff;
    border: 1px solid #e5e5ea !important;
    border-radius: 12px;
}

/* ── DataFrame ── */
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; border: 1px solid #e5e5ea; }

/* ── Asset card styles ── */
.asset-card-wrap {
    background: #ffffff;
    border-radius: 12px;
    padding: 0 20px;
    margin: 8px 0 20px 0;
    border: 1px solid #e5e5ea;
}
.asset-row {
    display: flex;
    align-items: center;
    padding: 14px 0;
    border-bottom: 1px solid #f5f5f7;
}
.asset-row:last-child { border-bottom: none; }
.asset-icon {
    width: 36px;
    height: 36px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    font-weight: 700;
    color: white;
    flex-shrink: 0;
    margin-right: 14px;
}
.asset-name   { font-size: 13px; font-weight: 600; color: #2c2c2e; }
.asset-detail { font-size: 11px; color: #8e8e93; margin-top: 2px; font-family: 'IBM Plex Mono', monospace; }
.asset-krw    { font-size: 13px; font-weight: 500; color: #2c2c2e; text-align: right; font-family: 'IBM Plex Mono', monospace; }
.asset-pct    { font-size: 11px; color: #8e8e93; text-align: right; margin-top: 2px; }

.total-num  { font-size: 40px; font-weight: 500; color: #2c2c2e; letter-spacing: -1px; margin: 6px 0 2px; font-family: 'IBM Plex Mono', monospace; }
.total-lbl  { font-size: 11px; color: #8e8e93; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 500; }
.section-hd { font-size: 11px; font-weight: 600; color: #8e8e93; margin: 20px 0 10px; text-transform: uppercase; letter-spacing: 1.5px; padding-bottom: 8px; border-bottom: 1px solid #e5e5ea; }
.quote-subtitle { font-size: 12px !important; color: #8e8e93 !important; font-style: italic !important; margin: 0 0 20px !important; }
</style>
""", unsafe_allow_html=True)

# ─── Constants ────────────────────────────────────────────────────────────────
ICON_COLORS = [
    "#3a3a3c",  # primary dark
    "#636366",
    "#8e8e93",
    "#aeaeb2",
    "#c7c7cc",
    "#d1d1d6",
    "#e5e5ea",
    "#3a3a3c",
    "#636366",
    "#8e8e93",
]

CHART_COLORS = [
    "#197BBD", "#F4A322", "#27AE60", "#E74C3C",
    "#8E44AD", "#2EACDE", "#F39C12", "#16A085",
    "#D35400", "#2980B9",
]
DEFAULTS = {
    "QLD":     {"qty": 0.0, "price": 0.0, "ratio": 30.0, "priority": 1},
    "Bitcoin": {"qty": 0.0, "price": 0.0, "ratio": 15.0, "priority": 2},
    "SCHD":    {"qty": 0.0, "price": 0.0, "ratio": 30.0, "priority": 3},
    "원화":    {"qty": 0.0, "price": 0.0, "ratio": 15.0, "priority": 4, "asset_type": "현금"},
    "달러":    {"qty": 0.0, "price": 0.0, "ratio": 10.0, "priority": 4, "asset_type": "현금"},
}

# ─── 투자 대가 명언 ──────────────────────────────────────────────────────────────
QUOTES = [
    ("주식 시장은 인내심이 없는 자로부터 인내심이 많은 자에게로 돈이 넘어가도록 설계되어 있다", "워렌 버핏"),
    ("기업을 공부하지 않고 투자하는 것은 포커를 칠 때 카드를 보지 않고 배팅하는 것과 같다", "피터 린치"),
    ("강세장에서 최대의 도박으로 최대 이익을 얻은 자는 필연적으로 뒤따르는 약세장에서 가장 큰 손실을 본다", "벤자민 그레이엄"),
    ("첫 번째 규칙은 절대로 잃지 마라. 두 번째 규칙은 첫 번째를 절대로 따라라", "워렌 버핏"),
    ("우량주 몇 종목을 산 다음 수면제를 먹고 몇 년 동안 푹 자라", "앙드레 코스톨라니"),
    ("10년 이상 보유할 종목이 아니면 10분도 보유하지 마라", "워렌 버핏"),
    ("당신이 잠자는 동안에도 돈이 들어오는 방법을 찾지 못한다면 평생 일해야 한다", "워렌 버핏"),
    ("장기적 투자 성공을 위해 단기적 부진을 견뎌내야 한다", "찰리 멍거"),
    ("가치에 대한 확고한 신념이 있어야만 수익 없는 기간을 버틸 수 있다", "하워드 막스"),
    ("개는 주인을 떠날 수 없다. 개는 주가, 주인은 기업가치다", "앙드레 코스톨라니"),
    ("투자는 IQ나 기법의 문제가 아닌 원칙과 태도의 문제다", "벤자민 그레이엄"),
    ("최적의 매수 타이밍은 시장에 피가 낭자할 때다", "존 템플턴"),
    ("투자 성공은 세상의 비관론을 무시할 수 있는지에 달렸다", "피터 린치"),
    ("모두가 탐욕스러울 때 두려워하고 두려워할 때 탐욕스러워라", "워렌 버핏"),
    ("잘 사기만 한다면 절반은 판 것과 같다", "하워드 막스"),
    ("투자자에게 가장 중요한 것은 지성이 아닌 기질이다", "워렌 버핏"),
    ("현명한 투자자는 비관주의자에게 사서 낙관주의자에게 판다", "벤자민 그레이엄"),
    ("하락장에서 돈을 가장 많이 벌 수 있으나 깨닫지 못할 뿐이다", "셀비 M.C. 데이비스"),
    ("싼 것을 꾸준히 사기 위해서는 다른 투자자들이 찾지 않을 것에서 최고의 대상을 발견하라", "하워드 막스"),
    ("이자율이 낮으면 주식시장에 점프하라", "앙드레 코스톨라니"),
    ("약세장은 일시적이다. 바닥 후 1~12개월 내 상승한다", "존 템플턴"),
    ("영리한 투자자는 약세장에서 매수해서 강세장에서 매도한다", "벤자민 그레이엄"),
    ("시장 타이밍을 맞추려는 것은 불안과 초조의 늪으로 빠지는 지름길이다", "랄프 웬저"),
    ("투자자는 자신만의 생각과 방향을 가져야 하며 감정적 행동을 하지 말아야 한다", "앙드레 코스톨라니"),
    ("가치에 초점을 맞출 때 더 많은 수익이 얻어진다", "존 템플턴"),
    ("조바심을 절제해야 한다", "워렌 버핏"),
    ("돈은 확률을 모르는 도박꾼에게서 확률을 아는 사람에게로 들어간다", "랄프 웬저"),
    ("주식이 바보보다 많으면 사고, 바보가 많으면 팔아야 한다", "앙드레 코스톨라니"),
    ("20% 손실을 예상하지 못한다면 투자하지 말아야 한다", "존 보글"),
    ("인기 주식에는 프리미엄이, 따분한 주식에는 할인이 있다. 할인된 주식을 사라", "랄프 웬저"),
]

# ─── Session state ─────────────────────────────────────────────────────────────
if "assets" not in st.session_state:
    st.session_state["assets"] = list(DEFAULTS.keys())


if "new_asset_name" not in st.session_state:
    st.session_state["new_asset_name"] = ""

if "daily_quote" not in st.session_state:
    st.session_state["daily_quote"] = random.choice(QUOTES)


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


# 위젯 key(_w_*)가 페이지 이동 시 삭제되므로 스토리지 key에 값을 별도 보존
def _save_price(asset):    st.session_state[f"price_{asset}"]    = st.session_state.get(f"_w_price_{asset}", 0.0)
def _save_qty(asset):      st.session_state[f"qty_{asset}"]      = st.session_state.get(f"_w_qty_{asset}", 0.0)
def _save_type(asset):     st.session_state[f"type_{asset}"]     = st.session_state.get(f"_w_type_{asset}", "투자")
def _save_ratio(asset):    st.session_state[f"ratio_{asset}"]    = st.session_state.get(f"_w_ratio_{asset}", 0.0)
def _save_priority(asset): st.session_state[f"priority_{asset}"] = st.session_state.get(f"_w_priority_{asset}", 99)

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
_DARK = dict(
    paper_bgcolor="#ffffff",
    plot_bgcolor="#ffffff",
    font=dict(color="#2c2c2e", family="Outfit, sans-serif"),
)


def make_pie(labels, values, title):
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.44,
        textinfo="label+percent",
        textfont=dict(size=12),
        hovertemplate="%{label}<br>%{value:,.0f}원<br>%{percent}<extra></extra>",
        marker=dict(
            colors=CHART_COLORS[:len(labels)],
            line=dict(color="#ffffff", width=2),
        ),
        rotation=90,
    ))
    fig.update_layout(
        title_text=title, title_x=0.5,
        title_font=dict(size=14, color="#2c2c2e"),
        margin=dict(t=50, b=20, l=20, r=20),
        height=370, showlegend=False,
        transition=dict(duration=500, easing="cubic-in-out"),
        **_DARK,
    )
    return fig

# ════════════════════════════════════════════════════════════════════════════
#  SIDEBAR NAVIGATION
# ════════════════════════════════════════════════════════════════════════════
PAGES = ["💼 포트폴리오", "💰 월 투자 배분", "⚖️ 리밸런싱", "📈 미래 예측"]

with st.sidebar:
    st.markdown(
        '<div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">'
        '<div style="width:28px;height:28px;border-radius:7px;background:#3a3a3c;'
        'display:flex;align-items:center;justify-content:center;'
        'font-size:14px;color:white">📈</div>'
        '<span style="font-size:14px;font-weight:600;color:#2c2c2e;letter-spacing:-0.3px">Portfolio</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")
    page = st.radio("페이지", PAGES, label_visibility="collapsed")

# ════════════════════════════════════════════════════════════════════════════
#  PAGE 1 — 포트폴리오
# ════════════════════════════════════════════════════════════════════════════
if page == PAGES[0]:
    _q, _a = st.session_state["daily_quote"]
    st.markdown(
        '<h1 style="color:#2c2c2e;font-size:24px;font-weight:700;margin:0 0 4px;letter-spacing:-0.8px">포트폴리오</h1>'
        f'<div class="quote-subtitle">&ldquo;{_q}&rdquo; — {_a}</div>',
        unsafe_allow_html=True,
    )

    holdings = all_krw()
    total = sum(holdings.values())

    st.markdown('<div class="total-lbl">총 자산</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="total-num">{total:,.0f}원</div>', unsafe_allow_html=True)

    # ── Asset cards ──────────────────────────────────────────────────────
    assets = st.session_state["assets"]
    st.markdown('<div class="section-hd">내 포트폴리오</div>', unsafe_allow_html=True)

    html = '<div class="asset-card-wrap">'
    for i, asset in enumerate(assets):
        krw     = holdings.get(asset, 0.0)
        color   = icon_color(i)
        pct     = krw / total * 100 if total > 0 else 0
        pct_str = f"{pct:.1f}%"
        bar_w   = min(pct, 100)
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
  <div style="width:60px;margin:0 14px">
    <div style="width:60px;height:3px;background:#e5e5ea;border-radius:99px;overflow:hidden">
      <div style="width:{bar_w:.1f}%;height:100%;background:#3a3a3c;border-radius:99px"></div>
    </div>
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
                         key=f"_w_type_{asset}",
                         index=0 if atype == "투자" else 1,
                         on_change=_save_type, args=(asset,),
                         label_visibility="collapsed")
            atype = st.session_state.get(f"type_{asset}", "투자")  # 스토리지 key에서 재읽기

            if atype == "현금":
                cc1, cc2 = st.columns([4, 0.7], vertical_alignment="bottom")
                with cc1:
                    st.number_input("금액 (원)", min_value=0.0, step=1000.0,
                                    format="%.0f",
                                    value=st.session_state.get(f"price_{asset}", 0.0),
                                    key=f"_w_price_{asset}",
                                    on_change=_save_price, args=(asset,))
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
                                    format="%.4f",
                                    value=st.session_state.get(f"qty_{asset}", 0.0),
                                    key=f"_w_qty_{asset}",
                                    on_change=_save_qty, args=(asset,),
                                    label_visibility="collapsed")
                with ic2:
                    st.number_input("평가금 (원)", min_value=0.0, step=10000.0,
                                    format="%.0f",
                                    value=st.session_state.get(f"price_{asset}", 0.0),
                                    key=f"_w_price_{asset}",
                                    on_change=_save_price, args=(asset,),
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
    st.markdown('<h1 style="color:#2c2c2e;font-size:24px;font-weight:700;margin:0 0 20px;letter-spacing:-0.8px">💰 이번 달 투자금 배분</h1>', unsafe_allow_html=True)
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
                            step=1.0,
                            value=st.session_state.get(f"ratio_{asset}", 0.0),
                            key=f"_w_ratio_{asset}",
                            on_change=_save_ratio, args=(asset,),
                            label_visibility="collapsed")
        with c3:
            st.number_input("순위", min_value=1, max_value=99,
                            step=1,
                            value=int(st.session_state.get(f"priority_{asset}", 99)),
                            key=f"_w_priority_{asset}",
                            on_change=_save_priority, args=(asset,),
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
    st.markdown('<h1 style="color:#2c2c2e;font-size:24px;font-weight:700;margin:0 0 4px;letter-spacing:-0.8px">⚖️ 정기 리밸런싱 계산기</h1>', unsafe_allow_html=True)
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
    st.markdown('<h1 style="color:#2c2c2e;font-size:24px;font-weight:700;margin:0 0 4px;letter-spacing:-0.8px">📈 미래 수익 예측</h1>', unsafe_allow_html=True)
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

    FORECAST_COLORS = [
        ("#197BBD", "rgba(25,123,189,0.08)"),
        ("#27AE60", "rgba(39,174,96,0.08)"),
        ("#F4A322", "rgba(244,163,34,0.08)"),
    ]

    fig = go.Figure()
    for (name, values), (line_color, fill_color) in zip(
        [(sc_name1, v1), (sc_name2, v2), (sc_name3, v3)], FORECAST_COLORS
    ):
        fig.add_trace(go.Scatter(
            name=name,
            x=year_labels,
            y=values,
            mode="lines+markers",
            line=dict(shape="spline", smoothing=1.3, width=2.5, color=line_color),
            marker=dict(size=7, color=line_color,
                        line=dict(color="#ffffff", width=2)),
            fill="tozeroy",
            fillcolor=fill_color,
            hovertemplate=f"<b>{name}</b><br>%{{x}}: %{{y:,.0f}}원<extra></extra>",
        ))

    fig.update_layout(
        title="연도별 예상 자산",
        title_font=dict(size=15, color="#2c2c2e"),
        xaxis_title="기간",
        yaxis_title="자산 (원)",
        legend=dict(
            bgcolor="#ffffff", bordercolor="#EBEBEB", borderwidth=1,
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
        ),
        height=480,
        hovermode="x unified",
        transition=dict(duration=600, easing="cubic-in-out"),
        **_DARK,
    )
    fig.update_xaxes(gridcolor="#F0F0F0", showline=False, zeroline=False)
    fig.update_yaxes(gridcolor="#F0F0F0", showline=False, zeroline=False, tickformat=",d")
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
