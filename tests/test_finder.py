from datetime import date

from src.zeutara_contact_finder.finder import email_is_direct_and_domain_matched, validate_contact
from src.zeutara_contact_finder.scoring import score_account


def test_email_must_be_direct_and_domain_matched():
    assert email_is_direct_and_domain_matched("maya@northstarapi.com", "northstarapi.com")
    assert not email_is_direct_and_domain_matched("hello@northstarapi.com", "northstarapi.com")
    assert not email_is_direct_and_domain_matched("maya@gmail.com", "northstarapi.com")


def test_seed_account_scores_above_tier_one_threshold():
    account = {
        "funding_stage": "Seed",
        "last_funding_date": "2025-03-15",
        "revenue_signal": "confirmed_arr",
        "intent_signal": "active",
        "team_size": 8,
        "sector": "B2B SaaS",
        "warm_connection": "shared",
    }
    score, _ = score_account(account, today=date(2026, 5, 12))
    assert score >= 70


def test_quarantines_generic_email_and_missing_linkedin():
    account = {
        "company": "StealthOps",
        "domain": "stealthops.io",
        "funding_stage": "Seed",
        "last_funding_date": "2025-02-01",
        "revenue_signal": "none",
        "intent_signal": "mild",
        "team_size": 4,
        "sector": "B2B SaaS",
        "warm_connection": "cold",
    }
    contact = {
        "name": "Evan Brooks",
        "title": "Operations Lead",
        "email": "hello@stealthops.io",
        "linkedin_url": "",
        "source": "mock_apollo",
    }
    result = validate_contact(account, contact, today=date(2026, 5, 12))
    assert result.status == "quarantined"
    assert "email_not_verified_direct_domain_match" in result.reason
    assert "missing_linkedin_profile_url" in result.reason
