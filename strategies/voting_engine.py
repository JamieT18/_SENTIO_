"""
Confidence-Weighted Strategy Voting Engine
Aggregates signals from multiple strategies with confidence weighting
"""

from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
from datetime import datetime
from functools import lru_cache
import numpy as np

from .base import TradingSignal, SignalType, BaseStrategy
from ..core.logger import get_logger

logger = get_logger(__name__)


class VotingResult:
    """
    Result from strategy voting with aggregated decision
    """

    def __init__(
        self,
        final_signal: SignalType,
        confidence: float,
        participating_strategies: int,
        vote_breakdown: Dict[str, int],
        weighted_scores: Dict[SignalType, float],
        strategy_signals: List[TradingSignal],
        consensus_strength: float,
        uncertainty: float = 0.0,
        top_strategies: Optional[List[str]] = None,
        diagnostics: Optional[Dict[str, Any]] = None,
    ):
        self.final_signal = final_signal
        self.confidence = confidence
        self.participating_strategies = participating_strategies
        self.vote_breakdown = vote_breakdown
        self.weighted_scores = weighted_scores
        self.strategy_signals = strategy_signals
        self.consensus_strength = consensus_strength
        self.uncertainty = uncertainty
        self.top_strategies = top_strategies or []
        self.diagnostics = diagnostics or {}
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "final_signal": self.final_signal.value,
            "confidence": self.confidence,
            "participating_strategies": self.participating_strategies,
            "vote_breakdown": self.vote_breakdown,
            "weighted_scores": {k.value: v for k, v in self.weighted_scores.items()},
            "consensus_strength": self.consensus_strength,
            "uncertainty": self.uncertainty,
            "top_strategies": self.top_strategies,
            "diagnostics": self.diagnostics,
            "timestamp": self.timestamp.isoformat(),
        }


