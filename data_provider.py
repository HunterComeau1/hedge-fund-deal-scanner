from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

import numpy as np
import yfinance as yf


@dataclass
class StockSnapshot:
    ticker: str
    company: str | None
    sector: str | None
    industry: str | None
    price: float | None
    market_cap: float | None

    trailing_pe: float | None
    forward_pe: float | None
    price_to_book: float | None
    enterprise_to_ebitda: float | None
    enterprise_to_revenue: float | None

    return_on_equity: float | None
    return_on_assets: float | None
    gross_margin: float | None
    operating_margin: float | None
    profit_margin: float | None

    revenue_growth: float | None
    earnings_growth: float | None

    total_cash: float | None
    total_debt: float | None
    debt_to_equity: float | None
    current_ratio: float | None

    operating_cash_flow: float | None
    free_cash_flow: float | None
    total_revenue: float | None

    held_percent_insiders: float | None
    held_percent_institutions: float | None

    fifty_two_week_change: float | None
    target_mean_price: float | None
    recommendation_mean: float | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _num(value):
    try:
        if value is None:
            return None
        value = float(value)
        return value if np.isfinite(value) else None
    except (TypeError, ValueError):
        return None


def fetch_snapshot(ticker: str) -> StockSnapshot:
    t = yf.Ticker(ticker)
    info = t.info or {}

    return StockSnapshot(
        ticker=ticker.upper(),
        company=info.get("shortName") or info.get("longName"),
        sector=info.get("sector"),
        industry=info.get("industry"),
        price=_num(info.get("currentPrice") or info.get("regularMarketPrice")),
        market_cap=_num(info.get("marketCap")),
        trailing_pe=_num(info.get("trailingPE")),
        forward_pe=_num(info.get("forwardPE")),
        price_to_book=_num(info.get("priceToBook")),
        enterprise_to_ebitda=_num(info.get("enterpriseToEbitda")),
        enterprise_to_revenue=_num(info.get("enterpriseToRevenue")),
        return_on_equity=_num(info.get("returnOnEquity")),
        return_on_assets=_num(info.get("returnOnAssets")),
        gross_margin=_num(info.get("grossMargins")),
        operating_margin=_num(info.get("operatingMargins")),
        profit_margin=_num(info.get("profitMargins")),
        revenue_growth=_num(info.get("revenueGrowth")),
        earnings_growth=_num(info.get("earningsGrowth")),
        total_cash=_num(info.get("totalCash")),
        total_debt=_num(info.get("totalDebt")),
        debt_to_equity=_num(info.get("debtToEquity")),
        current_ratio=_num(info.get("currentRatio")),
        operating_cash_flow=_num(info.get("operatingCashflow")),
        free_cash_flow=_num(info.get("freeCashflow")),
        total_revenue=_num(info.get("totalRevenue")),
        held_percent_insiders=_num(info.get("heldPercentInsiders")),
        held_percent_institutions=_num(info.get("heldPercentInstitutions")),
        fifty_two_week_change=_num(info.get("52WeekChange")),
        target_mean_price=_num(info.get("targetMeanPrice")),
        recommendation_mean=_num(info.get("recommendationMean")),
    )
