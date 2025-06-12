import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import date, timedelta
import warnings
warnings.filterwarnings('ignore')

# Page Configuration
st.set_page_config(
    page_title="DCA vs Lump Sum Analyzer",
    page_icon="📈",
    layout="wide"
)

# Stock Lists
STOCK_CATEGORIES = {
    "SET 50": ["ADVANC.BK", "AOT.BK", "BBL.BK", "BDMS.BK", "BTS.BK", "CPALL.BK", 
               "CPF.BK", "CPN.BK", "DELTA.BK", "GULF.BK", "INTUCH.BK", "KBANK.BK", 
               "KTC.BK", "PTT.BK", "PTTEP.BK", "SCB.BK", "SCC.BK", "TRUE.BK"],
    "ETFs": ["TFFIF.BK", "QQQQ-R.BK", "SPY-R.BK", "VTI-R.BK"],
    "Banking": ["BBL.BK", "KBANK.BK", "KTB.BK", "SCB.BK", "TTB.BK"],
    "Energy": ["PTT.BK", "PTTEP.BK", "BANPU.BK", "GULF.BK"],
    "Technology": ["ADVANC.BK", "INTUCH.BK", "TRUE.BK", "DELTA.BK"]
}

# Helper Functions
@st.cache_data(ttl=300)
def get_stock_data(ticker, start_date, end_date):
    try:
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        if data.empty:
            return None, "No data found"
        
        data['Price'] = data['Adj Close'] if 'Adj Close' in data.columns else data['Close']
        data = data.ffill().bfill()
        return data, None
    except Exception as e:
        return None, str(e)

def simulate_dca(stock_data, monthly_amount, duration_months, start_date):
    results = []
    total_invested = 0
    total_shares = 0
    start_date = pd.to_datetime(start_date)
    
    for i in range(duration_months):
        investment_date = start_date + pd.DateOffset(months=i)
        available_dates = stock_data.index[stock_data.index >= investment_date]
        
        if len(available_dates) == 0:
            break
            
        actual_date = available_dates[0]
        
        # ✅ แก้ตรงนี้: ใช้ .at แทน .loc
        try:
            price = stock_data.at[actual_date, 'Price']
        except Exception:
            continue
        
        if price <= 0 or pd.isna(price):
            continue
        
        shares_bought = monthly_amount / price
        total_shares += shares_bought
        total_invested += monthly_amount
        current_value = total_shares * price
        
        results.append({
            'Date': actual_date,
            'Price': price,
            'Total_Invested': total_invested,
            'Portfolio_Value': current_value,
            'Return_Pct': ((current_value - total_invested) / total_invested) * 100 if total_invested > 0 else 0
        })
    
    return pd.DataFrame(results)

def simulate_lump_sum(stock_data, lump_sum_amount, start_date):
    start_date = pd.to_datetime(start_date)
    available_dates = stock_data.index[stock_data.index >= start_date]
    
    if len(available_dates) == 0:
        return pd.DataFrame()
    
    actual_start_date = available_dates[0]
    initial_price = stock_data.loc[actual_start_date, 'Price']
    
    if initial_price <= 0 or pd.isna(initial_price):
        return pd.DataFrame()
    
    shares = lump_sum_amount / initial_price
    portfolio_data = stock_data.loc[actual_start_date:].copy()
    portfolio_data['Portfolio_Value'] = shares * portfolio_data['Price']
    portfolio_data['Return_Pct'] = ((portfolio_data['Portfolio_Value'] - lump_sum_amount) / lump_sum_amount) * 100
    
    return portfolio_data

