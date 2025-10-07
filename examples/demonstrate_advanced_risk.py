#!/usr/bin/env python3
"""
Demonstration of Advanced Risk Management Features

This script demonstrates the new advanced risk management features:
1. Machine learning-based correlation prediction
2. VaR (Value at Risk) calculations
3. Multi-timeframe volatility analysis
4. Dynamic risk-reward ratio adjustment
"""

import sys
import numpy as np
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, '/home/runner/work/Sentio-2.0/Sentio-2.0')

from sentio.risk.risk_manager import RiskManager


def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def demonstrate_ml_correlation():
    """Demonstrate ML-based correlation prediction"""
    print_section("1. Machine Learning-Based Correlation Prediction")
    
    config = {
        'enable_ml_correlation': True,
        'min_risk_reward_ratio': 2.0,
    }
    
    risk_manager = RiskManager(config=config)
    
    # Simulate building correlation training data
    print("Building correlation training data...")
    for i in range(30):
        same_sector = i % 2 == 0
        actual_corr = 0.8 if same_sector else 0.3 + np.random.rand() * 0.3
        
        risk_manager.correlation_training_data.append({
            'same_sector': same_sector,
            'volatility_similarity': 0.7 + np.random.rand() * 0.2,
            'price_correlation': actual_corr + np.random.randn() * 0.1,
            'volume_correlation': 0.5 + np.random.rand() * 0.2,
            'market_cap_ratio': 1.0,
            'actual_correlation': actual_corr
        })
    
    print(f"✓ Collected {len(risk_manager.correlation_training_data)} correlation samples")
    
    # Train the model
    print("\nTraining ML correlation model...")
    risk_manager.train_correlation_model()
    
    if risk_manager.correlation_model is not None:
        print("✓ Model trained successfully")
        
        # Test prediction
        trade = {'symbol': 'AAPL', 'sector': 'technology'}
        position = {'symbol': 'MSFT', 'sector': 'technology'}
        
        predicted_corr = risk_manager.predict_correlation(trade, position)
        print(f"\nPrediction for AAPL vs MSFT (same sector):")
        print(f"  Predicted correlation: {predicted_corr:.2f}")
        print(f"  Interpretation: {'High' if predicted_corr > 0.7 else 'Moderate' if predicted_corr > 0.4 else 'Low'} correlation")
    else:
        print("✗ Model training failed")


def demonstrate_var_calculation():
    """Demonstrate VaR calculations"""
    print_section("2. Value at Risk (VaR) Calculations")
    
    config = {
        'enable_var_calculation': True,
        'var_confidence_level': 0.95,
    }
    
    risk_manager = RiskManager(config=config)
    risk_manager.daily_start_value = 100000
    
    # Simulate trading history
    print("Simulating 60 trades with varying P&L...")
    np.random.seed(42)  # For reproducibility
    
    for i in range(60):
        # Simulate realistic P&L distribution
        pnl = np.random.normal(150, 400)  # Mean profit $150, std dev $400
        risk_manager.close_position(f'TRADE_{i}', pnl)
    
    print(f"✓ Generated {len(risk_manager.trade_history)} trades")
    
    # Calculate VaR
    print("\nCalculating Value at Risk...")
    var_95 = risk_manager.calculate_portfolio_var(confidence_level=0.95)
    var_99 = risk_manager.calculate_portfolio_var(confidence_level=0.99)
    
    portfolio_value = 100000
    var_95_pct = risk_manager.calculate_parametric_var(portfolio_value, 0.95)
    var_99_pct = risk_manager.calculate_parametric_var(portfolio_value, 0.99)
    
    print(f"\nVaR Results:")
    print(f"  95% VaR: ${var_95:.2f} ({var_95_pct*100:.2f}% of portfolio)")
    print(f"  99% VaR: ${var_99:.2f} ({var_99_pct*100:.2f}% of portfolio)")
    print(f"\nInterpretation:")
    print(f"  We are 95% confident that daily loss will not exceed ${var_95:.2f}")
    print(f"  We are 99% confident that daily loss will not exceed ${var_99:.2f}")