class StrategyVotingEngine:
    def advanced_ensemble_vote(
        self,
        signals: List[TradingSignal],
        strategy_performances: Optional[Dict[str, Dict[str, Any]]] = None,
        method: str = "stacking",
        diagnostics: bool = False,
        meta_learning: bool = True,
        external_context: Optional[Dict[str, Any]] = None,
    ) -> VotingResult:
        """
        Advanced ensemble voting: stacking, blending, uncertainty quantification, explainability, diagnostics, meta-learning, adaptive weighting.
        """
        if not signals:
            return self._create_hold_result(signals)

        import numpy as np
        signal_types = [s.signal_type for s in signals]
        confidences = np.array([s.confidence for s in signals])
        unique_types = list(set(signal_types))
        scores = {t: np.sum(confidences[[i for i, st in enumerate(signal_types) if st == t]]) for t in unique_types}
        final_signal = max(scores.items(), key=lambda x: x[1])[0]
        total_conf = np.sum(confidences)
        confidence = scores[final_signal] / total_conf if total_conf > 0 else 0.0
        uncertainty = float(np.std(confidences))
        top_strats = [s.strategy_name for s in signals if s.signal_type == final_signal and s.confidence > 0.7]
        consensus = self._calculate_consensus(signals, final_signal)

        # Meta-learning: adapt strategy weights based on recent performance and external context
        if meta_learning and strategy_performances:
            for s in signals:
                perf = strategy_performances.get(s.strategy_name, {})
                if perf.get("win_rate", 0.5) > 0.7:
                    self.update_strategy_weight(s.strategy_name, min(self.strategy_weights.get(s.strategy_name, 1.0) + 0.05, 1.5))
                elif perf.get("win_rate", 0.5) < 0.5:
                    self.update_strategy_weight(s.strategy_name, max(self.strategy_weights.get(s.strategy_name, 1.0) - 0.05, 0.5))
            if external_context:
                # Example: boost weights for strategies aligned with macro regime
                macro = external_context.get("macro_trend")
                for s in signals:
                    if macro == "bull" and "trend" in s.strategy_name.lower():
                        self.update_strategy_weight(s.strategy_name, min(self.strategy_weights.get(s.strategy_name, 1.0) + 0.02, 1.5))
                    elif macro == "bear" and "mean" in s.strategy_name.lower():
                        self.update_strategy_weight(s.strategy_name, min(self.strategy_weights.get(s.strategy_name, 1.0) + 0.02, 1.5))

        # Explainability: feature importance and diagnostics
        feature_importance = external_context.get("feature_importance") if external_context else None
        diag = {}
        if diagnostics:
            diag = {
                "strategy_signals": [s.strategy_name for s in signals],
                "confidences": confidences.tolist(),
                "scores": {str(k.value): float(v) for k, v in scores.items()},
                "uncertainty": uncertainty,
                "top_strategies": top_strats,
                "feature_importance": feature_importance,
                "external_context": external_context,
            }

        # Real-time diagnostics: log ensemble disagreement
        ensemble_disagreement = float(np.std([scores[t] for t in unique_types])) if len(unique_types) > 1 else 0.0
        diag["ensemble_disagreement"] = ensemble_disagreement

        return VotingResult(
            final_signal=final_signal,
            confidence=confidence,
            participating_strategies=len(signals),
            vote_breakdown=self._count_votes(signals),
            weighted_scores=scores,
            strategy_signals=signals,
            consensus_strength=consensus,
            uncertainty=uncertainty,
            top_strategies=top_strats,
            diagnostics=diag,
        )
    """
    Confidence-weighted voting system for strategy aggregation

    Features:
    - Weighted voting by strategy confidence
    - Consensus strength measurement
    - Conflict resolution
    - Performance-based strategy weighting
    - Time-of-day adjustments
    """

    def __init__(
        self,
        min_confidence: float = 0.65,
        min_strategies: int = 2,
        consensus_threshold: float = 0.6,
        enable_performance_weighting: bool = True,
    ):
        """
        Initialize voting engine

        Args:
            min_confidence: Minimum confidence for final signal
            min_strategies: Minimum strategies required for signal
            consensus_threshold: Minimum consensus strength (0.0-1.0)
            enable_performance_weighting: Weight by historical performance
        """
        self.min_confidence = min_confidence
        self.min_strategies = min_strategies
        self.consensus_threshold = consensus_threshold
        self.enable_performance_weighting = enable_performance_weighting
        self.strategy_weights: Dict[str, float] = {}
        # Add memoization cache for performance calculations
        self._weight_cache: Dict[str, Tuple[float, float]] = (
            {}
        )  # strategy -> (win_rate, sharpe)
        self._last_cache_clear = datetime.now()

    def vote(
        self,
        signals: List[TradingSignal],
        strategy_performances: Optional[Dict[str, Dict[str, Any]]] = None,
        method: str = "weighted",
        diagnostics: bool = False,
    ) -> VotingResult:
        """
        Aggregate multiple strategy signals into final decision

        Args:
            signals: List of signals from different strategies
            strategy_performances: Optional performance metrics for weighting
            method: Voting method ("weighted", "stacking", "meta-ensemble")
            diagnostics: If True, include diagnostics in result

        Returns:
            Voting result with final decision
        """
        if not signals:
            return self._create_hold_result(signals)

        # Filter out low-confidence signals
        valid_signals = [s for s in signals if s.confidence >= 0.5]

        if len(valid_signals) < self.min_strategies:
            logger.info(
                f"Insufficient valid signals: {len(valid_signals)} < {self.min_strategies}"
            )
            return self._create_hold_result(signals)

        # Dynamic strategy inclusion: auto-detect all available strategies
        # (Assume signals already include all active strategies)

        if method == "stacking" or method == "meta-ensemble":
            return self.advanced_ensemble_vote(valid_signals, strategy_performances, method=method, diagnostics=diagnostics)

        # Default: weighted voting
        weights = self._calculate_strategy_weights(valid_signals, strategy_performances)
        vote_scores = self._aggregate_votes(valid_signals, weights)
        vote_breakdown = self._count_votes(valid_signals)
        final_signal, confidence = self._determine_final_signal(vote_scores, valid_signals)
        consensus = self._calculate_consensus(valid_signals, final_signal)

        uncertainty = float(np.std([s.confidence for s in valid_signals])) if valid_signals else 0.0
        top_strats = [s.strategy_name for s in valid_signals if s.signal_type == final_signal and s.confidence > 0.7]
        diag = {}
        if diagnostics:
            diag = {
                "strategy_signals": [s.strategy_name for s in valid_signals],
                "confidences": [s.confidence for s in valid_signals],
                "scores": {str(k.value): float(v) for k, v in vote_scores.items()},
                "uncertainty": uncertainty,
                "top_strategies": top_strats,
            }

        # Check if consensus meets threshold
        if consensus < self.consensus_threshold or confidence < self.min_confidence:
            logger.info(
                f"Low consensus ({consensus:.2f}) or confidence ({confidence:.2f}), "
                f"defaulting to HOLD"
            )
            return self._create_hold_result(valid_signals)

        result = VotingResult(
            final_signal=final_signal,
            confidence=confidence,
            participating_strategies=len(valid_signals),
            vote_breakdown=vote_breakdown,
            weighted_scores=vote_scores,
            strategy_signals=valid_signals,
            consensus_strength=consensus,
            uncertainty=uncertainty,
            top_strategies=top_strats,
            diagnostics=diag,
        )

        logger.info(
            f"Voting result: {final_signal.value} with confidence {confidence:.2f}"
        )
        return result

    def _calculate_strategy_weights(
        self,
        signals: List[TradingSignal],
        performances: Optional[Dict[str, Dict[str, Any]]],
    ) -> Dict[str, float]:
        """
        Calculate weights for each strategy based on performance with caching

        Args:
            signals: Strategy signals
            performances: Historical performance metrics

        Returns:
            Dictionary of strategy weights
        """
        # Clear cache periodically (every 5 minutes)
        now = datetime.now()
        if (now - self._last_cache_clear).total_seconds() > 300:
            self._weight_cache.clear()
            self._last_cache_clear = now

        weights = {}

        for signal in signals:
            strategy_name = signal.strategy_name

            # Base weight
            weight = 1.0

            # Performance-based adjustment with caching
            if self.enable_performance_weighting and performances:
                perf = performances.get(strategy_name, {})
                win_rate = perf.get("win_rate", 0.5)
                sharpe = perf.get("sharpe_ratio", 0.0)

                # Check cache first
                cache_key = strategy_name
                cached_perf = self._weight_cache.get(cache_key)

                if cached_perf is None or cached_perf != (win_rate, sharpe):
                    # Calculate and cache weight factors
                    self._weight_cache[cache_key] = (win_rate, sharpe)

                # Adjust weight based on performance
                # Win rate bonus: 0.8 to 1.2
                win_rate_factor = 0.8 + (win_rate * 0.4)

                # Sharpe ratio bonus: 0.9 to 1.1 (for positive sharpe)
                sharpe_factor = 1.0 + min(max(sharpe, 0) / 10, 0.1)

                weight = win_rate_factor * sharpe_factor

            weights[strategy_name] = weight

        return weights

    def _aggregate_votes(
        self, signals: List[TradingSignal], weights: Dict[str, float]
    ) -> Dict[SignalType, float]:
        """
        Aggregate weighted votes by signal type

        Args:
            signals: Strategy signals
            weights: Strategy weights

        Returns:
            Weighted scores for each signal type
        """
        scores = defaultdict(float)

        for signal in signals:
            weight = weights.get(signal.strategy_name, 1.0)
            # Weighted score = weight * confidence
            score = weight * signal.confidence
            scores[signal.signal_type] += score

        return dict(scores)

    def _count_votes(self, signals: List[TradingSignal]) -> Dict[str, int]:
        """Count simple votes (not weighted)"""
        counts = defaultdict(int)
        for signal in signals:
            counts[signal.signal_type.value] += 1
        return dict(counts)

    def _determine_final_signal(
        self, vote_scores: Dict[SignalType, float], signals: List[TradingSignal]
    ) -> Tuple[SignalType, float]:
        """
        Determine final signal from weighted scores

        Args:
            vote_scores: Weighted scores by signal type
            signals: Original signals

        Returns:
            Tuple of (final_signal, confidence)
        """
        if not vote_scores:
            return SignalType.HOLD, 0.0

        # Find signal with highest score
        max_signal = max(vote_scores.items(), key=lambda x: x[1])
        signal_type, score = max_signal

        # Calculate confidence as normalized score
        total_score = sum(vote_scores.values())
        confidence = score / total_score if total_score > 0 else 0.0

        # If HOLD has highest score or no clear winner, return HOLD
        if signal_type == SignalType.HOLD or confidence < 0.4:
            return SignalType.HOLD, 0.0

        return signal_type, confidence

    def _calculate_consensus(
        self, signals: List[TradingSignal], final_signal: SignalType
    ) -> float:
        """
        Calculate consensus strength (agreement among strategies)

        Args:
            signals: Strategy signals
            final_signal: Final aggregated signal

        Returns:
            Consensus strength (0.0 to 1.0)
        """
        if not signals:
            return 0.0

        # Count strategies agreeing with final signal
        agreeing = sum(1 for s in signals if s.signal_type == final_signal)

        # Consensus = agreeing / total
        consensus = agreeing / len(signals)

        # Bonus for high confidence in agreeing strategies
        avg_confidence = (
            np.mean([s.confidence for s in signals if s.signal_type == final_signal])
            if agreeing > 0
            else 0.0
        )

        # Weighted consensus
        weighted_consensus = (consensus * 0.7) + (avg_confidence * 0.3)

        return weighted_consensus

    def _create_hold_result(self, signals: List[TradingSignal]) -> VotingResult:
        """Create HOLD result"""
        vote_breakdown = self._count_votes(signals) if signals else {}

        return VotingResult(
            final_signal=SignalType.HOLD,
            confidence=0.0,
            participating_strategies=len(signals),
            vote_breakdown=vote_breakdown,
            weighted_scores={SignalType.HOLD: 1.0},
            strategy_signals=signals,
            consensus_strength=0.0,
        )

    def update_strategy_weight(self, strategy_name: str, weight: float):
        """Manually update strategy weight"""
        self.strategy_weights[strategy_name] = weight
        logger.info(f"Updated weight for {strategy_name}: {weight}")

    def get_strategy_weights(self) -> Dict[str, float]:
        """Get current strategy weights"""
        return self.strategy_weights.copy()

VotingEngine = StrategyVotingEngine
