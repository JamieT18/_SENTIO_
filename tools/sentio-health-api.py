"""
Sentio Health API Endpoint (FastAPI)
Provides real-time system health, diagnostics, and regime context for dashboards and external integrations.
"""
from fastapi import FastAPI
from sentio.analysis.diagnostics_aggregator import DiagnosticsAggregator

app = FastAPI()
aggregator = DiagnosticsAggregator()

# Simulated data sources (replace with live data in production)
SAMPLE_DIAGNOSTICS = [
    {"source": "strategy", "diagnostics": {"error_rate": 0.02}, "regime_context": {"regime": "bull"}, "health": {"status": "ok"}},
    {"source": "plugin", "diagnostics": {"error_rate": 0.12}, "regime_context": {"regime": "bear"}, "health": {"status": "warning"}},
    {"source": "ai", "diagnostics": {"error_rate": 0.05}, "regime_context": {"regime": "neutral"}, "health": {"status": "ok"}},
]
for record in SAMPLE_DIAGNOSTICS:
    aggregator.add_record(record["source"], record["diagnostics"], record["regime_context"], record["health"])

@app.get("/health")
def get_health():
    """Returns aggregated system health and diagnostics."""
    return aggregator.aggregate()

@app.get("/health/records")
def get_health_records():
    """Returns all diagnostics records."""
    return aggregator.records
