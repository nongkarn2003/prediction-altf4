import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Configure Streamlit page
st.set_page_config(
    page_title="สกรีนหุ้น",
    page_icon="📈",
    layout="wide"
)

# CSS Styling
streamlit_style = """
<style>
@import url(https://fonts.googleapis.com/css2?family=Mitr:wght@200;300;400;500;600;700&display=swap);
* {
    font-family: 'Mitr', sans-serif;
}
</style>
"""
st.markdown(streamlit_style, unsafe_allow_html=True)

# List of stock tickers
stocks = ["ADVANC.BK", "AOT.BK", "AWC.BK", "BANPU.BK", "BBL.BK", "BDMS.BK", "BEM.BK", "BGRIM.BK", "BH.BK", "BTS.BK",
          "CBG.BK", "CENTEL.BK", "COM7.BK", "CPALL.BK", "CPF.BK", "CPN.BK", "CRC.BK", "DELTA.BK", "EA.BK", "EGCO.BK",
          "GLOBAL.BK", "GPSC.BK", "GULF.BK", "HMPRO.BK", "INTUCH.BK", "IVL.BK", "KBANK.BK", "KCE.BK", "KTB.BK", "KTC.BK",
          "LH.BK", "MINT.BK", "MTC.BK", "OR.BK", "OSP.BK", "PTT.BK", "PTTEP.BK", "PTTGC.BK", "RATCH.BK", "SAWAD.BK",
          "SCB.BK", "SCC.BK", "SCGP.BK", "TISCO.BK", "TLI.BK", "TOP.BK", "TRUE.BK", "TTB.BK", "TU.BK", "WHA.BK"]

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_stock_data(ticker):
    """Get stock data with proper error handling and retry logic"""
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Validate that we got actual data
            if not info or len(info) < 10:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    return create_empty_stock_data(ticker)
            
            # Safely extract data with proper type conversion
            def safe_get_float(key, default=None):
                value = info.get(key, default)
                if value is None or pd.isna(value):
                    return None
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return None
            
            return {
                "Ticker": ticker,
                "Company Name": info.get('longName', ticker),
                "PE Ratio": safe_get_float('trailingPE'),
                "PB Ratio": safe_get_float('priceToBook'),
                "Debt to Equity": safe_get_float('debtToEquity'),
                "ROE": safe_get_float('returnOnEquity'),
                "ROA": safe_get_float('returnOnAssets'),
                "Current Price": safe_get_float('currentPrice'),
                "Market Cap": safe_get_float('marketCap'),
                "Sector": info.get('sector', 'N/A')
            }
            
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                continue
            else:
                st.warning(f"ไม่สามารถดาวน์โหลดข้อมูลสำหรับ {ticker}: {str(e)}")
                return create_empty_stock_data(ticker)

def create_empty_stock_data(ticker):
    """Create empty stock data structure"""
    return {
        "Ticker": ticker,
        "Company Name": "N/A",
        "PE Ratio": None,
        "PB Ratio": None,
        "Debt to Equity": None,
        "ROE": None,
        "ROA": None,
        "Current Price": None,
        "Market Cap": None,
        "Sector": "N/A"
    }

