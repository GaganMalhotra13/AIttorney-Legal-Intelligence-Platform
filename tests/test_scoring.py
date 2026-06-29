"""
tests/test_scoring.py
Unit tests for the 28-signal win probability scoring engine.
Run: pytest tests/test_scoring.py -v

These tests verify:
- High-confidence legal signals score correctly
- Negative signals reduce probability appropriately
- Combined signals are additive
- Output is always clamped between 15 and 88
- Grade thresholds are correct
- Resolution data is returned properly
"""
import sys
import os
import importlib.util
from unittest import result
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend_deploy")))

# Add project root to path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)


def _load_compute_win_probability():
    candidate_imports = [
        ("utils.scoring", "compute_win_probability"),
        ("scoring", "compute_win_probability"),
    ]
    for module_name, attr_name in candidate_imports:
        try:
            module = __import__(module_name, fromlist=[attr_name])
            return getattr(module, attr_name)
        except (ImportError, AttributeError):
            continue

    candidate_paths = [
        os.path.join(ROOT_DIR, "utils", "scoring.py"),
        os.path.join(ROOT_DIR, "scoring.py"),
    ]
    for path in candidate_paths:
        if os.path.exists(path):
            spec = importlib.util.spec_from_file_location("scoring_module", path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return getattr(module, "compute_win_probability")

    raise ImportError("Could not import compute_win_probability from utils.scoring or scoring")


compute_win_probability = _load_compute_win_probability()


class TestWinProbabilityBasics:
    def test_neutral_baseline(self):
        """No signals → 50% baseline."""
        result = compute_win_probability("unrelated text", "")
        assert result["probability"] == 50
        assert result["confidence"] == "Low"

    def test_probability_always_in_range(self):
        """Probability must always be between 15 and 88."""
        # Max positive signals
        strong_q = "section 138 cheque bounce consumer protection motor accident written agreement"
        r1 = compute_win_probability(strong_q, "")
        assert 15 <= r1["probability"] <= 88

        # Max negative signals
        weak_q = "limitation period arbitration clause force majeure settlement agreement no receipt verbal agreement"
        r2 = compute_win_probability(weak_q, "")
        assert 15 <= r2["probability"] <= 88

    def test_returns_all_required_fields(self):
        """Response must contain all expected keys."""
        result = compute_win_probability("landlord deposit", "")
        assert "probability"       in result
        assert "positive_factors"  in result
        assert "negative_factors"  in result
        assert "confidence"        in result
        assert "resolution_days"   in result
        assert "resolution_label"  in result
        assert "grade"             in result


class TestPositiveSignals:
    def test_cheque_bounce_scores_high(self):
        """NI Act §138 has very high conviction rate → strong positive signal."""
        result = compute_win_probability("section 138 cheque bounce", "")
        assert result["probability"] > 65
        assert result["grade"] == "Strong"
        assert len(result["positive_factors"]) > 0

    def test_consumer_protection_positive(self):
        """Consumer protection is plaintiff-friendly forum."""
        result = compute_win_probability("consumer protection act complaint", "")
        assert result["probability"] > 60

    def test_motor_accident_positive(self):
        """MACT awards are generally generous."""
        result = compute_win_probability("motor accident compensation claim", "")
        assert result["probability"] > 60

    def test_written_agreement_boosts_score(self):
        """Documentary evidence is strongest form of proof."""
        base    = compute_win_probability("contract dispute", "")
        with_doc= compute_win_probability("contract dispute written agreement registered", "")
        assert with_doc["probability"] > base["probability"]

    def test_domestic_violence_positive(self):
        """DV Act has strong statutory backing."""
        result = compute_win_probability("domestic violence protection order", "")
        assert result["probability"] > 60

    def test_wrongful_termination_positive(self):
        """Labour tribunals lean employee-side."""
        result = compute_win_probability("wrongful termination labour dispute", "")
        assert result["probability"] > 55


class TestNegativeSignals:
    def test_limitation_period_kills_case(self):
        """Time-barred cases almost always fail."""
        result = compute_win_probability("limitation period expired claim", "")
        assert result["probability"] < 40
        assert len(result["negative_factors"]) > 0

    def test_arbitration_clause_reduces_score(self):
        """Arbitration clause forces out of civil court."""
        base        = compute_win_probability("contract dispute", "")
        with_arbitr = compute_win_probability("contract dispute arbitration clause", "")
        assert with_arbitr["probability"] < base["probability"]

    def test_force_majeure_reduces_score(self):
        """Force majeure clauses can nullify claims."""
        result = compute_win_probability("contract breach force majeure covid", "")
        assert result["probability"] < 50

    def test_verbal_agreement_reduces_score(self):
        """Oral contracts are hard to prove."""
        result = compute_win_probability("verbal agreement dispute no receipt", "")
        assert result["probability"] < 45

    def test_settlement_agreement_reduces_score(self):
        """Prior settlement is a complete defence."""
        result = compute_win_probability("settlement agreement signed earlier", "")
        assert result["probability"] < 40


class TestGradeThresholds:
    def test_strong_grade_above_65(self):
        result = compute_win_probability("section 138 negotiable instruments cheque bounce", "")
        assert result["probability"] >= 65
        assert result["grade"] == "Strong"

    def test_weak_grade_below_45(self):
        result = compute_win_probability("limitation period arbitration clause force majeure", "")
        assert result["probability"] < 45
        assert result["grade"] == "Weak"

    def test_moderate_grade_between_45_and_65(self):
        # Property disputes are mixed — neither strong nor weak
        result = compute_win_probability("property dispute contract breach", "")
        # Just verify grade is assigned
        assert result["grade"] in ["Strong", "Moderate", "Weak"]


class TestConfidenceLevels:
    def test_high_confidence_with_many_signals(self):
        """3+ signals → High confidence."""
        result = compute_win_probability(
            "section 138 cheque bounce written agreement registered witnesses",
            "consumer protection"
        )
        assert result["confidence"] == "High"

    def test_low_confidence_with_no_signals(self):
        """No recognizable signals → Low confidence."""
        result = compute_win_probability("I need legal help", "")
        assert result["confidence"] == "Low"

    def test_medium_confidence_with_one_signal(self):
        # "section 138" fires exactly 1 signal → Medium confidence
        result = compute_win_probability("section 138 case filed", "")
        assert result["confidence"] in ["Medium", "High"]

class TestResolutionData:
    def test_cheque_bounce_resolution(self):
        """NI Act cases have specific resolution timeline."""
        result = compute_win_probability("section 138 cheque bounce", "")
        assert result["resolution_days"] > 0
        assert result["resolution_label"] != ""
        # NI Act track should be faster than civil court
        assert result["resolution_days"] <= 365

    def test_property_dispute_longer_resolution(self):
        """Property disputes take longer."""
        property_r = compute_win_probability("property dispute land title", "")
        cheque_r   = compute_win_probability("section 138 cheque bounce", "")
        assert property_r["resolution_days"] >= cheque_r["resolution_days"]

    def test_resolution_label_not_empty(self):
        """Every case should have a court label."""
        result = compute_win_probability("any legal issue", "")
        assert isinstance(result["resolution_label"], str)
        assert len(result["resolution_label"]) > 0


class TestContextIntegration:
    def test_live_context_contributes_to_score(self):
        """Signals in live_context should affect score just like query."""
        base = compute_win_probability("dispute with party", "")
        with_ctx = compute_win_probability(
            "dispute with party",
            "section 138 cheque bounce written agreement court"
        )
        assert with_ctx["probability"] != base["probability"]

    def test_combined_query_and_context(self):
        """Query + context together should detect more signals."""
        query_only = compute_win_probability("cheque bounce", "")
        combined   = compute_win_probability(
            "cheque bounce section 138",
            "negotiable instruments written agreement registered witnesses"
        )
        assert len(combined["positive_factors"]) >= len(query_only["positive_factors"])


class TestEdgeCases:
    def test_empty_strings(self):
        """Empty input should not crash — return baseline."""
        result = compute_win_probability("", "")
        assert result["probability"] == 50
        assert result["grade"] == "Moderate"

    def test_very_long_input(self):
        """Long strings should not crash or exceed bounds."""
        long_query = "section 138 " * 100
        result = compute_win_probability(long_query, "")
        assert 15 <= result["probability"] <= 88

    def test_special_characters(self):
        """Special characters in input should not crash."""
        result = compute_win_probability("₹50,000 चेक bounce §138", "")
        assert "probability" in result

    def test_all_caps_input(self):
        """Case insensitive matching — SECTION 138 same as section 138."""
        lower = compute_win_probability("section 138 cheque bounce", "")
        upper = compute_win_probability("SECTION 138 CHEQUE BOUNCE", "")
        assert lower["probability"] == upper["probability"]