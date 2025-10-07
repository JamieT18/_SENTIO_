"""
Demonstration of enhanced risk management features
"""
from sentio.risk.risk_manager import RiskManager
from datetime import datetime
import numpy as np


def main():
    """Demonstrate the enhanced risk management features"""
    
    print("=" * 80)
    print("SENTIO - Enhanced Risk Management Demonstration")
    print("=" * 80)
    print()
    
    # Initialize risk manager
    config = {
        'max_position_size': 0.05,
        'max_portfolio_risk': 0.20,
        'stop_loss_percent': 0.02,
        'take_profit_percent': 0.05,
        'max_daily_drawdown': 0.03,
        'circuit_breaker_threshold': 0.05,
        'min_risk_reward_ratio': 2.0,
        'max_loss_per_trade': 0.01,
        'max_correlation': 0.7,
        'enable_kelly_criterion': True,
        'max_sector_concentration': 0.30
    }
    
    risk_manager = RiskManager(config=config)
    risk_manager.daily_start_value = 100000
    
    print("1. INITIAL CONFIGURATION")
    print("-" * 80)
    print(f"   Max Position Size: {config['max_position_size']*100}%")
    print(f"   Min Risk-Reward Ratio: {config['min_risk_reward_ratio']}:1")
    print(f"   Max Loss Per Trade: {config['max_loss_per_trade']*100}%")
    print(f"   Max Sector Concentration: {config['max_sector_concentration']*100}%")
    print(f"   Kelly Criterion: {'Enabled' if config['enable_kelly_criterion'] else 'Disabled'}")
    print()
    
    # Simulate adding price history for volatility calculation
    print("2. ADDING PRICE HISTORY FOR VOLATILITY ASSESSMENT")
    print("-" * 80)
    
    symbols = ['AAPL', 'MSFT', 'GOOGL']
    base_prices = {'AAPL': 150, 'MSFT': 300, 'GOOGL': 100}
    
    for symbol in symbols:
        base_price = base_prices[symbol]
        for i in range(50):
            # Simulate price movement with varying volatility
            volatility = 0.02 if symbol == 'AAPL' else 0.04
            price = base_price + np.random.normal(0, base_price * volatility)
            risk_manager.price_history[symbol].append((datetime.now(), price))
        
        print(f"   Added 50 price points for {symbol}")
    print()
    
    # Test 1: Good trade with proper risk-reward ratio
    print("3. ASSESSING GOOD TRADE (High R:R, Low Volatility)")
    print("-" * 80)
    
    trade1 = {
        'symbol': 'AAPL',
        'price': 150,
        'size': 100,
        'direction': 'long',
        'stop_loss': 147,  # 2% stop loss
        'take_profit': 159,  # 6% take profit (3:1 R:R)
        'sector': 'technology'
    }
    
    result1 = risk_manager.assess_trade_risk(
        trade=trade1,
        portfolio_value=100000,
        current_exposure=0
    )
    
    print(f"   Trade: {trade1['symbol']} @ ${trade1['price']}")
    print(f"   Stop Loss: ${trade1['stop_loss']} | Take Profit: ${trade1['take_profit']}")
    print(f"   Approved: {result1.approved}")
    print(f"   Risk Level: {result1.risk_level.value}")
    print(f"   Warnings: {len(result1.warnings)}")
    if result1.warnings:
        for warning in result1.warnings:
            print(f"      - {warning}")
    print()
    
    # Add position to portfolio
    risk_manager.update_position({
        'symbol': 'AAPL',
        'price': 150,
        'size': 100,
        'value': 15000,
        'sector': 'technology',
        'current_price': 150
    })
    
    # Test 2: Poor risk-reward ratio
    print("4. ASSESSING POOR TRADE (Low R:R)")
    print("-" * 80)
    
    trade2 = {
        'symbol': 'MSFT',
        'price': 300,
        'size': 50,
        'direction': 'long',
        'stop_loss': 297,  # 1% stop loss
        'take_profit': 301.5,  # 0.5% take profit (0.5:1 R:R - bad!)
        'sector': 'technology'
    }
    
    result2 = risk_manager.assess_trade_risk(
        trade=trade2,
        portfolio_value=100000,
        current_exposure=15000
    )
    
    print(f"   Trade: {trade2['symbol']} @ ${trade2['price']}")
    print(f"   Stop Loss: ${trade2['stop_loss']} | Take Profit: ${trade2['take_profit']}")
    print(f"   Approved: {result2.approved}")
    print(f"   Risk Level: {result2.risk_level.value}")
    print(f"   Warnings: {len(result2.warnings)}")
    if result2.warnings:
        for warning in result2.warnings:
            print(f"      - {warning}")
    print()
    
    # Test 3: Sector concentration violation
    print("5. TESTING SECTOR CONCENTRATION LIMITS")
    print("-" * 80)
    
    trade3 = {
        'symbol': 'GOOGL',
        'price': 100,
        'size': 200,  # Large position
        'direction': 'long',
        'sector': 'technology'  # Same sector as AAPL
    }
    
    result3 = risk_manager.assess_trade_risk(
        trade=trade3,
        portfolio_value=100000,
        current_exposure=15000
    )
    
    print(f"   Trade: {trade3['symbol']} @ ${trade3['price']}")
    print(f"   Existing Tech Exposure: $15,000 (15%)")
    print(f"   New Position Value: $20,000 (20%)")
    print(f"   Total Tech Exposure: $35,000 (35%)")
    print(f"   Approved: {result3.approved}")
    print(f"   Risk Level: {result3.risk_level.value}")
    if result3.reasons:
        for reason in result3.reasons:
            print(f"   Rejection Reason: {reason}")
    print()
    
    # Simulate trading history
    print("6. BUILDING TRADING HISTORY")
    print("-" * 80)
    
    # Simulate 25 trades with 60% win rate
    for i in range(15):
        risk_manager.close_position(f'WIN_{i}', 100 + np.random.normal(0, 20))
    for i in range(10):
        risk_manager.close_position(f'LOSS_{i}', -(50 + np.random.normal(0, 10)))
    
    print(f"   Simulated 25 trades (15 wins, 10 losses)")
    print()
    
    # Display performance metrics
    print("7. PERFORMANCE METRICS")
    print("-" * 80)
    
    metrics = risk_manager.get_risk_metrics()
    
    print(f"   Win Rate: {metrics['win_rate']*100:.1f}%")
    print(f"   Total Trades: {metrics['total_trades']}")
    print(f"   Average Win: ${metrics['avg_win']:.2f}")
    print(f"   Average Loss: ${metrics['avg_loss']:.2f}")
    print(f"   Expectancy: ${metrics['expectancy']:.2f} per trade")
    print(f"   Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
    print()
    
    # Test Kelly Criterion
    print("8. KELLY CRITERION POSITION SIZING")
    print("-" * 80)
    
    kelly_size = risk_manager.calculate_position_size(
        portfolio_value=100000,
        risk_per_trade=0.02,
        entry_price=150,
        stop_loss=147
    )
    
    win_rate = metrics['win_rate']
    avg_win = metrics['avg_win']
    avg_loss = metrics['avg_loss']
    kelly_fraction = risk_manager.calculate_kelly_criterion(win_rate, avg_win, avg_loss)
    
    print(f"   Win Rate: {win_rate*100:.1f}%")
    print(f"   Avg Win: ${avg_win:.2f} | Avg Loss: ${avg_loss:.2f}")
    print(f"   Kelly Fraction: {kelly_fraction*100:.2f}% of portfolio")
    print(f"   Recommended Position Size: {kelly_size:.0f} shares")
    print(f"   Position Value: ${kelly_size * 150:.2f}")
    print()
    
    # Display correlation assessment
    print("9. CORRELATION RISK ASSESSMENT")
    print("-" * 80)
    
    test_trade = {'symbol': 'MSFT', 'sector': 'technology'}
    correlation = risk_manager._assess_correlation_risk(test_trade)
    
    print(f"   Correlation between MSFT and existing positions: {correlation:.2f}")
    print(f"   Threshold: {config['max_correlation']:.2f}")
    print(f"   Status: {'⚠️  High Correlation' if correlation > config['max_correlation'] else '✓ Acceptable'}")
    print()
    
    # Display volatility assessment
    print("10. VOLATILITY RISK ASSESSMENT")
    print("-" * 80)
    
    for symbol in ['AAPL', 'MSFT']:
        trade = {'symbol': symbol, 'sector': 'technology'}
        volatility = risk_manager._assess_volatility_risk(trade)
        print(f"   {symbol} Volatility Risk: {volatility:.2f} ({'High' if volatility > 0.7 else 'Moderate' if volatility > 0.4 else 'Low'})")
    print()
    
    print("=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("=" * 80)
    print()
    print("Key Improvements Demonstrated:")
    print("  ✓ Real volatility calculation from price history")
    print("  ✓ Correlation risk assessment between positions")
    print("  ✓ Risk-reward ratio validation")
    print("  ✓ Maximum loss per trade enforcement")
    print("  ✓ Sector concentration limits")
    print("  ✓ Win rate and expectancy tracking")
    print("  ✓ Kelly Criterion position sizing")
    print("  ✓ Sharpe ratio calculation")
    print("  ✓ Enhanced risk metrics reporting")
    print()


if __name__ == '__main__':
    main()
