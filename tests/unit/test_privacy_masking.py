from ms_survey.privacy import mask_text_balanced


def test_mask_text_redacts_email_phone_and_person_like_name() -> None:
    source = "Contact John Doe at john.doe@example.org or +31 6 1234 5678."
    masked = mask_text_balanced(source)

    assert masked is not None
    assert "john.doe@example.org" not in masked
    assert "+31 6 1234 5678" not in masked
    assert "John Doe" not in masked
    assert "[REDACTED_EMAIL]" in masked
    assert "[REDACTED_PHONE]" in masked
    assert "[REDACTED_NAME]" in masked

