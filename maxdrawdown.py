import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_datareader as pdr
import numpy as np

stocks = ('SET50.BK','ADVANC.BK', 'AOT.BK', 'AWC.BK', 'BANPU.BK', 'BBL.BK', 'BDMS.BK', 'BEM.BK', 'BGRIM.BK', 'BH.BK', 'BTS.BK', 'CBG.BK', 'CENTEL.BK', 'COM7.BK', 'CPALL.BK', 'CPF.BK', 'CPN.BK', 'CRC.BK', 'DELTA.BK', 'EA.BK', 'EGCO.BK', 'GLOBAL.BK', 'GPSC.BK', 'GULF.BK', 'HMPRO.BK', 'INTUCH.BK', 'IVL.BK', 'KBANK.BK', 'KCE.BK', 'KTB.BK', 'KTC.BK', 'LH.BK', 'MINT.BK', 'MTC.BK', 'OR.BK', 'OSP.BK', 'PTT.BK', 'PTTEP.BK', 'PTTGC.BK', 'RATCH.BK', 'SAWAD.BK', 'SCB.BK', 'SCC.BK', 'SCGP.BK', 'TISCO.BK', 'TLI.BK', 'TOP.BK', 'TRUE.BK', 'TTB.BK', 'TU.BK', 'WHA.BK')

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
st.header("ประเมินมูลค่าหุ้นและ Max Drawdown")
st.write('สูตรประเมินแบบ Benjamin Graham')
ticker = st.selectbox("เลือกหุ้น", stocks)
ng_pe = st.text_input('PE ที่ไม่มีการเติบโต', 8.5)
multiplier = st.text_input('ระยะการเติบโต', 2)
margin = st.text_input('ส่วนเผื่อราคา (%)', 35)

def get_data(ticker):
    ticker_data = yf.Ticker(ticker)
    df = ticker_data.history(period="5y")  # ดึงข้อมูลย้อนหลัง 5 ปี
    return df

def calculate_max_drawdown(df):
    peak = df['Close'].cummax()
    drawdown = (df['Close'] - peak) / peak
    max_drawdown = drawdown.min()
    return max_drawdown * 100  # คำนวณเป็นเปอร์เซ็นต์

def get_stock_info(ticker, ng_pe, multiplier, margin):
    ticker_data = yf.Ticker(ticker)
    quote = ticker_data.info
    current_price = quote.get("regularMarketPreviousClose", quote.get("ask"))
    eps = quote.get("trailingEps", 0)
    growth_rate = quote.get("earningsGrowth", 0)
    aaa_df = pdr.get_data_fred('AAA')
    current_yield = aaa_df.iloc[-1][0]
    return {
        "current_price": float(current_price),
        "eps": float(eps),
        "growth_rate": float(growth_rate),
        "current_yield": float(current_yield),
        "ng_pe": float(ng_pe),
        "multiplier": float(multiplier),
        "margin": float(margin)
    }

if st.button('คํานวณ'):
    df = get_data(ticker)
    data = get_stock_info(ticker, ng_pe, multiplier, margin)

    # คำนวณ Max Drawdown
    max_drawdown = calculate_max_drawdown(df)
    
    st.markdown("""---""")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="EPS(฿)", value=data["eps"])
    with col2:
        st.metric(label="อัตรการเติบโตระยะยาว (5 ปี)", value=data["growth_rate"])
    with col3:
        st.metric(label="ผลตอบแทนของบริษัท AAA", value=data["current_yield"])
    
    st.markdown("""---""")
    int_value = (data["eps"] * (data["ng_pe"] + data["multiplier"] * data["growth_rate"]) * 4.486) / data["current_yield"]
    int_value = round(int_value, 2)
    stock_price = round(data["current_price"], 2)
    margin_rate = data["margin"] / 100
    accept_price = (1 - margin_rate) * int_value
    accept_price = round(accept_price, 2)
    
    col4, col5, col6 = st.columns(3)
    with col4:
        st.subheader('ราคาหุ้นปัจจุบัน(฿)')
        st.subheader(f"**:blue[{stock_price}]**")
    with col5:
        st.subheader('มูลค่าหุ้นที่แท้จริง(฿)')
        st.subheader(f"**:blue[{int_value}]**")
    with col6:
        st.subheader('ราคาที่ยอมรับได้(฿)')
        st.subheader(f"**:blue[{accept_price}]**")
    
    st.markdown("""---""")
    st.subheader(f"Max Drawdown: **:red[{round(max_drawdown, 2)}%]**")
