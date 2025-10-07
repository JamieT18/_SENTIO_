# Sentio API

This module exposes Sentio analytics, risk, strategy, and backtesting features via REST endpoints using FastAPI.

## Endpoints
- `/risk/var` — Calculate Value at Risk (VaR)
- `/risk/cvar` — Calculate Conditional Value at Risk (CVaR)
- `/risk/dynamic` — ML-based dynamic risk model
- `/analysis/candlestick` — ML-based candlestick pattern recognition
- `/analysis/chart` — ML-based chart pattern recognition
- `/backtest/basic` — Run basic backtest
- `/backtest/multi` — Run multi-strategy walk-forward backtest

## Usage
Install dependencies:
```
pip install -r requirements-api.txt
```
Run the API server:
```
uvicorn sentio.api.main:app --reload
```