def demonstrate_multi_timeframe_volatility():
    """Demonstrate multi-timeframe volatility analysis"""
    print_section("3. Multi-Timeframe Volatility Analysis")
    
    config = {
        'enable_multi_timeframe_volatility': True,
    }
    
    risk_manager = RiskManager(config=config)
    
    # Simulate price history across different timeframes
    symbol = 'AAPL'
    print(f"Simulating price history for {symbol}...")
    
    now = datetime.now()
    base_price = 150.0
    
    # Simulate 200 hours of price data (includes data for all timeframes)
    for i in range(200):
        timestamp = now - timedelta(hours=200-i)
        # Add some volatility that increases over time
        volatility = 1.0 + (i / 200) * 2.0  # Increasing volatility
        price = base_price + np.random.normal(0, volatility)
        risk_manager.price_history[symbol].append((timestamp, price))
    
    print(f"✓ Generated {len(risk_manager.price_history[symbol])} price points")
    
    # Calculate multi-timeframe volatility
    print("\nCalculating multi-timeframe volatility...")
    vol_data = risk_manager.calculate_multi_timeframe_volatility(symbol)
    
    print(f"\nVolatility Analysis for {symbol}:")
    print(f"  1-hour volatility:  {vol_data['1h']:.4f}")
    print(f"  1-day volatility:   {vol_data['1d']:.4f}")
    print(f"  1-week volatility:  {vol_data['1w']:.4f}")
    
    # Detect volatility regime
    regime = risk_manager.detect_volatility_regime(symbol)
    print(f"\nVolatility Regime: {regime.upper()}")
    
    regime_descriptions = {
        'low': 'Market is stable with low price fluctuations',
        'normal': 'Market showing typical volatility levels',
        'high': 'Market is experiencing high volatility - use caution'
    }
    print(f"  {regime_descriptions.get(regime, 'Unknown')}")
    
    # Show how this affects risk assessment
    trade = {'symbol': symbol, 'sector': 'technology'}
    vol_risk = risk_manager._assess_volatility_risk(trade)
    print(f"\nVolatility Risk Score: {vol_risk:.2f} (0=low, 1=high)")


def demonstrate_dynamic_rr_adjustment():
    """Demonstrate dynamic risk-reward ratio adjustment"""
    print_section("4. Dynamic Risk-Reward Ratio Adjustment")
    
    config = {
        'enable_dynamic_rr_adjustment': True,
        'min_risk_reward_ratio': 2.0,
    }
    
    risk_manager = RiskManager(config=config)
    risk_manager.daily_start_value = 100000
    
    print(f"Base minimum R:R ratio: {config['min_risk_reward_ratio']:.1f}:1")
    
    # Scenario 1: High win rate
    print("\n--- Scenario 1: High Win Rate (70%) ---")
    for _ in range(14):
        risk_manager.close_position('WIN', 100)
    for _ in range(6):
        risk_manager.close_position('LOSS', -50)
    
    adjusted_rr = risk_manager.adjust_rr_ratio_dynamically()
    win_rate = risk_manager.get_win_rate()
    print(f"Win rate: {win_rate*100:.0f}%")
    print(f"Adjusted R:R ratio: {adjusted_rr:.2f}:1")
    print(f"Change: {(adjusted_rr/config['min_risk_reward_ratio'] - 1)*100:+.1f}%")
    
    # Scenario 2: Low win rate
    print("\n--- Scenario 2: Low Win Rate (40%) ---")
    risk_manager_2 = RiskManager(config=config)
    risk_manager_2.daily_start_value = 100000
    
    for _ in range(8):
        risk_manager_2.close_position('WIN', 100)
    for _ in range(12):
        risk_manager_2.close_position('LOSS', -50)
    
    adjusted_rr = risk_manager_2.adjust_rr_ratio_dynamically()
    win_rate = risk_manager_2.get_win_rate()
    print(f"Win rate: {win_rate*100:.0f}%")
    print(f"Adjusted R:R ratio: {adjusted_rr:.2f}:1")
    print(f"Change: {(adjusted_rr/config['min_risk_reward_ratio'] - 1)*100:+.1f}%")
    
    # Scenario 3: High volatility environment
    print("\n--- Scenario 3: High Volatility Environment ---")
    risk_manager_3 = RiskManager(config=config)
    risk_manager_3.daily_start_value = 100000
    
    # Add some trades
    for _ in range(10):
        risk_manager_3.close_position('WIN', 100)
    for _ in range(10):
        risk_manager_3.close_position('LOSS', -50)
    
    # Add high volatility data
    symbol = 'VOLATILE'
    now = datetime.now()
    for i in range(50):
        timestamp = now - timedelta(hours=50-i)
        price = 100 + np.random.normal(0, 8)  # High volatility
        risk_manager_3.price_history[symbol].append((timestamp, price))
    
    risk_manager_3.calculate_multi_timeframe_volatility(symbol)
    
    adjusted_rr = risk_manager_3.adjust_rr_ratio_dynamically()
    avg_vol = np.mean(list(risk_manager_3.volatility_1d.values()))
    print(f"Average volatility: {avg_vol:.4f}")
    print(f"Adjusted R:R ratio: {adjusted_rr:.2f}:1")
    print(f"Change: {(adjusted_rr/config['min_risk_reward_ratio'] - 1)*100:+.1f}%")


