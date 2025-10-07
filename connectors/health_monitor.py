"""
Health monitoring for external connectors in Sentio 2.0
"""
from typing import Dict

def check_connector_health(connector_name: str) -> Dict[str, str]:
    """
    Check health status of a connector.
    Args:
        connector_name: Name of the connector
    Returns:
        dict: Health status
    Raises:
        ValueError: If connector_name is empty
    """
    if not connector_name:
        raise ValueError("connector_name must not be empty")
    # Mock: Always healthy
    return {"connector": connector_name, "status": "healthy"}
