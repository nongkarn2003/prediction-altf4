import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="DCA vs Lump Sum", layout="wide")

# ------------------------ SETTINGS ------------------------
STOCK_LIST = ["AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA", "NVDA"]
DEFAULT_TICKER = "AAPL"

# ------------------------ FUNCTIONS ------------------------

@st.cache_data
def get_stock_data(ticker, start_date):
    data = yf.download(ticker, start=start_date)
    data = data[["Adj Close"]].rename(columns={"Adj Close": "Price"})
    return data

def simulate_dca(stock_data, monthly_amount, duration_months, start_date):
    results = []
    total_invested = 0
    total_shares = 0
    start_date = pd.to_datetime(start_date)

    for i in range(duration_months):
        date = start_date + pd.DateOffset(months=i)
        available_dates = stock_data.index[stock_data.index >= date]
        if len(available_dates) == 0:
            continue
        actual_date = available_dates[0]
        price = stock_data.at[actual_date, "Price"]
        if pd.isna(price) or price <= 0:
            continue
        shares_bought = monthly_amount / price
        total_invested += monthly_amount
        total_shares += shares_bought
        portfolio_value = total_shares * price
        results.append({
            "Date": actual_date,
            "Price": price,
            "Total_Invested": total_invested,
            "Portfolio_Value": portfolio_value,
            "Return (%)": ((portfolio_value - total_invested) / total_invested) * 100
        })

    return pd.DataFrame(results)

def simulate_lump_sum(stock_data, lump_sum_amount, start_date):
    start_date = pd.to_datetime(start_date)
    available_dates = stock_data.index[stock_data.index >= start_date]
    if len(available_dates) == 0:
        return pd.DataFrame()
    start_actual_date = available_dates[0]
    initial_price = stock_data.at[start_actual_date, "Price"]
    if pd.isna(initial_price) or initial_price <= 0:
        return pd.DataFrame()
    shares = lump_sum_amount / initial_price

    df = stock_data.loc[start_actual_date:].copy()
    df["Portfolio_Value"] = df["Price"] * shares
    df["Return (%)"] = ((df["Portfolio_Value"] - lump_sum_amount) / lump_sum_amount) * 100
    df["Total_Invested"] = lump_sum_amount
    df = df.reset_index()
    return df

# ------------------------ MAIN APP ------------------------

st.title("📈 DCA vs Lump Sum Investment Simulator")

col1, col2, col3 = st.columns(3)
with col1:
    ticker = st.selectbox("Select a stock:", STOCK_LIST, index=STOCK_LIST.index(DEFAULT_TICKER))
with col2:
    start_date = st.date_input("Start date:", datetime(2020, 1, 1))
with col3:
    duration_months = st.number_input("Investment duration (months):", min_value=1, max_value=240, value=36)

col4, col5 = st.columns(2)
with col4:
    monthly_amount = st.number_input("Monthly investment amount (DCA):", min_value=10, step=10, value=100)
with col5:
    lump_sum_amount = st.number_input("Lump Sum amount:", min_value=10, step=10, value=3600)

stock_data = get_stock_data(ticker, start_date)

if stock_data.empty:
    st.error("❌ Failed to retrieve data for selected stock.")
else:
    dca_data = simulate_dca(stock_data, monthly_amount, duration_months, start_date)
    lump_sum_data = simulate_lump_sum(stock_data, lump_sum_amount, start_date)

    if dca_data.empty or lump_sum_data.empty:
        st.warning("⚠️ Unable to simulate one or both strategies. Please try different parameters.")
    else:
        st.subheader("📊 Performance Over Time")

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(dca_data["Date"], dca_data["Portfolio_Value"], label="DCA")
        ax.plot(lump_sum_data["Date"], lump_sum_data["Portfolio_Value"], label="Lump Sum")
        ax.set_title(f"Portfolio Value Comparison ({ticker})")
        ax.set_xlabel("Date")
        ax.set_ylabel("Portfolio Value ($)")
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)

        st.subheader("📄 Final Summary")
        col1, col2 = st.columns(2)

        with col1:
            last = dca_data.iloc[-1]
            st.metric("DCA Portfolio Value", f"${last['Portfolio_Value']:.2f}")
            st.metric("Total Invested", f"${last['Total_Invested']:.2f}")
            st.metric("Return (%)", f"{last['Return (%)']:.2f}%")

        with col2:
            last = lump_sum_data.iloc[-1]
            st.metric("Lump Sum Portfolio Value", f"${last['Portfolio_Value']:.2f}")
            st.metric("Total Invested", f"${last['Total_Invested']:.2f}")
            st.metric("Return (%)", f"{last['Return (%)']:.2f}%")

        with st.expander("📋 View Raw Data"):
            st.write("DCA Simulation:")
            st.dataframe(dca_data)
            st.write("Lump Sum Simulation:")
            st.dataframe(lump_sum_data)