def demonstrate_integration():
    """Demonstrate how all features work together"""
    print_section("5. Integrated Risk Assessment")
    
    # Create risk manager with all features enabled
    config = {
        'enable_ml_correlation': True,
        'enable_var_calculation': True,
        'enable_multi_timeframe_volatility': True,
        'enable_dynamic_rr_adjustment': True,
        'min_risk_reward_ratio': 2.0,
        'max_position_size': 0.05,
        'max_correlation': 0.7,
    }
    
    risk_manager = RiskManager(config=config)
    risk_manager.daily_start_value = 100000
    
    print("Setting up trading environment...")
    
    # Build some trading history
    for i in range(40):
        pnl = np.random.normal(100, 300)
        risk_manager.close_position(f'TRADE_{i}', pnl)
    
    # Add price history for a symbol
    symbol = 'AAPL'
    now = datetime.now()
    for i in range(150):
        timestamp = now - timedelta(hours=150-i)
        price = 150 + np.random.normal(0, 2)
        risk_manager.price_history[symbol].append((timestamp, price))
    
    print("✓ Trading history and price data initialized")
    
    # Assess a trade
    print("\nAssessing a new trade:")
    trade = {
        'symbol': symbol,
        'price': 150,
        'size': 100,
        'direction': 'long',
        'stop_loss': 147,
        'take_profit': 156,
        'sector': 'technology'
    }
    
    print(f"  Symbol: {trade['symbol']}")
    print(f"  Entry: ${trade['price']}")
    print(f"  Stop Loss: ${trade['stop_loss']}")
    print(f"  Take Profit: ${trade['take_profit']}")
    print(f"  Size: {trade['size']} shares")
    
    result = risk_manager.assess_trade_risk(
        trade=trade,
        portfolio_value=100000,
        current_exposure=0
    )
    
    print(f"\nRisk Assessment Result:")
    print(f"  Approved: {result.approved}")
    print(f"  Risk Level: {result.risk_level.value}")
    print(f"  Warnings: {len(result.warnings)}")
    if result.warnings:
        for warning in result.warnings:
            print(f"    - {warning}")
    
    # Show enhanced metrics
    print("\nEnhanced Risk Metrics:")
    metrics = risk_manager.get_risk_metrics()
    
    print(f"  Win Rate: {metrics['win_rate']*100:.1f}%")
    print(f"  Expectancy: ${metrics['expectancy']:.2f}")
    
    if 'portfolio_var' in metrics:
        print(f"  Portfolio VaR (95%): ${metrics['portfolio_var']:.2f}")
    
    if 'current_min_rr_ratio' in metrics:
        print(f"  Current Min R:R: {metrics['current_min_rr_ratio']:.2f}:1")
    
    if 'avg_volatility_1d' in metrics:
        print(f"  Avg Daily Volatility: {metrics['avg_volatility_1d']:.4f}")


def main():
    """Main demonstration function"""
    print("\n" + "=" * 80)
    print("  SENTIO - Advanced Risk Management Features Demonstration")
    print("=" * 80)
    
    try:
        demonstrate_ml_correlation()
        demonstrate_var_calculation()
        demonstrate_multi_timeframe_volatility()
        demonstrate_dynamic_rr_adjustment()
        demonstrate_integration()
        
        print("\n" + "=" * 80)
        print("  Demonstration Complete!")
        print("=" * 80)
        print("\nAll advanced risk management features are working correctly.")
        print("See ADVANCED_RISK_FEATURES.md for detailed documentation.\n")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