# Main App
def main():
    st.title("📈 DCA vs Lump Sum Investment Analyzer")
    st.markdown("Compare Dollar Cost Averaging vs Lump Sum investment strategies")
    
    # Sidebar Configuration
    with st.sidebar:
        st.header("Investment Settings")
        
        # Stock Selection
        category = st.selectbox("Stock Category", list(STOCK_CATEGORIES.keys()))
        ticker = st.selectbox("Select Stock", STOCK_CATEGORIES[category])
        
        # Investment Parameters
        col1, col2 = st.columns(2)
        with col1:
            monthly_amount = st.number_input("DCA Monthly (฿)", 
                                           min_value=1000, value=10000, step=1000)
        with col2:
            duration_months = st.slider("Duration (months)", 6, 60, 24)
        
        lump_sum_amount = st.number_input("Lump Sum Amount (฿)", 
                                        min_value=1000, value=monthly_amount * duration_months, step=5000)
        
        start_date = st.date_input("Start Date", 
                                 value=date(2020, 1, 1),
                                 max_value=date.today() - timedelta(days=30))
    
    # Analysis Button
    if st.button("🚀 Analyze", use_container_width=True):
        end_date = start_date + timedelta(days=duration_months * 30)
        
        # Fetch Data
        with st.spinner(f"Fetching data for {ticker}..."):
            stock_data, error = get_stock_data(ticker, start_date, end_date)
        
        if error:
            st.error(f"Error: {error}")
            return
        
        if stock_data is None or stock_data.empty:
            st.warning("No data available for the selected period")
            return
        
        # Stock Info
        current_price = stock_data['Price'].iloc[-1]
        price_change = ((stock_data['Price'].iloc[-1] / stock_data['Price'].iloc[0]) - 1) * 100
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current Price", f"฿{current_price:.2f}")
        with col2:
            st.metric("Price Change", f"{price_change:+.2f}%")
        with col3:
            volatility = stock_data['Price'].pct_change().std() * np.sqrt(252) * 100
            st.metric("Volatility (Annual)", f"{volatility:.2f}%")
        
        # Simulate Strategies
        with st.spinner("Running simulations..."):
            dca_data = simulate_dca(stock_data, monthly_amount, duration_months, start_date)
            lump_sum_data = simulate_lump_sum(stock_data, lump_sum_amount, start_date)
        
        if dca_data.empty or lump_sum_data.empty:
            st.error("Unable to simulate strategies")
            return
        
        # Results Summary
        st.subheader("📊 Results Summary")
        
        dca_final_value = dca_data['Portfolio_Value'].iloc[-1]
        dca_total_invested = dca_data['Total_Invested'].iloc[-1]
        dca_return = dca_data['Return_Pct'].iloc[-1]
        
        ls_final_value = lump_sum_data['Portfolio_Value'].iloc[-1]
        ls_return = lump_sum_data['Return_Pct'].iloc[-1]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 💰 DCA Strategy")
            st.metric("Final Value", f"฿{dca_final_value:,.0f}")
            st.metric("Total Invested", f"฿{dca_total_invested:,.0f}")
            st.metric("Return", f"{dca_return:+.2f}%")
        
        with col2:
            st.markdown("### 📈 Lump Sum Strategy")
            st.metric("Final Value", f"฿{ls_final_value:,.0f}")
            st.metric("Total Invested", f"฿{lump_sum_amount:,.0f}")
            st.metric("Return", f"{ls_return:+.2f}%")
        
        # Winner Declaration
        if dca_return > ls_return:
            st.success(f"🏆 DCA wins by {dca_return - ls_return:.2f}%!")
        else:
            st.info(f"🏆 Lump Sum wins by {ls_return - dca_return:.2f}%!")
        
        # Comparison Chart
        st.subheader("📈 Portfolio Value Comparison")
        
        fig = go.Figure()
        
        # DCA line
        fig.add_trace(go.Scatter(
            x=dca_data['Date'], 
            y=dca_data['Portfolio_Value'],
            name='DCA Portfolio',
            line=dict(color='#2E86AB', width=3)
        ))
        
        # Lump Sum line
        fig.add_trace(go.Scatter(
            x=lump_sum_data.index, 
            y=lump_sum_data['Portfolio_Value'],
            name='Lump Sum Portfolio',
            line=dict(color='#A23B72', width=3)
        ))
        
        # DCA Investment line
        fig.add_trace(go.Scatter(
            x=dca_data['Date'], 
            y=dca_data['Total_Invested'],
            name='DCA Invested',
            line=dict(color='#F18F01', width=2, dash='dash')
        ))
        
        # Lump Sum Investment line
        fig.add_trace(go.Scatter(
            x=lump_sum_data.index, 
            y=[lump_sum_amount] * len(lump_sum_data),
            name='Lump Sum Invested',
            line=dict(color='#C73E1D', width=2, dash='dash')
        ))
        
        fig.update_layout(
            title=f"Investment Comparison - {ticker}",
            xaxis_title="Date",
            yaxis_title="Value (฿)",
            height=500,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Return Comparison Chart
        st.subheader("📊 Return Comparison")
        
        fig2 = go.Figure()
        
        fig2.add_trace(go.Scatter(
            x=dca_data['Date'], 
            y=dca_data['Return_Pct'],
            name='DCA Return %',
            line=dict(color='#2E86AB')
        ))
        
        fig2.add_trace(go.Scatter(
            x=lump_sum_data.index, 
            y=lump_sum_data['Return_Pct'],
            name='Lump Sum Return %',
            line=dict(color='#A23B72')
        ))
        
        fig2.update_layout(
            title="Return Percentage Over Time",
            xaxis_title="Date",
            yaxis_title="Return (%)",
            height=400
        )
        
        st.plotly_chart(fig2, use_container_width=True)
        
        # Summary Table
        st.subheader("📋 Summary Table")
        
        summary_data = {
            'Strategy': ['DCA', 'Lump Sum'],
            'Final Value (฿)': [f"{dca_final_value:,.0f}", f"{ls_final_value:,.0f}"],
            'Total Invested (฿)': [f"{dca_total_invested:,.0f}", f"{lump_sum_amount:,.0f}"],
            'Total Return (%)': [f"{dca_return:.2f}%", f"{ls_return:.2f}%"],
            'Profit/Loss (฿)': [f"{dca_final_value - dca_total_invested:+,.0f}", 
                               f"{ls_final_value - lump_sum_amount:+,.0f}"]
        }
        
        st.dataframe(pd.DataFrame(summary_data), use_container_width=True)
    
    # Information
    with st.expander("ℹ️ How to Use"):
        st.markdown("""
        **Steps:**
        1. Select a stock category and specific stock
        2. Set your DCA monthly amount and investment duration
        3. Set your lump sum amount (defaults to total DCA amount)
        4. Choose a start date
        5. Click "Analyze" to compare strategies
        
        **Key Metrics:**
        - **Final Value**: Portfolio value at the end
        - **Total Return**: Percentage gain/loss
        - **DCA**: Invests fixed amount monthly
        - **Lump Sum**: Invests entire amount at once
        """)
    
    with st.expander("⚠️ Disclaimer"):
        st.markdown("""
        - Past performance does not guarantee future results
        - Does not include trading fees, taxes, or other costs
        - This is for educational purposes only
        - Consult a financial advisor before making investment decisions
        """)

if __name__ == "__main__":
    main()
