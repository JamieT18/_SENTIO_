"""
Market strength signal service
Calculates market strength and generates signals
"""

from typing import Dict, Any

from ..core.constants import (
    STRENGTH_STRONG_BULLISH,
    STRENGTH_BULLISH,
    STRENGTH_NEUTRAL,
    STRENGTH_BEARISH,
    RSI_OVERBOUGHT,
    RSI_STRONG,
    RSI_OVERSOLD,
    MOMENTUM_HIGH_SCORE,
    MOMENTUM_STRONG_SCORE,
    MOMENTUM_MODERATE_SCORE,
    MOMENTUM_LOW_SCORE,
    SIGNAL_STRONG_BULLISH,
    SIGNAL_BULLISH,
    SIGNAL_NEUTRAL,
    SIGNAL_BEARISH,
    SIGNAL_STRONG_BEARISH,
)


class StrengthSignalService:
    """Service for calculating market strength signals"""

    def calculate_momentum_score(self, rsi: float) -> float:
        """
        Calculate momentum score from RSI

        Args:
            rsi: RSI indicator value

        Returns:
            Momentum score (0-100)
        """
        if rsi > RSI_OVERBOUGHT:
            return MOMENTUM_HIGH_SCORE
        elif rsi > RSI_STRONG:
            return MOMENTUM_STRONG_SCORE
        elif rsi > RSI_OVERSOLD:
            return MOMENTUM_MODERATE_SCORE
        else:
            return MOMENTUM_LOW_SCORE

    def calculate_strength_components(
        self, technical: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Calculate strength components from technical analysis

        Args:
            technical: Technical analysis results

        Returns:
            Dictionary of strength components
        """
        components = {"trend_strength": 0, "momentum": 0, "volume": 0, "volatility": 0}

        # Calculate momentum from RSI if available
        if "rsi" in technical:
            components["momentum"] = self.calculate_momentum_score(technical["rsi"])

        # Additional component calculations can be added here
        # For now, keeping it simple to maintain existing behavior

        return components

    def calculate_overall_strength(self, components: Dict[str, float]) -> float:
        """
        Calculate overall strength from components

        Args:
            components: Strength components dictionary

        Returns:
            Overall strength score (0-100)
        """
        if not components:
            return 0.0
        return sum(components.values()) / len(components)

    def determine_signal(self, strength: float) -> str:
        """
        Determine signal type from strength score

        Args:
            strength: Overall strength score (0-100)

        Returns:
            Signal type string
        """
        if strength >= STRENGTH_STRONG_BULLISH:
            return SIGNAL_STRONG_BULLISH
        elif strength >= STRENGTH_BULLISH:
            return SIGNAL_BULLISH
        elif strength >= STRENGTH_NEUTRAL:
            return SIGNAL_NEUTRAL
        elif strength >= STRENGTH_BEARISH:
            return SIGNAL_BEARISH
        else:
            return SIGNAL_STRONG_BEARISH

    def analyze_strength(self, technical: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform complete strength analysis

        Args:
            technical: Technical analysis results

        Returns:
            Complete strength analysis with signal
        """
        components = self.calculate_strength_components(technical)
        overall_strength = self.calculate_overall_strength(components)
        signal = self.determine_signal(overall_strength)

        return {
            "strength_score": overall_strength,
            "signal": signal,
            "components": components,
        }
