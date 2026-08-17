from app.verification.models import VerificationStatus
from app.verification.verifier import ResultVerifier


def test_verifier_accepts_valid_result():
    verifier = ResultVerifier()

    result = verifier.verify("150")

    assert result.status == VerificationStatus.PASSED
    assert result.reason == "Result contains usable output."


def test_verifier_rejects_none():
    verifier = ResultVerifier()

    result = verifier.verify(None)

    assert result.status == VerificationStatus.FAILED
    assert result.reason == "No result was produced."


def test_verifier_rejects_empty_result():
    verifier = ResultVerifier()

    result = verifier.verify("   ")

    assert result.status == VerificationStatus.FAILED
    assert result.reason == "Result was empty."
