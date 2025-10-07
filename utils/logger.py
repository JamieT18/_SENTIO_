"""
Logger utility for Sentio 2.0
"""
import logging
from typing import Optional
import threading
import queue
import logging.handlers

class AsyncLogger(logging.Logger):
    def __init__(self, name):
        super().__init__(name)
        self.queue = queue.Queue()
        self.worker = threading.Thread(target=self._process_queue, daemon=True)
        self.worker.start()

    def handle(self, record):
        self.queue.put(record)

    def _process_queue(self):
        while True:
            record = self.queue.get()
            super().handle(record)

def get_logger(name: str, level: Optional[int] = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s %(name)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger

def get_file_logger(name: str, filename: str, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    handler = logging.handlers.TimedRotatingFileHandler(filename, when='midnight', backupCount=7)
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s %(name)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger

def configure_advanced_logging():
    """
    Stub for advanced logging configuration (e.g., file, cloud, async logging).
    """
    # Not yet implemented
    pass
