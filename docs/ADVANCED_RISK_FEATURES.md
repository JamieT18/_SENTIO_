# Advanced Risk Management Features

## Overview

This document describes the advanced risk management features added to Sentio 2.0, including machine learning-based correlation prediction, Value at Risk (VaR) calculations, multi-timeframe volatility analysis, and dynamic risk-reward ratio adjustment.

## Features

### 1. Machine Learning-Based Correlation Prediction

**Purpose:** Predict correlations between assets using historical data and machine learning to improve portfolio diversification.

**Implementation:**
- Uses scikit-learn's Ridge regression model
- Features include:
  - Same sector indicator
  - Volatility similarity
  - Historical price correlation
  - Volume correlation (placeholder for future enhancement)
  - Market cap ratio (placeholder for future enhancement)
- Automatically collects training data from observed correlations
- Retrains model every 50 new observations
- Falls back to traditional correlation when ML model not available

**Benefits:**
- More accurate correlation predictions with limited historical data
- Learns patterns from multiple features beyond just price movements
- Improves over time as more data is collected
- Helps prevent over-concentration in correlated assets

**Configuration:**
```python
config = {
    'enable_ml_correlation': True,  # Enable ML-based correlation prediction
}
```

**Usage Example:**
```python
from sentio.risk.risk_manager import RiskManager

risk_manager = RiskManager(config={'enable_ml_correlation': True})

# ML model trains automatically as correlation data is collected
# Predictions are used automatically in correlation risk assessment
```

### 2. VaR (Value at Risk) Calculations

**Purpose:** Calculate the maximum expected loss over a given time period at a specified confidence level.

**Implementation:**
- **Historical VaR:** Uses actual historical returns to calculate VaR
- **Parametric VaR:** Uses statistical distribution (mean, std dev, z-score)
- Combines both methods for more robust estimates
- Configurable confidence levels (90%, 95%, 99%)
- Tracks VaR history for monitoring trends

**Benefits:**
- Quantifies portfolio risk in dollar terms
- Industry-standard risk metric
- Useful for regulatory compliance
- Helps set appropriate position sizes

**Configuration:**
```python
config = {
    'enable_var_calculation': True,  # Enable VaR calculations
    'var_confidence_level': 0.95,    # 95% confidence level
    'var_time_horizon': 1,           # 1-day VaR
}
```

**Usage Example:**
```python
from sentio.risk.risk_manager import RiskManager

risk_manager = RiskManager(config={
    'enable_var_calculation': True,
    'var_confidence_level': 0.95
})

# Build trading history (need at least 30 trades)
for i in range(50):
    risk_manager.close_position(f'TRADE_{i}', pnl)

# Calculate VaR
var = risk_manager.calculate_portfolio_var()
print(f"Portfolio VaR (95%): ${var:.2f}")

# Get VaR as percentage of portfolio
var_percent = risk_manager.calculate_parametric_var(portfolio_value=100000)
print(f"Portfolio VaR: {var_percent*100:.2f}%")

# VaR is also included in risk metrics
metrics = risk_manager.get_risk_metrics()
print(f"Current VaR: ${metrics['portfolio_var']:.2f}")
```

**Interpretation:**
- A 95% VaR of $5,000 means: "We are 95% confident that our maximum loss over the next day will not exceed $5,000"
- Or equivalently: "There is a 5% chance our loss will exceed $5,000"

### 3. Multi-Timeframe Volatility Analysis

**Purpose:** Analyze volatility across multiple timeframes (1h, 1d, 1w) for better risk assessment.

**Implementation:**
- Calculates volatility separately for:
  - 1-hour timeframe (short-term volatility)
  - 1-day timeframe (medium-term volatility)
  - 1-week timeframe (long-term volatility)
- Weighted combination: 20% (1h) + 50% (1d) + 30% (1w)
- Volatility regime detection: low, normal, high
- Enhanced volatility risk assessment

**Benefits:**
- Captures both short-term spikes and long-term trends
- More comprehensive risk picture
- Better adaptation to changing market conditions
- Helps identify when markets are transitioning between regimes

**Configuration:**
```python
config = {
    'enable_multi_timeframe_volatility': True,  # Enable multi-timeframe analysis
}
```

**Usage Example:**
```python
from sentio.risk.risk_manager import RiskManager

risk_manager = RiskManager(config={'enable_multi_timeframe_volatility': True})

# Add price history with timestamps
symbol = 'AAPL'
risk_manager.price_history[symbol].append((datetime.now(), 150.0))
# ... add more price points over time

# Calculate multi-timeframe volatility
vol_data = risk_manager.calculate_multi_timeframe_volatility(symbol)
print(f"1h volatility: {vol_data['1h']:.4f}")
print(f"1d volatility: {vol_data['1d']:.4f}")
print(f"1w volatility: {vol_data['1w']:.4f}")

# Detect volatility regime
regime = risk_manager.detect_volatility_regime(symbol)
print(f"Volatility regime: {regime}")  # 'low', 'normal', or 'high'
```

**Volatility Regimes:**
- **Low:** < 1% daily volatility (stable markets)
- **Normal:** 1-4% daily volatility (typical markets)
- **High:** > 4% daily volatility (turbulent markets)

### 4. Dynamic Risk-Reward Ratio Adjustment

**Purpose:** Automatically adjust minimum risk-reward ratio requirements based on market conditions and performance.

