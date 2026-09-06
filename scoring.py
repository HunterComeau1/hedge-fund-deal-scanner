from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Callable

import numpy as np

from core.data_provider import StockSnapshot


def clamp(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return float(max(lo, min(hi, x)))


def linear_score(value, bad, good, higher_is_better=True, neutral=50.0):
    if value is None or not np.isfinite(value):
        return neutral
    if bad == good:
        return neutral
    raw = (value - bad) / (good - bad) * 100
    if not higher_is_better:
        raw = 100 - raw
    return clamp(raw)


def avg(scores):
    vals = [float(x) for x in scores if x is not None]
    return round(sum(vals) / len(vals), 1) if vals else 50.0


@dataclass
class ScoreCard:
    valuation: float
    quality: float
    growth: float
    financial_health: float
    cash_flow: float
    revisions: float
    ownership: float
    market_catalyst: float
    deal_score: float
    value_trap_risk: float
    upside_to_target: float | None
    rating: str

    def to_dict(self):
        return asdict(self)


def score_valuation(s: StockSnapshot) -> float:
    return avg([
        linear_score(s.forward_pe, 40, 10, higher_is_better=True),
        linear_score(s.trailing_pe, 45, 12, higher_is_better=True),
        linear_score(s.enterprise_to_ebitda, 25, 8, higher_is_better=True),
        linear_score(s.enterprise_to_revenue, 8, 2, higher_is_better=True),
        linear_score(s.price_to_book, 10, 1.5, higher_is_better=True),
    ])


def score_quality(s: StockSnapshot) -> float:
    return avg([
        linear_score(s.return_on_equity, 0.00, 0.30),
        linear_score(s.return_on_assets, 0.00, 0.15),
        linear_score(s.gross_margin, 0.15, 0.65),
        linear_score(s.operating_margin, 0.03, 0.30),
        linear_score(s.profit_margin, 0.02, 0.25),
    ])


def score_growth(s: StockSnapshot) -> float:
    return avg([
        linear_score(s.revenue_growth, -0.10, 0.25),
        linear_score(s.earnings_growth, -0.20, 0.30),
    ])


def score_financial_health(s: StockSnapshot) -> float:
    cash_debt = None
    if s.total_cash is not None and s.total_debt not in (None, 0):
        cash_debt = s.total_cash / s.total_debt
    elif s.total_cash is not None and s.total_debt == 0:
        cash_debt = 3.0

    return avg([
        linear_score(s.debt_to_equity, 250, 30, higher_is_better=True),
        linear_score(s.current_ratio, 0.7, 2.0),
        linear_score(cash_debt, 0.15, 1.5),
    ])


def score_cash_flow(s: StockSnapshot) -> float:
    fcf_margin = None
    ocf_margin = None
    if s.total_revenue not in (None, 0):
        if s.free_cash_flow is not None:
            fcf_margin = s.free_cash_flow / s.total_revenue
        if s.operating_cash_flow is not None:
            ocf_margin = s.operating_cash_flow / s.total_revenue

    return avg([
        linear_score(fcf_margin, -0.03, 0.20),
        linear_score(ocf_margin, 0.00, 0.25),
        100 if (s.free_cash_flow or 0) > 0 else 20,
    ])


def score_revisions(s: StockSnapshot) -> float:
    # Temporary proxy until a dedicated estimate-revision feed is added.
    if s.recommendation_mean is None:
        return 50.0
    # Yahoo: ~1 strong buy, ~5 sell.
    return linear_score(s.recommendation_mean, 4.0, 1.2, higher_is_better=True)


def score_ownership(s: StockSnapshot) -> float:
    return avg([
        linear_score(s.held_percent_institutions, 0.20, 0.85),
        linear_score(s.held_percent_insiders, 0.00, 0.12),
    ])


def score_market_catalyst(s: StockSnapshot) -> tuple[float, float | None]:
    upside = None
    if s.price and s.target_mean_price:
        upside = (s.target_mean_price / s.price) - 1

    score = avg([
        linear_score(upside, -0.15, 0.35) if upside is not None else 50,
        linear_score(s.fifty_two_week_change, -0.30, 0.35),
    ])
    return score, upside


def score_value_trap_risk(s: StockSnapshot) -> float:
    risks = []

    if s.revenue_growth is not None:
        risks.append(linear_score(s.revenue_growth, 0.20, -0.15, higher_is_better=True))
    if s.earnings_growth is not None:
        risks.append(linear_score(s.earnings_growth, 0.25, -0.30, higher_is_better=True))
    if s.free_cash_flow is not None:
        risks.append(15 if s.free_cash_flow > 0 else 90)
    if s.debt_to_equity is not None:
        risks.append(linear_score(s.debt_to_equity, 30, 300))
    if s.operating_margin is not None:
        risks.append(linear_score(s.operating_margin, 0.25, -0.05, higher_is_better=True))

    return avg(risks)


def rating(score: float) -> str:
    if score >= 90:
        return "Exceptional Opportunity"
    if score >= 80:
        return "Strong Buy Candidate"
    if score >= 70:
        return "Attractive"
    if score >= 60:
        return "Fairly Valued"
    if score >= 50:
        return "Neutral"
    if score >= 40:
        return "Expensive / Weak"
    return "Avoid"


def score_stock(s: StockSnapshot) -> ScoreCard:
    valuation = score_valuation(s)
    quality = score_quality(s)
    growth = score_growth(s)
    health = score_financial_health(s)
    cash_flow = score_cash_flow(s)
    revisions = score_revisions(s)
    ownership = score_ownership(s)
    catalyst, upside = score_market_catalyst(s)

    composite = (
        valuation * 0.25
        + quality * 0.20
        + growth * 0.15
        + health * 0.15
        + cash_flow * 0.10
        + revisions * 0.05
        + ownership * 0.05
        + catalyst * 0.05
    )

    trap = score_value_trap_risk(s)

    # Modest penalty for severe value-trap risk.
    adjusted = clamp(composite - max(0, trap - 70) * 0.15)

    return ScoreCard(
        valuation=round(valuation, 1),
        quality=round(quality, 1),
        growth=round(growth, 1),
        financial_health=round(health, 1),
        cash_flow=round(cash_flow, 1),
        revisions=round(revisions, 1),
        ownership=round(ownership, 1),
        market_catalyst=round(catalyst, 1),
        deal_score=round(adjusted, 1),
        value_trap_risk=round(trap, 1),
        upside_to_target=round(upside * 100, 1) if upside is not None else None,
        rating=rating(adjusted),
    )
