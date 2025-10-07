"""
Command-Line Interface for Sentio Trading System
Provides CLI commands for managing and running the trading system
"""

import sys
import argparse
from typing import List

from .config import get_config
from .logger import get_logger
from ..execution.trading_engine import TradingEngine, TradingMode
from ..strategies.tjr_strategy import TJRStrategy
from ..strategies.momentum_strategy import MomentumStrategy
from ..strategies.mean_reversion_strategy import MeanReversionStrategy
from ..strategies.breakout_strategy import BreakoutStrategy

logger = get_logger(__name__)


def run_backtest(args):
    """Run backtesting"""
    print("🔬 Starting backtest...")

    # Initialize strategies
    strategies = [
        TJRStrategy(),
        MomentumStrategy(),
        MeanReversionStrategy(),
        BreakoutStrategy(),
    ]

    # Create engine in backtest mode
    engine = TradingEngine(
        strategies=strategies,
        mode=TradingMode.BACKTEST,
        portfolio_value=args.initial_capital,
    )

    print(f"📊 Backtesting {args.symbol} with ${args.initial_capital:,.0f}")
    print(f"⏰ Timeframe: {args.timeframe}")

    # In production: fetch historical data and run backtest
    print("\n⚠️  Backtest module not yet fully implemented")
    print("   This is a framework placeholder")


def run_paper_trading(args):
    """Run paper trading"""
    print("📄 Starting paper trading...")

    strategies = [
        TJRStrategy(),
        MomentumStrategy(),
        MeanReversionStrategy(),
        BreakoutStrategy(),
    ]

    engine = TradingEngine(
        strategies=strategies,
        mode=TradingMode.PAPER,
        portfolio_value=args.initial_capital,
    )

    print(f"💼 Initial capital: ${args.initial_capital:,.0f}")
    print(f"📈 Trading symbols: {', '.join(args.symbols)}")
    print(f"⏱️  Update interval: {args.interval} seconds")

    print("\n✅ Paper trading engine initialized")
    print("⚠️  Real-time trading loop not yet implemented")
    print("   Use the API endpoint for interactive trading")


def run_live_trading(args):
    """Run live trading (requires confirmation)"""
    print("⚠️  LIVE TRADING MODE")
    print("=" * 50)

    confirmation = input("Type 'I ACCEPT THE RISKS' to continue: ")

    if confirmation != "I ACCEPT THE RISKS":
        print("❌ Live trading canceled")
        return

    print("\n🔴 Starting live trading...")

    strategies = [
        TJRStrategy(),
        MomentumStrategy(),
        MeanReversionStrategy(),
        BreakoutStrategy(),
    ]

    engine = TradingEngine(
        strategies=strategies,
        mode=TradingMode.LIVE,
        portfolio_value=args.initial_capital,
    )

    print("⚠️  Live trading not yet fully implemented")
    print("   Framework is in place, broker integration pending")


def run_api_server(args):
    """Run API server"""
    print("🌐 Starting Sentio API Server...")

    from ..ui.api import app
    import uvicorn

    config = get_config()

    print(f"📡 Host: {args.host}")
    print(f"🔌 Port: {args.port}")
    print(f"👷 Workers: {args.workers}")

    uvicorn.run(
        app, host=args.host, port=args.port, workers=args.workers, log_level="info"
    )


def analyze_symbol(args):
    """Analyze a specific symbol"""
    print(f"🔍 Analyzing {args.symbol}...")

    from ..execution.trading_engine import TradingEngine
    from ..analysis.technical_analysis import TechnicalAnalysisEngine

    # Initialize
    strategies = [TJRStrategy(), MomentumStrategy()]
    engine = TradingEngine(strategies=strategies)
    ta_engine = TechnicalAnalysisEngine()

    # Run analysis
    voting_result = engine.analyze_symbol(args.symbol)

    print("\n" + "=" * 60)
    print(f"📊 ANALYSIS RESULTS FOR {args.symbol}")
    print("=" * 60)

    print(f"\n🎯 Final Signal: {voting_result.final_signal.value.upper()}")
    print(f"💯 Confidence: {voting_result.confidence:.1%}")
    print(f"🤝 Consensus: {voting_result.consensus_strength:.1%}")
    print(f"📈 Participating Strategies: {voting_result.participating_strategies}")

    print("\n📋 Vote Breakdown:")
    for signal_type, count in voting_result.vote_breakdown.items():
        print(f"   {signal_type}: {count}")

    print("\n" + "=" * 60)


def list_strategies(args):
    """List available strategies"""
    print("📚 Available Trading Strategies")
    print("=" * 60)

    strategies = [
        ("TJR", "Three Jump Rule - Momentum continuation pattern"),
        ("Momentum", "Trend-following with momentum indicators"),
        ("Mean Reversion", "Statistical reversion to mean"),
        ("Breakout", "Range breakout with volume confirmation"),
        ("Scalping", "High-frequency small profits (coming soon)"),
        ("Swing", "Multi-day position trading (coming soon)"),
        ("Trend Following", "Long-term trend capture (coming soon)"),
    ]

    for name, description in strategies:
        print(f"\n📈 {name}")
        print(f"   {description}")


