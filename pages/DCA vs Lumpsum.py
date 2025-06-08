import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import date, timedelta, datetime
import warnings
warnings.filterwarnings('ignore')

# ===== CONFIGURATION =====
st.set_page_config(
    page_title="DCA vs Lump Sum Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== CUSTOM STYLES =====
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    
    .success-card {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    
    .warning-card {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 1rem;
        border-radius: 10px;
        color: #8b4513;
        margin: 1rem 0;
    }
    
    .info-box {
        background: #f8f9ff;
        border: 1px solid #e1e5fe;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# ===== DATA =====
THAI_STOCKS = {
    "SET 50": ["ADVANC.BK", "AOT.BK", "AWC.BK", "BANPU.BK", "BBL.BK", "BDMS.BK", 
               "BEM.BK", "BGRIM.BK", "BH.BK", "BTS.BK", "CBG.BK", "CENTEL.BK", 
               "COM7.BK", "CPALL.BK", "CPF.BK", "CPN.BK", "CRC.BK", "DELTA.BK", 
               "EA.BK", "EGCO.BK", "GLOBAL.BK", "GPSC.BK", "GULF.BK", "HMPRO.BK", 
               "INTUCH.BK", "IVL.BK", "KBANK.BK", "KCE.BK", "KTB.BK", "KTC.BK", 
               "LH.BK", "MINT.BK", "MTC.BK", "OR.BK", "OSP.BK", "PTT.BK", 
               "PTTEP.BK", "PTTGC.BK", "RATCH.BK", "SAWAD.BK", "SCB.BK", 
               "SCC.BK", "SCGP.BK", "TISCO.BK", "TOP.BK", "TTB.BK", "TU.BK", "WHA.BK"],
    "Popular ETFs": ["TFFIF.BK", "QQQQ-R.BK", "SPY-R.BK", "VTI-R.BK"],
    "Banking": ["BBL.BK", "KBANK.BK", "KTB.BK", "SCB.BK", "TISCO.BK", "TTB.BK"],
    "Energy": ["PTT.BK", "PTTEP.BK", "PTTGC.BK", "BANPU.BK", "GULF.BK"],
    "Technology": ["ADVANC.BK", "INTUCH.BK", "TRUE.BK", "COM7.BK", "DELTA.BK"]
}

# ===== HELPER FUNCTIONS =====
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_stock_data(ticker, start_date, end_date):
    """ดึงข้อมูลหุ้นพร้อม error handling และ caching"""
    try:
        with st.spinner(f"กำลังดึงข้อมูล {ticker}..."):
            stock_data = yf.download(ticker, start=start_date, end=end_date, progress=False)
            
            if stock_data.empty:
                return pd.DataFrame(), "ไม่พบข้อมูลหุ้น"
            
            # เลือกคอลัมน์ราคา
            if 'Adj Close' in stock_data.columns:
                stock_data['Price'] = stock_data['Adj Close']
            elif 'Close' in stock_data.columns:
                stock_data['Price'] = stock_data['Close']
            else:
                return pd.DataFrame(), "ไม่พบข้อมูลราคา"
            
            # เติมข้อมูลที่หายไป
            stock_data = stock_data.fillna(method='ffill').fillna(method='bfill')
            
            # คำนวณผลตอบแทน
            stock_data['Daily_Return'] = stock_data['Price'].pct_change()
            stock_data['Volatility'] = stock_data['Daily_Return'].rolling(window=30).std() * np.sqrt(252)
            
            return stock_data, None
            
    except Exception as e:
        return pd.DataFrame(), f"เกิดข้อผิดพลาด: {str(e)}"

def calculate_metrics(returns_series):
    """คำนวณเมตริกต่างๆ สำหรับการวิเคราะห์"""
    if len(returns_series) == 0:
        return {}
    
    returns_series = returns_series.dropna()
    
    return {
        'total_return': (returns_series.iloc[-1] / returns_series.iloc[0] - 1) * 100,
        'annualized_return': ((returns_series.iloc[-1] / returns_series.iloc[0]) ** (252 / len(returns_series)) - 1) * 100,
        'volatility': returns_series.pct_change().std() * np.sqrt(252) * 100,
        'sharpe_ratio': (returns_series.pct_change().mean() * 252) / (returns_series.pct_change().std() * np.sqrt(252)),
        'max_drawdown': calculate_max_drawdown(returns_series)
    }

def calculate_max_drawdown(price_series):
    """คำนวณ Maximum Drawdown"""
    peak = price_series.expanding().max()
    drawdown = (price_series - peak) / peak * 100
    return drawdown.min()

def simulate_dca_advanced(stock_data, monthly_amount, duration_months, start_date):
    """จำลองการลงทุนแบบ DCA แบบละเอียด"""
    results = []
    total_invested = 0
    total_shares = 0
    start_date = pd.to_datetime(start_date)
    
    for i in range(duration_months):
        investment_date = start_date + pd.DateOffset(months=i)
        
        # หาวันที่ใกล้เคียง
        available_dates = stock_data.index[stock_data.index >= investment_date]
        if len(available_dates) == 0:
            break
            
        actual_date = available_dates[0]
        price = stock_data.loc[actual_date, 'Price']
        
        # คำนวณการซื้อ
        shares_bought = monthly_amount / price
        total_shares += shares_bought
        total_invested += monthly_amount
        
        # มูลค่าพอร์ตในปัจจุบัน
        current_value = total_shares * price
        unrealized_gain = current_value - total_invested
        
        results.append({
            'Date': actual_date,
            'Price': price,
            'Shares_Bought': shares_bought,
            'Total_Shares': total_shares,
            'Monthly_Investment': monthly_amount,
            'Total_Invested': total_invested,
            'Portfolio_Value': current_value,
            'Unrealized_Gain': unrealized_gain,
            'Return_Pct': (unrealized_gain / total_invested) * 100 if total_invested > 0 else 0
        })
    
    return pd.DataFrame(results)

def simulate_lump_sum_advanced(stock_data, lump_sum_amount, start_date):
    """จำลองการลงทุนแบบ Lump Sum แบบละเอียด"""
    start_date = pd.to_datetime(start_date)
    available_dates = stock_data.index[stock_data.index >= start_date]
    
    if len(available_dates) == 0:
        return pd.DataFrame()
    
    actual_start_date = available_dates[0]
    initial_price = stock_data.loc[actual_start_date, 'Price']
    shares = lump_sum_amount / initial_price
    
    # คำนวณมูลค่าพอร์ตตลอดระยะเวลา
    portfolio_data = stock_data.loc[actual_start_date:].copy()
    portfolio_data['Portfolio_Value'] = shares * portfolio_data['Price']
    portfolio_data['Total_Invested'] = lump_sum_amount
    portfolio_data['Unrealized_Gain'] = portfolio_data['Portfolio_Value'] - lump_sum_amount
    portfolio_data['Return_Pct'] = (portfolio_data['Unrealized_Gain'] / lump_sum_amount) * 100
    portfolio_data['Shares'] = shares
    
    return portfolio_data

def create_comparison_chart(dca_data, lump_sum_data, investment_type_comparison=True):
    """สร้างกราฟเปรียบเทียบ DCA vs Lump Sum"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Portfolio Value Comparison', 'Return Comparison', 
                       'Investment vs Portfolio Value', 'Risk Analysis'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": True}, {"secondary_y": False}]]
    )
    
    if not dca_data.empty and not lump_sum_data.empty:
        # Portfolio Value Comparison
        fig.add_trace(
            go.Scatter(x=dca_data['Date'], y=dca_data['Portfolio_Value'], 
                      name='DCA Portfolio', line=dict(color='#667eea', width=3)),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=lump_sum_data.index, y=lump_sum_data['Portfolio_Value'], 
                      name='Lump Sum Portfolio', line=dict(color='#764ba2', width=3)),
            row=1, col=1
        )
        
        # Return Comparison
        fig.add_trace(
            go.Scatter(x=dca_data['Date'], y=dca_data['Return_Pct'], 
                      name='DCA Return %', line=dict(color='#84fab0', width=2)),
            row=1, col=2
        )
        fig.add_trace(
            go.Scatter(x=lump_sum_data.index, y=lump_sum_data['Return_Pct'], 
                      name='Lump Sum Return %', line=dict(color='#8fd3f4', width=2)),
            row=1, col=2
        )
        
        # Investment vs Portfolio (DCA)
        fig.add_trace(
            go.Scatter(x=dca_data['Date'], y=dca_data['Total_Invested'], 
                      name='Total Invested (DCA)', line=dict(color='#ffecd2')),
            row=2, col=1
        )
        fig.add_trace(
            go.Scatter(x=dca_data['Date'], y=dca_data['Portfolio_Value'], 
                      name='Portfolio Value (DCA)', line=dict(color='#fcb69f')),
            row=2, col=1
        )
    
    fig.update_layout(
        height=800,
        showlegend=True,
        title_text="Investment Strategy Comparison Dashboard",
        title_font_size=20
    )
    
    return fig

def create_advanced_metrics_table(dca_metrics, lump_sum_metrics):
    """สร้างตารางเปรียบเทียบเมตริก"""
    comparison_data = {
        'Metric': ['Total Return (%)', 'Annualized Return (%)', 'Volatility (%)', 
                  'Sharpe Ratio', 'Max Drawdown (%)'],
        'DCA': [
            f"{dca_metrics.get('total_return', 0):.2f}",
            f"{dca_metrics.get('annualized_return', 0):.2f}",
            f"{dca_metrics.get('volatility', 0):.2f}",
            f"{dca_metrics.get('sharpe_ratio', 0):.2f}",
            f"{dca_metrics.get('max_drawdown', 0):.2f}"
        ],
        'Lump Sum': [
            f"{lump_sum_metrics.get('total_return', 0):.2f}",
            f"{lump_sum_metrics.get('annualized_return', 0):.2f}",
            f"{lump_sum_metrics.get('volatility', 0):.2f}",
            f"{lump_sum_metrics.get('sharpe_ratio', 0):.2f}",
            f"{lump_sum_metrics.get('max_drawdown', 0):.2f}"
        ]
    }
    
    return pd.DataFrame(comparison_data)

# ===== MAIN APPLICATION =====
def main():
    load_css()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚀 Advanced DCA vs Lump Sum Investment Analyzer</h1>
        <p>เครื่องมือวิเคราะห์การลงทุนแบบครบวงจร สำหรับเปรียบเทียบกลยุทธ์การลงทุน</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ การตั้งค่า")
        
        # Stock Selection
        st.subheader("📊 เลือกหุ้น")
        category = st.selectbox("หมวดหุ้น", list(THAI_STOCKS.keys()))
        selected_ticker = st.selectbox("หุ้น", THAI_STOCKS[category])
        
        # Investment Parameters
        st.subheader("💰 พารามิเตอร์การลงทุน")
        
        col1, col2 = st.columns(2)
        with col1:
            monthly_amount = st.number_input("DCA ต่อเดือน (บาท)", 
                                           min_value=1000, max_value=1000000, 
                                           value=10000, step=1000)
        with col2:
            lump_sum_amount = st.number_input("Lump Sum (บาท)", 
                                            min_value=1000, max_value=10000000, 
                                            value=120000, step=10000)
        
        duration_months = st.slider("ระยะเวลา (เดือน)", 6, 120, 24)
        
        col3, col4 = st.columns(2)
        with col3:
            start_date = st.date_input("วันเริ่มต้น", 
                                     value=date(2020, 1, 1),
                                     max_value=date.today() - timedelta(days=30))
        with col4:
            analysis_type = st.selectbox("ประเภทการวิเคราะห์", 
                                       ["เปรียบเทียบ", "DCA เท่านั้น", "Lump Sum เท่านั้น"])
    
    # Main Content
    end_date = start_date + timedelta(days=duration_months * 30)
    
    # Fetch Data
    stock_data, error = get_stock_data(selected_ticker, start_date, end_date)
    
    if error:
        st.error(f"❌ {error}")
        return
    
    if stock_data.empty:
        st.warning("⚠️ ไม่พบข้อมูลในช่วงเวลาที่เลือก")
        return
    
    # Display Stock Info
    current_price = stock_data['Price'].iloc[-1]
    price_change = ((stock_data['Price'].iloc[-1] / stock_data['Price'].iloc[0]) - 1) * 100
    
    st.markdown("### 📈 ข้อมูลหุ้น")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("ราคาปัจจุบัน", f"฿{current_price:.2f}")
    with col2:
        st.metric("การเปลี่ยนแปลง", f"{price_change:+.2f}%", 
                 delta=f"{price_change:+.2f}%")
    with col3:
        volatility = stock_data['Daily_Return'].std() * np.sqrt(252) * 100
        st.metric("ความผันผวน (ปี)", f"{volatility:.2f}%")
    with col4:
        max_dd = calculate_max_drawdown(stock_data['Price'])
        st.metric("Max Drawdown", f"{max_dd:.2f}%")
    
    # Analysis Button
    if st.button("🚀 เริ่มการวิเคราะห์", use_container_width=True):
        with st.spinner("กำลังคำนวณ..."):
            
            # Simulate investments
            dca_data = simulate_dca_advanced(stock_data, monthly_amount, duration_months, start_date)
            lump_sum_data = simulate_lump_sum_advanced(stock_data, lump_sum_amount, start_date)
            
            if analysis_type == "เปรียบเทียบ" and not dca_data.empty and not lump_sum_data.empty:
                # Comparison Analysis
                st.markdown("## 📊 การเปรียบเทียบ DCA vs Lump Sum")
                
                # Summary Cards
                col1, col2 = st.columns(2)
                
                with col1:
                    dca_final_value = dca_data['Portfolio_Value'].iloc[-1]
                    dca_total_invested = dca_data['Total_Invested'].iloc[-1]
                    dca_return = ((dca_final_value - dca_total_invested) / dca_total_invested) * 100
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>💰 DCA Strategy</h3>
                        <p><strong>มูลค่าพอร์ต:</strong> ฿{dca_final_value:,.2f}</p>
                        <p><strong>เงินลงทุน:</strong> ฿{dca_total_invested:,.2f}</p>
                        <p><strong>ผลตอบแทน:</strong> {dca_return:+.2f}%</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    ls_final_value = lump_sum_data['Portfolio_Value'].iloc[-1]
                    ls_total_invested = lump_sum_amount
                    ls_return = ((ls_final_value - ls_total_invested) / ls_total_invested) * 100
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>📈 Lump Sum Strategy</h3>
                        <p><strong>มูลค่าพอร์ต:</strong> ฿{ls_final_value:,.2f}</p>
                        <p><strong>เงินลงทุน:</strong> ฿{ls_total_invested:,.2f}</p>
                        <p><strong>ผลตอบแทน:</strong> {ls_return:+.2f}%</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Winner Declaration
                if dca_return > ls_return:
                    st.markdown(f"""
                    <div class="success-card">
                        <h3>🏆 DCA ชนะ!</h3>
                        <p>DCA ให้ผลตอบแทนสูงกว่า {dca_return - ls_return:.2f}%</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="warning-card">
                        <h3>🏆 Lump Sum ชนะ!</h3>
                        <p>Lump Sum ให้ผลตอบแทนสูงกว่า {ls_return - dca_return:.2f}%</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Advanced Charts
                fig = create_comparison_chart(dca_data, lump_sum_data)
                st.plotly_chart(fig, use_container_width=True)
                
                # Metrics Table
                dca_metrics = calculate_metrics(dca_data['Portfolio_Value'])
                ls_metrics = calculate_metrics(lump_sum_data['Portfolio_Value'])
                
                st.markdown("### 📋 เมตริกการวิเคราะห์")
                metrics_df = create_advanced_metrics_table(dca_metrics, ls_metrics)
                st.dataframe(metrics_df, use_container_width=True)
                
            elif analysis_type == "DCA เท่านั้น" and not dca_data.empty:
                # DCA Only Analysis
                st.markdown("## 💰 การวิเคราะห์ DCA")
                
                dca_final_value = dca_data['Portfolio_Value'].iloc[-1]
                dca_total_invested = dca_data['Total_Invested'].iloc[-1]
                dca_return = ((dca_final_value - dca_total_invested) / dca_total_invested) * 100
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("มูลค่าพอร์ต", f"฿{dca_final_value:,.2f}")
                with col2:
                    st.metric("เงินลงทุนรวม", f"฿{dca_total_invested:,.2f}")
                with col3:
                    st.metric("ผลตอบแทน", f"{dca_return:+.2f}%")
                
                # DCA Chart
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=dca_data['Date'], y=dca_data['Portfolio_Value'],
                                       name='มูลค่าพอร์ต', line=dict(color='#667eea', width=3)))
                fig.add_trace(go.Scatter(x=dca_data['Date'], y=dca_data['Total_Invested'],
                                       name='เงินลงทุนสะสม', line=dict(color='#764ba2', width=2)))
                fig.update_layout(title="DCA Investment Progress", height=500)
                st.plotly_chart(fig, use_container_width=True)
                
            elif analysis_type == "Lump Sum เท่านั้น" and not lump_sum_data.empty:
                # Lump Sum Only Analysis
                st.markdown("## 📈 การวิเคราะห์ Lump Sum")
                
                ls_final_value = lump_sum_data['Portfolio_Value'].iloc[-1]
                ls_return = ((ls_final_value - lump_sum_amount) / lump_sum_amount) * 100
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("มูลค่าพอร์ต", f"฿{ls_final_value:,.2f}")
                with col2:
                    st.metric("เงินลงทุน", f"฿{lump_sum_amount:,.2f}")
                with col3:
                    st.metric("ผลตอบแทน", f"{ls_return:+.2f}%")
                
                # Lump Sum Chart
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=lump_sum_data.index, y=lump_sum_data['Portfolio_Value'],
                                       name='มูลค่าพอร์ต', line=dict(color='#84fab0', width=3)))
                fig.add_trace(go.Scatter(x=lump_sum_data.index, y=[lump_sum_amount] * len(lump_sum_data),
                                       name='เงินลงทุน', line=dict(color='#8fd3f4', width=2)))
                fig.update_layout(title="Lump Sum Investment Progress", height=500)
                st.plotly_chart(fig, use_container_width=True)
    
    # Educational Content
    with st.expander("📚 คู่มือการใช้งาน"):
        st.markdown("""
        ### 🎯 DCA vs Lump Sum คืออะไร?
        
        **Dollar Cost Averaging (DCA)**: การลงทุนเป็นงวดๆ เป็นจำนวนเงินคงที่ในช่วงเวลาที่กำหนด
        - ✅ ลดความเสี่ยงจากการเข้าจังหวะผิด
        - ✅ เหมาะกับนักลงทุนมือใหม่
        - ❌ อาจพลาดโอกาสเมื่อตลาดขาขึ้น
        
        **Lump Sum**: การลงทุนเงินก้อนครั้งเดียว
        - ✅ ได้ผลตอบแทนสูงกว่าในตลาดขาขึ้น
        - ✅ ได้รับผลจากการทบต้นเร็วกว่า
        - ❌ ความเสี่ยงสูงหากเข้าจังหวะผิด
        
        ### 📊 วิธีอ่านผลการวิเคราะห์
        - **Total Return**: ผลตอบแทนรวมตลอดช่วงเวลา
        - **Annualized Return**: ผลตอบแทนเฉลี่ยต่อปี
        - **Volatility**: ความผันผวนของการลงทุน
        - **Sharpe Ratio**: อัตราส่วนผลตอบแทนต่อความเสี่ยง
        - **Max Drawdown**: การลดลงสูงสุดจากจุดสูงสุด
        """)

if __name__ == "__main__":
    main()
