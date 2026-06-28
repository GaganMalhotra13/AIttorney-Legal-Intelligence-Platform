"""
tests/test_anonymize.py
Unit tests for PII redaction in anonymize.py
Run: pytest tests/test_anonymize.py -v
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend_deploy.utils.anonymize import anonymize


class TestPhoneRedaction:
    """Phone numbers in various Indian formats are removed"""

    def test_10_digit_phone_removed(self):
        result = anonymize("Call me at 9876543210 regarding the case")
        assert "9876543210" not in result

    def test_phone_with_plus91_removed(self):
        result = anonymize("Contact: +91 9876543210 for details")
        assert "9876543210" not in result

    def test_phone_with_spaces_removed(self):
        result = anonymize("My number is 98765 43210")
        assert "9876543210" not in result.replace(" ", "")

    def test_normal_text_not_affected_by_phone_check(self):
        text   = "The landlord refused to return the deposit"
        result = anonymize(text)
        assert result == text


class TestEmailRedaction:
    """Email addresses are removed"""

    def test_basic_email_removed(self):
        result = anonymize("Email me at john@example.com for details")
        assert "john@example.com" not in result

    def test_gmail_removed(self):
        result = anonymize("Reach me at ramesh.kumar@gmail.com")
        assert "ramesh.kumar@gmail.com" not in result

    def test_multiple_emails_removed(self):
        result = anonymize("From: a@b.com and also c@d.org")
        assert "a@b.com"  not in result
        assert "c@d.org"  not in result


class TestAadhaarRedaction:
    """12-digit Aadhaar numbers are removed"""

    def test_aadhaar_12_digit_removed(self):
        result = anonymize("My Aadhaar number is 123456789012")
        assert "123456789012" not in result

    def test_aadhaar_with_spaces_removed(self):
        result = anonymize("Aadhaar: 1234 5678 9012")
        digits = result.replace(" ", "")
        assert "123456789012" not in digits


class TestNormalTextPreservation:
    """Legal text that is not PII is preserved"""

    def test_legal_terms_preserved(self):
        text   = "The tenant shall vacate the premises within 30 days"
        result = anonymize(text)
        assert "tenant" in result
        assert "vacate" in result
        assert "30 days" in result

    def test_case_description_preserved(self):
        text   = "Landlord refused to return deposit after 4 months"
        result = anonymize(text)
        assert "Landlord" in result
        assert "deposit"  in result

    def test_rupee_amounts_preserved(self):
        text   = "Security deposit of ₹80,000 not returned"
        result = anonymize(text)
        assert "₹80,000" in result

    def test_empty_string_returns_empty(self):
        assert anonymize("") == ""

    def test_returns_string_type(self):
        assert isinstance(anonymize("any input"), str)


class TestOutputAlwaysString:
    """anonymize() never crashes, always returns string"""

    def test_special_characters_input(self):
        result = anonymize("!@#$%^&*()")
        assert isinstance(result, str)

    def test_numbers_only_input(self):
        result = anonymize("1234 5678")
        assert isinstance(result, str)

    def test_very_long_input(self):
        text   = "The landlord " * 1000
        result = anonymize(text)
        assert isinstance(result, str)

    def test_mixed_pii_and_legal_text(self):
        text   = "Ramesh Kumar (9876543210) filed a complaint about ₹50,000 deposit"
        result = anonymize(text)
        assert isinstance(result, str)
        assert "9876543210" not in result
        assert "₹50,000"    in result