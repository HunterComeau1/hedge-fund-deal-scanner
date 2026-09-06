from core.data_provider import StockSnapshot
from core.scoring import score_stock


def test_score_in_range():
    s = StockSnapshot(
        ticker="TEST", company="Test", sector="Tech", industry="Software",
        price=100, market_cap=1_000_000_000,
        trailing_pe=20, forward_pe=18, price_to_book=4,
        enterprise_to_ebitda=12, enterprise_to_revenue=4,
        return_on_equity=0.25, return_on_assets=0.12,
        gross_margin=0.65, operating_margin=0.25, profit_margin=0.20,
        revenue_growth=0.15, earnings_growth=0.20,
        total_cash=500_000_000, total_debt=200_000_000,
        debt_to_equity=40, current_ratio=1.8,
        operating_cash_flow=200_000_000, free_cash_flow=150_000_000,
        total_revenue=1_000_000_000,
        held_percent_insiders=0.03, held_percent_institutions=0.75,
        fifty_two_week_change=0.15, target_mean_price=125,
        recommendation_mean=1.8,
    )
    result = score_stock(s)
    assert 0 <= result.deal_score <= 100
    assert 0 <= result.value_trap_risk <= 100
