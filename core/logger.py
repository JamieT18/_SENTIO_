"""
Centralized logging system for Sentio
Provides structured logging with multiple handlers and formatters
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from pythonjsonlogger import jsonlogger
import threading
import queue
import json


class AsyncLogHandler(logging.Handler):
    def __init__(self, target_handler):
        super().__init__()
        self.queue = queue.Queue()
        self.target_handler = target_handler
        self.worker = threading.Thread(target=self._process_queue, daemon=True)
        self.worker.start()

    def emit(self, record):
        self.queue.put(record)

    def _process_queue(self):
        while True:
            record = self.queue.get()
            self.target_handler.emit(record)


class StructuredLogger:
    def __init__(self, logger):
        self.logger = logger

    def log_event(self, event_type, message, context=None, level="info"):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "message": message,
            "context": context or {},
        }
        log_str = json.dumps(log_entry)
        if level == "info":
            self.logger.info(log_str)
        elif level == "warning":
            self.logger.warning(log_str)
        elif level == "error":
            self.logger.error(log_str)
        else:
            self.logger.debug(log_str)


class SentioLogger:
    """
    Sentio logging manager
    Provides structured logging with JSON format support
    """

    _loggers = {}

    @classmethod
    def get_logger(
        cls,
        name: str,
        log_level: str = "INFO",
        log_to_file: bool = True,
        log_dir: str = "logs",
        async_logging: bool = False,
        external_stream: callable = None,
    ) -> logging.Logger:
        """
        Get or create a logger instance

        Args:
            name: Logger name (typically module name)
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_to_file: Whether to log to file
            log_dir: Directory for log files

        Returns:
            Configured logger instance
        """
        if name in cls._loggers:
            return cls._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, log_level.upper()))

        # Prevent duplicate handlers
        if logger.handlers:
            return logger

        # Console handler with colored output
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(console_formatter)
        if async_logging:
            logger.addHandler(AsyncLogHandler(console_handler))
        else:
            logger.addHandler(console_handler)

        # File handler with JSON format and rotation
        if log_to_file:
            log_path = Path(log_dir)
            log_path.mkdir(parents=True, exist_ok=True)

            # Regular file handler
            file_handler = logging.FileHandler(
                log_path / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
            )
            file_handler.setLevel(logging.INFO)

            # JSON formatter for structured logging
            json_formatter = jsonlogger.JsonFormatter(
                "%(asctime)s %(name)s %(levelname)s %(message)s"
            )
            file_handler.setFormatter(json_formatter)
            if async_logging:
                logger.addHandler(AsyncLogHandler(file_handler))
            else:
                logger.addHandler(file_handler)

            # Error file handler
            error_handler = logging.FileHandler(
                log_path / f"{name}_error_{datetime.now().strftime('%Y%m%d')}.log"
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(json_formatter)
            if async_logging:
                logger.addHandler(AsyncLogHandler(error_handler))
            else:
                logger.addHandler(error_handler)

        # External log streaming (e.g., ELK, CloudWatch)
        if external_stream:
            ext_handler = logging.StreamHandler()
            ext_handler.emit = external_stream
            logger.addHandler(ext_handler)

        cls._loggers[name] = logger
        return logger

    @classmethod
    def get_structured_logger(cls, name: str, log_level: str = "INFO"):
        logger = get_logger(name, log_level)
        return StructuredLogger(logger)

    @classmethod
    def log_trade(cls, logger: logging.Logger, trade_data: dict):
        """Log trade execution with structured data"""
        logger.info("Trade executed", extra={"trade": trade_data})

    @classmethod
    def log_strategy_signal(cls, logger: logging.Logger, strategy: str, signal: dict):
        """Log strategy signal with metadata"""
        logger.info(f"Strategy signal: {strategy}", extra={"signal": signal})

    @classmethod
    def log_error(cls, logger: logging.Logger, error: Exception, context: dict = None):
        """Log error with context"""
        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {},
        }
        logger.error("Error occurred", extra=error_data, exc_info=True)

    @classmethod
    def log_performance(cls, logger: logging.Logger, metrics: dict):
        """Log performance metrics"""
        logger.info("Performance metrics", extra={"metrics": metrics})


def get_logger(name: str, log_level: str = "INFO") -> logging.Logger:
    """
    Convenience function to get a logger

    Args:
        name: Logger name
        log_level: Logging level

    Returns:
        Configured logger
    """
    return SentioLogger.get_logger(name, log_level)
