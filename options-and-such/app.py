import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from scipy.stats import norm
from scipy.optimize import brentq
from datetime import datetime, timedelta

__author__ = "https://github.com/theredplanetsings"
__date__ = "20/6/2025"

st.set_page_config(page_title="Options & Volatility Dashboard", layout="wide")

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
    st.header("📊 Black-Scholes Option Pricing Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Input Parameters")
        S = st.number_input("Current Stock Price ($)", value=100.0, min_value=0.01)
        K = st.number_input("Strike Price ($)", value=100.0, min_value=0.01)
        T = st.number_input("Time to Expiration (years)", value=0.25, min_value=0.001)
        r = st.number_input("Risk-free Rate (%)", value=5.0, min_value=0.0) / 100
        sigma = st.number_input("Volatility (%)", value=20.0, min_value=0.1) / 100
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

def implied_volatility_calculator():
    st.header("🔍 Implied Volatility Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Input Parameters")
        market_price = st.number_input("Market Option Price ($)", value=5.0, min_value=0.01)
        S = st.number_input("Current Stock Price ($)", value=100.0, min_value=0.01, key="iv_S")
        K = st.number_input("Strike Price ($)", value=100.0, min_value=0.01, key="iv_K")
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
    st.header("📈 Volatility Surface Visualization")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Parameters")
        spot_price = st.number_input("Spot Price ($)", value=100.0, min_value=0.01, key="vs_spot")
        
        # Strike range
        strike_min = st.number_input("Min Strike (%)", value=80, min_value=1, key="vs_strike_min")
        strike_max = st.number_input("Max Strike (%)", value=120, min_value=1, key="vs_strike_max")
        
        # Time range
        days_min = st.number_input("Min Days to Expiry", value=7, min_value=1, key="vs_days_min")
        days_max = st.number_input("Max Days to Expiry", value=365, min_value=1, key="vs_days_max")
        
        # Volatility smile parameters
        base_vol = st.slider("Base Volatility (%)", 10, 50, 20, key="vs_base_vol") / 100
        skew = st.slider("Volatility Skew", -0.1, 0.1, -0.02, 0.01, key="vs_skew")
        smile = st.slider("Volatility Smile", 0.0, 0.1, 0.02, 0.01, key="vs_smile")
    
    with col2:
        # Generate volatility surface data
        strikes = np.linspace(spot_price * strike_min/100, spot_price * strike_max/100, 20)
        days = np.linspace(days_min, days_max, 15)
        
        vol_surface = np.zeros((len(days), len(strikes)))
        
        for i, day in enumerate(days):
            for j, strike in enumerate(strikes):
                moneyness = np.log(strike / spot_price)
                time_factor = np.sqrt(day / 365)
                
                # Simple volatility smile model
                vol = base_vol + skew * moneyness + smile * moneyness**2
                vol_surface[i, j] = vol
        
        # Create 3D surface plot
        fig = go.Figure(data=[go.Surface(
            x=strikes,
            y=days,
            z=vol_surface * 100,
            colorscale='Viridis',
            showscale=True
        )])
        
        fig.update_layout(
            title='Implied Volatility Surface',
            scene=dict(
                xaxis_title='Strike Price ($)',
                yaxis_title='Days to Expiration',
                zaxis_title='Implied Volatility (%)'
            ),
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Main app
def main():
    st.title("🎯 Options & Volatility Dashboard")
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