def load_all_stock_data(stock_list):
    """Load all stock data with progress bar and multithreading"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    data = []
    
    # Use ThreadPoolExecutor for concurrent downloads
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Submit all tasks
        future_to_stock = {executor.submit(get_stock_data, stock): stock for stock in stock_list}
        
        # Collect results as they complete
        completed = 0
        for future in as_completed(future_to_stock):
            stock = future_to_stock[future]
            try:
                result = future.result()
                if result:
                    data.append(result)
            except Exception as e:
                st.warning(f"Error processing {stock}: {str(e)}")
                data.append(create_empty_stock_data(stock))
            
            completed += 1
            progress = completed / len(stock_list)
            progress_bar.progress(progress)
            status_text.text(f'กำลังดาวน์โหลดข้อมูล... {completed}/{len(stock_list)}')
    
    progress_bar.empty()
    status_text.empty()
    return data

def apply_filters(df, filters):
    """Apply filters to dataframe with proper validation"""
    filtered_df = df.copy()
    
    # Only apply filters if the filter is active and has valid data
    if filters['pe_active'] and filters['pe_ratio'] is not None:
        mask = (df['PE Ratio'].notna()) & (df['PE Ratio'] <= filters['pe_ratio'])
        filtered_df = filtered_df[mask]
    
    if filters['pb_active'] and filters['pb_ratio'] is not None:
        mask = (df['PB Ratio'].notna()) & (df['PB Ratio'] <= filters['pb_ratio'])
        filtered_df = filtered_df[mask]
    
    if filters['de_active'] and filters['de_ratio'] is not None:
        mask = (df['Debt to Equity'].notna()) & (df['Debt to Equity'] <= filters['de_ratio'])
        filtered_df = filtered_df[mask]
    
    if filters['roe_active'] and filters['roe'] is not None:
        mask = (df['ROE'].notna()) & (df['ROE'] >= (filters['roe'] / 100))
        filtered_df = filtered_df[mask]
    
    if filters['roa_active'] and filters['roa'] is not None:
        mask = (df['ROA'].notna()) & (df['ROA'] >= (filters['roa'] / 100))
        filtered_df = filtered_df[mask]
    
    return filtered_df

def format_dataframe(df):
    """Format dataframe for display"""
    if df.empty:
        return df
    
    # Create a copy to avoid modifying original
    display_df = df.copy()
    
    # Format numeric columns
    format_dict = {}
    if 'PE Ratio' in display_df.columns:
        format_dict['PE Ratio'] = "{:.2f}"
    if 'PB Ratio' in display_df.columns:
        format_dict['PB Ratio'] = "{:.2f}"
    if 'Debt to Equity' in display_df.columns:
        format_dict['Debt to Equity'] = "{:.2f}"
    if 'ROE' in display_df.columns:
        format_dict['ROE'] = "{:.2%}"
    if 'ROA' in display_df.columns:
        format_dict['ROA'] = "{:.2%}"
    if 'Current Price' in display_df.columns:
        format_dict['Current Price'] = "{:.2f}"
    if 'Market Cap' in display_df.columns:
        # Format market cap in billions
        display_df['Market Cap (B)'] = display_df['Market Cap'].apply(
            lambda x: f"{x/1e9:.2f}" if pd.notna(x) and x > 0 else "N/A"
        )
        display_df = display_df.drop('Market Cap', axis=1)
    
    return display_df.style.format(format_dict)

def main():
    """Main application function"""
    st.title("📈 สกรีนหุ้น")
    st.markdown("---")
    
    # Sidebar for filters
    with st.sidebar:
        st.header("⚙️ ตัวกรอง")
        
        # Filter selection
        st.subheader("เลือกเกณฑ์การกรอง")
        
        filters = {}
        
        # PE Ratio filter
        filters['pe_active'] = st.checkbox("PE Ratio", value=True)
        if filters['pe_active']:
            filters['pe_ratio'] = st.number_input(
                "PE Ratio (มากสุด)", 
                min_value=0.0, 
                value=25.0, 
                step=0.1,
                help="ค่า PE Ratio ที่ยอมรับได้สูงสุด"
            )
        else:
            filters['pe_ratio'] = None
        
        # PB Ratio filter
        filters['pb_active'] = st.checkbox("PB Ratio", value=True)
        if filters['pb_active']:
            filters['pb_ratio'] = st.number_input(
                "PB Ratio (มากสุด)", 
                min_value=0.0, 
                value=3.0, 
                step=0.1,
                help="ค่า PB Ratio ที่ยอมรับได้สูงสุด"
            )
        else:
            filters['pb_ratio'] = None
        
        # Debt to Equity filter
        filters['de_active'] = st.checkbox("Debt to Equity", value=True)
        if filters['de_active']:
            filters['de_ratio'] = st.number_input(
                "Debt to Equity (มากสุด)", 
                min_value=0.0, 
                value=2.0, 
                step=0.1,
                help="อัตราส่วนหนี้สินต่อทุนที่ยอมรับได้สูงสุด"
            )
        else:
            filters['de_ratio'] = None
        
        # ROE filter
        filters['roe_active'] = st.checkbox("ROE", value=True)
        if filters['roe_active']:
            filters['roe'] = st.number_input(
                "ROE ขั้นต่ำ (%)", 
                min_value=0.0, 
                value=10.0, 
                step=0.1,
                help="ผลตอบแทนต่อทุนขั้นต่ำ"
            )
        else:
            filters['roe'] = None
        
        # ROA filter
        filters['roa_active'] = st.checkbox("ROA", value=True)
        if filters['roa_active']:
            filters['roa'] = st.number_input(
                "ROA ขั้นต่ำ (%)", 
                min_value=0.0, 
                value=5.0, 
                step=0.1,
                help="ผลตอบแทนต่อสินทรัพย์ขั้นต่ำ"
            )
        else:
            filters['roa'] = None
        
        st.markdown("---")
        refresh_button = st.button("🔄 รีเฟรชข้อมูล", use_container_width=True)
    
    # Main content area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("📊 ผลการสกรีน")
    
    with col2:
        if st.button("📥 ดาวน์โหลดข้อมูล", use_container_width=True):
            st.info("กรุณารอจนข้อมูลโหลดเสร็จแล้วกดดาวน์โหลดใหม่")
    
    # Load data
    if 'stock_data' not in st.session_state or refresh_button:
        with st.spinner('กำลังดาวน์โหลดข้อมูลหุ้น...'):
            stock_data = load_all_stock_data(stocks)
            st.session_state.stock_data = stock_data
            st.success(f"ดาวน์โหลดข้อมูลเสร็จสิ้น! ทั้งหมด {len(stock_data)} หุ้น")
    else:
        stock_data = st.session_state.stock_data
    
    # Create DataFrame
    df = pd.DataFrame(stock_data)
    
    if df.empty:
        st.error("ไม่สามารถดาวน์โหลดข้อมูลหุ้นได้")
        return
    
    # Apply filters
    filtered_df = apply_filters(df, filters)
    
    # Display results
    st.markdown(f"**จำนวนหุ้นที่ผ่านการกรอง: {len(filtered_df)} จาก {len(df)} หุ้น**")
    
    if filtered_df.empty:
        st.warning("ไม่มีหุ้นที่ผ่านเกณฑ์การกรองที่กำหนด กรุณาปรับเกณฑ์ใหม่")
    else:
        # Display formatted table
        formatted_df = format_dataframe(filtered_df)
        st.dataframe(formatted_df, height=600, use_container_width=True)
        
        # Download button
        csv_data = filtered_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 ดาวน์โหลดผลการสกรีน (CSV)",
            data=csv_data,
            file_name=f'screened_stocks_{pd.Timestamp.now().strftime("%Y%m%d_%H%M")}.csv',
            mime='text/csv',
            use_container_width=True
        )
        
        # Summary statistics
        with st.expander("📈 สถิติสรุป"):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                avg_pe = filtered_df['PE Ratio'].mean()
                st.metric("PE เฉลี่ย", f"{avg_pe:.2f}" if pd.notna(avg_pe) else "N/A")
            
            with col2:
                avg_pb = filtered_df['PB Ratio'].mean()
                st.metric("PB เฉลี่ย", f"{avg_pb:.2f}" if pd.notna(avg_pb) else "N/A")
            
            with col3:
                avg_roe = filtered_df['ROE'].mean()
                st.metric("ROE เฉลี่ย", f"{avg_roe:.2%}" if pd.notna(avg_roe) else "N/A")
            
            with col4:
                avg_roa = filtered_df['ROA'].mean()
                st.metric("ROA เฉลี่ย", f"{avg_roa:.2%}" if pd.notna(avg_roa) else "N/A")

# Run the application
if __name__ == "__main__":
    main()
