import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.title("Max Drawdown ของหุ้น")

# เลือกหุ้น
stocks = ('^SET.BK', 'ADVANC.BK', 'AOT.BK', 'AWC.BK', 'BANPU.BK', 'BBL.BK', 'BDMS.BK', 'BEM.BK', 'BGRIM.BK', 'BH.BK', 'BTS.BK', 'CBG.BK', 'CENTEL.BK', 'COM7.BK', 'CPALL.BK', 'CPF.BK', 'CPN.BK', 'CRC.BK', 'DELTA.BK', 'EA.BK', 'EGCO.BK', 'GLOBAL.BK', 'GPSC.BK', 'GULF.BK', 'HMPRO.BK', 'INTUCH.BK', 'IVL.BK', 'KBANK.BK', 'KCE.BK', 'KTB.BK', 'KTC.BK', 'LH.BK', 'MINT.BK', 'MTC.BK', 'OR.BK', 'OSP.BK', 'PTT.BK', 'PTTEP.BK', 'PTTGC.BK', 'RATCH.BK', 'SAWAD.BK', 'SCB.BK', 'SCC.BK', 'SCGP.BK', 'TISCO.BK', 'TLI.BK', 'TOP.BK', 'TRUE.BK', 'TTB.BK', 'TU.BK', 'WHA.BK')

dropdown = st.selectbox('เลือกหุ้นที่ต้องการแสดง Max Drawdown', options=stocks)

# เลือกช่วงเวลาย้อนหลัง
start = st.date_input('วันที่เริ่ม', value=pd.to_datetime('2019-01-01'))
end = st.date_input('วันที่ล่าสุด', value=pd.to_datetime('today'))

def calculate_max_drawdown(df):
    """
    คำนวณ Max Drawdown จากข้อมูลราคา
    """
    peak = df.cummax()
    drawdown = (df - peak) / peak
    max_drawdown = drawdown.min()  # หา drawdown ต่ำสุด
    return max_drawdown * 100, drawdown  # Return both the percentage and the series

# ดึงข้อมูลราคาหุ้นย้อนหลัง
if dropdown:
    stock_data = yf.download(dropdown, start=start, end=end, progress=False)['Adj Close']
    
    # คำนวณ Max Drawdown
    max_drawdown, drawdown_series = calculate_max_drawdown(stock_data)
    
    # แสดงผล Max Drawdown
    st.write(f"Max Drawdown ของ {dropdown}: {round(max_drawdown, 2)}%")
    
    # สร้างกราฟการเปลี่ยนแปลงของ Drawdown
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=stock_data.index, y=drawdown_series * 100, mode='lines', name='Drawdown (%)'))
    fig.update_layout(title=f"Drawdown ของ {dropdown} ย้อนหลัง", xaxis_title="Date", yaxis_title="Drawdown (%)")
    
    # แสดงกราฟ
    st.plotly_chart(fig)
