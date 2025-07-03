# Options & Volatility Dashboard

A professional Python webapp for options pricing and volatility analysis.

## Live Demo

[Access the live app here](https://optionsandsuch.streamlit.app)

Now live and accessible to anyone worldwide.

## Features

1. Black-Scholes Calculator: Calculate option prices and Greeks
2. Implied Volatility Calculator: Extract implied volatility from market prices
3. Volatility Surface: Visualise 3D volatility surfaces

## Deployment Status

Successfully deployed on Streamlit Community Cloud.
Live URL: https://optionsandsuch.streamlit.app
Status: Ready for public use

## Local Development

### Installation

```bash
pip install -r requirements.txt
```

### Usage

```bash
streamlit run app.py
```

Open your browser to `http://localhost:8501` to access the dashboard.

## Tools Overview

- Black-Scholes: Classic option pricing with Delta, Gamma, Theta, and Vega
- Implied Vol: Reverse-engineer volatility from market option prices
- Vol Surface: Interactive 3D visualisation of volatility across strikes and expiries