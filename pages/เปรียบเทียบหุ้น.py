import streamlit as st
from datetime import date
import yfinance as yf 
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objects as go
import pandas as pd



st.title("Stock Prediction App")

stocks = ("ADVANC.BK", "AOT.BK", "AWC.BK", "BANPU.BK", "BBL.BK", "BDMS.BK", "BEM.BK", "BGRIM.BK", "BH.BK", "BTS.BK",
    "CBG.BK", "CENTEL.BK", "COM7.BK", "CPALL.BK", "CPF.BK", "CPN.BK", "CRC.BK", "DELTA.BK", "EA.BK", "EGCO.BK",
    "GLOBAL.BK", "GPSC.BK", "GULF.BK", "HMPRO.BK", "INTUCH.BK", "IVL.BK", "KBANK.BK", "KCE.BK", "KTB.BK", "KTC.BK",
    "LH.BK", "MINT.BK", "MTC.BK", "OR.BK", "OSP.BK", "PTT.BK", "PTTEP.BK", "PTTGC.BK", "RATCH.BK", "SAWAD.BK",
    "SCB.BK", "SCC.BK", "SCGP.BK", "TISCO.BK", "TOP.BK", "TTB.BK", "TU.BK", "WHA.BK")

dropdown= st.multiselect('เลือกหุ้นที่ต้องการเปรียบเทียบ',options=stocks)

start = st.date_input('วันที่เริ่ม',value= pd.to_datetime('2019-01-01'))
end = st.date_input('วันที่ล่าสุด',value= pd.to_datetime('today'))

def relativereturn(df):
    rel = df.pct_change()
    cumret = (1+rel).cumprod()-1
    cumret = cumret.fillna(0)
    return cumret

if len(dropdown) > 0:
    df = relativereturn(yf.download(dropdown,start,end,)['Adj Close'],progress=False)
    st.line_chart(df)


    
