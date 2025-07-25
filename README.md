# Options & Volatility Dashboard

A comprehensive Python web application for professional options pricing and volatility analysis, featuring real-time market data integration and advanced visualisation tools.

## Live Demo

[Access the live application here](https://optionsandsuch.streamlit.app)

Now live and accessible worldwide for educational and analytical purposes.

## Key Features

### 1. Black-Scholes Option Pricing Calculator
- **Real-time stock data integration** via Yahoo Finance API
- **Complete option pricing** with theoretical values for calls and puts
- **Full Greeks calculation**: Delta, Gamma, Theta, and Vega
- **Interactive 3D surfaces**: Price surfaces and volatility surfaces
- **Historical volatility analysis** with 30-day rolling calculations

### 2. Implied Volatility Calculator
- **Market-to-model analysis** extracting implied volatility from real option prices
- **Theoretical vs market pricing** comparison
- **Real-time stock price integration** for accurate calculations
- **Error analysis** showing pricing discrepancies

### 3. Market Volatility Surface Visualisation
- **Realistic volatility patterns** with smile and skew effects
- **Interactive 3D visualisation** across strikes and expiration dates
- **Customisable parameters** for volatility smile, skew, and term structure
- **Educational comparison** with flat Black-Scholes assumptions

## Technical Features

- **Live market data** fetched automatically via yfinance
- **Professional-grade calculations** using scipy optimisation
- **Interactive 3D plotting** with Plotly graphics
- **Real-time updates** with minimal latency
- **Educational tooltips** explaining theoretical vs market differences
- **Clean, professional interface** optimised for analysis

## Deployment Status

Successfully deployed on Streamlit Community Cloud.
- **Live URL**: https://optionsandsuch.streamlit.app
- **Status**: Production ready for public use
- **Availability**: 24/7 global access

## Local Development

### Prerequisites

- Python 3.8 or higher
- Internet connection for market data

### Installation

```bash
git clone https://github.com/theredplanetsings/options-and-such.git
cd options-and-such
pip install -r requirements.txt
```

### Usage

```bash
streamlit run app.py
```

Open your browser to `http://localhost:8501` to access the dashboard locally.

## Educational Value

This tool bridges the gap between theoretical options pricing models and real market behaviour:

- **Black-Scholes Theory**: Demonstrates the classical model with constant volatility assumptions
- **Market Reality**: Shows how implied volatility varies across strikes and time
- **Practical Application**: Uses real stock symbols and current market prices
- **Professional Context**: Suitable for finance students, traders, and quantitative analysts

## Dependencies

- **Streamlit**: Web application framework
- **NumPy/Pandas**: Numerical computing and data manipulation
- **SciPy**: Scientific computing for optimisation algorithms
- **Plotly**: Interactive 3D visualisation
- **yfinance**: Real-time financial market data
- **Yahoo Finance API**: Live stock prices and historical data

## Contributing

This project is open for educational use and contributions. Feel free to submit issues or pull requests to enhance functionality.