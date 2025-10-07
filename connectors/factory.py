"""
Connector factory for creating and managing connector instances
"""

from typing import Dict, Any, Optional, Type
from .base import (
    BaseConnector,
    BrokerConnector,
    DataProviderConnector,
    NotificationConnector,
)
from ..core.logger import get_logger

logger = get_logger(__name__)


class ConnectorFactory:
    """
    Factory for creating and managing connector instances

    Features:
    - Connector registration
    - Instance management
    - Configuration validation
    """

    _broker_connectors: Dict[str, Type[BrokerConnector]] = {}
    _data_connectors: Dict[str, Type[DataProviderConnector]] = {}
    _notification_connectors: Dict[str, Type[NotificationConnector]] = {}
    _instances: Dict[str, BaseConnector] = {}

    @classmethod
    def register_broker(cls, name: str, connector_class: Type[BrokerConnector]):
        """
        Register broker connector class

        Args:
            name: Connector name
            connector_class: Connector class
        """
        cls._broker_connectors[name] = connector_class
        logger.info(f"Registered broker connector: {name}")

    @classmethod
    def register_data_provider(
        cls, name: str, connector_class: Type[DataProviderConnector]
    ):
        """
        Register data provider connector class

        Args:
            name: Connector name
            connector_class: Connector class
        """
        cls._data_connectors[name] = connector_class
        logger.info(f"Registered data provider connector: {name}")

    @classmethod
    def register_notification(
        cls, name: str, connector_class: Type[NotificationConnector]
    ):
        """
        Register notification connector class

        Args:
            name: Connector name
            connector_class: Connector class
        """
        cls._notification_connectors[name] = connector_class
        logger.info(f"Registered notification connector: {name}")

    @classmethod
    def create_broker(
        cls, name: str, config: Dict[str, Any], instance_id: Optional[str] = None
    ) -> BrokerConnector:
        """
        Create broker connector instance

        Args:
            name: Connector type name
            config: Configuration dictionary
            instance_id: Optional instance identifier

        Returns:
            Broker connector instance

        Raises:
            ValueError: If connector type not registered
        """
        if name not in cls._broker_connectors:
            raise ValueError(f"Broker connector '{name}' not registered")

        connector_class = cls._broker_connectors[name]
        instance = connector_class(name, config)

        # Store instance if ID provided
        if instance_id:
            cls._instances[instance_id] = instance

        return instance

    @classmethod
    def create_data_provider(
        cls, name: str, config: Dict[str, Any], instance_id: Optional[str] = None
    ) -> DataProviderConnector:
        """
        Create data provider connector instance

        Args:
            name: Connector type name
            config: Configuration dictionary
            instance_id: Optional instance identifier

        Returns:
            Data provider connector instance

        Raises:
            ValueError: If connector type not registered
        """
        if name not in cls._data_connectors:
            raise ValueError(f"Data provider connector '{name}' not registered")

        connector_class = cls._data_connectors[name]
        instance = connector_class(name, config)

        # Store instance if ID provided
        if instance_id:
            cls._instances[instance_id] = instance

        return instance

    @classmethod
    def create_notification(
        cls, name: str, config: Dict[str, Any], instance_id: Optional[str] = None
    ) -> NotificationConnector:
        """
        Create notification connector instance

        Args:
            name: Connector type name
            config: Configuration dictionary
            instance_id: Optional instance identifier

        Returns:
            Notification connector instance

        Raises:
            ValueError: If connector type not registered
        """
        if name not in cls._notification_connectors:
            raise ValueError(f"Notification connector '{name}' not registered")

        connector_class = cls._notification_connectors[name]
        instance = connector_class(name, config)

        # Store instance if ID provided
        if instance_id:
            cls._instances[instance_id] = instance

        return instance

    @classmethod
    def get_instance(cls, instance_id: str) -> Optional[BaseConnector]:
        """
        Get connector instance by ID

        Args:
            instance_id: Instance identifier

        Returns:
            Connector instance or None
        """
        return cls._instances.get(instance_id)

    @classmethod
    def list_instances(cls) -> Dict[str, BaseConnector]:
        """
        Get all connector instances

        Returns:
            Dictionary of instances
        """
        return cls._instances.copy()

    @classmethod
    def list_registered_brokers(cls) -> list:
        """Get list of registered broker connectors"""
        return list(cls._broker_connectors.keys())

    @classmethod
    def list_registered_data_providers(cls) -> list:
        """Get list of registered data provider connectors"""
        return list(cls._data_connectors.keys())

    @classmethod
    def list_registered_notifications(cls) -> list:
        """Get list of registered notification connectors"""
        return list(cls._notification_connectors.keys())
