"""
WebSocket Service for Real-Time Dashboard Updates
Provides streaming updates for trade signals, earnings, and notifications
"""

from typing import Dict, Set, List, Any
import asyncio
from datetime import datetime
from fastapi import WebSocket
from ..core.logger import get_logger

logger = get_logger(__name__)


class DashboardWebSocketManager:
    """
    Manages WebSocket connections for real-time dashboard updates

    Features:
    - Multi-client support
    - User-specific subscriptions
    - Trade signals, earnings, and notification updates
    - Automatic cleanup of disconnected clients
    """

    def __init__(self, update_interval: int = 5):
        """
        Initialize WebSocket manager

        Args:
            update_interval: Seconds between updates
        """
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "trade_signals": set(),
            "earnings": set(),
            "notifications": set(),
            "admin": set(),
        }
        self.user_subscriptions: Dict[WebSocket, Dict[str, Any]] = {}
        self.update_interval = update_interval
        self._running = False
        self._broadcast_task = None
        logger.info(
            f"Dashboard WebSocket manager initialized (update_interval={update_interval}s)"
        )

    async def connect(self, websocket: WebSocket, channel: str, user_id: str = None):
        """
        Accept and register a new WebSocket connection

        Args:
            websocket: WebSocket connection to register
            channel: Channel type (trade_signals, earnings, notifications, admin)
            user_id: User identifier for personalized updates
        """
        await websocket.accept()

        if channel not in self.active_connections:
            self.active_connections[channel] = set()

        self.active_connections[channel].add(websocket)
        self.user_subscriptions[websocket] = {
            "channel": channel,
            "user_id": user_id,
            "symbols": set(),
            "connected_at": datetime.now().isoformat(),
        }

        logger.info(
            f"WebSocket client connected to {channel}. User: {user_id}. Total: {len(self.active_connections[channel])}"
        )

    def disconnect(self, websocket: WebSocket):
        """
        Unregister a WebSocket connection

        Args:
            websocket: WebSocket connection to unregister
        """
        if websocket in self.user_subscriptions:
            channel = self.user_subscriptions[websocket]["channel"]
            self.active_connections[channel].discard(websocket)
            del self.user_subscriptions[websocket]
            logger.info(f"WebSocket client disconnected from {channel}")

    async def subscribe_symbols(self, websocket: WebSocket, symbols: List[str]):
        """
        Subscribe a client to specific symbols

        Args:
            websocket: Client WebSocket connection
            symbols: List of symbols to subscribe to
        """
        if websocket in self.user_subscriptions:
            for symbol in symbols:
                self.user_subscriptions[websocket]["symbols"].add(symbol.upper())
            logger.info(f"Client subscribed to symbols: {symbols}")

    async def unsubscribe_symbols(self, websocket: WebSocket, symbols: List[str]):
        """
        Unsubscribe a client from specific symbols

        Args:
            websocket: Client WebSocket connection
            symbols: List of symbols to unsubscribe from
        """
        if websocket in self.user_subscriptions:
            for symbol in symbols:
                self.user_subscriptions[websocket]["symbols"].discard(symbol.upper())
            logger.info(f"Client unsubscribed from symbols: {symbols}")

    async def broadcast_trade_signals(self, signals: List[Dict[str, Any]]):
        """
        Broadcast trade signals to all subscribed clients

        Args:
            signals: List of trade signal data
        """
        if not self.active_connections["trade_signals"]:
            return

        disconnected = []
        for websocket in self.active_connections["trade_signals"]:
            try:
                if websocket in self.user_subscriptions:
                    # Filter signals based on user's symbol subscriptions
                    user_symbols = self.user_subscriptions[websocket]["symbols"]

                    if user_symbols:
                        # Send only subscribed symbols
                        filtered_signals = [
                            s for s in signals if s.get("symbol") in user_symbols
                        ]
                    else:
                        # Send all signals if no specific subscription
                        filtered_signals = signals

                    if filtered_signals:
                        message = {
                            "type": "trade_signals",
                            "data": filtered_signals,
                            "timestamp": datetime.now().isoformat(),
                        }
                        await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting trade signals: {e}")
                disconnected.append(websocket)

        # Clean up disconnected clients
        for ws in disconnected:
            self.disconnect(ws)

    async def broadcast_earnings(self, user_id: str, earnings_data: Dict[str, Any]):
        """
        Broadcast earnings update to a specific user

        Args:
            user_id: User identifier
            earnings_data: Earnings data dictionary
        """
        if not self.active_connections["earnings"]:
            return

        disconnected = []
        for websocket in self.active_connections["earnings"]:
            try:
                if websocket in self.user_subscriptions:
                    ws_user_id = self.user_subscriptions[websocket]["user_id"]

                    # Send only to the specific user
                    if ws_user_id == user_id:
                        message = {
                            "type": "earnings",
                            "data": earnings_data,
                            "timestamp": datetime.now().isoformat(),
                        }
                        await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting earnings: {e}")
                disconnected.append(websocket)

        # Clean up disconnected clients
        for ws in disconnected:
            self.disconnect(ws)

    async def broadcast_notification(self, user_id: str, notification: Dict[str, Any]):
        """
        Broadcast notification to a specific user

        Args:
            user_id: User identifier
            notification: Notification data
        """
        if not self.active_connections["notifications"]:
            return

        disconnected = []
        for websocket in self.active_connections["notifications"]:
            try:
                if websocket in self.user_subscriptions:
                    ws_user_id = self.user_subscriptions[websocket]["user_id"]

                    # Send only to the specific user
                    if ws_user_id == user_id:
                        message = {
                            "type": "notification",
                            "data": notification,
                            "timestamp": datetime.now().isoformat(),
                        }
                        await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting notification: {e}")
                disconnected.append(websocket)

        # Clean up disconnected clients
        for ws in disconnected:
            self.disconnect(ws)

    async def broadcast_admin_update(self, update_type: str, data: Dict[str, Any]):
        """
        Broadcast update to all admin connections

        Args:
            update_type: Type of admin update (users, subscribers, revenue, etc.)
            data: Update data
        """
        if not self.active_connections["admin"]:
            return

        disconnected = []
        for websocket in self.active_connections["admin"]:
            try:
                message = {
                    "type": f"admin_{update_type}",
                    "data": data,
                    "timestamp": datetime.now().isoformat(),
                }
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting admin update: {e}")
                disconnected.append(websocket)

        # Clean up disconnected clients
        for ws in disconnected:
            self.disconnect(ws)

    async def _broadcast_periodic_updates(self):
        """
        Periodically broadcast updates to all connected clients
        This can be used for background updates
        """
        while self._running:
            try:
                # This method can be customized to fetch and broadcast periodic updates
                await asyncio.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Error in periodic broadcast loop: {e}")
                await asyncio.sleep(self.update_interval)

    async def start_broadcasting(self):
        """Start the background task for broadcasting updates"""
        if not self._running:
            self._running = True
            logger.info("Starting dashboard broadcast")
            self._broadcast_task = asyncio.create_task(
                self._broadcast_periodic_updates()
            )

    def stop_broadcasting(self):
        """Stop the background task for broadcasting updates"""
        self._running = False
        if self._broadcast_task:
            self._broadcast_task.cancel()
        logger.info("Stopped dashboard broadcast")


# Global dashboard WebSocket manager instance
dashboard_ws_manager = DashboardWebSocketManager(update_interval=5)
