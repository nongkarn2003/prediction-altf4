import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import datetime as dt
import matplotlib.pyplot as plt

# ========================
# 📌 ฟังก์ชันคำนวณผลตอบแทนพอร์ต
# ========================
def download_data(tickers, start, end):
    data = yf.download(tickers, start=start, end=end)["Close"]
    return data.dropna()

def calculate_portfolio(data, weights):
    normalized = data / data.iloc[0]
    weighted = normalized.mul(weights, axis=1)
    portfolio = weighted.sum(axis=1)
    return portfolio

def calculate_performance(portfolio, risk_free_rate=0.02):
    daily_return = portfolio.pct_change().dropna()
    total_return = portfolio[-1] / portfolio[0] - 1
    annual_return = (1 + total_return) ** (252 / len(portfolio)) - 1
    annual_volatility = daily_return.std() * np.sqrt(252)
    sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility
    return {
        "Total Return (%)": total_return * 100,
        "Annualized Return (%)": annual_return * 100,
        "Annualized Volatility (%)": annual_volatility * 100,
        "Sharpe Ratio": sharpe_ratio
    }

# ========================
# 📌 Streamlit App
# ========================
st.title("📊 Portfolio Allocation Simulator")

st.markdown("เลือกหุ้นและสัดส่วนการลงทุน เพื่อดูผลตอบแทนย้อนหลัง")

# --- Input ส่วนของผู้ใช้ ---
tickers_input = st.text_input("ใส่ชื่อหุ้น (Ticker) คั่นด้วย comma เช่น AAPL,MSFT,NVDA", "AAPL,MSFT,NVDA")
tickers = [x.strip().upper() for x in tickers_input.split(",") if x.strip() != ""]

weight_input = st.text_input("ใส่น้ำหนัก (%) ตามลำดับ เช่น 40,30,30", "40,30,30")
weights = [float(w.strip()) / 100 for w in weight_input.split(",")]

if len(tickers) != len(weights):
    st.error("จำนวน Ticker กับ Weight ไม่ตรงกัน")
    st.stop()

if sum(weights) != 1.0:
    st.warning(f"น้ำหนักรวม = {sum(weights)*100:.2f}%, ควรเท่ากับ 100%")

# --- เลือกช่วงเวลา ---
end_date = dt.date.today()
start_date = st.date_input("เลือกวันเริ่มต้น", dt.date(end_date.year - 5, 1, 1))

# --- ดึงข้อมูลและคำนวณ ---
with st.spinner("📥 กำลังโหลดข้อมูล..."):
    data = download_data(tickers, start_date, end_date)

if data.empty:
    st.error("ไม่สามารถโหลดข้อมูลได้")
    st.stop()

portfolio = calculate_portfolio(data, weights)
performance = calculate_performance(portfolio)

# --- แสดงผล ---
st.subheader("📈 ผลตอบแทนพอร์ตย้อนหลัง")
st.line_chart(portfolio)

st.subheader("📊 สถิติของพอร์ต")
st.write(pd.DataFrame(performance, index=["Portfolio"]).T)

# --- เทียบกับ SPY ---
spy = yf.download("SPY", start=start_date, end=end_date)["Close"]
spy = spy / spy.iloc[0]
comparison = pd.DataFrame({"Portfolio": portfolio / portfolio.iloc[0], "SPY": spy})
st.subheader("📉 เปรียบเทียบกับดัชนี S&P 500")
st.line_chart(comparison)
