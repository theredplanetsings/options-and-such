import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from scipy.stats import norm
from scipy.optimize import brentq
from datetime import datetime, timedelta
import yfinance as yf

__author__ = "https://github.com/theredplanetsings"
__date__ = "20/6/2025"

st.set_page_config(page_title="Options & Volatility Dashboard", layout="wide")

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_stock_data(symbol):
    """Fetch current stock price and basic info using yfinance"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period="1d")
        
        if hist.empty:
            return None, None, None
        
        current_price = hist['Close'].iloc[-1]
        company_name = info.get('longName', symbol)
        
        # Try to get some basic volatility estimate from recent data
        hist_30d = ticker.history(period="30d")
        if len(hist_30d) > 1:
            returns = np.log(hist_30d['Close'] / hist_30d['Close'].shift(1)).dropna()
            historical_vol = returns.std() * np.sqrt(252)  # Annualized volatility
        else:
            historical_vol = None
            
        return current_price, company_name, historical_vol
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {str(e)}")
        return None, None, None

def black_scholes_call(S, K, T, r, sigma):
    """Calculate Black-Scholes call option price"""
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    call_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    return call_price

def black_scholes_put(S, K, T, r, sigma):
    """Calculate Black-Scholes put option price"""
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    put_price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    return put_price

def implied_volatility(option_price, S, K, T, r, option_type='call'):
    """Calculate implied volatility using Brent's method"""
    def objective(sigma):
        if option_type == 'call':
            return black_scholes_call(S, K, T, r, sigma) - option_price
        else:
            return black_scholes_put(S, K, T, r, sigma) - option_price
    
    try:
        return brentq(objective, 0.001, 5.0)
    except ValueError:
        return np.nan

def option_greeks(S, K, T, r, sigma, option_type='call'):
    """Calculate option Greeks"""
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    # Delta
    if option_type == 'call':
        delta = norm.cdf(d1)
    else:
        delta = norm.cdf(d1) - 1
    
    # Gamma
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    
    # Theta
    if option_type == 'call':
        theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) - 
                r * K * np.exp(-r * T) * norm.cdf(d2)) / 365
    else:
        theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) + 
                r * K * np.exp(-r * T) * norm.cdf(-d2)) / 365
    
    # Vega
    vega = S * norm.pdf(d1) * np.sqrt(T) / 100
    
    return {'delta': delta, 'gamma': gamma, 'theta': theta, 'vega': vega}

