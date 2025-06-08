import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_datareader as pdr
from datetime import datetime, timedelta

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

st.header("ประเมินมูลค่าหุ้น")
st.write('สูตรประเมินแบบ Benjamin Graham')
ticker = st.selectbox("เลือกหุ้น", stocks)
ng_pe = st.text_input('PE ที่ไม่มีการเติบโต', 8.5)
multiplier = st.text_input('ระยะการเติบโต', 2)
margin = st.text_input('ส่วนเผื่อราคา (%)', 35)

def get_current_price(ticker_data):
    """ฟังก์ชันสำหรับหาราคาปัจจุบันจากหลายแหล่ง"""
    quote = ticker_data.info
    
    # ลองหาราคาจากหลายฟิลด์
    price_fields = [
        "regularMarketPrice",
        "regularMarketPreviousClose", 
        "currentPrice",
        "ask",
        "bid",
        "previousClose"
    ]
    
    for field in price_fields:
        if field in quote and quote[field] is not None:
            try:
                price = float(quote[field])
                if price > 0:
                    return price
            except (ValueError, TypeError):
                continue
    
    # ถ้าไม่เจอราคาจาก info ให้ลองใช้ history
    try:
        hist = ticker_data.history(period="5d")
        if not hist.empty:
            return float(hist['Close'].iloc[-1])
    except Exception:
        pass
    
    return None

def get_eps(ticker_data):
    """ฟังก์ชันสำหรับหา EPS"""
    quote = ticker_data.info
    
    eps_fields = [
        "trailingEps",
        "forwardEps", 
        "eps"
    ]
    
    for field in eps_fields:
        if field in quote and quote[field] is not None:
            try:
                eps = float(quote[field])
                if eps != 0:
                    return eps
            except (ValueError, TypeError):
                continue
    
    return None

def get_growth_rate(ticker_data):
    """ฟังก์ชันสำหรับหาอัตราการเติบโต"""
    quote = ticker_data.info
    
    growth_fields = [
        "earningsGrowth",
        "earningsQuarterlyGrowth",
        "revenueGrowth"
    ]
    
    for field in growth_fields:
        if field in quote and quote[field] is not None:
            try:
                growth = float(quote[field])
                # แปลงเป็นเปอร์เซ็นต์ถ้าเป็นทศนิยม
                if abs(growth) <= 1:
                    growth = growth * 100
                return growth
            except (ValueError, TypeError):
                continue
    
    # ถ้าไม่เจอให้ใช้ค่าเริ่มต้น 5%
    return 5.0

def get_aaa_yield():
    """ฟังก์ชันสำหรับหาผลตอบแทนบอนด์ AAA"""
    try:
        # ลองใช้ 10-year Treasury rate แทน AAA
        treasury_df = pdr.get_data_fred('DGS10', start=datetime.now() - timedelta(days=30))
        if not treasury_df.empty:
            current_yield = treasury_df.dropna().iloc[-1][0]
            return float(current_yield)
    except Exception:
        pass
    
    try:
        # ลองใช้ AAA อีกครั้ง
        aaa_df = pdr.get_data_fred('AAA', start=datetime.now() - timedelta(days=30))
        if not aaa_df.empty:
            current_yield = aaa_df.dropna().iloc[-1][0]
            return float(current_yield)
    except Exception:
        pass
    
    # ถ้าไม่สามารถดึงข้อมูลได้ให้ใช้ค่าเริ่มต้น 4%
    return 4.0

def get_data(ticker, ng_pe, multiplier, margin):
    try:
        ticker_data = yf.Ticker(ticker)
        
        # ดึงราคาปัจจุบัน
        current_price = get_current_price(ticker_data)
        if current_price is None:
            st.error(f"ไม่สามารถดึงราคาปัจจุบันของ {ticker} ได้")
            return None
        
        # ดึง EPS
        eps = get_eps(ticker_data)
        if eps is None:
            st.warning(f"ไม่สามารถดึงข้อมูล EPS ของ {ticker} ได้ กรุณาใส่ค่าด้วยตนเอง")
            eps = st.number_input("กรุณาใส่ค่า EPS:", min_value=0.0, step=0.01)
            if eps == 0:
                return None
        
        # ดึงอัตราการเติบโต
        growth_rate = get_growth_rate(ticker_data)
        
        # ดึงผลตอบแทนบอนด์
        current_yield = get_aaa_yield()
        
        output = {
            "current_price": float(current_price),
            "eps": float(eps),
            "growth_rate": float(growth_rate),
            "current_yield": float(current_yield),
            "ng_pe": float(ng_pe),
            "multiplier": float(multiplier),
            "margin": float(margin)
        }
        return output
        
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {str(e)}")
        return None

if st.button('คํานวณ'):
    try:
        data = get_data(ticker, ng_pe, multiplier, margin)
        
        if data is not None:
            st.markdown("""---""")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="EPS(฿)", value=f"{data['eps']:.2f}")
            with col2:
                st.metric(label="อัตรการเติบโตระยะยาว (%)", value=f"{data['growth_rate']:.2f}")
            with col3:
                st.metric(label="ผลตอบแทนบอนด์อ้างอิง (%)", value=f"{data['current_yield']:.2f}")
            
            st.markdown("""---""")
            
            # คำนวณมูลค่าที่แท้จริง
            # ใช้สูตร Benjamin Graham: V = EPS × (8.5 + 2g) × 4.4 / Y
            # โดยที่ g = growth rate, Y = current yield
            growth_decimal = data["growth_rate"] / 100 if data["growth_rate"] > 1 else data["growth_rate"]
            yield_decimal = data["current_yield"] / 100 if data["current_yield"] > 1 else data["current_yield"]
            
            int_value = (data["eps"] * (data["ng_pe"] + data["multiplier"] * growth_decimal * 100) * 4.4) / data["current_yield"]
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
            
            # เพิ่มคำแนะนำ
            st.markdown("""---""")
            if stock_price <= accept_price:
                st.success(f"🟢 **แนะนำซื้อ**: ราคาปัจจุบัน ({stock_price} ฿) ต่ำกว่าราคาที่ยอมรับได้ ({accept_price} ฿)")
            elif stock_price <= int_value:
                st.warning(f"🟡 **พิจารณา**: ราคาปัจจุบัน ({stock_price} ฿) อยู่ระหว่างราคาที่ยอมรับได้และมูลค่าที่แท้จริง")
            else:
                st.error(f"🔴 **ไม่แนะนำ**: ราคาปัจจุบัน ({stock_price} ฿) สูงกว่ามูลค่าที่แท้จริง ({int_value} ฿)")
                
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการคำนวณ: {str(e)}")
else:
    st.text("")
