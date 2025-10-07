import pytest
from sentio.billing.integration import process_payment, get_subscription_status, get_billing_history

def test_process_payment():
    assert process_payment("user1", 19.0, "card") is True

def test_get_subscription_status():
    assert get_subscription_status("user1") == "active"

def test_get_billing_history():
    history = get_billing_history("user1")
    assert "user_id" in history
    assert "history" in history
    assert isinstance(history["history"], list)
