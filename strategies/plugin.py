"""
Plugin system for custom strategies in Sentio
"""
from typing import Dict, Any, Callable
import logging

logger = logging.getLogger("sentio.strategies.plugin")

class StrategyPluginRegistry:

    def __init__(self):
        self.plugins: Dict[str, Callable] = {}
        self.plugin_versions: Dict[str, str] = {}
        self.plugin_diagnostics: Dict[str, Any] = {}
        logger.info("StrategyPluginRegistry initialized.")

    def register(self, name: str, strategy_cls: Callable, version: str = "1.0", diagnostics: Any = None):
        self.plugins[name] = strategy_cls
        self.plugin_versions[name] = version
        self.plugin_diagnostics[name] = diagnostics or {}
        logger.info(f"Registered strategy plugin: {name} v{version}")

    def get(self, name: str) -> Callable:
        return self.plugins.get(name)

    def get_diagnostics(self, name: str) -> Any:
        return self.plugin_diagnostics.get(name, {})

    def get_version(self, name: str) -> str:
        return self.plugin_versions.get(name, "unknown")

    def list_plugins(self):
        return list(self.plugins.keys())

strategy_plugins = StrategyPluginRegistry()