def black_scholes_calculator():
    st.header("Black-Scholes Option Pricing Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Input Parameters")
        
        # Stock selection
        st.markdown("**Stock Selection**")
        use_stock_symbol = st.checkbox("Use specific stock symbol", value=False, key="bs_use_symbol")
        
        if use_stock_symbol:
            stock_symbol = st.text_input("Stock Symbol (e.g., AAPL, MSFT, SPY)", value="AAPL", key="bs_symbol").upper()
            
            if stock_symbol:
                with st.spinner(f"Fetching data for {stock_symbol}..."):
                    current_price, company_name, hist_vol = get_stock_data(stock_symbol)
                
                if current_price is not None:
                    st.success(f"✓ {company_name} ({stock_symbol})")
                    st.info(f"Current Price: ${current_price:.2f}")
                    if hist_vol is not None:
                        st.info(f"30-day Historical Volatility: {hist_vol*100:.1f}%")
                    
                    price_label = f"{stock_symbol} Price"
                    default_price = float(current_price)
                    default_vol = float(hist_vol) if hist_vol is not None else 0.20
                else:
                    st.error(f"Could not fetch data for {stock_symbol}")
                    price_label = f"{stock_symbol} Price ($)"
                    default_price = 100.0
                    default_vol = 0.20
                    stock_symbol = None
            else:
                price_label = "Stock Price ($)"
                default_price = 100.0
                default_vol = 0.20
                stock_symbol = None
        else:
            stock_symbol = None
            price_label = "Current Stock Price ($)"
            default_price = 100.0
            default_vol = 0.20
        
        st.markdown("**Option Parameters**")
        S = st.number_input(price_label, value=default_price, min_value=0.01)
        K = st.number_input("Strike Price ($)", value=default_price, min_value=0.01)
        T = st.number_input("Time to Expiration (years)", value=0.25, min_value=0.001)
        r = st.number_input("Risk-free Rate (%)", value=5.0, min_value=0.0) / 100
        sigma = st.number_input("Volatility (%)", value=default_vol*100, min_value=0.1) / 100
        option_type = st.radio("Option Type", ["Call", "Put"])
    
    with col2:
        st.subheader("Results")
        if option_type == "Call":
            price = black_scholes_call(S, K, T, r, sigma)
        else:
            price = black_scholes_put(S, K, T, r, sigma)
        
        greeks = option_greeks(S, K, T, r, sigma, option_type.lower())
        
        st.metric("Option Price", f"${price:.4f}")
        st.metric("Delta", f"{greeks['delta']:.4f}")
        st.metric("Gamma", f"{greeks['gamma']:.4f}")
        st.metric("Theta", f"{greeks['theta']:.4f}")
        st.metric("Vega", f"{greeks['vega']:.4f}")
    
    st.divider()
    
    # Black-Scholes Surfaces
    st.subheader("Black-Scholes Model Surfaces")
    
    # Surface type selection
    surface_type = st.radio(
        "Select Surface Type",
        ["Price Surface", "Volatility Surface"],
        horizontal=True,
        help="Price Surface: Shows how option prices vary with strike and time. Volatility Surface: Shows the constant volatility assumption in Black-Scholes.",
        key="surface_type_selector"
    )
    
    # Surface parameters
    col_params1, col_params2, col_params3 = st.columns(3)
    with col_params1:
        strike_range = st.slider("Strike Range (% of spot)", 50, 150, (80, 120), key="bs_strike_range")
    with col_params2:
        time_range = st.slider("Time Range (days)", 1, 365, (7, 90), key="bs_time_range")
    with col_params3:
        show_current_point = st.checkbox("Show Current Option", value=True, key="bs_show_point")
    
    # Generate surface data
    strike_min, strike_max = strike_range
    time_min, time_max = time_range
    
    strikes = np.linspace(S * strike_min/100, S * strike_max/100, 25)
    times = np.linspace(time_min/365, time_max/365, 20)
    
    # Create container for the plot that will be updated
    plot_container = st.empty()
    
    with plot_container.container():
        if surface_type == "Price Surface":
            surface_data = np.zeros((len(times), len(strikes)))
            for i, time in enumerate(times):
                for j, strike in enumerate(strikes):
                    if option_type == "Call":
                        surface_data[i, j] = black_scholes_call(S, strike, time, r, sigma)
                    else:
                        surface_data[i, j] = black_scholes_put(S, strike, time, r, sigma)
            z_title = "Option Price ($)"
            surface_title = f'Black-Scholes {option_type} Option Price Surface'
            current_z = price
            colorscale = 'Viridis'
        else:  # Volatility Surface
            # In Black-Scholes, volatility is constant across all strikes and times
            surface_data = np.full((len(times), len(strikes)), sigma * 100)
            z_title = "Volatility (%)"
            surface_title = f'Black-Scholes Volatility Surface (Constant σ = {sigma*100:.1f}%)'
            current_z = sigma * 100
            colorscale = 'Blues'
        
        # Create 3D surface plot
        fig = go.Figure()
        
        # Add surface
        fig.add_trace(go.Surface(
            x=strikes,
            y=times * 365,  # Convert back to days for display
            z=surface_data,
            colorscale=colorscale,
            showscale=True,
            name=f"{option_type} {surface_type}",
            hovertemplate=f'<b>Strike:</b> $%{{x:.2f}}<br><b>Days:</b> %{{y:.0f}}<br><b>{z_title}:</b> %{{z:.4f}}<extra></extra>'
        ))
        
        # Add current option point if checkbox is selected
        if show_current_point:
            fig.add_trace(go.Scatter3d(
                x=[K],
                y=[T * 365],  # Convert to days
                z=[current_z],
                mode='markers',
                marker=dict(
                    size=12,
                    color='red',
                    symbol='diamond',
                    line=dict(color='darkred', width=2)
                ),
                name=f"Current {option_type}",
                showlegend=True,
                hovertemplate=f'<b>Current {option_type}</b><br>Strike: ${K:.2f}<br>Days: {T*365:.0f}<br>{z_title}: {current_z:.4f}<extra></extra>'
            ))
        
        fig.update_layout(
            title=f'{surface_title}{f" - {stock_symbol}" if stock_symbol else ""}<br>Spot: ${S:.2f}, Vol: {sigma*100:.1f}%, Rate: {r*100:.1f}%',
            scene=dict(
                xaxis_title='Strike Price ($)',
                yaxis_title='Days to Expiration',
                zaxis_title=z_title,
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5)
                )
            ),
            height=600,
            margin=dict(l=0, r=0, b=0, t=80),
            # Add animation configuration for smoother transitions
            transition=dict(
                duration=300,
                easing="cubic-in-out"
            )
        )
        
        st.plotly_chart(fig, use_container_width=True, key=f"surface_plot_{surface_type}")
        
        # Educational note about volatility surface
        if surface_type == "Volatility Surface":
            st.info(
                "Educational Note: In the Black-Scholes model, volatility is assumed to be constant across all strikes and expiration dates. "
                "This is why the volatility surface is completely flat. In reality, market-observed implied volatilities show patterns like volatility smile/skew. "
                "Check the 'Volatility Surface' tab to see realistic implied volatility patterns."
            )

