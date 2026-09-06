import streamlit as st


def render_methodology():
    st.subheader("Scoring Methodology")
    st.markdown(
        """
### Composite Deal Score

| Factor | Weight |
|---|---:|
| Valuation | 25% |
| Business Quality | 20% |
| Growth | 15% |
| Financial Health | 15% |
| Cash Flow | 10% |
| Estimate Revisions | 5% |
| Ownership | 5% |
| Market / Catalyst | 5% |

### Value Trap Risk

The scanner separately estimates whether a stock is cheap for a bad reason. Risk rises with:

- declining revenue
- declining earnings
- negative free cash flow
- excessive leverage
- weak operating margins

### Rating bands

- **90–100:** Exceptional Opportunity
- **80–89:** Strong Buy Candidate
- **70–79:** Attractive
- **60–69:** Fairly Valued
- **50–59:** Neutral
- **40–49:** Expensive / Weak
- **0–39:** Avoid

### Important v0.1 limitation

This first model uses broad absolute thresholds. A true institutional model should compare each company with:

1. its industry
2. its sector
3. its own historical valuation range
4. the growth and return profile implied by the current price

Those relative-value upgrades are the next development phase.
        """
    )
