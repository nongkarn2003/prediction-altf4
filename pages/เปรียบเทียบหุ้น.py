import streamlit as st
from datetime import date
import yfinance as yf 
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objects as go
import pandas as pd
import plotly.express as px
import numpy as np

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

st.title("เปรียบเทียบหุ้น")

# Stock list
stocks = ('^SET.BK','ADVANC.BK', 'AOT.BK', 'AWC.BK', 'BANPU.BK', 'BBL.BK', 'BDMS.BK', 'BEM.BK', 
         'BGRIM.BK', 'BH.BK', 'BTS.BK', 'CBG.BK', 'CENTEL.BK', 'COM7.BK', 'CPALL.BK', 'CPF.BK', 
         'CPN.BK', 'CRC.BK', 'DELTA.BK', 'EA.BK', 'EGCO.BK', 'GLOBAL.BK', 'GPSC.BK', 'GULF.BK', 
         'HMPRO.BK', 'INTUCH.BK', 'IVL.BK', 'KBANK.BK', 'KCE.BK', 'KTB.BK', 'KTC.BK', 'LH.BK', 
         'MINT.BK', 'MTC.BK', 'OR.BK', 'OSP.BK', 'PTT.BK', 'PTTEP.BK', 'PTTGC.BK', 'RATCH.BK', 
         'SAWAD.BK', 'SCB.BK', 'SCC.BK', 'SCGP.BK', 'TISCO.BK', 'TLI.BK', 'TOP.BK', 'TRUE.BK', 
         'TTB.BK', 'TU.BK', 'WHA.BK')

# User inputs
dropdown = st.multiselect('เลือกหุ้นที่ต้องการเปรียบเทียบ', options=stocks)
start = st.date_input('วันที่เริ่ม', value=pd.to_datetime('2019-01-01'))
end = st.date_input('วันที่ล่าสุด', value=pd.to_datetime('today'))

def relativereturn(df):
    """Calculate relative return with proper error handling"""
    try:
        if df is None or df.empty:
            return pd.DataFrame()
        
        # Convert to DataFrame if Series
        if isinstance(df, pd.Series):
            df = df.to_frame()
        
        # Calculate percentage change
        rel = df.pct_change()
        
        # Calculate cumulative returns
        cumret = (1 + rel).cumprod() - 1
        
        # Fill NaN values with 0
        cumret = cumret.fillna(0)
        
        return cumret
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการคำนวณผลตอบแทน: {str(e)}")
        return pd.DataFrame()

def safe_download_data(tickers, start_date, end_date):
    """Safely download stock data with error handling"""
    try:
        if not tickers:
            return None
        
        # Download data
        data = yf.download(tickers, start=start_date, end=end_date, progress=False)
        
        if data.empty:
            st.warning("ไม่พบข้อมูลสำหรับหุ้นที่เลือก")
            return None
        
        # Handle multi-level columns
        if isinstance(data.columns, pd.MultiIndex):
            if 'Adj Close' in data.columns.levels[0]:
                data = data['Adj Close']
            elif 'Close' in data.columns.levels[0]:
                data = data['Close']
            else:
                st.error("ไม่พบข้อมูลราคาปิด")
                return None
        
        return data
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการดาวน์โหลดข้อมูล: {str(e)}")
        return None

