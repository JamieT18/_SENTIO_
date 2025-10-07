"""
Sentio Health Alert System
Automatically sends notifications when system health status is warning or caution.
Integrates with CLI and diagnostics aggregator.
"""
import time
from sentio.analysis.diagnostics_aggregator import DiagnosticsAggregator

# Simulated notification function
def send_alert(message: str):
    print(f"[ALERT] {message}")

# Simulated periodic health check
def monitor_health():
    aggregator = DiagnosticsAggregator()
    # Simulated data sources (replace with live data in production)
    SAMPLE_DIAGNOSTICS = [
        {"source": "strategy", "diagnostics": {"error_rate": 0.02}, "regime_context": {"regime": "bull"}, "health": {"status": "ok"}},
        {"source": "plugin", "diagnostics": {"error_rate": 0.12}, "regime_context": {"regime": "bear"}, "health": {"status": "warning"}},
        {"source": "ai", "diagnostics": {"error_rate": 0.05}, "regime_context": {"regime": "neutral"}, "health": {"status": "ok"}},
    ]
    for record in SAMPLE_DIAGNOSTICS:
        aggregator.add_record(record["source"], record["diagnostics"], record["regime_context"], record["health"])
    summary = aggregator.aggregate()
    if summary["health_status"] in ["warning", "caution"]:
        send_alert(f"System health status: {summary['health_status']}. Immediate attention required!")
    else:
        print("System health is OK.")

if __name__ == "__main__":
    # For demo, run once. In production, run periodically (e.g., with cron or as a service)
    monitor_health()
