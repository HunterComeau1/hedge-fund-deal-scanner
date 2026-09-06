import streamlit as st

from pages.scanner import render_scanner
from pages.methodology import render_methodology

st.set_page_config(
    page_title="Hedge Fund Deal Scanner",
    page_icon="📈",
    layout="wide",
)

st.title("Hedge Fund Deal Scanner")
st.caption("Find stocks that look mispriced relative to business quality, growth, cash flow, and financial strength.")

page = st.sidebar.radio("Page", ["Deal Scanner", "Methodology"])

if page == "Deal Scanner":
    render_scanner()
else:
    render_methodology()
