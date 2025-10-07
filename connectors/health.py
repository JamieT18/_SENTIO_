"""
Health monitoring for connector instances
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from .base import BaseConnector, ConnectorStatus
from ..core.logger import get_logger

logger = get_logger(__name__)


class HealthMonitor:
    """
    Monitor health of connector instances

    Features:
    - Periodic health checks
    - Status tracking
    - Alert generation
    """

    def __init__(self, check_interval: int = 60):
        """
        Initialize health monitor

        Args:
            check_interval: Seconds between health checks
        """
        self.check_interval = check_interval
        self.connectors: Dict[str, BaseConnector] = {}
        self.last_check_time: Dict[str, datetime] = {}
        self.health_history: Dict[str, List[Dict[str, Any]]] = {}

    def register_connector(self, connector_id: str, connector: BaseConnector):
        """
        Register connector for monitoring

        Args:
            connector_id: Connector identifier
            connector: Connector instance
        """
        self.connectors[connector_id] = connector
        self.health_history[connector_id] = []
        logger.info(f"Registered connector for health monitoring: {connector_id}")

    def unregister_connector(self, connector_id: str):
        """
        Unregister connector from monitoring

        Args:
            connector_id: Connector identifier
        """
        if connector_id in self.connectors:
            del self.connectors[connector_id]
            del self.last_check_time[connector_id]
            logger.info(
                f"Unregistered connector from health monitoring: {connector_id}"
            )

    def check_health(self, connector_id: str) -> Dict[str, Any]:
        """
        Check health of specific connector

        Args:
            connector_id: Connector identifier

        Returns:
            Health status
        """
        if connector_id not in self.connectors:
            return {
                "connector_id": connector_id,
                "status": "unknown",
                "error": "Connector not registered",
            }

        connector = self.connectors[connector_id]

        try:
            # Get connector health check
            health = connector.health_check()

            # Add status information
            status_info = connector.get_status()
            health.update(status_info)

            # Record check time
            self.last_check_time[connector_id] = datetime.now()

            # Add to history
            self._add_to_history(connector_id, health)

            return health

        except Exception as e:
            error_status = {
                "connector_id": connector_id,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

            # Add to history
            self._add_to_history(connector_id, error_status)

            logger.error(f"Health check failed for {connector_id}: {e}")
            return error_status

    def check_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Check health of all registered connectors

        Returns:
            Dictionary mapping connector IDs to health status
        """
        results = {}

        for connector_id in self.connectors.keys():
            results[connector_id] = self.check_health(connector_id)

        return results

    def get_unhealthy_connectors(self) -> List[str]:
        """
        Get list of unhealthy connectors

        Returns:
            List of connector IDs with issues
        """
        unhealthy = []

        for connector_id, connector in self.connectors.items():
            if connector.status in [
                ConnectorStatus.ERROR,
                ConnectorStatus.DISCONNECTED,
            ]:
                unhealthy.append(connector_id)
            elif connector.circuit_open:
                unhealthy.append(connector_id)

        return unhealthy

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of all connector health

        Returns:
            Summary statistics
        """
        total = len(self.connectors)
        unhealthy = len(self.get_unhealthy_connectors())
        healthy = total - unhealthy

        status_counts = {}
        for connector in self.connectors.values():
            status = connector.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "total_connectors": total,
            "healthy": healthy,
            "unhealthy": unhealthy,
            "status_counts": status_counts,
            "timestamp": datetime.now().isoformat(),
        }

    def get_history(self, connector_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get health check history for connector

        Args:
            connector_id: Connector identifier
            limit: Maximum number of records to return

        Returns:
            List of health check records
        """
        if connector_id not in self.health_history:
            return []

        return self.health_history[connector_id][-limit:]

    def _add_to_history(self, connector_id: str, health_status: Dict[str, Any]):
        """
        Add health status to history

        Args:
            connector_id: Connector identifier
            health_status: Health status to record
        """
        if connector_id not in self.health_history:
            self.health_history[connector_id] = []

        # Add timestamp if not present
        if "timestamp" not in health_status:
            health_status["timestamp"] = datetime.now().isoformat()

        # Add to history
        self.health_history[connector_id].append(health_status)

        # Limit history size (keep last 100 records)
        if len(self.health_history[connector_id]) > 100:
            self.health_history[connector_id] = self.health_history[connector_id][-100:]

    def should_check(self, connector_id: str) -> bool:
        """
        Check if connector is due for health check

        Args:
            connector_id: Connector identifier

        Returns:
            True if check is due
        """
        if connector_id not in self.last_check_time:
            return True

        elapsed = (datetime.now() - self.last_check_time[connector_id]).total_seconds()
        return elapsed >= self.check_interval
