import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_datareader as pdr
import numpy as np

# หุ้นใน SET50
stocks = ('SET50.BK', 'ADVANC.BK', 'AOT.BK', 'AWC.BK', 'BANPU.BK', 'BBL.BK', 'BDMS.BK', 
          'BEM.BK', 'BGRIM.BK', 'BH.BK', 'BTS.BK', 'CBG.BK', 'CENTEL.BK', 'COM7.BK', 
          'CPALL.BK', 'CPF.BK', 'CPN.BK', 'CRC.BK', 'DELTA.BK', 'EA.BK', 'EGCO.BK', 
          'GLOBAL.BK', 'GPSC.BK', 'GULF.BK', 'HMPRO.BK', 'INTUCH.BK', 'IVL.BK', 
          'KBANK.BK', 'KCE.BK', 'KTB.BK', 'KTC.BK', 'LH.BK', 'MINT.BK', 'MTC.BK', 
          'OR.BK', 'OSP.BK', 'PTT.BK', 'PTTEP.BK', 'PTTGC.BK', 'RATCH.BK', 'SAWAD.BK', 
          'SCB.BK', 'SCC.BK', 'SCGP.BK', 'TISCO.BK', 'TLI.BK', 'TOP.BK', 'TRUE.BK', 
          'TTB.BK', 'TU.BK', 'WHA.BK')

# สไตล์ Streamlit
streamlit_style = """
<style>
@import url(https://fonts.googleapis.com/css2?family=Mitr:wght@200;300;400;500;600;700&display=swap);
* { font-family: 'Mitr', sans-serif; }
.st-emotion-cache-1dp5vir { background-image: linear-gradient(90deg, rgb(0 0 0), rgb(0 0 0)); }
</style>
"""
st.markdown(streamlit_style, unsafe_allow_html=True)

# ส่วนหัว
st.header("ประเมินมูลค่าหุ้นและ Max Drawdown")
st.write('สูตรประเมินแบบ Benjamin Graham')
ticker = st.selectbox("เลือกหุ้น", stocks)
ng_pe = st.text_input('PE ที่ไม่มีการเติบโต', "8.5")
multiplier = st.text_input('ระยะการเติบโต', "2")
margin = st.text_input('ส่วนเผื่อราคา (%)', "35")

def get_data(ticker):
    try:
        ticker_data = yf.Ticker(ticker)
        df = ticker_data.history(period="5y")  # ดึงข้อมูลย้อนหลัง 5 ปี
        if 'Adj Close' in df.columns:
            df['Price'] = df['Adj Close']
        elif 'Close' in df.columns:
            df['Price'] = df['Close']
        else:
            st.warning("ไม่มีข้อมูลราคา ('Adj Close' หรือ 'Close') สำหรับหุ้นนี้")
            return pd.DataFrame()  # คืนค่า DataFrame ว่าง
        return df
    except Exception as e:
        st.error(f"ไม่สามารถดึงข้อมูลหุ้นได้: {e}")
        return pd.DataFrame()
# คำนวณ Max Drawdown
def calculate_max_drawdown(df):
    if df.empty:
        return None
    peak = df['Price'].cummax()
    drawdown = (df['Price'] - peak) / peak
    return drawdown.min() * 100

# ดึงข้อมูลหุ้นและดัชนี AAA
def get_stock_info(ticker, ng_pe, multiplier, margin):
    try:
        ticker_data = yf.Ticker(ticker)
        quote = ticker_data.info
        current_price = quote.get("regularMarketPreviousClose", 0)
        eps = quote.get("trailingEps", 0) or 0
        growth_rate = quote.get("earningsGrowth", 0) or 0
        aaa_df = pdr.get_data_fred('AAA')
        current_yield = aaa_df.iloc[-1][0] if not aaa_df.empty else 0
        return {
            "current_price": float(current_price or 0),
            "eps": float(eps),
            "growth_rate": float(growth_rate),
            "current_yield": float(current_yield or 0),
            "ng_pe": float(ng_pe),
            "multiplier": float(multiplier),
            "margin": float(margin) / 100
        }
    except Exception as e:
        st.error(f"ไม่สามารถดึงข้อมูลได้: {e}")
        return None

# คำนวณ
if st.button('คํานวณ'):
    df = get_data(ticker)
    if df.empty:
        st.error("ไม่สามารถดึงข้อมูลสำหรับหุ้นที่เลือกได้")
    else:
        data = get_stock_info(ticker, ng_pe, multiplier, margin)
        if data:
            max_drawdown = calculate_max_drawdown(df) or 0
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="EPS(฿)", value=data["eps"])
            with col2:
                st.metric(label="อัตรการเติบโตระยะยาว (5 ปี)", value=data["growth_rate"])
            with col3:
                st.metric(label="ผลตอบแทนของบริษัท AAA", value=data["current_yield"])
            
            st.markdown("---")
            intrinsic_value = (data["eps"] * (data["ng_pe"] + data["multiplier"] * data["growth_rate"]) * 4.486) / data["current_yield"]
            intrinsic_value = round(intrinsic_value, 2)
            stock_price = round(data["current_price"], 2)
            accept_price = round((1 - data["margin"]) * intrinsic_value, 2)
            
            col4, col5, col6 = st.columns(3)
            with col4:
                st.subheader('ราคาหุ้นปัจจุบัน(฿)')
                st.subheader(f"**:blue[{stock_price}]**")
            with col5:
                st.subheader('มูลค่าหุ้นที่แท้จริง(฿)')
                st.subheader(f"**:blue[{intrinsic_value}]**")
            with col6:
                st.subheader('ราคาที่ยอมรับได้(฿)')
                st.subheader(f"**:blue[{accept_price}]**")
            
            st.markdown("---")
            st.subheader(f"Max Drawdown: **:red[{round(max_drawdown, 2)}%]**")
