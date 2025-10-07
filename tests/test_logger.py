"""
Tests for core logger module
"""

import logging
from sentio.core.logger import SentioLogger, get_logger


def test_get_logger_returns_logger():
    """Test that get_logger returns a logging.Logger instance"""
    logger = get_logger("test_logger")
    assert isinstance(logger, logging.Logger)


def test_get_logger_singleton():
    """Test that get_logger returns the same logger for the same name"""
    logger1 = get_logger("test_logger_singleton")
    logger2 = get_logger("test_logger_singleton")
    assert logger1 is logger2


def test_get_logger_different_names():
    """Test that get_logger returns different loggers for different names"""
    logger1 = get_logger("logger1")
    logger2 = get_logger("logger2")
    assert logger1 is not logger2
    assert logger1.name == "logger1"
    assert logger2.name == "logger2"


def test_sentio_logger_class():
    """Test SentioLogger class methods"""
    logger = SentioLogger.get_logger("sentio_test")
    assert isinstance(logger, logging.Logger)


def test_logger_log_levels():
    """Test logger accepts different log levels"""
    logger_debug = get_logger("test_debug", log_level="DEBUG")
    logger_info = get_logger("test_info", log_level="INFO")
    logger_warning = get_logger("test_warning", log_level="WARNING")

    assert logger_debug.level == logging.DEBUG
    assert logger_info.level == logging.INFO
    assert logger_warning.level == logging.WARNING
