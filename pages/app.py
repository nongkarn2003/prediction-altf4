import streamlit as st
from datetime import date
import yfinance as yf 
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objects as go


# เปลี่ยนแปลงพอร์ตเซิร์ฟเวอร์เมื่อมีการรัน Streamlit app
port = 8502
START = "2019-01-01"
TODAY = date.today().strftime("%Y-%m-%d")

st.title("Stock Prediction App")

stocks = ("ADVANC.bk", "AOT.bk", "AWC.bk", "BANPU.bk", "BBL.bk", "BDMS.bk", "BEM.bk", "BGRIM.bk", "BH.bk", "BTS.bk",
    "CBG.bk", "CENTEL.bk", "COM7.bk", "CPALL.bk", "CPF.bk", "CPN.bk", "CRC.bk", "DELTA.bk", "EA.bk", "EGCO.bk",
    "GLOBAL.bk", "GPSC.bk", "GULF.bk", "HMPRO.bk", "INTUCH.bk", "IVL.bk", "KBANK.bk", "KCE.bk", "KTB.bk", "KTC.bk",
    "LH.bk", "MINT.bk", "MTC.bk", "OR.bk", "OSP.bk", "PTT.bk", "PTTEP.bk", "PTTGC.bk", "RATCH.bk", "SAWAD.bk",
    "SCB.bk", "SCC.bk", "SCGP.bk", "TISCO.bk", "TOP.bk", "TTB.bk", "TU.bk", "WHA.bk")

selected_stocks = st.selectbox("Select Symbol for prediction",stocks)

n_years = st.slider("Year of Prediction",1,4)
period = n_years * 365 

@st.cache_data
def load_data(ticker):
    data = yf.download(ticker,START,TODAY)
    data.reset_index(inplace=True)
    return data

data_load_state = st.text("Load data....")
data = load_data(selected_stocks)
data_load_state.text("Loading data...done")


def plot_raw_data():
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date'],y=data['Open'],name='stock_open'))
    fig.add_trace(go.Scatter(x=data['Date'],y=data['Close'],name='stock_close'))
    fig.layout.update(title_text="Time Series Data", xaxis_rangeslider_visible=True)
    st.plotly_chart(fig)

plot_raw_data()

#Forecasting
df_train = data[['Date','Close']]
df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})

m = Prophet()
m.fit(df_train)
future = m.make_future_dataframe(periods=period)
forecast = m.predict(future)

st.subheader('Forecast data')
st.write(forecast.tail())

st.write('forecast data')
fig1 = plot_plotly(m,forecast)
st.plotly_chart(fig1)

st.write('forecast components')
fig2 = m.plot_components(forecast)
st.write(fig2)
