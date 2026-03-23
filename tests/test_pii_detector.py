from src.pii_detector import mask_pii

def test_mask_pii():
    text = "My email is john@example.com and my SSN is 123-45-6789."
    masked = mask_pii(text)
    assert "[REDACTED EMAIL]" in masked
    assert "[REDACTED SSN]" in masked