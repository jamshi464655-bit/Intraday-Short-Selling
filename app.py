import streamlit as st
import pandas as pd
import yfinance as yf

# Page Configuration
st.set_page_config(page_title="EasyCharts Pro - Intraday Down-Trend Scanner", layout="wide")

# UI Custom CSS Styling (Premium Dark/Red Theme for Down-Trend)
st.markdown("""
<style>
    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0;
    }
    .header-box {
        background: linear-gradient(135deg, #111827, #7f1d1d, #0f172a); 
        padding: 30px; 
        border-radius: 20px; 
        color: white; 
        text-align: center; 
        margin-bottom: 30px; 
        border: 1px solid #ef4444;
        box-shadow: 0 10px 30px rgba(239, 68, 68, 0.2);
    }
    .header-box h1 {
        font-size: 32px;
        font-weight: 800;
        background: linear-gradient(to right, #f87171, #f43f5e, #fb7185);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background: #111827;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #1f2937;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Nifty 500 ലിസ്റ്റ്
nifty500_raw = """
360ONE, ABB, ABCAPITAL, ABFRL, ACC, ADANIENSOL, ADANIENT, ADANIGREEN, ADANIPORTS, ADANIPOWER, ATGL,
ALKEM, AMBUJACEM, ANGELONE, APOLLOHOSP, APOLLOTYRE, ASHOKLEY, ASIANPAINT, ASTRAL, AUBANK, AUROPHARMA,
AXISBANK, BAJAJ-AUTO, BAJFINANCE, BAJAJFINSV, BALKRISIND, BANDHANBNK, BANKBARODA, BANKINDIA, BATAINDIA,
BEL, BHARATFORG, BHEL, BHARTIARTL, BIOCON, BOSCHLTD, BPCL, BRITANNIA, BSE, CANBK, CGPOWER, CIPLA,
COALINDIA, COFORGE, COLPAL, CONCOR, CUMMINSIND, DABUR, DALBHARAT, DEEPAKNTR, DELHIVERY, DIVISLAB,
DIXON, DLF, DMART, DRREDDY, EICHERMOT, ESCORTS, EXIDEIND, FEDERALBNK, FORTIS, GAIL, GLENMARK,
GMRINFRA, GODREJCP, GODREJPROP, GRASIM, HAL, HAVELLS, HCLTECH, HDFCAMC, HDFCBANK, HDFCLIFE,
HEROMOTOCO, HINDALCO, HINDPETRO, HINDUNILVR, ICICIBANK, ICICIGI, ICICIPRULI, IDFCFIRSTB, IEX,
INDHOTEL, INDUSINDBK, INDUSTOWER, INFY, IPCALAB, IRCTC, IRFC, ITC, JINDALSTEL, JIOFIN, JSWSTEEL,
JUBLFOOD, KALYANKJIL, KOTAKBANK, KPITTECH, LT, LTIM, LTTS, LUPIN, M&M, M&MFIN, MANAPPURAM, MARICO,
MARUTI, MAXHEALTH, MCX, METROPOLIS, MPHASIS, MRF, MUTHOOTFIN, NATIONALUM, NAUKRI, NAVINFLUOR,
NESTLEIND, NHPC, NMDC, NTPC, NYKAA, OBEROIRLTY, OFSS, OIL, ONGC, PAGEIND, PAYTM, PERSISTENT,
PETRONET, PFC, PIDILITIND, PIIND, PNB, POLYCAB, POWERGRID, PRESTIGE, RADICO, RECLTD, RELIANCE,
RVNL, SAIL, SBICARD, SBILIFE, SBIN, SHREECEM, SHRIRAMFIN, SIEMENS, SONACOMS, SUNPHARMA, SUNTV,
SUZLON, TATACOMM, TATACONSUM, TATAELXSI, TATAMOTORS, TATAPOWER, TATASTEEL, TATATECH, TCS, TECHM,
TITAN, TORNTPHARM, TORNTPOWER, TRENT, TRIDENT, TVSMOTOR, UBL, ULTRACEMCO, UNIONBANK, UNITDSPR,
UPL, VBL, VEDL, VOLTAS, WIPRO, YESBANK, ZOMATO, ZYDUSLIFE
"""

def get_nifty500_symbols(text):
    symbols = text.replace('\n', ',').split(',')
    cleaned = sorted(list(set([s.strip() for s in symbols if s.strip()])))
    return [s + ".NS" for s in cleaned]

stocks = get_nifty500_symbols(nifty500_raw)

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).ewm(alpha=1/period, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/period, adjust=False).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs.iloc[-1]))

# Top Header Banner
st.markdown("""
<div class="header-box">
    <h1>📉 EASYCHARTS PRO — INTRADAY BEARISH TERMINAL</h1>
    <p style="color: #cbd5e1; font-size: 16px;">EMA 8, 13, 21, 55 അടിസ്ഥാനമാക്കി 5m, 15m ടൈംഫ്രെയിമുകളിൽ തകർച്ചയിലുള്ള (Down-Trend) സ്റ്റോക്കുകൾ കണ്ടെത്തുന്നു</p>
</div>
""", unsafe_allow_html=True)

# SIDEBAR CONFIGURATION
st.sidebar.markdown("### ⚙️ Scanner Configuration")
tf_choice = st.sidebar.selectbox("Select Timeframe", ["5 Minute (5m)", "15 Minute (15m)"])
max_rsi = st.sidebar.slider("Maximum RSI Filter (Weakness)", 30, 50, 45)

# ടൈംഫ്രെയിം അനുസരിച്ച് പീരിയഡ് സെറ്റ് ചെയ്യുന്നു
period_setting = "3d" if "5m" in tf_choice else "5d"  
interval_setting = "5m" if "5m" in tf_choice else "15m"

# SCAN BUTTON
if st.button(f'🔍 RUN BEARISH {interval_setting.upper()} SCAN', use_container_width=True):
    with st.spinner(f"Nifty 500 ചാർട്ടുകൾ {tf_choice}-ൽ ഡൗൺട്രെൻഡ് പരിശോധിക്കുന്നു..."):
        try:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text(f"📥 Market-ൽ നിന്നും {interval_setting} ഡാറ്റ ഡൗൺലോഡ് ചെയ്യുന്നു...")
            all_data = yf.download(stocks, period=period_setting, interval=interval_setting, group_by="ticker", progress=False)
            
            results = []
            total_stocks = len(stocks)
            
            for i, s in enumerate(stocks):
                if i % 20 == 0:
                    status_text.text(f"Scanning Down-Trends: {i}/{total_stocks} Stocks Evaluated")
                    progress_bar.progress((i + 1) / total_stocks)
                    
                try:
                    df = all_data[s].dropna() if isinstance(all_data.columns, pd.MultiIndex) else all_data.dropna()
                    
                    if len(df) < 55:
                        continue

                    close_series = df['Close'].squeeze()
                    close = float(close_series.iloc[-1])
                    prev_close = float(close_series.iloc[-2])
                    change_pct = ((close - prev_close) / prev_close) * 100
                    
                    # EMAs Calculation
                    ema8 = close_series.ewm(span=8, adjust=False).mean().iloc[-1]
                    ema13 = close_series.ewm(span=13, adjust=False).mean().iloc[-1]
                    ema21 = close_series.ewm(span=21, adjust=False).mean().iloc[-1]
                    ema55 = close_series.ewm(span=55, adjust=False).mean().iloc[-1]
                    
                    # Previous EMAs for Crossover
                    ema8_prev = close_series.ewm(span=8, adjust=False).mean().iloc[-2]
                    ema13_prev = close_series.ewm(span=13, adjust=False).mean().iloc[-2]
                    
                    rsi = calculate_rsi(close_series)
                    
                    # 📉 Bearish Down-Trend Logic
                    is_bearish_structure = (close < ema55) and (ema8 < ema13) and (ema13 < ema21)
                    
                    if is_bearish_structure and rsi <= max_rsi:
                        name = s.replace(".NS", "")
                        tv_link = f"https://in.tradingview.com/chart/?symbol=NSE:{name}"
                        
                        # സിഗ്നൽ തരം തിരിക്കൽ
                        if ema8_prev >= ema13_prev:
                            status = "🚨 FRESH BEARISH CROSS"
                        elif (close_series.iloc[-1] <= ema8) and (close_series.iloc[-2] >= ema8_prev):
                            status = "🩸 BEARISH PULLBACK"
                        else:
                            status = "📉 STRONG DOWN-TREND"
                            
                        results.append({
                            "Stock": name,
                            "Price (₹)": round(close, 2),
                            "Change %": round(change_pct, 2),
                            "RSI (14)": round(rsi, 2),
                            "Bearish Signal": status,
                            "TradingView": tv_link
                        })
                except:
                    pass
            
            progress_bar.progress(1.0)
            status_text.text("✅ ഡൗൺട്രെൻഡ് സ്കാനിംഗ് പൂർത്തിയായി!")
            
            if results:
                final_df = pd.DataFrame(results)
                # ഏറ്റവും കൂടുതൽ താഴേക്ക് പോയ സ്റ്റോക്കുകൾ മുകളിൽ കാണിക്കാൻ (Ascending=True)
                final_df = final_df.sort_values(by="Change %", ascending=True)
                
                # Metric Summary
                st.markdown(f'<div class="metric-card"><h4 style="color: #f87171; margin:0;">🎯 TOTAL DOWN-TREND STOCKS FOUND</h4><h2 style="margin:5px 0 0 0;">{len(final_df)} Stocks</h2></div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Table Config
                st.data_editor(
                    final_df,
                    column_config={
                        "TradingView": st.column_config.LinkColumn(
                            "TradingView 🔗",
                            display_text="Open Chart 📈"
                        ),
                        "Price (₹)": st.column_config.NumberColumn(format="₹ %.2f"),
                        "Change %": st.column_config.NumberColumn(format="%.2f %%"),
                        "RSI (14)": st.column_config.NumberColumn(format="%.1f")
                    },
                    use_container_width=True,
                    hide_index=True,
                    disabled=True
                )
            else:
                st.info("നിങ്ങൾ വെച്ച ഫിൽട്ടറുകൾക്ക് അനുയോജ്യമായ ഡൗൺട്രെൻഡ് സ്റ്റോക്കുകൾ ഇപ്പോൾ ലഭ്യമല്ല.")
                
        except Exception as e:
            st.error(f"Error during scan: {e}")
else:
    st.markdown("""
    <div style="text-align: center; padding: 40px; background: #111827; border-radius: 12px; border: 1px dashed #ef4444;">
        <p style="color: #9ca3af; font-size: 16px; margin: 0;">സൈഡ്‌ബാറിൽ 5m അല്ലെങ്കിൽ 15m ടൈംഫ്രെയിം തിരഞ്ഞെടുത്ത ശേഷം മുകളിലെ ബട്ടൺ അമർത്തുക.</p>
    </div>
    """, unsafe_allow_html=True)