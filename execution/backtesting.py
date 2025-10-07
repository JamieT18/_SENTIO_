"""
Backtesting engine for Sentio trading strategies
"""
import pandas as pd
from typing import Dict, Any, List
import logging
import concurrent.futures
from sentio.utils.helpers import calculate_sharpe_ratio, calculate_max_drawdown, calculate_win_rate, calculate_profit_factor

logger = logging.getLogger("sentio.execution.backtesting")

def run_backtest(strategy: Any, market_data: pd.DataFrame) -> Dict[str, Any]:
    """
    Run backtest for a given strategy and market data.
    Args:
        strategy: Trading strategy instance with a 'generate_signals' method
        market_data: Historical market data (DataFrame)
    Returns:
        dict: Backtest results
    Raises:
        ValueError: If market_data is empty or strategy is missing method
    """
    if market_data.empty:
        raise ValueError("market_data must not be empty")
    if not hasattr(strategy, 'generate_signals'):
        raise ValueError("strategy must have a 'generate_signals' method")
    signals = strategy.generate_signals(market_data)
    trades = []
    TRADE_AUDIT_LOG = []
    for i, signal_info in enumerate(signals):
        signal = signal_info['signal'] if isinstance(signal_info, dict) else signal_info
        explanation = signal_info.get('explanation', '') if isinstance(signal_info, dict) else ''
        trade = None
        if signal == 'buy':
            trade = {'index': i, 'action': 'buy', 'price': market_data['close'].iloc[i], 'explanation': explanation}
        elif signal == 'sell':
            trade = {'index': i, 'action': 'sell', 'price': market_data['close'].iloc[i], 'explanation': explanation}
        if trade:
            trades.append(trade)
            TRADE_AUDIT_LOG.append({
                'timestamp': pd.Timestamp.now().isoformat(),
                'trade': trade
            })
            on_trade(trade)  # Trigger trade event hook
    # Automated learning after backtest
    if hasattr(strategy, 'learn_from_trades'):
        strategy.learn_from_trades(trades)
    profit = sum(t['price'] for t in trades if t['action'] == 'sell') - sum(t['price'] for t in trades if t['action'] == 'buy')
    logger.debug(f"Backtest trades: {trades}, profit: {profit}")
    logger.info(f"Trade audit log: {TRADE_AUDIT_LOG}")
    return {'trades': trades, 'profit': float(profit), 'audit_log': TRADE_AUDIT_LOG}

def run_multi_strategy_backtest(strategies: List[Any], market_data: pd.DataFrame) -> Dict[str, Any]:
    """
    Stub for multi-strategy backtesting.
    Args:
        strategies: List of strategy instances
        market_data: Historical market data
    Returns:
        dict: Results for each strategy
    """
    if market_data.empty or not strategies:
        logger.warning("No market data or strategies provided for multi-strategy backtest.")
        return {}
    results = {}
    n = len(market_data)
    window = max(10, n // 5)  # Walk-forward window size
    for strategy in strategies:
        strategy_results = []
        for start in range(0, n, window):
            end = min(start + window, n)
            window_data = market_data.iloc[start:end]
            if window_data.empty:
                continue
            try:
                signals = strategy.generate_signals(window_data)
                trades = []
                for i, signal in enumerate(signals):
                    if signal == 'buy':
                        trades.append({'index': start + i, 'action': 'buy', 'price': window_data['close'].iloc[i]})
                    elif signal == 'sell':
                        trades.append({'index': start + i, 'action': 'sell', 'price': window_data['close'].iloc[i]})
                profit = sum(t['price'] for t in trades if t['action'] == 'sell') - sum(t['price'] for t in trades if t['action'] == 'buy')
                strategy_results.append({'window': (start, end), 'trades': trades, 'profit': float(profit)})
            except Exception as e:
                logger.error(f"Error in walk-forward for strategy {getattr(strategy, '__class__', type(strategy)).__name__}: {e}")
        results[getattr(strategy, '__class__', type(strategy)).__name__] = strategy_results
    logger.info(f"Multi-strategy walk-forward backtest results: {results}")
    return results

def run_parallel_backtests(strategies: List[Any], market_data: pd.DataFrame) -> Dict[str, Any]:
    """
    Run backtests for multiple strategies in parallel
    """
    def backtest_worker(strategy):
        return run_backtest(strategy, market_data)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(backtest_worker, strategies))
    return {getattr(s, '__class__', type(s)).__name__: r for s, r in zip(strategies, results)}

def analyze_trades(trades: List[dict]) -> dict:
    """
    Compute advanced analytics for trade results
    """
    returns = [t['price'] for t in trades if t['action'] == 'sell'] + [-t['price'] for t in trades if t['action'] == 'buy']
    return {
        'sharpe': calculate_sharpe_ratio(returns),
        'max_drawdown': calculate_max_drawdown(returns),
        'win_rate': calculate_win_rate(trades),
        'profit_factor': calculate_profit_factor(trades)
    }

def on_trade(trade: dict):
    """
    Event hook for trade execution
    """
    print(f"Trade executed: {trade}")

def on_signal(signal: dict):
    """
    Event hook for signal generation
    """
    print(f"Signal generated: {signal}")
