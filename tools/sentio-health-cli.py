"""
Sentio System Health CLI
Command-line tool to report aggregated diagnostics, health, and regime context for Sentio.
"""
import argparse
from sentio.analysis.diagnostics_aggregator import DiagnosticsAggregator

# Simulated data sources for demonstration
SAMPLE_DIAGNOSTICS = [
    {"source": "strategy", "diagnostics": {"error_rate": 0.02}, "regime_context": {"regime": "bull"}, "health": {"status": "ok"}},
    {"source": "plugin", "diagnostics": {"error_rate": 0.12}, "regime_context": {"regime": "bear"}, "health": {"status": "warning"}},
    {"source": "ai", "diagnostics": {"error_rate": 0.05}, "regime_context": {"regime": "neutral"}, "health": {"status": "ok"}},
]

def main():
    parser = argparse.ArgumentParser(description="Sentio System Health CLI")
    parser.add_argument("--summary", action="store_true", help="Show system health summary")
    args = parser.parse_args()

    aggregator = DiagnosticsAggregator()
    for record in SAMPLE_DIAGNOSTICS:
        aggregator.add_record(record["source"], record["diagnostics"], record["regime_context"], record["health"])

    if args.summary:
        summary = aggregator.aggregate()
        print("\nSentio System Health Summary:")
        print(f"Total Records: {summary['total_records']}")
        print(f"Sources: {summary['sources']}")
        print(f"Average Error Rate: {summary['error_rate']:.2%}")
        print(f"Regimes Detected: {summary['regimes']}")
        print(f"Health Status: {summary['health_status']}")
    else:
        print("Use --summary to show system health summary.")

if __name__ == "__main__":
    main()