def implied_volatility_calculator():
    st.header("Implied Volatility Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Input Parameters")
        
        # Stock selection
        st.markdown("**Stock Selection**")
        use_stock_symbol_iv = st.checkbox("Use specific stock symbol", value=False, key="iv_use_symbol")
        
        if use_stock_symbol_iv:
            stock_symbol_iv = st.text_input("Stock Symbol (e.g., AAPL, MSFT, SPY)", value="AAPL", key="iv_symbol").upper()
            
            if stock_symbol_iv:
                with st.spinner(f"Fetching data for {stock_symbol_iv}..."):
                    iv_current_price, iv_company_name, iv_hist_vol = get_stock_data(stock_symbol_iv)
                
                if iv_current_price is not None:
                    st.success(f"✓ {iv_company_name} ({stock_symbol_iv})")
                    st.info(f"Current Price: ${iv_current_price:.2f}")
                    
                    iv_price_label = f"{stock_symbol_iv} Price"
                    market_price_label = f"{stock_symbol_iv} Option Price ($)"
                    iv_default_price = float(iv_current_price)
                else:
                    st.error(f"Could not fetch data for {stock_symbol_iv}")
                    iv_price_label = f"{stock_symbol_iv} Price ($)"
                    market_price_label = f"{stock_symbol_iv} Option Price ($)"
                    iv_default_price = 100.0
                    stock_symbol_iv = None
            else:
                iv_price_label = "Stock Price ($)"
                market_price_label = "Option Price ($)"
                iv_default_price = 100.0
                stock_symbol_iv = None
        else:
            stock_symbol_iv = None
            iv_price_label = "Current Stock Price ($)"
            market_price_label = "Market Option Price ($)"
            iv_default_price = 100.0
        
        st.markdown("**Option Parameters**")
        market_price = st.number_input(market_price_label, value=5.0, min_value=0.01)
        S = st.number_input(iv_price_label, value=iv_default_price, min_value=0.01, key="iv_S")
        K = st.number_input("Strike Price ($)", value=iv_default_price, min_value=0.01, key="iv_K")
        T = st.number_input("Time to Expiration (years)", value=0.25, min_value=0.001, key="iv_T")
        r = st.number_input("Risk-free Rate (%)", value=5.0, min_value=0.0, key="iv_r") / 100
        option_type = st.radio("Option Type", ["Call", "Put"], key="iv_type")
    
    with col2:
        st.subheader("Results")
        iv = implied_volatility(market_price, S, K, T, r, option_type.lower())
        
        if not np.isnan(iv):
            st.metric("Implied Volatility", f"{iv*100:.2f}%")
            
            # Calculate theoretical price with implied vol
            if option_type == "Call":
                theoretical_price = black_scholes_call(S, K, T, r, iv)
            else:
                theoretical_price = black_scholes_put(S, K, T, r, iv)
            
            st.metric("Theoretical Price", f"${theoretical_price:.4f}")
            st.metric("Price Difference", f"${abs(market_price - theoretical_price):.4f}")
        else:
            st.error("Could not calculate implied volatility. Check input parameters.")