def get_financial_ratios(tickers):
    """Get financial ratios with proper error handling"""
    ratios = {}
    
    if not tickers:
        return pd.DataFrame()
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, ticker in enumerate(tickers):
        try:
            status_text.text(f'กำลังดาวน์โหลดข้อมูล {ticker}...')
            progress_bar.progress((i + 1) / len(tickers))
            
            stock_info = yf.Ticker(ticker).info
            
            # Safely get values with default fallback
            def safe_get(key, default='N/A'):
                value = stock_info.get(key, default)
                # Convert to float if possible, otherwise keep as string
                if isinstance(value, (int, float)) and not pd.isna(value):
                    return round(value, 4) if value != 'N/A' else 'N/A'
                return 'N/A'
            
            ratios[ticker] = {
                'Price/Book': safe_get('priceToBook'),
                'Price/Earnings': safe_get('trailingPE'),
                'Price/Sales': safe_get('priceToSalesTrailingTwelveMonths'),
                'Price/Cash Flow': safe_get('priceToOperatingCashFlowsTrailingTwelveMonths'),
                'Debt/Equity': safe_get('debtToEquity'),
                'Return on Equity': safe_get('returnOnEquity'),
                'Return on Assets': safe_get('returnOnAssets'),
                'Operating Margin': safe_get('operatingMargin'),
                'Profit Margin': safe_get('profitMargins'),
                'Current Ratio': safe_get('currentRatio'),
                'Quick Ratio': safe_get('quickRatio'),
            }
            
        except Exception as e:
            st.warning(f"ไม่สามารถดาวน์โหลดข้อมูลสำหรับ {ticker}: {str(e)}")
            ratios[ticker] = {key: 'N/A' for key in [
                'Price/Book', 'Price/Earnings', 'Price/Sales', 'Price/Cash Flow',
                'Debt/Equity', 'Return on Equity', 'Return on Assets',
                'Operating Margin', 'Profit Margin', 'Current Ratio', 'Quick Ratio'
            ]}
    
    progress_bar.empty()
    status_text.empty()
    
    return pd.DataFrame.from_dict(ratios, orient='index')

def create_ratio_chart(ratios_df, ratio_col):
    """Create bar chart for financial ratios with error handling"""
    try:
        if ratios_df.empty or ratio_col not in ratios_df.columns:
            st.error("ไม่พบข้อมูลสำหรับสัดส่วนการเงินที่เลือก")
            return
        
        # Filter out 'N/A' values and convert to numeric
        chart_data = ratios_df[ratio_col].copy()
        
        # Convert to numeric, replacing 'N/A' with NaN
        numeric_data = pd.to_numeric(chart_data, errors='coerce')
        
        # Remove NaN values
        numeric_data = numeric_data.dropna()
        
        if numeric_data.empty:
            st.warning("ไม่มีข้อมูลที่สามารถแสดงในกราฟได้")
            return
        
        # Create bar chart
        fig = px.bar(
            x=numeric_data.index, 
            y=numeric_data.values,
            title=f'{ratio_col}',
            labels={'x': 'หุ้น', 'y': ratio_col}
        )
        
        fig.update_layout(
            xaxis_title='หุ้น',
            yaxis_title=ratio_col,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการสร้างกราฟ: {str(e)}")

def main():
    """Main function to run the app"""
    
    # Stock price comparison
    if len(dropdown) > 0:
        st.subheader("เปรียบเทียบผลตอบแทนหุ้น")
        
        # Download and process data
        with st.spinner('กำลังดาวน์โหลดข้อมูลราคาหุ้น...'):
            raw_data = safe_download_data(dropdown, start, end)
        
        if raw_data is not None:
            # Calculate relative returns
            df = relativereturn(raw_data)
            
            if not df.empty:
                # Display line chart
                st.line_chart(df)
                
                # Show summary statistics
                st.subheader("สถิติสรุป")
                summary_stats = df.describe()
                st.dataframe(summary_stats)
            else:
                st.error("ไม่สามารถคำนวณผลตอบแทนได้")
    
    # Financial ratios comparison
    if len(dropdown) > 0:
        st.subheader("เปรียบเทียบสัดส่วนการเงิน")
        
        with st.spinner('กำลังดาวน์โหลดข้อมูลการเงิน...'):
            ratios_df = get_financial_ratios(dropdown)
        
        if not ratios_df.empty:
            st.subheader('สัดส่วนการเงิน')
            
            # Display ratios table
            st.dataframe(ratios_df)
            
            # Select ratio for chart
            ratio_col = st.selectbox('เลือกสัดส่วนการเงินสำหรับกราฟ', list(ratios_df.columns))
            
            if ratio_col:
                create_ratio_chart(ratios_df, ratio_col)
        else:
            st.warning("ไม่สามารถดาวน์โหลดข้อมูลการเงินได้")
    
    # Instructions for users
    if len(dropdown) == 0:
        st.info("กรุณาเลือกหุ้นที่ต้องการเปรียบเทียบ")
        st.markdown("""
        ### วิธีใช้งาน:
        1. เลือกหุ้นที่ต้องการเปรียบเทียบจากรายการ
        2. กำหนดช่วงเวลาที่ต้องการ
        3. ดูกราฟเปรียบเทียบผลตอบแทนและสัดส่วนการเงิน
        """)

# Run the application
if __name__ == "__main__":
    main()
