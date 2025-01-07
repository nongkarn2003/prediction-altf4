import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import date, timedelta

# สไตล์ Streamlit
streamlit_style = """
<style>
@import url(https://fonts.googleapis.com/css2?family=Mitr:wght@200;300;400;500;600;700&display=swap);
* { font-family: 'Mitr', sans-serif; }
.st-emotion-cache-1dp5vir {   
background-image: linear-gradient(90deg, rgb(0 0 0), rgb(0 0 0));
}
</style>
"""
st.markdown(streamlit_style, unsafe_allow_html=True)

# สไตล์เพิ่มเติม
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
st.markdown(css_string, unsafe_allow_html=True)

# รายชื่อหุ้น
tickers = [
    "ADVANC.BK", "AOT.BK", "AWC.BK", "BANPU.BK", "BBL.BK", "BDMS.BK", "BEM.BK",
    "BGRIM.BK", "BH.BK", "BTS.BK", "CBG.BK", "CENTEL.BK", "COM7.BK", "CPALL.BK",
    "CPF.BK", "CPN.BK", "CRC.BK", "DELTA.BK", "EA.BK", "EGCO.BK", "GLOBAL.BK",
    "GPSC.BK", "GULF.BK", "HMPRO.BK", "INTUCH.BK", "IVL.BK", "KBANK.BK",
    "KCE.BK", "KTB.BK", "KTC.BK", "LH.BK", "MINT.BK", "MTC.BK", "OR.BK",
    "OSP.BK", "PTT.BK", "PTTEP.BK", "PTTGC.BK", "RATCH.BK", "SAWAD.BK",
    "SCB.BK", "SCC.BK", "SCGP.BK", "TISCO.BK", "TOP.BK", "TTB.BK", "TU.BK", "WHA.BK"
]

# ดึงข้อมูลหุ้น
def get_stock_data(ticker, start_date, end_date):
    try:
        stock_data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        if 'Adj Close' in stock_data.columns:
            stock_data['Price'] = stock_data['Adj Close']
        elif 'Close' in stock_data.columns:
            stock_data['Price'] = stock_data['Close']
        else:
            st.warning(f"หุ้น {ticker} ไม่มีข้อมูล 'Adj Close' หรือ 'Close'")
            return pd.DataFrame()
        stock_data = stock_data.ffill()
        return stock_data
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")
        return pd.DataFrame()

# จำลองการลงทุนแบบ DCA
def simulate_dca(stock_data, monthly_amount, duration_months, start_date):
    dca_data = pd.DataFrame(columns=["Date", "Shares", "Total Invested", "Portfolio Value"])
    total_invested = 0
    shares = 0
    start_date = pd.to_datetime(start_date)

    for i in range(duration_months):
        date = start_date + pd.DateOffset(months=i)
        if date not in stock_data.index:
            date = stock_data.index[stock_data.index.searchsorted(date)]
        price = stock_data.loc[date, "Price"]
        shares_bought = monthly_amount / price
        shares += shares_bought
        total_invested += monthly_amount
        portfolio_value = shares * price
        dca_data.loc[len(dca_data)] = [date, shares, total_invested, portfolio_value]
    return dca_data

# แสดงผลกราฟสำหรับ DCA
def plot_returns_and_price(dca_data, total_invested, stock_data, investment_type):
    fig = go.Figure()
    if investment_type == "DCA":
        fig.add_trace(go.Scatter(x=dca_data["Date"], y=dca_data["Portfolio Value"], mode="lines", name="มูลค่าของพอร์ต"))
        fig.add_trace(go.Scatter(x=dca_data["Date"], y=dca_data["Total Invested"], mode="lines", name="จำนวนเงินลงทุน"))
        fig.update_layout(title="ผลตอบแทนของการลงทุนแบบ DCA", xaxis_title="Date", yaxis_title="Value")
    st.plotly_chart(fig)

# แสดงผลกราฟสำหรับ Lump Sum
def plot_returns_and_price_lump_sum(stock_data, initial_investment, investment_type):
    fig = go.Figure()
    initial_shares = initial_investment / stock_data.iloc[0]["Price"]
    portfolio_value = initial_shares * stock_data["Price"]
    dates = stock_data.index
    fig.add_trace(go.Scatter(x=dates, y=portfolio_value, mode="lines", name="มูลค่าของพอร์ต"))
    fig.add_trace(go.Scatter(x=dates, y=[initial_investment] * len(dates), mode="lines", name="จำนวนเงินลงทุน"))
    fig.update_layout(title="ผลตอบแทนของการลงทุนแบบ Lump Sum", xaxis_title="Date", yaxis_title="Value")
    st.plotly_chart(fig)

# แสดงผลลัพธ์
def display_summary(data, initial_investment, investment_type, final_portfolio_value=None):
    if investment_type == "DCA":
        final_portfolio_value = data["Portfolio Value"].iloc[-1]
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

# ฟังก์ชันหลัก
def main():
    st.title("DCA vs Lump Sum Investment")
    investment_type = st.radio("เลือกวิธีการลงทุน", ["DCA", "Lump Sum"])
    selected_ticker = st.selectbox("เลือกหุ้น", tickers)
    if investment_type == "DCA":
        monthly_amount = st.number_input("จํานวนเงินลงทุนต่อเดือน", min_value=0.0, step=1.0)
        duration_months = st.number_input("ระยะเวลาการลงทุน (เดือน)", min_value=1, step=1)
    else:
        lump_sum_amount = st.number_input("จํานวนเงินลงทุน", min_value=0.0, step=1.0)
        duration_months = st.number_input("ระยะเวลาการลงทุน (เดือน)", min_value=1, step=1)
    start_date = st.date_input("วันที่เริ่มลงทุน", value=date(2018, 1, 1), max_value=date.today() - timedelta(days=1))
    end_date = start_date + pd.DateOffset(months=duration_months)
    stock_data = get_stock_data(selected_ticker, start_date, end_date)
    if stock_data.empty:
        st.warning("ไม่มีข้อมูลสำหรับหุ้นนี้ในช่วงเวลาที่เลือก")
    else:
        if st.button("คำนวณ"):
            if investment_type == "DCA":
                dca_data = simulate_dca(stock_data, monthly_amount, duration_months, start_date)
                plot_returns_and_price(dca_data, monthly_amount * duration_months, stock_data, investment_type)
                display_summary(dca_data, monthly_amount * duration_months, investment_type)
            else:
                initial_shares = lump_sum_amount / stock_data.iloc[0]["Price"]
                final_portfolio_value = initial_shares * stock_data.iloc[-1]["Price"]
                plot_returns_and_price_lump_sum(stock_data, lump_sum_amount, investment_type)
                display_summary(stock_data, lump_sum_amount, investment_type, final_portfolio_value)

if __name__ == "__main__":
    main()
