"""
WebSocket Service for Real-Time Market Data
Provides streaming market data updates via WebSocket connections
"""

from typing import Dict, Set, List
import asyncio
from datetime import datetime
from fastapi import WebSocket
from ..core.logger import get_logger
from .market_data import MarketDataManager

logger = get_logger(__name__)


class MarketDataWebSocketManager:
    """
    Manages WebSocket connections for real-time market data streaming

    Features:
    - Multi-client support
    - Symbol subscription management
    - Periodic price updates
    - Automatic cleanup of disconnected clients
    """

    def __init__(self, update_interval: int = 5):
        """
        Initialize WebSocket manager

        Args:
            update_interval: Seconds between price updates
        """
        self.active_connections: Set[WebSocket] = set()
        self.subscriptions: Dict[WebSocket, Set[str]] = {}
        self.market_data_manager = MarketDataManager(use_real_data=True)
        self.update_interval = update_interval
        self._running = False
        logger.info(
            f"WebSocket manager initialized (update_interval={update_interval}s)"
        )

    async def connect(self, websocket: WebSocket):
        """
        Accept and register a new WebSocket connection

        Args:
            websocket: WebSocket connection to register
        """
        await websocket.accept()
        self.active_connections.add(websocket)
        self.subscriptions[websocket] = set()
        logger.info(
            f"WebSocket client connected. Total connections: {len(self.active_connections)}"
        )

    def disconnect(self, websocket: WebSocket):
        """
        Unregister a WebSocket connection

        Args:
            websocket: WebSocket connection to unregister
        """
        self.active_connections.discard(websocket)
        if websocket in self.subscriptions:
            del self.subscriptions[websocket]
        logger.info(
            f"WebSocket client disconnected. Total connections: {len(self.active_connections)}"
        )

    async def subscribe(self, websocket: WebSocket, symbols: List[str]):
        """
        Subscribe a client to symbol updates

        Args:
            websocket: Client WebSocket connection
            symbols: List of symbols to subscribe to
        """
        if websocket not in self.subscriptions:
            self.subscriptions[websocket] = set()

        for symbol in symbols:
            self.subscriptions[websocket].add(symbol.upper())

        logger.info(f"Client subscribed to {symbols}")

        # Send immediate update for subscribed symbols
        await self._send_quotes_to_client(websocket, symbols)

    async def unsubscribe(self, websocket: WebSocket, symbols: List[str]):
        """
        Unsubscribe a client from symbol updates

        Args:
            websocket: Client WebSocket connection
            symbols: List of symbols to unsubscribe from
        """
        if websocket in self.subscriptions:
            for symbol in symbols:
                self.subscriptions[websocket].discard(symbol.upper())
            logger.info(f"Client unsubscribed from {symbols}")

    async def _send_quotes_to_client(self, websocket: WebSocket, symbols: List[str]):
        """
        Send current quotes for specified symbols to a client

        Args:
            websocket: Client WebSocket connection
            symbols: List of symbols to send quotes for
        """
        try:
            quotes = []
            for symbol in symbols:
                quote = self.market_data_manager.get_quote(symbol.upper())
                quotes.append(quote)

            message = {
                "type": "quotes",
                "data": quotes,
                "timestamp": datetime.now().isoformat(),
            }

            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending quotes to client: {e}")

    async def _broadcast_updates(self):
        """
        Periodically broadcast price updates to all connected clients
        """
        while self._running:
            try:
                # Collect all unique symbols being watched
                all_symbols = set()
                for symbols in self.subscriptions.values():
                    all_symbols.update(symbols)

                if all_symbols:
                    # Fetch quotes for all symbols
                    quotes = {}
                    for symbol in all_symbols:
                        quotes[symbol] = self.market_data_manager.get_quote(symbol)

                    # Send relevant quotes to each client
                    disconnected = []
                    for websocket, symbols in self.subscriptions.items():
                        try:
                            if websocket in self.active_connections:
                                # Filter quotes for this client's subscriptions
                                client_quotes = [
                                    quotes[sym] for sym in symbols if sym in quotes
                                ]

                                if client_quotes:
                                    message = {
                                        "type": "update",
                                        "data": client_quotes,
                                        "timestamp": datetime.now().isoformat(),
                                    }
                                    await websocket.send_json(message)
                        except Exception as e:
                            logger.error(f"Error sending update to client: {e}")
                            disconnected.append(websocket)

                    # Clean up disconnected clients
                    for ws in disconnected:
                        self.disconnect(ws)

                # Wait for next update interval
                await asyncio.sleep(self.update_interval)

            except Exception as e:
                logger.error(f"Error in broadcast loop: {e}")
                await asyncio.sleep(self.update_interval)

    async def start_broadcasting(self):
        """Start the background task for broadcasting updates"""
        if not self._running:
            self._running = True
            logger.info("Starting market data broadcast")
            asyncio.create_task(self._broadcast_updates())

    def stop_broadcasting(self):
        """Stop the background task for broadcasting updates"""
        self._running = False
        logger.info("Stopped market data broadcast")


# Global WebSocket manager instance
ws_manager = MarketDataWebSocketManager(update_interval=5)
