import streamlit as st
from datetime import date
import yfinance as yf
from prophet import Prophet
from prophet.plot import plot_plotly
import plotly.graph_objs as go
import streamlit.components.v1 as components
import numpy as np
import pandas as pd

# CSS Styling
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

# Constants
START = "2019-01-01"
TODAY = date.today().strftime("%Y-%m-%d")

st.title("พยากรณ์แนวโน้มหุ้น")

# Stock list
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
    try:
        data = yf.download(ticker, START, TODAY, progress=False)
        if data.empty:
            st.error(f"ไม่สามารถโหลดข้อมูลสำหรับ {ticker} ได้")
            return None
        data.reset_index(inplace=True)
        return data
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {str(e)}")
        return None

def plot_raw_data(data):
    if data is None or data.empty:
        st.error("ไม่มีข้อมูลสำหรับการแสดงกราф")
        return
    
    try:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name='ราคาเปิด'))
        fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name='ราคาปิด'))
        fig.layout.update(title_text="ราคาหุ้น", xaxis_rangeslider_visible=True)
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการแสดงกราฟ: {str(e)}")

def main():
    # Load data
    data_load_state = st.text("กําลังโหลดข้อมูล....")
    data = load_data(selected_stocks)
    
    if data is None:
        data_load_state.text("โหลดข้อมูลไม่สำเร็จ")
        return
    
    data_load_state.text("โหลดข้อมูล...สําเร็จ")
    
    # Plot raw data
    plot_raw_data(data)
    
    # Check if data has required columns
    if 'Close' not in data.columns or 'Date' not in data.columns:
        st.error("ข้อมูลไม่ครบถ้วน ไม่มีคอลัมน์ที่จำเป็น")
        return
    
    # Check if data is sufficient
    if len(data) < 30:
        st.error("ข้อมูลไม่เพียงพอสำหรับการพยากরณ์")
        return
    
    try:
        # Prepare data for Prophet
        df_train = data[['Date', 'Close']].copy()
        df_train.columns = ['ds', 'y']
        
        # Clean data - remove NaN values
        df_train = df_train.dropna()
        
        # Ensure data types are correct
        df_train['y'] = pd.to_numeric(df_train['y'], errors='coerce')
        df_train = df_train.dropna()  # Remove any remaining NaN after conversion
        
        if len(df_train) < 10:
            st.error("ข้อมูลที่สะอาดแล้วไม่เพียงพอสำหรับการพยากรณ์")
            return
        
        # Create and fit Prophet model
        m = Prophet()
        m.fit(df_train)
        
        # Make future predictions
        future = m.make_future_dataframe(periods=period)
        forecast = m.predict(future)
        
        # Display forecast data
        st.subheader('ข้อมูลการพยากรณ์')
        if not forecast.empty:
            st.write(forecast.tail())
        else:
            st.error("ไม่สามารถสร้างการพยากรณ์ได้")
            return
        
        # Plot forecast
        try:
            fig1 = plot_plotly(m, forecast)
            if fig1:
                components.html(fig1.to_html(full_html=False), height=600)
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการแสดงกราฟพยากรณ์: {str(e)}")
        
        # Plot components
        try:
            fig2 = m.plot_components(forecast)
            st.pyplot(fig2)
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการแสดงกราฟส่วนประกอบ: {str(e)}")
        
        # Calculate metrics
        try:
            available_period = min(period, len(df_train))
            if available_period > 0:
                actual_values = df_train['y'].values[-available_period:]
                forecast_values = forecast['yhat'].values[-available_period:]
                
                # Check if arrays have the same length
                min_length = min(len(actual_values), len(forecast_values))
                actual_values = actual_values[-min_length:]
                forecast_values = forecast_values[-min_length:]
                
                if len(actual_values) > 0 and len(forecast_values) > 0:
                    mae = np.mean(np.abs(actual_values - forecast_values))
                    mse = np.mean((actual_values - forecast_values) ** 2)
                    rmse = np.sqrt(mse)
                    
                    st.subheader("ตัวชี้วัดความแม่นยำ")
                    st.write(f"Mean Absolute Error (MAE): {mae:.4f}")
                    st.write(f"Mean Squared Error (MSE): {mse:.4f}")
                    st.write(f"Root Mean Squared Error (RMSE): {rmse:.4f}")
                else:
                    st.warning("ไม่สามารถคำนวณตัวชี้วัดความแม่นยำได้")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการคำนวณตัวชี้วัด: {str(e)}")
            
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการประมวลผล: {str(e)}")

# Run the main function
if __name__ == "__main__":
    main()
