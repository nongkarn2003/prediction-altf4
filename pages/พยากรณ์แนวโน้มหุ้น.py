import streamlit as st
from datetime import date
import yfinance as yf 
from prophet import Prophet
import plotly.graph_objs as go
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Custom styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Mitr:wght@200;300;400;500;600;700&display=swap');
    * {font-family: 'Mitr', sans-serif;}
    .st-emotion-cache-1dp5vir {background-image: linear-gradient(90deg, rgb(0 0 0), rgb(0 0 0));}
    </style>
""", unsafe_allow_html=True)

# Constants
START = "2019-01-01"
TODAY = date.today().strftime("%Y-%m-%d")
STOCKS = ('ADVANC.BK', 'AOT.BK', 'AWC.BK', 'BANPU.BK', 'BBL.BK', 'BDMS.BK', 'BEM.BK', 
          'BGRIM.BK', 'BH.BK', 'BTS.BK', 'CBG.BK', 'CENTEL.BK', 'COM7.BK', 'CPALL.BK', 
          'CPF.BK', 'CPN.BK', 'CRC.BK', 'DELTA.BK', 'EA.BK', 'EGCO.BK', 'GLOBAL.BK', 
          'GPSC.BK', 'GULF.BK', 'HMPRO.BK', 'INTUCH.BK', 'IVL.BK', 'KBANK.BK', 'KCE.BK', 
          'KTB.BK', 'KTC.BK', 'LH.BK', 'MINT.BK', 'MTC.BK', 'OR.BK', 'OSP.BK', 'PTT.BK', 
          'PTTEP.BK', 'PTTGC.BK', 'RATCH.BK', 'SAWAD.BK', 'SCB.BK', 'SCC.BK', 'SCGP.BK', 
          'TISCO.BK', 'TLI.BK', 'TOP.BK', 'TRUE.BK', 'TTB.BK', 'TU.BK', 'WHA.BK')

@st.cache_data
def load_data(ticker):
    """Load and cache stock data"""
    data = yf.download(ticker, START, TODAY, progress=False)
    return data.reset_index()

def plot_stock_prices(data):
    """Plot stock opening and closing prices"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name='ราคาเปิด'))
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name='ราคาปิด'))
    fig.update_layout(
        title_text="ราคาหุ้น",
        xaxis_rangeslider_visible=True,
        height=500
    )
    return fig

def create_forecast(data, period):
    """Create and train Prophet model for forecasting"""
    df_train = data[['Date', 'Close']].rename(columns={"Date": "ds", "Close": "y"})
    model = Prophet()
    model.fit(df_train)
    future = model.make_future_dataframe(periods=period)
    forecast = model.predict(future)
    return model, forecast, df_train

def calculate_metrics(actual, predicted):
    """Calculate forecast accuracy metrics"""
    mae = mean_absolute_error(actual, predicted)
    mse = mean_squared_error(actual, predicted)
    rmse = np.sqrt(mse)
    return mae, mse, rmse

def main():
    st.title("พยากรณ์แนวโน้มหุ้น")
    
    # User inputs
    selected_stocks = st.selectbox("เลือกหุ้น", STOCKS)
    n_years = st.slider("จํานวนปีที่ต้องการพยากรณ์", 1, 4)
    period = n_years * 365
    
    # Load data
    with st.spinner("กําลังโหลดข้อมูล...."):
        data = load_data(selected_stocks)
    st.success("โหลดข้อมูล...สําเร็จ")
    
    # Plot raw data
    st.plotly_chart(plot_stock_prices(data))
    
    # Create forecast
    model, forecast, df_train = create_forecast(data, period)
    
    # Display forecast results
    st.subheader('ข้อมูลการพยากรณ์')
    st.dataframe(forecast.tail())
    
    # Plot forecast
    fig_forecast = model.plot(forecast)
    st.pyplot(fig_forecast)
    
    # Plot components
    fig_components = model.plot_components(forecast)
    st.pyplot(fig_components)
    
    # Calculate and display metrics
    actual = df_train['y'].values[-period:]
    predicted = forecast['yhat'].values[-period:]
    mae, mse, rmse = calculate_metrics(actual, predicted)
    
    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
    with metrics_col1:
        st.metric("MAE", f"{mae:.2f}")
    with metrics_col2:
        st.metric("MSE", f"{mse:.2f}")
    with metrics_col3:
        st.metric("RMSE", f"{rmse:.2f}")

if __name__ == "__main__":
    main()
