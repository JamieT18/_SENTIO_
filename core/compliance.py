"""
Automated compliance checks and audit trail utilities for Sentio
"""
import datetime
from typing import Dict, Any, List
from sentio.core.logger import SentioLogger

structured_logger = SentioLogger.get_structured_logger("compliance")

class ComplianceChecker:
    def __init__(self, rules: List[Dict[str, Any]] = None):
        self.rules = rules or []

    def check(self, portfolio: dict) -> list:
        structured_logger.log_event(
            "compliance_check",
            "Checking portfolio compliance",
            {"portfolio": portfolio}
        )
        try:
            result = self._check_logic(portfolio)
            structured_logger.log_event(
                "compliance_check_result",
                "Compliance check completed",
                {"result": result}
            )
            return result
        except Exception as e:
            structured_logger.log_event(
                "compliance_check_error",
                str(e),
                {"portfolio": portfolio, "exception": repr(e)},
                level="error"
            )
            raise

class AuditTrail:
    def __init__(self):
        self.logs = []

    def log(self, action: str, details: dict):
        structured_logger.log_event(
            "audit_log",
            f"Audit log action: {action}",
            {"action": action, "details": details}
        )
        try:
            result = self._log_logic(action, details)
            structured_logger.log_event(
                "audit_log_result",
                f"Audit log action {action} completed",
                {"result": result}
            )
            return result
        except Exception as e:
            structured_logger.log_event(
                "audit_log_error",
                str(e),
                {"action": action, "details": details, "exception": repr(e)},
                level="error"
            )
            raise

    def get_logs(self) -> List[Dict[str, Any]]:
        return self.logs