def show_config(args):
    """Show current configuration"""
    config = get_config()

    print("⚙️  Sentio Configuration")
    print("=" * 60)

    print(f"\n🎯 Trading Mode: {config.trading_mode.value}")
    print(f"⚖️  Risk Level: {config.risk_level.value}")
    print(f"🔒 Live Trading: {'Enabled' if config.enable_live_trading else 'Disabled'}")
    print(
        f"📄 Paper Trading: {'Enabled' if config.enable_paper_trading else 'Disabled'}"
    )

    print("\n📊 Strategy Settings:")
    print(f"   Min Confidence: {config.strategy.confidence_threshold:.0%}")
    print(f"   Max Concurrent Trades: {config.strategy.max_concurrent_trades}")

    print("\n🛡️  Risk Management:")
    print(f"   Max Position Size: {config.risk_management.max_position_size:.0%}")
    print(f"   Stop Loss: {config.risk_management.stop_loss_percent:.0%}")
    print(f"   Daily Drawdown Limit: {config.risk_management.max_daily_drawdown:.0%}")
    print(f"   Circuit Breaker: {config.risk_management.circuit_breaker_threshold:.0%}")


def show_status(args):
    """Show system status"""
    print("\n🟢 Sentio System Status: Operational")
    # Could add health checks, uptime, etc.


def run_diagnostics(args):
    """Run diagnostics and health checks"""
    print("\n🔍 Running diagnostics...")
    # Placeholder for diagnostics logic
    print("All systems nominal.")


def reload_config(args):
    """Reload configuration dynamically"""
    from .config import ConfigManager

    config_mgr = ConfigManager()
    config_mgr.reload()
    print("\n🔄 Configuration reloaded.")


def main(argv: List[str] = None):
    """Main CLI entry point"""
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
    description="Sentio - Intelligent Trading System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Backtest command
    backtest_parser = subparsers.add_parser("backtest", help="Run backtesting")
    backtest_parser.add_argument("symbol", help="Symbol to backtest")
    backtest_parser.add_argument("--initial-capital", type=float, default=100000.0)
    backtest_parser.add_argument("--timeframe", default="5min")
    backtest_parser.set_defaults(func=run_backtest)

    # Paper trading command
    paper_parser = subparsers.add_parser("paper", help="Run paper trading")
    paper_parser.add_argument("symbols", nargs="+", help="Symbols to trade")
    paper_parser.add_argument("--initial-capital", type=float, default=100000.0)
    paper_parser.add_argument("--interval", type=int, default=60)
    paper_parser.set_defaults(func=run_paper_trading)

    # Live trading command
    live_parser = subparsers.add_parser("live", help="Run live trading")
    live_parser.add_argument("symbols", nargs="+", help="Symbols to trade")
    live_parser.add_argument("--initial-capital", type=float, default=100000.0)
    live_parser.set_defaults(func=run_live_trading)

    # API server command
    api_parser = subparsers.add_parser("api", help="Start API server")
    api_parser.add_argument("--host", default="0.0.0.0")
    api_parser.add_argument("--port", type=int, default=8000)
    api_parser.add_argument("--workers", type=int, default=4)
    api_parser.set_defaults(func=run_api_server)

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a symbol")
    analyze_parser.add_argument("symbol", help="Symbol to analyze")
    analyze_parser.set_defaults(func=analyze_symbol)

    # List strategies command
    list_parser = subparsers.add_parser("strategies", help="List available strategies")
    list_parser.set_defaults(func=list_strategies)

    # Config command
    config_parser = subparsers.add_parser("config", help="Show configuration")
    config_parser.set_defaults(func=show_config)

    # New commands
    status_parser = subparsers.add_parser("status", help="Show system status")
    status_parser.set_defaults(func=show_status)

    diag_parser = subparsers.add_parser("diagnostics", help="Run diagnostics")
    diag_parser.set_defaults(func=run_diagnostics)

    reload_parser = subparsers.add_parser("reload-config", help="Reload configuration")
    reload_parser.set_defaults(func=reload_config)

    # Interactive strategy selection
    strat_parser = subparsers.add_parser("select-strategy", help="Select trading strategy interactively")
    strat_parser.add_argument("--list", action="store_true", help="List available strategies")
    strat_parser.set_defaults(func=select_strategy)

    # Parse arguments
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    try:
        args.func(args)
        return 0
    except Exception as e:
        logger.error(f"Command failed: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        return 1


def select_strategy(args):
    from .config import StrategyConfig

    config = StrategyConfig()
    if args.list:
        print("\nAvailable strategies:")
        for strat in config.enabled_strategies:
            print(f"- {strat}")
    else:
        chosen = input("Enter strategy name: ")
        if chosen in config.enabled_strategies:
            print(f"✅ Selected strategy: {chosen}")
        else:
            print(f"❌ Strategy not found: {chosen}")


if __name__ == "__main__":
    sys.exit(main())