def volatility_surface():
    st.header("Market Implied Volatility Surface")
    st.markdown("*Realistic volatility patterns with smile/skew effects - separate from Black-Scholes*")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Market Parameters")
        
        # Stock selection for volatility surface
        st.markdown("**Stock Selection**")
        use_market_symbol = st.checkbox("Use specific stock symbol", value=False, key="market_use_symbol")
        
        if use_market_symbol:
            market_symbol = st.text_input("Stock Symbol (e.g., AAPL, MSFT, SPY)", value="AAPL", key="market_symbol").upper()
            
            if market_symbol:
                with st.spinner(f"Fetching data for {market_symbol}..."):
                    market_current_price, market_company_name, market_hist_vol = get_stock_data(market_symbol)
                
                if market_current_price is not None:
                    st.success(f"✓ {market_company_name} ({market_symbol})")
                    st.info(f"Current Price: ${market_current_price:.2f}")
                    if market_hist_vol is not None:
                        st.info(f"30-day Historical Vol: {market_hist_vol*100:.1f}%")
                    
                    market_price_label = f"{market_symbol} Spot Price"
                    market_default_price = float(market_current_price)
                    market_default_vol = int(market_hist_vol*100) if market_hist_vol is not None else 20
                else:
                    st.error(f"Could not fetch data for {market_symbol}")
                    market_price_label = f"{market_symbol} Spot Price ($)"
                    market_default_price = 100.0
                    market_default_vol = 20
                    market_symbol = None
            else:
                market_price_label = "Spot Price ($)"
                market_default_price = 100.0
                market_default_vol = 20
                market_symbol = None
        else:
            market_symbol = None
            market_price_label = "Market Spot Price ($)"
            market_default_price = 100.0
            market_default_vol = 20
        
        st.markdown("**Price Parameters**")
        market_spot = st.number_input(market_price_label, value=market_default_price, min_value=0.01, key="market_spot")
        
        # Strike range
        market_strike_min = st.number_input("Min Strike (%)", value=80, min_value=1, key="market_strike_min")
        market_strike_max = st.number_input("Max Strike (%)", value=120, min_value=1, key="market_strike_max")
        
        # Time range
        market_days_min = st.number_input("Min Days to Expiry", value=7, min_value=1, key="market_days_min")
        market_days_max = st.number_input("Max Days to Expiry", value=365, min_value=1, key="market_days_max")
        
        st.divider()
        st.subheader("Volatility Smile Parameters")
        
        # Volatility smile parameters
        market_base_vol = st.slider("Base Volatility (%)", 10, 50, market_default_vol, key="market_base_vol") / 100
        market_skew = st.slider("Volatility Skew", -0.1, 0.1, -0.02, 0.01, key="market_skew", 
                               help="Negative skew means OTM puts have higher IV than OTM calls")
        market_smile = st.slider("Volatility Smile", 0.0, 0.1, 0.02, 0.01, key="market_smile",
                                help="Positive smile means both OTM puts and calls have higher IV")
        
        # Term structure effect
        term_structure = st.slider("Term Structure Effect", -0.05, 0.05, 0.01, 0.005, key="market_term_structure",
                                  help="How volatility changes with time to expiration")
    
    with col2:
        # Generate market volatility surface data
        market_strikes = np.linspace(market_spot * market_strike_min/100, market_spot * market_strike_max/100, 25)
        market_days = np.linspace(market_days_min, market_days_max, 20)
        
        market_vol_surface = np.zeros((len(market_days), len(market_strikes)))
        
        for i, day in enumerate(market_days):
            for j, strike in enumerate(market_strikes):
                # Calculate moneyness (log-strike relative to spot)
                moneyness = np.log(strike / market_spot)
                
                # Time factor for term structure
                time_factor = np.sqrt(day / 365)
                
                # Market volatility model with smile/skew
                vol = (market_base_vol + 
                      market_skew * moneyness + 
                      market_smile * moneyness**2 +
                      term_structure * time_factor)
                
                # Ensure volatility is positive
                market_vol_surface[i, j] = max(vol, 0.05)  # Minimum 5% vol
        
        # Create 3D surface plot for market volatility
        market_fig = go.Figure()
        
        market_fig.add_trace(go.Surface(
            x=market_strikes,
            y=market_days,
            z=market_vol_surface * 100,
            colorscale='Plasma',
            showscale=True,
            name="Market Implied Volatility",
            hovertemplate='<b>Strike:</b> $%{x:.2f}<br><b>Days:</b> %{y:.0f}<br><b>Implied Vol:</b> %{z:.2f}%<extra></extra>'
        ))
        
        market_fig.update_layout(
            title=f'Market Implied Volatility Surface{f" - {market_symbol}" if market_symbol else ""}<br>Spot: ${market_spot:.2f}, Base Vol: {market_base_vol*100:.1f}%',
            scene=dict(
                xaxis_title='Strike Price ($)',
                yaxis_title='Days to Expiration',
                zaxis_title='Implied Volatility (%)',
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5)
                )
            ),
            height=600,
            margin=dict(l=0, r=0, b=0, t=80)
        )
        
        st.plotly_chart(market_fig, use_container_width=True, key="market_volatility_surface")
        
        # Educational info about market volatility patterns
        st.info(
            "Market Reality: Unlike Black-Scholes' flat volatility assumption, real markets show:\n"
            "- **Volatility Smile**: Higher IV for OTM options\n"
            "- **Volatility Skew**: Different IV for puts vs calls\n"
            "- **Term Structure**: IV varies with time to expiration\n"
            "- **Sticky Strike**: IV tends to follow strike levels rather than moneyness"
        )

# Main app
def main():
    st.title("Options & Volatility Dashboard")
    st.markdown("Professional options trading and volatility analysis tools")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    tool = st.sidebar.radio(
        "Select Tool",
        ["Black-Scholes Calculator", "Implied Volatility", "Volatility Surface"]
    )
    
    if tool == "Black-Scholes Calculator":
        black_scholes_calculator()
    elif tool == "Implied Volatility":
        implied_volatility_calculator()
    elif tool == "Volatility Surface":
        volatility_surface()

if __name__ == "__main__":
    main()
