from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import streamlit as st

from core.data_provider import fetch_snapshot
from core.scoring import score_stock


DEFAULT_TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META",
    "NVDA", "AVGO", "JPM", "V", "MA",
    "COST", "WMT", "HD", "UNH", "LLY",
    "XOM", "CVX", "CAT", "GE", "ORCL",
]


@st.cache_data(ttl=3600, show_spinner=False)
def scan_tickers(tickers: tuple[str, ...]) -> pd.DataFrame:
    rows = []

    def worker(ticker):
        snap = fetch_snapshot(ticker)
        score = score_stock(snap)
        return {
            "Ticker": snap.ticker,
            "Company": snap.company,
            "Sector": snap.sector,
            "Price": snap.price,
            "Deal Score": score.deal_score,
            "Rating": score.rating,
            "Valuation": score.valuation,
            "Quality": score.quality,
            "Growth": score.growth,
            "Financial Health": score.financial_health,
            "Cash Flow": score.cash_flow,
            "Value Trap Risk": score.value_trap_risk,
            "Upside to Target %": score.upside_to_target,
        }

    with ThreadPoolExecutor(max_workers=min(8, max(1, len(tickers)))) as pool:
        futures = {pool.submit(worker, t): t for t in tickers}
        for future in as_completed(futures):
            ticker = futures[future]
            try:
                rows.append(future.result())
            except Exception as exc:
                rows.append({
                    "Ticker": ticker,
                    "Company": None,
                    "Sector": None,
                    "Price": None,
                    "Deal Score": None,
                    "Rating": f"Data error: {exc}",
                    "Valuation": None,
                    "Quality": None,
                    "Growth": None,
                    "Financial Health": None,
                    "Cash Flow": None,
                    "Value Trap Risk": None,
                    "Upside to Target %": None,
                })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("Deal Score", ascending=False, na_position="last").reset_index(drop=True)
    return df


def render_scanner():
    st.subheader("Good Deal Scanner")

    st.info(
        "v0.1 uses absolute scoring thresholds. The next major upgrade will normalize valuation "
        "and quality against each stock's sector, industry, and historical range."
    )

    raw = st.text_area(
        "Tickers",
        value=", ".join(DEFAULT_TICKERS),
        help="Comma-separated US stock symbols.",
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        min_score = st.slider("Minimum Deal Score", 0, 100, 0)
    with c2:
        max_trap = st.slider("Maximum Value Trap Risk", 0, 100, 100)
    with c3:
        top_n = st.number_input("Top results", min_value=5, max_value=100, value=25, step=5)

    tickers = tuple(dict.fromkeys(
        t.strip().upper() for t in raw.replace("\n", ",").split(",") if t.strip()
    ))

    if st.button("Run Scan", type="primary", use_container_width=True):
        if not tickers:
            st.warning("Enter at least one ticker.")
            return
        with st.spinner(f"Scoring {len(tickers)} stocks..."):
            df = scan_tickers(tickers)
        st.session_state["deal_scan_df"] = df

    df = st.session_state.get("deal_scan_df")
    if df is None:
        st.caption("Run the scanner to build the first ranking.")
        return

    filtered = df[
        (df["Deal Score"].fillna(-1) >= min_score)
        & (df["Value Trap Risk"].fillna(101) <= max_trap)
    ].head(int(top_n))

    if filtered.empty:
        st.warning("No stocks meet the current filters.")
        return

    leader = filtered.iloc[0]
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Top Stock", leader["Ticker"])
    m2.metric("Deal Score", f'{leader["Deal Score"]:.1f}')
    m3.metric("Quality", f'{leader["Quality"]:.1f}')
    m4.metric("Value Trap Risk", f'{leader["Value Trap Risk"]:.1f}')

    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Deal Score": st.column_config.ProgressColumn(
                "Deal Score", min_value=0, max_value=100, format="%.1f"
            ),
            "Value Trap Risk": st.column_config.ProgressColumn(
                "Value Trap Risk", min_value=0, max_value=100, format="%.1f"
            ),
            "Price": st.column_config.NumberColumn("Price", format="$%.2f"),
            "Upside to Target %": st.column_config.NumberColumn("Upside to Target %", format="%.1f%%"),
        },
    )

    st.download_button(
        "Download scan CSV",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="hedge_fund_deal_scan.csv",
        mime="text/csv",
    )
