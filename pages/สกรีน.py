import streamlit as st
import yfinance as yf
import pandas as pd

# List of stock tickers
stocks = ["ADVANC.BK", "AOT.BK", "AWC.BK", "BANPU.BK", "BBL.BK", "BDMS.BK", "BEM.BK", "BGRIM.BK", "BH.BK", "BTS.BK",
          "CBG.BK", "CENTEL.BK", "COM7.BK", "CPALL.BK", "CPF.BK", "CPN.BK", "CRC.BK", "DELTA.BK", "EA.BK", "EGCO.BK",
          "GLOBAL.BK", "GPSC.BK", "GULF.BK", "HMPRO.BK", "INTUCH.BK", "IVL.BK", "KBANK.BK", "KCE.BK", "KTB.BK", "KTC.BK",
          "LH.BK", "MINT.BK", "MTC.BK", "OR.BK", "OSP.BK", "PTT.BK", "PTTEP.BK", "PTTGC.BK", "RATCH.BK", "SAWAD.BK",
          "SCB.BK", "SCC.BK", "SCGP.BK", "TISCO.BK", "TLI.BK", "TOP.BK", "TRUE.BK", "TTB.BK", "TU.BK", "WHA.BK"]

# Function to get stock data
def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    return {
        "Ticker": ticker,
        "PE Ratio": info.get('trailingPE', None),
        "PB Ratio": info.get('priceToBook', None),
        "Debt to Equity": info.get('debtToEquity', None),
        "ROE": info.get('returnOnEquity', None),
        "ROA": info.get('returnOnAssets', None),
    }

# Streamlit app
st.title("Stock Screener")

# Expander for filter criteria
with st.expander("Filter Criteria", expanded=True):
    selected_filters = st.multiselect(
        "Select Filters",
        ["PE Ratio", "PB Ratio", "Debt to Equity", "ROE", "ROA"],
        default=["PE Ratio", "PB Ratio", "Debt to Equity", "ROE", "ROA"]
    )

    pe_ratio = pb_ratio = de_ratio = roe = roa = None

    if "PE Ratio" in selected_filters:
        pe_ratio = st.number_input("PE Ratio (Maximum)", min_value=0.0, value=1000.0, step=0.1)
    if "PB Ratio" in selected_filters:
        pb_ratio = st.number_input("PB Ratio (Maximum)", min_value=0.0, value=1000.0, step=0.1)
    if "Debt to Equity" in selected_filters:
        de_ratio = st.number_input("Debt to Equity (Maximum)", min_value=0.0, value=1000.0, step=0.1)
    if "ROE" in selected_filters:
        roe = st.number_input("ROE (Minimum, in %)", min_value=0.0, value=0.0, step=0.1)
    if "ROA" in selected_filters:
        roa = st.number_input("ROA (Minimum, in %)", min_value=0.0, value=0.0, step=0.1)

# Load data for all stocks
data = []
for stock in stocks:
    data.append(get_stock_data(stock))

df = pd.DataFrame(data)

# Remove rows with None or NaN values in the selected filters
if pe_ratio is not None:
    df = df[df['PE Ratio'].notna()]
if pb_ratio is not None:
    df = df[df['PB Ratio'].notna()]
if de_ratio is not None:
    df = df[df['Debt to Equity'].notna()]
if roe is not None:
    df = df[df['ROE'].notna()]
if roa is not None:
    df = df[df['ROA'].notna()]

# Apply filters conditionally based on user selection
filtered_df = df.copy()

if pe_ratio is not None and pe_ratio < 1000.0:
    filtered_df = filtered_df[filtered_df['PE Ratio'] <= pe_ratio]
if pb_ratio is not None and pb_ratio < 1000.0:
    filtered_df = filtered_df[filtered_df['PB Ratio'] <= pb_ratio]
if de_ratio is not None and de_ratio < 1000.0:
    filtered_df = filtered_df[filtered_df['Debt to Equity'] <= de_ratio]
if roe is not None and roe > 0.0:
    filtered_df = filtered_df[filtered_df['ROE'] >= (roe / 100)]
if roa is not None and roa > 0.0:
    filtered_df = filtered_df[filtered_df['ROA'] >= (roa / 100)]

# Show the filtered stocks in a scrollable table
st.header("Filtered Stocks")
st.dataframe(filtered_df.style.format({
    "PE Ratio": "{:.2f}",
    "PB Ratio": "{:.2f}",
    "Debt to Equity": "{:.2f}",
    "ROE": "{:.2%}",
    "ROA": "{:.2%}"
}), height=600)

# Display download button for filtered data
st.download_button(
    label="Download data as CSV",
    data=filtered_df.to_csv(index=False).encode('utf-8'),
    file_name='filtered_stocks.csv',
    mime='text/csv',
)
