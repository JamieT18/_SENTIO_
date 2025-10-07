"""
Diagnostics Aggregator for Sentio 2.0
Aggregates diagnostics, health, and regime context from all modules for unified system health reporting.
"""
from typing import Dict, Any, List

class DiagnosticsAggregator:
    def __init__(self):
        self.records: List[Dict[str, Any]] = []
"""
Diagnostics Aggregator for Sentio
"""
            "source": source,
            "diagnostics": diagnostics,
            "regime_context": regime_context,
            "health": health
        })

    def aggregate(self) -> Dict[str, Any]:
        summary = {
            "total_records": len(self.records),
            "sources": list(set(r["source"] for r in self.records)),
            "error_rate": sum(r["diagnostics"].get("error_rate", 0) for r in self.records) / max(len(self.records), 1),
            "regimes": list(set(r["regime_context"].get("regime") for r in self.records if r["regime_context"])),
            "health_status": self._aggregate_health()
        }
        return summary

    def _aggregate_health(self) -> str:
        statuses = [r["health"].get("status") for r in self.records if r["health"]]
        if "warning" in statuses:
            return "warning"
        if "caution" in statuses:
            return "caution"
        return "ok"

# Example usage:
# aggregator = DiagnosticsAggregator()
# aggregator.add_record("strategy", diagnostics, regime_context, health)
# aggregator.add_record("plugin", diagnostics, regime_context, health)
# system_health = aggregator.aggregate()
