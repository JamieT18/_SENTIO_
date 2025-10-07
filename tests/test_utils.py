"""
Unit tests for Sentio utils module
"""
import unittest
from sentio.utils import get_logger, configure_advanced_logging

class TestLogger(unittest.TestCase):
    def test_get_logger(self):
        logger = get_logger("test_logger")
        self.assertEqual(logger.name, "test_logger")
        logger.info("Logger test message.")

    def test_configure_advanced_logging_stub(self):
        try:
            configure_advanced_logging()
        except Exception as e:
            self.fail(f"configure_advanced_logging raised exception: {e}")

if __name__ == "__main__":
    unittest.main()
