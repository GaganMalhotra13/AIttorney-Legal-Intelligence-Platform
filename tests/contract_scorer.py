"""
tests/test_contract_scorer.py
Unit tests for the NLP contract risk scorer.
Run: pytest tests/test_contract_scorer.py -v
"""
import os
import importlib.util

contract_scorer_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "backend_deploy", "utils", "contract_scorer.py")
)
spec = importlib.util.spec_from_file_location("contract_scorer", contract_scorer_path)
contract_scorer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contract_scorer)
score_contract = contract_scorer.score_contract


class TestBasicStructure:
    """Output always has required fields"""

    def test_returns_all_required_fields(self):
        result = score_contract("This is a contract.", "Employee")
        assert "score"       in result
        assert "grade"       in result
        assert "flags"       in result
        assert "green_flags" in result
        assert "flag_count"  in result
        assert "summary"     in result

    def test_score_is_integer_or_float(self):
        result = score_contract("contract text", "Employee")
        assert isinstance(result["score"], (int, float))

    def test_score_never_exceeds_95(self):
        # Even with every red flag, score caps at 95
        text = ("non-compete unilateral termination without cause sole discretion "
                "liquidated damages arbitration intellectual property all inventions "
                "auto renewal indemnify and hold limitation of liability waiver of jury")
        result = score_contract(text, "Employee")
        assert result["score"] <= 95

    def test_score_never_negative(self):
        text = "mutual termination 60 days notice severance governed by indian law"
        result = score_contract(text, "Employee")
        assert result["score"] >= 0

    def test_empty_contract_returns_zero(self):
        result = score_contract("", "Employee")
        assert result["score"]      == 0
        assert result["flags"]      == []
        assert result["flag_count"] == 0

    def test_empty_contract_grade_is_low(self):
        result = score_contract("", "Employee")
        assert result["grade"] == "LOW"


class TestRedFlagDetection:
    """Each risk pattern is correctly detected"""

    def test_arbitration_detected(self):
        result = score_contract(
            "All disputes shall be resolved through arbitration proceedings.", "Employee"
        )
        assert result["score"] > 0
        clauses = [f["clause"].lower() for f in result["flags"]]
        assert any("arbitrat" in c for c in clauses)

    def test_non_compete_detected(self):
        result = score_contract(
            "Employee agrees to a strict non-compete clause for two years after termination.",
            "Employee"
        )
        assert result["score"] > 0
        clauses = [f["clause"].lower() for f in result["flags"]]
        assert any("non" in c or "compet" in c for c in clauses)

    def test_sole_discretion_detected(self):
        result = score_contract(
            "Management decisions shall be made at the sole discretion of the employer.",
            "Employee"
        )
        assert result["score"] > 0

    def test_without_cause_detected(self):
        result = score_contract(
            "The company may terminate this agreement without cause at any time.",
            "Employee"
        )
        assert result["score"] > 0

    def test_liquidated_damages_detected(self):
        result = score_contract(
            "Liquidated damages of ₹5,00,000 shall apply for breach.",
            "Freelancer / Contractor"
        )
        assert result["score"] > 0

    def test_indemnification_detected(self):
        result = score_contract(
            "You agree to indemnify and hold harmless the company from all claims.",
            "Buyer"
        )
        assert result["score"] > 0

    def test_auto_renewal_detected(self):
        result = score_contract(
            "This agreement shall automatically renew each year unless cancelled.",
            "Tenant"
        )
        assert result["score"] > 0

    def test_ip_ownership_detected(self):
        result = score_contract(
            "All intellectual property created during employment belongs to the Employer.",
            "Employee"
        )
        assert result["score"] > 0

    def test_case_insensitive_matching(self):
        lower = score_contract("arbitration clause applies", "Employee")
        upper = score_contract("ARBITRATION CLAUSE APPLIES", "Employee")
        assert lower["score"] == upper["score"]

    def test_multiple_flags_accumulate(self):
        single = score_contract("arbitration clause", "Employee")
        multi  = score_contract(
            "arbitration clause non-compete without cause sole discretion", "Employee"
        )
        assert multi["score"] > single["score"]


class TestGreenFlagDetection:
    """Protective clauses correctly reduce score"""

    def test_mutual_termination_reduces_score(self):
        risky    = score_contract("unilateral termination without cause", "Employee")
        balanced = score_contract(
            "unilateral termination without cause mutual termination 60 days notice",
            "Employee"
        )
        assert balanced["score"] <= risky["score"]

    def test_severance_is_green_flag(self):
        result = score_contract(
            "arbitration clause severance package provided upon termination",
            "Employee"
        )
        assert len(result["green_flags"]) > 0

    def test_indian_governing_law_is_green_flag(self):
        result = score_contract(
            "arbitration clause governed by indian law and courts",
            "Employee"
        )
        assert len(result["green_flags"]) > 0


class TestGradeThresholds:
    """Grade values map to correct score ranges"""

    def test_high_risk_grade(self):
        text = ("non-compete unilateral termination without cause sole discretion "
                "liquidated damages arbitration intellectual property")
        result = score_contract(text, "Employee")
        assert result["grade"] == "HIGH"
        assert result["score"] > 60

    def test_low_risk_grade(self):
        result = score_contract(
            "Both parties agree to fair and mutual terms of employment.", "Employee"
        )
        assert result["grade"] == "LOW"
        assert result["score"] <= 30

    def test_moderate_risk_grade(self):
        result = score_contract("arbitration clause applies to all disputes.", "Employee")
        if 30 < result["score"] <= 60:
            assert result["grade"] == "MODERATE"


class TestExcerptExtraction:
    """Excerpt correctly locates flagged clause in contract text"""

    def test_excerpt_present_when_flag_found(self):
        result = score_contract(
            "The company may terminate this agreement without cause at any time.",
            "Employee"
        )
        for flag in result["flags"]:
            assert "excerpt" in flag
            assert isinstance(flag["excerpt"], str)

    def test_excerpt_not_empty(self):
        result = score_contract(
            "Employee agrees to a non-compete clause for two years.", "Employee"
        )
        for flag in result["flags"]:
            assert len(flag["excerpt"]) > 0


class TestRoleSpecificSummary:
    """Summary changes based on role"""

    def test_employee_summary_mentions_employee(self):
        result = score_contract("arbitration clause", "Employee")
        assert "Employee" in result["summary"]

    def test_tenant_summary_mentions_tenant(self):
        result = score_contract("arbitration clause", "Tenant")
        assert "Tenant" in result["summary"]

    def test_flag_count_matches_flags_list(self):
        result = score_contract(
            "non-compete arbitration without cause", "Employee"
        )
        assert result["flag_count"] == len(result["flags"])


class TestEdgeCases:
    """Handles unusual inputs without crashing"""

    def test_very_long_text(self):
        text   = "arbitration clause " * 500
        result = score_contract(text, "Employee")
        assert result is not None
        assert result["score"] > 0

    def test_special_characters(self):
        result = score_contract(
            "₹50,000 non-compete @employer #arbitration!", "Employee"
        )
        assert result is not None

    def test_numbers_and_symbols_only(self):
        result = score_contract("1234567890 !@#$%^&*()", "Employee")
        assert result["score"] == 0

    def test_all_roles_work(self):
        roles = [
            "Employee", "Tenant", "Freelancer / Contractor",
            "Buyer", "Seller", "Service Provider", "Borrower", "Investor"
        ]
        for role in roles:
            result = score_contract("arbitration clause", role)
            assert result is not None, f"Failed for role: {role}"