import streamlit as st
from datetime import date
import yfinance as yf
from prophet import Prophet
from prophet.plot import plot_plotly
import plotly.graph_objs as go
import streamlit.components.v1 as components
import numpy as np

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

START = "2019-01-01"
TODAY = date.today().strftime("%Y-%m-%d")

st.title("พยากรณ์แนวโน้มหุ้น")

stocks = ('ADVANC.BK', 'AOT.BK', 'AWC.BK', 'BANPU.BK', 'BBL.BK', 'BDMS.BK', 'BEM.BK', 
         'BGRIM.BK', 'BH.BK', 'BTS.BK', 'CBG.BK', 'CENTEL.BK', 'COM7.BK', 'CPALL.BK', 
         'CPF.BK', 'CPN.BK', 'CRC.BK', 'DELTA.BK', 'EA.BK', 'EGCO.BK', 'GLOBAL.BK', 
         'GPSC.BK', 'GULF.BK', 'HMPRO.BK', 'INTUCH.BK', 'IVL.BK', 'KBANK.BK', 'KCE.BK', 
         'KTB.BK', 'KTC.BK', 'LH.BK', 'MINT.BK', 'MTC.BK', 'OR.BK', 'OSP.BK', 'PTT.BK', 
         'PTTEP.BK', 'PTTGC.BK', 'RATCH.BK', 'SAWAD.BK', 'SCB.BK', 'SCC.BK', 'SCGP.BK', 
         'TISCO.BK', 'TLI.BK', 'TOP.BK', 'TRUE.BK', 'TTB.BK', 'TU.BK', 'WHA.BK')

selected_stocks = st.selectbox("เลือกหุ้น", stocks)
n_years = st.slider("จํานวนปีที่ต้องการพยากรณ์", 1, 4)
period = n_years * 365

@st.cache_data
def load_data(ticker):
    data = yf.download(ticker, START, TODAY, progress=False)
    data.reset_index(inplace=True)
    return data

data_load_state = st.text("กําลังโหลดข้อมูล....")
data = load_data(selected_stocks)
data_load_state.text("โหลดข้อมูล...สําเร็จ")

def plot_raw_data():
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name='ราคาเปิด'))
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name='ราคาปิด'))
    fig.layout.update(title_text="ราคาหุ้น", xaxis_rangeslider_visible=True)
    st.plotly_chart(fig)

plot_raw_data()

df_train = data[['Date', 'Close']]
df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})
m = Prophet()
m.fit(df_train)
future = m.make_future_dataframe(periods=period)
forecast = m.predict(future)

st.subheader('ข้อมูลการพยากรณ์')
st.write(forecast.tail())

fig1 = plot_plotly(m, forecast)
components.html(fig1.to_html(full_html=False), height=600)

fig2 = m.plot_components(forecast)
st.pyplot(fig2)

actual_values = df_train['y'].values[-period:]
forecast_values = forecast['yhat'].values[-period:]

mae = np.mean(np.abs(actual_values - forecast_values))
st.write("Mean Absolute Error (MAE):", mae)

mse = np.mean((actual_values - forecast_values) ** 2)
st.write("Mean Squared Error (MSE):", mse)

rmse = np.sqrt(mse)
st.write("Root Mean Squared Error (RMSE):", rmse)
