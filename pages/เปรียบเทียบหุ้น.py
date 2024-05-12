import streamlit as st
from datetime import date
import yfinance as yf 
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objects as go
import pandas as pd

streamlit_style = """
<style>
@import url(https://fonts.googleapis.com/css2?family=Mitr:wght@200;300;400;500;600;700&display=swap);

* {
    font-family: 'Mitr', sans-serif;
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
    background-image: linear-gradient(90deg, #92CA68;, #92CA68;); /* Red to blue gradient */
    z-index: 999990;
}
</style>
"""

# Render the CSS styles in your Streamlit app
st.markdown(css_string, unsafe_allow_html=True)

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
    df = relativereturn(yf.download(dropdown,start,end,progress=False)['Adj Close'])
    st.line_chart(df)

def get_financial_ratios(tickers):
    ratios = {}
    for ticker in tickers:
        try:
            stock_info = yf.Ticker(ticker).info
            ratios[ticker] = {
                'Price/Book': stock_info.get('priceToBook', 'N/A'),
                'Price/Earnings': stock_info.get('trailingPE', 'N/A'),
                'Price/Sales': stock_info.get('priceToSalesTrailingTwelveMonths', 'N/A'),
                'Price/Cash Flow': stock_info.get('priceToOperatingCashFlowsTrailingTwelveMonths', 'N/A'),
                'Debt/Equity': stock_info.get('debtToEquity', 'N/A'),
                'Return on Equity': stock_info.get('returnOnEquity', 'N/A'),
                'Return on Assets': stock_info.get('returnOnAssets', 'N/A'),
                'Operating Margin': stock_info.get('operatingMargin', 'N/A'),
                'Profit Margin': stock_info.get('profitMargins', 'N/A'),
                'Current Ratio': stock_info.get('currentRatio', 'N/A'),
                'Quick Ratio': stock_info.get('quickRatio', 'N/A'),
            }
        except:
            pass
    return pd.DataFrame.from_dict(ratios, orient='index')

if len(dropdown) > 0:
    ratios_df = get_financial_ratios(dropdown)
    if not ratios_df.empty:
        st.header('สัดส่วนการเงิน')
        ratio_col = st.selectbox('เลือกสัดส่วนการเงิน', list(ratios_df.columns))
        if ratio_col:
            fig = px.bar(ratios_df[[ratio_col]], x=ratios_df.index, y=ratio_col, barmode='group', title=ratio_col)
            st.plotly_chart(fig)


    
