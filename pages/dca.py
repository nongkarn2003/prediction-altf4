import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import date, timedelta

streamlit_style = """
<style>
@import url(https://fonts.googleapis.com/css2?family=Mitr:wght@200;300;400;500;600;700&display=swap);

* {
    font-family: 'Mitr', sans-serif;
}
.st-emotion-cache-1dp5vir {   
background-image: linear-gradient(90deg, rgb(0 0 0), rgb(0 0 0));
}
</style>
"""

st.markdown(streamlit_style, unsafe_allow_html=True)

css_string = """
<style>
.st-emotion-cache-1dp5vir {
    position: absolute;
    top: 0px;
    right: 0px;
    left: 0px;
    height: 0.125rem;
    z-index: 999990;
}
</style>
"""

# Render the CSS styles in your Streamlit app
st.markdown(css_string, unsafe_allow_html=True)

# List of stock tickers
tickers = ["ADVANC.BK", "AOT.BK", "AWC.BK", "BANPU.BK", "BBL.BK", "BDMS.BK", "BEM.BK", "BGRIM.BK", "BH.BK", "BTS.BK", 
           "CBG.BK", "CENTEL.BK", "COM7.BK", "CPALL.BK", "CPF.BK", "CPN.BK", "CRC.BK", "DELTA.BK", "EA.BK", "EGCO.BK", 
           "GLOBAL.BK", "GPSC.BK", "GULF.BK", "HMPRO.BK", "INTUCH.BK", "IVL.BK", "KBANK.BK", "KCE.BK", "KTB.BK", "KTC.BK", 
           "LH.BK", "MINT.BK", "MTC.BK", "OR.BK", "OSP.BK", "PTT.BK", "PTTEP.BK", "PTTGC.BK", "RATCH.BK", "SAWAD.BK", 
           "SCB.BK", "SCC.BK", "SCGP.BK", "TISCO.BK", "TOP.BK", "TTB.BK", "TU.BK", "WHA.BK"]

# Streamlit app
def main():
    st.title("DCA vs Lump Sum Investment Comparison")

    # User input for stock ticker
    selected_ticker = st.selectbox("เลือกหุ้น", tickers)

    # User input for investment duration and amount
    duration_months = st.number_input("ระยะเวลาการลงทุน (เดือน)", min_value=1, step=1)
    start_date = st.date_input("วันที่เริ่มลงทุน", value=date(2018, 1, 1), max_value=date.today() - timedelta(days=1))

    # User input for investment amounts (input both to avoid confusion)
    monthly_amount = st.number_input("จำนวนเงินลงทุนต่อเดือน (DCA)", min_value=0.0, step=1.0)
    lump_sum_amount = st.number_input("จำนวนเงินลงทุนครั้งเดียว (Lump Sum)", min_value=0.0, step=1.0)

    # Get stock data
    end_date = start_date + pd.DateOffset(months=duration_months)
    stock_data = yf.download(selected_ticker, start=start_date, end=end_date, progress=False)

    # Forward fill missing data to handle non-trading days
    stock_data = stock_data.ffill()

    # Calculate returns and plot both methods
    if st.button("คำนวณ"):
        # Simulate DCA
        total_dca_invested = monthly_amount * duration_months
        dca_data = simulate_dca(stock_data, monthly_amount, duration_months, start_date)
        dca_final_portfolio_value = dca_data["Portfolio Value"].iloc[-1]

        # Simulate Lump Sum
        initial_shares = lump_sum_amount / stock_data.iloc[0]["Adj Close"]
        final_portfolio_value_lump_sum = initial_shares * stock_data.iloc[-1]["Adj Close"]

        # Plot the comparison graph
        fig = plot_comparison(dca_data, total_dca_invested, stock_data, lump_sum_amount, final_portfolio_value_lump_sum)
        st.plotly_chart(fig)

        # Display summary for both
        display_summary(dca_data, total_dca_invested, "DCA", dca_final_portfolio_value)
        display_summary(stock_data, lump_sum_amount, "Lump Sum", final_portfolio_value_lump_sum)

# Function to simulate DCA
def simulate_dca(stock_data, monthly_amount, duration_months, start_date):
    dca_data = pd.DataFrame(columns=["Date", "Shares", "Total Invested", "Portfolio Value"])
    total_invested = 0
    shares = 0
    start_date = pd.to_datetime(start_date)  # Convert start_date to datetime

    for i in range(duration_months):
        date = start_date + pd.DateOffset(months=i)  # Calculate the monthly date
        if date not in stock_data.index:  # Check if the date is not a trading day
            date = stock_data.index[stock_data.index.searchsorted(date)]  # Adjust to the closest trading day
        price = stock_data.loc[date, "Adj Close"]
        shares_bought = monthly_amount / price
        shares += shares_bought
        total_invested += monthly_amount
        portfolio_value = shares * price
        dca_data.loc[len(dca_data)] = [date, shares, total_invested, portfolio_value]

    return dca_data

# Function to plot comparison between DCA and Lump Sum
def plot_comparison(dca_data, total_dca_invested, stock_data, lump_sum_investment, lump_sum_final_value):
    fig = go.Figure()

    # Plot DCA
    fig.add_trace(go.Scatter(x=dca_data["Date"], y=dca_data["Portfolio Value"], mode="lines", name="มูลค่าของพอร์ต DCA"))
    fig.add_trace(go.Scatter(x=dca_data["Date"], y=dca_data["Total Invested"], mode="lines", name="จำนวนเงินลงทุน DCA"))

    # Plot Lump Sum
    initial_shares = lump_sum_investment / stock_data.iloc[0]["Adj Close"]
    portfolio_value_lump_sum = initial_shares * stock_data["Adj Close"]
    dates = stock_data.index
    fig.add_trace(go.Scatter(x=dates, y=portfolio_value_lump_sum, mode="lines", name="มูลค่าของพอร์ต Lump Sum"))
    fig.add_trace(go.Scatter(x=dates, y=[lump_sum_investment] * len(dates), mode="lines", name="จำนวนเงินลงทุน Lump Sum"))

    fig.update_layout(title="เปรียบเทียบผลตอบแทน DCA vs Lump Sum", xaxis_title="Date", yaxis_title="Value")
    
    return fig

# Function to display summary
def display_summary(data, initial_investment, investment_type, final_portfolio_value=None):
    if investment_type == "DCA":
        total_invested = data["Total Invested"].iloc[-1]
        returns = (final_portfolio_value - total_invested) / total_invested * 100
        st.write(f"**ภาพรวมของการลงทุนแบบ DCA**")
        st.write(f"มูลค่าของพอร์ต: {final_portfolio_value:.2f}")
        st.write(f"จำนวนเงินที่ลงทุน: {total_invested:.2f}")
        st.write(f"ผลตอบแทน: {returns:.2f}%")
    else:
        returns = (final_portfolio_value - initial_investment) / initial_investment * 100
        st.write(f"**ภาพรวมของการลงทุนแบบ Lump Sum**")
        st.write(f"มูลค่าของพอร์ต: {final_portfolio_value:.2f}")
        st.write(f"จำนวนเงินที่ลงทุน: {initial_investment:.2f}")
        st.write(f"ผลตอบแทน: {returns:.2f}%")

if __name__ == "__main__":
    main()
