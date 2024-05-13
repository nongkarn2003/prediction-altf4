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
tickers = ["ADVANC.BK", "AOT.BK", "AWC.BK", "BANPU.BK", "BBL.BK", "BDMS.BK", "BEM.BK", "BGRIM.BK", "BH.BK", "BTS.BK", "CBG.BK", "CENTEL.BK", "COM7.BK", "CPALL.BK", "CPF.BK", "CPN.BK", "CRC.BK", "DELTA.BK", "EA.BK", "EGCO.BK", "GLOBAL.BK", "GPSC.BK", "GULF.BK", "HMPRO.BK", "INTUCH.BK", "IVL.BK", "KBANK.BK", "KCE.BK", "KTB.BK", "KTC.BK", "LH.BK", "MINT.BK", "MTC.BK", "OR.BK", "OSP.BK", "PTT.BK", "PTTEP.BK", "PTTGC.BK", "RATCH.BK", "SAWAD.BK", "SCB.BK", "SCC.BK", "SCGP.BK", "TISCO.BK", "TOP.BK", "TTB.BK", "TU.BK", "WHA.BK"]

# Streamlit app
def main():
    st.title("DCA vs Lump Sum Investment")

    # User input for investment type
    investment_type = st.radio("Select investment type", ["DCA", "Lump Sum"])

    # User input for stock ticker
    selected_ticker = st.selectbox("Select stock ticker", tickers)

    # User input for investment amount and duration
    if investment_type == "DCA":
        monthly_amount = st.number_input("Monthly investment amount", min_value=0.0, step=1.0)
        duration_months = st.number_input("Investment duration (months)", min_value=1, step=1)
    else:
        lump_sum_amount = st.number_input("Lump sum investment amount", min_value=0.0, step=1.0)
        duration_months = st.number_input("Investment duration (months)", min_value=1, step=1)

    # User input for start date
    start_date = st.date_input("Select start date", value=date(2018, 1, 1), max_value=date.today() - timedelta(days=1))

    # Get stock data
    end_date = date.today()
    stock_data = yf.download(selected_ticker, start=start_date, end=end_date)

    # Calculate returns and plot
    if st.button("Calculate"):
        if investment_type == "DCA":
            total_invested = monthly_amount * duration_months
            dca_data = simulate_dca(stock_data, monthly_amount, duration_months)
            plot_returns_and_price(dca_data, total_invested, stock_data, investment_type)
            display_summary(dca_data, total_invested, investment_type)
        else:
            initial_shares = lump_sum_amount / stock_data.iloc[0]["Adj Close"]
            final_portfolio_value = initial_shares * stock_data.iloc[-1]["Adj Close"]
            plot_returns_and_price(stock_data, lump_sum_amount, stock_data, investment_type, duration_months)
            display_summary(stock_data, lump_sum_amount, final_portfolio_value, investment_type)

# Function to simulate DCA
def simulate_dca(stock_data, monthly_amount, duration_months):
    dca_data = pd.DataFrame(columns=["Date", "Shares", "Total Invested", "Portfolio Value"])
    total_invested = 0
    shares = 0

    for i in range(duration_months):
        date = stock_data.index[i * 21]  # Assuming monthly investment on the first trading day
        price = stock_data.loc[date, "Adj Close"]
        shares_bought = monthly_amount / price
        shares += shares_bought
        total_invested += monthly_amount
        portfolio_value = shares * price
        dca_data.loc[i] = [date, shares, total_invested, portfolio_value]

    return dca_data

# Function to plot returns and stock price
def plot_returns_and_price(data, initial_investment, stock_data, investment_type, duration_months=None):
    if investment_type == "DCA":
        portfolio_value = data["Portfolio Value"]
        dates = data["Date"]
        total_invested = data["Total Invested"]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=portfolio_value, mode="lines", name="Portfolio Value"))
        fig.add_trace(go.Scatter(x=dates, y=total_invested, mode="lines", name="Total Invested"))
        fig.update_layout(title="DCA Investment Returns and Stock Price", xaxis_title="Date", yaxis_title="Value")
    else:
        portfolio_value = stock_data["Adj Close"] * initial_investment / stock_data.iloc[0]["Adj Close"]
        dates = stock_data.index[:duration_months * 21]  # Adjust the number of data points based on the duration
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=portfolio_value[:len(dates)], mode="lines", name="Portfolio Value"))
        fig.add_trace(go.Scatter(x=dates, y=[initial_investment] * len(dates), mode="lines", name="Initial Investment"))
        fig.update_layout(title="Lump Sum Investment Returns and Stock Price", xaxis_title="Date", yaxis_title="Value")

    st.plotly_chart(fig)

# Function to display summary
def display_summary(data, initial_investment, final_portfolio_value=None, investment_type="DCA"):
    if investment_type == "DCA":
        final_portfolio_value = data["Portfolio Value"].iloc[-1]
        total_invested = data["Total Invested"].iloc[-1]
        returns = (final_portfolio_value - total_invested) / total_invested * 100
        st.write(f"**Summary for DCA Investment**")
        st.write(f"Final Portfolio Value: {final_portfolio_value:.2f}")
        st.write(f"Total Invested: {total_invested:.2f}")
        st.write(f"Returns: {returns:.2f}%")
    else:
        returns = (final_portfolio_value - initial_investment) / initial_investment * 100
        st.write(f"**Summary for Lump Sum Investment**")
        st.write(f"Final Portfolio Value: {final_portfolio_value:.2f}")
        st.write(f"Initial Investment: {initial_investment:.2f}")
        st.write(f"Returns: {returns:.2f}%")

if __name__ == "__main__":
    main()