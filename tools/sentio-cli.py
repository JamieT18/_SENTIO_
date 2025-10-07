#!/usr/bin/env python3
"""
Sentio CLI - Command-line tool for Sentio API development and testing

This tool provides easy access to Sentio API endpoints for testing and development.
"""
import argparse
import json
import sys
import os
from typing import Optional

# Add parent directory to path to import SDK
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sdk', 'python'))

try:
    from sentio_sdk import SentioClient, SentioAPIError
except ImportError:
    print("Error: Could not import sentio_sdk. Make sure the SDK is installed.")
    sys.exit(1)


def pretty_print(data):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=2))


def handle_error(error: SentioAPIError):
    """Handle API errors"""
    print(f"❌ Error: {error}", file=sys.stderr)
    if error.status_code:
        print(f"   Status Code: {error.status_code}", file=sys.stderr)
    if error.response:
        print(f"   Details: {json.dumps(error.response, indent=2)}", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Sentio CLI - Development tool for Sentio Trading API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check API health
  %(prog)s health
  
  # Login
  %(prog)s login -u username -p password
  
  # Analyze a symbol
  %(prog)s analyze AAPL --token YOUR_TOKEN
  
  # Get trade signals
  %(prog)s signals --symbols AAPL,GOOGL,MSFT --token YOUR_TOKEN
  
  # Get pricing tiers
  %(prog)s pricing
  
  # Load full dashboard
  %(prog)s dashboard --user-id user_123 --token YOUR_TOKEN
        """
    )
    
    parser.add_argument(
        '--base-url',
        default='http://localhost:8000',
        help='API base URL (default: http://localhost:8000)'
    )
    parser.add_argument(
        '--token',
        help='JWT authentication token'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Health check
    subparsers.add_parser('health', help='Check API health')
    
    # Status
    subparsers.add_parser('status', help='Get system status')
    
    # Login
    login_parser = subparsers.add_parser('login', help='Login and get token')
    login_parser.add_argument('-u', '--username', required=True, help='Username')
    login_parser.add_argument('-p', '--password', required=True, help='Password')
    
    # Analyze symbol
    analyze_parser = subparsers.add_parser('analyze', help='Analyze a symbol')
    analyze_parser.add_argument('symbol', help='Stock symbol (e.g., AAPL)')
    
    # Trade signals
    signals_parser = subparsers.add_parser('signals', help='Get trade signals')
    signals_parser.add_argument('--symbols', help='Comma-separated symbols (default: AAPL,GOOGL,MSFT,TSLA)')
    
    # Insider trades
    insider_parser = subparsers.add_parser('insider', help='Get insider trades')
    insider_parser.add_argument('symbol', help='Stock symbol')
    insider_parser.add_argument('--limit', type=int, default=10, help='Number of trades (default: 10)')
    
    # Top insider symbols
    top_insider_parser = subparsers.add_parser('top-insider', help='Get top insider symbols')
    top_insider_parser.add_argument('--limit', type=int, default=10, help='Number of symbols (default: 10)')
    
    # Fundamental analysis
    fundamental_parser = subparsers.add_parser('fundamental', help='Get fundamental analysis')
    fundamental_parser.add_argument('symbol', help='Stock symbol')
    
    # Pricing
    subparsers.add_parser('pricing', help='Get subscription pricing')
    
    # Dashboard
    dashboard_parser = subparsers.add_parser('dashboard', help='Load dashboard data')
    dashboard_parser.add_argument('--user-id', required=True, help='User ID')
    dashboard_parser.add_argument('--symbols', help='Comma-separated symbols for trade signals')
    
    # Earnings
    earnings_parser = subparsers.add_parser('earnings', help='Get earnings summary')
    earnings_parser.add_argument('--user-id', required=True, help='User ID')
    
    # Performance
    performance_parser = subparsers.add_parser('performance', help='Get performance metrics')
    performance_parser.add_argument('--user-id', help='User ID (optional)')
    
    # Strategies
    subparsers.add_parser('strategies', help='List available strategies')
    
    # Toggle strategy
    toggle_parser = subparsers.add_parser('toggle', help='Toggle strategy on/off')
    toggle_parser.add_argument('strategy', help='Strategy name')
    toggle_parser.add_argument('--enable', action='store_true', help='Enable strategy')
    toggle_parser.add_argument('--disable', action='store_true', help='Disable strategy')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize client
    client = SentioClient(base_url=args.base_url, token=args.token)
    
    try:
        # Execute command
        if args.command == 'health':
            result = client.health_check()
            print("✅ API is healthy")
            pretty_print(result)
            
        elif args.command == 'status':
            result = client.get_status()
            print("📊 System Status")
            pretty_print(result)
            
        elif args.command == 'login':
            result = client.login(args.username, args.password)
            print("✅ Login successful!")
            print(f"🔑 Token: {result['access_token']}")
            print(f"⏰ Expires in: {result['expires_in']} seconds")
            
        elif args.command == 'analyze':
            result = client.analyze_symbol(args.symbol)
            print(f"📈 Analysis for {args.symbol}")
            pretty_print(result)
            
        elif args.command == 'signals':
            symbols = args.symbols.split(',') if args.symbols else None
            result = client.get_trade_signals(symbols)
            print(f"📊 Trade Signals ({result['count']} symbols)")
            for signal in result['signals']:
                icon = '🟢' if signal['signal'] == 'buy' else '🔴' if signal['signal'] == 'sell' else '🟡'
                print(f"{icon} {signal['symbol']}: {signal['signal'].upper()} "
                      f"(confidence: {signal['confidence']:.2%})")
            
        elif args.command == 'insider':
            result = client.get_insider_trades(args.symbol, args.limit)
            print(f"🔍 Insider Trades for {args.symbol}")
            pretty_print(result)
            
        elif args.command == 'top-insider':
            result = client.get_top_insider_symbols(args.limit)
            print(f"🏆 Top {args.limit} Insider-Traded Symbols")
            pretty_print(result)
            
        elif args.command == 'fundamental':
            result = client.get_fundamental_analysis(args.symbol)
            print(f"📊 Fundamental Analysis for {args.symbol}")
            print(f"Overall Score: {result['overall_score']}")
            print(f"Recommendation: {result['recommendation'].upper()}")
            print("\nDetailed Scores:")
            pretty_print(result['scores'])
            
        elif args.command == 'pricing':
            result = client.get_pricing()
            print("💰 Subscription Pricing")
            for tier in result['tiers']:
                print(f"\n{tier['tier'].upper()}: ${tier['price']:.2f}/month")
                features = tier['features']
                if features.get('profit_sharing_enabled'):
                    print(f"  💸 Profit Sharing: {features['profit_sharing_rate']:.1f}%")
            
        elif args.command == 'dashboard':
            symbols = args.symbols.split(',') if args.symbols else None
            result = client.load_dashboard_data(args.user_id, symbols)
            print(f"📊 Dashboard Data for {args.user_id}")
            pretty_print(result)
            
        elif args.command == 'earnings':
            result = client.get_earnings(args.user_id)
            print(f"💰 Earnings Summary for {args.user_id}")
            print(f"Portfolio Value: ${result['portfolio_value']:,.2f}")
            print(f"Total Return: ${result['total_return']:,.2f} ({result['total_return_pct']:.2f}%)")
            print(f"Win Rate: {result['win_rate']:.2%}")
            print(f"Total Trades: {result['total_trades']}")
            
        elif args.command == 'performance':
            result = client.get_performance(args.user_id)
            print("📈 Performance Metrics")
            pretty_print(result)
            
        elif args.command == 'strategies':
            result = client.get_strategies()
            print("🎯 Available Strategies")
            pretty_print(result)
            
        elif args.command == 'toggle':
            if args.enable:
                enabled = True
            elif args.disable:
                enabled = False
            else:
                print("Error: Must specify --enable or --disable", file=sys.stderr)
                sys.exit(1)
            
            result = client.toggle_strategy(args.strategy, enabled)
            status = "enabled" if enabled else "disabled"
            print(f"✅ Strategy '{args.strategy}' {status}")
            pretty_print(result)
            
    except SentioAPIError as e:
        handle_error(e)
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        sys.exit(1)


if __name__ == '__main__':
    main()
