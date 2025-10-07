"""
Unit tests for Subscription Manager
Tests subscription tiers, features, and profit-sharing
"""

import pytest
from datetime import datetime, timedelta

from sentio.billing.subscription_manager import (
    SubscriptionManager,
    SubscriptionTier,
    SubscriptionStatus,
    TierFeatures,
    TIER_CONFIGS,
)


@pytest.mark.unit
class TestSubscriptionTiers:
    """Test subscription tier configurations"""

    def test_tier_configs_exist(self):
        """Test that all tier configurations are defined"""
        assert SubscriptionTier.FREE in TIER_CONFIGS
        assert SubscriptionTier.BASIC in TIER_CONFIGS
        assert SubscriptionTier.PROFESSIONAL in TIER_CONFIGS
        assert SubscriptionTier.ENTERPRISE in TIER_CONFIGS

    def test_free_tier_features(self):
        """Test free tier feature restrictions"""
        free_tier = TIER_CONFIGS[SubscriptionTier.FREE]

        assert free_tier.day_trading is False
        assert free_tier.long_term_investment is True
        assert free_tier.profit_sharing_enabled is False
        assert free_tier.profit_sharing_rate == 0.0
        assert free_tier.max_strategies == 2
        assert free_tier.api_access is False

    def test_professional_tier_features(self):
        """Test professional tier has all features"""
        pro_tier = TIER_CONFIGS[SubscriptionTier.PROFESSIONAL]

        assert pro_tier.day_trading is True
        assert pro_tier.long_term_investment is True
        assert pro_tier.profit_sharing_enabled is True
        assert pro_tier.profit_sharing_rate > 0
        assert pro_tier.advanced_analytics is True
        assert pro_tier.insider_tracking is True

    def test_enterprise_tier_features(self):
        """Test enterprise tier has maximum features"""
        ent_tier = TIER_CONFIGS[SubscriptionTier.ENTERPRISE]

        assert ent_tier.max_concurrent_trades >= 50
        assert ent_tier.priority_support is True
        assert ent_tier.custom_strategies is True
        # Enterprise tier has different profit sharing rate (not necessarily higher)

    def test_tier_progression(self):
        """Test that higher tiers have more features"""
        free = TIER_CONFIGS[SubscriptionTier.FREE]
        basic = TIER_CONFIGS[SubscriptionTier.BASIC]
        pro = TIER_CONFIGS[SubscriptionTier.PROFESSIONAL]

        # Check progression
        assert basic.max_strategies > free.max_strategies
        assert pro.max_strategies > basic.max_strategies
        assert pro.profit_sharing_rate > free.profit_sharing_rate


@pytest.mark.unit
class TestSubscriptionManager:
    """Test SubscriptionManager functionality"""

    @pytest.fixture
    def manager(self):
        """Create a SubscriptionManager instance"""
        return SubscriptionManager()

    def test_initialization(self, manager):
        """Test SubscriptionManager initialization"""
        assert manager is not None

    def test_get_tier_features(self, manager):
        """Test getting tier features"""
        features = manager.get_tier_features(SubscriptionTier.PROFESSIONAL)

        assert isinstance(features, TierFeatures)
        assert features.tier == SubscriptionTier.PROFESSIONAL

    def test_check_feature_access_allowed(self, manager):
        """Test feature access check for allowed feature"""
        # Create a professional subscription
        manager.create_subscription("test_user", SubscriptionTier.PROFESSIONAL)

        has_access = manager.check_feature_access(
            user_id="test_user", feature="day_trading"
        )

        assert has_access is True

    def test_check_feature_access_denied(self, manager):
        """Test feature access check for denied feature"""
        # Create a free subscription
        manager.create_subscription("test_user", SubscriptionTier.FREE)

        has_access = manager.check_feature_access(
            user_id="test_user", feature="day_trading"
        )

        assert has_access is False

    def test_calculate_profit_sharing_professional(self, manager):
        """Test profit sharing calculation for professional tier"""
        # Create a professional subscription
        manager.create_subscription("test_user", SubscriptionTier.PROFESSIONAL)

        profit_share = manager.calculate_profit_sharing(
            user_id="test_user", trading_profit=10000.0
        )

        # Professional tier: 20% profit sharing
        expected = 10000.0 * 0.20
        assert profit_share == expected

    def test_calculate_profit_sharing_free_tier(self, manager):
        """Test that free tier has no profit sharing"""
        # Create a free subscription
        manager.create_subscription("test_user", SubscriptionTier.FREE)

        profit_share = manager.calculate_profit_sharing(
            user_id="test_user", trading_profit=10000.0
        )

        assert profit_share == 0.0

    def test_calculate_profit_sharing_negative_profit(self, manager):
        """Test profit sharing with losses"""
        # Create a professional subscription
        manager.create_subscription("test_user", SubscriptionTier.PROFESSIONAL)

        profit_share = manager.calculate_profit_sharing(
            user_id="test_user", trading_profit=-5000.0
        )

        # No profit sharing on losses
        assert profit_share == 0.0

    def test_create_subscription(self, manager):
        """Test creating a subscription"""
        subscription = manager.create_subscription(
            user_id="test_user", tier=SubscriptionTier.PROFESSIONAL, trial_days=14
        )

        assert subscription.user_id == "test_user"
        assert subscription.tier == SubscriptionTier.PROFESSIONAL
        assert subscription.status == SubscriptionStatus.TRIAL

    def test_upgrade_subscription(self, manager):
        """Test upgrading a subscription"""
        # Create free tier first
        manager.create_subscription("test_user", SubscriptionTier.FREE)

        # Upgrade to professional
        subscription = manager.upgrade_subscription(
            "test_user", SubscriptionTier.PROFESSIONAL
        )

        assert subscription.tier == SubscriptionTier.PROFESSIONAL
        assert subscription.status == SubscriptionStatus.ACTIVE

    def test_cancel_subscription(self, manager):
        """Test canceling a subscription"""
        # Create subscription
        manager.create_subscription("test_user", SubscriptionTier.PROFESSIONAL)

        # Cancel it
        manager.cancel_subscription("test_user")

        subscription = manager.subscriptions["test_user"]
        assert subscription.status == SubscriptionStatus.CANCELED
        assert subscription.end_date is not None


@pytest.mark.unit
class TestProfitSharing:
    """Test profit sharing calculations"""

    @pytest.fixture
    def manager(self):
        """Create a SubscriptionManager instance"""
        return SubscriptionManager()

    def test_profit_sharing_rates(self, manager):
        """Test profit sharing rates for different tiers"""
        test_profit = 10000.0

        # Create subscriptions
        manager.create_subscription("free_user", SubscriptionTier.FREE)
        manager.create_subscription("pro_user", SubscriptionTier.PROFESSIONAL)

        free_share = manager.calculate_profit_sharing("free_user", test_profit)
        pro_share = manager.calculate_profit_sharing("pro_user", test_profit)

        assert free_share == 0.0
        assert pro_share > 0.0
        assert pro_share < test_profit  # Should be a percentage

    def test_profit_sharing_accumulation(self, manager):
        """Test profit sharing accumulation over time"""
        # Create subscription
        manager.create_subscription("test_user", SubscriptionTier.PROFESSIONAL)

        # Make multiple profitable trades
        profit1 = manager.calculate_profit_sharing("test_user", 1000.0)
        profit2 = manager.calculate_profit_sharing("test_user", 2000.0)

        subscription = manager.subscriptions["test_user"]

        # Total profit sharing should accumulate
        assert subscription.total_profits_shared == profit1 + profit2
        assert subscription.total_profits_shared > 0