**Implementation:**
- Adjusts based on three factors:
  1. **Win Rate:** High win rate → lower RR requirement, Low win rate → higher RR
  2. **Recent Performance:** Recent losses → increase RR requirement
  3. **Market Volatility:** High volatility → higher RR requirement
- Bounded between 1.5 and 3.5 to prevent extreme adjustments
- Applied automatically in trade risk assessment

**Benefits:**
- Adapts to changing market conditions
- Compensates for poor recent performance with higher standards
- Relaxes requirements when trading well
- More flexible than static RR ratios

**Configuration:**
```python
config = {
    'enable_dynamic_rr_adjustment': True,  # Enable dynamic RR adjustment
    'min_risk_reward_ratio': 2.0,          # Base minimum RR ratio
}
```

**Usage Example:**
```python
from sentio.risk.risk_manager import RiskManager

risk_manager = RiskManager(config={
    'enable_dynamic_rr_adjustment': True,
    'min_risk_reward_ratio': 2.0
})

# Build trading history
for _ in range(10):
    risk_manager.close_position('WIN', 100)
for _ in range(5):
    risk_manager.close_position('LOSS', -50)

# Get dynamically adjusted RR ratio
adjusted_rr = risk_manager.adjust_rr_ratio_dynamically()
print(f"Base RR: 2.0, Adjusted RR: {adjusted_rr:.2f}")

# Used automatically in trade assessment
trade = {
    'symbol': 'AAPL',
    'price': 150,
    'stop_loss': 148,
    'take_profit': 154,  # 2:1 RR
    # ...
}
result = risk_manager.assess_trade_risk(trade, portfolio_value=100000, current_exposure=0)
```

**Adjustment Logic:**
- **High win rate (>65%):** RR *= 0.9 (reduce by 10%)
- **Low win rate (<45%):** RR *= 1.2 (increase by 20%)
- **Recent losses:** RR *= 1.1 (increase by 10%)
- **High volatility (>4%):** RR *= 1.15 (increase by 15%)
- **Low volatility (<1.5%):** RR *= 0.95 (reduce by 5%)

## Integration

All features are integrated into the existing `RiskManager` and work seamlessly with existing risk controls:

```python
from sentio.risk.risk_manager import RiskManager

# Full configuration with all advanced features
config = {
    # Standard risk parameters
    'max_position_size': 0.05,
    'max_portfolio_risk': 0.20,
    'min_risk_reward_ratio': 2.0,
    
    # Advanced features (all enabled by default)
    'enable_ml_correlation': True,
    'enable_var_calculation': True,
    'enable_multi_timeframe_volatility': True,
    'enable_dynamic_rr_adjustment': True,
    'var_confidence_level': 0.95,
}

risk_manager = RiskManager(config=config)

# Use normally - advanced features work automatically
result = risk_manager.assess_trade_risk(
    trade={'symbol': 'AAPL', 'price': 150, 'size': 100, ...},
    portfolio_value=100000,
    current_exposure=0
)

# Enhanced metrics include new data
metrics = risk_manager.get_risk_metrics()
print(f"Portfolio VaR: ${metrics.get('portfolio_var', 0):.2f}")
print(f"Current min RR: {metrics.get('current_min_rr_ratio', 2.0):.2f}")
print(f"Avg 1d Volatility: {metrics.get('avg_volatility_1d', 0):.4f}")
```

## Performance Impact

- **Minimal overhead:** All calculations are O(1) or O(n) where n is typically < 100
- **Memory efficient:** Price history limited to 100 points per symbol
- **ML model training:** Only happens every 50 samples, takes < 100ms
- **VaR calculation:** Only when explicitly requested or in metrics
- **Multi-timeframe volatility:** Cached results, recalculated on demand

## Backward Compatibility

All features are fully backward compatible:
- **All features default to enabled** in new configurations
- **Existing code works unchanged**
- **No breaking changes** to existing APIs
- **Graceful fallbacks** when insufficient data
- **Optional features** can be disabled via config

## Testing

Comprehensive test suite includes:
- Multi-timeframe volatility calculation tests
- Volatility regime detection tests
- VaR calculation tests (both methods)
- Dynamic RR adjustment tests (multiple scenarios)
- ML correlation training and prediction tests
- Integration tests with existing risk assessment
- Edge cases and error handling

Run tests:
```bash
pytest sentio/tests/test_risk_manager.py -v
```

## Future Enhancements

Potential areas for further improvement:
1. **Advanced ML models:** Neural networks, ensemble methods
2. **More features:** Market cap, sector beta, fundamental ratios
3. **CVaR (Conditional VaR):** Expected loss beyond VaR threshold
4. **Stress testing:** Scenario analysis, historical event simulation
5. **Market regime detection:** Bull/bear/sideways classification
6. **Time-decay adjustments:** Different RR ratios by time of day
7. **Conditional correlations:** Time-varying correlation models
8. **Portfolio optimization:** Modern Portfolio Theory integration

## References

- **VaR Methodology:** Basel Committee on Banking Supervision
- **ML Correlation:** "Machine Learning for Asset Management" by Marcos López de Prado
- **Multi-timeframe Analysis:** "Evidence-Based Technical Analysis" by David Aronson
- **Dynamic Position Sizing:** "The New Trading for a Living" by Dr. Alexander Elder
